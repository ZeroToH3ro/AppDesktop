import customtkinter as ctk
from src.services.notification import notification
from src.views.engineer_detail import EngineerDetailDialog
from src.views.engineer_dialog import EngineerDialog
from src.models.engineer import Engineer
import math

class EngineerTable(ctk.CTkFrame):
    def __init__(self, parent, session, on_page_change=None):
        super().__init__(parent, fg_color="transparent")
        
        self.session = session
        self.on_page_change = on_page_change
        self.current_page = 1
        self.rows_per_page = 10
        self.total_pages = 1
        self.selected_rows = set()
        
        # Column configurations with relative weights
        self.columns = [
            {"name": "Select", "width": 60, "weight": 0},
            {"name": "ID", "width": 60, "weight": 0},
            {"name": "Name", "width": 180, "weight": 2},
            {"name": "Company", "width": 150, "weight": 2},
            {"name": "Areas", "width": 150, "weight": 2},
            {"name": "Projects", "width": 140, "weight": 2},
            {"name": "Actions", "width": 300, "weight": 0}
        ]
        
        # Configure main frame to expand
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create table container with border
        self.table_container = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=8)
        self.table_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure table container to expand
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Create header
        self._create_header()
        
        # Create scrollable frame for table content
        self.table_frame = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.table_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure column weights in table frame
        for i, col in enumerate(self.columns):
            self.table_frame.grid_columnconfigure(i, weight=col["weight"], minsize=col["width"])
            
    def _create_header(self):
        header_frame = ctk.CTkFrame(self.table_container, fg_color="#252525", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Configure header columns with weights
        for i, col in enumerate(self.columns):
            header_frame.grid_columnconfigure(i, weight=col["weight"], minsize=col["width"])
            
            header_cell = ctk.CTkFrame(header_frame, fg_color="#2C2C2C", corner_radius=0)
            header_cell.grid(row=0, column=i, sticky="nsew", padx=(0, 1), pady=(0, 1))
            header_cell.grid_columnconfigure(0, weight=1)
            
            label = ctk.CTkLabel(
                header_cell,
                text=col["name"],
                font=("Arial Bold", 12),
                text_color="#E0E0E0",
                anchor="center"
            )
            label.grid(row=0, column=0, sticky="nsew", padx=10, pady=12)

    def load_data(self):
        try:
            # Clear existing table
            for widget in self.table_frame.grid_slaves():
                widget.destroy()
            
            # Get engineers for current page
            offset = (self.current_page - 1) * self.rows_per_page
            engineers = self.session.query(Engineer).offset(offset).limit(self.rows_per_page).all()
            
            # Get total count for pagination
            total_count = self.session.query(Engineer).count()
            self.total_pages = math.ceil(total_count / self.rows_per_page)
            
            # Insert data rows
            for row_idx, engineer in enumerate(engineers):
                row_color = "#2A2A2A" if row_idx % 2 == 0 else "#262626"
                
                # Create row container
                row_frame = ctk.CTkFrame(self.table_frame, fg_color=row_color, corner_radius=0)
                row_frame.grid(row=row_idx, column=0, columnspan=len(self.columns), sticky="ew")
                
                # Configure row columns with weights
                for i, col in enumerate(self.columns):
                    row_frame.grid_columnconfigure(i, weight=col["weight"], minsize=col["width"])
                
                # Checkbox cell
                checkbox_cell = ctk.CTkFrame(row_frame, fg_color="transparent", corner_radius=0)
                checkbox_cell.grid(row=0, column=0, sticky="nsew", padx=(0, 1), pady=(0, 1))
                
                checkbox = ctk.CTkCheckBox(
                    checkbox_cell,
                    text="",
                    command=lambda id=engineer.id: self.toggle_row_selection(id),
                    width=20,
                    height=20,
                    fg_color="#1f538d",
                    hover_color="#3b8ed0",
                    border_color="#4F4F4F",
                    corner_radius=3
                )
                checkbox.pack(expand=True, padx=10, pady=10)
                
                # Data cells
                cells = [
                    (0, str(engineer.id)),
                    (1, engineer.name or ""),
                    (2, engineer.company_name or ""),
                    (3, engineer.field_name or ""),
                    (4, engineer.evaluation_target or "")
                ]
                
                for col, text in cells:
                    cell = ctk.CTkFrame(row_frame, fg_color="transparent", corner_radius=0)
                    cell.grid(row=0, column=col+1, sticky="nsew", padx=(0, 1), pady=(0, 1))
                    cell.grid_columnconfigure(0, weight=1)
                    
                    label = ctk.CTkLabel(
                        cell,
                        text=text,
                        anchor="w",
                        wraplength=0,  # Let the text wrap naturally
                        justify="left",
                        font=("Arial", 12),
                        text_color="#D0D0D0"
                    )
                    label.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)
                
                # Actions cell with buttons
                actions_frame = self._create_actions_frame(row_frame, engineer)
                actions_frame.grid(row=0, column=len(cells)+1, sticky="nsew", padx=(0, 1), pady=(0, 1))
                
            # Update pagination state
            if hasattr(self, 'on_page_change'):
                self.on_page_change(self.current_page, self.total_pages)
                
        except Exception as e:
            print(f"Error loading engineers: {str(e)}")

    def _create_actions_frame(self, parent, engineer):
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        
        # Configure all columns with equal weight
        for i in range(3):
            actions_frame.grid_columnconfigure(i, weight=1)
        
        # Button styling
        button_style = {
            "height": 28,
            "width": 65,  # Increased button width
            "corner_radius": 4,
            "font": ("Arial", 12)
        }
        
        # View button
        view_btn = ctk.CTkButton(
            actions_frame,
            text="View",
            command=lambda e=engineer: self.show_details(e),
            fg_color="#2980B9",
            hover_color="#2573A7",
            **button_style
        )
        view_btn.grid(row=0, column=0, padx=(5, 2), pady=6)  # Adjusted padding
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            command=lambda e=engineer: self.edit_engineer(e),
            fg_color="#27AE60",
            hover_color="#219A52",
            **button_style
        )
        edit_btn.grid(row=0, column=1, padx=2, pady=6)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="Delete",
            command=lambda e=engineer: self.delete_engineer(e),
            fg_color="#E74C3C",
            hover_color="#C0392B",
            **button_style
        )
        delete_btn.grid(row=0, column=2, padx=(2, 5), pady=6)  # Adjusted padding
        
        return actions_frame
    
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
    
    def show_details(self, engineer):
        EngineerDetailDialog(self, engineer)
    
    def get_selected_engineer(self):
        if len(self.selected_rows) == 1:
            engineer_id = list(self.selected_rows)[0]
            return self.session.query(Engineer).get(engineer_id)
        return None
    
    def delete_engineer(self, engineer):
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
