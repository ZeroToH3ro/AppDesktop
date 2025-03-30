import customtkinter as ctk
import json
from src.services.notification import notification
from src.models.engineer import Engineer, Qualification, Education, Employment, Training
from src.widgets.date_picker import DatePicker, PeriodPicker
from datetime import datetime

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
        
        # Replace text entry with DatePicker for birth date
        self.birth_date_label = ctk.CTkLabel(container, text="Birth Date:")
        self.birth_date_label.grid(row=row, column=0, padx=5, pady=5, sticky="e")
        self.birth_date_input = DatePicker(container)
        self.birth_date_input.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        row += 1
        
        self.address_input = self.create_entry_row(container, "Address:", row)
        row += 1
        self.company_input = self.create_entry_row(container, "Company:", row)
        row += 1
        self.currency_input = self.create_entry_row(container, "Currency Unit:", row, default="백만원")
        row += 1
        self.position_title = self.create_entry_row(container, "Position Title:", row)
        row += 1
        self.expertise_area = self.create_entry_row(container, "Expertise Area:", row)
        row += 1
        self.project_lead = self.create_entry_row(container, "Project Lead:", row)
        row += 1
        self.experience_summary = self.create_entry_row(container, "Experience Summary:", row)
        row += 1
        
        # TODO: Add participation days and details in the future
        # self.participation_days = self.create_entry_row(container, "Participation Days:", row)
        # row += 1
        # self.participation_details = self.create_entry_row(container, "Participation Details:", row)
        # row += 1
        
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
        header = ctk.CTkLabel(parent, text=text, font=("Arial Bold", 14))
        header.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(15, 5))

    def create_entry_row(self, parent, label, row, default=""):
        label = ctk.CTkLabel(parent, text=label)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        entry.insert(0, default)
        
        return entry

    def add_tech_area(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        type_entry = ctk.CTkEntry(frame, placeholder_text="Type")
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        grade_entry = ctk.CTkEntry(frame, placeholder_text="Grade")
        grade_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            command=lambda: self.remove_item(frame, self.tech_areas),
            width=60,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)
        
        self.tech_areas.append({'area': type_entry, 'grade': grade_entry})

    def add_qualification(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        title_entry = ctk.CTkEntry(frame, placeholder_text="Title")
        title_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        date_entry = ctk.CTkEntry(frame, placeholder_text="Date")
        date_entry.pack(side="left", padx=5)
        
        reg_entry = ctk.CTkEntry(frame, placeholder_text="Registration Number")
        reg_entry.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            command=lambda: self.remove_item(frame, self.qualifications),
            width=60,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)
        
        self.qualifications.append((title_entry, date_entry, reg_entry))

    def add_education(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        grad_entry = ctk.CTkEntry(frame, placeholder_text="Graduation Date")
        grad_entry.pack(side="left", padx=5)
        
        inst_entry = ctk.CTkEntry(frame, placeholder_text="Institution")
        inst_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        major_entry = ctk.CTkEntry(frame, placeholder_text="Major")
        major_entry.pack(side="left", padx=5)
        
        degree_entry = ctk.CTkEntry(frame, placeholder_text="Degree")
        degree_entry.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            command=lambda: self.remove_item(frame, self.education),
            width=60,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)
        
        self.education.append((grad_entry, inst_entry, major_entry, degree_entry))

    def add_employment(self, container):
        employment_frame = ctk.CTkFrame(container)
        employment_frame.pack(fill="x", padx=5, pady=2)
        
        # Use PeriodPicker for employment period
        period_picker = PeriodPicker(employment_frame, "Period:")
        period_picker.pack(side="left", padx=5, pady=2)
        
        company_input = ctk.CTkEntry(employment_frame, placeholder_text="Company")
        company_input.pack(side="left", padx=5, pady=2, fill="x", expand=True)
        
        remove_btn = ctk.CTkButton(
            employment_frame,
            text="Remove",
            command=lambda: employment_frame.destroy(),
            width=60,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5, pady=2)
        
        self.employment.append({
            'period': period_picker,
            'company': company_input
        })
        
        return employment_frame

    def add_training(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        
        period_entry = ctk.CTkEntry(frame, placeholder_text="Period")
        period_entry.pack(side="left", padx=5)
        
        course_entry = ctk.CTkEntry(frame, placeholder_text="Course Name")
        course_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        inst_entry = ctk.CTkEntry(frame, placeholder_text="Institution")
        inst_entry.pack(side="left", padx=5)
        
        cert_entry = ctk.CTkEntry(frame, placeholder_text="Certificate Number")
        cert_entry.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            command=lambda: self.remove_item(frame, self.training),
            width=60,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)
        
        self.training.append((course_entry, period_entry, inst_entry))

    def remove_item(self, frame, items_list):
        frame.destroy()
        items_list.remove([item for item in items_list if item[0].winfo_parent() == str(frame)][0])

    def load_engineer_data(self, engineer):
        # Load basic information
        self.name_input.insert(0, engineer.person_name or "")
        if engineer.birth_date:
            try:
                date_obj = datetime.strptime(engineer.birth_date, "%Y-%m-%d")
                self.birth_date_input.set(date_obj.strftime("%y.%m.%d"))
            except ValueError:
                pass
        self.address_input.insert(0, engineer.address or "")
        self.company_input.insert(0, engineer.associated_company or "")
        self.currency_input.insert(0, engineer.currency_unit or "백만원")
        self.position_title.insert(0, engineer.position_title or "")
        self.expertise_area.insert(0, engineer.expertise_area or "")
        self.project_lead.insert(0, engineer.project_lead or "")
        self.experience_summary.insert(0, engineer.experience_summary or "")
        
        # Load technical grades
        try:
            grades = json.loads(engineer.technical_grades or '{}')
            for grade_type, grade in grades.items():
                self.add_tech_area(self.tech_areas[-1]['area'].master)
                self.tech_areas[-1]['area'].insert(0, grade_type)
                self.tech_areas[-1]['grade'].insert(0, grade)
        except json.JSONDecodeError:
            pass
        
        # Load qualifications
        for qual in engineer.qualifications:
            self.add_qualification(self.qualifications[-1][0].master)
            self.qualifications[-1][0].insert(0, qual.title or "")
            self.qualifications[-1][1].insert(0, qual.acquisition_date or "")
            self.qualifications[-1][2].insert(0, qual.registration_number or "")
        
        # Load education
        for edu in engineer.education:
            self.add_education(self.education[-1][0].master)
            self.education[-1][0].insert(0, edu.graduation_date or "")
            self.education[-1][1].insert(0, edu.institution or "")
            self.education[-1][2].insert(0, edu.major or "")
            self.education[-1][3].insert(0, edu.degree or "")
        
        # Load employment
        for emp in engineer.employment:
            employment_frame = self.add_employment(self.employment[-1]['company'].master)
            self.employment[-1]['period'].set_date(emp.period or "")
            self.employment[-1]['company'].insert(0, emp.company or "")
        
        # Load training
        for train in engineer.training:
            self.add_training(self.training[-1][0].master)
            self.training[-1][0].insert(0, train.course_name or "")
            self.training[-1][1].insert(0, train.period or "")
            self.training[-1][2].insert(0, train.institution or "")

    def save_engineer(self):
        try:
            if not self.name_input.get():
                notification.show_error("Name is required")
                return
            
            # Create new engineer if needed
            if not self.engineer:
                self.engineer = Engineer()
            
            # Save basic information
            self.engineer.person_name = self.name_input.get()
            birth_date = self.birth_date_input.get()
            if birth_date:
                try:
                    self.engineer.birth_date = datetime.strptime(birth_date, "%y.%m.%d").date()
                except ValueError:
                    self.engineer.birth_date = None
            else:
                self.engineer.birth_date = None
                
            self.engineer.address = self.address_input.get()
            self.engineer.associated_company = self.company_input.get()
            self.engineer.currency_unit = self.currency_input.get()
            self.engineer.position_title = self.position_title.get()
            self.engineer.expertise_area = self.expertise_area.get()
            self.engineer.project_lead = self.project_lead.get()
            self.engineer.experience_summary = self.experience_summary.get()
            
            # Save technical grades
            grades = {}
            for area in self.tech_areas:
                area_name = area['area'].get()
                grade = area['grade'].get()
                if area_name and grade:
                    grades[area_name] = grade
            self.engineer.technical_grades = json.dumps(grades)
            
            # Save qualifications
            self.engineer.qualifications.clear()
            for title, acq_date, reg_num in self.qualifications:
                if title.get():
                    qual_date = None
                    if acq_date.get():
                        try:
                            qual_date = datetime.strptime(acq_date.get(), "%y.%m.%d").date()
                        except ValueError:
                            pass
                            
                    qual = Qualification(
                        title=title.get(),
                        acquisition_date=qual_date,
                        registration_number=reg_num.get()
                    )
                    self.engineer.qualifications.append(qual)
            
            # Save education
            self.engineer.education.clear()
            for grad_date, inst, major, degree in self.education:
                if inst.get():
                    grad_date_obj = None
                    if grad_date.get():
                        try:
                            grad_date_obj = datetime.strptime(grad_date.get(), "%y.%m.%d").date()
                        except ValueError:
                            pass
                            
                    edu = Education(
                        graduation_date=grad_date_obj,
                        institution=inst.get(),
                        major=major.get(),
                        degree=degree.get()
                    )
                    self.engineer.education.append(edu)
            
            # Save employment
            self.engineer.employment.clear()
            for emp in self.employment:
                if emp['company'].get():
                    period = emp['period'].get()
                    if period:
                        employment = Employment(
                            period=period,
                            company=emp['company'].get()
                        )
                        self.engineer.employment.append(employment)
            
            # Save training
            self.engineer.training.clear()
            for course, period, org in self.training:
                if course.get():
                    train = Training(
                        course=course.get(),
                        period=period.get(),
                        organization=org.get()
                    )
                    self.engineer.training.append(train)
            
            # Save to database
            if not self.engineer.id:
                self.session.add(self.engineer)
            self.session.commit()
            
            notification.show_success("Engineer saved successfully")
            
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except Exception as e:
            notification.show_error(f"Error saving engineer: {str(e)}")
            self.session.rollback()
