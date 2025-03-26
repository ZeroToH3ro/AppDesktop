from PyQt5.QtWidgets import QPushButton, QLineEdit, QToolButton
from PyQt5.QtCore import QSize, QPropertyAnimation, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QColor

class SidebarButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(50)
        self.setIconSize(QSize(22, 22))
        
        if icon_path:
            self.setIcon(QIcon(icon_path))
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a0a0a0;
                text-align: left;
                padding-left: 20px;
                border: none;
                font-size: 14px;
                border-radius: 0;
            }
            QPushButton:hover {
                background-color: #2d325a;
                color: white;
            }
            QPushButton:checked {
                background-color: #2d325a;
                color: #4fd1c5;
                border-left: 3px solid #4fd1c5;
            }
        """)
        self.setCheckable(True)

class SidebarToggleButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: white;
                border: none;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        
        # Create hamburger icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor("white"), 2))
        # Draw three lines
        painter.drawLine(8, 10, 24, 10)
        painter.drawLine(8, 16, 24, 16)
        painter.drawLine(8, 22, 24, 22)
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(24, 24))

class SearchInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Search...")
        self.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: white;
            }
        """)
