# # data_handler.py
# import os
# import pandas as pd
# import yfinance as yf
# import requests
# import time

# CSV_FOLDER = "./csv_data_files"
# os.makedirs(CSV_FOLDER, exist_ok=True)

# news_cache = {}

# def get_stock_data(ticker):
#     ticker = ticker.upper().strip()
#     csv_path = os.path.join(CSV_FOLDER, f"{ticker}.csv")

#     # Step 1️⃣: Load existing CSV (if exists)
#     if os.path.exists(csv_path):
#         df = pd.read_csv(csv_path, header=0)

#         # Ensure correct columns
#         if "Date" not in df.columns:
#             df = pd.read_csv(csv_path, header=[0, 1])
#             df.columns = [c[0] if "Date" not in c[0] else "Date" for c in df.columns]

#         df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#         df.dropna(subset=["Date"], inplace=True)
#     else:
#         df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

#     # Step 2️⃣: Fetch last 6 months from Yahoo
#     try:
#         new_df = yf.download(ticker, period="6mo", group_by="ticker", progress=False)
#         if new_df.empty:
#             return None

#         # Flatten if MultiIndex
#         if isinstance(new_df.columns, pd.MultiIndex):
#             new_df.columns = [col[1] for col in new_df.columns]

#         new_df.reset_index(inplace=True)
#         new_df["Date"] = pd.to_datetime(new_df["Date"], errors="coerce")

#         # Keep only required columns
#         new_df = new_df[["Date", "Open", "High", "Low", "Close", "Volume"]]

#         # Step 3️⃣: Merge (avoid duplicates)
#         if not df.empty:
#             merged_df = pd.concat([df, new_df]).drop_duplicates(subset=["Date"], keep="last")
#         else:
#             merged_df = new_df

#         # Step 4️⃣: Sort and save back
#         merged_df.sort_values("Date", inplace=True)
#         merged_df.reset_index(drop=True, inplace=True)
#         merged_df.to_csv(csv_path, index=False)
#         df = merged_df

#         print(f"✅ Synced {ticker} (6mo history merged, {len(df)} records)")
#     except Exception as e:
#         print(f"⚠️ Error updating history for {ticker}: {e}")
#         return df if not df.empty else None

#     # Step 5️⃣: Final cleaning
#     expected_cols = {"Date", "Open", "High", "Low", "Close", "Volume"}
#     if not expected_cols.issubset(df.columns):
#         print(f"⚠️ Missing columns for {ticker}: {df.columns}")
#         return None

#     for col in ["Open", "High", "Low", "Close", "Volume"]:
#         df[col] = pd.to_numeric(df[col], errors="coerce")

#     df.dropna(subset=["Date", "Close"], inplace=True)
#     return df

# def get_fundamentals(ticker):
#     try:
#         stock = yf.Ticker(ticker)
#         info = stock.info
#         return {
#             "Symbol": info.get("symbol"),
#             "Name": info.get("longName"),
#             "Sector": info.get("sector"),
#             "Market Cap": info.get("marketCap"),
#             "P/E Ratio": info.get("trailingPE"),
#             "Dividend Yield": info.get("dividendYield"),
#             "52 Week High": info.get("fiftyTwoWeekHigh"),
#             "52 Week Low": info.get("fiftyTwoWeekLow"),
#         }
#     except Exception as e:
#         return {"Error": str(e)}


# def get_news(ticker, count=10, tab="news"):
#     ticker = ticker.upper().strip()

#     if ticker in news_cache and time.time() - news_cache[ticker]["time"] < 300:
#         return news_cache[ticker]["data"]

#     try:
#         t = yf.Ticker(ticker)
#         raw_news = t.get_news(count=count, tab=tab)
#         news_items = []
#         for item in raw_news:
#             content = item.get("content", {})
#             provider = content.get("provider", {})
#             canonical_url = content.get("canonicalUrl", {})
#             thumbnail_data = content.get("thumbnail", {})

#             # Accessing the required fields with safe checks
#             title = content.get("title", "No Title")
#             link = canonical_url.get("url", "")
#             publisher = provider.get("displayName", "Unknown")
#             summary = content.get("summary", "")

#             # Accessing the thumbnail URL
#             thumbnail_url = ""
#             if thumbnail_data:
#                 resolutions = thumbnail_data.get("resolutions", [])
#                 if resolutions:
#                     thumbnail_url = resolutions[0].get("url", "")

#             news_items.append(
#                 {
#                     "title": title,
#                     "link": link,
#                     "publisher": publisher,
#                     "summary": summary,
#                     "thumbnail": thumbnail_url,
#                 }
#             )

#         news_cache[ticker] = {"time": time.time(), "data": news_items}
#         return news_items

#     except Exception as e:
#         return [
#             {
#                 "title": "Error fetching news",
#                 "link": "",
#                 "publisher": str(e),
#                 "summary": "",
#                 "thumbnail": "",
#             }
#         ]


# def get_details(ticker):
#     try:
#         t = yf.Ticker(ticker)
#         info = t.info

#         details = f"""
#     🏢 {info.get('longName', ticker)}
#     Sector: {info.get('sector', 'N/A')}
#     Industry: {info.get('industry', 'N/A')}
#     Country: {info.get('country', 'N/A')}

#     📊 Stock Overview
#     Current Price: {info.get('currentPrice', 'N/A')}
#     Market Cap: {info.get('marketCap', 'N/A')}
#     52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}
#     52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}
#     Volume: {info.get('volume', 'N/A')} / Avg: {info.get('averageVolume', 'N/A')}

#     💰 Valuation
#     P/E Ratio: {info.get('trailingPE', 'N/A')}
#     Dividend Yield: {info.get('dividendYield', 'N/A')}
#     EPS: {info.get('trailingEps', 'N/A')}
#     """
#         return details
#     except Exception as e:
#         print(f"Error: {e}")

# data_handler.py
import os
import pandas as pd
import yfinance as yf
import time

CSV_FOLDER = "./csv_data_files"
os.makedirs(CSV_FOLDER, exist_ok=True)

news_cache = {}

def get_stock_data(ticker):
    ticker = ticker.upper().strip()
    parquet_path = os.path.join(CSV_FOLDER, f"{ticker}.parquet")

    # Step 1: Load existing Parquet (if exists)
    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df.dropna(subset=["Date"], inplace=True)
    else:
        df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

    # Step 2: Fetch last 6 months from Yahoo
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

        # Step 3: Merge (avoid duplicates)
        if not df.empty:
            merged_df = pd.concat([df, new_df]).drop_duplicates(subset=["Date"], keep="last")
        else:
            merged_df = new_df

        # Step 4: Sort and save back
        merged_df.sort_values("Date", inplace=True)
        merged_df.reset_index(drop=True, inplace=True)
        
        # Convert types for Parquet compatibility
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce")
        
        merged_df.to_parquet(parquet_path, index=False, engine="pyarrow")
        df = merged_df

        print(f"✅ Synced {ticker} (6mo history merged, {len(df)} records)")
    except Exception as e:
        print(f"⚠️ Error updating history for {ticker}: {e}")
        return df if not df.empty else None

    # Step 5: Final cleaning
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

            title = content.get("title", "No Title")
            link = canonical_url.get("url", "")
            publisher = provider.get("displayName", "Unknown")
            summary = content.get("summary", "")

            thumbnail_url = ""
            if thumbnail_data:
                resolutions = thumbnail_data.get("resolutions", [])
                if resolutions:
                    thumbnail_url = resolutions[0].get("url", "")

            news_items.append({
                "title": title,
                "link": link,
                "publisher": publisher,
                "summary": summary,
                "thumbnail": thumbnail_url,
            })

        news_cache[ticker] = {"time": time.time(), "data": news_items}
        return news_items

    except Exception as e:
        return [{
            "title": "Error fetching news",
            "link": "",
            "publisher": str(e),
            "summary": "",
            "thumbnail": "",
        }]


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