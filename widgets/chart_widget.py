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
    finished = pyqtSignal(object)  # Changed to object to pass Figure
    error = pyqtSignal(str)

    def __init__(self, df, ticker, options, is_dark, parent=None):
        super().__init__(parent)
        # Store raw DataFrame - all work happens in worker thread
        self.raw_df = df
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
            # Create ENTIRE figure in worker thread - this is the key optimization
            fig = self._create_figure()
            if fig is None or self._is_cancelled:
                return
            self.finished.emit(fig)
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))

    def _prepare_dataframe(self):
        """Prepare DataFrame for charting"""
        df = self.raw_df.copy()
        
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
        return df

    def _calculate_indicators(self, df):
        """Calculate technical indicators"""
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

        return indicators

    def _create_figure(self):
        """Create complete matplotlib Figure in worker thread - KEY OPTIMIZATION"""
        df = self._prepare_dataframe()
        if df.empty or self._is_cancelled:
            return None

        indicators = self._calculate_indicators(df)
        if self._is_cancelled:
            return None

        options = self.options
        is_dark = self.is_dark

        # Determine layout
        nrows = 2
        heights = [3, 1]
        if options.get('show_rsi'):
            nrows += 1
            heights.append(1)
        if options.get('show_macd'):
            nrows += 1
            heights.append(1)

        # Create Figure in worker thread (thread-safe for matplotlib)
        fig = Figure(figsize=(12, 10), dpi=100)
        bg_color = "#1e293b" if is_dark else "#ffffff"
        fig.patch.set_facecolor(bg_color)
        fig.subplots_adjust(left=0.06, bottom=0.08, right=0.97, top=0.98, hspace=0.25)

        gs = fig.add_gridspec(nrows, 1, height_ratios=heights, hspace=0.25)
        ax_main = fig.add_subplot(gs[0])
        ax_vol = fig.add_subplot(gs[1], sharex=ax_main)

        idx = 2
        ax_rsi, ax_macd = None, None
        if options.get('show_rsi'):
            ax_rsi = fig.add_subplot(gs[idx], sharex=ax_main)
            idx += 1
        if options.get('show_macd'):
            ax_macd = fig.add_subplot(gs[idx], sharex=ax_main)

        if self._is_cancelled:
            plt.close(fig)
            return None

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

        # Build plot kwargs
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

        if self._is_cancelled:
            plt.close(fig)
            return None

        # HEAVY CALL - now runs in worker thread instead of main thread
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

        return fig


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

        # Cleanly replace worker without blocking wait
        if self.worker:
            self.worker.cancel()
            # Disconnect signals to prevent UI interference
            try:
                self.worker.finished.disconnect()
                self.worker.error.disconnect()
            except Exception:
                pass
            # Schedule for deletion when finished (handled by Qt)
            self.worker.finished.connect(self.worker.deleteLater)
            # Or if it's already done check isFinished
            if self.worker.isFinished():
                self.worker.deleteLater()
            
            # Drop reference - parent=self keeps it alive until deleted by Qt
            self.worker = None

        # Store for caching - minimal main thread work
        self.last_df = df
        self._last_options = options.copy()
        self.current_ticker = ticker
        
        # Quick header update
        self._update_header(df, ticker)

        # Start worker immediately - all heavy work happens in thread
        # Pass PARENT=self to prevent Python GC from killing it
        self.worker = ChartWorker(df, ticker, options, self.is_dark, parent=self)
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

    @pyqtSlot(object)  # Changed from dict to object for Figure
    def _on_data_ready(self, fig):
        """Embed pre-rendered Figure from worker - LIGHTWEIGHT main thread work"""
        try:
            if fig is not None:
                self._embed_figure(fig)
        except Exception as e:
            print(f"Embed error: {e}")
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
            self.canvas.deleteLater()  # Async cleanup
        if self.toolbar:
            self.layout.removeWidget(self.toolbar)
            self.toolbar.setParent(None)
            self.toolbar.deleteLater()  # Async cleanup
        if self.fig:
            plt.close(self.fig)
            self.fig = None
        self.canvas = None
        self.toolbar = None

    def _embed_figure(self, fig):
        """Embed pre-rendered Figure into canvas - LIGHTWEIGHT, no heavy work"""
        # Cleanup old canvas first
        self._cleanup_canvas()
        
        # Store and embed the figure created by worker
        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()
        self.layout.addWidget(self.canvas)
        # draw_idle() is non-blocking
        self.canvas.draw_idle()

    def set_theme(self, is_dark: bool):
        self.is_dark = is_dark
        self._apply_theme()
        if self.popover:
            self.popover.is_dark = is_dark
            self.popover._apply_styling()
        # Defer chart replot to prevent UI blocking during theme switch
        if self.last_df is not None and self.current_ticker:
            QTimer.singleShot(50, lambda: self.plot_chart(self.last_df, self.current_ticker, **self._last_options))

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