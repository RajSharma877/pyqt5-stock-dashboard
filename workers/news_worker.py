# news_worker.py
import feedparser
import time
from PyQt5.QtCore import QThread, pyqtSignal


class LiveNewsWorker(QThread):
    news_ready = pyqtSignal(list)

    def __init__(self, ticker, interval=60):
        super().__init__()
        self.ticker = ticker.upper()
        self.interval = interval
        self.running = True

    def fetch_rss_news(self):
        """Fetch news from Yahoo Finance RSS feed"""
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={self.ticker}&region=US&lang=en-US"
        
        try:
            feed = feedparser.parse(url)
            
            if not feed or not hasattr(feed, 'entries'):
                print(f"⚠️ No feed data received for {self.ticker}")
                return []
            
            news_items = []
            for entry in feed.entries[:10]:  # Limit to 10 news items
                news_items.append({
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "publisher": "Yahoo Finance",
                })
            
            print(f"📰 Fetched {len(news_items)} news items for {self.ticker}")
            return news_items
            
        except Exception as e:
            print(f"❌ Error fetching RSS news: {e}")
            return []

    def run(self):
        """Main worker loop"""
        print(f"🚀 News worker started for {self.ticker}")
        
        # Fetch news immediately on start
        try:
            news = self.fetch_rss_news()
            if news:
                self.news_ready.emit(news)
        except Exception as e:
            print(f"Initial news fetch error: {e}")
        
        # Continue fetching at intervals
        while self.running:
            try:
                # Sleep in small chunks to allow faster shutdown
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                
                # Only fetch if still running
                if self.running:
                    news = self.fetch_rss_news()
                    if news:
                        self.news_ready.emit(news)
                        
            except Exception as e:
                if self.running:  # Only log if still running
                    print(f"News worker error: {e}")
        
        print(f"✓ News worker stopped for {self.ticker}")

    def stop(self):
        """Stop the worker gracefully"""
        print(f"🛑 Stopping news worker for {self.ticker}...")
        self.running = False