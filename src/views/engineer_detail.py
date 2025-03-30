import customtkinter as ctk
import json

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
        section_label = ctk.CTkLabel(
            self.main_frame,
            text=title,
            font=("Arial Bold", 14),
            anchor="w"
        )
        section_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
    
    def create_detail_field(self, parent, label, value, row=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        if row is not None:
            frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        else:
            frame.pack(fill="x", padx=5, pady=2)
        
        label = ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial Bold", 12),
            width=100,
            anchor="w"
        )
        label.pack(side="left")
        
        value = ctk.CTkLabel(
            frame,
            text=str(value if value is not None else ""),
            font=("Arial", 12),
            anchor="w"
        )
        value.pack(side="left", fill="x", expand=True)
