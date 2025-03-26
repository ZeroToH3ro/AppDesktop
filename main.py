import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QDialog, QFormLayout, QLineEdit, QMessageBox, QLabel,
    QFrame, QHeaderView, QSizePolicy, QComboBox, QDateEdit, QTextEdit,
    QToolButton, QFileDialog, QSpinBox, QMenu, QAction, QCheckBox, QInputDialog
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QDate, QSize, QPropertyAnimation, QSortFilterProxyModel, QPoint
from PyQt5.QtGui import QColor, QPalette, QFont, QPixmap, QPainter, QPen, QIcon
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from src.services.translator import Translator
from src.services.notification import NotificationService
import csv
import os

# Ensure Qt uses the right platform plugin
os.environ['QT_QPA_PLATFORM'] = 'cocoa'

Base = declarative_base()
translator = Translator()
notification = NotificationService()

class Engineer(Base):
    __tablename__ = 'engineers'
    id = Column(Integer, primary_key=True)
    person_name = Column(String)
    birth_date = Column(Date)  
    address = Column(String)
    associated_company = Column(String)
    currency_unit = Column(String, default='백만원')
    technical_grades = Column(String)  
    position_title = Column(String)
    expertise_area = Column(String)
    qualifications = relationship("Qualification", back_populates="engineer", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="engineer", cascade="all, delete-orphan")
    employment = relationship("Employment", back_populates="engineer", cascade="all, delete-orphan")
    training = relationship("Training", back_populates="engineer", cascade="all, delete-orphan")

class Qualification(Base):
    __tablename__ = 'qualifications'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    title = Column(String)
    acquisition_date = Column(String)
    registration_number = Column(String)
    engineer = relationship("Engineer", back_populates="qualifications")

class Education(Base):
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    graduation_date = Column(String)
    institution = Column(String)
    major = Column(String)
    degree = Column(String)
    engineer = relationship("Engineer", back_populates="education")

class Employment(Base):
    __tablename__ = 'employment'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    period = Column(String)
    company = Column(String)
    engineer = relationship("Engineer", back_populates="employment")

class Training(Base):
    __tablename__ = 'training'
    id = Column(Integer, primary_key=True)
    engineer_id = Column(Integer, ForeignKey('engineers.id'))
    period = Column(String)
    course_name = Column(String)
    institution = Column(String)
    certificate_number = Column(String)
    engineer = relationship("Engineer", back_populates="training")

# Database initialization
engine = create_engine('sqlite:///engineer_db.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class EngineerModel(QAbstractTableModel):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.engineers = []
        self.filtered_engineers = []
        self.filter_text = ""
        self.page_size = 10
        self.current_page = 0
        self.selected_rows = set()
        self.headers = ["ID", "Name", "Birth Date", "Address", "Company", "Technical Grade"]
        self.load_data()

    def load_data(self):
        self.engineers = self.session.query(Engineer).all()
        self.apply_filter()
        
    def apply_filter(self, filter_text=""):
        self.filter_text = filter_text.lower()
        if not self.filter_text:
            self.filtered_engineers = self.engineers.copy()
        else:
            self.filtered_engineers = [
                engineer for engineer in self.engineers
                if (self.filter_text in str(engineer.id).lower() or
                    self.filter_text in (engineer.person_name or "").lower() or
                    self.filter_text in (engineer.address or "").lower() or
                    self.filter_text in (engineer.associated_company or "").lower() or
                    (engineer.technical_grades and 
                     self.filter_text in str(engineer.technical_grades).lower()))
            ]
        self.current_page = 0
        self.selected_rows.clear()
        self.layoutChanged.emit()
        
    def set_page(self, page):
        if page >= 0 and page <= self.page_count() - 1:
            self.current_page = page
            self.layoutChanged.emit()
            
    def set_page_size(self, size):
        self.page_size = size
        self.current_page = 0
        self.layoutChanged.emit()
            
    def page_count(self):
        if not self.filtered_engineers:
            return 1
        return max(1, (len(self.filtered_engineers) + self.page_size - 1) // self.page_size)
    
    def get_visible_engineers(self):
        start = self.current_page * self.page_size
        end = min(start + self.page_size, len(self.filtered_engineers))
        if start >= len(self.filtered_engineers):
            return []
        return self.filtered_engineers[start:end]

    def rowCount(self, parent=None):
        return min(self.page_size, len(self.get_visible_engineers()))

    def columnCount(self, parent=None):
        return 6

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            engineers = self.get_visible_engineers()
            if not engineers or index.row() >= len(engineers):
                return None
                
            engineer = engineers[index.row()]
            if index.column() == 0:
                return str(engineer.id)
            elif index.column() == 1:
                return engineer.person_name
            elif index.column() == 2:
                return engineer.birth_date
            elif index.column() == 3:
                return engineer.address
            elif index.column() == 4:
                return engineer.associated_company
            elif index.column() == 5:
                return engineer.technical_grades
        
        if role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                return QColor("#1e2433")
            else:
                return QColor("#262b40")
                
        if role == Qt.TextAlignmentRole:
            if index.column() == 0:  # ID column
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        if role == Qt.CheckStateRole and index.column() == 0:
            if index.row() in self.selected_rows:
                return Qt.Checked
            return Qt.Unchecked

        return None
        
    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and index.column() == 0:
            if value == Qt.Checked:
                self.selected_rows.add(index.row())
            else:
                self.selected_rows.discard(index.row())
            self.dataChanged.emit(index, index)
            return True
        return False
        
    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
        
    def get_selected_engineers(self):
        """Return list of selected engineers"""
        engineers = self.get_visible_engineers()
        return [engineers[row] for row in self.selected_rows if row < len(engineers)]

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

class EngineerDialog(QDialog):
    def __init__(self, session, engineer=None):
        super().__init__()
        self.session = session
        self.engineer = engineer
        self.setWindowTitle(translator.translations['en']['basic_info'])
        self.setMinimumWidth(600)
        layout = QFormLayout()

        # Basic Information
        self.name_input = QLineEdit()
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setDisplayFormat("yyyy-MM-dd")
        self.birth_date_input.setCalendarPopup(True)  # Enable calendar popup
        self.birth_date_input.setDate(QDate.currentDate())  # Set default to current date
        self.address_input = QLineEdit()
        self.company_input = QLineEdit()
        
        # Technical Grades
        self.grade_input = QComboBox()
        self.grade_input.addItems(['Junior', 'Intermediate', 'Senior', 'Expert'])
        
        if engineer:
            self.name_input.setText(engineer.person_name)
            if engineer.birth_date:
                try:
                    date = QDate.fromString(engineer.birth_date, "yyyy-MM-dd")
                    self.birth_date_input.setDate(date)
                except:
                    self.birth_date_input.setDate(QDate.currentDate())
            self.address_input.setText(engineer.address)
            self.company_input.setText(engineer.associated_company)
        
        layout.addRow(translator.translations['en']['name'] + ":", self.name_input)
        layout.addRow(translator.translations['en']['birth_date'] + ":", self.birth_date_input)
        layout.addRow("Address:", self.address_input)
        layout.addRow("Company:", self.company_input)
        layout.addRow("Technical Grade:", self.grade_input)
        
        save_button = QPushButton(translator.translations['en']['save'])
        save_button.clicked.connect(self.save_engineer)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

    def save_engineer(self):
        name = self.name_input.text()
        birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")
        address = self.address_input.text()
        company = self.company_input.text()
        grade = self.grade_input.currentText()
        
        if not name or not birth_date:
            notification.show_error("Name and birth date are required!", self)
            return
        
        try:
            if self.engineer:
                self.engineer.person_name = name
                self.engineer.birth_date = birth_date
                self.engineer.address = address
                self.engineer.associated_company = company
                self.engineer.technical_grades = grade
                message = f"Engineer {name} updated successfully"
            else:
                new_engineer = Engineer(
                    person_name=name,
                    birth_date=birth_date,
                    address=address,
                    associated_company=company,
                    technical_grades=grade
                )
                self.session.add(new_engineer)
                message = f"Engineer {name} added successfully"
            
            self.session.commit()
            notification.show_success(message, self)
            self.accept()
        except Exception as e:
            notification.show_error(f"Error saving engineer: {str(e)}", self)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(translator.translations['en']['app_title'])
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e2433;
            }
            QTableView {
                background-color: #1e2433;
                border: none;
                gridline-color: #373b69;
            }
            QTableView::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #373b69;
                color: white;
                padding: 10px;
                border: 1px solid #4a4d7c;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                color: white;
            }
        """)
        
        self.session = Session()
        self.sidebar_expanded = True
        self.sidebar_width = 250
        self.sidebar_collapsed_width = 70
        
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #171c2c;
            }
        """)
        self.sidebar.setFixedWidth(self.sidebar_width)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Header with toggle button and title
        sidebar_header = QWidget()
        sidebar_header.setFixedHeight(60)
        sidebar_header.setStyleSheet("background-color: #1a203a;")
        header_layout = QHBoxLayout(sidebar_header)
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        # Toggle button
        self.toggle_button = SidebarToggleButton()
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        
        # App title
        title_label = QLabel(translator.translations['en']['app_title'])
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        header_layout.addWidget(self.toggle_button)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        sidebar_layout.addWidget(sidebar_header)
        
        # User profile section
        profile_widget = QWidget()
        profile_widget.setFixedHeight(150)
        profile_widget.setStyleSheet("background-color: #171c2c;")
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setAlignment(Qt.AlignCenter)
        
        # Profile picture (circle)
        profile_pic = QLabel()
        profile_pic.setFixedSize(80, 80)
        profile_pic.setStyleSheet("""
            background-color: #2d325a;
            border-radius: 40px;
        """)
        profile_pic.setAlignment(Qt.AlignCenter)
        
        # Create a user icon
        user_pixmap = QPixmap(60, 60)
        user_pixmap.fill(Qt.transparent)
        painter = QPainter(user_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        # Draw head
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#4fd1c5"))
        painter.drawEllipse(20, 5, 20, 20)
        # Draw body
        painter.drawEllipse(10, 30, 40, 30)
        painter.end()
        
        profile_pic.setPixmap(user_pixmap)
        
        # User name
        user_name = QLabel("Engineer Admin")
        user_name.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        # User role
        user_role = QLabel("Administrator")
        user_role.setStyleSheet("color: #4fd1c5; font-size: 14px;")
        
        profile_layout.addWidget(profile_pic, 0, Qt.AlignCenter)
        profile_layout.addWidget(user_name, 0, Qt.AlignCenter)
        profile_layout.addWidget(user_role, 0, Qt.AlignCenter)
        
        sidebar_layout.addWidget(profile_widget)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #2d325a;")
        sidebar_layout.addWidget(separator)
        
        # Navigation section
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(5)
        
        # Create navigation buttons with icons
        self.nav_buttons = []
        
        # Dashboard button
        dashboard_btn = SidebarButton(translator.translations['en']['engineer_list'])
        dashboard_icon = QPixmap(22, 22)
        dashboard_icon.fill(Qt.transparent)
        painter = QPainter(dashboard_icon)
        painter.setPen(QPen(QColor("#a0a0a0"), 1.5))
        painter.drawRect(4, 4, 14, 8)
        painter.drawRect(4, 14, 14, 4)
        painter.end()
        dashboard_btn.setIcon(QIcon(dashboard_icon))
        dashboard_btn.setChecked(True)
        self.nav_buttons.append(dashboard_btn)
        
        # Basic info button
        basic_info_btn = SidebarButton(translator.translations['en']['basic_info'])
        info_icon = QPixmap(22, 22)
        info_icon.fill(Qt.transparent)
        painter = QPainter(info_icon)
        painter.setPen(QPen(QColor("#a0a0a0"), 1.5))
        painter.drawEllipse(6, 6, 10, 10)
        painter.drawLine(11, 18, 11, 20)
        painter.end()
        basic_info_btn.setIcon(QIcon(info_icon))
        self.nav_buttons.append(basic_info_btn)
        
        # Qualifications button
        qualifications_btn = SidebarButton(translator.translations['en']['qualifications'])
        qual_icon = QPixmap(22, 22)
        qual_icon.fill(Qt.transparent)
        painter = QPainter(qual_icon)
        painter.setPen(QPen(QColor("#a0a0a0"), 1.5))
        painter.drawRect(4, 4, 14, 14)
        painter.drawLine(8, 10, 14, 10)
        painter.drawLine(8, 14, 14, 14)
        painter.end()
        qualifications_btn.setIcon(QIcon(qual_icon))
        self.nav_buttons.append(qualifications_btn)
        
        # Education button
        education_btn = SidebarButton(translator.translations['en']['education'])
        edu_icon = QPixmap(22, 22)
        edu_icon.fill(Qt.transparent)
        painter = QPainter(edu_icon)
        painter.setPen(QPen(QColor("#a0a0a0"), 1.5))
        painter.drawRect(4, 8, 14, 10)
        painter.drawLine(4, 8, 11, 3)
        painter.drawLine(18, 8, 11, 3)
        painter.end()
        education_btn.setIcon(QIcon(edu_icon))
        self.nav_buttons.append(education_btn)
        
        # Experience button
        experience_btn = SidebarButton(translator.translations['en']['experience'])
        exp_icon = QPixmap(22, 22)
        exp_icon.fill(Qt.transparent)
        painter = QPainter(exp_icon)
        painter.setPen(QPen(QColor("#a0a0a0"), 1.5))
        painter.drawRect(4, 6, 14, 12)
        painter.drawLine(7, 10, 15, 10)
        painter.drawLine(7, 14, 15, 14)
        painter.end()
        experience_btn.setIcon(QIcon(exp_icon))
        self.nav_buttons.append(experience_btn)
        
        # Training button
        training_btn = SidebarButton(translator.translations['en']['training'])
        train_icon = QPixmap(22, 22)
        train_icon.fill(Qt.transparent)
        painter = QPainter(train_icon)
        painter.setPen(QPen(QColor("#a0a0a0"), 1.5))
        painter.drawEllipse(4, 6, 10, 10)
        painter.drawLine(14, 11, 18, 11)
        painter.drawLine(16, 9, 18, 11)
        painter.drawLine(16, 13, 18, 11)
        painter.end()
        training_btn.setIcon(QIcon(train_icon))
        self.nav_buttons.append(training_btn)
        
        # Add buttons to layout
        for btn in self.nav_buttons:
            nav_layout.addWidget(btn)
            btn.clicked.connect(self.on_nav_button_clicked)
        
        nav_layout.addStretch()
        
        sidebar_layout.addWidget(nav_widget)
        
        # Bottom buttons (Logout and Quit)
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(10, 10, 10, 20)
        bottom_layout.setSpacing(15)  # Increased spacing between buttons
        
        # Add a separator before bottom buttons
        bottom_separator = QFrame()
        bottom_separator.setFrameShape(QFrame.HLine)
        bottom_separator.setFixedHeight(1)
        bottom_separator.setStyleSheet("background-color: #2d325a;")
        bottom_layout.addWidget(bottom_separator)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_icon = QPixmap(16, 16)
        logout_icon.fill(Qt.transparent)
        painter = QPainter(logout_icon)
        painter.setPen(QPen(QColor("white"), 1.5))
        painter.drawLine(4, 8, 12, 8)
        painter.drawLine(8, 4, 12, 8)
        painter.drawLine(8, 12, 12, 8)
        painter.end()
        logout_btn.setIcon(QIcon(logout_icon))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a0a0a0;
                text-align: left;
                padding: 8px 16px;
                border: 1px solid #2d325a;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2d325a;
                color: white;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        
        # Quit button
        quit_btn = QPushButton("Quit")
        quit_icon = QPixmap(16, 16)
        quit_icon.fill(Qt.transparent)
        painter = QPainter(quit_icon)
        painter.setPen(QPen(QColor("white"), 1.5))
        painter.drawLine(4, 4, 12, 12)
        painter.drawLine(4, 12, 12, 4)
        painter.end()
        quit_btn.setIcon(QIcon(quit_icon))
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a0a0a0;
                text-align: left;
                padding: 8px 16px;
                border: 1px solid #2d325a;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f44336;
                color: white;
            }
        """)
        quit_btn.clicked.connect(self.quit_app)
        
        bottom_layout.addWidget(logout_btn)
        bottom_layout.addWidget(quit_btn)
        
        sidebar_layout.addWidget(bottom_widget)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)  # Added margins
        
        # Create a container for table and search
        table_container = QVBoxLayout()
        table_container.setSpacing(10)
        
        # Create a header container for search and export button
        table_header = QHBoxLayout()
        
        # Search bar container - positioned above the table
        search_container = QWidget()
        search_container.setFixedWidth(300)
        search_container.setFixedHeight(36)
        search_container.setStyleSheet("""
            QWidget {
                background-color: #2d325a;
                border-radius: 18px;
                padding: 0 10px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 0, 10, 0)
        
        # Search icon
        search_icon = QLabel()
        search_icon.setFixedSize(16, 16)
        # Create search icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor("#a0a0a0"), 1.5))
        painter.drawEllipse(4, 4, 8, 8)
        painter.drawLine(11, 11, 15, 15)
        painter.end()
        search_icon.setPixmap(pixmap)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: white;
            }
        """)
        self.search_input.textChanged.connect(self.search_engineers)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        
        # Export to CSV button
        export_button = QPushButton("Export CSV")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
        """)
        export_button.clicked.connect(self.export_to_csv)
        
        # Add search and export button to the table header
        table_header.addWidget(search_container, 0, Qt.AlignLeft)
        table_header.addStretch()
        table_header.addWidget(export_button, 0, Qt.AlignRight)
        
        # Add the header and table to the container
        table_container.addLayout(table_header)
        
        # Table view for engineers
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setShowGrid(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setSectionsClickable(True)
        self.table_view.horizontalHeader().sectionClicked.connect(self.header_clicked)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        self.table_view.setStyleSheet("""
            QTableView {
                alternate-background-color: #262b40;
                gridline-color: #373b69;
            }
            QTableView::item:selected {
                background-color: #373b69;
            }
            QHeaderView::section {
                background-color: #373b69;
                color: white;
                padding: 8px;
                border: 1px solid #4a4d7c;
                font-weight: bold;
            }
        """)
        
        table_container.addWidget(self.table_view)
        
        # Set up the model and proxy model for sorting
        self.model = EngineerModel(self.session)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)
        
        # Action buttons container (moved above pagination)
        action_container = QWidget()
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 10, 0, 10)
        action_layout.setSpacing(15)  # Added spacing between buttons
        
        # Add button
        add_button = QPushButton(translator.translations['en']['add'])
        add_button.clicked.connect(self.add_engineer)
        action_layout.addWidget(add_button)
        
        # Edit button
        edit_button = QPushButton(translator.translations['en']['edit'])
        edit_button.clicked.connect(self.edit_engineer)
        action_layout.addWidget(edit_button)
        
        # Delete button
        delete_button = QPushButton(translator.translations['en']['delete'])
        delete_button.clicked.connect(self.delete_engineer)
        action_layout.addWidget(delete_button)
        
        action_layout.addStretch()
        
        table_container.addWidget(action_container)
        
        # Pagination controls
        pagination_container = QWidget()
        pagination_layout = QHBoxLayout(pagination_container)
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        
        # Rows per page selector
        rows_label = QLabel("Rows per page:")
        rows_label.setStyleSheet("color: white;")
        pagination_layout.addWidget(rows_label)
        
        self.page_size_selector = QComboBox()
        self.page_size_selector.addItems(["10", "25", "50", "100"])
        self.page_size_selector.setStyleSheet("""
            QComboBox {
                background-color: #373b69;
                color: white;
                border: none;
                padding: 5px;
                min-width: 70px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #4a4d7c;
                border-left-style: solid;
            }
        """)
        self.page_size_selector.currentTextChanged.connect(self.change_page_size)
        pagination_layout.addWidget(self.page_size_selector)
        
        pagination_layout.addStretch()
        
        # Page display
        self.page_display = QLabel("1-10 of 0")
        self.page_display.setStyleSheet("color: white;")
        pagination_layout.addWidget(self.page_display)
        
        # Navigation buttons
        self.prev_button = QPushButton()
        self.prev_button.setIcon(self.create_arrow_icon("left"))
        self.prev_button.setFixedSize(32, 32)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
            QPushButton:disabled {
                background-color: transparent;
                opacity: 0.5;
            }
        """)
        self.prev_button.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton()
        self.next_button.setIcon(self.create_arrow_icon("right"))
        self.next_button.setFixedSize(32, 32)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
            QPushButton:disabled {
                background-color: transparent;
                opacity: 0.5;
            }
        """)
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)
        
        table_container.addWidget(pagination_container)
        
        # Add layouts to content layout
        content_layout.addLayout(table_container)
        
        # Add layouts to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(content_layout)
        
        self.central_widget.setLayout(main_layout)

    def create_arrow_icon(self, direction):
        """Create an arrow icon for pagination"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor("white"), 2))
        
        if direction == "left":
            # Draw left arrow
            painter.drawLine(12, 3, 4, 8)
            painter.drawLine(4, 8, 12, 13)
        else:
            # Draw right arrow
            painter.drawLine(4, 3, 12, 8)
            painter.drawLine(12, 8, 4, 13)
            
        painter.end()
        return QIcon(pixmap)
        
    def update_pagination_display(self):
        """Update the pagination display text"""
        total = len(self.model.filtered_engineers)
        if total == 0:
            self.page_display.setText("0-0 of 0")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
            
        page_size = self.model.page_size
        current_page = self.model.current_page
        start = current_page * page_size + 1
        end = min(start + page_size - 1, total)
        
        self.page_display.setText(f"{start}-{end} of {total}")
        
        # Enable/disable navigation buttons
        self.prev_button.setEnabled(current_page > 0)
        self.next_button.setEnabled(current_page < self.model.page_count() - 1)
        
    def previous_page(self):
        """Go to the previous page"""
        if self.model.current_page > 0:
            self.model.set_page(self.model.current_page - 1)
            self.update_pagination_display()
            
    def next_page(self):
        """Go to the next page"""
        if self.model.current_page < self.model.page_count() - 1:
            self.model.set_page(self.model.current_page + 1)
            self.update_pagination_display()
            
    def change_page_size(self, size_text):
        """Change the number of rows per page"""
        try:
            size = int(size_text)
            self.model.set_page_size(size)
            self.update_pagination_display()
        except ValueError:
            pass
            
    def search_engineers(self):
        """Search engineers based on input text"""
        search_text = self.search_input.text()
        self.model.apply_filter(search_text)
        self.update_pagination_display()
        
        if search_text and self.model.rowCount(None) == 0:
            notification.show_error(f"No engineers found matching '{search_text}'", self)

    def add_engineer(self):
        dialog = EngineerDialog(self.session)
        if dialog.exec_():
            self.model.load_data()
            notification.show_success("Engineer added successfully", self)

    def edit_engineer(self):
        """Edit selected engineer"""
        # Check if we have engineers selected by checkboxes
        selected_engineers = self.model.get_selected_engineers()
        
        if selected_engineers:
            if len(selected_engineers) > 1:
                notification.show_error("Please select only one engineer to edit", self)
                return
            engineer = selected_engineers[0]
        else:
            # Fall back to the old selection method
            index = self.table_view.selectionModel().currentIndex()
            if not index.isValid():
                notification.show_error("Please select an engineer to edit!", self)
                return
            # Map proxy index to source index
            source_index = self.proxy_model.mapToSource(index)
            engineer = self.model.get_visible_engineers()[source_index.row()]
        
        dialog = EngineerDialog(self.session, engineer)
        if dialog.exec_():
            self.model.load_data()
            self.update_pagination_display()
            notification.show_success("Engineer updated successfully", self)

    def delete_engineer(self):
        """Delete selected engineer(s)"""
        # Check if we have engineers selected by checkboxes
        selected_engineers = self.model.get_selected_engineers()
        
        if not selected_engineers:
            # Fall back to the old selection method
            index = self.table_view.selectionModel().currentIndex()
            if not index.isValid():
                notification.show_error("Please select an engineer to delete!", self)
                return
            # Map proxy index to source index
            source_index = self.proxy_model.mapToSource(index)
            selected_engineers = [self.model.get_visible_engineers()[source_index.row()]]
            
        if len(selected_engineers) == 1:
            message = "Are you sure you want to delete this engineer?"
        else:
            message = f"Are you sure you want to delete {len(selected_engineers)} engineers?"
            
        if QMessageBox.question(self, "Confirm", message) == QMessageBox.Yes:
            try:
                for engineer in selected_engineers:
                    self.session.delete(engineer)
                
                self.session.commit()
                self.model.load_data()
                self.update_pagination_display()
                
                if len(selected_engineers) == 1:
                    notification.show_success(f"Engineer {selected_engineers[0].person_name} deleted successfully", self)
                else:
                    notification.show_success(f"{len(selected_engineers)} engineers deleted successfully", self)
            except Exception as e:
                notification.show_error(f"Error deleting engineer(s): {str(e)}", self)
    
    def header_clicked(self, section):
        """Handle header click to show sorting menu"""
        menu = QMenu(self)
        
        # Unsort action
        unsort_action = QAction("Unsort", self)
        unsort_action.triggered.connect(lambda: self.sort_table(-1, None))
        menu.addAction(unsort_action)
        
        # Sort ascending action
        asc_action = QAction("Sort by ASC", self)
        asc_action.triggered.connect(lambda: self.sort_table(section, Qt.AscendingOrder))
        menu.addAction(asc_action)
        
        # Sort descending action
        desc_action = QAction("Sort by DESC", self)
        desc_action.triggered.connect(lambda: self.sort_table(section, Qt.DescendingOrder))
        menu.addAction(desc_action)
        
        # Add separator
        menu.addSeparator()
        
        # Filter action
        filter_action = QAction("Filter", self)
        filter_action.triggered.connect(lambda: self.show_filter_dialog(section))
        menu.addAction(filter_action)
        
        # Show columns action
        columns_action = QAction("Show columns", self)
        columns_action.triggered.connect(self.show_columns_dialog)
        menu.addAction(columns_action)
        
        # Hide column action
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(lambda: self.hide_column(section))
        menu.addAction(hide_action)
        
        # Show the menu at cursor position
        header = self.table_view.horizontalHeader()
        menu.exec_(self.table_view.mapToGlobal(header.pos() + QPoint(header.sectionPosition(section), header.height())))
    
    def show_context_menu(self, pos):
        """Show context menu for table cells"""
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return
            
        menu = QMenu(self)
        
        # Edit action
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self.edit_engineer)
        menu.addAction(edit_action)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_engineer)
        menu.addAction(delete_action)
        
        # Show the menu at cursor position
        menu.exec_(self.table_view.viewport().mapToGlobal(pos))
    
    def sort_table(self, column, order):
        """Sort table by column and order"""
        if column == -1 or order is None:
            self.proxy_model.sort(-1)  # Unsort
        else:
            self.proxy_model.sort(column, order)
    
    def hide_column(self, column):
        """Hide specified column"""
        self.table_view.setColumnHidden(column, True)
    
    def show_columns_dialog(self):
        """Show dialog to select visible columns"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Show/Hide Columns")
        dialog.setFixedWidth(300)
        layout = QVBoxLayout(dialog)
        
        checkboxes = []
        for i, header in enumerate(self.model.headers):
            checkbox = QCheckBox(header)
            checkbox.setChecked(not self.table_view.isColumnHidden(i))
            checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        
        if dialog.exec_():
            for i, checkbox in enumerate(checkboxes):
                self.table_view.setColumnHidden(i, not checkbox.isChecked())
    
    def show_filter_dialog(self, column):
        """Show dialog to filter by column value"""
        header = self.model.headers[column]
        text, ok = QInputDialog.getText(self, f"Filter by {header}", f"Enter text to filter by {header}:")
        if ok and text:
            self.search_input.setText(text)
            self.search_engineers()
    
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states"""
        self.sidebar_expanded = not self.sidebar_expanded
        target_width = self.sidebar_width if self.sidebar_expanded else self.sidebar_collapsed_width
        
        # Create animation
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(self.sidebar.width())
        self.animation.setEndValue(target_width)
        self.animation.start()
        
        # Update UI elements based on state
        for btn in self.nav_buttons:
            btn.setText(btn.text() if self.sidebar_expanded else "")
            
    def on_nav_button_clicked(self):
        """Handle navigation button clicks"""
        # Uncheck all buttons
        for btn in self.nav_buttons:
            if btn != self.sender():
                btn.setChecked(False)
                
    def logout(self):
        """Handle logout button click"""
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            notification.show_success("Logged out successfully", self)
            # Here you would implement actual logout functionality
            
    def quit_app(self):
        """Handle quit button click"""
        reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()

    def export_to_csv(self):
        """Export engineer data to CSV file"""
        try:
            # Get file name from save dialog
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_name:
                # If no extension is provided, add .csv
                if not file_name.endswith('.csv'):
                    file_name += '.csv'
                
                # Get all engineers from the model
                engineers = self.model.engineers
                
                # Write to CSV
                with open(file_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    headers = ["ID", "Name", "Birth Date", "Address", "Company", "Technical Grade"]
                    writer.writerow(headers)
                    
                    # Write data
                    for engineer in engineers:
                        row = [
                            engineer.id,
                            engineer.person_name,
                            engineer.birth_date,
                            engineer.address,
                            engineer.associated_company,
                            engineer.technical_grades
                        ]
                        writer.writerow(row)
                
                notification.show_success(f"Data exported to {file_name}", self)
        except Exception as e:
            notification.show_error(f"Error exporting data: {str(e)}", self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())