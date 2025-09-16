from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import QPixmap, QFont, QCursor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import requests
from io import BytesIO


class ImageLoader(QThread):
    """Async image loader to prevent UI blocking"""

    imageLoaded = pyqtSignal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=5)
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    self.imageLoaded.emit(pixmap)
        except Exception as e:
            print(f"Failed to load image: {e}")


class NewsWidget(QFrame):
    def __init__(self, news):
        super().__init__()
        self.news = news
        self.setObjectName("news_item")
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # Enhanced styling for the news widget
        # self.setStyleSheet("""
        #     QFrame#news_item {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        #                                     stop: 0 rgba(255, 255, 255, 0.95),
        #                                     stop: 1 rgba(248, 250, 252, 0.9));
        #         border: 1px solid rgba(59, 130, 246, 0.15);
        #         border-radius: 12px;
        #         padding: 12px;
        #         margin: 6px 2px;
        #         min-height: 100px;
        #     }
        #     QFrame#news_item:hover {
        #         background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        #                                     stop: 0 rgba(59, 130, 246, 0.08),
        #                                     stop: 1 rgba(29, 78, 216, 0.04));
        #         border: 1px solid #3b82f6;
        #         transform: translateY(-2px);
        #     }
        # """)

        self.setStyleSheet(
            """
    QFrame#news_item {
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 14px;
        padding: 16px;
        margin: 8px 4px;
        min-height: 140px;
    }
    QFrame#news_item:hover {
        background: #f9fafb;
        border: 1px solid #3b82f6;
    }
"""
        )

        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(Qt.gray)
        self.setGraphicsEffect(shadow)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)

        # Thumbnail section
        self.setup_thumbnail(main_layout)

        # Text content section
        self.setup_text_content(main_layout)

        # Set size policies for responsive behavior
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

    def setup_thumbnail(self, main_layout):
        """Setup thumbnail image section"""
        if self.news.get("thumbnail"):
            # Thumbnail container
            thumbnail_container = QFrame()
            thumbnail_container.setFixedSize(100, 100)
            thumbnail_container.setFixedSize(100, 100)
            thumbnail_container.setStyleSheet(
                """
                QFrame {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 3px;
                }
            """
            )

            thumbnail_layout = QVBoxLayout(thumbnail_container)
            thumbnail_layout.setContentsMargins(0, 0, 0, 0)

            # Placeholder for image
            self.img_label = QLabel("📷")
            self.img_label.setAlignment(Qt.AlignCenter)
            self.img_label.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    color: #9ca3af;
                    font-size: 24px;
                    border: none;
                }
            """
            )
            thumbnail_layout.addWidget(self.img_label)

            # Load image asynchronously
            self.image_loader = ImageLoader(self.news["thumbnail"])
            self.image_loader.imageLoaded.connect(self.set_thumbnail)
            self.image_loader.start()

            main_layout.addWidget(thumbnail_container, 0)
        else:
            # News icon placeholder if no thumbnail
            icon_label = QLabel("📰")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(60, 60)
            icon_label.setStyleSheet(
                """
                QLabel {
                    font-size: 28px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                                stop: 0 rgba(59, 130, 246, 0.1), 
                                                stop: 1 rgba(29, 78, 216, 0.05));
                    border-radius: 8px;
                    color: #3b82f6;
                }
            """
            )
            main_layout.addWidget(icon_label, 0)

    def setup_text_content(self, main_layout):
        """Setup text content section"""
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)

        # Header with timestamp/publisher
        header_layout = QHBoxLayout()

        # Publisher info
        publisher_text = self.news.get("publisher", "Unknown Source")
        publisher = QLabel(f"📍 {publisher_text}")
        publisher.setStyleSheet(
            """
            QLabel {
                font-size: 10px;
                color: #6b7280;
                font-weight: 600;
                background: rgba(107, 114, 128, 0.1);
                padding: 2px 8px;
                border-radius: 4px;
                margin-bottom: 4px;
            }
        """
        )
        header_layout.addWidget(publisher)
        header_layout.addStretch()

        # Time indicator (if available)
        if "published_date" in self.news or "date" in self.news:
            date_text = self.news.get("published_date", self.news.get("date", ""))
            if date_text:
                time_label = QLabel(f"🕐 {date_text[:10]}")
                time_label.setStyleSheet(
                    """
                    QLabel {
                        font-size: 9px;
                        color: #9ca3af;
                        font-style: italic;
                    }
                """
                )
                header_layout.addWidget(time_label)

        text_layout.addLayout(header_layout)

        # Title with enhanced styling
        title_text = self.news.get("title", "News Update")
        title = QLabel(title_text)
        title.setWordWrap(True)

        # Title font and styling
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setWeight(QFont.DemiBold)
        title.setFont(title_font)

        title.setStyleSheet(
            """
            QLabel {
                color: #1f2937;
                line-height: 1.4;
                margin-bottom: 6px;
                padding: 2px 0px;
            }
        """
        )
        text_layout.addWidget(title)

        # Summary with better formatting
        summary_text = self.news.get("summary", self.news.get("description", ""))
        if summary_text:
            # Limit summary length
            if len(summary_text) > 120:
                summary_text = summary_text[:120] + "..."

            summary = QLabel(summary_text)
            summary.setWordWrap(True)

            summary_font = QFont()
            summary_font.setPointSize(11)
            summary.setFont(summary_font)

            summary.setStyleSheet(
                """
    QLabel {
        color: #374151;
        line-height: 1.6;
        background: rgba(243, 244, 246, 0.5);
        padding: 6px 8px;
        border-radius: 6px;
    }
"""
            )
            text_layout.addWidget(summary)

        # Read more link with enhanced styling
        if self.news.get("link"):
            link = QLabel(
                f'<a href="{self.news["link"]}" style="color: #3b82f6; text-decoration: none; font-weight: 600;">📖 Read full article →</a>'
            )
            link.setOpenExternalLinks(True)
            link.setStyleSheet(
                """
                QLabel {
                    font-size: 11px;
                    padding: 4px 0px;
                }
                QLabel a {
                    color: #3b82f6;
                    text-decoration: none;
                    font-weight: 600;
                }
                QLabel a:hover {
                    color: #2563eb;
                    text-decoration: underline;
                }
            """
            )
            text_layout.addWidget(link)

        # Add stretch to push content to top
        text_layout.addStretch()

        main_layout.addLayout(text_layout, 1)

    def set_thumbnail(self, pixmap):
        """Set the loaded thumbnail image"""
        if hasattr(self, "img_label") and pixmap and not pixmap.isNull():
            # Scale image to fit container while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                82, 82, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled_pixmap)
            self.img_label.setStyleSheet(
                """
                QLabel {
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                }
            """
            )

    def mousePressEvent(self, event):
        """Handle click events on news items"""
        if event.button() == Qt.LeftButton:
            # Add click animation effect
            self.setStyleSheet(
                self.styleSheet()
                + """
                QFrame#news_item {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 rgba(59, 130, 246, 0.15), 
                                                stop: 1 rgba(29, 78, 216, 0.08));
                    border: 2px solid #2563eb;
                }
            """
            )

            # Reset style after short delay
            QTimer.singleShot(150, self.reset_style)

            # Optional: Open link directly on click
            if self.news.get("link"):
                import webbrowser

                try:
                    webbrowser.open(self.news["link"])
                except:
                    pass

        super().mousePressEvent(event)

    def reset_style(self):
        """Reset the widget style after click animation"""
        self.setStyleSheet(
            """
            QFrame#news_item {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(255, 255, 255, 0.95), 
                                            stop: 1 rgba(248, 250, 252, 0.9));
                border: 1px solid rgba(59, 130, 246, 0.15);
                border-radius: 12px;
                padding: 12px;
                margin: 6px 2px;
                min-height: 100px;
            }
            QFrame#news_item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(59, 130, 246, 0.08), 
                                            stop: 1 rgba(29, 78, 216, 0.04));
                border: 1px solid #3b82f6;
            }
        """
        )
