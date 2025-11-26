# from PyQt5.QtWidgets import (
#     QWidget,
#     QVBoxLayout,
#     QLabel,
#     QPushButton,
#     QTextEdit,
#     QFrame,
#     QSizePolicy,
#     QHBoxLayout,
#     QScrollArea,
#     QGridLayout,
#     QToolTip,
#     QApplication,
# )
# from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
# from PyQt5.QtGui import QFont, QPalette, QColor
# import matplotlib
# matplotlib.use('Qt5Agg')  # Set backend before importing pyplot
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import pandas as pd
# import numpy as np


# class ChartWorker(QThread):
#     """Worker thread for chart generation to prevent UI blocking"""
#     chart_ready = pyqtSignal(object)  # Emits the figure object
#     error_occurred = pyqtSignal(str)
    
#     def __init__(self, df, ticker, forecast_df, is_dark_mode):
#         super().__init__()
#         self.df = df.copy()  # Copy to avoid threading issues
#         self.ticker = ticker
#         self.forecast_df = forecast_df.copy() if forecast_df is not None else None
#         self.is_dark_mode = is_dark_mode
        
#     def run(self):
#         try:
#             fig = self.create_chart()
#             self.chart_ready.emit(fig)
#         except Exception as e:
#             self.error_occurred.emit(str(e))
    
#     def create_chart(self):
#         """Create chart in background thread"""
#         # Pre-calculate rolling means to avoid doing it during plot
#         hist_smoothed = self.df['Close'].rolling(window=3, min_periods=1).mean()
        
#         # Configure matplotlib theme
#         if self.is_dark_mode:
#             plt.style.use('dark_background')
#         else:
#             plt.style.use('default')
        
#         # Create figure
#         fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        
#         # Set colors
#         fig_color = '#2d3748' if self.is_dark_mode else 'white'
#         ax_color = '#020305' if self.is_dark_mode else 'white'
#         line_color = '#4299e1' if self.is_dark_mode else '#007bff'
#         forecast_color = '#f56565' if self.is_dark_mode else '#dc3545'
#         text_color = '#e9ecef' if self.is_dark_mode else '#2c3e50'
        
#         fig.patch.set_facecolor(fig_color)
#         ax.set_facecolor(ax_color)
        
#         # Plot historical data (smoothed)
#         ax.plot(
#             self.df.index,
#             hist_smoothed,
#             label='Historical Price',
#             color=line_color,
#             linewidth=2,
#         )
        
#         # Plot forecast if available
#         if self.forecast_df is not None and not self.forecast_df.empty and 'Forecast' in self.forecast_df.columns:
#             forecast_smoothed = self.forecast_df['Forecast'].rolling(window=3, min_periods=1).mean()
            
#             ax.plot(
#                 self.forecast_df.index,
#                 forecast_smoothed,
#                 label='Forecasted Price',
#                 linestyle='--',
#                 color=forecast_color,
#                 linewidth=2,
#             )
            
#             # Confidence interval
#             ax.fill_between(
#                 self.forecast_df.index,
#                 self.forecast_df['Lower_Bound'],
#                 self.forecast_df['Upper_Bound'],
#                 color='#fbbf24',
#                 alpha=0.2,
#             )
        
#         # Styling
#         ax.set_title(
#             f'{self.ticker} Price Analysis & Forecast',
#             fontsize=16,
#             fontweight='bold',
#             pad=10,
#             color=text_color,
#         )
#         ax.set_xlabel('Date', fontweight='bold', color=text_color)
#         ax.set_ylabel('Price (USD)', fontweight='bold', color=text_color)
        
#         # Legend
#         legend = ax.legend(loc='upper left', framealpha=0.9)
#         legend.get_frame().set_facecolor(fig_color)
        
#         # Grid and ticks
#         ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
#         ax.tick_params(colors=text_color)
        
#         # Rotate labels
#         plt.xticks(rotation=45)
#         plt.tight_layout(rect=[0, 0, 1, 0.95])
        
#         return fig


# class ReportsUI(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.is_dark_mode = True
#         self.current_canvas = None
#         self.chart_worker = None
#         self._cached_stats = None
#         self.setup_ui()

#     def setup_ui(self):
#         main_layout = QVBoxLayout()
#         main_layout.setSpacing(20)
#         main_layout.setContentsMargins(30, 30, 30, 30)

#         # Header section
#         header_frame = QFrame()
#         header_layout = QVBoxLayout(header_frame)
#         header_layout.setSpacing(15)

#         # Top bar with back button
#         top_bar = QHBoxLayout()
#         self.back_btn = QPushButton("← Back to Dashboard")
#         self.back_btn.setFixedSize(180, 40)
#         self.back_btn.setCursor(Qt.PointingHandCursor)

#         top_bar.addWidget(self.back_btn, alignment=Qt.AlignLeft)
#         top_bar.addStretch()

#         # Title
#         self.title_label = QLabel("📊 Financial Reports")
#         self.title_label.setAlignment(Qt.AlignCenter)
#         title_font = QFont()
#         title_font.setPointSize(24)
#         title_font.setBold(True)
#         self.title_label.setFont(title_font)

#         header_layout.addLayout(top_bar)
#         header_layout.addWidget(self.title_label)

#         # Content area with scroll
#         scroll_area = QScrollArea()
#         scroll_area.setWidgetResizable(True)
#         scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

#         content_widget = QWidget()
#         content_layout = QVBoxLayout(content_widget)
#         content_layout.setSpacing(25)

#         # Summary statistics cards
#         self.stats_frame = QFrame()
#         self.stats_layout = QGridLayout(self.stats_frame)
#         self.stats_layout.setSpacing(15)
#         self.stat_cards = {}

#         # Summary text area
#         summary_frame = QFrame()
#         summary_layout = QVBoxLayout(summary_frame)

#         summary_title = QLabel("📈 Summary Report")
#         summary_title_font = QFont()
#         summary_title_font.setPointSize(16)
#         summary_title_font.setBold(True)
#         summary_title.setFont(summary_title_font)

#         self.summary_text = QTextEdit()
#         self.summary_text.setReadOnly(True)
#         self.summary_text.setFixedHeight(200)
#         summary_font = QFont("Consolas", 11)
#         self.summary_text.setFont(summary_font)

#         summary_layout.addWidget(summary_title)
#         summary_layout.addWidget(self.summary_text)

#         # Chart section with loading indicator
#         chart_frame = QFrame()
#         chart_layout = QVBoxLayout(chart_frame)

#         chart_title = QLabel("📊 Price Analysis Chart")
#         chart_title_font = QFont()
#         chart_title_font.setPointSize(16)
#         chart_title_font.setBold(True)
#         chart_title.setFont(chart_title_font)

#         self.report_chart_frame = QFrame()
#         self.report_chart_frame.setFrameShape(QFrame.StyledPanel)
#         self.report_chart_frame.setSizePolicy(
#             QSizePolicy.Expanding, QSizePolicy.Expanding
#         )
#         self.report_chart_frame.setMinimumHeight(600)
#         self.report_chart_layout = QVBoxLayout(self.report_chart_frame)
        
#         # Loading label
#         self.loading_label = QLabel("⏳ Loading chart...")
#         self.loading_label.setAlignment(Qt.AlignCenter)
#         self.loading_label.setVisible(False)
#         self.report_chart_layout.addWidget(self.loading_label)

#         chart_layout.addWidget(chart_title)
#         chart_layout.addWidget(self.report_chart_frame)

#         # Export buttons
#         export_frame = QFrame()
#         export_layout = QHBoxLayout(export_frame)
#         export_layout.setSpacing(15)

#         self.export_csv_btn = QPushButton("📄 Export to CSV")
#         self.export_csv_btn.setFixedSize(160, 45)
#         self.export_csv_btn.setCursor(Qt.PointingHandCursor)

#         self.export_pdf_btn = QPushButton("📋 Export to PDF")
#         self.export_pdf_btn.setFixedSize(160, 45)
#         self.export_pdf_btn.setCursor(Qt.PointingHandCursor)

#         export_layout.addStretch()
#         export_layout.addWidget(self.export_csv_btn)
#         export_layout.addWidget(self.export_pdf_btn)
#         export_layout.addStretch()

#         # Add all sections
#         content_layout.addWidget(self.stats_frame)
#         content_layout.addWidget(summary_frame)
#         content_layout.addWidget(chart_frame)
#         content_layout.addWidget(export_frame)
#         content_layout.addStretch()

#         scroll_area.setWidget(content_widget)
#         main_layout.addWidget(header_frame)
#         main_layout.addWidget(scroll_area)
#         self.setLayout(main_layout)

#     def create_stat_card(self, title, value, icon="📈"):
#         """Create a statistics card widget"""
#         card = QFrame()
#         card.setFixedSize(250, 150)
#         card.setObjectName("stat_card")
#         card_layout = QVBoxLayout(card)
#         card_layout.setSpacing(12)
#         card_layout.setContentsMargins(8, 8, 8, 8)

#         # Icon and title
#         header_layout = QHBoxLayout()
#         header_layout.setSpacing(8)

#         icon_label = QLabel(icon)
#         icon_label.setAlignment(Qt.AlignCenter)
#         icon_label.setFixedSize(50, 50)
#         icon_font = QFont()
#         icon_font.setPointSize(20)
#         icon_label.setFont(icon_font)

#         title_label = QLabel(title)
#         title_label.setWordWrap(False)
#         title_label.setAlignment(Qt.AlignCenter)
#         title_label.setFixedSize(130, 50)
#         title_font = QFont()
#         title_font.setPointSize(9)
#         title_font.setBold(True)
#         title_label.setFont(title_font)

#         header_layout.addWidget(icon_label)
#         header_layout.addWidget(title_label)

#         # Value
#         value_label = QLabel(str(value))
#         value_label.setAlignment(Qt.AlignCenter)
#         value_label.setObjectName("stat_value")
#         value_label.setFixedSize(120, 50)
#         value_font = QFont()
#         value_font.setPointSize(20)
#         value_font.setBold(True)
#         value_label.setFont(value_font)

#         card_layout.addLayout(header_layout)
#         card_layout.addWidget(value_label, alignment=Qt.AlignCenter)
#         card_layout.addStretch(1)

#         card.setToolTip(f"{icon} {title}\nValue: {value}")
#         return card, value_label

#     def set_theme(self, is_dark_mode):
#         """Set theme - called from main window"""
#         self.is_dark_mode = is_dark_mode
#         self.apply_theme()

#     def apply_theme(self):
#         """Apply light or dark theme"""
#         if self.is_dark_mode:
#             self.apply_dark_theme()
#         else:
#             self.apply_light_theme()

#     def apply_light_theme(self):
#         """Apply light theme styling"""
#         QToolTip.setFont(QFont("Segoe UI", 10))
#         QToolTip.setPalette(QPalette(QColor("#2c3e50"), QColor("#ffffff")))

#         self.setStyleSheet("""
#             QWidget {
#                 background-color: #f8f9fa;
#                 color: #2c3e50;
#             }
#             QFrame {
#                 background-color: #ffffff;
#                 border: 1px solid #e9ecef;
#                 border-radius: 12px;
#                 padding: 10px;
#             }
#             QFrame#stat_card {
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 #ffffff, stop: 1 #f8f9fa);
#                 border: 2px solid #e9ecef;
#                 border-radius: 12px;
#             }
#             QFrame#stat_card:hover {
#                 border: 2px solid #007bff;
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 rgba(0, 123, 255, 0.05), 
#                                             stop: 1 rgba(0, 123, 255, 0.02));
#             }
#             QLabel#stat_value {
#                 color: #007bff;
#             }
#             QToolTip {
#                 background-color: #ffffff;
#                 color: #2c3e50;
#                 border: 1px solid #ced4da;
#                 padding: 8px;
#                 border-radius: 6px;
#             }
#             QPushButton {
#                 background-color: #007bff;
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 padding: 10px 20px;
#                 font-weight: bold;
#                 font-size: 12px;
#             }
#             QPushButton:hover {
#                 background-color: #0056b3;
#             }
#             QPushButton:pressed {
#                 background-color: #004085;
#             }
#             QTextEdit {
#                 background-color: #ffffff;
#                 border: 2px solid #e9ecef;
#                 border-radius: 8px;
#                 padding: 15px;
#                 font-family: 'Consolas', monospace;
#             }
#             QLabel {
#                 color: #2c3e50;
#             }
#             QScrollArea {
#                 border: none;
#                 background-color: transparent;
#             }
#             QScrollBar:vertical {
#                 background-color: #f8f9fa;
#                 width: 12px;
#                 border-radius: 6px;
#             }
#             QScrollBar::handle:vertical {
#                 background-color: #ced4da;
#                 border-radius: 6px;
#                 min-height: 20px;
#             }
#             QScrollBar::handle:vertical:hover {
#                 background-color: #adb5bd;
#             }
#         """)

#     def apply_dark_theme(self):
#         """Apply dark theme styling"""
#         QToolTip.setFont(QFont("Segoe UI", 10))
#         QToolTip.setPalette(QPalette(QColor("#e9ecef"), QColor("#2d3748")))
        
#         self.setStyleSheet("""
#             QWidget {
#                 background-color: #1a1a1a;
#                 color: #e9ecef;
#             }
#             QFrame {
#                 background-color: #2d3748;
#                 border: 1px solid #4a5568;
#                 border-radius: 12px;
#                 padding: 10px;
#             }
#             QFrame#stat_card {
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 #2d3748, stop: 1 #1a202c);
#                 border: 2px solid #4a5568;
#                 border-radius: 12px;
#             }
#             QFrame#stat_card:hover {
#                 border: 2px solid #4299e1;
#                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                             stop: 0 rgba(66, 153, 225, 0.1), 
#                                             stop: 1 rgba(66, 153, 225, 0.05));
#             }
#             QLabel#stat_value {
#                 color: #4299e1;
#             }
#             QPushButton {
#                 background-color: #4299e1;
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 padding: 10px 20px;
#                 font-weight: bold;
#                 font-size: 12px;
#             }
#             QPushButton:hover {
#                 background-color: #3182ce;
#             }
#             QPushButton:pressed {
#                 background-color: #2c5282;
#             }
#             QTextEdit {
#                 background-color: #2d3748;
#                 border: 2px solid #4a5568;
#                 border-radius: 8px;
#                 padding: 15px;
#                 color: #e9ecef;
#                 font-family: 'Consolas', monospace;
#             }
#             QToolTip {
#                 background-color: #2d3748;
#                 color: #e9ecef;
#                 border: 1px solid #4a5568;
#                 padding: 8px;
#                 border-radius: 6px;
#             }
#             QLabel {
#                 color: #e9ecef;
#             }
#             QScrollArea {
#                 border: none;
#                 background-color: transparent;
#             }
#             QScrollBar:vertical {
#                 background-color: #2d3748;
#                 width: 12px;
#                 border-radius: 6px;
#             }
#             QScrollBar::handle:vertical {
#                 background-color: #4a5568;
#                 border-radius: 6px;
#                 min-height: 20px;
#             }
#             QScrollBar::handle:vertical:hover {
#                 background-color: #718096;
#             }
#         """)

#     def set_report(self, df: pd.DataFrame, ticker: str, forecast_df: pd.DataFrame = None):
#         """Populate summary + chart in reports UI (optimized version)"""
#         if df is None or df.empty:
#             self.summary_text.setText("❌ No data available for analysis.")
#             return

#         # Use cached stats if DataFrame hasn't changed
#         if self._cached_stats is None or len(df) != self._cached_stats.get('data_length'):
#             stats = {
#                 "Min Price": float(df["Close"].min()),
#                 "Max Price": float(df["Close"].max()),
#                 "Average Price": float(df["Close"].mean()),
#                 "Volatility": float(df["Close"].std()),
#             }
#             self._cached_stats = {'stats': stats, 'data_length': len(df)}
#         else:
#             stats = self._cached_stats['stats']

#         # Clear and recreate stat cards
#         for card in self.stat_cards.values():
#             card.setParent(None)
#         self.stat_cards.clear()

#         icons = ["📉", "📈", "💰", "📊"]
#         for i, (stat_name, value) in enumerate(stats.items()):
#             card, value_label = self.create_stat_card(
#                 stat_name, f"${value:.2f}", icons[i]
#             )
#             self.stat_cards[stat_name] = card
#             self.stats_layout.addWidget(card, i // 2, i % 2)
        
#         self.stats_layout.setContentsMargins(0, -20, 0, 0)

#         # Update tooltips
#         self.back_btn.setToolTip("Return to the main dashboard")
#         self.export_csv_btn.setToolTip("Export stock data to CSV file")
#         self.export_pdf_btn.setToolTip("Export stock report as PDF")
#         self.report_chart_frame.setToolTip(
#             "Historical and forecasted stock prices with confidence bands"
#         )

#         # Update summary text
#         summary_str = f"🏢 Stock Analysis Report: {ticker}\n"
#         summary_str += "=" * 50 + "\n\n"
#         summary_str += "📊 Key Statistics:\n"
#         for stat_name, value in stats.items():
#             summary_str += f"   • {stat_name}: ${value:.2f}\n"
#         summary_str += f"\n📈 Data Points: {len(df)} records"

#         # Ensure datetime index
#         if not pd.api.types.is_datetime64_any_dtype(df.index):
#             if "Date" in df.columns:
#                 df["Date"] = pd.to_datetime(df["Date"])
#                 df.set_index("Date", inplace=True)
#             else:
#                 df.index = pd.to_datetime(df.index)

#         try:
#             summary_str += f"\n📅 Date Range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
#         except:
#             summary_str += f"\n📅 Date Range: {df.index[0]} to {df.index[-1]}"

#         if forecast_df is not None and not forecast_df.empty:
#             forecast_df.index = pd.to_datetime(forecast_df.index)
#             summary_str += f"\n🔮 Forecast: {len(forecast_df)} future predictions included"
#             if "Forecast" in forecast_df.columns:
#                 avg_forecast = forecast_df["Forecast"].mean()
#                 summary_str += f"\n🎯 Average Forecasted Price: ${avg_forecast:.2f}"

#         self.summary_text.setText(summary_str)

#         # Create chart in background thread
#         self._create_chart_async(df, ticker, forecast_df)

#     def _create_chart_async(self, df, ticker, forecast_df):
#         """Create chart using worker thread to prevent UI blocking"""
#         # Show loading indicator
#         self.loading_label.setVisible(True)
        
#         # Clear old canvas
#         if self.current_canvas:
#             self.current_canvas.setParent(None)
#             self.current_canvas.deleteLater()
#             self.current_canvas = None
        
#         # Stop any existing worker
#         if self.chart_worker and self.chart_worker.isRunning():
#             self.chart_worker.quit()
#             self.chart_worker.wait()
        
#         # Create and start worker
#         self.chart_worker = ChartWorker(df, ticker, forecast_df, self.is_dark_mode)
#         self.chart_worker.chart_ready.connect(self._display_chart)
#         self.chart_worker.error_occurred.connect(self._show_chart_error)
#         self.chart_worker.start()

#     def _display_chart(self, fig):
#         """Display the chart created by worker thread"""
#         self.loading_label.setVisible(False)
        
#         # Create canvas and add to layout
#         self.current_canvas = FigureCanvas(fig)
#         self.current_canvas.setParent(self.report_chart_frame)
#         self.report_chart_layout.addWidget(self.current_canvas)
        
#         # Draw once (no need for update())
#         self.current_canvas.draw_idle()  # Use draw_idle instead of draw for better performance

#     def _show_chart_error(self, error_msg):
#         """Show error message if chart creation fails"""
#         self.loading_label.setVisible(False)
        
#         error_label = QLabel(f"❌ Chart Error: {error_msg}")
#         error_label.setAlignment(Qt.AlignCenter)
#         error_label.setStyleSheet("""
#             QLabel {
#                 color: #ff6b6b;
#                 font-size: 14px;
#                 font-weight: bold;
#                 padding: 20px;
#                 background: rgba(255, 107, 107, 0.1);
#                 border: 2px solid #ff6b6b;
#                 border-radius: 8px;
#             }
#         """)
#         self.report_chart_layout.addWidget(error_label)
    
#     def cleanup(self):
#         """Clean up resources when widget is closed"""
#         if self.chart_worker and self.chart_worker.isRunning():
#             self.chart_worker.quit()
#             self.chart_worker.wait()
        
#         if self.current_canvas:
#             self.current_canvas.deleteLater()
        
#         plt.close('all')

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFrame,
    QSizePolicy, QHBoxLayout, QScrollArea, QGridLayout, QToolTip,
    QApplication, QProgressBar,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np


class ChartWorker(QThread):
    """Worker thread for chart generation to prevent UI blocking"""
    chart_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, df, ticker, forecast_df, is_dark_mode):
        super().__init__()
        self.df = df.copy()
        self.ticker = ticker
        self.forecast_df = forecast_df.copy() if forecast_df is not None else None
        self.is_dark_mode = is_dark_mode
        
    def run(self):
        try:
            fig = self.create_chart()
            self.chart_ready.emit(fig)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def create_chart(self):
        """Create chart in background thread"""
        hist_smoothed = self.df['Close'].rolling(window=3, min_periods=1).mean()
        
        if self.is_dark_mode:
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        fig_color = '#2d3748' if self.is_dark_mode else 'white'
        ax_color = '#020305' if self.is_dark_mode else 'white'
        line_color = '#4299e1' if self.is_dark_mode else '#007bff'
        forecast_color = '#f56565' if self.is_dark_mode else '#dc3545'
        text_color = '#e9ecef' if self.is_dark_mode else '#2c3e50'
        
        fig.patch.set_facecolor(fig_color)
        ax.set_facecolor(ax_color)
        
        # Plot historical data
        ax.plot(
            self.df.index, hist_smoothed,
            label='Historical Price', color=line_color, linewidth=2,
        )
        
        # Plot forecast if available
        if self.forecast_df is not None and not self.forecast_df.empty and 'Forecast' in self.forecast_df.columns:
            # Get only future dates
            last_date = self.df.index[-1]
            future_forecast = self.forecast_df[self.forecast_df.index > last_date]
            
            if len(future_forecast) > 0:
                forecast_smoothed = future_forecast['Forecast'].rolling(window=3, min_periods=1).mean()
                
                ax.plot(
                    future_forecast.index, forecast_smoothed,
                    label='Hybrid Forecast (Prophet + XGBoost)',
                    linestyle='--', color=forecast_color, linewidth=2,
                )
                
                # Confidence interval
                ax.fill_between(
                    future_forecast.index,
                    future_forecast['Lower_Bound'],
                    future_forecast['Upper_Bound'],
                    color='#fbbf24', alpha=0.2,
                    label='Confidence Interval'
                )
        
        # Styling
        ax.set_title(
            f'{self.ticker} Price Analysis & AI Forecast',
            fontsize=16, fontweight='bold', pad=10, color=text_color,
        )
        ax.set_xlabel('Date', fontweight='bold', color=text_color)
        ax.set_ylabel('Price (USD)', fontweight='bold', color=text_color)
        
        legend = ax.legend(loc='upper left', framealpha=0.9)
        legend.get_frame().set_facecolor(fig_color)
        
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.tick_params(colors=text_color)
        
        plt.xticks(rotation=45)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        return fig


class ReportsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = True
        self.current_canvas = None
        self.chart_worker = None
        self._cached_stats = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header section
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(15)

        # Top bar
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

        # Content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)

        # ===== NEW: Progress Bar Section =====
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        
        self.progress_label = QLabel("⏳ Generating forecast...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_font = QFont()
        progress_font.setPointSize(12)
        progress_font.setBold(True)
        self.progress_label.setFont(progress_font)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(30)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_frame.setVisible(False)  # Hidden by default
        # ===== END Progress Bar =====

        # Stats cards
        self.stats_frame = QFrame()
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setSpacing(15)
        self.stat_cards = {}

        # ===== NEW: Model Metrics Section =====
        self.metrics_frame = QFrame()
        self.metrics_frame.setObjectName("metrics_frame")
        metrics_layout = QVBoxLayout(self.metrics_frame)
        
        metrics_title = QLabel("🧠 AI Model Performance")
        metrics_title_font = QFont()
        metrics_title_font.setPointSize(14)
        metrics_title_font.setBold(True)
        metrics_title.setFont(metrics_title_font)
        
        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(10)
        
        metrics_layout.addWidget(metrics_title)
        metrics_layout.addLayout(self.metrics_grid)
        
        self.metrics_frame.setVisible(False)  # Hidden until forecast completes
        # ===== END Metrics =====

        # Summary text area
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

        # Chart section
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
        
        self.loading_label = QLabel("⏳ Loading chart...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)
        self.report_chart_layout.addWidget(self.loading_label)

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.report_chart_frame)

        # Export buttons
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

        # Add all sections
        content_layout.addWidget(self.progress_frame)  # NEW
        content_layout.addWidget(self.stats_frame)
        content_layout.addWidget(self.metrics_frame)   # NEW
        content_layout.addWidget(summary_frame)
        content_layout.addWidget(chart_frame)
        content_layout.addWidget(export_frame)
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(header_frame)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    # ===== NEW METHODS for Progress & Metrics =====
    
    def show_loading(self, message="⏳ Initializing forecast..."):
        """Show loading state when starting forecast"""
        self.progress_frame.setVisible(True)
        self.progress_label.setText(message)
        self.progress_bar.setValue(0)
        self.metrics_frame.setVisible(False)
        self.summary_text.setText(message)
    
    def update_progress(self, message, percentage):
        """Update progress bar during forecast generation"""
        self.progress_label.setText(message)
        self.progress_bar.setValue(percentage)
        QApplication.processEvents()  # Force UI update
    
    def hide_loading(self):
        """Hide loading indicators after forecast completes"""
        self.progress_frame.setVisible(False)
    
    def show_error(self, error_msg):
        """Display error message"""
        self.summary_text.append(f"\n\n❌ {error_msg}")
    
    def display_metrics(self, metrics):
        """Display model performance metrics"""
        if not metrics:
            return
        
        # Clear existing metrics
        while self.metrics_grid.count():
            item = self.metrics_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create metric cards
        metric_info = {
            'MAPE': ('📉', '%', 'Mean Absolute Percentage Error'),
            'RMSE': ('📊', '$', 'Root Mean Squared Error'),
            'Directional Accuracy': ('🎯', '%', 'Prediction Direction Accuracy'),
        }
        
        col = 0
        for key, value in metrics.items():
            if key == 'Models Used':
                continue  # Handle separately
            
            icon, unit, tooltip = metric_info.get(key, ('📈', '', key))
            
            card = QFrame()
            card.setObjectName("metric_card")
            card.setFixedSize(200, 100)
            card.setToolTip(tooltip)
            
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(5)
            
            title_label = QLabel(f"{icon} {key}")
            title_label.setAlignment(Qt.AlignCenter)
            title_font = QFont()
            title_font.setPointSize(9)
            title_font.setBold(True)
            title_label.setFont(title_font)
            
            value_label = QLabel(f"{value}{unit}")
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setObjectName("metric_value")
            value_font = QFont()
            value_font.setPointSize(18)
            value_font.setBold(True)
            value_label.setFont(value_font)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            self.metrics_grid.addWidget(card, 0, col)
            col += 1
        
        # Show which models were used
        if 'Models Used' in metrics:
            models_label = QLabel(f"🤖 Models: {' + '.join(metrics['Models Used'])}")
            models_label.setAlignment(Qt.AlignCenter)
            models_font = QFont()
            models_font.setPointSize(10)
            models_font.setBold(True)
            models_label.setFont(models_font)
            self.metrics_grid.addWidget(models_label, 1, 0, 1, col)
        
        self.metrics_frame.setVisible(True)
    
    # ===== END NEW METHODS =====

    def create_stat_card(self, title, value, icon="📈"):
        """Create a statistics card widget"""
        card = QFrame()
        card.setFixedSize(250, 150)
        card.setObjectName("stat_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(8, 8, 8, 8)

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

        self.setStyleSheet("""
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
            QFrame#stat_card, QFrame#metric_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #ffffff, stop: 1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
            }
            QFrame#stat_card:hover, QFrame#metric_card:hover {
                border: 2px solid #007bff;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(0, 123, 255, 0.05), 
                                            stop: 1 rgba(0, 123, 255, 0.02));
            }
            QLabel#stat_value, QLabel#metric_value {
                color: #007bff;
            }
            QProgressBar {
                border: 2px solid #007bff;
                border-radius: 8px;
                text-align: center;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #007bff;
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
            }
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', monospace;
            }
        """)

    def apply_dark_theme(self):
        """Apply dark theme styling"""
        QToolTip.setFont(QFont("Segoe UI", 10))
        QToolTip.setPalette(QPalette(QColor("#e9ecef"), QColor("#2d3748")))
        
        self.setStyleSheet("""
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
            QFrame#stat_card, QFrame#metric_card {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 12px;
            }
            QFrame#stat_card:hover, QFrame#metric_card:hover {
                border: 2px solid #4299e1;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(66, 153, 225, 0.1), 
                                            stop: 1 rgba(66, 153, 225, 0.05));
            }
            QLabel#stat_value, QLabel#metric_value {
                color: #4299e1;
            }
            QProgressBar {
                border: 2px solid #4299e1;
                border-radius: 8px;
                text-align: center;
                background-color: #1a202c;
            }
            QProgressBar::chunk {
                background-color: #4299e1;
                border-radius: 6px;
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
            }
            QTextEdit {
                background-color: #2d3748;
                border: 2px solid #4a5568;
                border-radius: 8px;
                padding: 15px;
                color: #e9ecef;
                font-family: 'Consolas', monospace;
            }
        """)

    def set_report(self, df: pd.DataFrame, ticker: str, forecast_df: pd.DataFrame = None, metrics: dict = None):
        """Populate summary + chart + metrics in reports UI"""
        if df is None or df.empty:
            self.summary_text.setText("❌ No data available for analysis.")
            self.hide_loading()
            return

        # Hide loading indicators
        self.hide_loading()

        # Calculate and display stats
        if self._cached_stats is None or len(df) != self._cached_stats.get('data_length'):
            stats = {
                "Min Price": float(df["Close"].min()),
                "Max Price": float(df["Close"].max()),
                "Average Price": float(df["Close"].mean()),
                "Volatility": float(df["Close"].std()),
            }
            self._cached_stats = {'stats': stats, 'data_length': len(df)}
        else:
            stats = self._cached_stats['stats']

        # Recreate stat cards
        for card in self.stat_cards.values():
            card.setParent(None)
        self.stat_cards.clear()

        icons = ["📉", "📈", "💰", "📊"]
        for i, (stat_name, value) in enumerate(stats.items()):
            card, value_label = self.create_stat_card(
                stat_name, f"${value:.2f}", icons[i]
            )
            self.stat_cards[stat_name] = card
            self.stats_layout.addWidget(card, i // 2, i % 2)
        
        self.stats_layout.setContentsMargins(0, -20, 0, 0)

        # Display metrics if available
        if metrics:
            self.display_metrics(metrics)

        # Update summary text
        summary_str = f"🏢 Stock Analysis Report: {ticker}\n"
        summary_str += "=" * 50 + "\n\n"
        summary_str += "📊 Key Statistics:\n"
        for stat_name, value in stats.items():
            summary_str += f"   • {stat_name}: ${value:.2f}\n"
        summary_str += f"\n📈 Data Points: {len(df)} records"

        # Ensure datetime index
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)
            else:
                df.index = pd.to_datetime(df.index)

        try:
            summary_str += f"\n📅 Date Range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
        except:
            summary_str += f"\n📅 Date Range: {df.index[0]} to {df.index[-1]}"

        if forecast_df is not None and not forecast_df.empty:
            forecast_df.index = pd.to_datetime(forecast_df.index)
            future_points = len(forecast_df[forecast_df.index > df.index[-1]])
            summary_str += f"\n🔮 Forecast: {future_points} future predictions"
            
            if "Forecast" in forecast_df.columns:
                future_fc = forecast_df[forecast_df.index > df.index[-1]]
                if len(future_fc) > 0:
                    avg_forecast = future_fc["Forecast"].mean()
                    summary_str += f"\n🎯 Average Forecasted Price: ${avg_forecast:.2f}"

        # Add metrics summary
        if metrics:
            summary_str += f"\n\n🧠 AI Model Performance:"
            for key, value in metrics.items():
                if key != 'Models Used':
                    summary_str += f"\n   • {key}: {value}"
                else:
                    summary_str += f"\n   • {key}: {', '.join(value)}"

        self.summary_text.setText(summary_str)

        # Create chart asynchronously
        self._create_chart_async(df, ticker, forecast_df)

    def _create_chart_async(self, df, ticker, forecast_df):
        """Create chart using worker thread"""
        self.loading_label.setVisible(True)
        
        if self.current_canvas:
            self.current_canvas.setParent(None)
            self.current_canvas.deleteLater()
            self.current_canvas = None
        
        if self.chart_worker and self.chart_worker.isRunning():
            self.chart_worker.quit()
            self.chart_worker.wait()
        
        self.chart_worker = ChartWorker(df, ticker, forecast_df, self.is_dark_mode)
        self.chart_worker.chart_ready.connect(self._display_chart)
        self.chart_worker.error_occurred.connect(self._show_chart_error)
        self.chart_worker.start()

    def _display_chart(self, fig):
        """Display chart from worker"""
        self.loading_label.setVisible(False)
        
        self.current_canvas = FigureCanvas(fig)
        self.current_canvas.setParent(self.report_chart_frame)
        self.report_chart_layout.addWidget(self.current_canvas)
        self.current_canvas.draw_idle()

    def _show_chart_error(self, error_msg):
        """Show error if chart fails"""
        self.loading_label.setVisible(False)
        
        error_label = QLabel(f"❌ Chart Error: {error_msg}")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 14px;
                font-weight: bold;
                padding: 20px;
                background: rgba(255, 107, 107, 0.1);
                border: 2px solid #ff6b6b;
                border-radius: 8px;
            }
        """)
        self.report_chart_layout.addWidget(error_label)
    
    def cleanup(self):
        """Clean up resources"""
        if self.chart_worker and self.chart_worker.isRunning():
            self.chart_worker.quit()
            self.chart_worker.wait()
        
        if self.current_canvas:
            self.current_canvas.deleteLater()
        
        plt.close('all')