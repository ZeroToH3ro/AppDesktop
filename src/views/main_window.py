from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLabel, QComboBox, QMenu, QAction, QDialog,
    QCheckBox, QMessageBox, QInputDialog, QFileDialog, QHeaderView,
    QListWidget, QListWidgetItem, QFrame, QSizePolicy, QLineEdit
)
from PyQt5.QtCore import Qt, QPoint, QSortFilterProxyModel
from PyQt5.QtGui import QColor, QPainter, QPen, QIcon, QPixmap

from src.models.table_models import EngineerTableModel
from src.views.components import SidebarButton, SearchInput
from src.views.dialogs import EngineerDialog
from src.services.notification import notification
from src.services.translator import translator
import csv

class MainWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.sidebar_expanded = True
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(translator.translate('app_title'))
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1d2d;
            }
            QWidget {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d325a;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #3d426a;
            }
            QLineEdit {
                background-color: #2d325a;
                border: 1px solid #4a4d7c;
                padding: 8px;
                border-radius: 4px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #6a6d9c;
            }
        """)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize sidebar first
        self.setup_sidebar()
        
        # Add sidebar to layout
        main_layout.addWidget(self.sidebar)
        
        # Create content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section with title
        header_container = QHBoxLayout()
        title_label = QLabel(translator.translate('engineer_list'))
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        header_container.addWidget(title_label)
        header_container.addStretch()
        
        # Search and export container
        search_container = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.search_engineers)
        self.search_input.setFixedWidth(300)
        search_container.addWidget(self.search_input)
        
        search_container.addStretch()
        
        # Export button
        export_button = QPushButton("Export CSV")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #0077ee;
            }
        """)
        export_button.clicked.connect(self.export_to_csv)
        search_container.addWidget(export_button)
        
        content_layout.addLayout(header_container)
        content_layout.addLayout(search_container)
        
        # Table container
        table_container = QVBoxLayout()
        
        # Action buttons
        action_buttons = QHBoxLayout()
        add_button = QPushButton(translator.translate('add'))
        edit_button = QPushButton(translator.translate('edit'))
        delete_button = QPushButton(translator.translate('delete'))
        
        for btn in [add_button, edit_button, delete_button]:
            btn.setMinimumWidth(100)
            action_buttons.addWidget(btn)
        action_buttons.addStretch()
        
        add_button.clicked.connect(self.add_engineer)
        edit_button.clicked.connect(self.edit_engineer)
        delete_button.clicked.connect(self.delete_engineer)
        
        table_container.addLayout(action_buttons)
        
        # Setup table
        self.setup_table(table_container)
        
        # Add layouts to content layout
        content_layout.addLayout(table_container)
        
        # Add layouts to main layout
        main_layout.addWidget(content_widget)
        
        self.central_widget.setLayout(main_layout)
        
    def setup_sidebar(self):
        # Create sidebar widget
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Add user profile section
        profile_container = QWidget()
        profile_container.setStyleSheet('background-color: #1a1d3a; padding: 20px;')
        profile_layout = QVBoxLayout(profile_container)
        
        # Profile image
        profile_image = QLabel()
        profile_pixmap = QPixmap(32, 32)
        profile_pixmap.fill(Qt.transparent)
        painter = QPainter(profile_pixmap)
        painter.setPen(QPen(QColor("#4fd1c5")))
        painter.setBrush(QColor("#4fd1c5"))
        painter.drawEllipse(0, 0, 32, 32)
        painter.end()
        profile_image.setPixmap(profile_pixmap)
        profile_layout.addWidget(profile_image, alignment=Qt.AlignCenter)
        
        # Profile text
        profile_name = QLabel('Engineer Admin')
        profile_name.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        profile_role = QLabel('Administrator')
        profile_role.setStyleSheet('color: #4fd1c5; font-size: 14px;')
        
        profile_layout.addWidget(profile_name, alignment=Qt.AlignCenter)
        profile_layout.addWidget(profile_role, alignment=Qt.AlignCenter)
        
        sidebar_layout.addWidget(profile_container)
        
        # Navigation menu
        nav_menu = QListWidget()
        nav_menu.setStyleSheet("""
            QListWidget {
                background-color: #1a1d3a;
                border: none;
                color: #a0a0a0;
            }
            QListWidget::item {
                padding: 15px 20px;
                border-left: 3px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #2d325a;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #2d325a;
                color: #4fd1c5;
                border-left: 3px solid #4fd1c5;
            }
        """)
        
        menu_items = [
            ('Engineer List', True),
            ('Basic Information', False),
            ('Qualifications', False),
            ('Education', False),
            ('Experience', False),
            ('Training', False)
        ]
        
        for item_text, selected in menu_items:
            item = QListWidgetItem(item_text)
            nav_menu.addItem(item)
            if selected:
                item.setSelected(True)
        
        sidebar_layout.addWidget(nav_menu)
        
        # Add language switcher
        lang_container = QFrame()
        lang_container.setStyleSheet('background-color: #1a1d3a; padding: 10px 20px;')
        lang_layout = QHBoxLayout(lang_container)
        
        lang_label = QLabel('Language:')
        lang_label.setStyleSheet('color: #a0a0a0;')
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', '한국어'])
        self.lang_combo.setStyleSheet('''
            QComboBox {
                background-color: #2d325a;
                color: #fff;
                border: 1px solid #4fd1c5;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d325a;
                color: #fff;
                selection-background-color: #4fd1c5;
            }
        ''')
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        
        sidebar_layout.addWidget(lang_container)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sidebar_layout.addWidget(spacer)
        
        # Add logout button at bottom
        logout_btn = QPushButton('Logout')
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a0a0a0;
                padding: 15px 20px;
                text-align: left;
                border-radius: 0;
            }
            QPushButton:hover {
                background-color: #2d325a;
                color: white;
            }
        """)
        sidebar_layout.addWidget(logout_btn)
        
        quit_btn = QPushButton('Quit')
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a0a0a0;
                padding: 15px 20px;
                text-align: left;
                border-radius: 0;
            }
            QPushButton:hover {
                background-color: #2d325a;
                color: white;
            }
        """)
        quit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(quit_btn)
        
        # Set fixed width and styling for sidebar
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet('background-color: #1a1d3a;')
        
    def setup_table(self, table_container):
        # Table view setup
        self.table_view = QTableView()
        self.table_view.setStyleSheet("""
            QTableView {
                background-color: #1a1d2d;
                border: 1px solid #2d325a;
                gridline-color: #2d325a;
            }
            QTableView::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #2d325a;
                color: white;
                padding: 8px;
                border: none;
                border-right: 1px solid #4a4d7c;
                border-bottom: 1px solid #4a4d7c;
            }
            QTableView::item:selected {
                background-color: #3d426a;
            }
        """)
        
        # Set up the model and proxy model for sorting
        self.model = EngineerTableModel(self.session)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)
        
        # Set up the horizontal header
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft)
        
        # Set up the vertical header
        self.table_view.verticalHeader().setVisible(False)
        
        # Set selection behavior
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        
        table_container.addWidget(self.table_view)
        
        # Pagination controls
        pagination = QHBoxLayout()
        
        # Rows per page
        rows_label = QLabel("Rows per page:")
        rows_label.setStyleSheet("color: #a0a0a0;")
        pagination.addWidget(rows_label)
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(['10', '25', '50', '100'])
        self.page_size_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d325a;
                color: white;
                border: 1px solid #4a4d7c;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.page_size_combo.currentTextChanged.connect(lambda x: self.model.set_page_size(int(x)))
        pagination.addWidget(self.page_size_combo)
        
        pagination.addStretch()
        
        # Page navigation
        self.page_info = QLabel("1-10 of 0")
        self.page_info.setStyleSheet("color: #a0a0a0;")
        pagination.addWidget(self.page_info)
        
        prev_page = QPushButton("←")
        next_page = QPushButton("→")
        
        for btn in [prev_page, next_page]:
            btn.setFixedWidth(40)
            pagination.addWidget(btn)
        
        prev_page.clicked.connect(lambda: self.model.set_page(self.model.current_page - 1))
        next_page.clicked.connect(lambda: self.model.set_page(self.model.current_page + 1))
        
        table_container.addLayout(pagination)
        
    # Table operations
    def header_clicked(self, section):
        menu = QMenu(self)
        self.setup_header_menu(menu, section)
        header = self.table_view.horizontalHeader()
        menu.exec_(self.table_view.mapToGlobal(
            header.pos() + QPoint(header.sectionPosition(section), header.height())
        ))
        
    def setup_header_menu(self, menu, section):
        # Sorting actions
        unsort_action = QAction("Unsort", self)
        unsort_action.triggered.connect(lambda: self.sort_table(-1, None))
        menu.addAction(unsort_action)
        
        asc_action = QAction("Sort by ASC", self)
        asc_action.triggered.connect(lambda: self.sort_table(section, Qt.AscendingOrder))
        menu.addAction(asc_action)
        
        desc_action = QAction("Sort by DESC", self)
        desc_action.triggered.connect(lambda: self.sort_table(section, Qt.DescendingOrder))
        menu.addAction(desc_action)
        
        menu.addSeparator()
        
        # Column actions
        filter_action = QAction("Filter", self)
        filter_action.triggered.connect(lambda: self.show_filter_dialog(section))
        menu.addAction(filter_action)
        
        columns_action = QAction("Show columns", self)
        columns_action.triggered.connect(self.show_columns_dialog)
        menu.addAction(columns_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(lambda: self.hide_column(section))
        menu.addAction(hide_action)
        
    def show_context_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction('Edit')
        delete_action = menu.addAction('Delete')

        action = menu.exec_(self.table_view.viewport().mapToGlobal(position))
        if action == edit_action:
            self.edit_selected_engineer()
        elif action == delete_action:
            self.delete_selected_engineer()
            
    # CRUD Operations
    def add_engineer(self):
        dialog = EngineerDialog(self.session)
        if dialog.exec_():
            self.model.load_data()
            self.update_pagination_display()
            notification.show_success("Engineer added successfully", self)
            
    def edit_engineer(self):
        selected_engineers = self.model.get_selected_engineers()
        
        if selected_engineers:
            if len(selected_engineers) > 1:
                notification.show_error("Please select only one engineer to edit", self)
                return
            engineer = selected_engineers[0]
        else:
            index = self.table_view.selectionModel().currentIndex()
            if not index.isValid():
                notification.show_error("Please select an engineer to edit!", self)
                return
            source_index = self.proxy_model.mapToSource(index)
            engineer = self.model.get_visible_engineers()[source_index.row()]
        
        dialog = EngineerDialog(self.session, engineer)
        if dialog.exec_():
            self.model.load_data()
            self.update_pagination_display()
            notification.show_success("Engineer updated successfully", self)
            
    def delete_engineer(self):
        selected_engineers = self.model.get_selected_engineers()
        
        if not selected_engineers:
            index = self.table_view.selectionModel().currentIndex()
            if not index.isValid():
                notification.show_error("Please select an engineer to delete!", self)
                return
            source_index = self.proxy_model.mapToSource(index)
            selected_engineers = [self.model.get_visible_engineers()[source_index.row()]]
            
        message = "Are you sure you want to delete this engineer?" if len(selected_engineers) == 1 else \
                 f"Are you sure you want to delete {len(selected_engineers)} engineers?"
            
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
                
    def export_to_csv(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_name:
                if not file_name.endswith('.csv'):
                    file_name += '.csv'
                
                engineers = self.model.engineers
                
                with open(file_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.model.headers)
                    
                    for engineer in engineers:
                        writer.writerow([
                            engineer.id,
                            engineer.person_name,
                            engineer.birth_date,
                            engineer.address,
                            engineer.associated_company,
                            engineer.technical_grades.get('grade', [''])[0] if engineer.technical_grades else ''
                        ])
                
                notification.show_success(f"Data exported to {file_name}", self)
        except Exception as e:
            notification.show_error(f"Error exporting data: {str(e)}", self)
            
    # Other UI operations...
    def sort_table(self, column, order):
        if column == -1 or order is None:
            self.proxy_model.sort(-1)
        else:
            self.proxy_model.sort(column, order)
    
    def hide_column(self, column):
        self.table_view.setColumnHidden(column, True)
    
    def show_columns_dialog(self):
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
        header = self.model.headers[column]
        text, ok = QInputDialog.getText(self, f"Filter by {header}", f"Enter text to filter by {header}:")
        if ok and text:
            self.search_input.setText(text)
            self.search_engineers()
            
    def search_engineers(self):
        search_text = self.search_input.text()
        self.model.apply_filter(search_text)
        self.update_pagination_display()
        
        if search_text and self.model.rowCount(None) == 0:
            notification.show_error(f"No engineers found matching '{search_text}'", self)

    def change_language(self, text):
        lang_code = 'en' if text == 'English' else 'ko'
        translator.set_language(lang_code)
        self.update_translations()
        
    def update_translations(self):
        # Update window title
        self.setWindowTitle(translator.translate('app_title'))
        
        # Update table headers
        self.model.update_headers()
        
        # Update any other UI elements that need translation
        notification.show_success(translator.translate('success'), 'Language changed successfully')
