# # # live_price_worker.py
# # import asyncio
# # import threading
# # import time
# # import os
# # import pandas as pd
# # import yfinance as yf
# # from datetime import datetime
# # from PyQt5.QtCore import QThread, pyqtSignal


# # class LivePriceWorker(QThread):
# #     price_update = pyqtSignal(str, float)
# #     error = pyqtSignal(str)

# #     def __init__(self, ticker):
# #         super().__init__()
# #         self._last_emit_ts = 0.0
# #         self._emit_interval = 0.5   # seconds between UI emits
# #         self._last_csv_write_ts = 0.0
# #         self._csv_write_interval = 5.0  # seconds between file writes
# #         self._pending_price_for_csv = None
# #         self.ticker = ticker.upper().strip()
# #         self.loop = None
# #         self.websocket = None
# #         self.running = True
# #         self.csv_path = f"./csv_data_files/{self.ticker}.csv"
# #         self.ohlc_thread = None

# #     # -------------------------------------------------------------------
# #     # Handle incoming WebSocket messages
# #     # -------------------------------------------------------------------
# #     async def _message_handler(self, data):
# #         try:
# #             price = None
# #             if "id" in data and "price" in data:
# #                 price = data["price"]
# #             elif "id" in data and "regularMarketPrice" in data:
# #                 price = data["regularMarketPrice"]

# #             if price is None:
# #                 return

# #             now = time.time()

# #             # Buffer the latest price for UI emitting (throttled)
# #             if now - self._last_emit_ts >= self._emit_interval:
# #                 self._last_emit_ts = now
# #                 try:
# #                     self.price_update.emit(self.ticker, float(price))
# #                 except Exception:
# #                     pass

# #             # Buffer price for eventual CSV write (less frequent)
# #             self._pending_price_for_csv = float(price)
# #             if now - self._last_csv_write_ts >= self._csv_write_interval:
# #                 self._last_csv_write_ts = now
# #                 # perform CSV write synchronously here (worker thread, OK)
# #                 self._update_close_price(float(price))

# #         except Exception as e:
# #             self.error.emit(f"Error parsing message: {e}")

# #     # -------------------------------------------------------------------
# #     # Update Close price in CSV (from WebSocket)
# #     # -------------------------------------------------------------------
# #     def _update_close_price(self, price: float):
# #         try:
# #             if not os.path.exists(self.csv_path):
# #                 return

# #             df = pd.read_csv(self.csv_path)
# #             today = datetime.now().strftime("%Y-%m-%d")

# #             if not df.empty and df.iloc[-1]["Date"] == today:
# #                 df.loc[df.index[-1], "Close"] = price
# #             else:
# #                 df.loc[len(df)] = [today, "", "", "", price, ""]

# #             df.to_csv(self.csv_path, index=False)
# #         except Exception as e:
# #             self.error.emit(f"Error updating CSV with price: {e}")

# #     # -------------------------------------------------------------------
# #     # Periodic OHLCV Updater (background thread)
# #     # -------------------------------------------------------------------
# #     def _periodic_ohlc_updater(self):
# #         """Fetch OHLCV data every 5 minutes, respecting rate limits"""
# #         while self.running:
# #             try:
# #                 if not os.path.exists(self.csv_path):
# #                     time.sleep(60)
# #                     continue

# #                 df_latest = yf.download(
# #                     self.ticker, period="1d", interval="1m", progress=False
# #                 )

# #                 if not df_latest.empty:
# #                     latest_row = df_latest.iloc[-1]

# #                     # Safely extract values
# #                     o = float(latest_row["Open"])
# #                     h = float(latest_row["High"])
# #                     l = float(latest_row["Low"])
# #                     c = float(latest_row["Close"])
# #                     v = float(latest_row["Volume"])

# #                     df = pd.read_csv(self.csv_path)

# #                     # Clean up any unnamed columns
# #                     df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

# #                     today = datetime.now().strftime("%Y-%m-%d")

# #                     # Ensure columns exist
# #                     for col in ["Open", "High", "Low", "Close", "Volume"]:
# #                         if col not in df.columns:
# #                             df[col] = ""

# #                     # Update today's OHLCV
# #                     if not df.empty and df.iloc[-1]["Date"] == today:
# #                         df.at[df.index[-1], "Open"] = o
# #                         df.at[df.index[-1], "High"] = h
# #                         df.at[df.index[-1], "Low"] = l
# #                         df.at[df.index[-1], "Close"] = c
# #                         df.at[df.index[-1], "Volume"] = v
# #                     else:
# #                         df.loc[len(df)] = [today, o, h, l, c, v]

# #                     df.to_csv(self.csv_path, index=False)

# #             except Exception as e:
# #                 if self.running:  # Only emit error if still running
# #                     self.error.emit(f"OHLC updater error: {e}")

# #             # Sleep in small chunks to allow for faster shutdown
# #             for _ in range(60):  # 60 * 5 = 300 seconds (5 minutes)
# #                 if not self.running:
# #                     break
# #                 time.sleep(5)

# #     # -------------------------------------------------------------------
# #     # Async WebSocket Runner
# #     # -------------------------------------------------------------------
# #     async def _run_async(self):
# #         try:
# #             from yfinance import AsyncWebSocket
            
# #             self.websocket = AsyncWebSocket(
# #                 url="wss://streamer.finance.yahoo.com/?version=2", 
# #                 verbose=False
# #             )
# #             await self.websocket.subscribe(self.ticker)
            
# #             # Listen with timeout to allow checking self.running
# #             while self.running:
# #                 try:
# #                     await asyncio.wait_for(
# #                         self.websocket.listen(self._message_handler),
# #                         timeout=1.0
# #                     )
# #                 except asyncio.TimeoutError:
# #                     continue
                    
# #         except Exception as e:
# #             if self.running:  # Only emit error if still running
# #                 self.error.emit(str(e))

# #     # -------------------------------------------------------------------
# #     # Thread run method
# #     # -------------------------------------------------------------------
# #     def run(self):
# #         try:
# #             # Start OHLC updater in a separate daemon thread
# #             self.ohlc_thread = threading.Thread(
# #                 target=self._periodic_ohlc_updater, 
# #                 daemon=True
# #             )
# #             self.ohlc_thread.start()

# #             # Start event loop for WebSocket
# #             self.loop = asyncio.new_event_loop()
# #             asyncio.set_event_loop(self.loop)
# #             self.loop.run_until_complete(self._run_async())
            
# #         except Exception as e:
# #             if self.running:
# #                 self.error.emit(f"WebSocket loop error: {e}")
# #         finally:
# #             # Clean up the event loop
# #             if self.loop:
# #                 try:
# #                     self.loop.close()
# #                 except:
# #                     pass

# #     # -------------------------------------------------------------------
# #     # Graceful stop
# #     # -------------------------------------------------------------------
# #     def stop(self):
# #         """Stop the worker gracefully"""
# #         print(f"🛑 Stopping LivePriceWorker for {self.ticker}...")
# #         self.running = False
        
# #         # Stop the event loop if it's running
# #         if self.loop and self.loop.is_running():
# #             self.loop.call_soon_threadsafe(self.loop.stop)
        
# #         # Close websocket if connected
# #         if self.websocket:
# #             try:
# #                 asyncio.run_coroutine_threadsafe(
# #                     self.websocket.close(), 
# #                     self.loop
# #                 )
# #             except:
# #                 pass
        
# #         print(f"✓ LivePriceWorker for {self.ticker} stopped")

# # live_price_worker.py
# import asyncio
# import threading
# import time
# import os
# import pandas as pd
# import yfinance as yf
# from datetime import datetime
# from PyQt5.QtCore import QThread, pyqtSignal


# class LivePriceWorker(QThread):
#     price_update = pyqtSignal(str, float)
#     error = pyqtSignal(str)

#     def __init__(self, ticker):
#         super().__init__()
#         self._last_emit_ts = 0.0
#         self._emit_interval = 0.5
#         self._last_parquet_write_ts = 0.0
#         self._parquet_write_interval = 5.0
#         self._pending_price_for_parquet = None
#         self.ticker = ticker.upper().strip()
#         self.loop = None
#         self.websocket = None
#         self.running = True
#         self.parquet_path = f"./csv_data_files/{self.ticker}.parquet"
#         self.ohlc_thread = None
#         self._df_cache = None  # Cache DataFrame in memory
#         self._df_cache_time = 0.0
#         self._df_cache_ttl = 10.0  # Refresh cache every 10 seconds

#     def _get_cached_df(self):
#         """Get DataFrame from cache or load from disk"""
#         now = time.time()
#         if self._df_cache is None or (now - self._df_cache_time) > self._df_cache_ttl:
#             if os.path.exists(self.parquet_path):
#                 self._df_cache = pd.read_parquet(self.parquet_path)
#                 self._df_cache_time = now
#             else:
#                 self._df_cache = None
#         return self._df_cache

#     def _save_df(self, df):
#         """Save DataFrame and update cache"""
#         df.to_parquet(self.parquet_path, index=False, engine="pyarrow")
#         self._df_cache = df
#         self._df_cache_time = time.time()

#     async def _message_handler(self, data):
#         try:
#             price = None
#             if "id" in data and "price" in data:
#                 price = data["price"]
#             elif "id" in data and "regularMarketPrice" in data:
#                 price = data["regularMarketPrice"]

#             if price is None:
#                 return

#             now = time.time()

#             if now - self._last_emit_ts >= self._emit_interval:
#                 self._last_emit_ts = now
#                 try:
#                     self.price_update.emit(self.ticker, float(price))
#                 except Exception:
#                     pass

#             self._pending_price_for_parquet = float(price)
#             if now - self._last_parquet_write_ts >= self._parquet_write_interval:
#                 self._last_parquet_write_ts = now
#                 self._update_close_price(float(price))

#         except Exception as e:
#             self.error.emit(f"Error parsing message: {e}")

#     def _update_close_price(self, price: float):
#         try:
#             df = self._get_cached_df()
#             if df is None:
#                 return

#             today = datetime.now().strftime("%Y-%m-%d")
#             df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

#             if not df.empty and df.iloc[-1]["Date"] == today:
#                 df.loc[df.index[-1], "Close"] = price
#             else:
#                 new_row = pd.DataFrame([{
#                     "Date": today, "Open": None, "High": None, 
#                     "Low": None, "Close": price, "Volume": None
#                 }])
#                 df = pd.concat([df, new_row], ignore_index=True)

#             # Ensure proper types before saving
#             for col in ["Open", "High", "Low", "Close", "Volume"]:
#                 df[col] = pd.to_numeric(df[col], errors="coerce")
            
#             self._save_df(df)
#         except Exception as e:
#             self.error.emit(f"Error updating Parquet with price: {e}")

#     def _periodic_ohlc_updater(self):
#         """Fetch OHLCV data every 5 minutes"""
#         while self.running:
#             try:
#                 df = self._get_cached_df()
#                 if df is None:
#                     time.sleep(60)
#                     continue

#                 df_latest = yf.download(
#                     self.ticker, period="1d", interval="1m", progress=False
#                 )

#                 if not df_latest.empty:
#                     latest_row = df_latest.iloc[-1]

#                     o = float(latest_row["Open"])
#                     h = float(latest_row["High"])
#                     l = float(latest_row["Low"])
#                     c = float(latest_row["Close"])
#                     v = float(latest_row["Volume"])

#                     today = datetime.now().strftime("%Y-%m-%d")
#                     df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

#                     if not df.empty and df.iloc[-1]["Date"] == today:
#                         df.at[df.index[-1], "Open"] = o
#                         df.at[df.index[-1], "High"] = h
#                         df.at[df.index[-1], "Low"] = l
#                         df.at[df.index[-1], "Close"] = c
#                         df.at[df.index[-1], "Volume"] = v
#                     else:
#                         new_row = pd.DataFrame([{
#                             "Date": today, "Open": o, "High": h,
#                             "Low": l, "Close": c, "Volume": v
#                         }])
#                         df = pd.concat([df, new_row], ignore_index=True)

#                     # Ensure proper types
#                     for col in ["Open", "High", "Low", "Close", "Volume"]:
#                         df[col] = pd.to_numeric(df[col], errors="coerce")

#                     self._save_df(df)

#             except Exception as e:
#                 if self.running:
#                     self.error.emit(f"OHLC updater error: {e}")

#             for _ in range(60):
#                 if not self.running:
#                     break
#                 time.sleep(5)

#     async def _run_async(self):
#         try:
#             from yfinance import AsyncWebSocket
            
#             self.websocket = AsyncWebSocket(
#                 url="wss://streamer.finance.yahoo.com/?version=2", 
#                 verbose=False
#             )
#             await self.websocket.subscribe(self.ticker)
            
#             while self.running:
#                 try:
#                     await asyncio.wait_for(
#                         self.websocket.listen(self._message_handler),
#                         timeout=1.0
#                     )
#                 except asyncio.TimeoutError:
#                     continue
                    
#         except Exception as e:
#             if self.running:
#                 self.error.emit(str(e))

#     def run(self):
#         try:
#             self.ohlc_thread = threading.Thread(
#                 target=self._periodic_ohlc_updater, 
#                 daemon=True
#             )
#             self.ohlc_thread.start()

#             self.loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(self.loop)
#             self.loop.run_until_complete(self._run_async())
            
#         except Exception as e:
#             if self.running:
#                 self.error.emit(f"WebSocket loop error: {e}")
#         finally:
#             if self.loop:
#                 try:
#                     self.loop.close()
#                 except:
#                     pass

#     def stop(self):
#         """Stop the worker gracefully"""
#         print(f"🛑 Stopping LivePriceWorker for {self.ticker}...")
#         self.running = False
        
#         if self.loop and self.loop.is_running():
#             self.loop.call_soon_threadsafe(self.loop.stop)
        
#         if self.websocket:
#             try:
#                 asyncio.run_coroutine_threadsafe(
#                     self.websocket.close(), 
#                     self.loop
#                 )
#             except:
#                 pass
        
#         print(f"✓ LivePriceWorker for {self.ticker} stopped")

# live_price_worker.py
import asyncio
import threading
import time
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal


class LivePriceWorker(QThread):
    price_update = pyqtSignal(str, float)
    error = pyqtSignal(str)

    def __init__(self, ticker):
        super().__init__()
        self._last_emit_ts = 0.0
        self._emit_interval = 0.5
        self._last_parquet_write_ts = 0.0
        self._parquet_write_interval = 5.0
        self._pending_price = None
        self.ticker = ticker.upper().strip()
        self.loop = None
        self.websocket = None
        self.running = True
        self.parquet_path = f"./csv_data_files/{self.ticker}.parquet"
        self.ohlc_thread = None
        self._df_cache = None
        self._df_cache_time = 0.0
        self._df_cache_ttl = 10.0

    def _get_cached_df(self):
        """Get DataFrame from cache or load from disk"""
        now = time.time()
        if self._df_cache is None or (now - self._df_cache_time) > self._df_cache_ttl:
            if os.path.exists(self.parquet_path):
                self._df_cache = pd.read_parquet(self.parquet_path)
                self._df_cache_time = now
            else:
                self._df_cache = None
        return self._df_cache

    def _save_df(self, df):
        """Save DataFrame and update cache"""
        df.to_parquet(self.parquet_path, index=False, engine="pyarrow")
        self._df_cache = df
        self._df_cache_time = time.time()

    def _safe_float(self, val):
        """Safely convert value to float, handling Series"""
        if hasattr(val, 'iloc'):
            return float(val.iloc[0])
        return float(val)

    async def _message_handler(self, data):
        try:
            price = None
            if "id" in data and "price" in data:
                price = data["price"]
            elif "id" in data and "regularMarketPrice" in data:
                price = data["regularMarketPrice"]

            if price is None:
                return

            now = time.time()

            if now - self._last_emit_ts >= self._emit_interval:
                self._last_emit_ts = now
                try:
                    self.price_update.emit(self.ticker, float(price))
                except Exception:
                    pass

            self._pending_price = float(price)
            if now - self._last_parquet_write_ts >= self._parquet_write_interval:
                self._last_parquet_write_ts = now
                self._update_close_price(float(price))

        except Exception as e:
            self.error.emit(f"Error parsing message: {e}")

    def _update_close_price(self, price: float):
        try:
            df = self._get_cached_df()
            if df is None:
                return

            today = datetime.now().strftime("%Y-%m-%d")
            
            # Ensure Date column is string for comparison
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

            if not df.empty and str(df.iloc[-1]["Date"]) == today:
                df.loc[df.index[-1], "Close"] = price
            else:
                new_row = pd.DataFrame([{
                    "Date": today, "Open": None, "High": None,
                    "Low": None, "Close": price, "Volume": None
                }])
                df = pd.concat([df, new_row], ignore_index=True)

            for col in ["Open", "High", "Low", "Close", "Volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            self._save_df(df)
        except Exception as e:
            self.error.emit(f"Error updating Parquet with price: {e}")

    def _periodic_ohlc_updater(self):
        """Fetch OHLCV data every 5 minutes"""
        while self.running:
            try:
                df = self._get_cached_df()
                if df is None:
                    time.sleep(60)
                    continue

                df_latest = yf.download(
                    self.ticker, period="1d", interval="1m", progress=False
                )

                if not df_latest.empty:
                    latest_row = df_latest.iloc[-1]

                    # Use safe_float to handle Series properly
                    o = self._safe_float(latest_row["Open"])
                    h = self._safe_float(latest_row["High"])
                    l = self._safe_float(latest_row["Low"])
                    c = self._safe_float(latest_row["Close"])
                    v = self._safe_float(latest_row["Volume"])

                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    # Ensure Date is string for comparison
                    if "Date" in df.columns:
                        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

                    if not df.empty and str(df.iloc[-1]["Date"]) == today:
                        df.at[df.index[-1], "Open"] = o
                        df.at[df.index[-1], "High"] = h
                        df.at[df.index[-1], "Low"] = l
                        df.at[df.index[-1], "Close"] = c
                        df.at[df.index[-1], "Volume"] = v
                    else:
                        new_row = pd.DataFrame([{
                            "Date": today, "Open": o, "High": h,
                            "Low": l, "Close": c, "Volume": v
                        }])
                        df = pd.concat([df, new_row], ignore_index=True)

                    for col in ["Open", "High", "Low", "Close", "Volume"]:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors="coerce")

                    self._save_df(df)

            except Exception as e:
                if self.running:
                    self.error.emit(f"OHLC updater error: {e}")

            for _ in range(60):
                if not self.running:
                    break
                time.sleep(5)

    async def _run_async(self):
        try:
            from yfinance import AsyncWebSocket

            self.websocket = AsyncWebSocket(
                url="wss://streamer.finance.yahoo.com/?version=2",
                verbose=False
            )
            await self.websocket.subscribe(self.ticker)

            while self.running:
                try:
                    await asyncio.wait_for(
                        self.websocket.listen(self._message_handler),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

        except Exception as e:
            if self.running:
                self.error.emit(str(e))

    def run(self):
        try:
            self.ohlc_thread = threading.Thread(
                target=self._periodic_ohlc_updater,
                daemon=True
            )
            self.ohlc_thread.start()

            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._run_async())

        except Exception as e:
            if self.running:
                self.error.emit(f"WebSocket loop error: {e}")
        finally:
            if self.loop:
                try:
                    self.loop.close()
                except:
                    pass

    def stop(self):
        """Stop the worker gracefully"""
        print(f"🛑 Stopping LivePriceWorker for {self.ticker}...")
        self.running = False

        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

        if self.websocket:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.close(),
                    self.loop
                )
            except:
                pass

        print(f"✓ LivePriceWorker for {self.ticker} stopped")