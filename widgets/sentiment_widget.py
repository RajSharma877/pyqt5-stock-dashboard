# widgets/sentiment_widget.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient
from datetime import datetime
import pyqtgraph as pg


class SentimentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sentiment_history = []  # Store historical sentiment scores
        self.max_history = 50  # Keep last 50 data points
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setFixedSize(180, 40)
        self.back_btn.setCursor(Qt.PointingHandCursor)

        top_bar.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)
        
        # Header
        header = QLabel("📊 Market Mood Analyzer")
        header.setObjectName("section_header")
        header_font = QFont()
        header_font.setPointSize(24)
        header_font.setWeight(QFont.Bold)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Current sentiment card
        self.sentiment_card = self.create_sentiment_card()
        main_layout.addWidget(self.sentiment_card)
        
        # Sentiment bar
        self.sentiment_bar = SentimentBar()
        main_layout.addWidget(self.sentiment_bar)
        
        # News feed section
        news_label = QLabel("📰 Latest Market Headlines")
        news_label.setObjectName("section_header")
        news_font = QFont()
        news_font.setPointSize(16)
        news_font.setWeight(QFont.Bold)
        news_label.setFont(news_font)
        main_layout.addWidget(news_label)
        
        # Scrollable news area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        
        news_container = QWidget()
        self.news_layout = QVBoxLayout(news_container)
        self.news_layout.setSpacing(8)
        scroll.setWidget(news_container)
        main_layout.addWidget(scroll)
        
        # Historical sentiment chart
        chart_label = QLabel("📈 Sentiment Over Time")
        chart_label.setObjectName("section_header")
        chart_font = QFont()
        chart_font.setPointSize(16)
        chart_font.setWeight(QFont.Bold)
        chart_label.setFont(chart_font)
        main_layout.addWidget(chart_label)
        
        self.sentiment_chart = pg.PlotWidget()
        self.setup_chart()
        main_layout.addWidget(self.sentiment_chart)
        
        # Alert section
        self.alert_label = QLabel("")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setWordWrap(True)
        self.alert_label.hide()
        main_layout.addWidget(self.alert_label)
        
        main_layout.addStretch()
    
    def create_sentiment_card(self):
        card = QFrame()
        card.setMinimumHeight(180)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #3b82f6, stop: 1 #1d4ed8);
                border-radius: 20px;
                padding: 24px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        # Sentiment score
        self.score_label = QLabel("-- / 100")
        self.score_label.setAlignment(Qt.AlignCenter)
        score_font = QFont()
        score_font.setPointSize(48)
        score_font.setWeight(QFont.Bold)
        self.score_label.setFont(score_font)
        self.score_label.setStyleSheet("color: white;")
        layout.addWidget(self.score_label)
        
        # Sentiment label
        self.sentiment_label = QLabel("Analyzing Market...")
        self.sentiment_label.setAlignment(Qt.AlignCenter)
        label_font = QFont()
        label_font.setPointSize(20)
        label_font.setWeight(QFont.DemiBold)
        self.sentiment_label.setFont(label_font)
        self.sentiment_label.setStyleSheet("color: white;")
        layout.addWidget(self.sentiment_label)
        
        # Reasoning
        self.reasoning_label = QLabel("Loading sentiment analysis...")
        self.reasoning_label.setAlignment(Qt.AlignCenter)
        self.reasoning_label.setWordWrap(True)
        reason_font = QFont()
        reason_font.setPointSize(12)
        self.reasoning_label.setFont(reason_font)
        self.reasoning_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        layout.addWidget(self.reasoning_label)
        
        # Last updated
        self.updated_label = QLabel("")
        self.updated_label.setAlignment(Qt.AlignCenter)
        self.updated_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 10px;")
        layout.addWidget(self.updated_label)
        
        return card
    
    def setup_chart(self):
        self.sentiment_chart.setBackground('#1e293b')
        self.sentiment_chart.setTitle("", color='w', size='14pt')
        self.sentiment_chart.setLabel('left', 'Sentiment Score', color='w')
        self.sentiment_chart.setLabel('bottom', 'Time', color='w')
        self.sentiment_chart.showGrid(x=True, y=True, alpha=0.3)
        
        # Add reference lines
        self.sentiment_chart.addLine(y=50, pen=pg.mkPen('gray', width=2, style=Qt.DashLine))
        self.sentiment_chart.addLine(y=70, pen=pg.mkPen('green', width=1, style=Qt.DotLine))
        self.sentiment_chart.addLine(y=30, pen=pg.mkPen('red', width=1, style=Qt.DotLine))
    
    def update_sentiment(self, sentiment_data):
        """Update UI with new sentiment data"""
        score = sentiment_data.get("score", 50)
        label = sentiment_data.get("label", "Neutral")
        reasoning = sentiment_data.get("reasoning", "No analysis available")
        
        # Update main card
        self.score_label.setText(f"{score}")
        self.sentiment_label.setText(f"🎯 {label}")
        self.reasoning_label.setText(reasoning)
        self.updated_label.setText(f"Updated: {datetime.now().strftime('%I:%M %p')}")
        
        # Update sentiment bar
        self.sentiment_bar.set_value(score)
        
        # Update card gradient based on sentiment
        if score >= 70:
            gradient = "stop: 0 #10b981, stop: 1 #059669"  # Green
        elif score >= 40:
            gradient = "stop: 0 #3b82f6, stop: 1 #1d4ed8"  # Blue
        else:
            gradient = "stop: 0 #ef4444, stop: 1 #dc2626"  # Red
        
        self.sentiment_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, {gradient});
                border-radius: 20px;
                padding: 24px;
            }}
        """)
        
        # Add to history
        timestamp = len(self.sentiment_history)
        self.sentiment_history.append({"time": timestamp, "score": score})
        
        # Keep only recent history
        if len(self.sentiment_history) > self.max_history:
            self.sentiment_history.pop(0)
        
        # Update chart
        self.update_chart()
        
        # Check for alerts
        self.check_alerts(score, label)
    
    def update_chart(self):
        """Update the sentiment history chart"""
        if not self.sentiment_history:
            return
        
        times = [d["time"] for d in self.sentiment_history]
        scores = [d["score"] for d in self.sentiment_history]
        
        self.sentiment_chart.clear()
        
        # Re-add reference lines
        self.sentiment_chart.addLine(y=50, pen=pg.mkPen('gray', width=2, style=Qt.DashLine))
        self.sentiment_chart.addLine(y=70, pen=pg.mkPen('green', width=1, style=Qt.DotLine))
        self.sentiment_chart.addLine(y=30, pen=pg.mkPen('red', width=1, style=Qt.DotLine))
        
        # Plot sentiment line
        pen = pg.mkPen(color='#3b82f6', width=3)
        self.sentiment_chart.plot(times, scores, pen=pen, symbol='o', symbolSize=8, symbolBrush='#3b82f6')
    
    def update_news(self, news_items):
        """Update the news feed"""
        # Clear existing news
        while self.news_layout.count():
            item = self.news_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add news items
        for news in news_items[:10]:  # Show top 10
            news_widget = self.create_news_item(news)
            self.news_layout.addWidget(news_widget)
    
    def create_news_item(self, news):
        """Create a news item widget"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                background: #334155;
                border: 1px solid #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(6)
        
        # Title
        title = QLabel(f"📰 {news.get('title', 'No Title')}")
        title.setWordWrap(True)
        title.setStyleSheet("color: #e2e8f0; font-weight: bold; font-size: 13px;")
        layout.addWidget(title)
        
        # Publisher
        publisher = news.get('publisher', 'Unknown')
        pub_label = QLabel(f"📍 {publisher}")
        pub_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
        layout.addWidget(pub_label)
        
        return frame
    
    def check_alerts(self, score, label):
        """Check and display alerts for significant sentiment shifts"""
        if score <= 30:
            self.show_alert(f"⚠️ ALERT: Market sentiment is {label}! Score: {score}/100", "red")
        elif score >= 80:
            self.show_alert(f"🚀 ALERT: Market sentiment is {label}! Score: {score}/100", "green")
        else:
            self.alert_label.hide()
    
    def show_alert(self, message, color):
        """Display an alert message"""
        bg_color = "rgba(239, 68, 68, 0.2)" if color == "red" else "rgba(16, 185, 129, 0.2)"
        border_color = "#ef4444" if color == "red" else "#10b981"
        
        self.alert_label.setText(message)
        self.alert_label.setStyleSheet(f"""
            QLabel {{
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 16px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        self.alert_label.show()


class SentimentBar(QWidget):
    """Custom widget for displaying sentiment as a colored bar"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 50  # Default neutral
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)
    
    def set_value(self, value):
        self.value = max(0, min(100, value))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw background
        painter.setBrush(QColor("#1e293b"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, width, height, 10, 10)
        
        # Draw gradient bar
        gradient = QLinearGradient(0, 0, width, 0)
        gradient.setColorAt(0, QColor("#ef4444"))  # Red
        gradient.setColorAt(0.5, QColor("#3b82f6"))  # Blue
        gradient.setColorAt(1, QColor("#10b981"))  # Green
        
        fill_width = int((self.value / 100) * width)
        painter.setBrush(gradient)
        painter.drawRoundedRect(0, 0, fill_width, height, 10, 10)
        
        # Draw labels
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(10)
        font.setWeight(QFont.Bold)
        painter.setFont(font)
        
        painter.drawText(10, height // 2 + 5, "Bearish")
        painter.drawText(width // 2 - 25, height // 2 + 5, "Neutral")
        painter.drawText(width - 60, height // 2 + 5, "Bullish")
