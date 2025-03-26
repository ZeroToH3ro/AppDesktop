from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QDateEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QDate
from src.models.engineer import Engineer
from src.services import notification

class EngineerDialog(QDialog):
    def __init__(self, session, engineer=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.engineer = engineer
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Engineer Details")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Create form fields
        self.name_input = QLineEdit()
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate())
        self.address_input = QLineEdit()
        self.company_input = QLineEdit()
        self.grade_input = QLineEdit()
        
        # Add fields to form
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Birth Date:", self.birth_date_input)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("Company:", self.company_input)
        form_layout.addRow("Technical Grade:", self.grade_input)
        
        layout.addLayout(form_layout)
        
        # Button container
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_engineer)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # If editing existing engineer, populate fields
        if self.engineer:
            self.name_input.setText(self.engineer.person_name or "")
            if self.engineer.birth_date:
                self.birth_date_input.setDate(self.engineer.birth_date)
            self.address_input.setText(self.engineer.address or "")
            self.company_input.setText(self.engineer.associated_company or "")
            if self.engineer.technical_grades and 'grade' in self.engineer.technical_grades:
                self.grade_input.setText(self.engineer.technical_grades['grade'][0])
                
    def save_engineer(self):
        try:
            name = self.name_input.text().strip()
            if not name:
                notification.show_error("Name is required!", self)
                return
                
            if not self.engineer:
                self.engineer = Engineer()
                
            self.engineer.person_name = name
            self.engineer.birth_date = self.birth_date_input.date().toPyDate()
            self.engineer.address = self.address_input.text().strip()
            self.engineer.associated_company = self.company_input.text().strip()
            self.engineer.technical_grades = {'grade': [self.grade_input.text().strip()]} if self.grade_input.text().strip() else None
            
            if not self.engineer.id:
                self.session.add(self.engineer)
                
            self.session.commit()
            self.accept()
            
        except Exception as e:
            notification.show_error(f"Error saving engineer: {str(e)}", self)
            self.session.rollback()
