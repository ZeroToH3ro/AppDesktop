import customtkinter as ctk
from PIL import Image, ImageDraw
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from src.services.translator import Translator
from src.services.notification import NotificationService
from src.widgets.date_picker import DatePicker
import csv
import math

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Constants
SIDEBAR_WIDTH = 240
ICON_SIZE = 20

Base = declarative_base()
translator = Translator()
notification = NotificationService()

class Engineer(Base):
    __tablename__ = 'engineers'
    id = Column(Integer, primary_key=True)
    person_name = Column(String)
    birth_date = Column(Date)  
    address = Column(String)
    associated_company = Column(String)
    currency_unit = Column(String, default='백만원')
    technical_grades = Column(String)  
    position_title = Column(String)
    expertise_area = Column(String)
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

# Database initialization
engine = create_engine('sqlite:///engineer_db.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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
        
        headers = ["ID", "Name", "Birth Date", "Address", "Company", "Technical Grade"]
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
                    command=lambda e=engineer: self.toggle_row_selection(e.id)
                )
                checkbox.grid(row=row, column=0, padx=5, pady=2)
                checkbox.select() if engineer.id in self.selected_rows else checkbox.deselect()
                
                # Add engineer data
                ctk.CTkLabel(self.table_frame, text=str(engineer.id)).grid(
                    row=row, column=1, padx=5, pady=2, sticky="w"
                )
                ctk.CTkLabel(self.table_frame, text=engineer.person_name or "").grid(
                    row=row, column=2, padx=5, pady=2, sticky="w"
                )
                ctk.CTkLabel(self.table_frame, text=str(engineer.birth_date or "")).grid(
                    row=row, column=3, padx=5, pady=2, sticky="w"
                )
                ctk.CTkLabel(self.table_frame, text=engineer.address or "").grid(
                    row=row, column=4, padx=5, pady=2, sticky="w"
                )
                ctk.CTkLabel(self.table_frame, text=engineer.associated_company or "").grid(
                    row=row, column=5, padx=5, pady=2, sticky="w"
                )
                ctk.CTkLabel(self.table_frame, text=engineer.technical_grades or "").grid(
                    row=row, column=6, padx=5, pady=2, sticky="w"
                )
            
            # Update pagination controls
            self.prev_button.configure(state="normal" if self.current_page > 1 else "disabled")
            self.next_button.configure(state="normal" if self.current_page < self.total_pages else "disabled")
            self.page_info.configure(text=f"Page {self.current_page} of {self.total_pages}")
        
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

class EngineerDialog(ctk.CTkToplevel):
    def __init__(self, session, engineer=None, on_save=None):
        super().__init__()
        self.session = session
        self.engineer = engineer
        self.on_save = on_save
        self.title(translator.translations['en']['basic_info'])
        self.geometry("600x500")  # Increased height for date picker
        
        # Create form
        form = ctk.CTkFrame(self)
        form.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Basic Information
        self.name_input = ctk.CTkEntry(form)
        self.address_input = ctk.CTkEntry(form)
        self.company_input = ctk.CTkEntry(form)
        
        # Date picker
        self.birth_date_frame = ctk.CTkFrame(form)
        self.birth_date_input = ctk.CTkEntry(self.birth_date_frame)
        self.birth_date_input.pack(side="left", padx=(0, 5))
        
        def show_date_picker():
            if hasattr(self, 'date_picker_window'):
                return
            
            self.date_picker_window = ctk.CTkToplevel(self)
            self.date_picker_window.title("Select Date")
            self.date_picker_window.geometry("300x300")
            
            def on_date_selected(date):
                self.birth_date_input.delete(0, "end")
                self.birth_date_input.insert(0, date.strftime("%Y-%m-%d"))
                self.date_picker_window.destroy()
                delattr(self, 'date_picker_window')
            
            date_picker = DatePicker(self.date_picker_window, command=on_date_selected)
            date_picker.pack(padx=10, pady=10)
            
            if self.birth_date_input.get():
                try:
                    date_picker.set_date(self.birth_date_input.get())
                except ValueError:
                    pass
        
        calendar_button = ctk.CTkButton(
            self.birth_date_frame,
            text="📅",
            width=30,
            command=show_date_picker
        )
        calendar_button.pack(side="left")
        
        # Technical Grades
        self.grade_input = ctk.CTkComboBox(form, values=['Junior', 'Intermediate', 'Senior', 'Expert'])
        
        # Layout
        row = 0
        ctk.CTkLabel(form, text=translator.translations['en']['name']).grid(row=row, column=0, padx=5, pady=5)
        self.name_input.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        row += 1
        ctk.CTkLabel(form, text=translator.translations['en']['birth_date']).grid(row=row, column=0, padx=5, pady=5)
        self.birth_date_frame.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        row += 1
        ctk.CTkLabel(form, text="Address").grid(row=row, column=0, padx=5, pady=5)
        self.address_input.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        row += 1
        ctk.CTkLabel(form, text="Company").grid(row=row, column=0, padx=5, pady=5)
        self.company_input.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        row += 1
        ctk.CTkLabel(form, text="Technical Grade").grid(row=row, column=0, padx=5, pady=5)
        self.grade_input.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        # Configure grid
        form.grid_columnconfigure(1, weight=1)
        
        # Save button
        row += 1
        save_button = ctk.CTkButton(form, text=translator.translations['en']['save'], command=self.save_engineer)
        save_button.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Load data if editing
        if engineer:
            self.name_input.insert(0, engineer.person_name or "")
            self.birth_date_input.insert(0, str(engineer.birth_date or ""))
            self.address_input.insert(0, engineer.address or "")
            self.company_input.insert(0, engineer.associated_company or "")
            if engineer.technical_grades:
                self.grade_input.set(engineer.technical_grades)
        else:
            # Set default date to current date
            self.birth_date_input.insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    def save_engineer(self):
        try:
            if not self.engineer:
                self.engineer = Engineer()
            
            name = self.name_input.get().strip()
            birth_date = self.birth_date_input.get().strip()
            
            if not name or not birth_date:
                notification.show_error("Name and birth date are required!")
                return
            
            try:
                parsed_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            except ValueError:
                notification.show_error("Invalid date format. Use YYYY-MM-DD")
                return
            
            self.engineer.person_name = name
            self.engineer.birth_date = parsed_date
            self.engineer.address = self.address_input.get()
            self.engineer.associated_company = self.company_input.get()
            self.engineer.technical_grades = self.grade_input.get()
            
            if not self.engineer.id:
                self.session.add(self.engineer)
            
            self.session.commit()
            if self.on_save:
                self.on_save()
            notification.show_success(f"Engineer {name} {'updated' if self.engineer.id else 'added'} successfully!")
            self.destroy()
            
        except Exception as e:
            notification.show_error(f"Error saving engineer: {str(e)}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Engineer Management System")
        self.geometry("1200x800")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create SQLite database
        engine = create_engine('sqlite:///engineers.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
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
        
        # Bottom frame for pagination and actions
        bottom_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        bottom_frame.grid_columnconfigure(0, weight=1)  # Make pagination expand
        
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
        
        prev_page = ctk.CTkButton(
            pagination_frame,
            text="←",
            width=35,
            height=35,
            command=self.engineer_table.prev_page
        )
        prev_page.pack(side="left", padx=5)
        
        page_label = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 of 1",
            width=100,
            height=35
        )
        page_label.pack(side="left", padx=5)
        
        next_page = ctk.CTkButton(
            pagination_frame,
            text="→",
            width=35,
            height=35,
            command=self.engineer_table.next_page
        )
        next_page.pack(side="left", padx=5)
        
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
            text="Delete",
            command=self.delete_engineer,
            height=35,
            width=80,
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

if __name__ == "__main__":
    app = App()
    app.mainloop()