import customtkinter as ctk
from tkinter import filedialog
from src.services.notification import notification # Import notification service
from src.models.engineer import (
    Engineer, TechnicalGrade, Qualification, Education, TechnicalSectorParticipation,
    JobSectorParticipation, SpecializedFieldParticipation, ConstructionTypeParticipation,
    EducationAndTraining, Award, Sanction, Workplace, ProjectDetail
)
from src.widgets.date_picker import DatePicker
from datetime import datetime
import traceback # Import traceback for error logging

class EngineerDialog(ctk.CTkToplevel):
    def __init__(self, session, engineer=None, on_save=None):
        super().__init__()
        self.session = session
        # If editing, use the existing engineer; otherwise, create a new one
        self.engineer = engineer if engineer else Engineer()
        self.on_save = on_save # Callback function to refresh parent table
        self.title("Edit Engineer" if engineer else "Add Engineer")
        self.geometry("1120x800") # Adjust size as needed

        # Initialize lists to hold dictionaries of widgets for dynamic sections
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

        # Dictionary to store the container frame for each dynamic section
        self.input_containers = {}

        # Main scrollable frame to hold all content
        self.container = ctk.CTkScrollableFrame(self)
        self.container.pack(padx=20, pady=20, fill="both", expand=True)
        # Configure column 1 (where widgets are placed) to expand
        self.container.grid_columnconfigure(1, weight=1)

        row = 0

        # --- Basic Information Section ---
        row = self.create_section_header(self.container, "Basic Information", row)

        # Name and Birth Date (Side-by-side)
        name_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        name_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=2) # Reduced pady
        name_frame.grid_columnconfigure(1, weight=1) # Name entry expands
        name_frame.grid_columnconfigure(3, weight=0) # Date picker less expansion
        ctk.CTkLabel(name_frame, text="Name", width=150, anchor='w').grid(row=0, column=0, padx=5, sticky='w')
        self.name_input = ctk.CTkEntry(name_frame)
        self.name_input.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(name_frame, text="Birth Date", width=100, anchor='w').grid(row=0, column=2, padx=(20, 5), sticky='w') # Add padding before label
        self.birth_date_input = DatePicker(name_frame) # Assuming DatePicker handles its layout
        self.birth_date_input.grid(row=0, column=3, padx=5, sticky="w")
        row += 1

        # Address
        self.address_input = self.create_entry_row(self.container, "Address", row)
        row += 1

        # Company Name and Position (Side-by-side)
        company_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        company_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=2) # Reduced pady
        company_frame.grid_columnconfigure(1, weight=1) # Company entry expands
        company_frame.grid_columnconfigure(3, weight=1) # Position entry expands
        ctk.CTkLabel(company_frame, text="Company Name", width=150, anchor='w').grid(row=0, column=0, padx=5, sticky='w')
        self.company_input = ctk.CTkEntry(company_frame)
        self.company_input.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(company_frame, text="Position and Rank", width=100, anchor='w').grid(row=0, column=2, padx=(20, 5), sticky='w') # Add padding
        self.position_input = ctk.CTkEntry(company_frame)
        self.position_input.grid(row=0, column=3, padx=5, sticky="ew")
        row += 1

        # Other Basic Info Fields
        self.responsible_technical_manager = self.create_entry_row(self.container, "Responsible Technical Manager", row)
        row += 1
        # Corrected: Use distinct variable name for the 'Field Name' entry
        self.field_name_input = self.create_entry_row(self.container, "Field Name", row)
        row += 1
        self.experience = self.create_textbox_row(self.container, "Experience Summary", row, height=60) # Adjusted height
        row += 1
        # Corrected: Use distinct variable name for the 'Expertise Area' textbox
        self.expertise_area_input = self.create_textbox_row(self.container, "Expertise Area", row, height=60) # Adjusted height
        # Note: Expertise Area is not saved by default as it's not in the Engineer model
        row += 1
        self.evaluation_target = self.create_entry_row(self.container, "Evaluation Target", row)
        row += 1

        # PDF File Upload
        pdf_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        pdf_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=2) # Reduced pady
        pdf_frame.grid_columnconfigure(1, weight=1) # Allow entry to expand
        ctk.CTkLabel(pdf_frame, text="PDF File Path", width=150, anchor='w').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pdf_file_path = ctk.StringVar()
        pdf_entry = ctk.CTkEntry(pdf_frame, textvariable=self.pdf_file_path, state="readonly") # Show path
        pdf_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.pdf_file_button = ctk.CTkButton(pdf_frame, text="Browse...", command=self._upload_pdf, width=80)
        self.pdf_file_button.grid(row=0, column=2, padx=5, pady=5)
        row += 1

        # Selected Checkbox
        selected_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        selected_frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2) # Reduced pady
        ctk.CTkLabel(selected_frame, text="Selected", width=150, anchor='w').grid(row=0, column=0, padx=5)
        self.selected_var = ctk.BooleanVar(value=False)
        self.selected_checkbox = ctk.CTkCheckBox(selected_frame, text="", variable=self.selected_var)
        self.selected_checkbox.grid(row=0, column=1, padx=5)
        row += 1

        # --- Relationship Sections ---
        # Reverted to explicit calls similar to original code, but within try-except
        try:
            row = self.add_relationship_section_explicit("Technical Grades", row, self.add_tech_grade, self._create_tech_grade_fields)
            row = self.add_relationship_section_explicit("Technical Qualifications", row, self.add_qualification, self._create_qualification_fields)
            row = self.add_relationship_section_explicit("Education", row, self.add_education, self._create_education_fields)
            row = self.add_relationship_section_explicit("Technical Sector Participation", row, self.add_tech_sector, self._create_tech_sector_fields)
            row = self.add_relationship_section_explicit("Job Sector Participation", row, self.add_job_sector, self._create_job_sector_fields)
            row = self.add_relationship_section_explicit("Specialized Field Participation", row, self.add_specialized_field, self._create_specialized_field_fields)
            row = self.add_relationship_section_explicit("Construction Type Participation", row, self.add_construction_type, self._create_construction_type_fields)
            row = self.add_relationship_section_explicit("Education and Training", row, self.add_training, self._create_training_fields)
            row = self.add_relationship_section_explicit("Awards", row, self.add_award, self._create_award_fields)
            row = self.add_relationship_section_explicit("Sanctions", row, self.add_sanction, self._create_sanction_fields)
            row = self.add_relationship_section_explicit("Workplace", row, self.add_workplace, self._create_workplace_fields)
            row = self.add_relationship_section_explicit("Project Details", row, self.add_project_detail, self._create_project_detail_fields)
        except Exception as e_init:
            print(f"--- ERROR DURING DIALOG INIT (Explicit Sections) ---")
            print(f"Error creating relationship sections: {e_init}")
            traceback.print_exc()
            print(f"--- END ERROR ---")
            notification.show_error(f"Error initializing dialog sections: {e_init}")


        # --- Buttons (Save/Cancel) ---
        buttons_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        buttons_frame.grid(row=row, column=1, sticky="e", pady=20, padx=5) # Aligned to right
        ctk.CTkButton(
            buttons_frame, text="Cancel", command=self.destroy, width=100, fg_color="#E74C3C", hover_color="#C0392B"
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            buttons_frame, text="Save", command=self.save_engineer, width=100
        ).pack(side="left", padx=10)

        # Load existing engineer data if provided (editing mode)
        if engineer:
            try:
                self.load_engineer_data(engineer) # Use the corrected load_engineer_data
            except Exception as e_load:
                print(f"--- ERROR DURING DATA LOAD ---"); traceback.print_exc(); print(f"--- END ERROR ---")
                notification.show_error(f"Error loading engineer data: {e_load}")

        # Make the dialog modal
        self.transient(self.master)
        self.grab_set()
        self.after(100, self.name_input.focus_set) # Focus first field

    # --- Helper Methods for UI Creation ---
    # create_section_header, create_entry_row, create_textbox_row remain the same as previous version

    def create_section_header(self, parent, text, row):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=0, pady=(15, 2))
        label = ctk.CTkLabel(header_frame, text=text, font=("Arial", 14, "bold"), anchor='w')
        label.pack(side="left", padx=5)
        return row + 1

    def create_entry_row(self, parent, label, row):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=label, width=150, anchor='w').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry = ctk.CTkEntry(frame)
        entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        return entry

    def create_textbox_row(self, parent, label, row, height):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, width=150, anchor='nw').grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        textbox = ctk.CTkTextbox(frame, height=height)
        textbox.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        return textbox

    # --- Reverted add_relationship_section_explicit ---
    # This version explicitly calls the correct _create_*_fields method
    def add_relationship_section_explicit(self, title, row, add_method, create_fields_method):
        # Outer frame with border
        section_outer_frame = ctk.CTkFrame(self.container, border_width=1, border_color="gray50")
        section_outer_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=5, pady=10)
        section_outer_frame.grid_columnconfigure(0, weight=1)

        # Header frame
        header_frame = ctk.CTkFrame(section_outer_frame, fg_color="gray20")
        header_frame.pack(fill="x", padx=0, pady=0)
        ctk.CTkLabel(header_frame, text=title, font=("Arial", 13, "bold"), anchor='w').pack(side="left", padx=10, pady=5)
        ctk.CTkButton(
            header_frame, text=f"Add", command=add_method, fg_color="#2980B9",
            hover_color="#2573A7", height=28, width=60
        ).pack(side="right", padx=10, pady=5)

        # Content container
        input_container = ctk.CTkFrame(section_outer_frame, fg_color="transparent")
        input_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.input_containers[title] = input_container

        # Create initial fields only if creating new OR if editing and relation list is empty/None
        try:
            relation_attr = title.lower().replace(' ', '_')
            relation_data = getattr(self.engineer, relation_attr, None) if self.engineer else None
            if self.engineer is None or not relation_data:
                 print(f"Creating initial fields EXPLICITLY for: {title}") # Debug print
                 create_fields_method(input_container) # Create one initial empty row
            # else: # Load engineer data will handle adding rows for existing data
                 # print(f"Skipping initial fields EXPLICITLY for {title}, data exists.") # Debug print
        except Exception as e_create_initial:
            print(f"--- ERROR CREATING INITIAL FIELDS EXPLICITLY for {title} ---")
            print(f"Error: {e_create_initial}"); traceback.print_exc(); print(f"--- END ERROR ---")

        return row + 1

    # --- Reverted Explicit _create_*_fields Methods ---
    # These now manage appending to self lists and setup remove command correctly

    def _create_tech_grade_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2) # Use padx=0 for internal frames

        type_entry = ctk.CTkEntry(frame, placeholder_text="Grade Type", height=30)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")

        field_entry = ctk.CTkEntry(frame, placeholder_text="Field", height=30)
        field_entry.pack(side="left", padx=5, expand=True, fill="x")

        grade_options = ["Beginner", "Intermediate", "Advanced", "Special", "Technician"]
        grade_dropdown = ctk.CTkComboBox(frame, values=grade_options, state="readonly", height=30, width=120)
        grade_dropdown.set(grade_options[0]) # Default selection
        grade_dropdown.pack(side="left", padx=5, expand=False)

        # Store widgets in a dictionary
        fields = {'frame': frame, 'type': type_entry, 'field': field_entry, 'grade': grade_dropdown}
        self.tech_grades.append(fields) # Add dict to list

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            # Pass the dictionary and the list to remove_field
            command=lambda f=fields: self._remove_field(f, self.tech_grades)
        )
        remove_btn.pack(side="right", padx=5)
        return fields # Return the dict

    def _create_qualification_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        title_entry = ctk.CTkEntry(frame, placeholder_text="Title", height=30)
        title_entry.pack(side="left", padx=5, expand=True, fill="x")

        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)

        reg_entry = ctk.CTkEntry(frame, placeholder_text="Reg Number", height=30)
        reg_entry.pack(side="left", padx=5, expand=True, fill="x")

        fields = {'frame': frame, 'title': title_entry, 'date': date_entry, 'reg_num': reg_entry}
        self.qualifications.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.qualifications)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_education_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        grad_date_entry = DatePicker(frame)
        grad_date_entry.pack(side="left", padx=5)

        school_entry = ctk.CTkEntry(frame, placeholder_text="School Name", height=30)
        school_entry.pack(side="left", padx=5, expand=True, fill="x")

        major_entry = ctk.CTkEntry(frame, placeholder_text="Major", height=30)
        major_entry.pack(side="left", padx=5, expand=True, fill="x")

        degree_entry = ctk.CTkEntry(frame, placeholder_text="Degree", height=30, width=100)
        degree_entry.pack(side="left", padx=5, expand=False)

        fields = {'frame': frame, 'grad_date': grad_date_entry, 'school': school_entry, 'major': major_entry, 'degree': degree_entry}
        self.education.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.education)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_tech_sector_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        sector_entry = ctk.CTkEntry(frame, placeholder_text="Technical Sector", height=30)
        sector_entry.pack(side="left", padx=5, expand=True, fill="x")

        days_entry = ctk.CTkEntry(frame, placeholder_text="Days", height=30, width=80)
        days_entry.pack(side="left", padx=5, expand=False)

        fields = {'frame': frame, 'sector': sector_entry, 'days': days_entry}
        self.tech_sectors.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.tech_sectors)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_job_sector_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        job_entry = ctk.CTkEntry(frame, placeholder_text="Job", height=30)
        job_entry.pack(side="left", padx=5, expand=True, fill="x")

        days_entry = ctk.CTkEntry(frame, placeholder_text="Days", height=30, width=80)
        days_entry.pack(side="left", padx=5, expand=False)

        fields = {'frame': frame, 'job': job_entry, 'days': days_entry}
        self.job_sectors.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.job_sectors)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_specialized_field_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        field_entry = ctk.CTkEntry(frame, placeholder_text="Specialized Field", height=30)
        field_entry.pack(side="left", padx=5, expand=True, fill="x")

        days_entry = ctk.CTkEntry(frame, placeholder_text="Days", height=30, width=80)
        days_entry.pack(side="left", padx=5, expand=False)

        fields = {'frame': frame, 'field': field_entry, 'days': days_entry}
        self.specialized_fields.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.specialized_fields)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_construction_type_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        type_entry = ctk.CTkEntry(frame, placeholder_text="Construction Type", height=30)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")

        days_entry = ctk.CTkEntry(frame, placeholder_text="Days", height=30, width=80)
        days_entry.pack(side="left", padx=5, expand=False)

        fields = {'frame': frame, 'type': type_entry, 'days': days_entry}
        self.construction_types.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.construction_types)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_training_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        period_entry = ctk.CTkEntry(frame, placeholder_text="Period", height=30, width=100)
        period_entry.pack(side="left", padx=5, expand=False)
        course_entry = ctk.CTkEntry(frame, placeholder_text="Course Name", height=30)
        course_entry.pack(side="left", padx=5, expand=True, fill="x")
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Institution", height=30)
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")
        completion_entry = ctk.CTkEntry(frame, placeholder_text="Comp#", height=30, width=80)
        completion_entry.pack(side="left", padx=5, expand=False)
        field_entry = ctk.CTkEntry(frame, placeholder_text="Field", height=30)
        field_entry.pack(side="left", padx=5, expand=True, fill="x")

        fields = {'frame': frame, 'period': period_entry, 'course': course_entry, 'institution': institution_entry, 'completion': completion_entry, 'field': field_entry}
        self.trainings.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.trainings)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_award_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        type_entry = ctk.CTkEntry(frame, placeholder_text="Type & Basis", height=30)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Institution", height=30)
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")

        fields = {'frame': frame, 'date': date_entry, 'type': type_entry, 'institution': institution_entry}
        self.awards.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.awards)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_sanction_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        points_entry = ctk.CTkEntry(frame, placeholder_text="Points", height=30, width=60)
        points_entry.pack(side="left", padx=5, expand=False)
        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        type_entry = ctk.CTkEntry(frame, placeholder_text="Type", height=30)
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        period_entry = ctk.CTkEntry(frame, placeholder_text="Period", height=30, width=100)
        period_entry.pack(side="left", padx=5, expand=False)
        basis_entry = ctk.CTkEntry(frame, placeholder_text="Basis", height=30)
        basis_entry.pack(side="left", padx=5, expand=True, fill="x")
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Institution", height=30)
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")

        fields = {'frame': frame, 'points': points_entry, 'date': date_entry, 'type': type_entry, 'period': period_entry, 'basis': basis_entry, 'institution': institution_entry}
        self.sanctions.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.sanctions)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_workplace_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        period_entry = ctk.CTkEntry(frame, placeholder_text="Period", height=30)
        period_entry.pack(side="left", padx=5, expand=True, fill="x")
        company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name", height=30)
        company_entry.pack(side="left", padx=5, expand=True, fill="x")

        fields = {'frame': frame, 'period': period_entry, 'company': company_entry}
        self.workplaces.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.workplaces)
        )
        remove_btn.pack(side="right", padx=5)
        return fields

    def _create_project_detail_fields(self, container):
        frame = ctk.CTkFrame(container, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)

        service_entry = ctk.CTkEntry(frame, placeholder_text="Service Name", height=30)
        service_entry.pack(side="left", padx=5, expand=True, fill="x")
        project_type_entry = ctk.CTkEntry(frame, placeholder_text="Project Type", height=30)
        project_type_entry.pack(side="left", padx=5, expand=True, fill="x")
        company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name", height=30)
        company_entry.pack(side="left", padx=5, expand=True, fill="x")
        contractor_entry = ctk.CTkEntry(frame, placeholder_text="Contractor", height=30)
        contractor_entry.pack(side="left", padx=5, expand=True, fill="x")
        contract_date_entry = DatePicker(frame)
        contract_date_entry.pack(side="left", padx=5)

        fields = {'frame': frame, 'service': service_entry, 'project_type': project_type_entry, 'company': company_entry, 'contractor': contractor_entry, 'contract_date': contract_date_entry}
        self.project_details.append(fields)

        remove_btn = ctk.CTkButton(
            frame, text="✕", width=30, height=30, fg_color="#E74C3C", hover_color="#C0392B",
            command=lambda f=fields: self._remove_field(f, self.project_details)
        )
        remove_btn.pack(side="right", padx=5)
        return fields


    # --- Add Methods (called by Add buttons) ---
    # These now just call the explicit create methods directly
    def add_tech_grade(self): self._create_tech_grade_fields(self.input_containers["Technical Grades"])
    def add_qualification(self): self._create_qualification_fields(self.input_containers["Technical Qualifications"])
    def add_education(self): self._create_education_fields(self.input_containers["Education"])
    def add_tech_sector(self): self._create_tech_sector_fields(self.input_containers["Technical Sector Participation"])
    def add_job_sector(self): self._create_job_sector_fields(self.input_containers["Job Sector Participation"])
    def add_specialized_field(self): self._create_specialized_field_fields(self.input_containers["Specialized Field Participation"])
    def add_construction_type(self): self._create_construction_type_fields(self.input_containers["Construction Type Participation"])
    def add_training(self): self._create_training_fields(self.input_containers["Education and Training"])
    def add_award(self): self._create_award_fields(self.input_containers["Awards"])
    def add_sanction(self): self._create_sanction_fields(self.input_containers["Sanctions"])
    def add_workplace(self): self._create_workplace_fields(self.input_containers["Workplace"])
    def add_project_detail(self): self._create_project_detail_fields(self.input_containers["Project Details"])

    # --- Load Engineer Data ---
    # Use the corrected version that works with explicit create methods
    def load_engineer_data(self, engineer):
        # Basic Info
        self.name_input.insert(0, engineer.name or "")
        if engineer.date_of_birth:
            self._set_datepicker_date(self.birth_date_input, engineer.date_of_birth)
        self.address_input.insert(0, engineer.address or "")
        self.company_input.insert(0, engineer.company_name or "") # Corrected field
        self.position_input.insert(0, engineer.position_and_rank or "") # Corrected field
        self.responsible_technical_manager.insert(0, engineer.responsible_technical_manager or "")
        self.experience.insert("1.0", engineer.experience or "")
        self.field_name_input.insert(0, engineer.field_name or "") # Corrected widget
        # Load expertise area if needed: self.expertise_area_input.insert("1.0", engineer.expertise_area or "")
        self.evaluation_target.insert(0, engineer.evaluation_target or "")
        self.pdf_file_path.set(engineer.pdf_file or "")
        self.selected_var.set(engineer.selected or False)

        # --- Helper to load relationship data (Works with explicit create methods) ---
        def load_relation_data(relation_attr, data_list, field_map, create_fields_method):
            title_key = relation_attr.replace('_', ' ').title()
            container = self.input_containers.get(title_key)
            if not container: print(f"Warning: Cont missing '{title_key}'"); return

            items = getattr(engineer, relation_attr, [])

            for widget_dict in data_list[:]: self._remove_field(widget_dict, data_list) # Clear UI

            if items:
                for item in items:
                    new_fields = create_fields_method(container) # Create new UI row explicitly
                    if not new_fields: continue
                    # Populate the newly created widgets
                    for model_attr, widget_key in field_map.items():
                        value = getattr(item, model_attr, None)
                        widget = new_fields.get(widget_key)
                        if widget:
                            if isinstance(widget, DatePicker): self._set_datepicker_date(widget, value)
                            elif isinstance(widget, ctk.CTkComboBox):
                                str_value = str(value) if value is not None else ""; opts = widget.cget('values')
                                if str_value in opts: widget.set(str_value)
                                elif opts: widget.set(opts[0])
                            elif isinstance(widget, ctk.CTkEntry):
                                widget.delete(0, ctk.END); widget.insert(0, str(value) if value is not None else "")
            else:
                 # Create one empty row if no items exist
                 create_fields_method(container)

        # --- Load Relationships (Using Explicit Create Methods) ---
        load_relation_data('technical_grades', self.tech_grades,
                           {'grade_type': 'type', 'field': 'field', 'grade': 'grade'}, self._create_tech_grade_fields)
        load_relation_data('technical_qualifications', self.qualifications,
                           {'title': 'title', 'acquisition_date': 'date', 'registration_number': 'reg_num'}, self._create_qualification_fields)
        load_relation_data('education', self.education,
                           {'graduation_date': 'grad_date', 'school_name': 'school', 'major': 'major', 'degree': 'degree'}, self._create_education_fields)
        load_relation_data('technical_sector_participation', self.tech_sectors,
                           {'technical_sector': 'sector', 'participation_days': 'days'}, self._create_tech_sector_fields)
        load_relation_data('job_sector_participation', self.job_sectors,
                           {'job': 'job', 'participation_days': 'days'}, self._create_job_sector_fields)
        load_relation_data('specialized_field_participation', self.specialized_fields,
                           {'specialized_field': 'field', 'participation_days': 'days'}, self._create_specialized_field_fields)
        load_relation_data('construction_type_participation', self.construction_types,
                           {'construction_type': 'type', 'participation_days': 'days'}, self._create_construction_type_fields)
        load_relation_data('education_and_training', self.trainings,
                           {'training_period': 'period', 'course_name': 'course', 'institution_name': 'institution',
                            'completion_number': 'completion', 'training_field': 'field'}, self._create_training_fields)
        load_relation_data('awards', self.awards,
                           {'date': 'date', 'type_and_basis': 'type', 'awarding_institution': 'institution'}, self._create_award_fields)
        load_relation_data('sanctions', self.sanctions,
                           {'penalty_points': 'points', 'date': 'date', 'type': 'type', 'sanction_period': 'period',
                            'basis': 'basis', 'sanctioning_institution': 'institution'}, self._create_sanction_fields)
        load_relation_data('workplace', self.workplaces,
                           {'workplace_experience_period': 'period', 'workplace_company_name': 'company'}, self._create_workplace_fields)
        load_relation_data('project_details', self.project_details,
                           {'service_name': 'service', 'project_type': 'project_type', 'company_name': 'company',
                            'representative_contractor': 'contractor', 'contract_date': 'contract_date'}, self._create_project_detail_fields)

    # --- Set DatePicker Date Helper ---
    # (Keep the improved _set_datepicker_date from previous version)
    def _set_datepicker_date(self, datepicker_widget, date_value):
        """Safely sets the date on a DatePicker widget."""
        if not isinstance(datepicker_widget, DatePicker): return
        if date_value:
             try:
                 if isinstance(date_value, datetime): date_value = date_value.date()
                 if hasattr(date_value, 'year') and hasattr(date_value, 'month') and hasattr(date_value, 'day'):
                     if hasattr(datepicker_widget, 'select_date'):
                        datepicker_widget.current_year = date_value.year; datepicker_widget.current_month = date_value.month
                        datepicker_widget.select_date(date_value.day)
                     else: # Fallback
                         datepicker_widget.date_entry.configure(state='normal'); datepicker_widget.date_entry.delete(0, ctk.END)
                         datepicker_widget.date_entry.insert(0, date_value.strftime(datepicker_widget.date_format))
                         if not datepicker_widget.allow_manual_input: datepicker_widget.date_entry.configure(state='disabled')
                 else: print(f"Warn: Invalid date type: {type(date_value)}")
             except Exception as e: print(f"Err setting date '{date_value}': {e}")
        else: # Clear datepicker
            try:
                datepicker_widget.date_entry.configure(state='normal'); datepicker_widget.date_entry.delete(0, ctk.END)
                if not datepicker_widget.allow_manual_input: datepicker_widget.date_entry.configure(state='disabled')
                if hasattr(datepicker_widget, 'selected_date'): datepicker_widget.selected_date = None
            except Exception as e: print(f"Err clearing datepicker: {e}")


    # --- Remove Field ---
    def _remove_field(self, fields_dict, data_list):
        """Removes a row of fields from UI and the tracking list."""
        if fields_dict in data_list:
            data_list.remove(fields_dict)
        frame = fields_dict.get('frame')
        if frame and frame.winfo_exists():
            frame.destroy()

    # --- Save Engineer Data ---
    # Use the fully corrected save_engineer method from previous responses
    # It handles correct field names, data types, date parsing, notifications etc.
    def save_engineer(self):
        try:
            # --- Basic information ---
            self.engineer.name = self.name_input.get().strip()
            birth_date_str = self.birth_date_input.get_date()
            birth_date_obj = None
            if birth_date_str:
                try: birth_date_obj = datetime.strptime(birth_date_str, self.birth_date_input.date_format).date()
                except (ValueError, TypeError): notification.show_error(f"Invalid Birth Date: {birth_date_str}"); return
            self.engineer.date_of_birth = birth_date_obj
            self.engineer.address = self.address_input.get().strip()
            self.engineer.company_name = self.company_input.get().strip() # Correct
            self.engineer.position_and_rank = self.position_input.get().strip() # Correct
            self.engineer.responsible_technical_manager = self.responsible_technical_manager.get().strip()
            self.engineer.experience = self.experience.get("1.0", "end-1c").strip()
            self.engineer.field_name = self.field_name_input.get().strip() # Correct
            self.engineer.evaluation_target = self.evaluation_target.get().strip()
            self.engineer.pdf_file = self.pdf_file_path.get().strip()
            self.engineer.selected = self.selected_var.get()

            # --- Helper to Save Relationships ---
            def save_relation(relation_attr, data_list, model_class, field_map):
                target_list = getattr(self.engineer, relation_attr, [])
                if target_list is None: target_list = []; setattr(self.engineer, relation_attr, target_list)
                target_list.clear()
                for item_widgets in data_list:
                    kwargs = {}; has_data = False
                    for model_attr, widget_key in field_map.items():
                        widget = item_widgets.get(widget_key); value_to_save = None
                        if isinstance(widget, DatePicker):
                            date_str = widget.get_date()
                            if date_str:
                                try: value_to_save = datetime.strptime(date_str, widget.date_format).date(); has_data = True
                                except (ValueError, TypeError): value_to_save = None
                        elif isinstance(widget, ctk.CTkComboBox): value = widget.get();
                        elif isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)): value = widget.get().strip() if isinstance(widget, ctk.CTkEntry) else widget.get("1.0", "end-1c").strip()
                        else: value = None # Should not happen with current setup

                        if value_to_save is None and value: value_to_save = value; has_data = True # Capture value from Entry/Combo/Text

                        if model_attr in ['participation_days', 'penalty_points']: kwargs[model_attr] = str(value_to_save) if value_to_save is not None else ""
                        elif value_to_save is not None: kwargs[model_attr] = value_to_save
                    if has_data:
                        try: target_list.append(model_class(**kwargs))
                        except TypeError as te: print(f"Err creating {model_class.__name__} ({kwargs}): {te}")

            # --- Save Relationships using Helper ---
            save_relation('technical_grades', self.tech_grades, TechnicalGrade,
                          {'grade_type': 'type', 'field': 'field', 'grade': 'grade'})
            save_relation('technical_qualifications', self.qualifications, Qualification,
                          {'title': 'title', 'acquisition_date': 'date', 'registration_number': 'reg_num'})
            save_relation('education', self.education, Education,
                          {'graduation_date': 'grad_date', 'school_name': 'school', 'major': 'major', 'degree': 'degree'})
            save_relation('technical_sector_participation', self.tech_sectors, TechnicalSectorParticipation,
                          {'technical_sector': 'sector', 'participation_days': 'days'})
            save_relation('job_sector_participation', self.job_sectors, JobSectorParticipation,
                          {'job': 'job', 'participation_days': 'days'})
            save_relation('specialized_field_participation', self.specialized_fields, SpecializedFieldParticipation,
                          {'specialized_field': 'field', 'participation_days': 'days'})
            save_relation('construction_type_participation', self.construction_types, ConstructionTypeParticipation,
                          {'construction_type': 'type', 'participation_days': 'days'})
            save_relation('education_and_training', self.trainings, EducationAndTraining,
                          {'training_period': 'period', 'course_name': 'course', 'institution_name': 'institution',
                           'completion_number': 'completion', 'training_field': 'field'}) # Added completion_number
            save_relation('awards', self.awards, Award,
                          {'date': 'date', 'type_and_basis': 'type', 'awarding_institution': 'institution'}) # Corrected mapping
            save_relation('sanctions', self.sanctions, Sanction,
                          {'penalty_points': 'points', 'date': 'date', 'type': 'type',
                           'sanction_period': 'period', 'basis': 'basis',
                           'sanctioning_institution': 'institution'}) # Corrected mappings
            save_relation('workplace', self.workplaces, Workplace,
                          {'workplace_experience_period': 'period', 'workplace_company_name': 'company'})
            save_relation('project_details', self.project_details, ProjectDetail,
                          {'service_name': 'service', 'project_type': 'project_type',
                           'company_name': 'company', 'representative_contractor': 'contractor',
                           'contract_date': 'contract_date'}) # Corrected mappings
            # --- End Save Relationships ---

            self.session.add(self.engineer)
            self.session.commit()
            if self.on_save: self.on_save()
            notification.show_success("Engineer data saved successfully")
            self.destroy()
        except Exception as e:
            notification.show_error(f"Error saving: {str(e)}"); print(f"--- Save Error ---"); traceback.print_exc(); print(f"--- End ---")
            self.session.rollback()

    # --- Upload PDF ---
    def _upload_pdf(self):
        file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF Files", "*.pdf")])
        if file_path: self.pdf_file_path.set(file_path)