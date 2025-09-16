# data_handler.py
import os
import pandas as pd
import yfinance as yf
import requests
import time

CSV_FOLDER = "./csv_data_files"
os.makedirs(CSV_FOLDER, exist_ok=True)

news_cache = {}

def get_stock_data(ticker):
    ticker = ticker.upper().strip()
    csv_path = os.path.join(CSV_FOLDER, f"{ticker}.csv")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = yf.download(ticker, period="6mo", group_by="ticker")
        if df.empty:
            return None

        # If it's multi-index, flatten it
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df.reset_index(inplace=True)
        df.to_csv(csv_path, index=False)

    # Ensure required columns exist
    expected_cols = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not expected_cols.issubset(df.columns):
        print(f"⚠️ Missing columns for {ticker}, got {df.columns}")
        return None

    # Convert types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

    df.dropna(subset=["Date", "Close", "Volume"], inplace=True)
    return df


def get_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "Symbol": info.get("symbol"),
            "Name": info.get("longName"),
            "Sector": info.get("sector"),
            "Market Cap": info.get("marketCap"),
            "P/E Ratio": info.get("trailingPE"),
            "Dividend Yield": info.get("dividendYield"),
            "52 Week High": info.get("fiftyTwoWeekHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"),
        }
    except Exception as e:
        return {"Error": str(e)}


def get_news(ticker, count=10, tab="news"):
    ticker = ticker.upper().strip()

    if ticker in news_cache and time.time() - news_cache[ticker]["time"] < 300:
        return news_cache[ticker]["data"]

    try:
        t = yf.Ticker(ticker)
        raw_news = t.get_news(count=count, tab=tab)
        news_items = []
        for item in raw_news:
            content = item.get("content", {})
            provider = content.get("provider", {})
            canonical_url = content.get("canonicalUrl", {})
            thumbnail_data = content.get("thumbnail", {})

            # Accessing the required fields with safe checks
            title = content.get("title", "No Title")
            link = canonical_url.get("url", "")
            publisher = provider.get("displayName", "Unknown")
            summary = content.get("summary", "")

            # Accessing the thumbnail URL
            thumbnail_url = ""
            if thumbnail_data:
                resolutions = thumbnail_data.get("resolutions", [])
                if resolutions:
                    thumbnail_url = resolutions[0].get("url", "")

            news_items.append(
                {
                    "title": title,
                    "link": link,
                    "publisher": publisher,
                    "summary": summary,
                    "thumbnail": thumbnail_url,
                }
            )

        news_cache[ticker] = {"time": time.time(), "data": news_items}
        return news_items

    except Exception as e:
        return [
            {
                "title": "Error fetching news",
                "link": "",
                "publisher": str(e),
                "summary": "",
                "thumbnail": "",
            }
        ]


def get_details(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info

        details = f"""
    🏢 {info.get('longName', ticker)}
    Sector: {info.get('sector', 'N/A')}
    Industry: {info.get('industry', 'N/A')}
    Country: {info.get('country', 'N/A')}

    📊 Stock Overview
    Current Price: {info.get('currentPrice', 'N/A')}
    Market Cap: {info.get('marketCap', 'N/A')}
    52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}
    52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}
    Volume: {info.get('volume', 'N/A')} / Avg: {info.get('averageVolume', 'N/A')}

    💰 Valuation
    P/E Ratio: {info.get('trailingPE', 'N/A')}
    Dividend Yield: {info.get('dividendYield', 'N/A')}
    EPS: {info.get('trailingEps', 'N/A')}
    """
        return details
    except Exception as e:
        print(f"Error: {e}")
