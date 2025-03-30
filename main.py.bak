import customtkinter as ctk
from PIL import Image, ImageDraw
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from src.services.translator import Translator
from src.services.notification import notification
from src.widgets.date_picker import DatePicker
import csv
import math
import json

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Constants
SIDEBAR_WIDTH = 240
ICON_SIZE = 20
DB_FILE = "engineers.db"  # Constant for database file

Base = declarative_base()
translator = Translator()
notification = notification

def init_database():
    # Create database engine
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILE)
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create tables only if they don't exist
    if not os.path.exists(db_path):
        Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    return Session()

class Engineer(Base):
    __tablename__ = 'engineers'
    id = Column(Integer, primary_key=True)
    person_name = Column(String)
    birth_date = Column(String)  # Changed to String to match the format '86.02.18'
    address = Column(String)
    associated_company = Column(String)
    currency_unit = Column(String, default='백만원')
    technical_grades = Column(String)  # Store as JSON string
    position_title = Column(String)
    expertise_area = Column(String)
    project_lead = Column(String)
    experience_summary = Column(String)
    participation_days = Column(String)  # Store as JSON string
    participation_details = Column(String)  # Store as JSON string
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

class EngineerTable(ctk.CTkFrame):
    def __init__(self, master, session):
        super().__init__(master)
        self.session = session
        self.engineers = []
        self.filtered_engineers = []
        self.current_page = 1
        self.rows_per_page = 10
        self.total_pages = 1
        self.selected_rows = set()
        
        # Create table header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=5, pady=(5,0))
        
        headers = ["Select", "ID", "Name", "Birth Date", "Company", "Position", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Create scrollable frame for table content
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid columns
        for i in range(len(headers)):
            self.table_frame.grid_columnconfigure(i, weight=1)
        
        self.load_data()
    
    def load_data(self):
        try:
            # Clear existing table
            for widget in self.table_frame.grid_slaves():
                widget.destroy()
            
            # Calculate offset and limit
            offset = (self.current_page - 1) * self.rows_per_page
            
            # Get total count
            total_count = self.session.query(Engineer).count()
            self.total_pages = math.ceil(total_count / self.rows_per_page)
            
            # Get engineers for current page
            engineers = self.session.query(Engineer).offset(offset).limit(self.rows_per_page).all()
            
            # Insert data
            for row, engineer in enumerate(engineers):
                # Create row selection checkbox
                checkbox = ctk.CTkCheckBox(
                    self.table_frame,
                    text="",
                    command=lambda id=engineer.id: self.toggle_row_selection(id),
                    width=20,
                    height=20
                )
                checkbox.grid(row=row, column=0, padx=5, pady=2)
                
                # Display engineer data
                ctk.CTkLabel(self.table_frame, text=str(engineer.id)).grid(row=row, column=1, padx=5, pady=2)
                ctk.CTkLabel(self.table_frame, text=engineer.person_name or "").grid(row=row, column=2, padx=5, pady=2)
                ctk.CTkLabel(self.table_frame, text=engineer.birth_date or "").grid(row=row, column=3, padx=5, pady=2)
                ctk.CTkLabel(self.table_frame, text=engineer.associated_company or "").grid(row=row, column=4, padx=5, pady=2)
                ctk.CTkLabel(self.table_frame, text=engineer.position_title or "").grid(row=row, column=5, padx=5, pady=2)
                
                # Actions buttons frame
                actions_frame = ctk.CTkFrame(self.table_frame)
                actions_frame.grid(row=row, column=6, padx=5, pady=2)
                
                # View Detail button
                view_btn = ctk.CTkButton(
                    actions_frame,
                    text="View",
                    width=60,
                    height=25,
                    command=lambda e=engineer: self.show_engineer_detail(e),
                    font=("Arial", 11)
                )
                view_btn.pack(side="left", padx=2)
                
                # Delete button
                delete_btn = ctk.CTkButton(
                    actions_frame,
                    text="Delete",
                    width=60,
                    height=25,
                    command=lambda e=engineer: self.delete_single_engineer(e),
                    font=("Arial", 11),
                    fg_color="#E74C3C",
                    hover_color="#C0392B"
                )
                delete_btn.pack(side="left", padx=2)
            
            # Update pagination state
            if hasattr(self, 'on_page_change'):
                self.on_page_change(self.current_page, self.total_pages)
        
        except Exception as e:
            notification.show_error(f"Error loading engineers: {str(e)}")
    
    def apply_filter(self, filter_text=""):
        self.filter_text = filter_text.lower()
        if not self.filter_text:
            self.filtered_engineers = self.session.query(Engineer).all()
        else:
            self.filtered_engineers = [
                engineer for engineer in self.session.query(Engineer).all()
                if (self.filter_text in str(engineer.id).lower() or
                    self.filter_text in (engineer.person_name or "").lower() or
                    self.filter_text in (engineer.address or "").lower() or
                    self.filter_text in (engineer.associated_company or "").lower() or
                    self.filter_text in (engineer.technical_grades or "").lower())
            ]
        self.current_page = 1
        self.load_data()
    
    def set_rows_per_page(self, value):
        """Set number of rows per page"""
        self.rows_per_page = int(value)
        self.current_page = 1  # Reset to first page
        self.load_data()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()
    
    def toggle_row_selection(self, engineer_id):
        if engineer_id in self.selected_rows:
            self.selected_rows.remove(engineer_id)
        else:
            self.selected_rows.add(engineer_id)
        self.load_data()

    def set_page_change_callback(self, callback):
        self.on_page_change = callback

    def show_engineer_detail(self, engineer):
        detail_dialog = EngineerDetailDialog(self, engineer)
        detail_dialog.focus()

    def get_selected_engineer(self):
        if len(self.selected_rows) != 1:
            return None
        engineer_id = list(self.selected_rows)[0]
        return self.session.query(Engineer).get(engineer_id)

    def delete_single_engineer(self, engineer):
        if notification.show_confirmation(f"Are you sure you want to delete engineer {engineer.person_name}?"):
            try:
                self.session.delete(engineer)
                self.session.commit()
                notification.show_success("Engineer deleted successfully")
                self.load_data()
            except Exception as e:
                self.session.rollback()
                notification.show_error(f"Error deleting engineer: {str(e)}")

class EngineerDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, engineer):
        super().__init__(parent)
        
        # Window setup
        self.title("Engineer Details")
        self.geometry("800x600")
        
        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Basic Information Section
        self.create_section("Basic Information", 0)
        basic_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        basic_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Left column
        left_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.create_detail_field(left_frame, "Name:", engineer.person_name)
        self.create_detail_field(left_frame, "Birth Date:", engineer.birth_date)
        self.create_detail_field(left_frame, "Position:", engineer.position_title)
        
        # Right column
        right_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.create_detail_field(right_frame, "Company:", engineer.associated_company)
        self.create_detail_field(right_frame, "Address:", engineer.address)
        self.create_detail_field(right_frame, "Currency:", engineer.currency_unit)
        
        # Technical Grades Section
        self.create_section("Technical Grades", 2)
        grades_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        grades_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        try:
            grades = json.loads(engineer.technical_grades or '{}')
            for i, (grade_type, grade) in enumerate(grades.items()):
                self.create_detail_field(grades_frame, f"{grade_type}:", grade, row=i)
        except json.JSONDecodeError:
            self.create_detail_field(grades_frame, "Error:", "Invalid grade data")
        
        # Qualifications Section
        self.create_section("Qualifications", 4)
        qual_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        qual_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        for i, qual in enumerate(engineer.qualifications):
            qual_item = ctk.CTkFrame(qual_frame, fg_color="#34495E", corner_radius=5)
            qual_item.pack(fill="x", padx=10, pady=5)
            self.create_detail_field(qual_item, "Title:", qual.title)
            self.create_detail_field(qual_item, "Date:", qual.acquisition_date)
            self.create_detail_field(qual_item, "Reg. Number:", qual.registration_number)
        
        # Education Section
        self.create_section("Education", 6)
        edu_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        edu_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        for i, edu in enumerate(engineer.education):
            edu_item = ctk.CTkFrame(edu_frame, fg_color="#34495E", corner_radius=5)
            edu_item.pack(fill="x", padx=10, pady=5)
            self.create_detail_field(edu_item, "Graduation:", edu.graduation_date)
            self.create_detail_field(edu_item, "Institution:", edu.institution)
            self.create_detail_field(edu_item, "Major:", edu.major)
            self.create_detail_field(edu_item, "Degree:", edu.degree)
        
        # Employment Section
        self.create_section("Employment History", 8)
        emp_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        emp_frame.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        for i, emp in enumerate(engineer.employment):
            emp_item = ctk.CTkFrame(emp_frame, fg_color="#34495E", corner_radius=5)
            emp_item.pack(fill="x", padx=10, pady=5)
            self.create_detail_field(emp_item, "Period:", emp.period)
            self.create_detail_field(emp_item, "Company:", emp.company)
        
        # Training Section
        self.create_section("Training", 10)
        train_frame = ctk.CTkFrame(self.main_frame, fg_color="#2C3E50", corner_radius=10)
        train_frame.grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        for i, train in enumerate(engineer.training):
            train_item = ctk.CTkFrame(train_frame, fg_color="#34495E", corner_radius=5)
            train_item.pack(fill="x", padx=10, pady=5)
            self.create_detail_field(train_item, "Period:", train.period)
            self.create_detail_field(train_item, "Course:", train.course_name)
            self.create_detail_field(train_item, "Institution:", train.institution)
            self.create_detail_field(train_item, "Certificate:", train.certificate_number)
        
        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            height=35,
            width=100,
            font=("Arial Bold", 12)
        )
        close_btn.pack(pady=20)
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()
    
    def create_section(self, title, row):
        label = ctk.CTkLabel(
            self.main_frame,
            text=title,
            font=("Arial Bold", 16),
            text_color="#3498DB"
        )
        label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
    
    def create_detail_field(self, parent, label, value, row=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        if row is not None:
            frame.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        else:
            frame.pack(fill="x", padx=5, pady=2)
        
        label_widget = ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial Bold", 12),
            text_color="#BDC3C7",
            width=100,
            anchor="e"
        )
        label_widget.pack(side="left", padx=(5, 10))
        
        value_widget = ctk.CTkLabel(
            frame,
            text=str(value or "N/A"),
            font=("Arial", 12),
            text_color="#ECF0F1",
            anchor="w"
        )
        value_widget.pack(side="left", fill="x", expand=True)

class EngineerDialog(ctk.CTkToplevel):
    def __init__(self, session, engineer=None, on_save=None):
        super().__init__()
        self.session = session
        self.engineer = engineer
        self.on_save = on_save
        self.title("Add/Edit Engineer")
        self.geometry("800x800")
        
        # Create main container with scrollbar
        container = ctk.CTkScrollableFrame(self)
        container.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Personal Information Section
        self.create_section_header(container, "Personal Information", 0)
        row = 1
        
        # Basic fields
        self.name_input = self.create_entry_row(container, "Name:", row)
        row += 1
        self.birth_date_input = self.create_entry_row(container, "Birth Date (YY.MM.DD):", row)
        row += 1
        self.address_input = self.create_entry_row(container, "Address:", row)
        row += 1
        self.company_input = self.create_entry_row(container, "Company:", row)
        row += 1
        self.currency_input = self.create_entry_row(container, "Currency Unit:", row, default="백만원")
        row += 1
        
        # Technical Grades Section
        self.create_section_header(container, "Technical Grades", row)
        row += 1
        
        # Technical Areas Frame
        tech_areas_frame = ctk.CTkFrame(container)
        tech_areas_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.tech_areas = []  # List to store technical area entries
        add_tech_area_btn = ctk.CTkButton(
            tech_areas_frame,
            text="Add Technical Area",
            command=lambda: self.add_tech_area(tech_areas_frame)
        )
        add_tech_area_btn.pack(pady=5)
        row += 1
        
        # Specializations Frame
        spec_frame = ctk.CTkFrame(container)
        spec_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.specializations = []  # List to store specialization entries
        add_spec_btn = ctk.CTkButton(
            spec_frame,
            text="Add Specialization",
            command=lambda: self.add_specialization(spec_frame)
        )
        add_spec_btn.pack(pady=5)
        row += 1
        
        # Grades Frame
        grades_frame = ctk.CTkFrame(container)
        grades_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.grades = []  # List to store grade entries
        add_grade_btn = ctk.CTkButton(
            grades_frame,
            text="Add Grade",
            command=lambda: self.add_grade(grades_frame)
        )
        add_grade_btn.pack(pady=5)
        row += 1
        
        # Qualifications Section
        self.create_section_header(container, "Qualifications", row)
        row += 1
        
        # Qualifications Frame
        qual_frame = ctk.CTkFrame(container)
        qual_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.qualifications = []  # List to store qualification entries
        add_qual_btn = ctk.CTkButton(
            qual_frame,
            text="Add Qualification",
            command=lambda: self.add_qualification(qual_frame)
        )
        add_qual_btn.pack(pady=5)
        row += 1
        
        # Education Section
        self.create_section_header(container, "Education", row)
        row += 1
        
        # Education Frame
        edu_frame = ctk.CTkFrame(container)
        edu_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.education = []  # List to store education entries
        add_edu_btn = ctk.CTkButton(
            edu_frame,
            text="Add Education",
            command=lambda: self.add_education(edu_frame)
        )
        add_edu_btn.pack(pady=5)
        row += 1
        
        # Employment History Section
        self.create_section_header(container, "Employment History", row)
        row += 1
        
        # Employment Frame
        emp_frame = ctk.CTkFrame(container)
        emp_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.employment = []  # List to store employment entries
        add_emp_btn = ctk.CTkButton(
            emp_frame,
            text="Add Employment",
            command=lambda: self.add_employment(emp_frame)
        )
        add_emp_btn.pack(pady=5)
        row += 1
        
        # Training Section
        self.create_section_header(container, "Training", row)
        row += 1
        
        # Training Frame
        training_frame = ctk.CTkFrame(container)
        training_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.training = []  # List to store training entries
        add_training_btn = ctk.CTkButton(
            training_frame,
            text="Add Training",
            command=lambda: self.add_training(training_frame)
        )
        add_training_btn.pack(pady=5)
        row += 1
        
        # Configure grid
        container.grid_columnconfigure(1, weight=1)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Save button
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=self.save_engineer,
            width=100
        )
        save_button.pack(side="left", padx=5)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            width=100
        )
        cancel_button.pack(side="left", padx=5)
        
        # Load data if editing
        if engineer:
            self.load_engineer_data(engineer)
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()
    
    def create_section_header(self, parent, text, row):
        header = ctk.CTkLabel(
            parent,
            text=text,
            font=("Arial Bold", 14)
        )
        header.grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5))
    
    def create_entry_row(self, parent, label, row, default=""):
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=("Arial", 12)
        )
        label_widget.grid(row=row, column=0, sticky="e", padx=(0, 10), pady=2)
        
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, sticky="ew", pady=2)
        entry.insert(0, default)
        return entry
    
    def add_tech_area(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        entry = ctk.CTkEntry(frame, placeholder_text="Technical Area")
        entry.pack(side="left", expand=True, fill="x", padx=5)
        
        remove_btn = ctk.CTkButton(
            frame, text="×", width=30,
            command=lambda: self.remove_item(frame, self.tech_areas)
        )
        remove_btn.pack(side="right", padx=5)
        
        self.tech_areas.append((frame, entry))
    
    def add_specialization(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        entry = ctk.CTkEntry(frame, placeholder_text="Specialization")
        entry.pack(side="left", expand=True, fill="x", padx=5)
        
        remove_btn = ctk.CTkButton(
            frame, text="×", width=30,
            command=lambda: self.remove_item(frame, self.specializations)
        )
        remove_btn.pack(side="right", padx=5)
        
        self.specializations.append((frame, entry))
    
    def add_grade(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        entry = ctk.CTkComboBox(frame, values=["초급", "중급", "고급"])
        entry.pack(side="left", expand=True, fill="x", padx=5)
        
        remove_btn = ctk.CTkButton(
            frame, text="×", width=30,
            command=lambda: self.remove_item(frame, self.grades)
        )
        remove_btn.pack(side="right", padx=5)
        
        self.grades.append((frame, entry))
    
    def add_qualification(self, parent):
        # Create a frame for this qualification entry
        entry_frame = ctk.CTkFrame(parent)
        entry_frame.pack(fill="x", padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(entry_frame, text="Title:", anchor="w")
        title_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        title_entry = ctk.CTkEntry(entry_frame, width=200)
        title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Date
        date_label = ctk.CTkLabel(entry_frame, text="Date:", anchor="w")
        date_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        date_entry = ctk.CTkEntry(entry_frame, width=200, placeholder_text="YY.MM.DD")
        date_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Registration Number
        reg_label = ctk.CTkLabel(entry_frame, text="Reg. Number:", anchor="w")
        reg_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        reg_entry = ctk.CTkEntry(entry_frame, width=200)
        reg_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Remove button
        remove_btn = ctk.CTkButton(
            entry_frame,
            text="✕",
            width=30,
            height=30,
            command=lambda: self.remove_item(entry_frame, self.qualifications),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.grid(row=0, column=2, padx=5, rowspan=3, sticky="ns")
        
        # Configure grid
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Store references
        self.qualifications.append((entry_frame, title_entry, date_entry, reg_entry))

    def add_education(self, parent):
        # Create a frame for this education entry
        entry_frame = ctk.CTkFrame(parent)
        entry_frame.pack(fill="x", padx=5, pady=5)
        
        # Graduation Date
        grad_label = ctk.CTkLabel(entry_frame, text="Graduation:", anchor="w")
        grad_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        grad_entry = ctk.CTkEntry(entry_frame, width=200, placeholder_text="YY.MM.DD")
        grad_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Institution
        inst_label = ctk.CTkLabel(entry_frame, text="Institution:", anchor="w")
        inst_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        inst_entry = ctk.CTkEntry(entry_frame, width=200)
        inst_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Major
        major_label = ctk.CTkLabel(entry_frame, text="Major:", anchor="w")
        major_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        major_entry = ctk.CTkEntry(entry_frame, width=200)
        major_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Degree
        degree_label = ctk.CTkLabel(entry_frame, text="Degree:", anchor="w")
        degree_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        degree_entry = ctk.CTkEntry(entry_frame, width=200)
        degree_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # Remove button
        remove_btn = ctk.CTkButton(
            entry_frame,
            text="✕",
            width=30,
            height=30,
            command=lambda: self.remove_item(entry_frame, self.education),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.grid(row=0, column=2, padx=5, rowspan=4, sticky="ns")
        
        # Configure grid
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Store references
        self.education.append((entry_frame, grad_entry, inst_entry, major_entry, degree_entry))

    def add_employment(self, parent):
        # Create a frame for this employment entry
        entry_frame = ctk.CTkFrame(parent)
        entry_frame.pack(fill="x", padx=5, pady=5)
        
        # Period
        period_label = ctk.CTkLabel(entry_frame, text="Period:", anchor="w")
        period_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        period_entry = ctk.CTkEntry(entry_frame, width=200, placeholder_text="YY.MM - YY.MM")
        period_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Company
        company_label = ctk.CTkLabel(entry_frame, text="Company:", anchor="w")
        company_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        company_entry = ctk.CTkEntry(entry_frame, width=200)
        company_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Remove button
        remove_btn = ctk.CTkButton(
            entry_frame,
            text="✕",
            width=30,
            height=30,
            command=lambda: self.remove_item(entry_frame, self.employment),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.grid(row=0, column=2, padx=5, rowspan=2, sticky="ns")
        
        # Configure grid
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Store references
        self.employment.append((entry_frame, period_entry, company_entry))

    def add_training(self, parent):
        # Create a frame for this training entry
        entry_frame = ctk.CTkFrame(parent)
        entry_frame.pack(fill="x", padx=5, pady=5)
        
        # Period
        period_label = ctk.CTkLabel(entry_frame, text="Period:", anchor="w")
        period_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        period_entry = ctk.CTkEntry(entry_frame, width=200, placeholder_text="YY.MM - YY.MM")
        period_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Course Name
        course_label = ctk.CTkLabel(entry_frame, text="Course:", anchor="w")
        course_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        course_entry = ctk.CTkEntry(entry_frame, width=200)
        course_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Institution
        inst_label = ctk.CTkLabel(entry_frame, text="Institution:", anchor="w")
        inst_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        inst_entry = ctk.CTkEntry(entry_frame, width=200)
        inst_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Certificate Number
        cert_label = ctk.CTkLabel(entry_frame, text="Cert. Number:", anchor="w")
        cert_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        cert_entry = ctk.CTkEntry(entry_frame, width=200)
        cert_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # Remove button
        remove_btn = ctk.CTkButton(
            entry_frame,
            text="✕",
            width=30,
            height=30,
            command=lambda: self.remove_item(entry_frame, self.training),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.grid(row=0, column=2, padx=5, rowspan=4, sticky="ns")
        
        # Configure grid
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Store references
        self.training.append((entry_frame, period_entry, course_entry, inst_entry, cert_entry))

    def remove_item(self, frame, items_list):
        # Remove the frame from the UI
        frame.destroy()
        # Remove the item from our tracking list
        for i, item in enumerate(items_list):
            if item[0] == frame:
                items_list.pop(i)
                break
    
    def load_engineer_data(self, engineer):
        # Load basic information
        self.name_input.insert(0, engineer.person_name or "")
        self.birth_date_input.insert(0, engineer.birth_date or "")
        self.address_input.insert(0, engineer.address or "")
        self.company_input.insert(0, engineer.associated_company or "")
        
        # Load technical grades
        if engineer.technical_grades:
            grades = json.loads(engineer.technical_grades)
            for area in grades.get("technical_area", []):
                self.add_tech_area(self.tech_areas[-1][0].master)
                self.tech_areas[-1][1].insert(0, area)
            
            for spec in grades.get("specialization", []):
                self.add_specialization(self.specializations[-1][0].master)
                self.specializations[-1][1].insert(0, spec)
            
            for grade in grades.get("grade", []):
                self.add_grade(self.grades[-1][0].master)
                self.grades[-1][1].set(grade)
        
        # Load qualifications
        for qual in engineer.qualifications:
            self.add_qualification(self.qualifications[-1][0].master)
            self.qualifications[-1][1].insert(0, qual.title)
            self.qualifications[-1][2].insert(0, qual.acquisition_date)
            self.qualifications[-1][3].insert(0, qual.registration_number)
        
        # Load education
        for edu in engineer.education:
            self.add_education(self.education[-1][0].master)
            self.education[-1][1].insert(0, edu.graduation_date)
            self.education[-1][2].insert(0, edu.institution)
            self.education[-1][3].insert(0, edu.major)
            self.education[-1][4].insert(0, edu.degree)
        
        # Load employment
        for emp in engineer.employment:
            self.add_employment(self.employment[-1][0].master)
            self.employment[-1][1].insert(0, emp.period)
            self.employment[-1][2].insert(0, emp.company)
        
        # Load training
        for train in engineer.training:
            self.add_training(self.training[-1][0].master)
            self.training[-1][1].insert(0, train.period)
            self.training[-1][2].insert(0, train.course_name)
            self.training[-1][3].insert(0, train.institution)
            self.training[-1][4].insert(0, train.certificate_number)
    
    def save_engineer(self):
        try:
            # Create or get engineer
            if self.engineer is None:
                self.engineer = Engineer()
            
            # Basic information
            self.engineer.person_name = self.name_input.get()
            self.engineer.birth_date = self.birth_date_input.get()
            self.engineer.address = self.address_input.get()
            self.engineer.associated_company = self.company_input.get()
            self.engineer.currency_unit = self.currency_input.get()
            
            # Technical grades
            tech_grades = {
                "technical_area": [entry.get() for _, entry in self.tech_areas],
                "specialization": [entry.get() for _, entry in self.specializations],
                "grade": [entry.get() for _, entry in self.grades],
                "construction_project_management": ["초급"],
                "quality_management": ["초급"]
            }
            self.engineer.technical_grades = json.dumps(tech_grades)
            
            if not self.engineer.id:
                self.session.add(self.engineer)
                self.session.flush()  # Get the engineer ID
            
            # Clear existing relationships
            self.session.query(Qualification).filter_by(engineer_id=self.engineer.id).delete()
            self.session.query(Education).filter_by(engineer_id=self.engineer.id).delete()
            self.session.query(Employment).filter_by(engineer_id=self.engineer.id).delete()
            self.session.query(Training).filter_by(engineer_id=self.engineer.id).delete()
            
            # Save qualifications
            for _, title_entry, date_entry, reg_entry in self.qualifications:
                qual = Qualification(
                    engineer_id=self.engineer.id,
                    title=title_entry.get(),
                    acquisition_date=date_entry.get(),
                    registration_number=reg_entry.get()
                )
                self.session.add(qual)
            
            # Save education
            for _, grad_date, institution, major, degree in self.education:
                edu = Education(
                    engineer_id=self.engineer.id,
                    graduation_date=grad_date.get(),
                    institution=institution.get(),
                    major=major.get(),
                    degree=degree.get()
                )
                self.session.add(edu)
            
            # Save employment
            for _, period, company in self.employment:
                emp = Employment(
                    engineer_id=self.engineer.id,
                    period=period.get(),
                    company=company.get()
                )
                self.session.add(emp)
            
            # Save training
            for _, period, course, institution, cert_num in self.training:
                train = Training(
                    engineer_id=self.engineer.id,
                    period=period.get(),
                    course_name=course.get(),
                    institution=institution.get(),
                    certificate_number=cert_num.get()
                )
                self.session.add(train)
            
            self.session.commit()
            
            if self.on_save:
                self.on_save()
            
            notification.show_success("Engineer saved successfully")
            self.destroy()
            
        except Exception as e:
            self.session.rollback()
            notification.show_error(f"Error saving engineer: {str(e)}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set this window as the main window for notifications
        notification.set_main_window(self)
        
        # Configure window
        self.title("Engineer Management System")
        self.geometry("1200x800")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create SQLite database
        self.session = init_database()
        
        # Create sidebar
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Profile section
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Create circular profile image
        profile_size = 80
        profile_image = Image.new('RGB', (profile_size, profile_size), color='#2B2B2B')
        draw = ImageDraw.Draw(profile_image)
        draw.ellipse([0, 0, profile_size, profile_size], fill='#1F538D')
        draw.text((profile_size//2, profile_size//2), "A", fill='white', anchor='mm', font=None)
        
        self.profile_photo = ctk.CTkImage(
            light_image=profile_image,
            dark_image=profile_image,
            size=(profile_size, profile_size)
        )
        
        profile_label = ctk.CTkLabel(
            profile_frame,
            image=self.profile_photo,
            text=""
        )
        profile_label.grid(row=0, column=0, pady=(0, 10))
        
        name_label = ctk.CTkLabel(
            profile_frame,
            text="Admin User",
            font=("Arial Bold", 16)
        )
        name_label.grid(row=1, column=0)
        
        role_label = ctk.CTkLabel(
            profile_frame,
            text="System Administrator",
            font=("Arial", 12),
            text_color="gray"
        )
        role_label.grid(row=2, column=0)
        
        # Navigation section
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=1, column=0, padx=10, sticky="ew")
        
        # Navigation items
        nav_items = [
            ("Dashboard", "🏠"),
            ("Engineers", "👥"),
            ("Reports", "📊"),
            ("Settings", "⚙️")
        ]
        
        for i, (text, icon) in enumerate(nav_items):
            # Create a frame for each nav item
            nav_item_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            nav_item_frame.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            nav_item_frame.grid_columnconfigure(1, weight=1)
            
            def create_hover_effect(frame, text, icon, command):
                def on_enter(e):
                    frame.configure(fg_color=("gray70", "gray30"))
                    icon_label.configure(fg_color=("gray70", "gray30"))
                    text_label.configure(fg_color=("gray70", "gray30"))
                
                def on_leave(e):
                    frame.configure(fg_color="transparent")
                    icon_label.configure(fg_color="transparent")
                    text_label.configure(fg_color="transparent")
                
                def on_click(e):
                    command(text)
                
                # Icon label
                icon_label = ctk.CTkLabel(
                    frame,
                    text=icon,
                    font=("Arial", 16),
                    width=30,
                    fg_color="transparent",
                    text_color=("gray10", "gray90")
                )
                icon_label.grid(row=0, column=0, padx=(5, 5))
                
                # Text label
                text_label = ctk.CTkLabel(
                    frame,
                    text=text,
                    font=("Arial Bold", 13),
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    anchor="w"
                )
                text_label.grid(row=0, column=1, sticky="w")
                
                # Bind events
                frame.bind("<Enter>", on_enter)
                icon_label.bind("<Enter>", on_enter)
                text_label.bind("<Enter>", on_enter)
                
                frame.bind("<Leave>", on_leave)
                icon_label.bind("<Leave>", on_leave)
                text_label.bind("<Leave>", on_leave)
                
                frame.bind("<Button-1>", on_click)
                icon_label.bind("<Button-1>", on_click)
                text_label.bind("<Button-1>", on_click)
                
                # Make it look clickable
                frame.configure(cursor="hand2")
                icon_label.configure(cursor="hand2")
                text_label.configure(cursor="hand2")
            
            create_hover_effect(nav_item_frame, text, icon, self.on_nav_button_click)
        
        # Bottom buttons frame
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=4, column=0, padx=20, pady=20, sticky="sew")
        
        # Logout button
        logout_button = ctk.CTkButton(
            bottom_frame,
            text="Logout",
            command=self.logout,
            font=("Arial Bold", 13),
            height=35,
            fg_color="#2980B9",
            hover_color="#2471A3"
        )
        logout_button.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        
        # Quit button
        quit_button = ctk.CTkButton(
            bottom_frame,
            text="Quit",
            command=self.quit,
            font=("Arial Bold", 13),
            height=35,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        quit_button.grid(row=1, column=0, sticky="ew")
        
        # Main content area
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Top toolbar with theme toggle and search
        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 10))
        toolbar.grid_columnconfigure(1, weight=1)  # Make search frame expand
        
        # Theme toggle button
        theme_button = ctk.CTkButton(
            toolbar,
            text="🌓",  # Moon emoji for theme toggle
            width=40,
            height=35,
            command=self.toggle_theme,
            font=("Arial", 16),
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            corner_radius=8
        )
        theme_button.grid(row=0, column=0, padx=(5, 10))
        
        # Search frame
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search engineers...",
            height=35
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=80,
            height=35,
            command=lambda: self.engineer_table.apply_filter(self.search_entry.get())
        )
        search_button.pack(side="left", padx=5)
        
        # Engineer table
        self.engineer_table = EngineerTable(self.content, self.session)
        self.engineer_table.grid(row=1, column=0, sticky="nsew")
        self.engineer_table.set_page_change_callback(self.update_pagination)
        
        # Bottom frame for pagination and actions
        bottom_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        # Pagination frame (left side)
        pagination_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        pagination_frame.grid(row=0, column=0, sticky="w")
        
        # Add pagination controls
        rows_per_page = ctk.CTkOptionMenu(
            pagination_frame,
            values=["10", "25", "50", "100"],
            width=70,
            height=35,
            command=self.engineer_table.set_rows_per_page
        )
        rows_per_page.set("25")
        rows_per_page.pack(side="left", padx=5)
        
        self.prev_page = ctk.CTkButton(
            pagination_frame,
            text="←",
            width=35,
            height=35,
            command=self.engineer_table.prev_page
        )
        self.prev_page.pack(side="left", padx=5)
        
        self.page_info = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 of 1",
            width=100,
            height=35
        )
        self.page_info.pack(side="left", padx=5)
        
        self.next_page = ctk.CTkButton(
            pagination_frame,
            text="→",
            width=35,
            height=35,
            command=self.engineer_table.next_page
        )
        self.next_page.pack(side="left", padx=5)
        
        # Action buttons frame (right side)
        actions_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")
        
        add_button = ctk.CTkButton(
            actions_frame,
            text="Add Engineer",
            command=self.add_engineer,
            height=35,
            font=("Arial Bold", 12)
        )
        add_button.pack(side="left", padx=5)
        
        edit_button = ctk.CTkButton(
            actions_frame,
            text="Edit",
            command=self.edit_engineer,
            height=35,
            width=80,
            font=("Arial Bold", 12)
        )
        edit_button.pack(side="left", padx=5)
        
        delete_button = ctk.CTkButton(
            actions_frame,
            text="Delete Selected",
            command=self.delete_engineer,
            height=35,
            width=120,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            font=("Arial Bold", 12)
        )
        delete_button.pack(side="left", padx=5)
        
        export_button = ctk.CTkButton(
            actions_frame,
            text="Export CSV",
            command=self.export_to_csv,
            height=35,
            width=100,
            font=("Arial Bold", 12)
        )
        export_button.pack(side="left", padx=5)
    
    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
    
    def on_nav_button_click(self, section):
        # Handle navigation - for now just print the section
        print(f"Navigating to {section}")

    def add_engineer(self):
        dialog = EngineerDialog(self.session, on_save=self.engineer_table.load_data)
        self.wait_window(dialog)
    
    def edit_engineer(self):
        if len(self.engineer_table.selected_rows) != 1:
            notification.show_error("Please select exactly one engineer to edit")
            return
        
        engineer_id = list(self.engineer_table.selected_rows)[0]
        engineer = self.session.query(Engineer).get(engineer_id)
        if engineer:
            dialog = EngineerDialog(self.session, engineer, on_save=self.engineer_table.load_data)
            self.wait_window(dialog)
    
    def delete_engineer(self):
        if not self.engineer_table.selected_rows:
            notification.show_error("Please select at least one engineer to delete")
            return
        
        try:
            for engineer_id in self.engineer_table.selected_rows:
                engineer = self.session.query(Engineer).get(engineer_id)
                if engineer:
                    self.session.delete(engineer)
            
            self.session.commit()
            notification.show_success(f"Successfully deleted {len(self.engineer_table.selected_rows)} engineer(s)")
            self.engineer_table.selected_rows.clear()
            self.engineer_table.load_data()
            
        except Exception as e:
            notification.show_error(f"Error deleting engineers: {str(e)}")
    
    def export_to_csv(self):
        try:
            filename = "engineers.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Name", "Birth Date", "Address", "Company", "Technical Grade"])
                
                for engineer in self.session.query(Engineer).all():
                    writer.writerow([
                        engineer.id,
                        engineer.person_name,
                        engineer.birth_date,
                        engineer.address,
                        engineer.associated_company,
                        engineer.technical_grades
                    ])
            
            notification.show_success(f"Successfully exported to {filename}")
            
        except Exception as e:
            notification.show_error(f"Error exporting to CSV: {str(e)}")
    
    def logout(self):
        """Handle logout action"""
        if notification.show_confirmation("Are you sure you want to logout?"):
            # Add your logout logic here
            self.quit()  # For now, just quit the application

    def update_pagination(self, current_page, total_pages):
        self.prev_page.configure(state="normal" if current_page > 1 else "disabled")
        self.next_page.configure(state="normal" if current_page < total_pages else "disabled")
        self.page_info.configure(text=f"Page {current_page} of {total_pages}")

if __name__ == "__main__":
    app = App()
    app.mainloop()