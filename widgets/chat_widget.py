# widgets/chat_widget.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect, QApplication, QGridLayout
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor, QPainter, QPen, QPixmap, QIcon
import uuid
import time
import speech_recognition as sr
import pyttsx3

# class TTSThread(QThread):
#     finished = pyqtSignal()

#     def __init__(self, text: str,start_pos: int = 0, parent=None):
#         super().__init__(parent)
#         self.text = text
#         self.start_pos = start_pos
#         self.engine = pyttsx3.init()
#         self.engine.setProperty("rate", 165)
#         self.engine.setProperty("volume", 0.9)
#         self._stopped = False
#         self._current_pos = start_pos

#     def run(self):
#         try:
#             self.engine.connect('started-word', self.track_pos)
#             self._stopped = False
#             self.engine.say(self.text[self.start_pos:])
#             self.engine.runAndWait()
#         except Exception as e:
#             print("TTS error:", e)
#         self.finished.emit()

#     def track_pos(self, name, location, length):
#         self._current_pos = self.start_pos + location
#         if self._stopped:
#             self.engine.stop()

#     def stop(self):
#         """Force stop speech mid-sentence"""
#         self._stopped = True
#         self.engine.stop()

#     def get_current_pos(self):
#         return self._current_pos

class StatusIndicator(QWidget):
    """Online status indicator"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(8, 8)  # Smaller size to match image
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(34, 197, 94))  # Green
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 8, 8)


class QuickActionButton(QPushButton):
    """Quick action button widget"""
    
    def __init__(self, icon: str, text: str):
        super().__init__()
        self.icon_text = icon
        self.button_text = text
        self.setup_ui()
        
    def setup_ui(self):
        """Setup button UI"""
        self.setObjectName("quick_action_btn")
        self.setText(f"{self.icon_text} {self.button_text}")
        self.setFixedHeight(40)  # Slightly taller
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        font = QFont()
        font.setPointSize(20)      # 14px size
        font.setWeight(QFont.Medium)  # Medium weight
        self.setFont(font)

class ChatBubble(QFrame):
    """Individual chat bubble widget"""
    
    def __init__(self, message: str, is_user: bool = True, timestamp: str = None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or time.strftime("%H:%M")
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """Setup the bubble UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        # Message text
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Font setup
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Medium if self.is_user else QFont.Normal)
        self.message_label.setFont(font)
        
        layout.addWidget(self.message_label)
        
        # Timestamp
        timestamp_label = QLabel(self.timestamp)
        timestamp_label.setAlignment(Qt.AlignRight if self.is_user else Qt.AlignLeft)
        font_small = QFont()
        font_small.setPointSize(8)
        timestamp_label.setFont(font_small)
        timestamp_label.setObjectName("timestamp_label")
        
        layout.addWidget(timestamp_label)
        
    def setup_style(self):
        """Apply styling based on user/ai message"""
        if self.is_user:
            self.setObjectName("user_bubble")
        else:
            self.setObjectName("ai_bubble")

class TypingIndicator(QWidget):
    """Animated typing indicator"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(50)
        self.dots = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_dots)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        
        # AI avatar
        avatar_label = QLabel("🤖")
        avatar_label.setFixedSize(24, 24)
        avatar_label.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("AI is thinking")
        font = QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setObjectName("typing_label")
        
        layout.addWidget(avatar_label)
        layout.addWidget(self.label)
        layout.addStretch()
        
    def start_animation(self):
        """Start the typing animation"""
        self.timer.start(600)
        self.show()
        
    def stop_animation(self):
        """Stop the typing animation"""
        self.timer.stop()
        self.hide()
        
    def animate_dots(self):
        """Animate the dots"""
        self.dots = (self.dots + 1) % 4
        dots_text = "." * self.dots
        self.label.setText(f"AI is thinking{dots_text}")

class ChatWidget(QWidget):
    """Main chat widget with modern UI design"""
    
    # Signals
    user_message_sent = pyqtSignal(str, str)  # message, request_id
    chat_closed = pyqtSignal()
    quick_action_clicked = pyqtSignal(str)  # action_type
    
    def __init__(self, is_dark_mode=True):
        super().__init__()
        self.is_dark_mode = is_dark_mode
        self.request_counter = 0
        # self.tts_state = "idle"
        # self.tts_thread = None
        # self.last_response = ""
        # self.resume_pos = 0
        
        self.setup_ui()
        self.setup_animations()
        self.apply_styles()
        
    def setup_ui(self):
        """Setup the main chat UI"""
        self.setFixedSize(420, 950)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Quick actions - moved up with less spacing
        quick_actions = self.create_quick_actions()
        main_layout.addWidget(quick_actions)
        
        # Chat area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chat_scroll.setObjectName("chat_scroll_area")
        
        # Chat container
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(16)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        
        # Typing indicator
        self.typing_indicator = TypingIndicator()
        self.typing_indicator.hide()
        self.chat_layout.addWidget(self.typing_indicator)
        
        self.chat_scroll.setWidget(self.chat_container)
        main_layout.addWidget(self.chat_scroll, 1)
        
        # Input area
        input_area = self.create_input_area()
        main_layout.addWidget(input_area)
        
        # Add welcome message
        self.add_welcome_message()
        
    def create_header(self) -> QWidget:
        """Create the modern chat header with better positioning"""
        header = QFrame()
        header.setObjectName("chat_header")
        header.setFixedHeight(100)  # Slightly reduced height
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)  # Adjusted margins
        
        # AI Avatar and info
        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)
        
        # Avatar
        avatar_label = QLabel("🤖")
        avatar_label.setFixedSize(32, 32)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setObjectName("avatar_label")
        
        # Title and status container
        title_container = QFrame()
        title_container.setObjectName("title_container")
        title_container.setMinimumHeight(60)
        title_layout = QVBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignTop)
        title_layout.setSpacing(12)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        ai_title = "AI Stock Advisor"
        title = QLabel(ai_title)
        title.setFixedHeight(30)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setObjectName("header_title")
        
        # Status with indicator
        status_container = QWidget()
        status_container.setObjectName("status_container")
        status_container.setFixedHeight(35)
        status_layout = QHBoxLayout(status_container)
        status_layout.setSpacing(6)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        status_indicator = StatusIndicator()
        ai_status_label = "Online - Ready to help"
        status_label = QLabel(ai_status_label)
        status_font = QFont()
        status_font.setPointSize(9)
        status_label.setFont(status_font)
        status_label.setObjectName("status_label")
        
        status_layout.addWidget(status_indicator)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        title_layout.addWidget(title)
        title_layout.addWidget(status_container)
        
        info_layout.addWidget(avatar_label)
        info_layout.addWidget(title_container)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Close button - repositioned
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("chat_close_btn")
        self.close_btn.setFixedSize(28, 28)  # Slightly smaller
        self.close_btn.clicked.connect(self.close_chat)

        # self.speaker_btn = QPushButton("🔊")
        # self.speaker_btn.setObjectName("chat_speaker_btn")
        # self.speaker_btn.setFixedSize(28, 28)
        # self.speaker_btn.setCheckable(True)   # toggle style
        # self.speaker_btn.setToolTip("Read responses aloud")
        # self.speaker_btn.clicked.connect(self.toggle_tts)
        
        layout.addWidget(self.close_btn)
        # layout.addWidget(self.speaker_btn)
        
        return header
    
    # def toggle_tts(self):
    #     if self.tts_state == "speaking":
    #         # Pause
    #         if self.tts_thread and self.tts_thread.isRunning():
    #             self.resume_pos = self.tts_thread.get_current_pos()
    #             self.tts_thread.stop()
    #         self.tts_state = "paused"
    #         self.speaker_btn.setText("▶️")

    #     elif self.tts_state == "paused":
    #         # Resume
    #         if self.last_response:
    #             self.start_tts(self.last_response, pos=self.resume_pos)
    #             self.tts_state = "speaking"
    #             self.speaker_btn.setText("⏸")

    #     elif self.tts_state == "idle":
    #         # Start fresh
    #         if self.last_response:
    #             self.resume_pos = 0
    #             self.start_tts(self.last_response)
    #             self.tts_state = "speaking"
    #             self.speaker_btn.setText("⏸")

    # def on_tts_finished(self):
    #     if self.tts_state != "paused":  # if not paused manually
    #         self.tts_state = "idle"
    #         self.speaker_btn.setText("🔊")


    def create_quick_actions(self) -> QWidget:
        """Create the quick actions section with proper spacing"""
        actions_frame = QFrame()
        actions_frame.setObjectName("quick_actions_frame")
        actions_frame.setFixedHeight(250)  # Taller to avoid crowding
        
        layout = QVBoxLayout(actions_frame)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.setSpacing(12)
        
        # Section title
        title_label = QLabel("💡 Quick Actions:")
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setWeight(QFont.Medium)
        title_label.setFont(title_font)
        title_label.setObjectName("quick_actions_title")
        
        layout.addWidget(title_label)
        
        # Grid for buttons
        buttons_widget = QWidget()
        buttons_widget.setMinimumWidth(70)
        buttons_layout = QGridLayout(buttons_widget)
        buttons_layout.setVerticalSpacing(16)
        buttons_layout.setHorizontalSpacing(20)
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        
        # Quick actions (4 actions)
        actions = [
            ("📊", "Analyze AAPL"),
            ("🔍", "Explain MACD"),
            ("📈", "Buy/Sell Signal"),
            ("💭", "Market Sentiment"),
        ]
        
        # Arrange in 3 columns
        
        for i, (icon, text) in enumerate(actions):
            btn = QuickActionButton(icon, text)
            btn.clicked.connect(lambda checked, action=text: self.handle_quick_action(action))           
            cols = 2
            row = i // cols
            col = i % cols
            buttons_layout.addWidget(btn, row, col)
        
        layout.addWidget(buttons_widget)
        
        return actions_frame

    
    def create_input_area(self) -> QWidget:
        """Create the centered message input area"""
        input_frame = QFrame()
        input_frame.setObjectName("chat_input_frame")
        input_frame.setFixedHeight(80)  # Reduced height
        
        layout = QVBoxLayout(input_frame)
        layout.setContentsMargins(20, 0, 20, 16)
        layout.setSpacing(0)
        layout.addStretch()
        
        # Center the input row vertically
        layout.addStretch()
        
        # Input row - centered
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)  # Reduced spacing
        input_layout.setAlignment(Qt.AlignCenter)
        
        # Voice button (left)
        self.voice_btn = QPushButton("🎤")
        self.voice_btn.setObjectName("chat_voice_btn")
        self.voice_btn.setFixedSize(40, 40)  # Square button
        self.voice_btn.setToolTip("Click to speak")
        self.voice_btn.clicked.connect(self.start_voice_input)
        
        # Message input (center - takes most space)
        self.message_input = QLineEdit()
        self.message_input.setObjectName("chat_message_input")
        self.message_input.setPlaceholderText("Ask about stocks, indicators, or market")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setFixedHeight(40)
        
        # Send button (right)
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("chat_send_btn")
        self.send_btn.setFixedSize(60, 40)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.voice_btn)
        input_layout.addWidget(self.message_input, 1)  # Expand to fill
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        layout.addStretch()
        
        return input_frame
    
    def start_voice_input(self):
        """Capture voice, update mic button style, and auto-send recognized text"""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.set_mic_listening(True)

            QApplication.processEvents()

            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio)

                self.message_input.setText(text)

                # Auto-send the recognized message
                # self.speaker_btn.setChecked(True)
                QTimer.singleShot(200, self.send_message)

            except sr.WaitTimeoutError:
                self.message_input.setText("")
                print("No speech detected.")
            except sr.UnknownValueError:
                self.message_input.setText("")
                print("Could not understand audio.")
            except sr.RequestError as e:
                print("Speech recognition error:", e)

        self.set_mic_listening(False)


    def set_mic_listening(self, listening: bool):
        """Toggle mic button style for recording state"""
        if listening:
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                }
            """)
            self.voice_btn.setText("⏺")  # Recording indicator
        else:
            self.voice_btn.setStyleSheet("")
            self.voice_btn.setText("🎤")  # Reset back to mic



    def handle_quick_action(self, action: str):
        """Handle quick action button clicks"""
        action_messages = {
            "Analyze AAPL": "Can you analyze AAPL stock for me?",
            "Explain MACD": "What is MACD and how do I use it?",
            "Buy/Sell Signal": "What are the current buy/sell signals?",
            "Market Sentiment": "What's the current market sentiment?",
            "Trading Strategy": "Can you suggest a trading strategy?",
            "RSI Explained": "Explain RSI indicator in simple terms"
        }
        
        message = action_messages.get(action, action)
        self.message_input.setText(message)
        self.send_message()
    
    def setup_animations(self):
        """Setup entrance/exit animations"""
        # Slide-in animation
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(350)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(250)
        
    def show_animated(self, parent_rect: QRect):
        """Show the chat widget with animation"""
        # Position at bottom right of parent
        chat_x = parent_rect.right() - self.width() - 20
        chat_y = parent_rect.bottom() - self.height() - 20
        
        # Start position (off-screen)
        start_y = parent_rect.bottom() + 50
        self.setGeometry(chat_x, start_y, self.width(), self.height())
        
        # Animate to final position
        self.slide_animation.setStartValue(QRect(chat_x, start_y, self.width(), self.height()))
        self.slide_animation.setEndValue(QRect(chat_x, chat_y, self.width(), self.height()))
        
        self.show()
        self.slide_animation.start()
        self.message_input.setFocus()
        
    def close_chat(self):
        """Close the chat with animation"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.finished.connect(self.chat_closed.emit)
        self.fade_animation.start()
    
    def add_welcome_message(self):
        """Add initial welcome message"""
        welcome_text = ("Hi! I'm your AI stock advisor. 📊\n\n"
                       "I can help you with:\n"
                       "• Stock analysis and recommendations\n"
                       "• Technical indicator explanations\n"
                       "• Market sentiment analysis\n"
                       "• Trading strategies\n\n"
                       "What would you like to know?")
        
        bubble = ChatBubble(welcome_text, is_user=False)
        self.add_message_bubble(bubble)
    
    def send_message(self):
        """Send user message"""
        message = self.message_input.text().strip()
        if not message:
            return
            
        # Clear input
        self.message_input.clear()
        
        # Add user bubble
        user_bubble = ChatBubble(message, is_user=True)
        self.add_message_bubble(user_bubble)
        
        # Show typing indicator
        self.typing_indicator.start_animation()
        self.scroll_to_bottom()
        
        # Generate request ID and emit signal
        self.request_counter += 1
        request_id = f"req_{self.request_counter}_{uuid.uuid4().hex[:8]}"
        self.user_message_sent.emit(message, request_id)
        
        # Disable input while processing
        self.message_input.setEnabled(False)
        self.send_btn.setEnabled(False)
    
    def add_ai_response(self, response: str, request_id: str):
        """Add AI response bubble"""
        # Hide typing indicator
        self.typing_indicator.stop_animation()
        ai_bubble = ChatBubble(response, is_user=False)
        self.add_message_bubble(ai_bubble)

        self.last_response = response
        self.resume_pos = 0

        # if self.speaker_btn.isChecked():
        #     self.start_tts(response)

        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.message_input.setFocus()

    # Functions for start pause and resume voice 
    # def start_tts(self, text, pos=0):
    #     if self.tts_thread and self.tts_thread.isRunning():
    #         self.tts_thread.stop()
    #         self.tts_thread.wait()

    #     sub_text = text[pos:]
    #     self.tts_thread = TTSThread(sub_text, start_pos=pos, parent=self)
    #     self.tts_thread.finished.connect(self.on_tts_finished)

    #     self.tts_state = "speaking"
    #     self.speaker_btn.setText("⏸")
    #     self.tts_thread.start()
        
    def add_error_message(self, error: str, request_id: str):
        """Add error message"""
        # Hide typing indicator
        self.typing_indicator.stop_animation()
        
        error_text = f"Sorry, I encountered an error: {error}\n\nPlease try again or check your AI model configuration."
        error_bubble = ChatBubble(error_text, is_user=False)
        self.add_message_bubble(error_bubble)
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.message_input.setFocus()
    
    def add_message_bubble(self, bubble: ChatBubble):
        """Add a message bubble to the chat"""
        # Remove typing indicator temporarily
        self.chat_layout.removeWidget(self.typing_indicator)
        
        # Add bubble with proper alignment
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        if bubble.is_user:
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble, 0)
        else:
            bubble_layout.addWidget(bubble, 0)
            bubble_layout.addStretch()
            
        self.chat_layout.addWidget(bubble_container)
        
        # Re-add typing indicator at the end
        self.chat_layout.addWidget(self.typing_indicator)
        
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        QTimer.singleShot(50, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()))
    
    def set_theme(self, is_dark: bool):
        """Update theme"""
        self.is_dark_mode = is_dark
        self.apply_styles()
        
    def apply_styles(self):
        """Apply theme-based styles"""
        if self.is_dark_mode:
            self.setStyleSheet(self.get_dark_styles())
        else:
            self.setStyleSheet(self.get_light_styles())
    
    def get_dark_styles(self) -> str:
        """Dark mode styles matching the reference image"""
        return """
        QWidget {
            background-color: #1e1b4b;
            color: #f1f5f9;
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }
        
        QFrame#chat_header {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
            border: none;
            border-radius: 16px 16px 0px 0px;
        }

        QFrame#title_container {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
                padding: 6px;
                border: none;
        }

        QWidget#status_container {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
            border: none;    
        }
        
        QLabel#header_title {
            color: white;
            font-weight: bold;
            border: none;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
            
        }
        
        QLabel#status_label {
            color: rgba(255, 255, 255, 0.9);
            border: none;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
        }
        
        QLabel#avatar_label {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            font-size: 16px;
            border: none;
        }
        
        QPushButton#chat_close_btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 14px;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }
        
        QPushButton#chat_close_btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        QFrame#quick_actions_frame {
            background: #312e81;
            border: none;
        }
        
        QLabel#quick_actions_title {
            color: #e2e8f0;
            background: transparent;
        }
        
        QPushButton#quick_action_btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            color: #f1f5f9;
            padding: 10px 16px;
            text-align: left;
            font-size: 10px;
            font-weight: 500;
        }
        
        QPushButton#quick_action_btn:hover {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }
        
        QPushButton#quick_action_btn:pressed {
            background: rgba(59, 130, 246, 0.3);
            transform: translateY(0px);
        }
        
        QScrollArea#chat_scroll_area {
            border: none;
            background: #1e1b4b;
        }
        
        QFrame#chat_input_frame {
            background: #312e81;
            border: none;
            border-radius: 0px 0px 16px 16px;
        }
        
        QLineEdit#chat_message_input {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 11px;
            color: #f1f5f9;
        }
        
        QLineEdit#chat_message_input:focus {
            border: 2px solid #3b82f6;
            background: rgba(255, 255, 255, 0.15);
        }
        
        QPushButton#chat_send_btn {
            background: #3b82f6;
            border: none;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            font-size: 11px;
        }
        
        QPushButton#chat_send_btn:hover {
            background: #2563eb;
        }
        
        QPushButton#chat_send_btn:disabled {
            background: #6b7280;
        }
        
        QPushButton#chat_voice_btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            font-size: 16px;
            color: rgba(255, 255, 255, 0.7);
        }
        
        QPushButton#chat_voice_btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        QFrame#user_bubble {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #3b82f6, stop: 1 #2563eb);
            border-radius: 20px 20px 6px 20px;
            color: white;
            max-width: 280px;
            margin: 4px;
        }
        
        QFrame#ai_bubble {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px 20px 20px 6px;
            color: #f1f5f9;
            max-width: 280px;
            margin: 4px;
        }
        
        QLabel#timestamp_label {
            color: rgba(241, 245, 249, 0.7);
            font-size: 8px;
            background: transparent;
        }
        
        QLabel#typing_label {
            color: rgba(241, 245, 249, 0.8);
            background: transparent;
        }
        
        QScrollBar:vertical {
            background: rgba(255, 255, 255, 0.05);
            width: 4px;
            border-radius: 2px;
        }
        
        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 2px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        """
    
    def get_light_styles(self) -> str:
        """Light mode styles matching the reference image"""
        return """
        QWidget {
            background-color: #ffffff;
            color: #1f2937;
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }
        
        QFrame#chat_header {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
            border: none;
            border-radius: 16px 16px 0px 0px;
        }
        
        QFrame#title_container {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
                    padding: 6px;
            border: none;
        }
        
        QWidget#status_container {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
            border: none;    
        }
        QLabel#header_title {
            color: black;
            font-weight: bold;
            border: none;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
        }
        
        QLabel#status_label {
            color: rgba(255, 255, 255, 0.9);
            border: none;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #3b82f6, stop: 0.5 #8b5cf6, stop: 1 #a855f7);
        }
        
        QLabel#avatar_label {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            font-size: 16px;
            border: none;
        }
        
        QPushButton#chat_close_btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 14px;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }
        
        QPushButton#chat_close_btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        
        QFrame#quick_actions_frame {
            background: #f8fafc;
            border: none;
            border-bottom: 1px solid #e2e8f0;
        }
        
        QLabel#quick_actions_title {
            color: #4b5563;
            background: transparent;
        }
        
        QPushButton#quick_action_btn {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            color: #374151;
            padding: 10px 16px;
            text-align: left;
            font-size: 10px;
            font-weight: 500;
        }
        
        QPushButton#quick_action_btn:hover {
            background: #f9fafb;
            border: 1px solid #d1d5db;
            transform: translateY(-1px);
        }
        
        QPushButton#quick_action_btn:pressed {
            background: #e0e7ff;
            border: 1px solid #3b82f6;
            transform: translateY(0px);
        }
        
        QScrollArea#chat_scroll_area {
            border: none;
            background: #ffffff;
        }
        
        QFrame#chat_input_frame {
            background: #f8fafc;
            border: none;
            border-top: 1px solid #e2e8f0;
            border-radius: 0px 0px 16px 16px;
        }
        
        QLineEdit#chat_message_input {
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 11px;
            color: #1f2937;
        }
        
        QLineEdit#chat_message_input:focus {
            border: 2px solid #3b82f6;
            background: #ffffff;
        }
        
        QPushButton#chat_send_btn {
            background: #3b82f6;
            border: none;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            font-size: 11px;
        }
        
        QPushButton#chat_send_btn:hover {
            background: #2563eb;
        }
        
        QPushButton#chat_send_btn:disabled {
            background: #9ca3af;
        }
        
        QPushButton#chat_voice_btn {
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 20px;
            font-size: 16px;
            color: #6b7280;
        }
        
        QPushButton#chat_voice_btn:hover {
            background: #e5e7eb;
        }
        
        QFrame#user_bubble {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #3b82f6, stop: 1 #2563eb);
            border-radius: 20px 20px 6px 20px;
            color: white;
            max-width: 280px;
            margin: 4px;
        }
        
        QFrame#ai_bubble {
            background: #f3f4f6;
            border: 1px solid #e5e7eb;
            border-radius: 20px 20px 20px 6px;
            color: #374151;
            max-width: 280px;
            margin: 4px;
        }
        
        QLabel#timestamp_label {
            color: #9ca3af;
            font-size: 8px;
            background: transparent;
        }
        
        QLabel#typing_label {
            color: #6b7280;
            background: transparent;
        }
        
        QScrollBar:vertical {
            background: #f1f5f9;
            width: 4px;
            border-radius: 2px;
        }
        
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            border-radius: 2px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #94a3b8;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        """