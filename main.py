# main.py - OPTIMIZED VERSION
# pyqt5 library
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QStackedWidget,
    QPushButton,
    QMessageBox,
    QFrame,
    QLabel,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QCursor
from prophet import Prophet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from dotenv import load_dotenv

# core python libraries
import sys
import pandas as pd
import os
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

# workers
from workers.ai_worker import AIChatWorker
from workers.live_price_worker import LivePriceWorker
from workers.news_worker import LiveNewsWorker
from workers.sentiment_worker import SentimentWorker
from workers.hybrid_forecast_worker import HybridForecastWorker
from workers.ai_report_worker import AIReportWorker

# ui
from ui.ui_main import DashboardUI
from ui.ui_reports import ReportsUI

# widgets
from widgets.chart_widget import ChartWidget
from widgets.news_widget import NewsWidget
from widgets.chatbot_button import ChatbotButton
from widgets.chat_widget import ChatWidget
from widgets.sentiment_widget import SentimentWidget

# data handlers and indicators
from core.data_handler import get_news, get_stock_data, get_fundamentals, get_details
from core.indicators import calculate_sma, calculate_ema

# styles
from styles import get_theme


# -------- Forecast Worker (NEW) ----------#
# class ForecastWorker(QThread):
#     """Worker thread for Prophet forecasting to prevent UI blocking"""
#     forecast_ready = pyqtSignal(object)  # Emits forecast DataFrame
#     error_occurred = pyqtSignal(str)

#     def __init__(self, df):
#         super().__init__()
#         self.df = df.copy()  # Copy to avoid threading issues

#     def run(self):
#         try:
#             import logging
#             logging.getLogger('prophet').setLevel(logging.WARNING)

#             prophet_df = self.df.reset_index()[['Date', 'Close']].rename(
#                 columns={'Date': 'ds', 'Close': 'y'}
#             )

#             model = Prophet(daily_seasonality=True, yearly_seasonality=True)
#             model.fit(prophet_df)

#             future = model.make_future_dataframe(periods=30)
#             forecast = model.predict(future)

#             forecast_df = forecast.set_index('ds')[
#                 ['yhat', 'yhat_lower', 'yhat_upper']
#             ].rename(
#                 columns={
#                     'yhat': 'Forecast',
#                     'yhat_lower': 'Lower_Bound',
#                     'yhat_upper': 'Upper_Bound',
#                 }
#             )

#             self.forecast_ready.emit(forecast_df)
#         except Exception as e:
#             self.error_occurred.emit(str(e))


# -------- Export Worker (Background file I/O) ----------#
class ExportWorker(QThread):
    """Background worker for CSV/PDF exports to prevent UI blocking"""
    finished = pyqtSignal(str, str)  # (path, export_type)
    error = pyqtSignal(str)

    def __init__(self, df, ticker, export_type, avg_price=0, min_price=0, max_price=0, total_volume=0):
        super().__init__()
        self.df = df.copy()
        self.ticker = ticker
        self.export_type = export_type
        self.avg_price = avg_price
        self.min_price = min_price
        self.max_price = max_price
        self.total_volume = total_volume

    def run(self):
        try:
            os.makedirs("reports", exist_ok=True)
            if self.export_type == "csv":
                path = f"reports/{self.ticker}_reports.csv"
                self.df.to_csv(path)
            else:  # pdf
                path = f"reports/{self.ticker}_report.pdf"
                self._create_pdf(path)
            self.finished.emit(path, self.export_type)
        except Exception as e:
            self.error.emit(str(e))

    def _create_pdf(self, path):
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        doc = SimpleDocTemplate(path)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"📈 Stock Report for {self.ticker}", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"💰 Average Price: ${self.avg_price:.2f}", styles["Normal"]),
            Paragraph(f"📉 Minimum Price: ${self.min_price:.2f}", styles["Normal"]),
            Paragraph(f"📈 Maximum Price: ${self.max_price:.2f}", styles["Normal"]),
            Paragraph(f"📊 Total Volume: {self.total_volume:,}", styles["Normal"]),
            Spacer(1, 12),
        ]
        
        # Add data table (limited rows for performance)
        data = [["Date", "Open", "High", "Low", "Close", "Volume"]]
        for _, row in self.df.tail(20).iterrows():
            data.append([
                str(row.get("Date", ""))[:10],
                f"${row.get('Open', 0):.2f}",
                f"${row.get('High', 0):.2f}",
                f"${row.get('Low', 0):.2f}",
                f"${row.get('Close', 0):.2f}",
                f"{int(row.get('Volume', 0)):,}"
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        doc.build(story)


# -------- Data Worker ----------#
class DataWorker(QThread):
    finished = pyqtSignal(object, str, dict, str, list)
    error = pyqtSignal(str)

    def __init__(self, ticker, indicators, parent=None):
        super().__init__(parent)
        self.ticker = ticker
        self.indicators = indicators

    def run(self):
        try:
            df = get_stock_data(self.ticker)
            if df is None or df.empty:
                self.error.emit("No data found.")
                return

            numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df.dropna(subset=numeric_cols, inplace=True)

            # Indicators
            if "MA" in self.indicators:
                df = calculate_sma(df)
                df = calculate_ema(df)

            fundamentals = get_fundamentals(self.ticker)
            details = get_details(self.ticker)
            news_list = get_news(self.ticker)

            self.finished.emit(df, self.ticker, fundamentals, details, news_list)

        except Exception as e:
            self.error.emit(str(e))


# ---------------- Main Window ---------------- #
class StockDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 StockDash - Professional Market Analysis")
        self.resize(1400, 800)
        self.setMinimumSize(1200, 700)

        # --- Create stacked widget to hold all pages ---
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Initialize pages ---
        self.dashboard_ui = DashboardUI()
        self.reports_ui = ReportsUI()
        self.sentiment_widget = SentimentWidget()

        # Add pages to stack
        self.stacked_widget.addWidget(self.dashboard_ui)  # index 0
        self.stacked_widget.addWidget(self.reports_ui)  # index 1
        self.stacked_widget.addWidget(self.sentiment_widget)  # index 2

        # Start with dashboard
        self.stacked_widget.setCurrentWidget(self.dashboard_ui)

        # Setup chart widget
        if self.dashboard_ui.chart_frame.layout() is None:
            self.dashboard_ui.chart_frame.setLayout(QVBoxLayout())

        # Theme state
        self.is_dark_mode = True
        self.apply_theme()

        self.chart_widget = ChartWidget(is_dark=self.is_dark_mode)
        self.dashboard_ui.chart_frame.layout().addWidget(self.chart_widget)

        # Enhanced Theme toggle button setup
        self.setup_theme_button()

        # Enhanced sidebar connections
        self.connect_sidebar()
        self.setup_chat_system()

        # Dashboard signals with debouncing
        self.dashboard_ui.ticker_input.returnPressed.connect(self.load_data)
        self.dashboard_ui.search_btn.clicked.connect(self.load_data)

        # OPTIMIZATION: Debounce checkbox changes
        self._checkbox_debounce_timer = QTimer()
        self._checkbox_debounce_timer.setSingleShot(True)
        self._checkbox_debounce_timer.setInterval(500)  # 500ms debounce (increased from 300ms)
        self._checkbox_debounce_timer.timeout.connect(self._reload_chart_only)

        self.dashboard_ui.ma_checkbox.stateChanged.connect(
            self._debounced_indicator_change
        )
        self.dashboard_ui.rsi_checkbox.stateChanged.connect(
            self._debounced_indicator_change
        )
        self.dashboard_ui.macd_checkbox.stateChanged.connect(
            self._debounced_indicator_change
        )
        self.dashboard_ui.bb_checkbox.stateChanged.connect(
            self._debounced_indicator_change
        )
        self.dashboard_ui.sr_checkbox.stateChanged.connect(
            self._debounced_indicator_change
        )

        # Reports UI part variables
        self.last_df = None
        self.last_ticker = None

        self.avg_price = 0.0
        self.total_records = 0

        self._latest_price = None
        self._price_update_timer = QTimer(self)
        self._price_update_timer.setInterval(
            2000
        )  # OPTIMIZED: Changed from 500ms to 2000ms
        self._price_update_timer.timeout.connect(self._flush_latest_price_to_ui)

        # Reports button actions
        if hasattr(self.reports_ui, "back_btn"):
            self.reports_ui.back_btn.clicked.connect(self.show_dashboard)
        if hasattr(self.reports_ui, "export_csv_btn"):
            self.reports_ui.export_csv_btn.clicked.connect(self.export_csv)
        if hasattr(self.reports_ui, "export_pdf_btn"):
            self.reports_ui.export_pdf_btn.clicked.connect(self.export_pdf)
        if hasattr(self.reports_ui, "generate_ai_report_btn"):
            self.reports_ui.generate_ai_report_btn.clicked.connect(self.generate_ai_report)

        # Sentiment widget button actions
        if hasattr(self.sentiment_widget, "back_btn"):
            self.sentiment_widget.back_btn.clicked.connect(self.show_dashboard)

        # Worker references
        self.worker = None
        self.live_worker = None
        self.news_worker = None
        self.sentiment_worker = None
        self.ai_worker = None
        self.forecast_worker = None  # Hybrid Forecast Worker
        self.ai_report_worker = None  # AI Report Worker

    def _debounced_indicator_change(self):
        """Debounce checkbox changes to avoid excessive reloads"""
        self._checkbox_debounce_timer.start()

    def _reload_chart_only(self):
        """Reload only the chart without fetching new data"""
        if self.last_df is not None:
            self.chart_widget.plot_chart(
                self.last_df,
                self.last_ticker,
                show_sma=self.dashboard_ui.ma_checkbox.isChecked(),
                show_ema=self.dashboard_ui.ma_checkbox.isChecked(),
                show_rsi=self.dashboard_ui.rsi_checkbox.isChecked(),
                show_macd=self.dashboard_ui.macd_checkbox.isChecked(),
                show_bb=self.dashboard_ui.bb_checkbox.isChecked(),
                show_sr=self.dashboard_ui.sr_checkbox.isChecked(),
            )

    def generate_ai_report(self):
        """Generate AI-powered stock report using Groq API"""
        if self.last_df is None or self.last_ticker is None:
            QMessageBox.warning(
                self,
                "No Data",
                "📋 Please load stock data first before generating AI report."
            )
            return
        
        # Check for api key
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            QMessageBox.warning(
                self,
                "API Key Missing",
                "⚠️ GROQ_API_KEY not found in environment.\nPlease add it to your .env file."
            )
            return
        
        try:
            # Disable button during generation
            self.reports_ui.generate_ai_report_btn.setEnabled(False)
            self.reports_ui.generate_ai_report_btn.setText("⏳ Generating...")
            self.reports_ui.update_ai_status("🚀 Starting AI report generation...", 0)

            # prepare stock data package
            stock_data_package = {
                'dataframe': self.last_df,
                'ticker': self.last_ticker,
                'forecast': None
            }

            # Add forecast data if available (from hybrid forecast)
            if hasattr(self, 'last_forecast_df') and self.last_forecast_df is not None:
                try:
                    latest_forecast = self.last_forecast_df.iloc[-1]
                    stock_data_package['forecast'] = {
                        'forecasted_price': f"{latest_forecast['Forecast']:.2f}",
                        'lower_bound': f"{latest_forecast['Lower_Bound']:.2f}",
                        'upper_bound': f"{latest_forecast['Upper_Bound']:.2f}",
                        'model': 'Hybrid LSTM + Prophet',
                        'confidence': 'Medium-High'
                    }
                except Exception as e:
                    print(f"Could not add forecast data: {e}")

            # Clean up previous ai report worker
            if self.ai_report_worker and self.ai_report_worker.isRunning():
                self.ai_report_worker.cancel()
                self.ai_report_worker.quit()
                self.ai_report_worker.wait(1000)

            # Create and start ai report worker
            self.ai_report_worker = AIReportWorker(
                api_key=api_key,
                ticker=self.last_ticker,
                stock_data=stock_data_package
            )

            # Connect signals
            self.ai_report_worker.report_ready.connect(self._display_ai_report)
            self.ai_report_worker.progress_update.connect(self._update_ai_report_progress)
            self.ai_report_worker.error_occurred.connect(self._handle_ai_report_error)

            # Start generation
            self.ai_report_worker.start()
            print(f"🤖 Started AI report generation for {self.last_ticker}")

        except Exception as e:
            self._handle_ai_report_error(f"Failed to start AI report generation: {str(e)}")


    def handle_user_message(self, message: str, request_id: str):
        """Handle user message and call AI worker"""
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        # Clean up previous AI worker
        if self.ai_worker:
            if self.ai_worker.isRunning():
                self.ai_worker.quit()
                try:
                    self.ai_worker.response_ready.disconnect()
                    self.ai_worker.error_occurred.disconnect()
                except: pass
                self.ai_worker.finished.connect(self.ai_worker.deleteLater)
            else:
                self.ai_worker.deleteLater()
            self.ai_worker = None

        # TODO: Modify AIChatWorker to accept parent if possible, for now just cleaning up
        self.ai_worker = AIChatWorker(api_key, message)
        self.ai_worker.response_ready.connect(
            lambda resp: self.chat_widget.add_ai_response(resp, request_id)
        )
        self.ai_worker.error_occurred.connect(
            lambda err: self.chat_widget.add_error_message(err, request_id)
        )
        self.ai_worker.start()

    def setup_chat_system(self):
        """Setup the AI chat system components"""
        self.chatbot_button = ChatbotButton(self.is_dark_mode)
        self.chatbot_button.setParent(self)
        self.chatbot_button.clicked_with_animation.connect(self.toggle_chat)
        self.position_chatbot_button()

        self.chat_widget = ChatWidget(self.is_dark_mode)
        self.chat_widget.setParent(self)
        self.chat_widget.hide()

        self.chat_widget.user_message_sent.connect(self.handle_user_message)
        self.chat_widget.chat_closed.connect(self.on_chat_closed)

        self.chat_visible = False

    def position_chatbot_button(self):
        """Position the chatbot button at bottom right"""
        button_size = 60
        margin = 20
        x = self.width() - button_size - margin
        y = self.height() - button_size - margin - 50
        self.chatbot_button.move(x, y)
        self.chatbot_button.raise_()

    def resizeEvent(self, event):
        """Handle window resize to reposition chatbot button"""
        super().resizeEvent(event)
        self.position_chatbot_button()

    def toggle_chat(self):
        """Toggle chat widget visibility"""
        if not self.chat_visible:
            self.show_chat()
        else:
            self.hide_chat()

    def show_chat(self):
        """Show the chat widget with animation"""
        if not self.chat_visible:
            self.chat_widget.show_animated(self.geometry())
            self.chat_visible = True

    def hide_chat(self):
        """Hide the chat widget"""
        if self.chat_visible:
            self.chat_widget.close_chat()

    def on_chat_closed(self):
        """Handle chat widget closed"""
        self.chat_visible = False

    def setup_theme_button(self):
        """Enhanced theme button setup"""
        theme_buttons = self.dashboard_ui.findChildren(QPushButton)
        for btn in theme_buttons:
            if btn.objectName() == "theme_button":
                self.theme_btn = btn
                break
        else:
            self.theme_btn = QPushButton("🌙/☀️")
            self.theme_btn.setObjectName("theme_button")

        self.theme_btn.clicked.connect(self.toggle_theme)

    def connect_sidebar(self):
        """Enhanced sidebar connections"""
        nav_buttons = self.dashboard_ui.findChildren(QPushButton)

        for btn in nav_buttons:
            if btn.objectName() == "nav_button":
                btn_text = btn.text().lower()
                if "dashboard" in btn_text:
                    btn.clicked.connect(self.show_dashboard)
                elif "reports" in btn_text:
                    btn.clicked.connect(self.show_reports)
                elif "history" in btn_text:
                    btn.clicked.connect(self.show_history_placeholder)
                elif "market mood" in btn_text:
                    btn.clicked.connect(self.show_market_mood)

    def show_dashboard(self):
        """Switch to dashboard and stop Market Mood workers"""
        if self.news_worker and self.news_worker.isRunning():
            self.news_worker.stop()
            self.news_worker.quit()
            self.news_worker.wait(2000)
            print("🛑 News worker stopped (switching to dashboard)")

        self.stacked_widget.setCurrentWidget(self.dashboard_ui)

        # Restart price updates if ticker loaded
        if self._latest_price and not self._price_update_timer.isActive():
            self._price_update_timer.start()

    def show_reports(self):
        """Switch to reports page and generate report if ticker loaded (OPTIMIZED)"""
        if self.news_worker and self.news_worker.isRunning():
            self.news_worker.stop()
            self.news_worker.quit()
            self.news_worker.wait(2000)
            print("🛑 News worker stopped (switching to reports)")

        if self.last_df is not None:
            # Show loading message
            self.reports_ui.show_loading("⏳ Initializing forecast models...")

            # Switch to reports immediately (don't block)
            self.stacked_widget.setCurrentWidget(self.reports_ui)

            # Start forecast in background
            self._start_hybrid_forecast_async()
        else:
            self.stacked_widget.setCurrentWidget(self.reports_ui)

    def _start_hybrid_forecast_async(self):
        """Start forecast generation in background thread"""
        # Clean up previous forecast worker
        if self.forecast_worker and self.forecast_worker.isRunning():
            self.forecast_worker.cancel()
            self.forecast_worker.quit()
            self.forecast_worker.wait(1000)

        self.forecast_worker = HybridForecastWorker(self.last_df, periods=30)
        # Connect signals
        self.forecast_worker.forecast_ready.connect(
            self._display_report_with_hybrid_forecast
        )
        self.forecast_worker.progress_update.connect(self._update_forecast_progress)
        self.forecast_worker.error_occurred.connect(
            self._display_report_without_forecast
        )

        # Start forecast
        self.forecast_worker.start()
        print(f"🚀 Started hybrid forecast for {self.last_ticker}")

    def _update_forecast_progress(self, message, percentage):
        """Update progress indicator during forecast generation"""
        if self.stacked_widget.currentWidget() == self.reports_ui:
            self.reports_ui.update_progress(message, percentage)

    def _display_ai_report(self, report_text):
        """Display the generated AI report"""
        if self.stacked_widget.currentWidget() == self.reports_ui:
            self.reports_ui.set_ai_report(report_text)
            print("✅ AI report displayed successfully")

        # re enable button
        self.reports_ui.generate_ai_report_btn.setEnabled(True)
        self.reports_ui.generate_ai_report_btn.setText("⚡ Generate AI Report")

    def _update_ai_report_progress(self, message, percentage):
        """Update progress during ai report generation"""
        if self.stacked_widget.currentWidget() == self.reports_ui:
            self.reports_ui.update_ai_status(message, percentage)

    def _handle_ai_report_error(self, error_msg):
        """Handle AI report generation errors"""
        print(f"❌ AI Report Error: {error_msg}") 
        if self.stacked_widget.currentWidget() == self.reports_ui:
            self.reports_ui.show_ai_error(error_msg)

        # Re enable button
        self.reports_ui.generate_ai_report_btn.setEnabled(True)
        self.reports_ui.generate_ai_report_btn.setText("⚡ Generate AI Report")

     

    def _display_report_with_hybrid_forecast(self, forecast_df, metrics):
        """Display report with hybrid forecast and metrics"""
        if self.stacked_widget.currentWidget() == self.reports_ui:
            print(f"✅ Hybrid forecast complete! Metrics: {metrics}")
            # Store forecast_df for ai report generation
            self.last_forecast_df = forecast_df
            self.reports_ui.set_report(
                self.last_df, self.last_ticker, forecast_df, metrics
            )

    def _display_report_without_forecast(self, error_msg):
        """Display report without forecast if forecast fails"""
        print(f"Forecast error: {error_msg}")
        if self.stacked_widget.currentWidget() == self.reports_ui:
            self.reports_ui.set_report(self.last_df, self.last_ticker, None, None)
            self.reports_ui.show_error(f"Forecast failed: {error_msg}")

    def show_history_placeholder(self):
        """Placeholder for history functionality"""
        QMessageBox.information(
            self, "Coming Soon", "📊 History feature coming in the next version!"
        )

    def show_market_mood(self):
        """Switch to Market Mood view and start live updates"""
        if not self.last_ticker:
            QMessageBox.warning(
                self,
                "No Ticker Loaded",
                "⚠️ Please search for a stock first before viewing Market Mood!",
            )
            return

        self.stacked_widget.setCurrentWidget(self.sentiment_widget)
        self.start_live_news()
        print(f"✅ Market Mood view opened for {self.last_ticker}")

    def apply_theme(self):
        self.setStyleSheet(get_theme(self.is_dark_mode))

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        # Apply stylesheet first - this is fast
        self.apply_theme()

        # Update button immediately
        if hasattr(self, "theme_btn"):
            self.theme_btn.setText("☀️" if self.is_dark_mode else "🌙")

        # Defer heavy theme operations to prevent UI blocking
        QTimer.singleShot(10, lambda: self.chart_widget.set_theme(self.is_dark_mode))
        QTimer.singleShot(30, lambda: self.reports_ui.set_theme(self.is_dark_mode))

        if hasattr(self, "sentiment_widget"):
            QTimer.singleShot(50, lambda: self.sentiment_widget.setStyleSheet(get_theme(self.is_dark_mode)))

    def start_live_news(self):
        """Start fetching live news and analyzing sentiment"""
        if not self.last_ticker:
            print("⚠️ No ticker loaded, cannot start news feed")
            return

        try:
            if self.news_worker and self.news_worker.isRunning():
                self.news_worker.stop()
                self.news_worker.quit()
                self.news_worker.wait(2000)
                print("🛑 Stopped previous news worker")

            self.news_worker = LiveNewsWorker(self.last_ticker, interval=60)
            self.news_worker.news_ready.connect(self.handle_live_news)
            self.news_worker.start()

            print(f"📰 Started live news feed for {self.last_ticker}")

        except Exception as e:
            print(f"❌ Error starting news worker: {e}")
            QMessageBox.critical(
                self, "News Feed Error", f"❌ Failed to start news feed: {str(e)}"
            )

    def handle_live_news(self, news):
        """Process live news and run sentiment analysis"""
        if self.stacked_widget.currentWidget() != self.sentiment_widget:
            return

        self.sentiment_widget.update_news(news)
        headlines = [item["title"] for item in news if item.get("title")]

        if not headlines:
            print("⚠️ No headlines to analyze")
            return

        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            print("⚠️ GROQ_API_KEY not found in environment")
            return

        if self.sentiment_worker and self.sentiment_worker.isRunning():
            self.sentiment_worker.stop()
            self.sentiment_worker.quit()
            self.sentiment_worker.wait(1500)

        self.sentiment_worker = SentimentWorker(api_key, headlines)
        self.sentiment_worker.sentiment_ready.connect(self.update_sentiment_ui)
        self.sentiment_worker.error_occurred.connect(
            lambda err: print(f"Sentiment error: {err}")
        )
        self.sentiment_worker.start()

    def update_sentiment_ui(self, sentiment):
        """Update sentiment display only if on Market Mood page"""
        if self.stacked_widget.currentWidget() == self.sentiment_widget:
            self.sentiment_widget.update_sentiment(sentiment)

    # ---------------- Data Loading ---------------- #
    def load_data(self):
        if self.stacked_widget.currentWidget() != self.dashboard_ui:
            return

        ticker = self.dashboard_ui.ticker_input.text().upper().strip()
        if not ticker:
            QMessageBox.warning(
                self, "Input Required", "Please enter a stock symbol (e.g., AAPL)"
            )
            return

        self.dashboard_ui.search_btn.setEnabled(False)
        self.dashboard_ui.search_btn.setText("⏳ Loading...")
        self.dashboard_ui.avg_label.setText("⏳ Loading market data...")

        indicators = []
        if self.dashboard_ui.ma_checkbox.isChecked():
            indicators.append("MA")

        if self.worker:
            if self.worker.isRunning():
                self.worker.quit()
                try:
                    self.worker.finished.disconnect()
                    self.worker.error.disconnect()
                except: pass
                # Clean up when finished (non-blocking)
                self.worker.finished.connect(self.worker.deleteLater)
            else:
                self.worker.deleteLater()
            self.worker = None

        self.worker = DataWorker(ticker, indicators, parent=self)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_data_error)
        self.worker.start()

    def on_data_loaded(self, df, ticker, fundamentals, details, news_list):
        self.last_df = df
        self.last_ticker = ticker

        try:
            self.avg_price = df["Close"].mean()
            self.total_records = len(df)

            self.dashboard_ui.avg_label.setText(
                f"💰 Avg: ${self.avg_price:.2f} | 📊 Records: {self.total_records} | 📡 Connecting..."
            )

            # Chart update - already uses background worker
            self.chart_widget.plot_chart(
                df,
                ticker,
                show_sma=self.dashboard_ui.ma_checkbox.isChecked(),
                show_ema=self.dashboard_ui.ma_checkbox.isChecked(),
                show_rsi=self.dashboard_ui.rsi_checkbox.isChecked(),
                show_macd=self.dashboard_ui.macd_checkbox.isChecked(),
                show_bb=self.dashboard_ui.bb_checkbox.isChecked(),
                show_sr=self.dashboard_ui.sr_checkbox.isChecked(),
            )

            # Fundamentals display - quick string operation
            if fundamentals:
                fund_items = []
                for k, v in fundamentals.items():
                    icon = (
                        "📈"
                        if any(word in k.lower() for word in ["price", "value"])
                        else (
                            "💹"
                            if any(word in k.lower() for word in ["ratio", "pe"])
                            else (
                                "💰"
                                if any(word in k.lower() for word in ["cap", "revenue"])
                                else "📊"
                            )
                        )
                    )
                    fund_items.append(f"{icon} {k}: {v}")
                fund_text = "\n".join(fund_items)
            else:
                fund_text = "📊 Fundamental data not available for this symbol"

            self.dashboard_ui.fundamentals_text.setText(fund_text)

            # Details display
            if details:
                self.dashboard_ui.set_company_details(f"🏢 {details}")
            else:
                self.dashboard_ui.set_company_details(
                    "🏢 Company details not available"
                )

            # Re-enable search button immediately
            self.dashboard_ui.search_btn.setEnabled(True)
            self.dashboard_ui.search_btn.setText("🔍 SEARCH")

            # DEFER heavy operations to next event loop iteration
            # This prevents UI from blocking during widget creation
            QTimer.singleShot(0, lambda: self._update_news_widgets(news_list))
            QTimer.singleShot(50, lambda: self._start_live_price_worker(ticker))

        except Exception as e:
            self.on_data_error(f"Error processing data: {str(e)}")

    def _start_live_price_worker(self, ticker):
        """Start live price updates in background - called deferred"""
        try:
            if self.live_worker:
                if self.live_worker.isRunning():
                    self.live_worker.stop()
                    # Disconnect signals
                    try:
                        self.live_worker.price_update.disconnect()
                        self.live_worker.error.disconnect()
                    except: pass
                    # Safe cleanup
                    self.live_worker.finished.connect(self.live_worker.deleteLater)
                else:
                    self.live_worker.deleteLater()
                print("🛑 Stopping previous live worker")
                self.live_worker = None

            # Pass parent=self for safety
            self.live_worker = LivePriceWorker(ticker, parent=self)
            self.live_worker.price_update.connect(self.on_live_price)
            self.live_worker.error.connect(lambda err: print("Live WS Error:", err))
            self.live_worker.start()
            print(f"📡 Live price updates started for {ticker}")
        except Exception as e:
            print(f"⚠️ Could not start live feed: {e}")

    def _update_news_widgets(self, news_list):
        """Efficiently update news widgets (OPTIMIZED)"""
        # Clear existing news
        while self.dashboard_ui.news_layout.count():
            item = self.dashboard_ui.news_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

        # Removed processEvents() - deleteLater() handles cleanup asynchronously

        if news_list:
            # Limit to 5 news items and create them efficiently
            for news in news_list[:5]:
                news_widget = self.create_enhanced_news_widget(news)
                self.dashboard_ui.news_layout.addWidget(news_widget)
        else:
            no_news = QLabel("📰 No recent news available for this symbol")
            no_news.setAlignment(Qt.AlignCenter)
            no_news.setStyleSheet(
                """
                QLabel {
                    color: #64748b;
                    font-style: italic;
                    padding: 20px;
                    background: rgba(100, 116, 139, 0.1);
                    border-radius: 8px;
                    margin: 4px;
                }
            """
            )
            self.dashboard_ui.news_layout.addWidget(no_news)

    def on_live_price(self, ticker, price):
        """Store latest price — UI updated from timer (non-blocking)."""
        try:
            self._latest_price = (ticker, float(price))
            if not self._price_update_timer.isActive():
                self._price_update_timer.start()
        except Exception as e:
            print(f"Live price buffer error: {e}")

    def _flush_latest_price_to_ui(self):
        """Called on QTimer to update UI with the latest buffered price."""
        if not self._latest_price:
            return

        if self.stacked_widget.currentWidget() != self.dashboard_ui:
            self._price_update_timer.stop()
            return

        try:
            ticker, price = self._latest_price
            self.dashboard_ui.avg_label.setText(
                f"💰 Avg: ${self.avg_price:.2f} | 📡 Live: ${price:.2f} | 📊 Records: {self.total_records}"
            )
        except Exception as e:
            print(f"Error flushing live price to UI: {e}")

    def create_enhanced_news_widget(self, news):
        """Create an enhanced news widget with better styling (OPTIMIZED)"""
        news_frame = QFrame()
        news_frame.setObjectName("news_item")
        news_frame.setCursor(QCursor(Qt.PointingHandCursor))
        news_frame.setMinimumHeight(120)

        # OPTIMIZED: Use simpler stylesheet
        if self.is_dark_mode:
            news_frame.setStyleSheet(
                """
                QFrame#news_item {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 12px;
                    padding: 12px;
                    margin: 4px 0px;
                }
                QFrame#news_item:hover {
                    background-color: #2d3748;
                    border: 1px solid #3b82f6;
                }
            """
            )
        else:
            news_frame.setStyleSheet(
                """
                QFrame#news_item {
                    background-color: white;
                    border: 1px solid rgba(59, 130, 246, 0.2);
                    border-radius: 12px;
                    padding: 12px;
                    margin: 4px 0px;
                }
                QFrame#news_item:hover {
                    background-color: #dbeafe;
                    border: 1px solid #3b82f6;
                }
            """
            )

        layout = QVBoxLayout(news_frame)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # News header with timestamp
        header_layout = QHBoxLayout()

        if "published" in news and news["published"]:
            time_label = QLabel(f"📅 {news['published'][:10]}")
            time_label.setStyleSheet(
                """
                QLabel {
                    font-size: 10px;
                    color: #6b7280;
                    font-weight: 500;
                    background: rgba(107, 114, 128, 0.1);
                    padding: 2px 6px;
                    border-radius: 4px;
                }
            """
            )
            header_layout.addWidget(time_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # News title
        title_text = news.get("title", "Market Update")
        title_label = QLabel(f"📰 {title_text}")
        title_label.setWordWrap(True)

        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setWeight(QFont.DemiBold)
        title_label.setFont(title_font)

        color = "#e2e8f0" if self.is_dark_mode else "#1e293b"
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                line-height: 1.3;
                margin-bottom: 6px;
            }}
        """
        )
        layout.addWidget(title_label)

        # News summary/description
        summary_text = news.get("summary", news.get("description", ""))
        if summary_text:
            if len(summary_text) > 120:
                summary_text = summary_text[:120] + "..."

            summary_label = QLabel(summary_text)
            summary_label.setWordWrap(True)

            summary_font = QFont()
            summary_font.setPointSize(9)
            summary_label.setFont(summary_font)

            summary_color = "#94a3b8" if self.is_dark_mode else "#64748b"
            summary_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {summary_color};
                    line-height: 1.4;
                    font-weight: 400;
                }}
            """
            )
            layout.addWidget(summary_label)

        # Source information
        if "source" in news and news["source"]:
            source_label = QLabel(f"📍 {news['source']}")
            source_color = "#64748b" if self.is_dark_mode else "#94a3b8"
            source_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 8px;
                    color: {source_color};
                    font-weight: 500;
                    margin-top: 4px;
                    font-style: italic;
                }}
            """
            )
            layout.addWidget(source_label)

        return news_frame

    def on_data_error(self, msg):
        QMessageBox.critical(self, "Data Loading Error", f"❌ {msg}")
        self.dashboard_ui.avg_label.setText("❌ Error loading data")
        self.dashboard_ui.search_btn.setEnabled(True)
        self.dashboard_ui.search_btn.setText("🔍 SEARCH")

    # ---------------- Exporting (Background Workers) ---------------- #
    def export_csv(self):
        """Export CSV report in background thread"""
        if self.last_df is None:
            QMessageBox.warning(
                self,
                "No Data",
                "📋 No data available to export. Please load stock data first.",
            )
            return

        # Disable buttons and show progress
        self.reports_ui.export_csv_btn.setEnabled(False)
        self.reports_ui.export_csv_btn.setText("⏳ Exporting...")

        # Start background export
        self.export_worker = ExportWorker(self.last_df, self.last_ticker, "csv")
        self.export_worker.finished.connect(self._on_export_finished)
        self.export_worker.error.connect(self._on_export_error)
        self.export_worker.start()

    def export_pdf(self):
        """Export PDF report in background thread"""
        if self.last_df is None:
            QMessageBox.warning(
                self,
                "No Data",
                "📋 No data available to export. Please load stock data first.",
            )
            return

        # Disable buttons and show progress
        self.reports_ui.export_pdf_btn.setEnabled(False)
        self.reports_ui.export_pdf_btn.setText("⏳ Exporting...")

        # Calculate stats for PDF
        avg_price = self.last_df["Close"].mean()
        min_price = self.last_df["Close"].min()
        max_price = self.last_df["Close"].max()
        total_volume = self.last_df["Volume"].sum()

        # Start background export
        self.export_worker = ExportWorker(
            self.last_df, self.last_ticker, "pdf",
            avg_price, min_price, max_price, total_volume
        )
        self.export_worker.finished.connect(self._on_export_finished)
        self.export_worker.error.connect(self._on_export_error)
        self.export_worker.start()

    def _on_export_finished(self, path, export_type):
        """Handle successful export"""
        # Re-enable buttons
        self.reports_ui.export_csv_btn.setEnabled(True)
        self.reports_ui.export_csv_btn.setText("📊 Export CSV")
        self.reports_ui.export_pdf_btn.setEnabled(True)
        self.reports_ui.export_pdf_btn.setText("📄 Export PDF")

        QMessageBox.information(
            self,
            "Export Successful",
            f"{'📊 CSV' if export_type == 'csv' else '📄 PDF'} exported successfully!\nPath: {path}",
        )

    def _on_export_error(self, error_msg):
        """Handle export error"""
        # Re-enable buttons
        self.reports_ui.export_csv_btn.setEnabled(True)
        self.reports_ui.export_csv_btn.setText("📊 Export CSV")
        self.reports_ui.export_pdf_btn.setEnabled(True)
        self.reports_ui.export_pdf_btn.setText("📄 Export PDF")

        QMessageBox.critical(self, "Export Error", f"❌ Failed to export: {error_msg}")

    # ---------------- Cleanup ---------------- #
    def closeEvent(self, event):
        """Properly cleanup all workers before closing (OPTIMIZED)"""
        print("🛑 Application closing - cleaning up workers...")

        # Stop timers first
        if self._price_update_timer.isActive():
            self._price_update_timer.stop()
        if self._checkbox_debounce_timer.isActive():
            self._checkbox_debounce_timer.stop()

        # List of all workers to clean up
        workers_to_cleanup = [
            (self.live_worker, "live price"),
            (self.news_worker, "news"),
            (self.sentiment_worker, "sentiment"),
            (self.ai_worker, "AI"),
            (self.worker, "data"),
            (self.forecast_worker, "hybrid forecast"),
            (self.ai_report_worker, "AI report"),
        ]

        for worker, name in workers_to_cleanup:
            if worker and worker.isRunning():
                print(f"  Stopping {name} worker...")
                try:
                    # Cancel if hybrid forecast worker
                    if hasattr(worker, 'cancel'):
                        worker.cancel()
                    
                    # Stop if has stop method
                    if hasattr(worker, 'stop'):
                        worker.stop()

                    worker.quit()

                    # Wait for thread to finish
                    if not worker.wait(2000):  # Wait max 2 seconds
                        print(
                            f"  ⚠️ {name} worker didn't stop gracefully, terminating..."
                        )
                        worker.terminate()
                        worker.wait(1000)

                    print(f"  ✓ {name} worker stopped")
                except Exception as e:
                    print(f"  ⚠️ Error stopping {name} worker: {e}")

        # Clean up matplotlib
        try:
            plt.close("all")
            print("  ✓ Matplotlib figures closed")
        except Exception as e:
            print(f"  ⚠️ Error closing matplotlib: {e}")

        # Clean up reports UI if it has cleanup method
        if hasattr(self.reports_ui, "cleanup"):
            try:
                self.reports_ui.cleanup()
                print("  ✓ Reports UI cleaned up")
            except Exception as e:
                print(f"  ⚠️ Error cleaning reports UI: {e}")

        print("✅ All workers cleaned up successfully")
        event.accept()


# ---------------- Run App ---------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("StockDash Professional")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("StockDash Analytics")

    # Create and show main window
    window = StockDashboard()
    window.show()

    # Center the window on screen
    screen = app.primaryScreen().geometry()
    window_geometry = window.frameGeometry()
    window_geometry.moveCenter(screen.center())
    window.move(window_geometry.topLeft())

    sys.exit(app.exec_())
