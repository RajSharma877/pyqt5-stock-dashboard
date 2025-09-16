# ui_main.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFrame,
    QCheckBox,
    QTextEdit,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    QDialog,
    QDialogButtonBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class CompanyDetailsModal(QDialog):
    """Modal dialog for displaying company details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏢 Company Details")
        self.setModal(True)
        self.setFixedSize(800, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("🏢 Company Information")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #3b82f6;
                margin-bottom: 10px;
                padding: 16px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 12px;
                border: 2px solid rgba(59, 130, 246, 0.2);
            }
        """)
        layout.addWidget(header)
        
        # Details text area
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Company details will be displayed here...")
        self.details_text.setStyleSheet("""
            QTextEdit {
                background: #ffffff;
                border: 2px solid rgba(59, 130, 246, 0.2);
                border-radius: 12px;
                padding: 16px;
                font-size: 14px;
                line-height: 1.5;
                color: #1f2937;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
                outline: none;
            }
        """)
        layout.addWidget(self.details_text, 1)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background: #2563eb;
                transform: translateY(-1px);
            }
            QDialogButtonBox QPushButton:pressed {
                background: #1d4ed8;
                transform: translateY(0px);
            }
        """)
        layout.addWidget(button_box)
        
    def set_details(self, details_text):
        """Set the details text in the modal"""
        self.details_text.setPlainText(details_text)

class DashboardUI(QWidget):
    def __init__(self):
        super().__init__()

        self.company_details_modal = CompanyDetailsModal(self)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ======== LEFT SIDEBAR ========
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setSpacing(8)
        sidebar.setContentsMargins(20, 30, 20, 30)
        
        # Dashboard Title in Sidebar
        title_label = QLabel("📈 StockDash")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 800;
                color: #3b82f6;
                margin-bottom: 20px;
                padding: 10px;
                border-radius: 8px;
                background: rgba(59, 130, 246, 0.1);
            }
        """)
        sidebar.addWidget(title_label)
        
        menu_items = [
            ("🏠 Dashboard", "dashboard"),
            ("📊 History", "history"),
            ("📋 Reports", "reports"),
            ("⚙️ Settings", "settings"),
        ]
        
        for item_text, item_id in menu_items:
            btn = QPushButton(item_text)
            btn.setObjectName("nav_button")
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            
            # Set font for nav buttons
            font = QFont()
            font.setPointSize(17)
            font.setWeight(QFont.DemiBold)
            btn.setFont(font)
            
            sidebar.addWidget(btn)
        
        # Add flexible space
        sidebar.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # ======== CENTER AREA ========
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(16, 16, 16, 16)
        center_layout.setSpacing(10)
        
        # Top search bar with enhanced styling
        top_bar_widget = QWidget()
        top_bar_widget.setObjectName("top_bar")
        top_bar = QHBoxLayout(top_bar_widget)
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(16)
        
        # Search input with enhanced styling
        self.ticker_input = QLineEdit()
        self.ticker_input.setObjectName("ticker_input")
        self.ticker_input.setPlaceholderText("Enter stock symbol (e.g., AAPL, MSFT, GOOGL)")
        self.ticker_input.setFixedHeight(52)
        
        # Search button with enhanced styling
        self.search_btn = QPushButton("🔍 SEARCH")
        self.search_btn.setObjectName("search_button")
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setFixedHeight(52)
        self.search_btn.setFixedWidth(140)
        
        # Theme toggle button
        theme_btn = QPushButton("🌙/☀️")
        theme_btn.setObjectName("theme_button")
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setFixedHeight(52)
        theme_btn.setFixedWidth(80)
        
        top_bar.addWidget(self.ticker_input, 3)
        top_bar.addWidget(self.search_btn, 0)
        top_bar.addWidget(theme_btn, 0)
        
        # Chart area with enhanced frame
        self.chart_frame = QFrame()
        self.chart_frame.setObjectName("chart_frame")
        self.chart_frame.setFrameShape(QFrame.NoFrame)
        self.chart_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chart_frame.setMinimumHeight(600)
        
        # Average price label with enhanced styling
        self.avg_label = QLabel("💰 Average Closing Price: Ready to analyze...")
        self.avg_label.setObjectName("avg_price")
        self.avg_label.setAlignment(Qt.AlignCenter)
        
        # Details section with header
        self.details_button = QPushButton("🏢 Company Details - Click to View")
        self.details_button.setObjectName("details_button")
        self.details_button.setCursor(Qt.PointingHandCursor)
        self.details_button.setFixedHeight(60)
        self.details_button.clicked.connect(self.show_company_details_modal)

        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.DemiBold)
        self.details_button.setFont(font)
        
        self.details_button.setStyleSheet("""
            QPushButton#details_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.1),
                    stop:1 rgba(99, 102, 241, 0.1));
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                padding: 16px;
                color: #3b82f6;
                text-align: left;
                font-weight: 600;
            }
            QPushButton#details_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.15),
                    stop:1 rgba(99, 102, 241, 0.15));
                border: 2px solid rgba(59, 130, 246, 0.5);
                transform: translateY(-2px);
            }
            QPushButton#details_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.2),
                    stop:1 rgba(99, 102, 241, 0.2));
                border: 2px solid rgba(59, 130, 246, 0.7);
                transform: translateY(0px);
            }
        """)
        
        # Add widgets to center layout
        center_layout.addWidget(top_bar_widget)
        center_layout.addWidget(self.chart_frame, 1)
        center_layout.addWidget(self.avg_label)
        center_layout.addWidget(self.details_button)
        
        # ======== RIGHT PANEL ========
        right_widget = QWidget()
        right_widget.setObjectName("right_panel")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(16)
        
        # Indicators Section
        indicators_header = QLabel("📈 Technical Indicators")
        indicators_header.setObjectName("section_header")
        right_layout.addWidget(indicators_header)
        
        # Create indicators frame for better organization
        indicators_frame = QFrame()
        indicators_frame.setStyleSheet("""
            QFrame {
                background: rgba(59, 130, 246, 0.05);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 12px;
                padding: 16px;
                margin: 4px;
            }
        """)
        indicators_layout = QVBoxLayout(indicators_frame)
        indicators_layout.setSpacing(8)
        
        self.ma_checkbox = QCheckBox("📊 Moving Averages (SMA/EMA)")
        self.rsi_checkbox = QCheckBox("⚡ RSI - Relative Strength Index")
        self.macd_checkbox = QCheckBox("🔄 MACD - Moving Average Convergence")
        self.bb_checkbox = QCheckBox("📏 Bollinger Bands")
        self.sr_checkbox = QCheckBox("🎯 Support/Resistance Levels")
        
        # Style checkboxes
        checkboxes = [self.ma_checkbox, self.rsi_checkbox, self.macd_checkbox, 
                     self.bb_checkbox, self.sr_checkbox]
        
        for checkbox in checkboxes:
            checkbox.setCursor(Qt.PointingHandCursor)
            font = QFont()
            font.setPointSize(12)
            font.setWeight(QFont.Medium)
            checkbox.setFont(font)
            indicators_layout.addWidget(checkbox)
        
        right_layout.addWidget(indicators_frame)
        
        # Fundamentals Section
        fundamentals_header = QLabel("💼 Fundamentals")
        fundamentals_header.setObjectName("section_header")
        right_layout.addWidget(fundamentals_header)
        
        self.fundamentals_text = QTextEdit()
        self.fundamentals_text.setObjectName("fundamentals")
        self.fundamentals_text.setReadOnly(True)
        self.fundamentals_text.setMaximumHeight(180)
        self.fundamentals_text.setPlaceholderText("Financial metrics and ratios will appear here...")
        right_layout.addWidget(self.fundamentals_text)
        
        # News Section
        news_header = QLabel("📰 Latest News")
        news_header.setObjectName("section_header")
        right_layout.addWidget(news_header)
        
        # News scroll area with enhanced styling
        self.news_scroll = QScrollArea()
        self.news_scroll.setWidgetResizable(True)
        self.news_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.news_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.news_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 12px;
                min-height: 150px;
            }
        """)
        
        # Inner container for news items
        self.news_container = QWidget()
        self.news_layout = QVBoxLayout(self.news_container)
        self.news_layout.setAlignment(Qt.AlignTop)
        self.news_layout.setSpacing(8)
        self.news_layout.setContentsMargins(8, 8, 8, 8)
        
        # Add placeholder news item
        placeholder_news = QLabel("📊 Search for a stock to see latest news...")
        placeholder_news.setAlignment(Qt.AlignCenter)
        placeholder_news.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-style: italic;
                padding: 20px;
                background: rgba(100, 116, 139, 0.1);
                border-radius: 8px;
                margin: 4px;
            }
        """)
        self.news_layout.addWidget(placeholder_news)
        
        self.news_scroll.setWidget(self.news_container)
        right_layout.addWidget(self.news_scroll, 1)
        
        # Add flexible space at bottom of right panel
        right_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # ======== ADD ALL SECTIONS TO MAIN LAYOUT ========
        main_layout.addWidget(sidebar_widget, 0)  # Fixed width sidebar
        main_layout.addWidget(center_widget, 1)   # Expandable center
        main_layout.addWidget(right_widget, 0)    # Fixed width right panel
        
        # Set size policies for better responsive behavior
        sidebar_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        center_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        self.setLayout(main_layout)


    def show_company_details_modal(self):
        """Show the company details modal dialog"""
        self.company_details_modal.show()
        self.company_details_modal.raise_()
        self.company_details_modal.activateWindow()
    
    def set_company_details(self, details_text):
        """Set company details text in the modal"""
        self.company_details_modal.set_details(details_text)
        # Update button text to indicate data is available
        self.details_button.setText("🏢 Company Details - Click to View (Data Available)")
    
    def clear_company_details(self):
        """Clear company details and reset button text"""
        self.company_details_modal.set_details("")
        self.details_button.setText("🏢 Company Details - Click to View")