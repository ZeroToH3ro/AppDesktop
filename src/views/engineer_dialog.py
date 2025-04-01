import customtkinter as ctk
from tkinter import filedialog
from src.services.notification import notification
from src.models.engineer import (
    Engineer, TechnicalGrade, Qualification, Education, TechnicalSectorParticipation,
    JobSectorParticipation, SpecializedFieldParticipation, ConstructionTypeParticipation,
    EducationAndTraining, Award, Sanction, Workplace, ProjectDetail
)
from src.widgets.date_picker import DatePicker
from datetime import datetime

class EngineerDialog(ctk.CTkToplevel):
    def __init__(self, session, engineer=None, on_save=None):
        super().__init__()
        self.session = session
        self.engineer = engineer if engineer else Engineer()
        self.on_save = on_save
        self.title("Edit Engineer" if engineer else "Add Engineer")
        self.geometry("1120x800")

        # Initialize relationship lists
        self.tech_grades = []
        self.qualifications = []
        self.education = []
        self.tech_sectors = []
        self.job_sectors = []
        self.specialized_fields = []
        self.construction_types = []
        self.trainings = []
        self.awards = []
        self.sanctions = []
        self.workplaces = []
        self.project_details = []

        # Dictionary to store input containers for each section
        self.input_containers = {}

        # Main scrollable container
        self.container = ctk.CTkScrollableFrame(self)
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        row = 0

        # **Basic Information Section**
        row = self.create_section_header(self.container, "Basic Information", row)

        # Name and Birth Date row
        name_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        name_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        name_frame.grid_columnconfigure(1, weight=1)
        name_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(name_frame, text="Name").grid(row=0, column=0, padx=5)
        self.name_input = ctk.CTkEntry(name_frame)
        self.name_input.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(name_frame, text="Birth Date").grid(row=0, column=2, padx=5)
        self.birth_date_input = DatePicker(name_frame)
        self.birth_date_input.grid(row=0, column=3, padx=5, sticky="w")
        row += 1

        self.address_input = self.create_entry_row(self.container, "Address", row)
        row += 1

        # Company Name and Position and Rank row
        company_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        company_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        company_frame.grid_columnconfigure(1, weight=1)
        company_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(company_frame, text="Company Name").grid(row=0, column=0, padx=5)
        self.company_input = ctk.CTkEntry(company_frame)
        self.company_input.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(company_frame, text="Position and Rank").grid(row=0, column=2, padx=5)
        self.position_input = ctk.CTkEntry(company_frame)
        self.position_input.grid(row=0, column=3, padx=5, sticky="ew")
        row += 1

        self.responsible_technical_manager = self.create_entry_row(self.container, "Responsible Technical Manager", row)
        row += 1
        self.field_name = self.create_entry_row(self.container, "Field Name", row)
        row += 1
        self.experience = self.create_textbox_row(self.container, "Experience Summary", row, height=100)
        row += 1
        self.field_name = self.create_textbox_row(self.container, "Expertise Area", row, height=100)
        row += 1
        self.evaluation_target = self.create_entry_row(self.container, "Evaluation Target", row)
        row += 1
        ctk.CTkLabel(self.container, text="PDF File").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        self.pdf_file_path = ctk.StringVar()
        self.pdf_file_button = ctk.CTkButton(self.container, text="Upload PDF", command=self._upload_pdf)
        self.pdf_file_button.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        row += 1
        selected_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        selected_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(selected_frame, text="Project Lead").grid(row=0, column=0, padx=5)
        self.selected_var = ctk.BooleanVar(value=False)
        self.selected_checkbox = ctk.CTkCheckBox(selected_frame, text="", variable=self.selected_var)
        self.selected_checkbox.grid(row=0, column=1, padx=5)
        row += 1

        # **Relationship Sections**
        row = self.add_relationship_section("Technical Grades", row, self.add_tech_grade)
        row = self.add_relationship_section("Technical Qualifications", row, self.add_qualification)
        row = self.add_relationship_section("Education", row, self.add_education)
        row = self.add_relationship_section("Technical Sector Participation", row, self.add_tech_sector)
        row = self.add_relationship_section("Job Sector Participation", row, self.add_job_sector)
        row = self.add_relationship_section("Specialized Field Participation", row, self.add_specialized_field)
        row = self.add_relationship_section("Construction Type Participation", row, self.add_construction_type)
        row = self.add_relationship_section("Education and Training", row, self.add_training)
        row = self.add_relationship_section("Awards", row, self.add_award)
        row = self.add_relationship_section("Sanctions", row, self.add_sanction)
        row = self.add_relationship_section("Workplace", row, self.add_workplace)
        row = self.add_relationship_section("Project Details", row, self.add_project_detail)

        # **Buttons**
        buttons_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ctk.CTkButton(
            buttons_frame, text="Cancel", command=self.destroy, width=100, fg_color="#E74C3C", hover_color="#C0392B"
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            buttons_frame, text="Save", command=self.save_engineer, width=100
        ).pack(side="left", padx=5)

        # Load existing data
        if engineer:
            self.load_engineer_data(engineer)

        self.transient(self.master)
        self.grab_set()

    # **Helper Methods**
    def create_section_header(self, parent, text, row):
        header = ctk.CTkLabel(parent, text=text, font=("Arial", 14, "bold"))
        header.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))
        return row + 1

    def create_entry_row(self, parent, label, row):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return entry

    def create_textbox_row(self, parent, label, row, height):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="nw")
        textbox = ctk.CTkTextbox(parent, height=height)
        textbox.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
        return textbox

    def add_relationship_section(self, title, row, add_method):
        section_frame = ctk.CTkFrame(self.container)
        section_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Header with title and add button
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header_frame, text=title).pack(side="left")
        
        # Input container for fields
        input_container = ctk.CTkFrame(section_frame, fg_color="transparent")
        input_container.pack(fill="x", padx=5, pady=5)
        self.input_containers[title] = input_container
        
        # Pre-create initial fields
        if title == "Technical Grades":
            self._create_tech_grade_fields(input_container)
        elif title == "Technical Qualifications":
            self._create_qualification_fields(input_container)
        elif title == "Education":
            self._create_education_fields(input_container)
        elif title == "Technical Sector Participation":
            self._create_tech_sector_fields(input_container)
        elif title == "Job Sector Participation":
            self._create_job_sector_fields(input_container)
        elif title == "Specialized Field Participation":
            self._create_specialized_field_fields(input_container)
        elif title == "Construction Type Participation":
            self._create_construction_type_fields(input_container)
        elif title == "Education and Training":
            self._create_training_fields(input_container)
        elif title == "Awards":
            self._create_award_fields(input_container)
        elif title == "Sanctions":
            self._create_sanction_fields(input_container)
        elif title == "Workplace":
            self._create_workplace_fields(input_container)
        elif title == "Project Details":
            self._create_project_detail_fields(input_container)
            
        # Add button
        ctk.CTkButton(
            header_frame,
            text=f"Add {title}",
            command=add_method,
            fg_color="#2980B9",
            hover_color="#2573A7",
            height=32
        ).pack(side="right", padx=5)
        
        return row + 1

    def _create_tech_grade_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        type_entry = ctk.CTkEntry(frame, placeholder_text="Grade Type", height=32)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        field_entry = ctk.CTkEntry(frame, placeholder_text="Field", height=32)
        field_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        grade_options = ["Beginner", "Intermediate", "Advanced", "Special", "Technician"]
        grade_dropdown = ctk.CTkComboBox(frame, values=grade_options, state="readonly", height=32)
        grade_dropdown.set("Beginner")
        grade_dropdown.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def _create_qualification_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        title_entry = ctk.CTkEntry(frame, placeholder_text="Title", height=32)
        title_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        
        reg_entry = ctk.CTkEntry(frame, placeholder_text="Registration Number", height=32)
        reg_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)

    def _create_education_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        grad_date_entry = DatePicker(frame)
        grad_date_entry.pack(side="left", padx=5)
        
        school_entry = ctk.CTkEntry(frame, placeholder_text="School Name", height=32)
        school_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        major_entry = ctk.CTkEntry(frame, placeholder_text="Major", height=32)
        major_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        degree_entry = ctk.CTkEntry(frame, placeholder_text="Degree", height=32)
        degree_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)

    def _create_tech_sector_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        sector_entry = ctk.CTkEntry(frame, placeholder_text="Technical Sector", height=32)
        sector_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days", height=32)
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)

    def _create_job_sector_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        job_entry = ctk.CTkEntry(frame, placeholder_text="Job", height=32)
        job_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days", height=32)
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        remove_btn.pack(side="right", padx=5)

    # **Add Methods for Relationships**
    def add_tech_grade(self):
        input_container = self.input_containers["Technical Grades"]
        self._create_tech_grade_fields(input_container)

    def add_qualification(self):
        input_container = self.input_containers["Technical Qualifications"]
        self._create_qualification_fields(input_container)

    def add_education(self):
        input_container = self.input_containers["Education"]
        self._create_education_fields(input_container)

    def add_tech_sector(self):
        input_container = self.input_containers["Technical Sector Participation"]
        self._create_tech_sector_fields(input_container)

    def add_job_sector(self):
        input_container = self.input_containers["Job Sector Participation"]
        self._create_job_sector_fields(input_container)

    def add_specialized_field(self):
        input_container = self.input_containers["Specialized Field Participation"]
        self._create_specialized_field_fields(input_container)

    def add_construction_type(self):
        input_container = self.input_containers["Construction Type Participation"]
        self._create_construction_type_fields(input_container)

    def add_training(self):
        input_container = self.input_containers["Education and Training"]
        self._create_training_fields(input_container)

    def add_award(self):
        input_container = self.input_containers["Awards"]
        self._create_award_fields(input_container)

    def add_sanction(self):
        input_container = self.input_containers["Sanctions"]
        self._create_sanction_fields(input_container)

    def add_workplace(self):
        input_container = self.input_containers["Workplace"]
        self._create_workplace_fields(input_container)

    def add_project_detail(self):
        input_container = self.input_containers["Project Details"]
        self._create_project_detail_fields(input_container)

    def _create_specialized_field_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        field_entry = ctk.CTkEntry(frame, placeholder_text="Specialized Field", height=32)
        field_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days", height=32)
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def _create_construction_type_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        type_entry = ctk.CTkEntry(frame, placeholder_text="Construction Type", height=32)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days", height=32)
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def _create_training_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        period_entry = ctk.CTkEntry(frame, placeholder_text="Training Period", height=32)
        period_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        course_entry = ctk.CTkEntry(frame, placeholder_text="Course Name", height=32)
        course_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Institution Name", height=32)
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        completion_entry = ctk.CTkEntry(frame, placeholder_text="Completion Number", height=32)
        completion_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        field_entry = ctk.CTkEntry(frame, placeholder_text="Training Field", height=32)
        field_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def _create_award_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        
        type_entry = ctk.CTkEntry(frame, placeholder_text="Type and Basis", height=32)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Awarding Institution", height=32)
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def _create_sanction_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        points_entry = ctk.CTkEntry(frame, placeholder_text="Penalty Points", height=32)
        points_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        
        type_entry = ctk.CTkEntry(frame, placeholder_text="Type", height=32)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        period_entry = ctk.CTkEntry(frame, placeholder_text="Sanction Period", height=32)
        period_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        basis_entry = ctk.CTkEntry(frame, placeholder_text="Basis", height=32)
        basis_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Sanctioning Institution", height=32)
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def _create_workplace_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        period_entry = ctk.CTkEntry(frame, placeholder_text="Experience Period", height=32)
        period_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name", height=32)
        company_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def _create_project_detail_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=2)
        
        service_entry = ctk.CTkEntry(frame, placeholder_text="Service Name", height=32)
        service_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        project_type_entry = ctk.CTkEntry(frame, placeholder_text="Project Type", height=32)
        project_type_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name", height=32)
        company_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        contractor_entry = ctk.CTkEntry(frame, placeholder_text="Representative Contractor", height=32)
        contractor_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        contract_date_entry = DatePicker(frame)
        contract_date_entry.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(
            frame,
            text="Remove",
            width=80,
            height=32,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            command=lambda: frame.destroy()
        )
        remove_btn.pack(side="right", padx=5)

    def load_engineer_data(self, engineer):
        self.name_input.insert(0, engineer.name or "")
        if engineer.date_of_birth:
            self.birth_date_input.set_date(engineer.date_of_birth)
        self.address_input.insert(0, engineer.address or "")
        self.company_input.insert(0, engineer.company_name or "")
        self.position_input.insert(0, engineer.position_and_rank or "")
        self.responsible_technical_manager.insert(0, engineer.responsible_technical_manager or "")
        self.experience.insert("1.0", engineer.experience or "")
        self.field_name.insert("1.0", engineer.field_name or "")
        self.evaluation_target.insert(0, engineer.evaluation_target or "")
        self.pdf_file_path.set(engineer.pdf_file or "")
        self.selected_var.set(engineer.selected or False)

        for grade in engineer.technical_grades:
            self.add_tech_grade()
            self.tech_grades[-1]['type'].insert(0, grade.grade_type or "")
            self.tech_grades[-1]['field'].insert(0, grade.field or "")
            self.tech_grades[-1]['grade'].set(grade.grade or "")

        for qual in engineer.technical_qualifications:
            self.add_qualification()
            self.qualifications[-1]['title'].insert(0, qual.title or "")
            if qual.acquisition_date:
                self.qualifications[-1]['date'].set_date(qual.acquisition_date)
            self.qualifications[-1]['reg_num'].insert(0, qual.registration_number or "")

        for edu in engineer.education:
            self.add_education()
            if edu.graduation_date:
                self.education[-1]['grad_date'].set_date(edu.graduation_date)
            self.education[-1]['school'].insert(0, edu.school_name or "")
            self.education[-1]['major'].insert(0, edu.major or "")
            self.education[-1]['degree'].insert(0, edu.degree or "")

        for ts in engineer.technical_sector_participation:
            self.add_tech_sector()
            self.tech_sectors[-1]['sector'].insert(0, ts.technical_sector or "")
            self.tech_sectors[-1]['days'].insert(0, ts.participation_days or "")

        for js in engineer.job_sector_participation:
            self.add_job_sector()
            self.job_sectors[-1]['job'].insert(0, js.job or "")
            self.job_sectors[-1]['days'].insert(0, js.participation_days or "")

        for sf in engineer.specialized_field_participation:
            self.add_specialized_field()
            self.specialized_fields[-1]['field'].insert(0, sf.specialized_field or "")
            self.specialized_fields[-1]['days'].insert(0, sf.participation_days or "")

        for ct in engineer.construction_type_participation:
            self.add_construction_type()
            self.construction_types[-1]['type'].insert(0, ct.construction_type or "")
            self.construction_types[-1]['days'].insert(0, ct.participation_days or "")

        for train in engineer.education_and_training:
            self.add_training()
            self.trainings[-1]['period'].insert(0, train.training_period or "")
            self.trainings[-1]['course'].insert(0, train.course_name or "")
            self.trainings[-1]['institution'].insert(0, train.institution_name or "")
            self.trainings[-1]['completion'].insert(0, train.completion_number or "")
            self.trainings[-1]['field'].insert(0, train.training_field or "")

        for award in engineer.awards:
            self.add_award()
            if award.date:
                self.awards[-1]['date'].set_date(award.date)
            self.awards[-1]['type'].insert(0, award.type_and_basis or "")
            self.awards[-1]['institution'].insert(0, award.awarding_institution or "")

        for sanction in engineer.sanctions:
            self.add_sanction()
            self.sanctions[-1]['points'].insert(0, sanction.penalty_points or "")
            if sanction.date:
                self.sanctions[-1]['date'].set_date(sanction.date)
            self.sanctions[-1]['type'].insert(0, sanction.type or "")
            self.sanctions[-1]['period'].insert(0, sanction.sanction_period or "")
            self.sanctions[-1]['basis'].insert(0, sanction.basis or "")
            self.sanctions[-1]['institution'].insert(0, sanction.sanctioning_institution or "")

        for wp in engineer.workplace:
            self.add_workplace()
            self.workplaces[-1]['period'].insert(0, wp.workplace_experience_period or "")
            self.workplaces[-1]['company'].insert(0, wp.workplace_company_name or "")

        for pd in engineer.project_details:
            self.add_project_detail()
            self.project_details[-1]['service'].insert(0, pd.service_name or "")
            self.project_details[-1]['project_type'].insert(0, pd.project_type or "")
            self.project_details[-1]['company'].insert(0, pd.company_name or "")
            self.project_details[-1]['contractor'].insert(0, pd.representative_contractor or "")
            if pd.contract_date:
                self.project_details[-1]['contract_date'].set_date(pd.contract_date)
    # TODO: Fix date of birth
    def save_engineer(self):
        try:
            # Basic fields
            self.engineer.name = self.name_input.get().strip()
            birth_date_str = self.birth_date_input.get_date()
            if birth_date_str:
                try:
                    birth_date = datetime.strptime(birth_date_str, "%m/%d/%Y").date()
                    self.engineer.date_of_birth = birth_date
                except ValueError as e:
                    print(f"Birth date: {birth_date_str}")
                    print(f"Error parsing birth date: {e}")
            self.engineer.address = self.address_input.get().strip()
            self.engineer.company_name = self.company_input.get().strip()
            self.engineer.position_and_rank = self.position_input.get().strip()
            self.engineer.responsible_technical_manager = self.responsible_technical_manager.get().strip()
            self.engineer.experience = self.experience.get("1.0", "end-1c").strip()
            self.engineer.field_name = self.field_name.get("1.0", "end-1c").strip()
            self.engineer.evaluation_target = self.evaluation_target.get().strip()
            self.engineer.pdf_file = self.pdf_file_path.get().strip()
            self.engineer.selected = self.selected_var.get()

            # Relationships
            self.engineer.technical_grades.clear()
            for grade in self.tech_grades:
                if all(grade[k].get().strip() for k in ['type', 'field', 'grade']):
                    self.engineer.technical_grades.append(TechnicalGrade(
                        grade_type=grade['type'].get().strip(),
                        field=grade['field'].get().strip(),
                        grade=grade['grade'].get().strip()
                    ))

            self.engineer.technical_qualifications.clear()
            for qual in self.qualifications:
                if qual['title'].get().strip():
                    self.engineer.technical_qualifications.append(Qualification(
                        title=qual['title'].get().strip(),
                        acquisition_date=qual['date'].get_date(),
                        registration_number=qual['reg_num'].get().strip()
                    ))

            self.engineer.education.clear()
            for edu in self.education:
                if edu['school'].get().strip():
                    self.engineer.education.append(Education(
                        graduation_date=edu['grad_date'].get_date(),
                        school_name=edu['school'].get().strip(),
                        major=edu['major'].get().strip(),
                        degree=edu['degree'].get().strip()
                    ))

            self.engineer.technical_sector_participation.clear()
            for ts in self.tech_sectors:
                if ts['sector'].get().strip():
                    self.engineer.technical_sector_participation.append(TechnicalSectorParticipation(
                        technical_sector=ts['sector'].get().strip(),
                        participation_days=ts['days'].get().strip()
                    ))

            self.engineer.job_sector_participation.clear()
            for js in self.job_sectors:
                if js['job'].get().strip():
                    self.engineer.job_sector_participation.append(JobSectorParticipation(
                        job=js['job'].get().strip(),
                        participation_days=js['days'].get().strip()
                    ))

            self.engineer.specialized_field_participation.clear()
            for sf in self.specialized_fields:
                if sf['field'].get().strip():
                    self.engineer.specialized_field_participation.append(SpecializedFieldParticipation(
                        specialized_field=sf['field'].get().strip(),
                        participation_days=sf['days'].get().strip()
                    ))

            self.engineer.construction_type_participation.clear()
            for ct in self.construction_types:
                if ct['type'].get().strip():
                    self.engineer.construction_type_participation.append(ConstructionTypeParticipation(
                        construction_type=ct['type'].get().strip(),
                        participation_days=ct['days'].get().strip()
                    ))

            self.engineer.education_and_training.clear()
            for train in self.trainings:
                if train['course'].get().strip():
                    self.engineer.education_and_training.append(EducationAndTraining(
                        training_period=train['period'].get().strip(),
                        course_name=train['course'].get().strip(),
                        institution_name=train['institution'].get().strip(),
                        completion_number=train['completion'].get().strip(),
                        training_field=train['field'].get().strip()
                    ))

            self.engineer.awards.clear()
            for award in self.awards:
                if award['type'].get().strip():
                    self.engineer.awards.append(Award(
                        date=award['date'].get_date(),
                        type_and_basis=award['type'].get().strip(),
                        awarding_institution=award['institution'].get().strip()
                    ))

            self.engineer.sanctions.clear()
            for sanction in self.sanctions:
                if sanction['type'].get().strip():
                    self.engineer.sanctions.append(Sanction(
                        penalty_points=sanction['points'].get().strip(),
                        date=sanction['date'].get_date(),
                        type=sanction['type'].get().strip(),
                        sanction_period=sanction['period'].get().strip(),
                        basis=sanction['basis'].get().strip(),
                        sanctioning_institution=sanction['institution'].get().strip()
                    ))

            self.engineer.workplace.clear()
            for wp in self.workplaces:
                if wp['company'].get().strip():
                    self.engineer.workplace.append(Workplace(
                        workplace_experience_period=wp['period'].get().strip(),
                        workplace_company_name=wp['company'].get().strip()
                    ))

            self.engineer.project_details.clear()
            for pd in self.project_details:
                if pd['service'].get().strip():
                    self.engineer.project_details.append(ProjectDetail(
                        service_name=pd['service'].get().strip(),
                        project_type=pd['project_type'].get().strip(),
                        company_name=pd['company'].get().strip(),
                        representative_contractor=pd['contractor'].get().strip(),
                        contract_date=pd['contract_date'].get_date()
                    ))

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

    def _upload_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            self.pdf_file_path.set(file_path)