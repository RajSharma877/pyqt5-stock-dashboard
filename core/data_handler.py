# data_handler.py
import os
import pandas as pd
import yfinance as yf
import requests
import time

CSV_FOLDER = "./csv_data_files"
os.makedirs(CSV_FOLDER, exist_ok=True)

news_cache = {}


# def get_stock_data(ticker):
#     ticker = ticker.upper().strip()
#     csv_path = os.path.join(CSV_FOLDER, f"{ticker}.csv")

#     if os.path.exists(csv_path):
#         # 💡 KEY CHANGE: Read the CSV using the first TWO rows as headers
#         df = pd.read_csv(csv_path, header=[0, 1])

#         # 💡 KEY CHANGE: Flatten the MultiIndex columns to a single level
#         # This converts ('Open', 'AAPL') to 'Open', ('Date', '') to 'Date', etc.
#         new_cols = []
#         for col in df.columns:
#             # If the top level is 'Date', use only 'Date' (it's often a tuple like ('Date', ''))
#             if "Date" in col[0]:
#                 new_cols.append("Date")
#             # Otherwise, use the top level (Open, High, Low, Close, Volume)
#             else:
#                 new_cols.append(col[0])

#         df.columns = new_cols

#     else:
#         # --- Existing download logic ---
#         df = yf.download(ticker, period="6mo", group_by="ticker")
#         if df.empty:
#             return None

#         # When downloading, the data is typically MultiIndex (e.g., ('AAPL', 'Open'))
#         # You need to flatten it to match the expected single-level columns for saving.
#         # This part of your existing code is good for initial download/save:
#         if isinstance(df.columns, pd.MultiIndex):
#             # Flatten to just 'Open', 'High', 'Low', 'Close', 'Volume'
#             df.columns = [col[1] for col in df.columns]

#         df.reset_index(inplace=True)

#         # NOTE: Saving this *flattented* DataFrame will result in the two-row header
#         # when you read it back with the code above.
#         df.to_csv(csv_path, index=False)

#         print(f"✅ Saved and formatted {ticker}.csv")

#     # ✅ Ensure correct columns
#     expected_cols = {
#         "Date",
#         "Open",
#         "High",
#         "Low",
#         "Close",
#         "Volume",
#     }  # Added 'Adj Close' as it's common

#     # After flattening, check for columns
#     if not expected_cols.issubset(df.columns):
#         print(f"⚠️ Missing columns for {ticker}, got {df.columns}")
#         return None

#     # ✅ Clean and convert datatypes
#     df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#     df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
#     df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

#     df.dropna(subset=["Date", "Close", "Volume"], inplace=True)
#     return df

def get_stock_data(ticker):
    ticker = ticker.upper().strip()
    csv_path = os.path.join(CSV_FOLDER, f"{ticker}.csv")

    # Step 1️⃣: Load existing CSV (if exists)
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, header=0)

        # Ensure correct columns
        if "Date" not in df.columns:
            df = pd.read_csv(csv_path, header=[0, 1])
            df.columns = [c[0] if "Date" not in c[0] else "Date" for c in df.columns]

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df.dropna(subset=["Date"], inplace=True)
    else:
        df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

    # Step 2️⃣: Fetch last 6 months from Yahoo
    try:
        new_df = yf.download(ticker, period="6mo", group_by="ticker", progress=False)
        if new_df.empty:
            return None

        # Flatten if MultiIndex
        if isinstance(new_df.columns, pd.MultiIndex):
            new_df.columns = [col[1] for col in new_df.columns]

        new_df.reset_index(inplace=True)
        new_df["Date"] = pd.to_datetime(new_df["Date"], errors="coerce")

        # Keep only required columns
        new_df = new_df[["Date", "Open", "High", "Low", "Close", "Volume"]]

        # Step 3️⃣: Merge (avoid duplicates)
        if not df.empty:
            merged_df = pd.concat([df, new_df]).drop_duplicates(subset=["Date"], keep="last")
        else:
            merged_df = new_df

        # Step 4️⃣: Sort and save back
        merged_df.sort_values("Date", inplace=True)
        merged_df.reset_index(drop=True, inplace=True)
        merged_df.to_csv(csv_path, index=False)
        df = merged_df

        print(f"✅ Synced {ticker} (6mo history merged, {len(df)} records)")
    except Exception as e:
        print(f"⚠️ Error updating history for {ticker}: {e}")
        return df if not df.empty else None

    # Step 5️⃣: Final cleaning
    expected_cols = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not expected_cols.issubset(df.columns):
        print(f"⚠️ Missing columns for {ticker}: {df.columns}")
        return None

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["Date", "Close"], inplace=True)
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
