import customtkinter as ctk
from src.services.notification import notification
from src.models.engineer import Engineer
from src.widgets.date_picker import DatePicker
from datetime import datetime

class EngineerDialog(ctk.CTkToplevel):
    def __init__(self, session, engineer=None, on_save=None):
        super().__init__()
        self.session = session
        self.engineer = engineer
        self.on_save = on_save
        self.title("Edit Engineer" if engineer else "Add Engineer")
        self.geometry("500x600")
        
        # Create main container
        container = ctk.CTkFrame(self)
        container.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Basic fields
        row = 0
        
        # Name and Birth Date row
        name_frame = ctk.CTkFrame(container, fg_color="transparent")
        name_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        name_frame.grid_columnconfigure(1, weight=1)
        name_frame.grid_columnconfigure(3, weight=1)
        
        name_label = ctk.CTkLabel(name_frame, text="Name")
        name_label.grid(row=0, column=0, padx=5)
        self.name_input = ctk.CTkEntry(name_frame)
        self.name_input.grid(row=0, column=1, padx=5, sticky="ew")
        
        birth_label = ctk.CTkLabel(name_frame, text="Birth Date")
        birth_label.grid(row=0, column=2, padx=5)
        self.birth_date_input = DatePicker(name_frame)
        self.birth_date_input.grid(row=0, column=3, padx=5, sticky="w")
        row += 1
        
        # Address
        self.address_input = self.create_entry_row(container, "Address", row)
        row += 1
        
        # Company and Position row
        company_frame = ctk.CTkFrame(container, fg_color="transparent")
        company_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        company_frame.grid_columnconfigure(1, weight=1)
        company_frame.grid_columnconfigure(3, weight=1)
        
        company_label = ctk.CTkLabel(company_frame, text="Company")
        company_label.grid(row=0, column=0, padx=5)
        self.company_input = ctk.CTkEntry(company_frame)
        self.company_input.grid(row=0, column=1, padx=5, sticky="ew")
        
        position_label = ctk.CTkLabel(company_frame, text="Position")
        position_label.grid(row=0, column=2, padx=5)
        self.position_input = ctk.CTkEntry(company_frame)
        self.position_input.grid(row=0, column=3, padx=5, sticky="ew")
        row += 1
        
        # Project Lead
        self.project_lead = self.create_entry_row(container, "Project Lead", row)
        row += 1
        
        # Experience Summary (Multiline)
        exp_label = ctk.CTkLabel(container, text="Experience Summary")
        exp_label.grid(row=row, column=0, padx=5, pady=5, sticky="nw")
        self.experience_summary = ctk.CTkTextbox(container, height=100)
        self.experience_summary.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
        row += 1
        
        # Expertise Area (Multiline)
        exp_label = ctk.CTkLabel(container, text="Expertise Area")
        exp_label.grid(row=row, column=0, padx=5, pady=5, sticky="nw")
        self.expertise_area = ctk.CTkTextbox(container, height=100)
        self.expertise_area.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
        row += 1
        
        # Configure grid
        container.grid_columnconfigure(1, weight=1)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        cancel_button.pack(side="left", padx=5)
        
        # Save button
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=self.save_engineer,
            width=100
        )
        save_button.pack(side="left", padx=5)
        
        # Load data if editing
        if engineer:
            self.load_engineer_data(engineer)
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()

    def create_entry_row(self, parent, label, row):
        label = ctk.CTkLabel(parent, text=label)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        return entry

    def load_engineer_data(self, engineer):
        self.name_input.insert(0, engineer.name or "")
        if engineer.birth_date:
            self.birth_date_input.set_date(engineer.birth_date)
        self.address_input.insert(0, engineer.address or "")
        self.company_input.insert(0, engineer.company or "")
        self.position_input.insert(0, engineer.position or "")
        self.project_lead.insert(0, engineer.project_lead or "")
        self.experience_summary.insert("1.0", engineer.experience_summary or "")
        self.expertise_area.insert("1.0", engineer.expertise_area or "")

    def save_engineer(self):
        try:
            # Get values from inputs
            name = self.name_input.get().strip()
            birth_date = self.birth_date_input.get_date()
            address = self.address_input.get().strip()
            company = self.company_input.get().strip()
            position = self.position_input.get().strip()
            project_lead = self.project_lead.get().strip()
            experience_summary = self.experience_summary.get("1.0", "end-1c").strip()
            expertise_area = self.expertise_area.get("1.0", "end-1c").strip()
            
            # Validate required fields
            if not name:
                notification.error("Name is required")
                return
                
            if not birth_date:
                notification.error("Birth date is required")
                return
            
            # Create or update engineer
            if not self.engineer:
                self.engineer = Engineer()
            
            # Update engineer attributes
            self.engineer.name = name
            self.engineer.birth_date = birth_date
            self.engineer.address = address
            self.engineer.company = company
            self.engineer.position = position
            self.engineer.project_lead = project_lead
            self.engineer.experience_summary = experience_summary
            self.engineer.expertise_area = expertise_area
            
            # Save to database
            if not self.engineer.id:
                self.session.add(self.engineer)
            self.session.commit()
            
            # Notify success
            notification.success("Engineer saved successfully")
            
            # Call callback if provided
            if self.on_save:
                self.on_save()
            
            # Close dialog
            self.destroy()
            
        except Exception as e:
            notification.error(f"Error saving engineer: {str(e)}")
            self.session.rollback()
