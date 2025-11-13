# live_price_worker.py
import asyncio
import threading
import time
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from yfinance import AsyncWebSocket


class LivePriceWorker(QThread):
    price_update = pyqtSignal(str, float)
    error = pyqtSignal(str)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker.upper().strip()
        self.loop = None
        self.websocket = None
        self.running = True
        self.csv_path = f"./csv_data_files/{self.ticker}.csv"

    # -------------------------------------------------------------------
    # Handle incoming WebSocket messages
    # -------------------------------------------------------------------
    async def _message_handler(self, data):
        try:
            price = None
            if "id" in data and "price" in data:
                price = data["price"]
            elif "id" in data and "regularMarketPrice" in data:
                price = data["regularMarketPrice"]

            if price:
                self.price_update.emit(self.ticker, float(price))
                self._update_close_price(float(price))

        except Exception as e:
            self.error.emit(f"Error parsing message: {e}")

    # -------------------------------------------------------------------
    # Update Close price in CSV (from WebSocket)
    # -------------------------------------------------------------------
    def _update_close_price(self, price: float):
        try:
            if not os.path.exists(self.csv_path):
                return

            df = pd.read_csv(self.csv_path)
            today = datetime.now().strftime("%Y-%m-%d")

            if not df.empty and df.iloc[-1]["Date"] == today:
                df.loc[df.index[-1], "Close"] = price
            else:
                df.loc[len(df)] = [today, "", "", "", price, ""]

            df.to_csv(self.csv_path, index=False)
        except Exception as e:
            self.error.emit(f"Error updating CSV with price: {e}")

    # -------------------------------------------------------------------
    # Periodic OHLCV Updater (background thread)
    # -------------------------------------------------------------------
    def _periodic_ohlc_updater(self):
        """Fetch OHLCV data every 5–10 minutes, respecting rate limits"""
        while self.running:
            try:
                if not os.path.exists(self.csv_path):
                    time.sleep(60)
                    continue

                df_latest = yf.download(
                    self.ticker, period="1d", interval="1m", progress=False
                )

                if not df_latest.empty:
                    latest_row = df_latest.iloc[-1]

                    # Safely extract values
                    o = float(latest_row["Open"])
                    h = float(latest_row["High"])
                    l = float(latest_row["Low"])
                    c = float(latest_row["Close"])
                    v = float(latest_row["Volume"])

                    df = pd.read_csv(self.csv_path)

                    # Clean up any unnamed columns
                    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

                    today = datetime.now().strftime("%Y-%m-%d")

                    # Ensure columns exist
                    for col in ["Open", "High", "Low", "Close", "Volume"]:
                        if col not in df.columns:
                            df[col] = ""

                    # Update today's OHLCV
                    if not df.empty and df.iloc[-1]["Date"] == today:
                        df.at[df.index[-1], "Open"] = o
                        df.at[df.index[-1], "High"] = h
                        df.at[df.index[-1], "Low"] = l
                        df.at[df.index[-1], "Close"] = c
                        df.at[df.index[-1], "Volume"] = v
                    else:
                        df.loc[len(df)] = [today, o, h, l, c, v]

                    df.to_csv(self.csv_path, index=False)

            except Exception as e:
                self.error.emit(f"OHLC updater error: {e}")

            time.sleep(300)  # every 5 minutes


    # -------------------------------------------------------------------
    # Async WebSocket Runner
    # -------------------------------------------------------------------
    async def _run_async(self):
        try:
            self.websocket = AsyncWebSocket(url="wss://streamer.finance.yahoo.com/?version=2", verbose=False)
            await self.websocket.subscribe(self.ticker)
            await self.websocket.listen(self._message_handler)
        except Exception as e:
            self.error.emit(str(e))

    # -------------------------------------------------------------------
    # Thread run method
    # -------------------------------------------------------------------
    def run(self):
        try:
            # Start OHLC updater in a separate daemon thread
            threading.Thread(target=self._periodic_ohlc_updater, daemon=True).start()

            # Start event loop for WebSocket
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._run_async())
        except Exception as e:
            self.error.emit(f"WebSocket loop error: {e}")

    # -------------------------------------------------------------------
    # Graceful stop
    # -------------------------------------------------------------------
    def stop(self):
        self.running = False
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
