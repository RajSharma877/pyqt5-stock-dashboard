# import mplfinance as mpf
# import numpy as np
# import matplotlib.pyplot as plt
# from PyQt5.QtWidgets import (
#     QVBoxLayout, QWidget, QHBoxLayout, QLabel, 
#     QPushButton, QFrame, QGridLayout, QSizePolicy, QApplication
# )
# from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
# from PyQt5.QtGui import QFont
# from matplotlib.backends.backend_qt5agg import (
#     FigureCanvasQTAgg as FigureCanvas,
#     NavigationToolbar2QT as NavigationToolbar,
# )
# from matplotlib.figure import Figure
# import matplotlib.lines as mlines
# import pandas as pd
# from scipy.signal import argrelextrema
# from matplotlib import rcParams
# from functools import lru_cache


# # ============================================================================
# # OPTIMIZED INDICATOR CALCULATIONS WITH CACHING
# # ============================================================================

# @lru_cache(maxsize=32)
# def calculate_rsi_cached(data_hash, period=14):
#     """Cached RSI calculation"""
#     # Note: You'll pass a hash of the data, not the series itself
#     pass

# def calculate_rsi(series, period=14):
#     """Optimized RSI calculation"""
#     delta = series.diff()
#     gain = delta.where(delta > 0, 0)
#     loss = -delta.where(delta < 0, 0)
    
#     # Use exponential moving average for better performance
#     avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
#     avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#     return rsi


# def calculate_macd(series, short=12, long=26, signal=9):
#     """Optimized MACD calculation"""
#     short_ema = series.ewm(span=short, adjust=False).mean()
#     long_ema = series.ewm(span=long, adjust=False).mean()
#     macd = short_ema - long_ema
#     signal_line = macd.ewm(span=signal, adjust=False).mean()
#     hist = macd - signal_line
#     return macd, signal_line, hist


# # ============================================================================
# # BACKGROUND CHART WORKER THREAD
# # ============================================================================

# class ChartWorker(QThread):
#     """Worker thread for chart rendering to prevent UI blocking"""
#     finished = pyqtSignal(object)  # Emits the prepared figure
#     error = pyqtSignal(str)
    
#     def __init__(self, df, ticker, options, colors, is_dark):
#         super().__init__()
#         self.df = df.copy()
#         self.ticker = ticker
#         self.options = options
#         self.colors = colors
#         self.is_dark = is_dark
        
#     def run(self):
#         try:
#             # Prepare data in background
#             prepared_data = self.prepare_chart_data()
#             self.finished.emit(prepared_data)
#         except Exception as e:
#             self.error.emit(str(e))
    
#     def prepare_chart_data(self):
#         """Prepare all chart data without creating the actual figure"""
#         df = self.df
#         options = self.options
        
#         # Calculate indicators only if needed
#         indicators = {}
        
#         if options['show_sma']:
#             indicators['SMA_20'] = df['Close'].rolling(window=20).mean()
        
#         if options['show_ema']:
#             indicators['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        
#         if options['show_bb']:
#             bb_mid = df['Close'].rolling(window=20).mean()
#             bb_std = df['Close'].rolling(window=20).std()
#             indicators['BB_UPPER'] = bb_mid + (2 * bb_std)
#             indicators['BB_LOWER'] = bb_mid - (2 * bb_std)
        
#         if options['show_sr']:
#             close_prices = df['Close'].values
#             indicators['local_max'] = argrelextrema(close_prices, np.greater, order=10)[0]
#             indicators['local_min'] = argrelextrema(close_prices, np.less, order=10)[0]
        
#         if options['show_rsi']:
#             indicators['RSI'] = calculate_rsi(df['Close'])
        
#         if options['show_macd']:
#             macd, signal, hist = calculate_macd(df['Close'])
#             indicators['MACD'] = macd
#             indicators['Signal'] = signal
#             indicators['Hist'] = hist
        
#         return {
#             'df': df,
#             'indicators': indicators,
#             'ticker': self.ticker,
#             'options': options
#         }


# # ============================================================================
# # OPTIMIZED TOOLBAR POPOVER
# # ============================================================================

# class ToolbarPopover(QFrame):
#     """Lightweight popover for chart tools"""
    
#     def __init__(self, parent=None, is_dark=False, navigation_toolbar=None):
#         super().__init__(parent)
#         self.is_dark = is_dark
#         self.navigation_toolbar = navigation_toolbar
#         self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
#         self.setFixedSize(300, 280)
        
#         self.setup_ui()
#         self.apply_styling()
    
#     def setup_ui(self):
#         """Setup UI components"""
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(16, 16, 16, 16)
#         layout.setSpacing(12)
        
#         # Title
#         title_label = QLabel("Chart Tools")
#         title_label.setObjectName("popover_title")
#         title_font = QFont("Inter", 14, QFont.Bold)
#         title_label.setFont(title_font)
#         layout.addWidget(title_label)
        
#         # Tools grid
#         tools_frame = QFrame()
#         tools_frame.setObjectName("tools_container")
#         tools_layout = QGridLayout(tools_frame)
#         tools_layout.setHorizontalSpacing(12)
#         tools_layout.setVerticalSpacing(12)
        
#         self.create_tool_buttons(tools_layout)
#         layout.addWidget(tools_frame, alignment=Qt.AlignCenter)
#         layout.addStretch()
    
#     def create_tool_buttons(self, layout):
#         """Create tool buttons grid"""
#         tools = [
#             ("🏠", "Home", "Reset view", self.home),
#             ("◀", "Back", "Previous view", self.back),
#             ("▶", "Forward", "Next view", self.forward),
#             ("🔎", "Zoom", "Zoom mode", self.zoom),
#             ("⚙️", "Config", "Configure", self.configure),
#         ]
        
#         for i, (icon, name, tooltip, callback) in enumerate(tools):
#             btn = QPushButton(f"{icon}")
#             btn.setObjectName("tool_button")
#             btn.setToolTip(f"{name}: {tooltip}")
#             btn.setFixedSize(45, 45)
#             btn.clicked.connect(callback)
#             layout.addWidget(btn, i // 3, i % 3, alignment=Qt.AlignCenter)
    
#     def home(self):
#         if self.navigation_toolbar:
#             self.navigation_toolbar.home()
#         self.hide()
    
#     def back(self):
#         if self.navigation_toolbar:
#             self.navigation_toolbar.back()
#         self.hide()
    
#     def forward(self):
#         if self.navigation_toolbar:
#             self.navigation_toolbar.forward()
#         self.hide()
    
#     def zoom(self):
#         if self.navigation_toolbar:
#             self.navigation_toolbar.zoom()
#         self.hide()
    
#     def configure(self):
#         if self.navigation_toolbar:
#             self.navigation_toolbar.configure_subplots()
#         self.hide()
    
#     def apply_styling(self):
#         """Apply theme styling"""
#         if self.is_dark:
#             self.setStyleSheet("""
#                 ToolbarPopover {
#                     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                                 stop: 0 #1e293b, stop: 1 #0f172a);
#                     border: 2px solid #334155;
#                     border-radius: 16px;
#                 }
#                 QLabel#popover_title {
#                     color: #f1f5f9;
#                     background: transparent;
#                 }
#                 QPushButton#tool_button {
#                     background: #334155;
#                     border: 1px solid #475569;
#                     border-radius: 8px;
#                     color: #e2e8f0;
#                     font-size: 16px;
#                 }
#                 QPushButton#tool_button:hover {
#                     background: #3b82f6;
#                     border: 1px solid #2563eb;
#                 }
#             """)
#         else:
#             self.setStyleSheet("""
#                 ToolbarPopover {
#                     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                                 stop: 0 #ffffff, stop: 1 #f8fafc);
#                     border: 2px solid #e2e8f0;
#                     border-radius: 16px;
#                 }
#                 QLabel#popover_title {
#                     color: #111827;
#                     background: transparent;
#                 }
#                 QPushButton#tool_button {
#                     background: #ffffff;
#                     border: 1px solid #d1d5db;
#                     border-radius: 8px;
#                     color: #374151;
#                     font-size: 16px;
#                 }
#                 QPushButton#tool_button:hover {
#                     background: #3b82f6;
#                     color: #ffffff;
#                 }
#             """)
    
#     def show_at_position(self, parent_widget, button_rect):
#         """Show popover below button"""
#         parent_global = parent_widget.mapToGlobal(button_rect.bottomLeft())
#         x = parent_global.x() - self.width() + button_rect.width()
#         y = parent_global.y() + 8
#         self.move(x, y)
#         self.show()
#         self.raise_()


# # ============================================================================
# # OPTIMIZED CHART WIDGET
# # ============================================================================

# class ChartWidget(QWidget):
#     theme_changed = pyqtSignal(bool)
    
#     def __init__(self, parent=None, is_dark=False):
#         super().__init__(parent)
#         self.is_dark = is_dark
#         self.canvas = None
#         self.toolbar = None
#         self.current_ticker = ""
#         self.popover = None
#         self.worker = None
#         self.cursor = None  # Store cursor reference
        
#         # Cache for last plot data
#         self.last_df = None
#         self._last_options = {}
        
#         # Setup UI
#         self.layout = QVBoxLayout(self)
#         self.layout.setSpacing(8)
#         self.layout.setContentsMargins(0, 0, 0, 0)
        
#         self.create_compact_header()
#         self.apply_theme()
    
#     def create_compact_header(self):
#         """Create compact header with absolute positioning"""
#         self.header_frame = QFrame()
#         self.header_frame.setObjectName("chart_header")
#         self.header_frame.setFixedHeight(100)
#         self.header_frame.resizeEvent = self.header_resize_event
        
#         # Title
#         self.title_label = QLabel("Candlestick Chart", self.header_frame)
#         self.title_label.setObjectName("chart_title")
#         self.title_label.setFont(QFont("Inter", 16, QFont.Bold))
#         self.title_label.setFixedSize(330, 55)
        
#         # Subtitle
#         self.subtitle_label = QLabel("Select a ticker", self.header_frame)
#         self.subtitle_label.setObjectName("chart_subtitle")
#         self.subtitle_label.setFont(QFont("Inter", 11))
#         self.subtitle_label.setFixedSize(220, 45)
        
#         # Tools button
#         self.tools_button = QPushButton("🛠️ Tools", self.header_frame)
#         self.tools_button.setObjectName("tools_button")
#         self.tools_button.setFixedSize(120, 45)
#         self.tools_button.clicked.connect(self.toggle_tools_popover)
        
#         self.layout.addWidget(self.header_frame)
#         self.position_header_elements()
    
#     def header_resize_event(self, event):
#         """Handle header resize"""
#         super(QFrame, self.header_frame).resizeEvent(event)
#         self.position_header_elements()
    
#     def position_header_elements(self):
#         """Position header elements absolutely"""
#         if not hasattr(self, 'title_label'):
#             return
        
#         header_height = self.header_frame.height()
        
#         # Position title and subtitle
#         title_h = self.title_label.height()
#         subtitle_h = self.subtitle_label.height()
#         total_h = title_h + subtitle_h
#         y_pos = (header_height - total_h) // 4
        
#         self.title_label.move(16, y_pos)
#         self.subtitle_label.move(16, y_pos + title_h)
        
#         # Position tools button
#         button_width = self.tools_button.width()
#         button_height = self.tools_button.height()
#         x_pos = self.header_frame.width() - button_width - 16
#         y_pos = (header_height - button_height) // 2
#         self.tools_button.move(x_pos, y_pos)
    
#     def toggle_tools_popover(self):
#         """Toggle tools popover"""
#         if self.popover and self.popover.isVisible():
#             self.popover.hide()
#         else:
#             if not self.popover:
#                 self.popover = ToolbarPopover(self, self.is_dark, self.toolbar)
            
#             self.popover.navigation_toolbar = self.toolbar
#             button_rect = self.tools_button.geometry()
#             self.popover.show_at_position(self, button_rect)
    
#     def apply_theme(self):
#         """Apply theme styling"""
#         if self.is_dark:
#             self.apply_dark_theme()
#         else:
#             self.apply_light_theme()
    
#     def apply_light_theme(self):
#         """Light theme configuration"""
#         plt.style.use("default")
#         rcParams.update({
#             "figure.facecolor": "#ffffff",
#             "axes.facecolor": "#ffffff",
#             "axes.edgecolor": "#e2e8f0",
#             "axes.labelcolor": "#374151",
#             "grid.color": "#f3f4f6",
#             "text.color": "#1f2937",
#             "font.family": "Inter",
#             "font.size": 10,
#         })
        
#         self.setStyleSheet("""
#             QFrame#chart_header {
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 #ffffff, stop: 1 #f8fafc);
#                 border: 1px solid #e5e7eb;
#                 border-radius: 12px;
#             }
#             QLabel#chart_title {
#                 color: #111827;
#                 background: transparent;
#             }
#             QLabel#chart_subtitle {
#                 color: #6b7280;
#                 background: transparent;
#             }
#             QPushButton#tools_button {
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 #f3f4f6, stop: 1 #e5e7eb);
#                 border: 1px solid #d1d5db;
#                 border-radius: 8px;
#                 color: #374151;
#                 font-weight: 600;
#             }
#             QPushButton#tools_button:hover {
#                 background: #3b82f6;
#                 color: #ffffff;
#             }
#         """)
    
#     def apply_dark_theme(self):
#         """Dark theme configuration"""
#         plt.style.use("dark_background")
#         rcParams.update({
#             "figure.facecolor": "#1e293b",
#             "axes.facecolor": "#1e293b",
#             "axes.edgecolor": "#475569",
#             "axes.labelcolor": "#cbd5e1",
#             "grid.color": "#334155",
#             "text.color": "#e2e8f0",
#             "font.family": "Inter",
#             "font.size": 10,
#         })
        
#         self.setStyleSheet("""
#             QFrame#chart_header {
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 #1e293b, stop: 1 #0f172a);
#                 border: 1px solid #334155;
#                 border-radius: 12px;
#             }
#             QLabel#chart_title {
#                 color: #f1f5f9;
#                 background: transparent;
#             }
#             QLabel#chart_subtitle {
#                 color: #94a3b8;
#                 background: transparent;
#             }
#             QPushButton#tools_button {
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 #334155, stop: 1 #1e293b);
#                 border: 1px solid #475569;
#                 border-radius: 8px;
#                 color: #ffffff;
#                 font-weight: 600;
#             }
#             QPushButton#tools_button:hover {
#                 background: #3b82f6;
#                 color: #ffffff;
#             }
#         """)
    
#     @pyqtSlot(object)
#     def on_chart_data_ready(self, data):
#         """Handle prepared chart data from worker thread"""
#         try:
#             self.render_chart(data)
#         except Exception as e:
#             print(f"Error rendering chart: {e}")
#         finally:
#             if self.worker:
#                 self.worker.deleteLater()
#                 self.worker = None
    
#     @pyqtSlot(str)
#     def on_chart_error(self, error_msg):
#         """Handle chart preparation errors"""
#         print(f"Chart error: {error_msg}")
#         if self.worker:
#             self.worker.deleteLater()
#             self.worker = None
    
#     def plot_chart(self, df, ticker, show_sma=False, show_ema=False, 
#                    show_rsi=False, show_macd=False, show_bb=False, show_sr=False):
#         """Optimized chart plotting with background processing"""
        
#         # Cancel any existing worker
#         if self.worker and self.worker.isRunning():
#             self.worker.quit()
#             self.worker.wait()
        
#         # Cache parameters
#         self.last_df = df.copy()
#         self._last_options = {
#             'show_sma': show_sma,
#             'show_ema': show_ema,
#             'show_rsi': show_rsi,
#             'show_macd': show_macd,
#             'show_bb': show_bb,
#             'show_sr': show_sr,
#         }
#         self.current_ticker = ticker
        
#         # Update header immediately
#         self.update_header(df, ticker)
        
#         # Prepare DataFrame
#         df = df.copy()
#         df["Date"] = pd.to_datetime(df["Date"])
#         df.set_index("Date", inplace=True)
#         df.rename(columns=str.capitalize, inplace=True)
        
#         # Define colors
#         colors = {
#             "up": "#10b981" if self.is_dark else "#059669",
#             "down": "#ef4444" if self.is_dark else "#dc2626",
#             "volume": "#64748b",
#             "sma": "#3b82f6",
#             "ema": "#f59e0b",
#             "bb_upper": "#ef4444",
#             "bb_lower": "#10b981",
#             "rsi": "#8b5cf6",
#             "macd": "#06b6d4",
#             "signal": "#f59e0b",
#         }
        
#         # Start background worker
#         self.worker = ChartWorker(df, ticker, self._last_options, colors, self.is_dark)
#         self.worker.finished.connect(self.on_chart_data_ready)
#         self.worker.error.connect(self.on_chart_error)
#         self.worker.start()
    
#     def update_header(self, df, ticker):
#         """Update header with price information"""
#         self.title_label.setText(f"{ticker.upper()} Candlestick Chart")
        
#         try:
#             latest_price = df["Close"].iloc[-1]
#             price_change = df["Close"].iloc[-1] - df["Close"].iloc[-2] if len(df) > 1 else 0
#             change_pct = (price_change / df["Close"].iloc[-2] * 100) if len(df) > 1 else 0
            
#             if price_change >= 0:
#                 self.subtitle_label.setText(f"${latest_price:.2f} (+{change_pct:.1f}%)")
#                 color = "#059669" if not self.is_dark else "#10b981"
#             else:
#                 self.subtitle_label.setText(f"${latest_price:.2f} ({change_pct:.1f}%)")
#                 color = "#dc2626" if not self.is_dark else "#ef4444"
            
#             self.subtitle_label.setStyleSheet(f"color: {color}; font-weight: 600; background: transparent;")
#         except:
#             self.subtitle_label.setText(f"Loading {ticker.upper()}...")
    
#     def render_chart(self, data):
#         """Render the chart with prepared data - runs on main thread"""
#         df = data['df']
#         indicators = data['indicators']
#         options = data['options']
        
#         # Clean up old widgets efficiently
#         if self.canvas:
#             # Remove cursor to prevent memory leak
#             if self.cursor:
#                 self.cursor.remove()
#                 self.cursor = None
            
#             self.layout.removeWidget(self.canvas)
#             self.canvas.deleteLater()
#             self.canvas = None
        
#         if self.toolbar:
#             self.layout.removeWidget(self.toolbar)
#             self.toolbar.deleteLater()
#             self.toolbar = None
        
#         # Force garbage collection
#         QApplication.processEvents()
        
#         # Determine subplot layout
#         nrows = 2
#         if options['show_rsi']:
#             nrows += 1
#         if options['show_macd']:
#             nrows += 1
        
#         # Create figure with optimized settings
#         fig = Figure(figsize=(12, 10), dpi=100)
#         fig.patch.set_facecolor("#1e293b" if self.is_dark else "#ffffff")
#         fig.subplots_adjust(left=0.06, bottom=0.08, right=0.97, top=0.98, hspace=0.25)
        
#         # Height ratios
#         height_ratios = [4, 1]
#         if options['show_rsi']:
#             height_ratios.append(1)
#         if options['show_macd']:
#             height_ratios.append(1)
        
#         # Create subplots
#         gs = fig.add_gridspec(nrows, 1, height_ratios=height_ratios, hspace=0.25)
#         ax_main = fig.add_subplot(gs[0])
#         ax_vol = fig.add_subplot(gs[1], sharex=ax_main)
        
#         current_subplot = 2
#         ax_rsi = None
#         ax_macd = None
        
#         if options['show_rsi']:
#             ax_rsi = fig.add_subplot(gs[current_subplot], sharex=ax_main)
#             current_subplot += 1
        
#         if options['show_macd']:
#             ax_macd = fig.add_subplot(gs[current_subplot], sharex=ax_main)
        
#         # Build addplot list for indicators
#         add_plots = []
        
#         if 'SMA_20' in indicators:
#             df['SMA_20'] = indicators['SMA_20']
#             add_plots.append(mpf.make_addplot(df['SMA_20'], ax=ax_main, 
#                                              color="#3b82f6", width=2))
        
#         if 'EMA_20' in indicators:
#             df['EMA_20'] = indicators['EMA_20']
#             add_plots.append(mpf.make_addplot(df['EMA_20'], ax=ax_main, 
#                                              color="#f59e0b", width=2))
        
#         if 'BB_UPPER' in indicators:
#             df['BB_UPPER'] = indicators['BB_UPPER']
#             df['BB_LOWER'] = indicators['BB_LOWER']
#             add_plots += [
#                 mpf.make_addplot(df['BB_UPPER'], ax=ax_main, 
#                                 color="#ef4444", linestyle="--", width=1.5),
#                 mpf.make_addplot(df['BB_LOWER'], ax=ax_main, 
#                                 color="#10b981", linestyle="--", width=1.5),
#             ]
        
#         # Plot with mplfinance
#         colors = {
#             "up": "#10b981" if self.is_dark else "#059669",
#             "down": "#ef4444" if self.is_dark else "#dc2626",
#         }
        
#         market_colors = mpf.make_marketcolors(
#             up=colors["up"], down=colors["down"],
#             edge="inherit",
#             wick={"up": colors["up"], "down": colors["down"]},
#             volume="in",
#         )
        
#         style = mpf.make_mpf_style(
#             marketcolors=market_colors,
#             facecolor="#1e293b" if self.is_dark else "#ffffff",
#             figcolor="#1e293b" if self.is_dark else "#ffffff",
#             gridstyle="--",
#             gridcolor="#334155" if self.is_dark else "#f3f4f6",
#             y_on_right=False,
#         )
        
#         mpf.plot(df, type="candle", ax=ax_main, volume=ax_vol,
#                 addplot=add_plots if add_plots else [],
#                 style=style, warn_too_much_data=10000,
#                 datetime_format="%Y-%m-%d", xrotation=0)
        
#         # Style axes
#         ax_main.set_ylabel("Price ($)", fontweight="bold")
#         ax_main.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)
        
#         ax_vol.set_ylabel("Volume", fontweight="bold")
#         ax_vol.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)
        
#         # RSI subplot
#         if options['show_rsi'] and ax_rsi and 'RSI' in indicators:
#             df['RSI'] = indicators['RSI']
#             ax_rsi.plot(df.index, df['RSI'], color="#8b5cf6", linewidth=2)
#             ax_rsi.axhline(70, color="#ef4444", linestyle="--", alpha=0.8)
#             ax_rsi.axhline(30, color="#10b981", linestyle="--", alpha=0.8)
#             ax_rsi.fill_between(df.index, 30, 70, alpha=0.1, color="#8b5cf6")
#             ax_rsi.set_ylim(0, 100)
#             ax_rsi.set_ylabel("RSI", fontweight="bold")
#             ax_rsi.grid(True, alpha=0.4, linestyle="--")
        
#         # MACD subplot
#         if options['show_macd'] and ax_macd and 'MACD' in indicators:
#             df['MACD'] = indicators['MACD']
#             df['Signal'] = indicators['Signal']
#             df['Hist'] = indicators['Hist']
            
#             ax_macd.plot(df.index, df['MACD'], color="#06b6d4", linewidth=2, label="MACD")
#             ax_macd.plot(df.index, df['Signal'], color="#f59e0b", linewidth=2, label="Signal")
            
#             pos_hist = df['Hist'].where(df['Hist'] >= 0, 0)
#             neg_hist = df['Hist'].where(df['Hist'] < 0, 0)
            
#             ax_macd.bar(df.index, pos_hist, color="#10b981", alpha=0.7, width=0.8)
#             ax_macd.bar(df.index, neg_hist, color="#ef4444", alpha=0.7, width=0.8)
#             ax_macd.axhline(0, color="#64748b", linestyle="-", alpha=0.5)
#             ax_macd.set_ylabel("MACD", fontweight="bold")
#             ax_macd.grid(True, alpha=0.4, linestyle="--")
#             ax_macd.legend(loc="upper left", frameon=False)
        
#         # Support/Resistance lines
#         if options['show_sr'] and 'local_max' in indicators:
#             close_prices = df['Close'].values
#             for idx in indicators['local_max']:
#                 ax_main.axhline(y=close_prices[idx], color="#a855f7", 
#                                linestyle="--", alpha=0.7, linewidth=1.5)
#             for idx in indicators['local_min']:
#                 ax_main.axhline(y=close_prices[idx], color="#0d9488", 
#                                linestyle="--", alpha=0.7, linewidth=1.5)
        
#         # Create canvas
#         self.canvas = FigureCanvas(fig)
#         self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
#         # Create hidden toolbar
#         self.toolbar = NavigationToolbar(self.canvas, self)
#         self.toolbar.hide()
        
#         self.layout.addWidget(self.canvas)
#         self.canvas.draw()
        
#         # Note: Removed mplcursors for better performance
#         # If you need tooltips, use matplotlib's built-in hover events instead
    
#     def set_theme(self, is_dark: bool):
#         """Change theme and refresh chart"""
#         self.is_dark = is_dark
#         self.apply_theme()
        
#         if self.popover:
#             self.popover.is_dark = is_dark
#             self.popover.apply_styling()
        
#         # Replot if we have cached data
#         if self.last_df is not None and self.current_ticker:
#             self.plot_chart(
#                 self.last_df,
#                 self.current_ticker,
#                 **self._last_options
#             )
    
#     def resizeEvent(self, event):
#         """Handle resize events"""
#         super().resizeEvent(event)
#         if self.popover and self.popover.isVisible():
#             self.popover.hide()
    
#     def closeEvent(self, event):
#         """Clean up resources on close"""
#         # Stop any running worker
#         if self.worker and self.worker.isRunning():
#             self.worker.quit()
#             self.worker.wait()
        
#         # Remove cursor
#         if self.cursor:
#             self.cursor.remove()
#             self.cursor = None
        
#         # Clean up canvas
#         if self.canvas:
#             self.canvas.deleteLater()
        
#         super().closeEvent(event)

import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QLabel,
    QPushButton, QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
import pandas as pd
from scipy.signal import argrelextrema
from matplotlib import rcParams
import gc


# ============================================================================
# INDICATOR CALCULATIONS
# ============================================================================

def calculate_rsi(series, period=14):
    delta = series.diff().values
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    alpha = 1 / period
    avg_gain = pd.Series(gain).ewm(alpha=alpha, min_periods=period).mean()
    avg_loss = pd.Series(loss).ewm(alpha=alpha, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist


# ============================================================================
# CHART WORKER THREAD
# ============================================================================

class ChartWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, df, ticker, options, is_dark):
        super().__init__()
        self.df = df.copy()
        self.ticker = ticker
        self.options = options.copy()
        self.is_dark = is_dark
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            if self._is_cancelled:
                return
            data = self._prepare_chart_data()
            if not self._is_cancelled:
                self.finished.emit(data)
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))

    def _prepare_chart_data(self):
        df = self.df
        opts = self.options
        indicators = {}

        if opts.get('show_sma'):
            indicators['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()

        if opts.get('show_ema'):
            indicators['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

        if opts.get('show_bb'):
            bb_mid = df['Close'].rolling(window=20, min_periods=1).mean()
            bb_std = df['Close'].rolling(window=20, min_periods=1).std()
            indicators['BB_UPPER'] = bb_mid + (2 * bb_std)
            indicators['BB_LOWER'] = bb_mid - (2 * bb_std)

        if opts.get('show_sr'):
            close_vals = df['Close'].values
            order = min(10, len(close_vals) // 4) if len(close_vals) > 20 else 5
            indicators['local_max'] = argrelextrema(close_vals, np.greater, order=order)[0]
            indicators['local_min'] = argrelextrema(close_vals, np.less, order=order)[0]

        if opts.get('show_rsi'):
            indicators['RSI'] = calculate_rsi(df['Close'])

        if opts.get('show_macd'):
            macd, signal, hist = calculate_macd(df['Close'])
            indicators['MACD'] = macd
            indicators['Signal'] = signal
            indicators['Hist'] = hist

        return {
            'df': df,
            'indicators': indicators,
            'ticker': self.ticker,
            'options': opts,
            'is_dark': self.is_dark
        }


# ============================================================================
# TOOLBAR POPOVER
# ============================================================================

class ToolbarPopover(QFrame):
    def __init__(self, parent=None, is_dark=False, navigation_toolbar=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.navigation_toolbar = navigation_toolbar
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(300, 280)
        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Chart Tools")
        title.setObjectName("popover_title")
        title.setFont(QFont("Inter", 14, QFont.Bold))
        layout.addWidget(title)

        tools_frame = QFrame()
        tools_frame.setObjectName("tools_container")
        grid = QGridLayout(tools_frame)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        tools = [
            ("🏠", "Home", self._home),
            ("◀", "Back", self._back),
            ("▶", "Forward", self._forward),
            ("🔎", "Zoom", self._zoom),
            ("⚙️", "Config", self._configure),
        ]

        for i, (icon, tip, cb) in enumerate(tools):
            btn = QPushButton(icon)
            btn.setObjectName("tool_button")
            btn.setToolTip(tip)
            btn.setFixedSize(45, 45)
            btn.clicked.connect(cb)
            grid.addWidget(btn, i // 3, i % 3, alignment=Qt.AlignCenter)

        layout.addWidget(tools_frame, alignment=Qt.AlignCenter)
        layout.addStretch()

    def _home(self):
        if self.navigation_toolbar:
            self.navigation_toolbar.home()
        self.hide()

    def _back(self):
        if self.navigation_toolbar:
            self.navigation_toolbar.back()
        self.hide()

    def _forward(self):
        if self.navigation_toolbar:
            self.navigation_toolbar.forward()
        self.hide()

    def _zoom(self):
        if self.navigation_toolbar:
            self.navigation_toolbar.zoom()
        self.hide()

    def _configure(self):
        if self.navigation_toolbar:
            self.navigation_toolbar.configure_subplots()
        self.hide()

    def _apply_styling(self):
        if self.is_dark:
            self.setStyleSheet("""
                ToolbarPopover {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #1e293b,stop:1 #0f172a);
                    border: 2px solid #334155; border-radius: 16px;
                }
                QLabel#popover_title { color: #f1f5f9; background: transparent; }
                QPushButton#tool_button {
                    background: #334155; border: 1px solid #475569;
                    border-radius: 8px; color: #e2e8f0; font-size: 16px;
                }
                QPushButton#tool_button:hover { background: #3b82f6; border: 1px solid #2563eb; }
            """)
        else:
            self.setStyleSheet("""
                ToolbarPopover {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff,stop:1 #f8fafc);
                    border: 2px solid #e2e8f0; border-radius: 16px;
                }
                QLabel#popover_title { color: #111827; background: transparent; }
                QPushButton#tool_button {
                    background: #ffffff; border: 1px solid #d1d5db;
                    border-radius: 8px; color: #374151; font-size: 16px;
                }
                QPushButton#tool_button:hover { background: #3b82f6; color: #ffffff; }
            """)

    def show_at_position(self, parent_widget, button_rect):
        pos = parent_widget.mapToGlobal(button_rect.bottomLeft())
        x = pos.x() - self.width() + button_rect.width()
        y = pos.y() + 8
        self.move(x, y)
        self.show()
        self.raise_()


# ============================================================================
# CHART WIDGET
# ============================================================================

class ChartWidget(QWidget):
    theme_changed = pyqtSignal(bool)

    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.canvas = None
        self.toolbar = None
        self.fig = None
        self.current_ticker = ""
        self.popover = None
        self.worker = None
        self.last_df = None
        self._last_options = {}

        self._plot_timer = QTimer()
        self._plot_timer.setSingleShot(True)
        self._plot_timer.timeout.connect(self._execute_plot)
        self._pending_plot_args = None

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self._create_header()
        self._apply_theme()

    def _create_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("chart_header")
        self.header_frame.setFixedHeight(100)
        self.header_frame.resizeEvent = self._header_resize

        self.title_label = QLabel("Candlestick Chart", self.header_frame)
        self.title_label.setObjectName("chart_title")
        self.title_label.setFont(QFont("Inter", 16, QFont.Bold))
        self.title_label.setFixedSize(330, 55)

        self.subtitle_label = QLabel("Select a ticker", self.header_frame)
        self.subtitle_label.setObjectName("chart_subtitle")
        self.subtitle_label.setFont(QFont("Inter", 11))
        self.subtitle_label.setFixedSize(220, 45)

        self.tools_button = QPushButton("🛠️ Tools", self.header_frame)
        self.tools_button.setObjectName("tools_button")
        self.tools_button.setFixedSize(120, 45)
        self.tools_button.clicked.connect(self._toggle_popover)

        self.layout.addWidget(self.header_frame)
        self._position_header()

    def _header_resize(self, event):
        QFrame.resizeEvent(self.header_frame, event)
        self._position_header()

    def _position_header(self):
        if not hasattr(self, 'title_label'):
            return
        h = self.header_frame.height()
        title_h, subtitle_h = self.title_label.height(), self.subtitle_label.height()
        y = (h - title_h - subtitle_h) // 4
        self.title_label.move(16, y)
        self.subtitle_label.move(16, y + title_h)
        btn_w, btn_h = self.tools_button.width(), self.tools_button.height()
        self.tools_button.move(self.header_frame.width() - btn_w - 16, (h - btn_h) // 2)

    def _toggle_popover(self):
        if self.popover and self.popover.isVisible():
            self.popover.hide()
        else:
            if not self.popover:
                self.popover = ToolbarPopover(self, self.is_dark, self.toolbar)
            self.popover.navigation_toolbar = self.toolbar
            self.popover.show_at_position(self, self.tools_button.geometry())

    def _apply_theme(self):
        if self.is_dark:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()

    def _apply_light_theme(self):
        plt.style.use("default")
        rcParams.update({
            "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#e2e8f0", "axes.labelcolor": "#374151",
            "grid.color": "#f3f4f6", "text.color": "#1f2937",
            "font.family": "Inter", "font.size": 10,
        })
        self.setStyleSheet("""
            QFrame#chart_header {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff,stop:1 #f8fafc);
                border: 1px solid #e5e7eb; border-radius: 12px;
            }
            QLabel#chart_title { color: #111827; background: transparent; }
            QLabel#chart_subtitle { color: #6b7280; background: transparent; }
            QPushButton#tools_button {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f3f4f6,stop:1 #e5e7eb);
                border: 1px solid #d1d5db; border-radius: 8px; color: #374151; font-weight: 600;
            }
            QPushButton#tools_button:hover { background: #3b82f6; color: #ffffff; }
        """)

    def _apply_dark_theme(self):
        plt.style.use("dark_background")
        rcParams.update({
            "figure.facecolor": "#1e293b", "axes.facecolor": "#1e293b",
            "axes.edgecolor": "#475569", "axes.labelcolor": "#cbd5e1",
            "grid.color": "#334155", "text.color": "#e2e8f0",
            "font.family": "Inter", "font.size": 10,
        })
        self.setStyleSheet("""
            QFrame#chart_header {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #1e293b,stop:1 #0f172a);
                border: 1px solid #334155; border-radius: 12px;
            }
            QLabel#chart_title { color: #f1f5f9; background: transparent; }
            QLabel#chart_subtitle { color: #94a3b8; background: transparent; }
            QPushButton#tools_button {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #334155,stop:1 #1e293b);
                border: 1px solid #475569; border-radius: 8px; color: #ffffff; font-weight: 600;
            }
            QPushButton#tools_button:hover { background: #3b82f6; color: #ffffff; }
        """)

    def plot_chart(self, df, ticker, show_sma=False, show_ema=False,
                   show_rsi=False, show_macd=False, show_bb=False, show_sr=False):
        self._pending_plot_args = (df, ticker, {
            'show_sma': show_sma, 'show_ema': show_ema, 'show_rsi': show_rsi,
            'show_macd': show_macd, 'show_bb': show_bb, 'show_sr': show_sr,
        })
        self._plot_timer.stop()
        self._plot_timer.start(100)

    def _execute_plot(self):
        if not self._pending_plot_args:
            return

        df, ticker, options = self._pending_plot_args
        self._pending_plot_args = None

        if self.worker:
            self.worker.cancel()
            if self.worker.isRunning():
                self.worker.quit()
                self.worker.wait(500)
            self.worker.deleteLater()
            self.worker = None

        self.last_df = df.copy()
        self._last_options = options.copy()
        self.current_ticker = ticker
        self._update_header(df, ticker)

        df = df.copy()

        # Handle Date - reset if it's index
        if df.index.name == "Date" or isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()

        # Find and set Date column
        date_col = None
        for col in df.columns:
            if str(col).lower() == 'date':
                date_col = col
                break

        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df.set_index(date_col, inplace=True)
            df.index.name = "Date"

        # Normalize columns
        col_map = {c: str(c).capitalize() for c in df.columns}
        df.rename(columns=col_map, inplace=True)

        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=['Close'], inplace=True)

        if df.empty:
            return

        self.worker = ChartWorker(df, ticker, options, self.is_dark)
        self.worker.finished.connect(self._on_data_ready)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _update_header(self, df, ticker):
        self.title_label.setText(f"{ticker.upper()} Candlestick Chart")
        try:
            close_col = None
            for col in df.columns:
                if str(col).lower() == 'close':
                    close_col = col
                    break
            if close_col is None:
                raise ValueError("No Close column")
            
            latest = float(df[close_col].iloc[-1])
            prev = float(df[close_col].iloc[-2]) if len(df) > 1 else latest
            change = latest - prev
            pct = (change / prev * 100) if prev != 0 else 0

            if change >= 0:
                self.subtitle_label.setText(f"${latest:.2f} (+{pct:.1f}%)")
                color = "#10b981" if self.is_dark else "#059669"
            else:
                self.subtitle_label.setText(f"${latest:.2f} ({pct:.1f}%)")
                color = "#ef4444" if self.is_dark else "#dc2626"

            self.subtitle_label.setStyleSheet(f"color: {color}; font-weight: 600; background: transparent;")
        except Exception:
            self.subtitle_label.setText(f"Loading {ticker.upper()}...")

    @pyqtSlot(dict)
    def _on_data_ready(self, data):
        try:
            self._render_chart(data)
        except Exception as e:
            print(f"Render error: {e}")
        finally:
            if self.worker:
                self.worker.deleteLater()
                self.worker = None

    @pyqtSlot(str)
    def _on_error(self, msg):
        print(f"Chart worker error: {msg}")
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def _cleanup_canvas(self):
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.setParent(None)
        if self.toolbar:
            self.layout.removeWidget(self.toolbar)
            self.toolbar.setParent(None)
        if self.fig:
            plt.close(self.fig)
            self.fig = None
        self.canvas = None
        self.toolbar = None
        gc.collect()

    def _render_chart(self, data):
        df = data['df']
        indicators = data['indicators']
        options = data['options']
        is_dark = data['is_dark']

        self._cleanup_canvas()

        nrows = 2
        if options.get('show_rsi'):
            nrows += 1
        if options.get('show_macd'):
            nrows += 1

        heights = [4, 1]
        if options.get('show_rsi'):
            heights.append(1)
        if options.get('show_macd'):
            heights.append(1)

        self.fig = Figure(figsize=(12, 10), dpi=100)
        bg_color = "#1e293b" if is_dark else "#ffffff"
        self.fig.patch.set_facecolor(bg_color)
        self.fig.subplots_adjust(left=0.06, bottom=0.08, right=0.97, top=0.98, hspace=0.25)

        gs = self.fig.add_gridspec(nrows, 1, height_ratios=heights, hspace=0.25)
        ax_main = self.fig.add_subplot(gs[0])
        ax_vol = self.fig.add_subplot(gs[1], sharex=ax_main)

        idx = 2
        ax_rsi, ax_macd = None, None
        if options.get('show_rsi'):
            ax_rsi = self.fig.add_subplot(gs[idx], sharex=ax_main)
            idx += 1
        if options.get('show_macd'):
            ax_macd = self.fig.add_subplot(gs[idx], sharex=ax_main)

        up_color = "#10b981" if is_dark else "#059669"
        down_color = "#ef4444" if is_dark else "#dc2626"

        add_plots = []

        if 'SMA_20' in indicators:
            df['SMA_20'] = indicators['SMA_20']
            add_plots.append(mpf.make_addplot(df['SMA_20'], ax=ax_main, color="#3b82f6", width=2))

        if 'EMA_20' in indicators:
            df['EMA_20'] = indicators['EMA_20']
            add_plots.append(mpf.make_addplot(df['EMA_20'], ax=ax_main, color="#f59e0b", width=2))

        if 'BB_UPPER' in indicators:
            df['BB_UPPER'] = indicators['BB_UPPER']
            df['BB_LOWER'] = indicators['BB_LOWER']
            add_plots.append(mpf.make_addplot(df['BB_UPPER'], ax=ax_main, color="#ef4444", linestyle="--", width=1.5))
            add_plots.append(mpf.make_addplot(df['BB_LOWER'], ax=ax_main, color="#10b981", linestyle="--", width=1.5))

        mc = mpf.make_marketcolors(
            up=up_color, down=down_color, edge="inherit",
            wick={"up": up_color, "down": down_color}, volume="in"
        )
        style = mpf.make_mpf_style(
            marketcolors=mc, facecolor=bg_color, figcolor=bg_color,
            gridstyle="--", gridcolor="#334155" if is_dark else "#f3f4f6", y_on_right=False
        )

        # Build plot kwargs - only add addplot if we have indicators
        plot_kwargs = {
            'type': 'candle',
            'ax': ax_main,
            'volume': ax_vol,
            'style': style,
            'warn_too_much_data': 10000,
            'datetime_format': '%Y-%m-%d',
            'xrotation': 0
        }
        if add_plots:
            plot_kwargs['addplot'] = add_plots

        mpf.plot(df, **plot_kwargs)

        ax_main.set_ylabel("Price ($)", fontweight="bold")
        ax_main.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)
        ax_vol.set_ylabel("Volume", fontweight="bold")
        ax_vol.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)

        if ax_rsi and 'RSI' in indicators:
            rsi = indicators['RSI']
            ax_rsi.plot(df.index, rsi, color="#8b5cf6", linewidth=2)
            ax_rsi.axhline(70, color="#ef4444", linestyle="--", alpha=0.8)
            ax_rsi.axhline(30, color="#10b981", linestyle="--", alpha=0.8)
            ax_rsi.fill_between(df.index, 30, 70, alpha=0.1, color="#8b5cf6")
            ax_rsi.set_ylim(0, 100)
            ax_rsi.set_ylabel("RSI", fontweight="bold")
            ax_rsi.grid(True, alpha=0.4, linestyle="--")

        if ax_macd and 'MACD' in indicators:
            macd, sig, hist = indicators['MACD'], indicators['Signal'], indicators['Hist']
            ax_macd.plot(df.index, macd, color="#06b6d4", linewidth=2, label="MACD")
            ax_macd.plot(df.index, sig, color="#f59e0b", linewidth=2, label="Signal")
            pos = hist.where(hist >= 0, 0)
            neg = hist.where(hist < 0, 0)
            ax_macd.bar(df.index, pos, color="#10b981", alpha=0.7, width=0.8)
            ax_macd.bar(df.index, neg, color="#ef4444", alpha=0.7, width=0.8)
            ax_macd.axhline(0, color="#64748b", linestyle="-", alpha=0.5)
            ax_macd.set_ylabel("MACD", fontweight="bold")
            ax_macd.grid(True, alpha=0.4, linestyle="--")
            ax_macd.legend(loc="upper left", frameon=False)

        if options.get('show_sr') and 'local_max' in indicators:
            close_vals = df['Close'].values
            for i in indicators['local_max']:
                if i < len(close_vals):
                    ax_main.axhline(y=close_vals[i], color="#a855f7", linestyle="--", alpha=0.7, linewidth=1.5)
            for i in indicators['local_min']:
                if i < len(close_vals):
                    ax_main.axhline(y=close_vals[i], color="#0d9488", linestyle="--", alpha=0.7, linewidth=1.5)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()
        self.layout.addWidget(self.canvas)
        self.canvas.draw_idle()

    def set_theme(self, is_dark: bool):
        self.is_dark = is_dark
        self._apply_theme()
        if self.popover:
            self.popover.is_dark = is_dark
            self.popover._apply_styling()
        if self.last_df is not None and self.current_ticker:
            self.plot_chart(self.last_df, self.current_ticker, **self._last_options)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.popover and self.popover.isVisible():
            self.popover.hide()

    def closeEvent(self, event):
        self._plot_timer.stop()
        if self.worker:
            self.worker.cancel()
            if self.worker.isRunning():
                self.worker.quit()
                self.worker.wait(1000)
        self._cleanup_canvas()
        super().closeEvent(event)