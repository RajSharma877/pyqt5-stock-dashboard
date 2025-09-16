# main.py

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
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QCursor
from prophet import Prophet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from dotenv import load_dotenv

import sys
import pandas as pd
import os
import matplotlib.pyplot as plt

from workers.ai_worker import AIChatWorker
from ui.ui_main import DashboardUI
from ui.ui_reports import ReportsUI
from widgets.chart_widget import ChartWidget
from widgets.news_widget import NewsWidget
from widgets.chatbot_button import ChatbotButton
from widgets.chat_widget import ChatWidget
from core.data_handler import get_news, get_stock_data, get_fundamentals, get_details
from core.indicators import calculate_sma, calculate_ema
from styles import get_theme


# -------- Worker thread ----------#
class DataWorker(QThread):
    finished = pyqtSignal(object, str, dict, str, list)  # send df + ticker
    error = pyqtSignal(str)

    def __init__(self, ticker, indicators):
        super().__init__()
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

            # Fetching data for fundamentals, details and news in worker thread
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

        # Add pages to stack
        self.stacked_widget.addWidget(self.dashboard_ui)  # index 0
        self.stacked_widget.addWidget(self.reports_ui)  # index 1

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

        # Dashboard signals
        self.dashboard_ui.ticker_input.returnPressed.connect(self.load_data)
        self.dashboard_ui.search_btn.clicked.connect(self.load_data)
        self.dashboard_ui.ma_checkbox.stateChanged.connect(self.load_data)
        self.dashboard_ui.rsi_checkbox.stateChanged.connect(self.load_data)
        self.dashboard_ui.macd_checkbox.stateChanged.connect(self.load_data)
        self.dashboard_ui.bb_checkbox.stateChanged.connect(self.load_data)
        self.dashboard_ui.sr_checkbox.stateChanged.connect(self.load_data)

        # Reports UI part variables
        self.last_df = None
        self.last_ticker = None

        # Reports button actions
        if hasattr(self.reports_ui, "back_btn"):
            self.reports_ui.back_btn.clicked.connect(self.show_dashboard)
        if hasattr(self.reports_ui, "export_csv_btn"):
            self.reports_ui.export_csv_btn.clicked.connect(self.export_csv)
        if hasattr(self.reports_ui, "export_pdf_btn"):
            self.reports_ui.export_pdf_btn.clicked.connect(self.export_pdf)

        # Worker
        self.worker = None

    def handle_user_message(self, message: str, request_id: str):
        """Handle user message and call AI worker"""
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")  # safer with env vars
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
        # Create chatbot button
        self.chatbot_button = ChatbotButton(self.is_dark_mode)
        self.chatbot_button.setParent(self)
        self.chatbot_button.clicked_with_animation.connect(self.toggle_chat)

        # Position chatbot button at bottom right
        self.position_chatbot_button()

        # Create chat widget (initially hidden)
        self.chat_widget = ChatWidget(self.is_dark_mode)
        self.chat_widget.setParent(self)
        self.chat_widget.hide()

        # Connect chat signals
        # self.chat_widget.user_message_sent.connect(self.handle_user_message)
        self.chat_widget.user_message_sent.connect(self.handle_user_message)
        self.chat_widget.chat_closed.connect(self.on_chat_closed)

        # Chat state
        self.chat_visible = False

    def position_chatbot_button(self):
        """Position the chatbot button at bottom right"""
        button_size = 60
        margin = 20

        x = self.width() - button_size - margin
        y = self.height() - button_size - margin - 50  # Account for status bar

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
        # Find the theme button that was created in ui_main.py
        theme_buttons = self.dashboard_ui.findChildren(QPushButton)
        for btn in theme_buttons:
            if btn.objectName() == "theme_button":
                self.theme_btn = btn
                break
        else:
            # Fallback if not found
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
                elif "settings" in btn_text:
                    btn.clicked.connect(self.show_settings_placeholder)

    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_ui)

    def show_reports(self):
        """Switch to reports page and generate report if ticker loaded"""
        if self.last_df is not None:
            try:
                forecast_df = self.forecast_prices(self.last_df)
                self.reports_ui.set_report(self.last_df, self.last_ticker, forecast_df)
            except Exception as e:
                print(f"Error generating forecast: {e}")
        self.stacked_widget.setCurrentWidget(self.reports_ui)

    def show_history_placeholder(self):
        """Placeholder for history functionality"""
        QMessageBox.information(
            self, "Coming Soon", "📊 History feature coming in the next version!"
        )

    def show_settings_placeholder(self):
        """Placeholder for settings functionality"""
        QMessageBox.information(
            self, "Settings", "⚙️ Settings panel will be available in the next update!"
        )

    def apply_theme(self):
        self.setStyleSheet(get_theme(self.is_dark_mode))

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

        # Update chart widget theme too
        self.chart_widget.set_theme(self.is_dark_mode)

        self.reports_ui.set_theme(self.is_dark_mode)
        # Update theme button text
        if hasattr(self, "theme_btn"):
            self.theme_btn.setText("☀️" if self.is_dark_mode else "🌙")

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

        # Enhanced loading state
        self.dashboard_ui.search_btn.setEnabled(False)
        self.dashboard_ui.search_btn.setText("⏳ Loading...")
        self.dashboard_ui.avg_label.setText("⏳ Loading market data...")

        # Start worker
        indicators = []
        if self.dashboard_ui.ma_checkbox.isChecked():
            indicators.append("MA")

        self.worker = DataWorker(ticker, indicators)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.on_data_error)
        self.worker.start()

    def on_data_loaded(self, df, ticker, fundamentals, details, news_list):
        self.last_df = df
        self.last_ticker = ticker

        try:
            avg_close = df["Close"].mean()
            # Enhanced price display with emoji and formatting
            self.dashboard_ui.avg_label.setText(
                f"💰 Average Price: ${avg_close:.2f} | 📊 Total Records: {len(df)}"
            )

            # Chart update
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

            # Enhanced fundamentals display
            if fundamentals:
                fund_items = []
                for k, v in fundamentals.items():
                    # Add icons for different metrics
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

            # Enhanced details display
            # NEW (using modal system)
            if details:
                self.dashboard_ui.set_company_details(f"🏢 {details}")
            else:
                self.dashboard_ui.set_company_details(
                    "🏢 Company details not available"
                )

            # Clear existing news
            while self.dashboard_ui.news_layout.count():
                item = self.dashboard_ui.news_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Enhanced news display
            if news_list:
                for news in news_list:  # Limit to 5 news items
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

            # Re-enable UI
            self.dashboard_ui.search_btn.setEnabled(True)
            self.dashboard_ui.search_btn.setText("🔍 SEARCH")

        except Exception as e:
            self.on_data_error(f"Error processing data: {str(e)}")

    def create_enhanced_news_widget(self, news):
        """Create an enhanced news widget with better styling"""
        news_frame = QFrame()
        news_frame.setObjectName("news_item")
        news_frame.setCursor(QCursor(Qt.PointingHandCursor))
        news_frame.setMinimumHeight(120)

        # Enhanced styling based on current theme
        if self.is_dark_mode:
            news_frame.setStyleSheet(
                """
                QFrame#news_item {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #1e293b, stop: 1 #0f172a);
                    border: 1px solid #334155;
                    border-radius: 12px;
                    padding: 12px;
                    margin: 4px 0px;
                }
                QFrame#news_item:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 rgba(59, 130, 246, 0.1), 
                                                stop: 1 rgba(29, 78, 216, 0.05));
                    border: 1px solid #3b82f6;
                }
            """
            )
        else:
            news_frame.setStyleSheet(
                """
                QFrame#news_item {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.95),
        stop: 1 rgba(248, 250, 252, 0.9));
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 12px;
    padding: 12px;
    margin: 4px 0px;
}

QFrame#news_item:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(219, 234, 254, 0.9),   /* light sky blue */
        stop: 1 rgba(191, 219, 254, 0.8)    /* softer blue at bottom */
    );
    border: 1px solid #3b82f6;
}

            """
            )

        layout = QVBoxLayout(news_frame)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # News header with timestamp
        header_layout = QHBoxLayout()

        # News indicator and timestamp
        if "published" in news and news["published"]:
            time_label = QLabel(f"📅 {news['published'][:10]}")  # Just the date part
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

        # Title styling
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setWeight(QFont.DemiBold)
        title_label.setFont(title_font)
        print(self.is_dark_mode)
        color = "#4a4a4b"
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
            # Limit text length for better UI
            if len(summary_text) > 120:
                summary_text = summary_text[:120] + "..."

            summary_label = QLabel(summary_text)
            summary_label.setWordWrap(True)

            summary_font = QFont()
            summary_font.setPointSize(9)
            summary_label.setFont(summary_font)

            print("Is dark mode: ", self.is_dark_mode)
            summary_color = "#a0a0a0" 

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

        # Source information (if available)
        if "source" in news and news["source"]:
            source_label = QLabel(f"📍 {news['source']}")
            source_color = "#a0a0a0"
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

    # ---------------- Exporting ---------------- #
    def export_csv(self):
        if self.last_df is not None:
            try:
                path = f"reports/{self.last_ticker}_reports.csv"
                os.makedirs("reports", exist_ok=True)
                self.last_df.to_csv(path)
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"📊 CSV exported successfully!\nPath: {path}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", f"❌ Failed to export CSV: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "No Data",
                "📋 No data available to export. Please load stock data first.",
            )

    def export_pdf(self):
        if self.last_df is None:
            QMessageBox.warning(
                self,
                "No Data",
                "📋 No data available to export. Please load stock data first.",
            )
            return

        try:
            os.makedirs("reports", exist_ok=True)
            path = f"reports/{self.last_ticker}_report.pdf"

            # ReportLab setup
            doc = SimpleDocTemplate(path)
            styles = getSampleStyleSheet()
            story = [
                Paragraph(f"📈 Stock Report for {self.last_ticker}", styles["Title"]),
                Spacer(1, 12),
            ]

            # Add stats
            avg_price = self.last_df["Close"].mean()
            min_price = self.last_df["Close"].min()
            max_price = self.last_df["Close"].max()
            total_volume = self.last_df["Volume"].sum()

            story.append(
                Paragraph(f"💰 Average Price: ${avg_price:.2f}", styles["Normal"])
            )
            story.append(
                Paragraph(f"📉 Minimum Price: ${min_price:.2f}", styles["Normal"])
            )
            story.append(
                Paragraph(f"📈 Maximum Price: ${max_price:.2f}", styles["Normal"])
            )
            story.append(
                Paragraph(f"📊 Total Volume: {total_volume:,}", styles["Normal"])
            )
            story.append(Spacer(1, 12))

            # Plot and save graph
            plt.style.use("default")
            fig, ax = plt.subplots(figsize=(8, 4))
            self.last_df["Close"].plot(
                ax=ax, title=f"{self.last_ticker} Closing Prices", color="#3b82f6"
            )
            ax.set_ylabel("Price ($)")
            ax.set_xlabel("Date")
            ax.grid(True, alpha=0.3)

            graph_path = f"reports/{self.last_ticker}_graph.png"
            plt.savefig(graph_path, bbox_inches="tight", dpi=150)
            plt.close(fig)

            # Add graph to PDF
            story.append(Image(graph_path, width=500, height=250))

            # Build PDF
            doc.build(story)
            QMessageBox.information(
                self,
                "Export Successful",
                f"📄 PDF report exported successfully!\nPath: {path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"❌ Failed to export PDF: {str(e)}"
            )

    # ---------------- Forecasting ---------------- #
    def forecast_prices(self, df):
        """Run Prophet forecast for next 30 days"""
        try:
            prophet_df = df.reset_index()[["Date", "Close"]].rename(
                columns={"Date": "ds", "Close": "y"}
            )

            print("Prophet df: ", prophet_df)

            # Suppress Prophet logs
            import logging

            logging.getLogger("prophet").setLevel(logging.WARNING)

            model = Prophet(daily_seasonality=True, yearly_seasonality=True)
            model.fit(prophet_df)

            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)

            forecast_df = forecast.set_index("ds")[
                ["yhat", "yhat_lower", "yhat_upper"]
            ].rename(
                columns={
                    "yhat": "Forecast",
                    "yhat_lower": "Lower_Bound",
                    "yhat_upper": "Upper_Bound",
                }
            )

            print("Forecast df: ", forecast_df)
            return forecast_df

        except Exception as e:
            print(f"Forecasting error: {e}")
            # Return empty forecast if Prophet fails
            return pd.DataFrame()


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
