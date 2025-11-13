import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
import matplotlib.lines as mlines
import pandas as pd
import mplcursors
from scipy.signal import argrelextrema
import matplotlib.style as mplstyle
from matplotlib import rcParams


# Functions to calculate rsi and macd
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist


class ToolbarPopover(QFrame):
    """Modern popover widget for chart tools with NavigationToolbar integration"""

    def __init__(self, parent=None, is_dark=False, navigation_toolbar=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.navigation_toolbar = navigation_toolbar
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 300)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title
        title_label = QLabel("Chart Tools")
        title_label.setObjectName("popover_title")
        title_font = QFont("Inter", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Tools grid
        tools_frame = QFrame()
        tools_frame.setObjectName("tools_container")
        tools_layout = QGridLayout(tools_frame)
        # Add margins & spacing so buttons don’t overlap
        tools_layout.setHorizontalSpacing(15)
        tools_layout.setVerticalSpacing(15)

        # Let the grid expand nicely
        tools_layout.setColumnStretch(0, 1)
        tools_layout.setColumnStretch(1, 1)
        tools_layout.setColumnStretch(2, 1)

        # Create tool buttons
        self.create_tool_buttons(tools_layout)

        layout.addWidget(tools_frame, alignment=Qt.AlignCenter)
        layout.addStretch()

        # Apply styling
        self.apply_styling()

        # Add shadow effect

    def create_tool_buttons(self, layout):
        """Create the tool buttons grid with NavigationToolbar integration"""
        tools = [
            ("🏠", "Home", "Reset view to original", self.home),
            ("◀", "Back", "Previous view", self.back),
            ("▶", "Forward", "Next view", self.forward),
            ("🔎", "Zoom", "Zoom in/out", self.zoom),
            ("⚙️", "Config", "Configure subplot", self.configure),
        ]

        columns = 3
        button_size = 45

        for i, (icon, name, tooltip, callback) in enumerate(tools):
            btn = QPushButton(f"{icon}")
            btn.setObjectName("tool_button")
            btn.setToolTip(f"{name}: {tooltip}")
            btn.setFixedSize(button_size, button_size)
            btn.clicked.connect(callback)

            row = i // columns
            col = i % columns
            layout.addWidget(btn, row, col, alignment=Qt.AlignCenter)

        for c in range(columns):
            layout.setColumnStretch(c, 1)

        # for r in range((len(tools) + columns - 1) // columns):
        #     layout.setRowStretch(r, 1)

    def home(self):
        """Reset view to home"""
        if self.navigation_toolbar:
            self.navigation_toolbar.home()
        self.hide()

    def back(self):
        """Go to previous view"""
        if self.navigation_toolbar:
            self.navigation_toolbar.back()
        self.hide()

    def forward(self):
        """Go to next view"""
        if self.navigation_toolbar:
            self.navigation_toolbar.forward()
        self.hide()

    def pan(self):
        """Toggle pan mode"""
        if self.navigation_toolbar:
            self.navigation_toolbar.pan()
        self.hide()

    def zoom(self):
        """Toggle zoom mode"""
        if self.navigation_toolbar:
            self.navigation_toolbar.zoom()
        self.hide()

    def configure(self):
        """Configure subplots"""
        if self.navigation_toolbar:
            self.navigation_toolbar.configure_subplots()
        self.hide()

    def save(self):
        """Save figure"""
        if self.navigation_toolbar:
            self.navigation_toolbar.save_figure()
        self.hide()

    def export_data(self):
        """Export data (custom functionality)"""
        print("Exporting data...")
        # Add your data export logic here
        self.hide()

    def apply_styling(self):
        """Apply theme-specific styling"""
        if self.is_dark:
            self.setStyleSheet(
                """
                ToolbarPopover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #1e293b, stop: 1 #0f172a);
                    border: 2px solid #334155;
                    border-radius: 16px;
                }
                QFrame#tools_container {
                    background: transparent;
                }
                QLabel#popover_title {
                    color: #f1f5f9;
                    font-weight: 700;
                    margin-bottom: 8px;
                    background: transparent;
                }
                QPushButton#tool_button {
                    background: #334155;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    color: #e2e8f0;
                    font-size: 16px;
                    font-weight: 600;
                }
                QPushButton#tool_button:hover {
                    background: #3b82f6;
                    border: 1px solid #2563eb;
                    color: #ffffff;
                    transform: scale(1.05);
                }
                QPushButton#tool_button:pressed {
                    background: #1d4ed8;
                    transform: scale(0.95);
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                ToolbarPopover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #ffffff, stop: 1 #f8fafc);
                    border: 2px solid #e2e8f0;
                    border-radius: 16px;
                }
                QLabel#popover_title {
                    color: #111827;
                    font-weight: 700;
                    margin-bottom: 8px;
                }
                QFrame#tools_container {
                    background: transparent;
                }
                QPushButton#tool_button {
                    background: #ffffff;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    color: #374151;
                    font-size: 16px;
                    font-weight: 600;
                }
                QPushButton#tool_button:hover {
                    background: #3b82f6;
                    border: 1px solid #2563eb;
                    color: #ffffff;
                    transform: scale(1.05);
                }
                QPushButton#tool_button:pressed {
                    background: #1d4ed8;
                    transform: scale(0.95);
                }
            """
            )

    def show_at_position(self, parent_widget, button_rect):
        """Show popover below the button"""
        parent_global = parent_widget.mapToGlobal(button_rect.bottomLeft())
        # Position popover below button with some offset
        x = parent_global.x() - self.width() + button_rect.width()
        y = parent_global.y() + 8

        self.move(x, y)
        self.show()
        self.raise_()


class ChartWidget(QWidget):
    theme_changed = pyqtSignal(bool)  # Signal for theme changes

    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.canvas = None
        self.toolbar = None
        self.current_ticker = ""
        self.popover = None

        # Setup layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)  # Reduced spacing
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create compact header section
        self.create_compact_header()

        # Apply initial styling
        self.apply_theme()

    def header_resize_event(self, event):
        """Handle header resize to maintain button position"""
        super(QFrame, self.header_frame).resizeEvent(event)
        self.position_tools_button()
        self.position_left_layout()

    def position_tools_button(self):
        """Position the tools button absolutely within the header"""
        if hasattr(self, "tools_button") and self.tools_button:
            header_width = self.header_frame.width()
            header_height = self.header_frame.height()

            # Calculate position (right-aligned, vertically centered)
            button_width = self.tools_button.width()
            button_height = self.tools_button.height()

            x_pos = header_width - button_width - 16  # 16px from right edge
            y_pos = (header_height - button_height) // 2  # Vertically centered

            self.tools_button.move(x_pos, y_pos)

    def position_left_layout(self):
        """Position the title + subtitle inside header (absolute)"""
        if hasattr(self, "title_label") and hasattr(self, "subtitle_label"):
            header_height = self.header_frame.height()

            # Get label heights
            title_h = self.title_label.height()
            subtitle_h = self.subtitle_label.height()

            # Total height
            total_h = title_h + subtitle_h  # 4px spacing

            # Vertically center
            y_pos = (header_height - total_h) // 4

            # Place with left padding
            x_padding = 16
            self.title_label.move(x_padding, y_pos)
            self.subtitle_label.move(x_padding, y_pos + title_h)

    def create_compact_header(self):
        """Create a compact header for the chart with absolute positioning"""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("chart_header")
        self.header_frame.setFixedHeight(100)

        # Use a layout for the main content
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.direction
        header_layout.setSpacing(12)

        # Left side - Title and subtitle
        # left_widget = QFrame()
        # left_widget.setFixedSize(300, 70)
        # left_layout = QVBoxLayout(left_widget)
        # left_layout.setObjectName("left_layout")
        # left_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        # left_layout.setSpacing(4)
        # left_layout.setContentsMargins(0, 0, 0, 0)

       # Title label
        self.title_label = QLabel("Candlestick Chart and Volume Chart", self.header_frame)
        self.title_label.setObjectName("chart_title")
        title_font = QFont("Inter", 16, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setFixedSize(330, 55)

        # Subtitle label
        self.subtitle_label = QLabel("Select a ticker to view chart", self.header_frame)
        self.subtitle_label.setObjectName("chart_subtitle")
        subtitle_font = QFont("Inter", 11)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setFixedSize(220, 45)


        # left_layout.addWidget(self.title_label)
        # left_layout.addWidget(self.subtitle_label)

        # # Add left content to header
        # header_layout.addWidget(left_widget)
        header_layout.addStretch()

        self.position_left_layout()

        # Create tools button with absolute positioning
        self.tools_button = QPushButton("🛠️ Tools", self.header_frame)
        self.tools_button.setObjectName("tools_button")
        self.tools_button.setFixedSize(120, 45)
        self.tools_button.clicked.connect(self.toggle_tools_popover)

        # Position the button absolutely within the header frame
        self.position_tools_button()

        # Connect resize event to maintain button position
        self.header_frame.resizeEvent = self.header_resize_event

        self.layout.addWidget(self.header_frame)

    def toggle_tools_popover(self):
        """Toggle the tools popover"""
        if self.popover and self.popover.isVisible():
            self.popover.hide()
        else:
            if not self.popover:
                self.popover = ToolbarPopover(self, self.is_dark, self.toolbar)

            # Update the toolbar reference in case it changed
            self.popover.navigation_toolbar = self.toolbar

            # Show popover below the tools button
            button_rect = self.tools_button.geometry()
            self.popover.show_at_position(self, button_rect)

    def apply_theme(self):
        """Apply theme-specific styling to the chart widget"""
        if self.is_dark:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_light_theme(self):
        """Apply light theme styling"""
        # Configure matplotlib for light theme
        plt.style.use("default")
        rcParams.update(
            {
                "figure.facecolor": "#ffffff",
                "axes.facecolor": "#ffffff",
                "axes.edgecolor": "#e2e8f0",
                "axes.labelcolor": "#374151",
                "axes.axisbelow": True,
                "axes.grid": True,
                "grid.color": "#f3f4f6",
                "grid.alpha": 0.7,
                "text.color": "#1f2937",
                "xtick.color": "#6b7280",
                "ytick.color": "#6b7280",
                "font.family": "Inter",
                "font.size": 10,
                "font.weight": "normal",
            }
        )

        # Widget styling with better text contrast
        self.setStyleSheet(
            """
            QFrame[objectName="chart_header"] {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #ffffff, stop: 1 #f8fafc);
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                margin-bottom: 4px;
                
            }
           
            QLabel[objectName="chart_title"] {
            color: #111827;
            font-weight: 700;
            font-size: 16px;
            background: transparent;
        }
        
        QLabel[objectName="chart_subtitle"] {
            color: #6b7280;
            font-weight: 500;
            font-size: 11px;
            background: transparent;
        }
        
            QPushButton[objectName="tools_button"] {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #f3f4f6, stop: 1 #e5e7eb);
                border: 1px solid #d1d5db;
                border-radius: 8px;
                color: #374151;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton[objectName="tools_button"]:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #3b82f6, stop: 1 #2563eb);
                color: #ffffff;
                border: 1px solid #2563eb;
            }
            QPushButton[objectName="tools_button"]:pressed {
                background: #1d4ed8;
            }
        """
        )

    def apply_dark_theme(self):
        """Apply dark theme styling"""
        # Configure matplotlib for dark theme
        plt.style.use("dark_background")
        rcParams.update(
            {
                "figure.facecolor": "#1e293b",
                "axes.facecolor": "#1e293b",
                "axes.edgecolor": "#475569",
                "axes.labelcolor": "#cbd5e1",
                "axes.axisbelow": True,
                "axes.grid": True,
                "grid.color": "#334155",
                "grid.alpha": 0.7,
                "text.color": "#e2e8f0",
                "xtick.color": "#94a3b8",
                "ytick.color": "#94a3b8",
                "font.family": "Inter",
                "font.size": 10,
                "font.weight": "normal",
            }
        )

        # Widget styling with better text contrast for dark theme
        self.setStyleSheet(
            """
            QFrame[objectName="chart_header"] {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #1e293b, stop: 1 #0f172a);
                border: 1px solid #334155;
                border-radius: 12px;
                margin-bottom: 4px;
                
            }
            
            QLabel[objectName="chart_title"] {
            color: #f1f5f9;
            font-weight: 700;
            font-size: 16px;
            background: transparent;
        }
        
        QLabel[objectName="chart_subtitle"] {
            color: #94a3b8;
            font-weight: 500;
            font-size: 11px;
            background: transparent;
        }
            QPushButton[objectName="tools_button"] {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #334155, stop: 1 #1e293b);
                border: 1px solid #475569;
                border-radius: 8px;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton[objectName="tools_button"]:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #3b82f6, stop: 1 #2563eb);
                color: #ffffff;
                border: 1px solid #2563eb;
            }
            QPushButton[objectName="tools_button"]:pressed {
                background: #1d4ed8;
            }
        """
        )

    def plot_chart(
        self,
        df,
        ticker,
        show_sma=False,
        show_ema=False,
        show_rsi=False,
        show_macd=False,
        show_bb=False,
        show_sr=False,
    ):

        self.last_df = df.copy()
        self._last_show_sma = show_sma
        self._last_show_ema = show_ema
        self._last_show_rsi = show_rsi
        self._last_show_macd = show_macd
        self._last_show_bb = show_bb
        self._last_show_sr = show_sr
        # ---- Update header ----
        self.current_ticker = ticker
        print(f"{ticker.upper()} Candlestick Chart")
        self.title_label.setText(f"{ticker.upper()} Candlestick Chart")  # Shorter title
        print("Title label: ", self.title_label)

        # Get latest price for subtitle
        try:
            latest_price = df["Close"].iloc[-1]
            price_change = (
                df["Close"].iloc[-1] - df["Close"].iloc[-2] if len(df) > 1 else 0
            )
            change_pct = (
                (price_change / df["Close"].iloc[-2] * 100)
                if len(df) > 1 and df["Close"].iloc[-2] != 0
                else 0
            )

            if price_change >= 0:
                self.subtitle_label.setText(f"${latest_price:.2f} (+{change_pct:.1f}%)")
                print("Subtitle label green: ", self.subtitle_label)
                color = "#059669" if not self.is_dark else "#10b981"
                self.subtitle_label.setStyleSheet(
                    f"color: {color}; font-weight: 600; background: transparent;"
                )
            else:
                self.subtitle_label.setText(f"${latest_price:.2f} ({change_pct:.1f}%)")
                print("Subtitle label red: ", self.subtitle_label)
                color = "#dc2626" if not self.is_dark else "#ef4444"
                self.subtitle_label.setStyleSheet(
                    f"color: {color}; font-weight: 600; background: transparent;"
                )
        except:
            self.subtitle_label.setText(f"Loading {ticker.upper()}...")
            print("Subtitle label loading: ", self.subtitle_label)
            color = "#6b7280" if not self.is_dark else "#94a3b8"
            self.subtitle_label.setStyleSheet(
                f"color: {color}; font-weight: 500; background: transparent;"
            )

        # ---- Ensure correct index ----
        df = df.copy()  # Avoid modifying original data
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)

        # ---- Normalize column names ----
        df.rename(columns=str.capitalize, inplace=True)
        required = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in df.columns for col in required):
            print("❌ Missing OHLCV columns, got:", df.columns)
            return

        # ---- Remove old widgets ----
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.setParent(None)

        if self.toolbar:
            self.layout.removeWidget(self.toolbar)
            self.toolbar.setParent(None)

        # ---- Dynamic subplot layout ----
        nrows = 2  # candlestick + volume always
        if show_rsi:
            nrows += 1
        if show_macd:
            nrows += 1

        # Create figure with more space for chart (increased height)
        fig = Figure(figsize=(12, 10), dpi=100)  # Larger figure
        fig.patch.set_facecolor("#1e293b" if self.is_dark else "#ffffff")

        # Optimize subplot spacing for more chart visibility
        fig.subplots_adjust(left=0.06, bottom=0.08, right=0.97, top=0.98, hspace=0.25)

        # Height ratios for better visual hierarchy
        height_ratios = [4, 1]  # Even larger main chart
        if show_rsi:
            height_ratios.append(1)
        if show_macd:
            height_ratios.append(1)

        # Create subplots with custom height ratios
        gs = fig.add_gridspec(nrows, 1, height_ratios=height_ratios, hspace=0.25)

        ax_main = fig.add_subplot(gs[0])  # candlesticks
        ax_vol = fig.add_subplot(gs[1], sharex=ax_main)  # volume

        current_subplot = 2
        ax_rsi = None
        ax_macd = None

        if show_rsi:
            ax_rsi = fig.add_subplot(gs[current_subplot], sharex=ax_main)
            current_subplot += 1

        if show_macd:
            ax_macd = fig.add_subplot(gs[current_subplot], sharex=ax_main)

        # ---- Modern color scheme ----
        colors = {
            "up": "#10b981" if self.is_dark else "#059669",
            "down": "#ef4444" if self.is_dark else "#dc2626",
            "volume": "#64748b" if self.is_dark else "#6b7280",
            "sma": "#3b82f6",
            "ema": "#f59e0b",
            "bb_upper": "#ef4444",
            "bb_lower": "#10b981",
            "rsi": "#8b5cf6",
            "macd": "#06b6d4",
            "signal": "#f59e0b",
            "histogram": "#64748b",
        }

        # ---- Indicators ----
        add_plots = []
        legend_handles = []

        if show_sma:
            df["SMA_20"] = df["Close"].rolling(window=20).mean()
            add_plots.append(
                mpf.make_addplot(
                    df["SMA_20"], ax=ax_main, color=colors["sma"], width=2.5
                )
            )
            legend_handles.append(
                mlines.Line2D(
                    [], [], color=colors["sma"], label="SMA 20", linewidth=2.5
                )
            )

        if show_ema:
            df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
            add_plots.append(
                mpf.make_addplot(
                    df["EMA_20"], ax=ax_main, color=colors["ema"], width=2.5
                )
            )
            legend_handles.append(
                mlines.Line2D(
                    [], [], color=colors["ema"], label="EMA 20", linewidth=2.5
                )
            )

        if show_bb:
            df["BB_MID"] = df["Close"].rolling(window=20).mean()
            df["BB_STD"] = df["Close"].rolling(window=20).std()
            df["BB_UPPER"] = df["BB_MID"] + (2 * df["BB_STD"])
            df["BB_LOWER"] = df["BB_MID"] - (2 * df["BB_STD"])
            add_plots += [
                mpf.make_addplot(
                    df["BB_UPPER"],
                    ax=ax_main,
                    color=colors["bb_upper"],
                    linestyle="--",
                    alpha=0.8,
                    width=1.5,
                ),
                mpf.make_addplot(
                    df["BB_LOWER"],
                    ax=ax_main,
                    color=colors["bb_lower"],
                    linestyle="--",
                    alpha=0.8,
                    width=1.5,
                ),
            ]
            legend_handles += [
                mlines.Line2D(
                    [],
                    [],
                    color=colors["bb_upper"],
                    label="BB Upper",
                    linestyle="--",
                    linewidth=1.5,
                ),
                mlines.Line2D(
                    [],
                    [],
                    color=colors["bb_lower"],
                    label="BB Lower",
                    linestyle="--",
                    linewidth=1.5,
                ),
            ]

        if show_sr:
            close_prices = df["Close"].values
            local_max = argrelextrema(close_prices, np.greater, order=10)[0]
            local_min = argrelextrema(close_prices, np.less, order=10)[0]

            for idx in local_max:
                ax_main.axhline(
                    y=close_prices[idx],
                    color="#a855f7",
                    linestyle="--",
                    alpha=0.7,
                    linewidth=1.5,
                )
            for idx in local_min:
                ax_main.axhline(
                    y=close_prices[idx],
                    color="#0d9488",
                    linestyle="--",
                    alpha=0.7,
                    linewidth=1.5,
                )

        # ---- Custom market colors for mplfinance ----
        market_colors = mpf.make_marketcolors(
            up=colors["up"],
            down=colors["down"],
            edge="inherit",
            wick={"up": colors["up"], "down": colors["down"]},
            volume="in",
            ohlc="i",
        )

        # ---- Custom style ----
        style = mpf.make_mpf_style(
            marketcolors=market_colors,
            facecolor="#1e293b" if self.is_dark else "#ffffff",
            figcolor="#1e293b" if self.is_dark else "#ffffff",
            gridstyle="--",
            gridcolor="#334155" if self.is_dark else "#f3f4f6",
            y_on_right=False,
        )

        # ---- Plot candlestick chart ----
        mpf.plot(
            df,
            type="candle",
            ax=ax_main,
            volume=ax_vol,
            addplot=add_plots if add_plots else [],
            style=style,
            warn_too_much_data=10000,
            datetime_format="%Y-%m-%d",
            xrotation=0,
        )

        # ---- Style main chart ----
        ax_main.set_title("")  # Remove default title
        ax_main.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)
        ax_main.set_ylabel("Price ($)", fontweight="bold", fontsize=12)

        # ---- Style volume chart ----
        ax_vol.set_ylabel("Volume", fontweight="bold", fontsize=11)
        ax_vol.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)

        # --- RSI subplot ---
        if show_rsi and ax_rsi is not None:
            df["RSI"] = calculate_rsi(df["Close"])
            ax_rsi.plot(
                df.index,
                df["RSI"],
                color=colors["rsi"],
                linewidth=2.5,
                label="RSI",
                alpha=0.9,
            )
            ax_rsi.axhline(
                70, color=colors["down"], linestyle="--", linewidth=1.2, alpha=0.8
            )
            ax_rsi.axhline(
                30, color=colors["up"], linestyle="--", linewidth=1.2, alpha=0.8
            )
            ax_rsi.fill_between(df.index, 30, 70, alpha=0.1, color=colors["rsi"])
            ax_rsi.set_ylim(0, 100)
            ax_rsi.set_ylabel("RSI", fontweight="bold", fontsize=11)
            ax_rsi.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)
            ax_rsi.legend(loc="upper left", frameon=False)

        # --- MACD subplot ---
        if show_macd and ax_macd is not None:
            df["MACD"], df["Signal"], df["Hist"] = calculate_macd(df["Close"])
            ax_macd.plot(
                df.index, df["MACD"], label="MACD", color=colors["macd"], linewidth=2.5
            )
            ax_macd.plot(
                df.index,
                df["Signal"],
                label="Signal",
                color=colors["signal"],
                linewidth=2.5,
            )

            # Color histogram bars based on value
            pos_hist = df["Hist"].where(df["Hist"] >= 0, 0)
            neg_hist = df["Hist"].where(df["Hist"] < 0, 0)

            ax_macd.bar(df.index, pos_hist, color=colors["up"], alpha=0.7, width=0.8)
            ax_macd.bar(df.index, neg_hist, color=colors["down"], alpha=0.7, width=0.8)
            ax_macd.axhline(0, color="#64748b", linestyle="-", alpha=0.5, linewidth=1.2)
            ax_macd.set_ylabel("MACD", fontweight="bold", fontsize=11)
            ax_macd.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)
            ax_macd.legend(loc="upper left", frameon=False)

        # ---- Enhanced legends ----
        if legend_handles:
            legend = ax_main.legend(
                handles=legend_handles,
                loc="upper left",
                frameon=True,
                fancybox=True,
                shadow=True,
                framealpha=0.9,
            )
            legend.get_frame().set_facecolor("#1e293b" if self.is_dark else "#ffffff")
            legend.get_frame().set_edgecolor("#475569" if self.is_dark else "#e5e7eb")

        # ---- Enhanced tooltips ----
        cursor = mplcursors.cursor([ax_main], hover=True)
        cursor.connect("add", self.create_tooltip_handler(df))

        # Volume tooltip
        cursor_vol = mplcursors.cursor([ax_vol], hover=True)
        cursor_vol.connect("add", self.create_volume_tooltip_handler(df))

        # ---- Embed in PyQt ----
        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create NavigationToolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        # Hide the toolbar (we'll access it through our custom popover)
        self.toolbar.hide()

        self.layout.addWidget(self.canvas)
        self.canvas.draw()

    # def animate_redraw(self, df):
    #     """Smoothly redraw only the updated portion of the chart."""
    #     try:
    #         self.ax_main.clear()
    #         self.ax_volume.clear()
    #         import mplfinance as mpf
    #         mpf.plot(
    #             df,
    #             type='candle',
    #             style='yahoo' if not self.is_dark else 'charles',
    #             ax=self.ax_main,
    #             volume=self.ax_volume,
    #             show_nontrading=False,
    #         )
    #         self.canvas.draw_idle()  # Non-blocking, smooth refresh
    #     except Exception as e:
    #         print("Chart redraw error:", e)

    def set_theme(self, is_dark: bool):
        """Change theme and refresh chart"""
        self.is_dark = is_dark
        self.apply_theme()

        if self.popover:
            self.popover.is_dark = is_dark
            self.popover.apply_styling()

        # 🔑 Force replot if we already have data cached
        if (
            hasattr(self, "last_df")
            and self.last_df is not None
            and self.current_ticker
        ):
            self.plot_chart(
                self.last_df,
                self.current_ticker,
                show_sma=self._last_show_sma,
                show_ema=self._last_show_ema,
                show_rsi=self._last_show_rsi,
                show_macd=self._last_show_macd,
                show_bb=self._last_show_bb,
                show_sr=self._last_show_sr,
            )

    def create_tooltip_handler(self, df):
        """Create enhanced tooltip handler for main chart"""

        def on_hover(sel):
            try:
                i = int(round(sel.target[0]))
                if 0 <= i < len(df):
                    row = df.iloc[i]
                    change = row["Close"] - row["Open"]
                    change_pct = (change / row["Open"] * 100) if row["Open"] != 0 else 0

                    color = "#10b981" if change >= 0 else "#ef4444"
                    arrow = "▲" if change >= 0 else "▼"

                    sel.annotation.set(
                        text=(
                            f"📅 {row.name.strftime('%Y-%m-%d')}\n"
                            f"💰 Open: ${row['Open']:.2f}\n"
                            f"📈 High: ${row['High']:.2f}\n"
                            f"📉 Low: ${row['Low']:.2f}\n"
                            f"🎯 Close: ${row['Close']:.2f}\n"
                            f"{arrow} Change: {change:+.2f} ({change_pct:+.1f}%)\n"
                            f"📊 Volume: {row['Volume']:,.0f}"
                        ),
                        fontsize=9,
                        bbox=dict(
                            boxstyle="round,pad=0.5",
                            fc="#1e293b" if self.is_dark else "#ffffff",
                            ec=color,
                            alpha=0.95,
                            linewidth=2,
                        ),
                        color="#e2e8f0" if self.is_dark else "#1f2937",
                    )
            except Exception as e:
                sel.annotation.set(text=f"⚠️ Error: {str(e)}")

        return on_hover

    def create_volume_tooltip_handler(self, df):
        """Create tooltip handler for volume chart"""

        def on_hover_vol(sel):
            try:
                i = int(round(sel.target[0]))
                if 0 <= i < len(df):
                    row = df.iloc[i]
                    sel.annotation.set(
                        text=(
                            f"📅 {row.name.strftime('%Y-%m-%d')}\n"
                            f"📊 Volume: {row['Volume']:,.0f}\n"
                            f"💰 Price: ${row['Close']:.2f}"
                        ),
                        fontsize=9,
                        bbox=dict(
                            boxstyle="round,pad=0.5",
                            fc="#1e293b" if self.is_dark else "#ffffff",
                            ec="#3b82f6",
                            alpha=0.95,
                            linewidth=2,
                        ),
                        color="#e2e8f0" if self.is_dark else "#1f2937",
                    )
            except Exception as e:
                sel.annotation.set(text=f"⚠️ Error: {str(e)}")

        return on_hover_vol

    def resizeEvent(self, event):
        """Handle resize events to hide popover"""
        super().resizeEvent(event)
        if self.popover and self.popover.isVisible():
            self.popover.hide()
