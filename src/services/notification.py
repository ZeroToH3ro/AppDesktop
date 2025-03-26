from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QPainterPath, QFont

class CustomNotification(QWidget):
    def __init__(self, message, icon_type="success", parent=None, auto_close=True, duration=2000):
        super().__init__(parent)
        # Set window flags to create a frameless window that stays on top
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(350)
        
        # Store opacity for animation
        self._opacity = 0.0
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Container for all content with proper styling
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        # Header layout with icon, title and close button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel()
        icon_size = 24
        if icon_type == "success":
            # Create success icon (checkmark)
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#4CAF50"))
            painter.drawEllipse(2, 2, icon_size-4, icon_size-4)
            painter.setPen(QColor("white"))
            painter.setBrush(QColor("white"))
            # Draw checkmark
            painter.drawLine(8, 12, 12, 16)
            painter.drawLine(12, 16, 18, 8)
            painter.end()
            icon_label.setPixmap(pixmap)
        else:
            # Create error icon (X)
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#f44336"))
            painter.drawEllipse(2, 2, icon_size-4, icon_size-4)
            painter.setPen(QColor("white"))
            painter.setBrush(QColor("white"))
            # Draw X
            painter.drawLine(8, 8, 16, 16)
            painter.drawLine(8, 16, 16, 8)
            painter.end()
            icon_label.setPixmap(pixmap)
        
        # Title
        title = "Success" if icon_type == "success" else "Error"
        title_color = "#4CAF50" if icon_type == "success" else "#f44336"
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet(f"color: {title_color}; font-size: 16px; font-weight: bold;")
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #aaaaaa;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
            }
        """)
        close_button.clicked.connect(self.close_with_animation)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        
        # Message
        message_label = QLabel(message)
        message_label.setObjectName("messageLabel")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white; font-size: 14px;")
        
        # Add widgets to content layout
        content_layout.addLayout(header_layout)
        
        # Add separator line
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: rgba(255,255,255,0.1);")
        content_layout.addWidget(separator)
        
        content_layout.addWidget(message_label)
        
        # Add content widget to main layout
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        
        # Style the content widget with rounded corners and border
        border_color = "#4CAF50" if icon_type == "success" else "#f44336"
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: #1e2433;
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
        """)
        
        # Add drop shadow effect
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        # Store parent for positioning
        self.parent_widget = parent
        
        # Setup animations
        self.setupAnimations()
        
        # Auto-close timer
        if auto_close:
            self.close_timer = QTimer(self)
            self.close_timer.timeout.connect(self.close_with_animation)
            self.close_timer.start(duration)
    
    def setupAnimations(self):
        """Setup slide-in and fade animations"""
        # Slide-in animation
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.slide_animation.setDuration(300)
        
        # Fade animation
        self.fade_effect = QGraphicsOpacityEffect(self)
        self.fade_effect.setOpacity(0)
        self.setGraphicsEffect(self.fade_effect)
        
        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
    
    def showEvent(self, event):
        """Position the notification and start animations when shown"""
        super().showEvent(event)
        self.position_notification()
        self.start_show_animation()
    
    def start_show_animation(self):
        """Start the show animation (slide in and fade in)"""
        # Get current position
        current_pos = self.pos()
        
        # Setup slide animation from right
        start_pos = QPoint(current_pos.x() + 50, current_pos.y())
        self.move(start_pos)
        
        self.slide_animation.setStartValue(start_pos)
        self.slide_animation.setEndValue(current_pos)
        self.slide_animation.start()
        
        # Setup fade in animation
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
    
    def close_with_animation(self):
        """Close with fade out animation"""
        # Setup fade out animation
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
    
    def position_notification(self):
        """Position the notification in the top-right corner"""
        # Get screen geometry
        screen_geometry = QApplication.desktop().availableGeometry()
        
        if self.parent_widget and not self.parent_widget.isHidden():
            # If parent exists and is visible, position relative to parent
            parent_geo = self.parent_widget.geometry()
            x = parent_geo.x() + parent_geo.width() - self.width() - 20
            y = parent_geo.y() + 40
        else:
            # Otherwise position relative to screen
            x = screen_geometry.width() - self.width() - 20
            y = 40
        
        self.move(x, y)
    
    def closeEvent(self, event):
        """Handle notification close event"""
        super().closeEvent(event)

class NotificationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.active_notifications = []
    
    def close_all_notifications(self):
        """Close all active notifications"""
        for notification in self.active_notifications[:]:  # Create a copy of the list
            if notification and not notification.isHidden():
                notification.close_with_animation()
        self.active_notifications = []

    def show_success(self, message, parent=None, duration=2000):
        """Show success message with auto-close after duration (ms)"""
        # Close any existing notifications to avoid stacking
        self.close_all_notifications()
        
        # Create and show the notification
        notification = CustomNotification(
            message=message,
            icon_type="success",
            parent=parent,
            auto_close=True,
            duration=duration
        )
        
        # Show and raise to ensure visibility
        notification.show()
        notification.raise_()
        
        # Add to active notifications list
        self.active_notifications.append(notification)
        
        # Return the notification object
        return notification

    def show_error(self, message, parent=None):
        """Show error message with close button"""
        # Close any existing notifications to avoid stacking
        self.close_all_notifications()
        
        # Create and show the notification
        notification = CustomNotification(
            message=message,
            icon_type="error",
            parent=parent,
            auto_close=False
        )
        
        # Show and raise to ensure visibility
        notification.show()
        notification.raise_()
        
        # Add to active notifications list
        self.active_notifications.append(notification)
        
        # Return the notification object
        return notification

# Create a singleton instance
notification = NotificationService()
