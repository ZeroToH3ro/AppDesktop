# Required imports for the enhanced functionality
import customtkinter as ctk
import tkinter as tk
from tkinter import Menu, messagebox, ttk # Import ttk for themed scrollbar
import sqlalchemy
from sqlalchemy import func, asc, desc # For filtering, sorting
import math
import traceback # For detailed error logging

# Imports from your original code structure
# Ensure these paths are correct for your project
from src.services.notification import notification
# Assuming EngineerDialog handles both view and edit
from src.views.engineer_dialog import EngineerDialog
# from src.views.engineer_detail import EngineerDetailDialog # Potentially removed if merged into EngineerDialog
from src.models.engineer import Engineer # Assuming this is your SQLAlchemy model

# Simple notification function (using messagebox as fallback)
def show_notification(parent, message, title="Notification", type="info"):
    """Show a notification message to the user"""
    try:
        # Try using the imported notification service if available
        if type == "info":
            notification.show_info(title, message) # Adjust method name if needed
        elif type == "warning":
            notification.show_warning(title, message) # Adjust method name if needed
        elif type == "error":
            notification.show_error(title, message) # Adjust method name if needed
        else:
            notification.show_info(title, message)
    except Exception:
        # Fallback to messagebox if notification service fails or is not fully implemented
        print(f"Notification service fallback: {title} - {message}")
        if type == "info":
            messagebox.showinfo(title, message, parent=parent)
        elif type == "warning":
            messagebox.showwarning(title, message, parent=parent)
        elif type == "error":
            messagebox.showerror(title, message, parent=parent)
        else:
            messagebox.showinfo(title, message, parent=parent)


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

        # --- Column Definitions (UPDATED: Renamed, New Columns Added) ---
        # !!! USER ACTION REQUIRED: Verify 'db_field' names match your Engineer model !!!
        self.columns = [
            {"name": "Select",          "width": 50, "weight": 0, "min_width": 50,  "sortable": False, "filterable": False, "hideable": False, "select_all": True},
            {"name": "ID",              "width": 50, "weight": 0, "min_width": 50,  "db_field": "id",                  "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Name",            "width": 130,"weight": 3, "min_width": 100, "db_field": "name",                "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Company",         "width": 120,"weight": 2, "min_width": 100, "db_field": "company_name",        "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "DoB",             "width": 90, "weight": 0, "min_width": 90,  "db_field": "date_of_birth",       "sortable": True,  "filterable": False, "hideable": True},
            {"name": "Technical Field", "width": 120,"weight": 2, "min_width": 100, "db_field": "field_name",          "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Expertise",       "width": 120,"weight": 2, "min_width": 100, "db_field": "evaluation_target",   "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Is PM",           "width": 60, "weight": 0, "min_width": 60,  "db_field": "is_project_manager",  "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Experience",      "width": 80, "weight": 0, "min_width": 80,  "db_field": "years_experience",    "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Rating",          "width": 70, "weight": 0, "min_width": 70,  "db_field": "rating",              "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Actions",         "width": 180,"weight": 0, "min_width": 180, "sortable": False, "filterable": False, "hideable": False}
        ]
        # Initialize visibility state
        self.column_visibility = {col['name']: True for col in self.columns}

        # --- Constants for Padding ---
        self.vertical_padding = 3
        self.base_left_padding = 20

        # --- Layout Setup ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Allow table_container to expand vertically

        # --- Header Frame ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=8)
        self.header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(10, 0))
        self.header_frame.grid_rowconfigure(0, weight=0)


        # --- Table Container (Holds Canvas and Scrollbars) ---
        self.table_container = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=8)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.table_container.grid_columnconfigure(0, weight=1) # Canvas expands horizontally
        self.table_container.grid_columnconfigure(1, weight=0) # V scrollbar fixed width
        self.table_container.grid_rowconfigure(0, weight=1)    # Canvas expands vertically
        self.table_container.grid_rowconfigure(1, weight=0)    # H scrollbar fixed height

        # --- Canvas for Data Area ---
        # Using tk.Canvas for potentially more reliable scroll region behavior
        self.canvas = tk.Canvas(self.table_container, bg="#1E1E1E", borderwidth=0, highlightthickness=0)

        # --- Scrollbars (using CTkScrollbar for better theme matching) ---
        self.h_scrollbar = ctk.CTkScrollbar(self.table_container, orientation="horizontal", command=self.canvas.xview)
        self.v_scrollbar = ctk.CTkScrollbar(self.table_container, orientation="vertical", command=self.canvas.yview)

        # Configure Canvas to use Scrollbars
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        # Grid Canvas and Scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # --- Content Frame (Inside Canvas) ---
        self.content_frame = ctk.CTkFrame(self.canvas, fg_color="#1E1E1E") # Match canvas bg
        # Place content_frame onto the canvas using create_window
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", tags="content_frame")

        # --- Bind Events for Scroll Region Updates ---
        # Update scrollregion when content_frame size changes
        self.content_frame.bind("<Configure>", self._on_content_frame_configure)
        # Update the width of the frame inside canvas when canvas resizes
        self.canvas.bind("<Configure>", self._on_canvas_configure)


        # --- Initial Draw ---
        self._redraw_headers()
        self.bind("<Configure>", self._on_resize) # Bind main frame resize
        self.after(100, self.load_data)

    # --- Event Handlers for Manual Scrolling ---
    def _on_content_frame_configure(self, event=None):
        """Called when the size of the content_frame changes."""
        # Update the canvas scroll region to match the content frame's bounding box
        self.canvas.update_idletasks() # Ensure frame size is calculated
        bbox = self.canvas.bbox("all")
        if bbox: # Ensure bbox is valid
            self.canvas.configure(scrollregion=bbox)
            # print(f"Scrollregion updated: {bbox}") # Debug print
        # else:
            # print("Scrollregion update skipped: bbox is None")

    def _on_canvas_configure(self, event=None):
        """Called when the canvas size changes, adjust the frame width if needed."""
        # Make the frame inside the canvas match the canvas width
        # This primarily helps with vertical scrolling appearance
        canvas_width = self.canvas.winfo_width()
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)


    # --- Resize Handling (Target content_frame) ---
    def _on_resize(self, event=None):
        if self._resize_job: self.after_cancel(self._resize_job)
        self._resize_job = self.after(50, self._perform_resize, event)

    def _perform_resize(self, event=None):
        """Calculates and applies column widths to header and content frames."""
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
            self.header_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=col['weight'])
            # Configure columns ONLY in the intermediate content_frame
            self.content_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=col['weight'])
            current_grid_col += 1

        # --- Explicitly update scroll region after resize ---
        self.after(10, self._on_content_frame_configure)


    # --- Header Creation (Simplified Structure - Unchanged) ---
    def _redraw_headers(self):
        """Clears and redraws headers with a simple structure and consistent styling."""
        for widget in self.header_frame.winfo_children(): widget.destroy()
        self.header_widgets.clear()

        header_button_style = {"fg_color": "transparent", "hover_color": "#353535", "text_color": "#E0E0E0",
                               "font": ("Arial Bold", 12), "anchor": "w", "height": 25,
                               "corner_radius": 0, "border_width": 0}

        current_grid_col = 0
        for col_info in self.columns:
            col_name = col_info['name']
            if not self.column_visibility[col_name]:
                self.header_frame.grid_columnconfigure(current_grid_col, weight=0, minsize=0)
                self.content_frame.grid_columnconfigure(current_grid_col, weight=0, minsize=0)
                continue

            if col_name == "Select": # Removed select_all check
                select_all_var = tk.BooleanVar()
                select_all_cb = ctk.CTkCheckBox(
                    self.header_frame, text="", variable=select_all_var,
                    command=lambda: self.toggle_all_rows(select_all_var.get()),
                    width=20, height=20, fg_color="#1f538d", hover_color="#3b8ed0",
                    border_color="#4F4F4F", corner_radius=3
                )
                select_all_cb.grid(row=0, column=current_grid_col, sticky="w", padx=(self.base_left_padding, 0), pady=self.vertical_padding)
                self.header_widgets[col_name] = {"widget": select_all_cb, "var": select_all_var}
            else:
                header_button = ctk.CTkButton(
                    self.header_frame, text=col_name, **header_button_style
                )
                header_button.grid(row=0, column=current_grid_col, sticky="w", padx=(self.base_left_padding, 5), pady=self.vertical_padding)
                self.header_widgets[col_name] = {'widget': header_button}

                is_interactive = col_info.get('sortable', False) or col_info.get('filterable', False) or col_info.get('hideable', True)
                if is_interactive and col_name != "Actions":
                    header_button.configure(command=lambda c=col_name: self._show_header_menu(c))
                else:
                    header_button.configure(hover=False, command=None)

            # Configure column properties
            self.header_frame.grid_columnconfigure(current_grid_col, weight=col_info['weight'], minsize=col_info['min_width'])
            self.content_frame.grid_columnconfigure(current_grid_col, weight=col_info['weight'], minsize=col_info['min_width'])
            current_grid_col += 1

        self.after(50, self._perform_resize)
        self.after(55, self._update_header_indicators)

    # --- Header Menu Logic (Unchanged) ---
    def _show_header_menu(self, column_name):
        if self._current_menu and self._current_menu.winfo_exists(): self._current_menu.destroy()
        col_info = next((c for c in self.columns if c['name'] == column_name), None)
        if not col_info or column_name not in self.header_widgets: return
        button = self.header_widgets[column_name].get('widget')
        if not isinstance(button, ctk.CTkButton): return
        menu = Menu(button, tearoff=0, background="#333333", foreground="#FFFFFF", activebackground="#444444", activeforeground="#FFFFFF", relief="flat", borderwidth=0)
        if col_info.get('sortable'):
            menu.add_command(label="Sort Ascending", command=lambda: self._set_sort(column_name, 'asc'))
            menu.add_command(label="Sort Descending", command=lambda: self._set_sort(column_name, 'desc'))
            if self.sort_column == column_name: menu.add_separator(); menu.add_command(label="Clear Sort", command=lambda: self._set_sort(None, None))
            menu.add_separator()
        if col_info.get('filterable'):
            filter_text = self.column_filters.get(column_name, ""); filter_label = f"Filter..." if not filter_text else f"Filter: '{filter_text}'"
            menu.add_command(label=filter_label, command=lambda: self._prompt_filter(column_name))
            if filter_text: menu.add_command(label="Clear Filter", command=lambda: self._clear_column_filter(column_name))
            menu.add_separator()
        if col_info.get('hideable', True): menu.add_command(label="Hide Column", command=lambda: self._toggle_column_visibility(column_name, False)); menu.add_separator()
        menu.add_command(label="Show Columns...", command=self._show_column_chooser)
        menu.post(button.winfo_rootx() + 5, button.winfo_rooty() + button.winfo_height()); self._current_menu = menu

    # --- Sorting Logic (Unchanged) ---
    def _set_sort(self, column_name, direction):
        self.sort_column = column_name; self.sort_direction = direction; self.current_page = 1; self.load_data()

    # --- Header Indicator Update (Unchanged) ---
    def _update_header_indicators(self):
        for name, data in self.header_widgets.items():
            widget = data.get('widget')
            if isinstance(widget, ctk.CTkButton) and widget.winfo_exists():
                col_info = next((c for c in self.columns if c['name'] == name), None)
                if not col_info: continue
                base_text = name; sort_indicator = ""; menu_indicator = ""
                if name == self.sort_column: sort_indicator = " ⯅" if self.sort_direction == 'asc' else " ⯆"
                is_interactive = col_info.get('sortable', False) or col_info.get('filterable', False) or col_info.get('hideable', True)
                if is_interactive and name != "Actions": menu_indicator = " ⋮"
                widget.configure(text=base_text + sort_indicator + menu_indicator)

    # --- Filtering Logic (Unchanged) ---
    def _prompt_filter(self, column_name):
        dialog = ctk.CTkInputDialog(text=f"Filter {column_name}:", title=f"Filter {column_name}")
        val = dialog.get_input();
        if val is not None: self.apply_specific_filter(column_name, val.strip())
    def _clear_column_filter(self, column_name):
        self.apply_specific_filter(column_name, "")
    def apply_specific_filter(self, field_name, filter_value):
        col_info = next((c for c in self.columns if c["name"] == field_name), None)
        if not col_info and field_name is not None: print(f"Warning: Invalid filter field '{field_name}'"); return
        self.column_filters.clear()
        if field_name and filter_value: self.column_filters[field_name] = filter_value
        print(f"Applying filter: {self.column_filters}")
        self.current_page = 1; self.load_data()

    # --- Column Visibility Logic (Unchanged) ---
    def _toggle_column_visibility(self, column_name, visible):
        visible_count = sum(1 for v in self.column_visibility.values() if v)
        if not visible and visible_count <= 1: messagebox.showwarning("Cannot Hide", "Cannot hide the last column."); return
        self.column_visibility[column_name] = visible; self._redraw_table_layout()
    def _show_column_chooser(self):
        dialog = ctk.CTkToplevel(self); dialog.title("Show/Hide Columns"); dialog.transient(self); dialog.grab_set()
        vars = {}; frame = ctk.CTkFrame(dialog); frame.pack(padx=20, pady=10, fill="both", expand=True); row = 0
        for col in self.columns:
            name = col['name'];
            if col.get('hideable', True): var = tk.BooleanVar(value=self.column_visibility[name]); cb = ctk.CTkCheckBox(frame, text=name, variable=var); cb.grid(row=row, column=0, sticky="w", padx=10, pady=2); vars[name] = var; row += 1
        def apply():
            changed = False; new_vis = dict(self.column_visibility)
            for n, v in vars.items():
                if new_vis[n] != v.get(): new_vis[n] = v.get(); changed = True
            allowed = [c['name'] for c in self.columns if c.get('hideable', True)]
            if changed and not any(new_vis[n] for n in allowed): messagebox.showwarning("Error", "Keep at least one column visible.", parent=dialog); return
            if changed: self.column_visibility = new_vis; self._redraw_table_layout()
            dialog.destroy()
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent"); btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Apply", command=apply).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, fg_color="gray").pack(side="left", padx=5)

    def _redraw_table_layout(self):
        # Clear rows from content_frame
        for widget in self.content_frame.winfo_children(): widget.destroy()
        self._redraw_headers();
        self.after(10, self.load_data)

    # --- Data Loading (Uses content_frame, Update Scrollregion) ---
    def load_data(self):
        try:
            # Clear previous rows from the content_frame
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.all_engineer_ids_on_current_page = []

            data_font = ("Arial", 12)

            # --- Build Query (Includes Filters and Sorting) ---
            base_query = self.session.query(Engineer); query = base_query
            # Apply Specific Column Filters
            filter_clauses = []
            for col_name, filter_value in self.column_filters.items():
                 if not filter_value: continue
                 column_info = next((c for c in self.columns if c["name"] == col_name), None)
                 if column_info and column_info.get("filterable") and column_info.get("db_field"):
                     db_field_name = column_info["db_field"]; model_attr = getattr(Engineer, db_field_name, None)
                     if model_attr:
                         try:
                             if db_field_name == 'id': filter_clauses.append(model_attr == int(filter_value)) if filter_value.isdigit() else filter_clauses.append(sqlalchemy.sql.false())
                             elif isinstance(getattr(Engineer, db_field_name).type, sqlalchemy.types.String): filter_clauses.append(model_attr.ilike(f"%{filter_value}%"))
                             elif isinstance(getattr(Engineer, db_field_name).type, sqlalchemy.types.Boolean) and filter_value.lower() in ['true', 'false', 'yes', 'no', '1', '0']: filter_clauses.append(model_attr == (filter_value.lower() in ['true', 'yes', '1']))
                         except Exception as filter_err: print(f"Filter Error: {filter_err}"); traceback.print_exc()
            if filter_clauses: query = query.filter(sqlalchemy.and_(*filter_clauses))
            # Apply Sorting
            if self.sort_column:
                col_info = next((c for c in self.columns if c['name'] == self.sort_column), None)
                if col_info and col_info.get('sortable') and col_info.get('db_field'):
                    db_field = col_info['db_field']; model_attr = getattr(Engineer, db_field, None)
                    if model_attr:
                         try: sort_func = asc if self.sort_direction == 'asc' else desc; query = query.order_by(sort_func(model_attr))
                         except Exception as sort_err: print(f"Sort Error: {sort_err}"); traceback.print_exc()
            # Count and Paginate
            try: total_count = query.count()
            except Exception as count_e: print(f"Count Error: {count_e}"); total_count = 0
            self.total_pages = max(1, math.ceil(total_count / self.rows_per_page) if self.rows_per_page > 0 else 1)
            if self.current_page > self.total_pages: self.current_page = self.total_pages
            offset = (self.current_page - 1) * self.rows_per_page
            engineers = query.offset(offset).limit(self.rows_per_page).all()
            self.all_engineer_ids_on_current_page = [eng.id for eng in engineers if eng.id is not None]

            # --- Insert Data Rows (Into content_frame) ---
            current_grid_col_map = {name: i for i, name in enumerate(col['name'] for col in self.columns if self.column_visibility[col['name']])}
            if not engineers:
                placeholder_label = ctk.CTkLabel(self.content_frame, text="No engineers found.", text_color="gray50", padx=20, pady=20)
                placeholder_label.grid(row=0, column=0, columnspan=len(current_grid_col_map) or 1)
            else:
                for row_idx, engineer in enumerate(engineers):
                    row_color = "#282828" if row_idx % 2 == 0 else "#242424"
                    # Create row_frame inside the content_frame now
                    row_frame = ctk.CTkFrame(self.content_frame, fg_color=row_color, corner_radius=0)
                    # Configure columns within the row_frame
                    for grid_col_idx, col_name in enumerate(current_grid_col_map.keys()):
                         col_info = next(c for c in self.columns if c['name'] == col_name)
                         row_frame.grid_columnconfigure(grid_col_idx, weight=col_info['weight'], minsize=col_info['min_width'])
                    row_frame.grid(row=row_idx, column=0, columnspan=len(current_grid_col_map), sticky="ew", pady=(0, 1))

                    # --- Place content widgets directly into row_frame ---
                    for col_info in self.columns:
                         col_name = col_info['name']
                         if not self.column_visibility[col_name]: continue
                         grid_col = current_grid_col_map[col_name]

                         if col_name == "Select":
                             checkbox_var = tk.BooleanVar(value=(engineer.id in self.selected_rows))
                             checkbox = ctk.CTkCheckBox(row_frame, text="", variable=checkbox_var,
                                                        command=lambda id=engineer.id, var=checkbox_var: self.toggle_row_selection(id, var),
                                                        width=20, height=20, fg_color="#1f538d", hover_color="#3b8ed0",
                                                        border_color="#4F4F4F", corner_radius=3)
                             checkbox.grid(row=0, column=grid_col, sticky="w", padx=(self.base_left_padding, 0), pady=self.vertical_padding)

                         elif col_name == "Actions":
                             actions_frame = self._create_actions_frame(row_frame, engineer)
                             actions_frame.grid(row=0, column=grid_col, sticky="nsew", padx=0, pady=0)

                         elif col_info.get("db_field"):
                             attr_val = getattr(engineer, col_info["db_field"], "-")
                             # Formatting
                             if isinstance(attr_val, bool): text = "Yes" if attr_val else "No"
                             elif isinstance(attr_val, (int, float)): text = str(attr_val)
                             elif hasattr(attr_val, 'strftime'): text = attr_val.strftime('%Y-%m-%d')
                             else: text = str(attr_val) if attr_val is not None else "-"
                             # Label
                             label = ctk.CTkLabel(row_frame, text=text, anchor="w", justify="left",
                                                  font=data_font, text_color="#D0D0D0")
                             label.grid(row=0, column=grid_col, sticky="w", padx=(self.base_left_padding, 5), pady=self.vertical_padding)

            # --- Final UI Updates ---
            if self.on_page_change: self.on_page_change(self.current_page, self.total_pages)
            self._update_header_indicators(); self._update_select_all_checkbox_state()

            # --- Force Scrollregion Update AFTER rows are added ---
            self.content_frame.update_idletasks() # Update the content frame FIRST
            self.canvas.configure(scrollregion=self.canvas.bbox("all")) # Update canvas scroll region
            # print(f"Scrollregion updated after load: {self.canvas.bbox('all')}") # Debug print


        # --- Exception Handling ---
        except Exception as e:
            print(f"Error loading table data: {str(e)}")
            print(traceback.format_exc())
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
        select_all_widget_data = self.header_widgets.get("Select")
        if select_all_widget_data:
            select_all_var = select_all_widget_data.get("var")
            if select_all_var:
                ids_on_page = set(self.all_engineer_ids_on_current_page)
                if not ids_on_page: select_all_var.set(False)
                elif ids_on_page.issubset(self.selected_rows): select_all_var.set(True)
                else: select_all_var.set(False)
    def toggle_row_selection(self, engineer_id, checkbox_var=None):
        if engineer_id in self.selected_rows: self.selected_rows.remove(engineer_id)
        else: self.selected_rows.add(engineer_id)
        self._update_select_all_checkbox_state() # Update header checkbox state

    # --- Dialogs and Data Actions ---
    def show_details_or_edit(self, engineer):
        dialog = EngineerDialog(self, self.session, engineer=engineer, on_save=self.load_data)

    # --- Methods for External Buttons ---
    def select_all_on_page(self):
        ids_on_page = self.all_engineer_ids_on_current_page
        newly_selected = set(ids_on_page) - self.selected_rows
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

