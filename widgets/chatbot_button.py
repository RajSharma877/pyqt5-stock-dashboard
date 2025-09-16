# widgets/chatbot_button.py

from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont
import math

class ChatbotButton(QPushButton):
    """Animated floating chatbot button"""
    
    clicked_with_animation = pyqtSignal()
    
    def __init__(self, is_dark_mode=True):
        super().__init__()
        self.is_dark_mode = is_dark_mode
        self.pulse_phase = 0
        self.is_pulsing = True
        
        self.setup_button()
        self.setup_animations()
        self.start_pulse_animation()
    
    def setup_button(self):
        """Setup the button appearance"""
        self.setFixedSize(60, 60)
        self.setText("🤖")
        self.setObjectName("chatbot_button")
        
        # Font setup
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
        
        # Connect click
        self.clicked.connect(self.on_click)
        
        self.apply_style()
    
    def setup_animations(self):
        """Setup button animations"""
        # Click animation
        self.click_animation = QPropertyAnimation(self, b"geometry")
        self.click_animation.setDuration(150)
        self.click_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        # Pulse timer
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.update_pulse)
        self.pulse_timer.start(50)  # 20 FPS
    
    def start_pulse_animation(self):
        """Start the subtle pulse animation"""
        self.is_pulsing = True
    
    def stop_pulse_animation(self):
        """Stop the pulse animation"""
        self.is_pulsing = False
    
    def update_pulse(self):
        """Update pulse animation phase"""
        if self.is_pulsing:
            self.pulse_phase += 0.1
            if self.pulse_phase > 2 * math.pi:
                self.pulse_phase = 0
            self.update()
    
    def on_click(self):
        """Handle button click with animation"""
        # Stop pulse during click
        self.stop_pulse_animation()
        
        # Animate click (scale down then up)
        original_geometry = self.geometry()
        smaller_geometry = original_geometry.adjusted(3, 3, -3, -3)
        
        self.click_animation.setStartValue(original_geometry)
        self.click_animation.setEndValue(smaller_geometry)
        self.click_animation.finished.connect(self.bounce_back)
        self.click_animation.start()
    
    def bounce_back(self):
        """Bounce back animation"""
        original_geometry = self.geometry().adjusted(-3, -3, 3, 3)
        current_geometry = self.geometry()
        
        self.click_animation.finished.disconnect()
        self.click_animation.setStartValue(current_geometry)
        self.click_animation.setEndValue(original_geometry)
        self.click_animation.finished.connect(self.emit_clicked_signal)
        self.click_animation.start()
    
    def emit_clicked_signal(self):
        """Emit the custom clicked signal and restart pulse"""
        self.click_animation.finished.disconnect()
        self.start_pulse_animation()
        self.clicked_with_animation.emit()
    
    def paintEvent(self, event):
        """Custom paint event for pulse effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate pulse scale (subtle effect)
        pulse_scale = 1.0
        if self.is_pulsing:
            pulse_intensity = 0.05 * (1 + math.sin(self.pulse_phase))
            pulse_scale = 1.0 + pulse_intensity
        
        # Draw pulsing background circle
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = (min(self.width(), self.height()) // 2 - 4) * pulse_scale
        
        # Background circle
        if self.is_dark_mode:
            gradient_color = QColor(59, 130, 246)  # Blue
            bg_color = QColor(30, 41, 59)
        else:
            gradient_color = QColor(59, 130, 246)  # Blue
            bg_color = QColor(248, 250, 252)
        
        # Draw gradient background
        painter.setBrush(QBrush(gradient_color))
        painter.setPen(QPen(gradient_color.lighter(120), 2))
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), 
                           int(2 * radius), int(2 * radius))
        
        # Call parent paint event for text
        super().paintEvent(event)
    
    def set_theme(self, is_dark: bool):
        """Update theme"""
        self.is_dark_mode = is_dark
        self.apply_style()
        self.update()
    
    def apply_style(self):
        """Apply theme-based styling"""
        if self.is_dark_mode:
            style = """
            QPushButton#chatbot_button {
                background: qradial-gradient(circle, #3b82f6, #2563eb);
                border: 3px solid #1e40af;
                border-radius: 30px;
                color: white;
                font-weight: bold;
            }
            
            QPushButton#chatbot_button:hover {
                background: qradial-gradient(circle, #2563eb, #1d4ed8);
                border: 3px solid #1e3a8a;
                transform: scale(1.05);
            }
            
            QPushButton#chatbot_button:pressed {
                background: qradial-gradient(circle, #1d4ed8, #1e40af);
                border: 3px solid #1e3a8a;
            }
            """
        else:
            style = """
            QPushButton#chatbot_button {
                background: qradial-gradient(circle, #3b82f6, #2563eb);
                border: 3px solid #1e40af;
                border-radius: 30px;
                color: white;
                font-weight: bold;
            }
            
            QPushButton#chatbot_button:hover {
                background: qradial-gradient(circle, #2563eb, #1d4ed8);
                border: 3px solid #1e3a8a;
                transform: scale(1.05);
            }
            
            QPushButton#chatbot_button:pressed {
                background: qradial-gradient(circle, #1d4ed8, #1e40af);
                border: 3px solid #1e3a8a;
            }
            """
        
        self.setStyleSheet(style)