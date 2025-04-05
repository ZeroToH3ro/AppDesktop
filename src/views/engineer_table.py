# Required imports for the enhanced functionality
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, Menu
import customtkinter as ctk
import math
import traceback
from sqlalchemy import asc, desc

from src.models.engineer import Engineer

# Simple notification function
def show_notification(parent, message, title="Notification", type="info"):
    """Show a notification message to the user"""
    if type == "info":
        messagebox.showinfo(title, message, parent=parent)
    elif type == "warning":
        messagebox.showwarning(title, message, parent=parent)
    elif type == "error":
        messagebox.showerror(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent)

# Imports from your original code structure
# Ensure these paths are correct for your project
# Using our local show_notification function instead of external notification service
# Assuming EngineerDialog handles both view and edit
from src.views.engineer_dialog import EngineerDialog
# from src.views.engineer_detail import EngineerDetailDialog # Potentially removed if merged into EngineerDialog
from src.models.engineer import Engineer # Assuming this is your SQLAlchemy model

class EngineerTable(ctk.CTkFrame):
    def __init__(self, parent, session, on_page_change=None):
        super().__init__(parent, fg_color="transparent")

        self.session = session
        self.on_page_change = on_page_change
        self.current_page = 1
        self.rows_per_page = 10
        self.total_pages = 1
        self.selected_rows = set()
        self.all_engineer_ids_on_current_page = [] # Track IDs for select all

        # --- State Variables for Advanced Features ---
        self.sort_column = None # Name of the column to sort by
        self.sort_direction = None # 'asc' or 'desc'
        self.column_filters = {} # {column_name: filter_text}
        self._resize_job = None # For debouncing resize events
        # Storing dict: {'widget': CTkButton/CTkCheckBox, 'var': var (for Select)}
        self.header_widgets = {}
        self._current_menu = None # Track currently open menu
        self.columns = [
            {"name": "Select", "width": 50, "min_width": 50, "weight": 0, "select_all": True, "hideable": False},
            {"name": "ID", "width": 50, "min_width": 50, "weight": 0, "db_field": "id", "sortable": True, "filterable": True},
            {"name": "Name", "width": 130, "min_width": 100, "weight": 3, "db_field": "name", "sortable": True, "filterable": True},
            {"name": "Company", "width": 120, "min_width": 100, "weight": 2, "db_field": "company_name", "sortable": True, "filterable": True},
            {"name": "DoB", "width": 90, "min_width": 90, "weight": 0, "db_field": "date_of_birth", "sortable": True, "filterable": False},
            {"name": "Technical Field", "width": 120, "min_width": 100, "weight": 2, "db_field": "field_name", "sortable": True, "filterable": True},
            {"name": "Expertise", "width": 120, "min_width": 100, "weight": 2, "db_field": "evaluation_target", "sortable": True, "filterable": True},
            {"name": "Experience", "width": 80, "min_width": 80, "weight": 0, "db_field": "experience", "sortable": True, "filterable": True},
            {"name": "Actions", "width": 180, "min_width": 180, "weight": 0, "hideable": False}
        ]
        
        # --- Column Visibility ---
        self.column_visibility = {col["name"]: True for col in self.columns}
        
        # --- Layout Constants ---
        self.base_left_padding = 10
        self.vertical_padding = 5
        self.min_total_width = 800
        
        # --- Configure Main Frame ---
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Data section expands
        
        # --- Configure Main Frame ---
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Data section expands
        
        # --- Create Header Frame ---
        self.header_container = ctk.CTkFrame(self, fg_color="transparent")
        self.header_container.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.header_container.grid_columnconfigure(0, weight=1)
        
        # --- Create Data Container ---
        self.data_container = ctk.CTkFrame(self, fg_color="transparent")
        self.data_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.data_container.grid_columnconfigure(0, weight=1)
        self.data_container.grid_rowconfigure(0, weight=1)
        
        # --- Create Horizontal Scrollbar (shared between header and data) ---
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal")
        self.h_scrollbar.grid(row=2, column=0, sticky="ew", padx=10)
        
        # --- Create Header Canvas ---
        self.header_canvas = tk.Canvas(self.header_container, bg="#252525", highlightthickness=0, height=40)
        self.header_canvas.grid(row=0, column=0, sticky="ew")
        self.header_canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        # --- Create Header Frame inside Canvas ---
        self.header_frame = ctk.CTkFrame(self.header_canvas, fg_color="#252525", corner_radius=8)
        self.header_window = self.header_canvas.create_window(0, 0, window=self.header_frame, anchor="nw")
        
        # --- Create Data Canvas with Vertical Scrollbar ---
        self.data_canvas = tk.Canvas(self.data_container, bg="#1E1E1E", highlightthickness=0)
        self.data_canvas.grid(row=0, column=0, sticky="nsew")
        
        # --- Create Vertical Scrollbar ---
        self.v_scrollbar = ttk.Scrollbar(self.data_container, orient="vertical", command=self.data_canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.data_canvas.configure(yscrollcommand=self.v_scrollbar.set)
        
        # Configure the canvases to update the scrollbar
        self.header_canvas.configure(xscrollcommand=self.h_scrollbar.set)
        self.data_canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        # --- Configure Horizontal Scrollbar to Control Both Canvases ---
        self.h_scrollbar.config(command=self._on_h_scroll)
        
        # --- Create Data Frame inside Canvas ---
        self.content_frame = ctk.CTkFrame(self.data_canvas, fg_color="transparent")
        self.content_window = self.data_canvas.create_window(0, 0, window=self.content_frame, anchor="nw")
        
        # --- Configure Scrollbar Styles ---
        style = ttk.Style()
        style.configure("Horizontal.TScrollbar", background="#4a4a4a", troughcolor="#333333")
        style.configure("Vertical.TScrollbar", background="#4a4a4a", troughcolor="#333333")
        
        # --- Bind Events for Scroll Region Updates ---
        self.header_frame.bind("<Configure>", lambda e: self._update_scroll_region(self.header_canvas))
        self.content_frame.bind("<Configure>", lambda e: self._update_scroll_region(self.data_canvas))
        self.bind("<Configure>", self._on_window_resize)

        # --- Initial Draw ---
        self._redraw_headers()
        # Load data after a short delay to ensure UI is ready
        self.after(100, self.load_data)
        
        # Update scrollable frame when window is resized
        self.bind('<Configure>', self._update_scrollable_width)

    # --- Resize Handling (Target content_frame + Force Update) ---
    def _on_resize(self, event=None):
        if self._resize_job: self.after_cancel(self._resize_job)
        self._resize_job = self.after(50, self._perform_resize, event)

    def _perform_resize(self, event=None):
        """Calculates and applies column widths and updates scroll region."""
        if event: parent_width = event.width
        else:
            if not self.winfo_exists(): return
            parent_width = self.winfo_width()
        available_width = parent_width - 20
        if not self.header_frame.winfo_exists(): return
        visible_columns = [c for c in self.columns if self.column_visibility[c['name']]]
        if not visible_columns: return

        total_weight = sum(col["weight"] for col in visible_columns if col["weight"] > 0)
        fixed_width = sum(col["min_width"] for col in visible_columns if col["weight"] == 0)
        width_per_weight = max(0, available_width - fixed_width) / total_weight if total_weight > 0 else 0

        current_grid_col = 0
        for col in self.columns:
            if not self.column_visibility[col['name']]: continue
            new_width = max(col["min_width"], int(col["weight"] * width_per_weight)) if col["weight"] > 0 else col["min_width"]
            # Configure columns in header frame
            self.header_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=0)  # Set weight to 0 for fixed width
            # Configure columns ONLY in the intermediate content_frame
            self.content_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=0)  # Set weight to 0 for fixed width
            current_grid_col += 1

        # --- Force Scrollable Frame Update ---
        self.data_canvas.update_idletasks() # Allow tkinter to process geometry changes
        self.header_frame.update_idletasks()
        self._update_scrollable_width() # Update the scroll regions


    # --- Header Creation ---
    def _redraw_headers(self):
        """Clears and redraws headers with a simple structure and consistent styling."""
        for widget in self.header_frame.winfo_children(): widget.destroy()
        self.header_widgets.clear()
        
        # Create header cells for each visible column
        current_grid_col = 0
        
        for col_idx, col_def in enumerate(self.columns):
            if not self.column_visibility[col_def['name']]:
                continue
                
            # Calculate exact width for the column
            col_width = max(col_def.get('min_width', 50), col_def['width'])
            
            # Create a fixed-width frame for this column
            col_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent", width=col_width, height=40)
            col_frame.grid(row=0, column=current_grid_col, sticky="nsew", padx=0, pady=0)
            col_frame.grid_propagate(False)  # Force the frame to maintain its size
            
            # Create the header content based on column type
            if col_def.get('select_all', False):
                # Create checkbox for Select All
                var = tk.BooleanVar(value=False)
                checkbox = ctk.CTkCheckBox(
                    col_frame, text="", variable=var, 
                    width=20, height=20, corner_radius=3,
                    fg_color="#1f538d", hover_color="#2e6fbd",
                    border_color="#666666", border_width=1,
                    command=self._on_select_all_clicked
                )
                checkbox.place(relx=0.5, rely=0.5, anchor="center")
                self.header_widgets[col_def['name']] = {'widget': checkbox, 'var': var}
            else:
                # Create button for sortable columns
                button = ctk.CTkButton(
                    col_frame, text=col_def['name'],
                    fg_color="transparent", text_color="white",
                    hover_color="#333333", anchor="w",
                    height=28, width=col_width-10, corner_radius=0,
                    font=("Arial Bold", 13)
                )
                button.place(relx=0.5, rely=0.5, anchor="center")
                
                # Add right-click menu for column operations
                button.bind("<Button-3>", lambda e, col=col_def: self._show_column_menu(e, col))
                
                # Add sorting capability if column is sortable
                if col_def.get('sortable', False):
                    button.configure(command=lambda col=col_def: self._toggle_sort(col['name']))
                
                # Add filter indicator if column is filterable
                if col_def.get('filterable', False):
                    # Store button for later reference
                    self.header_widgets[col_def['name']] = {'widget': button}
            
            current_grid_col += 1
            
        # Update header indicators (sort, filter)
        self._update_header_indicators()
        
    def _update_header_indicators(self):
        """Update header indicators for sorting and filtering"""
        # Update sort indicators
        if self.sort_column and self.sort_column in self.header_widgets:
            widget_info = self.header_widgets[self.sort_column]
            if 'widget' in widget_info:
                button = widget_info['widget']
                # Add sort direction indicator to button text
                direction_symbol = "↑" if self.sort_direction == "asc" else "↓"
                col_name = self.sort_column
                button.configure(text=f"{col_name} {direction_symbol}")
        
        # Update filter indicators
        for col_name, filter_value in self.column_filters.items():
            if col_name in self.header_widgets and 'widget' in self.header_widgets[col_name]:
                button = self.header_widgets[col_name]['widget']
                # Add filter indicator to button text
                if filter_value:
                    button.configure(text=f"{col_name} 🔍")


    # --- Data Loading (Uses content_frame, Update Scrollregion) ---
    def load_data(self):
        try:
            # --- Clear existing content ---
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # --- Query Database with Filtering and Sorting ---
            query = self.session.query(Engineer)
            
            # Apply filters if any
            if self.column_filters:
                for col_name, filter_text in self.column_filters.items():
                    col_info = next((c for c in self.columns if c['name'] == col_name), None)
                    if col_info and 'db_field' in col_info and filter_text:
                        db_field = col_info['db_field']
                        query = query.filter(getattr(Engineer, db_field).ilike(f'%{filter_text}%'))
            
            # Apply sorting if specified
            if self.sort_column and self.sort_direction:
                col_info = next((c for c in self.columns if c['name'] == self.sort_column), None)
                if col_info and 'db_field' in col_info:
                    db_field = col_info['db_field']
                    sort_func = asc if self.sort_direction == 'asc' else desc
                    query = query.order_by(sort_func(getattr(Engineer, db_field)))
            
            # Calculate pagination
            total_records = query.count()
            self.total_pages = max(1, math.ceil(total_records / self.rows_per_page))
            self.current_page = min(self.current_page, self.total_pages)
            
            # Get paginated results
            offset = (self.current_page - 1) * self.rows_per_page
            engineers = query.offset(offset).limit(self.rows_per_page).all()
            
            # Store all IDs on current page for select all functionality
            self.all_engineer_ids_on_current_page = [e.id for e in engineers]
            
            # --- Create a grid layout for the content ---
            # First, create a row for column headers
            current_grid_col = 0
            
            # Create rows for each engineer
            for row_idx, engineer in enumerate(engineers):
                # Determine row color based on alternating pattern
                row_color = "#2A2A2A" if row_idx % 2 == 0 else "#333333"
                
                # Create a row container
                row_frame = ctk.CTkFrame(self.content_frame, fg_color=row_color, corner_radius=0)
                row_frame.grid(row=row_idx, column=0, sticky="ew", pady=(0, 1))
                
                # Add cells for each visible column
                current_grid_col = 0
                for col_idx, col_def in enumerate(self.columns):
                    if not self.column_visibility[col_def['name']]:
                        continue
                    
                    # Calculate exact width for the column
                    col_width = max(col_def.get('min_width', 50), col_def['width'])
                    
                    # Create a fixed-width frame for this cell
                    cell_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=col_width, height=40)
                    cell_frame.grid(row=0, column=current_grid_col, sticky="nsew", padx=0, pady=0)
                    cell_frame.grid_propagate(False)  # Force the frame to maintain its size
                    
                    # Add content based on column type
                    if col_def['name'] == "Select":
                        # Create checkbox for row selection
                        var = tk.BooleanVar(value=engineer.id in self.selected_rows)
                        checkbox = ctk.CTkCheckBox(
                            cell_frame, text="", variable=var, 
                            width=20, height=20, corner_radius=3,
                            fg_color="#1f538d", hover_color="#2e6fbd",
                            border_color="#666666", border_width=1,
                            command=lambda e_id=engineer.id, v=var: self.toggle_row_selection(e_id, v.get())
                        )
                        checkbox.place(relx=0.5, rely=0.5, anchor="center")
                    
                    elif col_def['name'] == "Actions":
                        # Create action buttons container
                        actions_frame = ctk.CTkFrame(cell_frame, fg_color="transparent")
                        actions_frame.place(relx=0.5, rely=0.5, anchor="center")
                        
                        # View/Edit button
                        view_btn = ctk.CTkButton(
                            actions_frame, text="View/Edit",
                            fg_color="#1f538d", hover_color="#2e6fbd",
                            height=24, width=80, corner_radius=4,
                            command=lambda e=engineer: self.edit_engineer(e)
                        )
                        view_btn.grid(row=0, column=0, padx=(0, 5))
                        
                        # Delete button
                        delete_btn = ctk.CTkButton(
                            actions_frame, text="Delete",
                            fg_color="#8B0000", hover_color="#A52A2A",
                            height=24, width=80, corner_radius=4,
                            command=lambda e_id=engineer.id: self._confirm_delete(e_id)
                        )
                        delete_btn.grid(row=0, column=1)
                    
                    else:
                        # Get field value based on db_field mapping
                        if 'db_field' in col_def:
                            # Handle special formatting for specific fields
                            if col_def['db_field'] == 'date_of_birth' and getattr(engineer, col_def['db_field']):
                                value = getattr(engineer, col_def['db_field']).strftime('%Y-%m-%d')
                            elif col_def['db_field'] == 'is_project_manager':
                                value = "Yes" if getattr(engineer, col_def['db_field']) else "No"
                            else:
                                value = getattr(engineer, col_def['db_field'], "-")
                                if value is None: value = "-"
                        else:
                            value = "-"
                        
                        # Create label for regular cell
                        label = ctk.CTkLabel(
                            cell_frame,
                            text=str(value),
                            fg_color="transparent",
                            text_color="white",
                            anchor="w",
                            font=("Arial", 12),
                            width=col_width-20,
                            height=28
                        )
                        label.place(relx=0.5, rely=0.5, anchor="center")
                    
                    current_grid_col += 1
            
            # --- Force scrollable frame update AFTER rows are added ---
            self.data_canvas.update_idletasks()
            self._update_scrollable_width()

        # --- Exception Handling ---
        except Exception as e:
            print(f"Error loading data: {e}")
            traceback.print_exc()
            try: show_notification(self, f"{str(e)}", "Error Loading Data", "error")
            except Exception as ne: print(f"--- ERROR IN NOTIFICATION SERVICE ---"); print(f"Original error: {e}"); print(f"Notification error: {ne}"); traceback.print_exc(); messagebox.showerror("Error Loading Data", f"{str(e)}\n\n(Notification service also failed)")


    # --- Action Button Creation (Combined View/Edit) ---
    def _create_actions_frame(self, parent, engineer):
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.grid_columnconfigure((0, 1), weight=1, minsize=90)
        button_style = {"height": 28, "font": ("Arial", 12), "corner_radius": 5}
        details_btn = ctk.CTkButton(actions_frame, text="View/Edit",
                                    command=lambda eng=engineer: self.show_details_or_edit(eng),
                                    fg_color="#2B5EA7", hover_color="#2573A7", **button_style)
        details_btn.grid(row=0, column=0, padx=(20, 5), pady=3, sticky="ew")
        delete_btn = ctk.CTkButton(actions_frame, text="Delete",
                                   command=lambda eng=engineer: self.delete_engineer(eng),
                                   fg_color="#A72B2B", hover_color="#C0392B", **button_style)
        delete_btn.grid(row=0, column=1, padx=(5, 20), pady=3, sticky="ew")
        return actions_frame

    # --- Select All / Row Selection Logic ---
    def toggle_all_rows(self, select_all_state):
        ids_on_page = self.all_engineer_ids_on_current_page; changed = False
        if select_all_state:
            newly_selected = set(ids_on_page) - self.selected_rows
            if newly_selected: self.selected_rows.update(newly_selected); changed = True
        else:
            removed_count = len(self.selected_rows.intersection(ids_on_page))
            if removed_count > 0: self.selected_rows.difference_update(ids_on_page); changed = True
        if changed: self.load_data() # Reload to update checkboxes
    def _update_select_all_checkbox_state(self):
        """Update the state of the select all checkbox based on current selections."""
        select_all_widget_data = self.header_widgets.get("Select")
        if select_all_widget_data:
            select_all_var = select_all_widget_data.get("var")
            if select_all_var:
                ids_on_page = set(self.all_engineer_ids_on_current_page)
                if not ids_on_page: 
                    select_all_var.set(False)
                elif all(id in self.selected_rows for id in ids_on_page): 
                    select_all_var.set(True)
                else: 
                    select_all_var.set(False)
    def toggle_row_selection(self, engineer_id, is_selected):
        """Toggle selection of a row and update the selected rows list."""
        if is_selected:
            if engineer_id not in self.selected_rows:
                self.selected_rows.add(engineer_id)
        else:
            if engineer_id in self.selected_rows:
                self.selected_rows.remove(engineer_id)
                
        # Update select all checkbox state
        self._update_select_all_checkbox_state()
        
    def _on_select_all_clicked(self):
        """Handle click on the select all checkbox."""
        select_all_widget_data = self.header_widgets.get("Select")
        if select_all_widget_data:
            select_all_var = select_all_widget_data.get("var")
            if select_all_var:
                is_selected = select_all_var.get()
                if is_selected:
                    # Select all rows on current page
                    for engineer_id in self.all_engineer_ids_on_current_page:
                        if engineer_id not in self.selected_rows:
                            self.selected_rows.add(engineer_id)
                else:
                    # Deselect all rows on current page
                    for engineer_id in self.all_engineer_ids_on_current_page:
                        if engineer_id in self.selected_rows:
                            self.selected_rows.remove(engineer_id)
                # Refresh the table to update checkboxes
                self.load_data()
                
    # --- Methods for External Buttons ---
    def select_all_on_page(self):
        ids_on_page = self.all_engineer_ids_on_current_page
        newly_selected = [id for id in ids_on_page if id not in self.selected_rows]
        self.selected_rows.update(ids_on_page)
        if newly_selected: self.load_data(); show_notification(self, f"Selected {len(ids_on_page)} on page.", "Selection", "info")
        else: show_notification(self, "All on page already selected.", "Selection", "warning")
    def clear_selection(self):
        if self.selected_rows: self.selected_rows.clear(); self.load_data(); show_notification(self, "Selection cleared.", "Selection", "info")
        else: show_notification(self, "No engineers selected.", "Selection", "warning")


    # --- Other Methods (Pagination, Set Rows, Clear Filters, Reset, Callbacks, Get Selected, Delete) ---
    def set_rows_per_page(self, value):
        try:
            new_rows = int(value)
            if new_rows > 0: self.rows_per_page = new_rows; self.current_page = 1; self.load_data()
            else: show_notification(self, "Rows > 0.", "Invalid Value", "warning")
        except ValueError: show_notification(self, "Enter number.", "Invalid Input", "warning")
    def next_page(self):
        if self.current_page < self.total_pages: self.current_page += 1; self.load_data()
    def prev_page(self):
        if self.current_page > 1: self.current_page -= 1; self.load_data()
    def go_to_page(self, page_num):
        try:
            page = int(page_num)
            if 1 <= page <= self.total_pages: self.current_page = page; self.load_data()
            else: show_notification(self, f"Page must be 1-{self.total_pages}", "Invalid Page", "warning")
        except ValueError: show_notification(self, "Enter valid page number.", "Invalid Input", "warning")
    def clear_all_filters(self):
        if self.column_filters: self.column_filters.clear(); self.current_page = 1; self.load_data()
    def reset_view(self):
        visibility = any(not v for v in self.column_visibility.values())
        filters = bool(self.column_filters); sort = bool(self.sort_column)
        self.column_filters.clear(); self.sort_column = None; self.sort_direction = None
        self.column_visibility = {col['name']: True for col in self.columns}
        if visibility or filters or sort: self.current_page = 1; self._redraw_table_layout()
    def set_page_change_callback(self, callback): self.on_page_change = callback
    def get_selected_engineer_ids(self): return set(self.selected_rows)
    def get_selected_engineers(self):
        if not self.selected_rows: return []
        try: return self.session.query(Engineer).filter(Engineer.id.in_(self.selected_rows)).all()
        except Exception as e: show_notification(self, f"{e}", "Error Fetching", "error"); return []
    def delete_engineer(self, engineer):
        if not messagebox.askyesno("Confirm Delete", f"Delete {getattr(engineer, 'name', 'this engineer')}?"): return
        try:
            self.session.delete(engineer); self.session.commit()
            show_notification(self, f"Engineer deleted.", "Deleted", "info")
            self.selected_rows.discard(engineer.id); self.load_data()
        except Exception as e: self.session.rollback(); show_notification(self, f"{e}", "Delete Error", "error"); traceback.print_exc()
    def add_engineer(self):
        dialog = EngineerDialog(self, self.session, on_save=self.load_data)
    def delete_selected(self):
        if not self.selected_rows: show_notification(self, "Select engineers first.", "No Selection", "warning"); return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(self.selected_rows)} selected engineer(s)?"): return
        count = 0
        try:
            engineers = self.session.query(Engineer).filter(Engineer.id.in_(self.selected_rows)).all()
            for engineer in engineers: self.session.delete(engineer); count += 1
            self.session.commit(); show_notification(self, f"{count} engineer(s) deleted.", "Deleted", "info")
            self.selected_rows.clear(); self.load_data()
        except Exception as e: self.session.rollback(); show_notification(self, f"{e}", "Delete Error", "error"); traceback.print_exc()

    # Ensure edit_engineer method exists if Details button calls it
    def edit_engineer(self, engineer):
         """Opens the dialog to edit an existing engineer."""
         dialog = EngineerDialog(self, self.session, engineer=engineer, on_save=self.load_data)

    # This method is no longer needed with the simplified approach

    def _update_scrollable_width(self, event=None):
        """Update the content width to ensure horizontal scrolling works"""
        # Calculate total width of visible columns
        total_width = sum(col['width'] for col in self.columns if self.column_visibility[col['name']])
        # Ensure minimum width to force scrolling
        total_width = max(total_width, self.min_total_width)
        
        # Set both header and content frames to the same width
        self.header_frame.configure(width=total_width)
        self.content_frame.configure(width=total_width)
        
        # Update the canvas scroll regions
        self._update_scroll_region(self.header_canvas)
        self._update_scroll_region(self.data_canvas)
        
        # Ensure the canvas widths match the container width
        container_width = self.winfo_width() - 20  # Account for padding
        if container_width > 0:
            self.header_canvas.configure(width=container_width)
            self.data_canvas.configure(width=container_width)
    
    def _update_scroll_region(self, canvas):
        """Update the scroll region for a canvas"""
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def _on_header_scroll(self, *args):
        """Synchronize header scrolling with data canvas"""
        self.data_canvas.xview(*args)
        # Update the horizontal scrollbar position
        self.h_scrollbar.set(*self.data_canvas.xview())
    
    def _on_data_scroll(self, *args):
        """Synchronize data scrolling with header canvas"""
        self.header_canvas.xview(*args)
        # Update the horizontal scrollbar position
        self.h_scrollbar.set(*self.header_canvas.xview())
    
    def _on_h_scroll(self, *args):
        """Synchronize horizontal scrolling between header and data canvases"""
        # Scroll both canvases together
        self.header_canvas.xview(*args)
        self.data_canvas.xview(*args)
    
    def _on_window_resize(self, event):
        """Handle window resize events"""
        # Only process events from the main window
        if event.widget == self:
            # Update canvas widths to match the window
            width = max(self.winfo_width() - 20, 100)  # Account for padding
            self.header_canvas.configure(width=width)
            self.data_canvas.configure(width=width)
            
            # Ensure scroll regions are updated
            self._update_scroll_region(self.header_canvas)
            self._update_scroll_region(self.data_canvas)
            
            # Make sure the header and content frames have the same width
            total_width = sum(col['width'] for col in self.columns if self.column_visibility[col['name']])
            total_width = max(total_width, self.min_total_width)
            self.header_frame.configure(width=total_width)
            self.content_frame.configure(width=total_width)

