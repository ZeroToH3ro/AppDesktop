# engineer_detail.py
import customtkinter as ctk
import os # For potential future use (like opening PDF)

# --- UI Configuration ---
COLOR_BACKGROUND = "#242424" # Main background
COLOR_FRAME_BG = "#2C3E50"   # Background for section content frames
COLOR_ITEM_BG = "#34495E"    # Background for list items (like qualifications)
COLOR_TEXT = "#EAEAEA"       # Default text color
COLOR_SECTION_TITLE = "#1ABC9C" # Color for section titles
COLOR_LABEL = "#B0BEC5"      # Color for field labels (slightly dimmer)

FONT_TITLE = ("Arial Bold", 16)
FONT_SECTION = ("Arial Bold", 14)
FONT_LABEL = ("Arial Bold", 12)
FONT_VALUE = ("Arial", 12)

PADDING_SECTION_Y = (15, 5) # Padding above/below section titles
PADDING_FRAME_Y = 5         # Padding above/below section content frames
PADDING_FRAME_X = 10
PADDING_ITEM_Y = 5          # Padding for items within list sections
PADDING_ITEM_X = 10
PADDING_FIELD_Y = 2         # Vertical padding between fields in a section
PADDING_FIELD_X = 5

class EngineerDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, engineer):
        super().__init__(parent)

        # --- Window setup ---
        self.title(f"Engineer Details - {engineer.name}")
        self.geometry("900x750")
        # self.configure(fg_color=COLOR_BACKGROUND) # Set main background if needed

        # --- Create main scrollable frame ---
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            # fg_color=COLOR_BACKGROUND, # Inherit or set explicitly
            scrollbar_button_color=COLOR_FRAME_BG,
            scrollbar_button_hover_color=COLOR_ITEM_BG
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1) # Allow content to expand horizontally

        current_row = 0 # Keep track of grid rows

        # --- Basic Information Section ---
        self.create_section("Basic Information", current_row)
        current_row += 1
        basic_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_FRAME_BG, corner_radius=10)
        basic_frame.grid(row=current_row, column=0, sticky="ew", padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y)
        basic_frame.grid_columnconfigure((0, 1), weight=1) # Make columns equal width
        current_row += 1

        # Left column
        left_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="ew", padx=(15, 5), pady=10)
        self.create_detail_field(left_frame, "Name:", engineer.name)
        self.create_detail_field(left_frame, "Birth Date:", engineer.date_of_birth)
        self.create_detail_field(left_frame, "Position:", engineer.position_and_rank)
        self.create_detail_field(left_frame, "Experience:", engineer.experience)
        self.create_detail_field(left_frame, "Evaluation Target:", engineer.evaluation_target)
        self.create_detail_field(left_frame, "PDF File:", engineer.pdf_file)

        # Right column
        right_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="ew", padx=(5, 15), pady=10)
        self.create_detail_field(right_frame, "Company:", engineer.company_name)
        self.create_detail_field(right_frame, "Address:", engineer.address)
        self.create_detail_field(right_frame, "Resp. Tech Manager:", engineer.responsible_technical_manager)
        self.create_detail_field(right_frame, "Field Name:", engineer.field_name)
        self.create_detail_field(right_frame, "Selected:", engineer.selected)

        # --- Technical Grades Section ---
        current_row = self.create_list_section(
            title="Technical Grades",
            items=engineer.technical_grades,
            item_formatter=lambda grade: f"{grade.grade_type} - {grade.field}: {grade.grade}",
            empty_message="No technical grades recorded.",
            start_row=current_row
        )

        # --- Qualifications Section ---
        current_row = self.create_item_detail_section(
            title="Qualifications",
            items=engineer.technical_qualifications,
            item_fields=[
                ("Title:", "title"),
                ("Acquisition Date:", "acquisition_date"),
                ("Reg. Number:", "registration_number")
            ],
            empty_message="No qualifications recorded.",
            start_row=current_row
        )

        # --- Education Section ---
        current_row = self.create_item_detail_section(
            title="Education",
            items=engineer.education,
            item_fields=[
                ("Graduation:", "graduation_date"),
                ("School Name:", "school_name"),
                ("Major:", "major"),
                ("Degree:", "degree")
            ],
            empty_message="No education history recorded.",
            start_row=current_row
        )

        # --- Workplace History Section ---
        current_row = self.create_item_detail_section(
            title="Workplace History",
            items=engineer.workplace,
            item_fields=[
                ("Period:", "workplace_experience_period"),
                ("Company:", "workplace_company_name")
            ],
            empty_message="No workplace history recorded.",
            start_row=current_row
        )

        # --- Education and Training Section ---
        current_row = self.create_item_detail_section(
            title="Education and Training",
            items=engineer.education_and_training,
            item_fields=[
                ("Period:", "training_period"),
                ("Course:", "course_name"),
                ("Institution:", "institution_name"),
                ("Completion No:", "completion_number"),
                ("Training Field:", "training_field")
            ],
            empty_message="No training recorded.",
            start_row=current_row
        )

        # --- Participation Details Section ---
        self.create_section("Participation Details", current_row)
        current_row += 1
        part_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_FRAME_BG, corner_radius=10)
        part_frame.grid(row=current_row, column=0, sticky="ew", padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y)
        current_row += 1
        has_participation = False
        part_row = 0
        if engineer.technical_sector_participation:
            has_participation = True
            self.create_detail_field(part_frame, "Technical Sector:", "", row=part_row, label_font=FONT_LABEL)
            part_row += 1
            for p in engineer.technical_sector_participation:
                 self.create_detail_field(part_frame, f"  • {p.technical_sector}", f"{p.participation_days} days", row=part_row)
                 part_row += 1
        if engineer.job_sector_participation:
            has_participation = True
            self.create_detail_field(part_frame, "Job Sector:", "", row=part_row, label_font=FONT_LABEL)
            part_row += 1
            for p in engineer.job_sector_participation:
                 self.create_detail_field(part_frame, f"  • {p.job}", f"{p.participation_days} days", row=part_row)
                 part_row += 1
        # ... Add specialized_field_participation and construction_type_participation similarly ...
        if not has_participation:
            no_data_label = ctk.CTkLabel(part_frame, text="No participation details recorded.", font=FONT_VALUE, text_color=COLOR_LABEL, anchor="w")
            no_data_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")


        # --- Awards Section ---
        current_row = self.create_item_detail_section(
            title="Awards",
            items=engineer.awards,
            item_fields=[
                ("Date:", "date"),
                ("Type/Basis:", "type_and_basis"),
                ("Institution:", "awarding_institution")
            ],
            empty_message="No awards recorded.",
            start_row=current_row
        )

        # --- Sanctions Section ---
        current_row = self.create_item_detail_section(
            title="Sanctions",
            items=engineer.sanctions,
            item_fields=[
                ("Date:", "date"),
                ("Type:", "type"),
                ("Points:", "penalty_points"),
                ("Period:", "sanction_period"),
                ("Basis:", "basis"),
                ("Institution:", "sanctioning_institution")
            ],
            empty_message="No sanctions recorded.",
            start_row=current_row
        )

        # --- Project Details Section ---
        current_row = self.create_item_detail_section(
            title="Project Details",
            items=engineer.project_details,
            item_fields=[
                ("Service Name:", "service_name"),
                ("Project Type:", "project_type"),
                ("Company:", "company_name"),
                ("Participation Period:", "participation_period"),
                ("Position:", "position"),
                ("Client:", "client")
                # Add more project fields if desired
            ],
            empty_message="No project details recorded.",
            start_row=current_row
        )


        # --- Close button ---
        close_btn = ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            height=35,
            width=100,
            font=FONT_LABEL
        )
        close_btn.pack(pady=(10, 15)) # Place below the scroll frame

        # --- Make dialog modal ---
        self.transient(self.master)
        self.grab_set()

    # --- Helper Methods ---

    def create_section(self, title, row):
        """Creates the section title label."""
        section_label = ctk.CTkLabel(
            self.main_frame,
            text=title,
            font=FONT_SECTION,
            anchor="w",
            text_color=COLOR_SECTION_TITLE
        )
        section_label.grid(row=row, column=0, sticky="w", padx=PADDING_FRAME_X, pady=PADDING_SECTION_Y)

    def create_detail_field(self, parent, label_text, value, row=None, label_font=FONT_LABEL, value_font=FONT_VALUE):
        """Creates a label-value pair within a parent frame."""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")

        # Use grid within the field_frame for alignment
        field_frame.grid_columnconfigure(0, weight=0) # Label column fixed width
        field_frame.grid_columnconfigure(1, weight=1) # Value column expands

        # Grid layout if row specified, pack otherwise
        if row is not None:
            field_frame.grid(row=row, column=0, sticky="ew", padx=PADDING_FIELD_X, pady=PADDING_FIELD_Y)
        else:
            field_frame.pack(fill="x", padx=PADDING_FIELD_X, pady=PADDING_FIELD_Y)

        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=label_font,
            width=160, # Fixed width for alignment
            anchor="w",
            text_color=COLOR_LABEL # Use distinct label color
        )
        label.grid(row=0, column=0, sticky="w")

        value_text = str(value) if value is not None else "N/A"
        value_label = ctk.CTkLabel(
            field_frame,
            text=value_text,
            font=value_font,
            anchor="w",
            wraplength=450, # Adjust wraplength as needed
            justify="left",
            text_color=COLOR_TEXT # Default text color for value
        )
        value_label.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def create_list_section(self, title, items, item_formatter, empty_message, start_row):
        """Creates a section for simple lists where each item is a single string."""
        self.create_section(title, start_row)
        start_row += 1
        list_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_FRAME_BG, corner_radius=10)
        list_frame.grid(row=start_row, column=0, sticky="ew", padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y)
        start_row += 1

        if items:
            for i, item in enumerate(items):
                item_text = item_formatter(item)
                item_label = ctk.CTkLabel(list_frame, text=item_text, font=FONT_VALUE, anchor="w", text_color=COLOR_TEXT)
                item_label.pack(fill="x", padx=15, pady=2) # Simpler packing for list items
        else:
            no_data_label = ctk.CTkLabel(list_frame, text=empty_message, font=FONT_VALUE, text_color=COLOR_LABEL, anchor="w")
            no_data_label.pack(fill="x", padx=15, pady=10) # Use pack for consistency

        return start_row

    def create_item_detail_section(self, title, items, item_fields, empty_message, start_row):
        """Creates a section where each item in a list has multiple details displayed in a sub-frame."""
        self.create_section(title, start_row)
        start_row += 1
        section_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_FRAME_BG, corner_radius=10)
        section_frame.grid(row=start_row, column=0, sticky="ew", padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y)
        start_row += 1

        if items:
            for i, item in enumerate(items):
                item_frame = ctk.CTkFrame(section_frame, fg_color=COLOR_ITEM_BG, corner_radius=5)
                item_frame.pack(fill="x", padx=PADDING_ITEM_X, pady=PADDING_ITEM_Y)
                for label_text, attr_name in item_fields:
                    value = getattr(item, attr_name, None) # Safely get attribute
                    self.create_detail_field(item_frame, label_text, value)
        else:
            no_data_label = ctk.CTkLabel(section_frame, text=empty_message, font=FONT_VALUE, text_color=COLOR_LABEL, anchor="w")
            no_data_label.pack(fill="x", padx=15, pady=10)

        return start_row


# --- Example Usage (if running this file directly for testing) ---
if __name__ == '__main__':
    # --- Dummy Data Setup (Mimicking SQLAlchemy Objects) ---
    class Dummy:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    dummy_grades = [
        Dummy(grade_type="Job Field", field="Construction", grade="Professional"),
        Dummy(grade_type="Technical Sector", field="Roads", grade="Senior")
    ]
    dummy_quals = [
        Dummy(title="PE Civil", acquisition_date="2020-05-15", registration_number="PE12345"),
        Dummy(title="Project Mgmt Cert", acquisition_date="2021-11-01", registration_number="PMC987")
    ]
    dummy_edu = [
        Dummy(graduation_date="2015-06-01", school_name="Tech University", major="Civil Engineering", degree="B.Sc.")
    ]
    dummy_wp = [
        Dummy(workplace_experience_period="2016-2018", workplace_company_name="BuildCorp"),
        Dummy(workplace_experience_period="2018-Present", workplace_company_name="InfraStruct Inc.")
    ]
    dummy_training = [
        Dummy(training_period="2 weeks", course_name="Advanced Concrete Tech", institution_name="Concrete Institute", completion_number="C101", training_field="Materials")
    ]
    dummy_awards = [
        Dummy(date="2022-01-10", type_and_basis="Project Excellence Award for Highway 50 Bridge", awarding_institution="National Engineering Society")
    ]
    dummy_sanctions = [] # Example with no sanctions
    dummy_projects = [
        Dummy(service_name="Highway 50 Bridge Design", project_type="Infrastructure", company_name="DesignFirm", participation_period="18 months", position="Lead Structural Engineer", client="State Department of Transportation"),
        Dummy(service_name="Downtown Redevelopment Planning", project_type="Urban Planning", company_name="InfraStruct Inc.", participation_period="9 months", position="Project Engineer", client="City of Metropolis")
    ]
    dummy_participation_tech = [Dummy(technical_sector="Bridge Design", participation_days="540"), Dummy(technical_sector="Road Design", participation_days="300")]
    dummy_participation_job = [Dummy(job="Design Engineer", participation_days="1000")]

    test_engineer = Dummy(
        id=1, name="Jane Rivera", company_name="InfraStruct Inc.", date_of_birth="1992-08-25",
        address="456 Structure Ave, Metropolis, 67890", position_and_rank="Lead Engineer II",
        responsible_technical_manager="Robert Chen", experience="9 years", field_name="Structural Engineering",
        evaluation_target="Senior Lead Promotion", pdf_file="~/docs/rivera_cv.pdf", selected=True,
        technical_grades=dummy_grades, technical_qualifications=dummy_quals, education=dummy_edu,
        technical_sector_participation=dummy_participation_tech, job_sector_participation=dummy_participation_job,
        specialized_field_participation=[], construction_type_participation=[],
        education_and_training=dummy_training, awards=dummy_awards, sanctions=dummy_sanctions,
        workplace=dummy_wp, project_details=dummy_projects
    )

    # --- CTk App Setup ---
    app = ctk.CTk()
    # app.set_appearance_mode("dark") # Ensure dark mode if not default
    app.geometry("400x200")
    app.title("Main App")

    def open_dialog():
        dialog = EngineerDetailDialog(app, test_engineer)
        # No mainloop needed here for Toplevel when app.mainloop() is running

    button = ctk.CTkButton(app, text="Show Engineer Details", command=open_dialog)
    button.pack(pady=50)

    app.mainloop()