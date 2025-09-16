from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
    QSizePolicy,
    QHBoxLayout,
    QScrollArea,
    QGridLayout,
    QSpacerItem,
    QToolTip,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import mplcursors


class ReportsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = True  # Will sync with main window theme
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header section
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(15)

        # Top bar with back button (keeping original button for compatibility)
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setFixedSize(180, 40)
        self.back_btn.setCursor(Qt.PointingHandCursor)

        top_bar.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        top_bar.addStretch()

        # Title
        self.title_label = QLabel("📊 Financial Reports")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        header_layout.addLayout(top_bar)
        header_layout.addWidget(self.title_label)

        # Content area with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)

        # Summary statistics cards
        self.stats_frame = QFrame()
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setSpacing(15)

        # Create stat cards (will be populated dynamically)
        self.stat_cards = {}

        # Summary text area (keeping original for compatibility)
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)

        summary_title = QLabel("📈 Summary Report")
        summary_title_font = QFont()
        summary_title_font.setPointSize(16)
        summary_title_font.setBold(True)
        summary_title.setFont(summary_title_font)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFixedHeight(200)
        summary_font = QFont("Consolas", 11)
        self.summary_text.setFont(summary_font)

        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self.summary_text)

        # Chart section (keeping original structure for compatibility)
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)

        chart_title = QLabel("📊 Price Analysis Chart")
        chart_title_font = QFont()
        chart_title_font.setPointSize(16)
        chart_title_font.setBold(True)
        chart_title.setFont(chart_title_font)

        self.report_chart_frame = QFrame()
        self.report_chart_frame.setFrameShape(QFrame.StyledPanel)
        self.report_chart_frame.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.report_chart_frame.setMinimumHeight(600)
        self.report_chart_layout = QVBoxLayout(self.report_chart_frame)

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.report_chart_frame)

        # Export buttons (keeping original for compatibility)
        export_frame = QFrame()
        export_layout = QHBoxLayout(export_frame)
        export_layout.setSpacing(15)

        self.export_csv_btn = QPushButton("📄 Export to CSV")
        self.export_csv_btn.setFixedSize(160, 45)
        self.export_csv_btn.setCursor(Qt.PointingHandCursor)

        self.export_pdf_btn = QPushButton("📋 Export to PDF")
        self.export_pdf_btn.setFixedSize(160, 45)
        self.export_pdf_btn.setCursor(Qt.PointingHandCursor)

        export_layout.addStretch()
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_pdf_btn)
        export_layout.addStretch()

        # Add all sections to content layout
        content_layout.addWidget(self.stats_frame)
        content_layout.addWidget(summary_frame)
        content_layout.addWidget(chart_frame)
        content_layout.addWidget(export_frame)
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)

        # Add everything to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def create_stat_card(self, title, value, icon="📈"):
        """Create a statistics card widget"""
        card = QFrame()
        card.setFixedSize(250, 150)
        card.setObjectName("stat_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(8, 8, 8, 8)



        # Icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(50, 50)
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)

        title_label = QLabel(title)
        title_label.setWordWrap(False)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedSize(130, 50)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        title_label.setFont(title_font)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)

        # Value
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("stat_value")
        value_label.setFixedSize(120, 50)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)

        card_layout.addLayout(header_layout)
        card_layout.addWidget(value_label, alignment=Qt.AlignCenter)
    
        card_layout.addStretch(1)

        card.setToolTip(f"{icon} {title}\nValue: {value}")

        return card, value_label

    def set_theme(self, is_dark_mode):
        """Set theme - called from main window"""
        self.is_dark_mode = is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Apply light or dark theme"""
        if self.is_dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_light_theme(self):
        """Apply light theme styling"""
        QToolTip.setFont(QFont("Segoe UI", 10))
        QToolTip.setPalette(QPalette(QColor("#2c3e50"), QColor("#ffffff")))

        self.setStyleSheet(
            """
            QWidget {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 12px;
                padding: 10px;
            }
            
            QFrame#stat_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
            }
            
            QFrame#stat_card:hover {
                border: 2px solid #007bff;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(0, 123, 255, 0.05), 
                                            stop: 1 rgba(0, 123, 255, 0.02));
            }
            
            QLabel#stat_value {
                color: #007bff;
            }
                           
            QToolTip {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #ced4da;
            padding: 8px;
            border-radius: 6px;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', monospace;
            }
            
            QLabel {
                color: #2c3e50;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #ced4da;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
        """
        )

    def apply_dark_theme(self):
        """Apply dark theme styling"""
        QToolTip.setFont(QFont("Segoe UI", 10))
        QToolTip.setPalette(QPalette(QColor("#e9ecef"), QColor("#2d3748")))
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1a1a1a;
                color: #e9ecef;
            }
            
            QFrame {
                background-color: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 12px;
                padding: 10px;
            }
            
            QFrame#stat_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 12px;
            }
            
            QFrame#stat_card:hover {
                border: 2px solid #4299e1;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(66, 153, 225, 0.1), 
                                            stop: 1 rgba(66, 153, 225, 0.05));
            }
            
            QLabel#stat_value {
                color: #4299e1;
            }
            
            QPushButton {
                background-color: #4299e1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #3182ce;
                transform: translateY(-1px);
            }
            
            QPushButton:pressed {
                background-color: #2c5282;
            }
            
            QTextEdit {
                background-color: #2d3748;
                border: 2px solid #4a5568;
                border-radius: 8px;
                padding: 15px;
                color: #e9ecef;
                font-family: 'Consolas', monospace;
            }

             QToolTip {
            background-color: #2d3748;
            color: #e9ecef;
            border: 1px solid #4a5568;
            padding: 8px;
            border-radius: 6px;
            }
            
            QLabel {
                color: #e9ecef;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #2d3748;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4a5568;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #718096;
            }
        """
        )

    def set_report(
        self, df: pd.DataFrame, ticker: str, forecast_df: pd.DataFrame = None
    ):
        """Populate summary + chart in reports UI"""
        if df is None or df.empty:
            self.summary_text.setText("❌ No data available for analysis.")
            return

        print(f"DEBUG: Setting report for {ticker}")
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame columns: {df.columns.tolist()}")
        print(f"DEBUG: DataFrame index type: {type(df.index)}")

        # Calculate statistics
        stats = {
            "Min Price": df["Close"].min(),
            "Max Price": df["Close"].max(),
            "Average Price": df["Close"].mean(),
            "Volatility": df["Close"].std(),
        }

        # Clear existing stat cards
        for card in self.stat_cards.values():
            card.setParent(None)
        self.stat_cards.clear()

        # Tooltips for buttons
        self.back_btn.setToolTip("Return to the main dashboard")
        self.export_csv_btn.setToolTip("Export stock data to CSV file")
        self.export_pdf_btn.setToolTip("Export stock report as PDF")

        # Tooltip for chart
        self.report_chart_frame.setToolTip(
            "Historical and forecasted stock prices with confidence bands"
        )

        # Create stat cards
        icons = ["📉", "📈", "💰", "📊"]

        for i, (stat_name, value) in enumerate(stats.items()):
            card, value_label = self.create_stat_card(
                stat_name, f"${value:.2f}", icons[i]
            )

            self.stat_cards[stat_name] = card
            self.stats_layout.addWidget(card, i // 2, i % 2)
            # Shift stats_frame upward by 20px
            self.stats_layout.setContentsMargins(0, -20, 0, 0)

        # Update summary text (keeping original format for compatibility)
        summary_str = f"🏢 Stock Analysis Report: {ticker}\n"
        summary_str += "=" * 50 + "\n\n"

        summary_str += "📊 Key Statistics:\n"
        for stat_name, value in stats.items():
            summary_str += f"   • {stat_name}: ${value:.2f}\n"

        summary_str += f"\n📈 Data Points: {len(df)} records"

        try:
            summary_str += f"\n📅 Date Range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
        except:
            summary_str += f"\n📅 Date Range: {df.index[0]} to {df.index[-1]}"

        if forecast_df is not None and not forecast_df.empty:
            summary_str += (
                f"\n🔮 Forecast: {len(forecast_df)} future predictions included"
            )
            if "Forecast" in forecast_df.columns:
                avg_forecast = forecast_df["Forecast"].mean()
                summary_str += f"\n🎯 Average Forecasted Price: ${avg_forecast:.2f}"

        self.summary_text.setText(summary_str)

        # Clear old charts
        for i in reversed(range(self.report_chart_layout.count())):
            widget = self.report_chart_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # --- Ensure datetime index ---
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)
            else:
                df.index = pd.to_datetime(df.index)

        if forecast_df is not None and not forecast_df.empty:
            forecast_df.index = pd.to_datetime(forecast_df.index)

        print("DEBUG: Creating chart...")

        try:
            # Reset matplotlib to default state
            plt.clf()
            plt.close("all")

            # Configure matplotlib theme
            if self.is_dark_mode:
                plt.style.use("dark_background")
            else:
                plt.style.use("default")

            # Create chart with explicit backend
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

            # Set background colors
            fig_color = "#2d3748" if self.is_dark_mode else "white"
            ax_color = "#020305" if self.is_dark_mode else "white"

            fig.patch.set_facecolor(fig_color)
            ax.set_facecolor(ax_color)

            # Plot data with error handling
            line_color = "#4299e1" if self.is_dark_mode else "#007bff"
            forecast_color = "#f56565" if self.is_dark_mode else "#dc3545"

            print(f"DEBUG: Plotting Close data, length: {len(df['Close'])}")

            # Use matplotlib's plot instead of pandas plot for better control
            ax.plot(
                df.index,
                df["Close"].rolling(3).mean(),
                label="Historical Price",
                color=line_color,
                linewidth=2,
            )

            if (
                forecast_df is not None
                and not forecast_df.empty
                and "Forecast" in forecast_df.columns
            ):
                print(
                    f"DEBUG: Plotting forecast data, length: {len(forecast_df['Forecast'])}"
                )
                ax.plot(
                    forecast_df.index,
                    forecast_df["Forecast"].rolling(3).mean(),
                    label="Forecasted Price",
                    linestyle="--",
                    color=forecast_color,
                    linewidth=2,
                )

                # Confidence interval shading
                ax.fill_between(
                    forecast_df.index,
                    forecast_df["Lower_Bound"],
                    forecast_df["Upper_Bound"],
                    color="#fbbf24",
                    alpha=0.2,
                )

                cursor_forecast = mplcursors.cursor(ax.lines[1], hover=True)
                cursor_forecast.connect(
                    "add",
                    lambda sel: sel.annotation.set_text(
                        f"Date: {pd.to_datetime(sel.target[0]).strftime('%Y-%m-%d')}\n"
                        f"Forecast: ${sel.target[1]:.2f}"
                    ),
                )
                cursor_hist = mplcursors.cursor(ax.lines[0], hover=True)
                cursor_hist.connect(
                    "add",
                    lambda sel: sel.annotation.set_text(
                        f"Date: {pd.to_datetime(sel.target[0]).strftime('%Y-%m-%d')}\n"
                        f"Price: ${sel.target[1]:.2f}"
                    ),
                )

            # Customize chart
            text_color = "#e9ecef" if self.is_dark_mode else "#2c3e50"

            ax.set_title(
                f"{ticker} Price Analysis & Forecast",
                fontsize=16,
                fontweight="bold",
                pad=10,
                color=text_color,
            )
            ax.set_xlabel("Date", fontweight="bold", color=text_color)
            ax.set_ylabel("Price (USD)", fontweight="bold", color=text_color)

            # Style the legend
            legend = ax.legend(loc="upper left", framealpha=0.9)
            legend.get_frame().set_facecolor(fig_color)

            # Grid styling
            ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

            # Tick colors
            ax.tick_params(colors=text_color)

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)

            # Adjust layout
            plt.tight_layout(rect=[0, 0, 1, 0.95])

            print("DEBUG: Chart created successfully")

            # Create canvas and add to layout
            canvas = FigureCanvas(fig)
            canvas.setParent(self.report_chart_frame)
            self.report_chart_layout.addWidget(canvas)

            # Force update
            canvas.draw()
            self.report_chart_frame.update()

            print("DEBUG: Canvas added to layout")

        except Exception as e:
            print(f"ERROR: Chart creation failed: {str(e)}")
            import traceback

            traceback.print_exc()

            # Show error message in chart area
            error_label = QLabel(f"❌ Chart Error: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet(
                """
                QLabel {
                    color: #ff6b6b;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 20px;
                    background: rgba(255, 107, 107, 0.1);
                    border: 2px solid #ff6b6b;
                    border-radius: 8px;
                }
            """
            )
            self.report_chart_layout.addWidget(error_label)
