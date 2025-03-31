import customtkinter as ctk
from src.services.notification import notification
from src.models.engineer import (
    Engineer, TechnicalGrade, Qualification, Education, TechnicalSectorParticipation,
    JobSectorParticipation, SpecializedFieldParticipation, ConstructionTypeParticipation,
    EducationAndTraining, Award, Sanction, Workplace, ProjectDetail
)
from src.widgets.date_picker import DatePicker
from src.widgets.widget_helper import WidgetHelper
from datetime import datetime

class EngineerDialog(ctk.CTkToplevel):
    def __init__(self, session, engineer=None, on_save=None):
        super().__init__()
        self.session = session
        self.engineer = engineer if engineer else Engineer()
        self.on_save = on_save
        self.title("Edit Engineer" if engineer else "Add Engineer")
        self.geometry("1000x800")

        # Main scrollable container
        self.container = ctk.CTkScrollableFrame(self)
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        row = 0

        # **Basic Information Section**
        row = WidgetHelper.create_section_header(self.container, "Basic Information", row)

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

        self.address_input = WidgetHelper.create_entry_row(self.container, "Address", row)
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

        self.responsible_technical_manager = WidgetHelper.create_entry_row(self.container, "Responsible Technical Manager", row)
        row += 1
        self.experience = WidgetHelper.create_textbox_row(self.container, "Experience", row, height=100)
        row += 1
        self.field_name = WidgetHelper.create_textbox_row(self.container, "Field Name", row, height=100)
        row += 1
        self.evaluation_target = WidgetHelper.create_entry_row(self.container, "Evaluation Target", row)
        row += 1
        self.pdf_file = WidgetHelper.create_entry_row(self.container, "PDF File", row)
        row += 1
        selected_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        selected_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(selected_frame, text="Selected").grid(row=0, column=0, padx=5)
        self.selected_var = ctk.BooleanVar(value=False)
        self.selected_checkbox = ctk.CTkCheckBox(selected_frame, text="", variable=self.selected_var)
        self.selected_checkbox.grid(row=0, column=1, padx=5)
        row += 1

        # **Relationship Sections**
        self.add_relationship_section("Technical Grades", row, self.add_tech_grade, lambda: self.tech_grades)
        row += 1
        self.add_relationship_section("Technical Qualifications", row, self.add_qualification, lambda: self.qualifications)
        row += 1
        self.add_relationship_section("Education", row, self.add_education, lambda: self.education)
        row += 1
        self.add_relationship_section("Technical Sector Participation", row, self.add_tech_sector, lambda: self.tech_sectors)
        row += 1
        self.add_relationship_section("Job Sector Participation", row, self.add_job_sector, lambda: self.job_sectors)
        row += 1
        self.add_relationship_section("Specialized Field Participation", row, self.add_specialized_field, lambda: self.specialized_fields)
        row += 1
        self.add_relationship_section("Construction Type Participation", row, self.add_construction_type, lambda: self.construction_types)
        row += 1
        self.add_relationship_section("Education and Training", row, self.add_training, lambda: self.trainings)
        row += 1
        self.add_relationship_section("Awards", row, self.add_award, lambda: self.awards)
        row += 1
        self.add_relationship_section("Sanctions", row, self.add_sanction, lambda: self.sanctions)
        row += 1
        self.add_relationship_section("Workplace", row, self.add_workplace, lambda: self.workplaces)
        row += 1
        self.add_relationship_section("Project Details", row, self.add_project_detail, lambda: self.project_details)
        row += 1

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
        return WidgetHelper.create_section_header(parent, text, row)

    def create_entry_row(self, parent, label, row):
        return WidgetHelper.create_entry_row(parent, label, row)

    def create_textbox_row(self, parent, label, row, height):
        return WidgetHelper.create_textbox_row(parent, label, row, height)

    def add_relationship_section(self, title, row, add_method, items_getter):
        return WidgetHelper.add_relationship_section(self.container, title, row, add_method, items_getter)

    # **Add Methods for Relationships**
    def add_tech_grade(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        type_entry = ctk.CTkEntry(frame, placeholder_text="Grade Type")
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        field_entry = ctk.CTkEntry(frame, placeholder_text="Field")
        field_entry.pack(side="left", padx=5, expand=True, fill="x")
        grade_entry = ctk.CTkEntry(frame, placeholder_text="Grade")
        grade_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.tech_grades.append({'type': type_entry, 'field': field_entry, 'grade': grade_entry})

    def add_qualification(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        title_entry = ctk.CTkEntry(frame, placeholder_text="Title")
        title_entry.pack(side="left", padx=5, expand=True, fill="x")
        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        reg_entry = ctk.CTkEntry(frame, placeholder_text="Registration Number")
        reg_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.qualifications.append({'title': title_entry, 'date': date_entry, 'reg_num': reg_entry})

    def add_education(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        grad_date_entry = DatePicker(frame)
        grad_date_entry.pack(side="left", padx=5)
        school_entry = ctk.CTkEntry(frame, placeholder_text="School Name")
        school_entry.pack(side="left", padx=5, expand=True, fill="x")
        major_entry = ctk.CTkEntry(frame, placeholder_text="Major")
        major_entry.pack(side="left", padx=5, expand=True, fill="x")
        degree_entry = ctk.CTkEntry(frame, placeholder_text="Degree")
        degree_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.education.append({'grad_date': grad_date_entry, 'school': school_entry, 'major': major_entry, 'degree': degree_entry})

    def add_tech_sector(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        sector_entry = ctk.CTkEntry(frame, placeholder_text="Technical Sector")
        sector_entry.pack(side="left", padx=5, expand=True, fill="x")
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days")
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.tech_sectors.append({'sector': sector_entry, 'days': days_entry})

    def add_job_sector(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        job_entry = ctk.CTkEntry(frame, placeholder_text="Job")
        job_entry.pack(side="left", padx=5, expand=True, fill="x")
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days")
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.job_sectors.append({'job': job_entry, 'days': days_entry})

    def add_specialized_field(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        field_entry = ctk.CTkEntry(frame, placeholder_text="Specialized Field")
        field_entry.pack(side="left", padx=5, expand=True, fill="x")
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days")
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.specialized_fields.append({'field': field_entry, 'days': days_entry})

    def add_construction_type(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        type_entry = ctk.CTkEntry(frame, placeholder_text="Construction Type")
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        days_entry = ctk.CTkEntry(frame, placeholder_text="Participation Days")
        days_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.construction_types.append({'type': type_entry, 'days': days_entry})

    def add_training(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        period_entry = ctk.CTkEntry(frame, placeholder_text="Training Period")
        period_entry.pack(side="left", padx=5, expand=True, fill="x")
        course_entry = ctk.CTkEntry(frame, placeholder_text="Course Name")
        course_entry.pack(side="left", padx=5, expand=True, fill="x")
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Institution Name")
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")
        completion_entry = ctk.CTkEntry(frame, placeholder_text="Completion Number")
        completion_entry.pack(side="left", padx=5, expand=True, fill="x")
        field_entry = ctk.CTkEntry(frame, placeholder_text="Training Field")
        field_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.trainings.append({
            'period': period_entry, 'course': course_entry, 'institution': institution_entry,
            'completion': completion_entry, 'field': field_entry
        })

    def add_award(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        type_entry = ctk.CTkEntry(frame, placeholder_text="Type and Basis")
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Awarding Institution")
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.awards.append({'date': date_entry, 'type': type_entry, 'institution': institution_entry})

    def add_sanction(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        points_entry = ctk.CTkEntry(frame, placeholder_text="Penalty Points")
        points_entry.pack(side="left", padx=5, expand=True, fill="x")
        date_entry = DatePicker(frame)
        date_entry.pack(side="left", padx=5)
        type_entry = ctk.CTkEntry(frame, placeholder_text="Type")
        type_entry.pack(side="left", padx=5, expand=True, fill="x")
        period_entry = ctk.CTkEntry(frame, placeholder_text="Sanction Period")
        period_entry.pack(side="left", padx=5, expand=True, fill="x")
        basis_entry = ctk.CTkEntry(frame, placeholder_text="Basis")
        basis_entry.pack(side="left", padx=5, expand=True, fill="x")
        institution_entry = ctk.CTkEntry(frame, placeholder_text="Sanctioning Institution")
        institution_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.sanctions.append({
            'points': points_entry, 'date': date_entry, 'type': type_entry,
            'period': period_entry, 'basis': basis_entry, 'institution': institution_entry
        })

    def add_workplace(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        period_entry = ctk.CTkEntry(frame, placeholder_text="Experience Period")
        period_entry.pack(side="left", padx=5, expand=True, fill="x")
        company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name")
        company_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.add_remove_button(frame)
        self.workplaces.append({'period': period_entry, 'company': company_entry})

    def add_project_detail(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=2)
        service_entry = ctk.CTkEntry(frame, placeholder_text="Service Name")
        service_entry.pack(side="left", padx=5, expand=True, fill="x")
        project_type_entry = ctk.CTkEntry(frame, placeholder_text="Project Type")
        project_type_entry.pack(side="left", padx=5, expand=True, fill="x")
        company_entry = ctk.CTkEntry(frame, placeholder_text="Company Name")
        company_entry.pack(side="left", padx=5, expand=True, fill="x")
        contractor_entry = ctk.CTkEntry(frame, placeholder_text="Representative Contractor")
        contractor_entry.pack(side="left", padx=5, expand=True, fill="x")
        contract_date_entry = DatePicker(frame)
        contract_date_entry.pack(side="left", padx=5)
        self.add_remove_button(frame)
        self.project_details.append({
            'service': service_entry, 'project_type': project_type_entry, 'company': company_entry,
            'contractor': contractor_entry, 'contract_date': contract_date_entry
        })

    def add_remove_button(self, frame):
        ctk.CTkButton(
            frame, text="Remove", command=lambda: frame.destroy(), width=60,
            fg_color="#E74C3C", hover_color="#C0392B"
        ).pack(side="right", padx=5)

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
        self.pdf_file.insert(0, engineer.pdf_file or "")
        self.selected_var.set(engineer.selected or False)

        for grade in engineer.technical_grades:
            self.add_tech_grade(self.technical_grades_frame)
            self.tech_grades[-1]['type'].insert(0, grade.grade_type or "")
            self.tech_grades[-1]['field'].insert(0, grade.field or "")
            self.tech_grades[-1]['grade'].insert(0, grade.grade or "")

        for qual in engineer.technical_qualifications:
            self.add_qualification(self.technical_qualifications_frame)
            self.qualifications[-1]['title'].insert(0, qual.title or "")
            if qual.acquisition_date:
                self.qualifications[-1]['date'].set_date(qual.acquisition_date)
            self.qualifications[-1]['reg_num'].insert(0, qual.registration_number or "")

        for edu in engineer.education:
            self.add_education(self.education_frame)
            if edu.graduation_date:
                self.education[-1]['grad_date'].set_date(edu.graduation_date)
            self.education[-1]['school'].insert(0, edu.school_name or "")
            self.education[-1]['major'].insert(0, edu.major or "")
            self.education[-1]['degree'].insert(0, edu.degree or "")

        for ts in engineer.technical_sector_participation:
            self.add_tech_sector(self.technical_sector_participation_frame)
            self.tech_sectors[-1]['sector'].insert(0, ts.technical_sector or "")
            self.tech_sectors[-1]['days'].insert(0, ts.participation_days or "")

        for js in engineer.job_sector_participation:
            self.add_job_sector(self.job_sector_participation_frame)
            self.job_sectors[-1]['job'].insert(0, js.job or "")
            self.job_sectors[-1]['days'].insert(0, js.participation_days or "")

        for sf in engineer.specialized_field_participation:
            self.add_specialized_field(self.specialized_field_participation_frame)
            self.specialized_fields[-1]['field'].insert(0, sf.specialized_field or "")
            self.specialized_fields[-1]['days'].insert(0, sf.participation_days or "")

        for ct in engineer.construction_type_participation:
            self.add_construction_type(self.construction_type_participation_frame)
            self.construction_types[-1]['type'].insert(0, ct.construction_type or "")
            self.construction_types[-1]['days'].insert(0, ct.participation_days or "")

        for train in engineer.education_and_training:
            self.add_training(self.education_and_training_frame)
            self.trainings[-1]['period'].insert(0, train.training_period or "")
            self.trainings[-1]['course'].insert(0, train.course_name or "")
            self.trainings[-1]['institution'].insert(0, train.institution_name or "")
            self.trainings[-1]['completion'].insert(0, train.completion_number or "")
            self.trainings[-1]['field'].insert(0, train.training_field or "")

        for award in engineer.awards:
            self.add_award(self.awards_frame)
            if award.date:
                self.awards[-1]['date'].set_date(award.date)
            self.awards[-1]['type'].insert(0, award.type_and_basis or "")
            self.awards[-1]['institution'].insert(0, award.awarding_institution or "")

        for sanction in engineer.sanctions:
            self.add_sanction(self.sanctions_frame)
            self.sanctions[-1]['points'].insert(0, sanction.penalty_points or "")
            if sanction.date:
                self.sanctions[-1]['date'].set_date(sanction.date)
            self.sanctions[-1]['type'].insert(0, sanction.type or "")
            self.sanctions[-1]['period'].insert(0, sanction.sanction_period or "")
            self.sanctions[-1]['basis'].insert(0, sanction.basis or "")
            self.sanctions[-1]['institution'].insert(0, sanction.sanctioning_institution or "")

        for wp in engineer.workplace:
            self.add_workplace(self.workplace_frame)
            self.workplaces[-1]['period'].insert(0, wp.workplace_experience_period or "")
            self.workplaces[-1]['company'].insert(0, wp.workplace_company_name or "")

        for pd in engineer.project_details:
            self.add_project_detail(self.project_details_frame)
            self.project_details[-1]['service'].insert(0, pd.service_name or "")
            self.project_details[-1]['project_type'].insert(0, pd.project_type or "")
            self.project_details[-1]['company'].insert(0, pd.company_name or "")
            self.project_details[-1]['contractor'].insert(0, pd.representative_contractor or "")
            if pd.contract_date:
                self.project_details[-1]['contract_date'].set_date(pd.contract_date)

    def save_engineer(self):
        try:
            # Basic fields
            name = self.name_input.get().strip()
            birth_date = self.birth_date_input.get_date()
            if not name or not birth_date:
                notification.error("Name and Birth Date are required")
                return

            self.engineer.name = name
            self.engineer.date_of_birth = birth_date
            self.engineer.address = self.address_input.get().strip()
            self.engineer.company_name = self.company_input.get().strip()
            self.engineer.position_and_rank = self.position_input.get().strip()
            self.engineer.responsible_technical_manager = self.responsible_technical_manager.get().strip()
            self.engineer.experience = self.experience.get("1.0", "end-1c").strip()
            self.engineer.field_name = self.field_name.get("1.0", "end-1c").strip()
            self.engineer.evaluation_target = self.evaluation_target.get().strip()
            self.engineer.pdf_file = self.pdf_file.get().strip()
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
            notification.success("Engineer saved successfully")
            if self.on_save:
                self.on_save()
            self.destroy()

        except Exception as e:
            notification.error(f"Error saving engineer: {str(e)}")
            self.session.rollback()