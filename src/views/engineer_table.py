import customtkinter as ctk
from src.services.notification import notification
from src.views.engineer_detail import EngineerDetailDialog
from src.views.engineer_dialog import EngineerDialog
from src.models.engineer import Engineer
import math

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
        
        # Create table container with border
        self.table_container = ctk.CTkFrame(self, fg_color="#2C3E50", corner_radius=10)
        self.table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create table header with distinct background
        header_frame = ctk.CTkFrame(self.table_container, fg_color="#34495E", corner_radius=0)
        header_frame.pack(fill="x", padx=2, pady=(2,0))
        
        # Configure header columns with equal width
        headers = ["Select", "ID", "Name", "Birth Date", "Company", "Position", "Actions"]
        column_widths = [60, 60, 150, 100, 150, 150, 200]  # Specify widths for each column
        
        for i, (header, width) in enumerate(zip(headers, column_widths)):
            header_cell = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_cell.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            header_cell.grid_columnconfigure(0, weight=1)
            
            label = ctk.CTkLabel(
                header_cell, 
                text=header, 
                font=("Arial Bold", 12),
                text_color="#ECF0F1",
                padx=10,
                pady=5
            )
            label.pack(fill="both", expand=True)
            
            header_frame.grid_columnconfigure(i, weight=0, minsize=width)
        
        # Create scrollable frame for table content
        self.table_frame = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.table_frame.pack(fill="both", expand=True, padx=2, pady=(0,2))
        
        # Configure grid columns in table frame to match header
        for i, width in enumerate(column_widths):
            self.table_frame.grid_columnconfigure(i, weight=0, minsize=width)
        
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
            for row_idx, engineer in enumerate(engineers):
                row_color = "#2C3E50" if row_idx % 2 == 0 else "#34495E"
                
                # Create row container
                row_frame = ctk.CTkFrame(self.table_frame, fg_color=row_color, corner_radius=0)
                row_frame.grid(row=row_idx, column=0, columnspan=7, sticky="ew", padx=1, pady=1)
                
                # Configure row columns
                for i, width in enumerate(column_widths):
                    row_frame.grid_columnconfigure(i, weight=0, minsize=width)
                
                # Create checkbox cell
                checkbox_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
                checkbox_cell.grid(row=0, column=0, sticky="nsew", padx=1)
                
                checkbox = ctk.CTkCheckBox(
                    checkbox_cell,
                    text="",
                    command=lambda id=engineer.id: self.toggle_row_selection(id),
                    width=20,
                    height=20
                )
                checkbox.pack(padx=10, pady=5)
                
                # Create data cells with proper text wrapping
                cells = [
                    (0, str(engineer.id), 60),
                    (1, engineer.person_name or "", 150),
                    (2, engineer.birth_date or "", 100),
                    (3, engineer.associated_company or "", 150),
                    (4, engineer.position_title or "", 150)
                ]
                
                for col, text, width in cells:
                    cell = ctk.CTkFrame(row_frame, fg_color="transparent")
                    cell.grid(row=0, column=col+1, sticky="nsew", padx=1)
                    
                    label = ctk.CTkLabel(
                        cell,
                        text=text,
                        anchor="w",
                        wraplength=width-20,  # Account for padding
                        justify="left",
                        padx=10,
                        pady=5
                    )
                    label.pack(fill="both", expand=True)
                
                # Create actions cell
                actions_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
                actions_cell.grid(row=0, column=6, sticky="nsew", padx=1)
                
                # Action buttons
                actions_frame = ctk.CTkFrame(actions_cell, fg_color="transparent")
                actions_frame.pack(padx=5, pady=5)
                
                # View button
                view_btn = ctk.CTkButton(
                    actions_frame,
                    text="View",
                    command=lambda e=engineer: self.show_engineer_detail(e),
                    width=60,
                    height=25,
                    fg_color="#2ECC71",
                    hover_color="#27AE60"
                )
                view_btn.pack(side="left", padx=2)
                
                # Edit button
                edit_btn = ctk.CTkButton(
                    actions_frame,
                    text="Edit",
                    command=lambda e=engineer: self.edit_engineer(e),
                    width=60,
                    height=25,
                    fg_color="#3498DB",
                    hover_color="#2980B9"
                )
                edit_btn.pack(side="left", padx=2)
                
                # Delete button
                delete_btn = ctk.CTkButton(
                    actions_frame,
                    text="Delete",
                    command=lambda e=engineer: self.delete_single_engineer(e),
                    width=60,
                    height=25,
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
            self.filtered_engineers = self.engineers
        else:
            self.filtered_engineers = [
                eng for eng in self.engineers
                if self.filter_text in eng.person_name.lower() or
                   self.filter_text in eng.associated_company.lower() or
                   self.filter_text in eng.position_title.lower()
            ]
        self.current_page = 1
        self.load_data()
    
    def set_rows_per_page(self, value):
        self.rows_per_page = value
        self.current_page = 1
        self.load_data()
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()
    
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()
    
    def toggle_row_selection(self, engineer_id):
        if engineer_id in self.selected_rows:
            self.selected_rows.remove(engineer_id)
        else:
            self.selected_rows.add(engineer_id)
    
    def set_page_change_callback(self, callback):
        self.on_page_change = callback
    
    def show_engineer_detail(self, engineer):
        EngineerDetailDialog(self, engineer)
    
    def get_selected_engineer(self):
        if len(self.selected_rows) == 1:
            engineer_id = list(self.selected_rows)[0]
            return self.session.query(Engineer).get(engineer_id)
        return None
    
    def delete_single_engineer(self, engineer):
        try:
            self.session.delete(engineer)
            self.session.commit()
            notification.show_success("Engineer deleted successfully")
            self.load_data()
        except Exception as e:
            notification.show_error(f"Error deleting engineer: {str(e)}")
            self.session.rollback()

    def add_engineer(self):
        dialog = EngineerDialog(self.session, on_save=self.load_data)
        dialog.mainloop()
        
    def delete_selected(self):
        if not self.selected_rows:
            notification.show_warning("No Selection", "Please select at least one engineer to delete.")
            return
            
        try:
            # Delete selected engineers
            for engineer_id in self.selected_rows:
                engineer = self.session.query(Engineer).get(engineer_id)
                if engineer:
                    self.session.delete(engineer)
            
            self.session.commit()
            notification.show_success("Success", "Selected engineers were deleted successfully.")
            
            # Clear selection and reload
            self.selected_rows.clear()
            self.load_data()
            
        except Exception as e:
            self.session.rollback()
            notification.show_error("Error", f"Failed to delete engineers: {str(e)}")

    def edit_engineer(self, engineer):
        dialog = EngineerDialog(self.session, engineer=engineer, on_save=self.load_data)
        dialog.mainloop()
