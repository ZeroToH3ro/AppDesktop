# Required imports for the enhanced functionality
import customtkinter as ctk
import tkinter as tk
from tkinter import Menu, messagebox # For dropdown menus and warnings
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
        # Storing dict: {'widget': container_frame/label/checkbox, 'icon_button': btn, 'label': lbl, 'var': var (for Select)}
        self.header_widgets = {}
        self._current_menu = None # Track currently open menu

        # --- Column Definitions (Reduced Min Widths) ---
        # User MUST verify 'db_field' matches their Engineer model attributes
        self.columns = [
            {"name": "Select", "width": 50, "weight": 0, "min_width": 50, "sortable": False, "filterable": False, "hideable": False, "select_all": True},
            {"name": "ID", "width": 50, "weight": 0, "min_width": 50, "db_field": "id", "sortable": True, "filterable": True, "hideable": True},
            {"name": "Name", "width": 150, "weight": 3, "min_width": 120, "db_field": "name", "sortable": True, "filterable": True, "hideable": True},
            {"name": "Company", "width": 120, "weight": 2, "min_width": 100, "db_field": "company_name", "sortable": True, "filterable": True, "hideable": True},
            {"name": "Areas", "width": 120, "weight": 2, "min_width": 100, "db_field": "field_name", "sortable": True, "filterable": True, "hideable": True},
            {"name": "Projects", "width": 120, "weight": 2, "min_width": 100, "db_field": "evaluation_target", "sortable": True, "filterable": True, "hideable": True},
            {"name": "Actions", "width": 180, "weight": 0, "min_width": 180, "sortable": False, "filterable": False, "hideable": False}
        ]
        # Initialize visibility state
        self.column_visibility = {col['name']: True for col in self.columns}

        # --- Layout Setup ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header Frame ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=8)
        self.header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(10, 5))
        # Configure row 0 to not expand vertically, preventing extra height
        self.header_frame.grid_rowconfigure(0, weight=0)


        # --- Table Container ---
        self.table_container = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=8)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(0, weight=1)

        # --- Scrollable Frame for Data ---
        self.table_frame = ctk.CTkScrollableFrame(
            self.table_container, fg_color="transparent", corner_radius=0, border_width=0
        )
        self.table_frame.grid(row=0, column=0, sticky="nsew")

        # --- Initial Draw ---
        self._redraw_headers()
        self.bind("<Configure>", self._on_resize)
        self.after(100, self.load_data)

    # --- Resize Handling (Unchanged) ---
    def _on_resize(self, event=None):
        if self._resize_job: self.after_cancel(self._resize_job)
        self._resize_job = self.after(50, self._perform_resize, event)

    def _perform_resize(self, event=None):
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
            self.header_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=col['weight'])
            self.table_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=col['weight'])
            current_grid_col += 1

    # --- Header Creation (Height/Padding/Actions Alignment Fixed) ---
    def _redraw_headers(self):
        """Clears and redraws headers with reduced height and corrected Actions alignment."""
        for widget in self.header_frame.winfo_children(): widget.destroy()
        self.header_widgets.clear()

        # Reduced vertical padding target
        vertical_padding = 3

        # Adjusted styles
        header_label_style = {"text_color": "#E0E0E0", "font": ("Arial Bold", 13), "anchor": "w"}
        # Reduced icon height and button padding implicitly reduces overall height
        icon_button_style = {"fg_color": "transparent", "hover_color": "#454545", "text_color": "#B0B0B0",
                             "font": ("Arial Bold", 16), "width": 20, "height": 22, # Reduced height
                             "corner_radius": 4, "border_width": 0}

        current_grid_col = 0
        for col_info in self.columns:
            col_name = col_info['name']
            if not self.column_visibility[col_name]:
                self.header_frame.grid_columnconfigure(current_grid_col, weight=0, minsize=0)
                self.table_frame.grid_columnconfigure(current_grid_col, weight=0, minsize=0)
                continue

            # --- Select All Checkbox Column ---
            if col_name == "Select" and col_info.get("select_all"):
                # Frame to precisely control padding
                checkbox_header_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
                checkbox_header_frame.grid(row=0, column=current_grid_col, sticky="nsew", padx=(20, 0), pady=vertical_padding) # Apply consistent padding
                checkbox_header_frame.grid_columnconfigure(0, weight=0)

                select_all_var = tk.BooleanVar()
                select_all_cb = ctk.CTkCheckBox(
                    checkbox_header_frame, text="", variable=select_all_var,
                    command=lambda: self.toggle_all_rows(select_all_var.get()),
                    width=20, height=20, fg_color="#1f538d", hover_color="#3b8ed0",
                    border_color="#4F4F4F", corner_radius=3
                )
                select_all_cb.grid(row=0, column=0, sticky="w") # Grid inside frame
                self.header_widgets[col_name] = {"widget": select_all_cb, "var": select_all_var}

            # --- Actions Column Header (Simplified) ---
            elif col_name == "Actions":
                 # Place label directly in the main header frame grid
                 header_label = ctk.CTkLabel(
                     self.header_frame, # Parent is header_frame directly
                     text=col_name,
                     **header_label_style
                 )
                 # Apply consistent padding directly to the label's grid call
                 header_label.grid(row=0, column=current_grid_col, sticky="w", padx=(20, 5), pady=vertical_padding)
                 # Store reference (no icon button here)
                 self.header_widgets[col_name] = {'widget': header_label, 'label': header_label}

            # --- Other Header Columns (Icon Button + Label) ---
            else:
                # Container frame for icon + label
                header_cell_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
                header_cell_frame.grid(row=0, column=current_grid_col, sticky="nsew", padx=(0, 1), pady=0) # Minimal gap between cells
                header_cell_frame.grid_columnconfigure(0, weight=0); header_cell_frame.grid_columnconfigure(1, weight=1)

                is_interactive = col_info.get('sortable', False) or col_info.get('filterable', False) or col_info.get('hideable', True)
                icon_button = None
                if is_interactive:
                    icon_button = ctk.CTkButton(header_cell_frame, text="⋮", command=lambda c=col_name: self._show_header_menu(c), **icon_button_style)
                    # Apply consistent padding
                    icon_button.grid(row=0, column=0, sticky="w", padx=(20, 5), pady=vertical_padding)
                else:
                    # Spacer needed if no icon to maintain label indent
                    spacer = ctk.CTkFrame(header_cell_frame, fg_color="transparent", width=icon_button_style["width"] + 25, height=icon_button_style["height"])
                    spacer.grid(row=0, column=0, sticky="w", padx=(0,0), pady=vertical_padding)

                header_label = ctk.CTkLabel(header_cell_frame, text=col_name, **header_label_style)
                # Apply consistent vertical padding
                header_label.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=vertical_padding)

                self.header_widgets[col_name] = {'widget': header_cell_frame, 'icon_button': icon_button, 'label': header_label}

            # Configure main grid column properties
            self.header_frame.grid_columnconfigure(current_grid_col, weight=col_info['weight'], minsize=col_info['min_width'])
            self.table_frame.grid_columnconfigure(current_grid_col, weight=col_info['weight'], minsize=col_info['min_width'])
            current_grid_col += 1

        self.after(50, self._perform_resize)
        self.after(55, self._update_header_indicators)

    # --- Header Menu Logic (Unchanged) ---
    def _show_header_menu(self, column_name):
        if self._current_menu and self._current_menu.winfo_exists(): self._current_menu.destroy()
        col_info = next((c for c in self.columns if c['name'] == column_name), None)
        if not col_info or column_name not in self.header_widgets: return
        icon_button = self.header_widgets[column_name].get('icon_button')
        if not icon_button: return
        menu = Menu(icon_button, tearoff=0, background="#333333", foreground="#FFFFFF", activebackground="#444444", activeforeground="#FFFFFF", relief="flat", borderwidth=0)
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
        menu.post(icon_button.winfo_rootx(), icon_button.winfo_rooty() + icon_button.winfo_height()); self._current_menu = menu

    # --- Sorting Logic (Unchanged) ---
    def _set_sort(self, column_name, direction):
        self.sort_column = column_name; self.sort_direction = direction; self.current_page = 1; self.load_data()

    # --- Header Indicator Update (Updates Label - Unchanged) ---
    def _update_header_indicators(self):
        for name, data in self.header_widgets.items():
            label = data.get('label') # Get the label part
            if isinstance(label, ctk.CTkLabel) and label.winfo_exists():
                original_text = name; indicator = ""
                if name == self.sort_column: indicator = "  ⯅" if self.sort_direction == 'asc' else "  ⯆"
                label.configure(text=original_text + indicator)

    # --- Filtering Logic (Unchanged) ---
    def _prompt_filter(self, column_name):
        dialog = ctk.CTkInputDialog(text=f"Filter {column_name}:", title=f"Filter {column_name}")
        val = dialog.get_input();
        if val is not None: self.column_filters[column_name] = val.strip(); self.current_page = 1; self.load_data()
    def _clear_column_filter(self, column_name):
        if column_name in self.column_filters: del self.column_filters[column_name]; self.current_page = 1; self.load_data()

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
        for widget in self.table_frame.winfo_children(): widget.destroy()
        self._redraw_headers();
        # self.load_data() called via after in redraw_headers

    # --- Data Loading (Unchanged) ---
    def load_data(self):
        # (Keep implementation from previous version)
        try:
            for widget in self.table_frame.winfo_children(): widget.destroy()
            self.all_engineer_ids_on_current_page = []
            base_query = self.session.query(Engineer); query = base_query
            # Apply Filters
            for col_name, filter_value in self.column_filters.items():
                 if not filter_value: continue
                 column_info = next((c for c in self.columns if c["name"] == col_name), None)
                 if column_info and column_info.get("filterable") and column_info.get("db_field"):
                     db_field_name = column_info["db_field"]; model_attr = getattr(Engineer, db_field_name, None)
                     if model_attr:
                         try:
                             if db_field_name == 'id': query = query.filter(model_attr == int(filter_value)) if filter_value.isdigit() else query.filter(sqlalchemy.sql.false())
                             elif isinstance(getattr(Engineer, db_field_name).type, sqlalchemy.types.String): query = query.filter(model_attr.ilike(f"%{filter_value}%"))
                         except Exception as filter_err: print(f"Filter Error: {filter_err}"); traceback.print_exc()
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
            # Insert Rows
            current_grid_col_map = {name: i for i, name in enumerate(col['name'] for col in self.columns if self.column_visibility[col['name']])}
            for row_idx, engineer in enumerate(engineers):
                row_color = "#282828" if row_idx % 2 == 0 else "#242424"
                row_frame = ctk.CTkFrame(self.table_frame, fg_color=row_color, corner_radius=0)
                for grid_col_idx, col_name in enumerate(current_grid_col_map.keys()):
                     col_info = next(c for c in self.columns if c['name'] == col_name)
                     row_frame.grid_columnconfigure(grid_col_idx, weight=col_info['weight'], minsize=col_info['min_width'])
                row_frame.grid(row=row_idx, column=0, columnspan=len(current_grid_col_map), sticky="ew", pady=(0, 1))
                for col_info in self.columns:
                     col_name = col_info['name']
                     if not self.column_visibility[col_name]: continue
                     grid_col = current_grid_col_map[col_name]
                     if col_name == "Select":
                         checkbox_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
                         checkbox_cell.grid(row=0, column=grid_col, sticky="nsew", padx=(20, 0), pady=3) # Reduced pady
                         checkbox_cell.grid_columnconfigure(0, weight=0)
                         checkbox_var = tk.BooleanVar(value=(engineer.id in self.selected_rows))
                         checkbox = ctk.CTkCheckBox(checkbox_cell, text="", variable=checkbox_var,
                                                    command=lambda id=engineer.id, var=checkbox_var: self.toggle_row_selection(id, var),
                                                    width=20, height=20, fg_color="#1f538d", hover_color="#3b8ed0",
                                                    border_color="#4F4F4F", corner_radius=3)
                         checkbox.grid(row=0, column=0, sticky="w")
                     elif col_name == "Actions":
                         actions_frame = self._create_actions_frame(row_frame, engineer)
                         actions_frame.grid(row=0, column=grid_col, sticky="nsew")
                     elif col_info.get("db_field"):
                         attr_val = getattr(engineer, col_info["db_field"], "-")
                         text = str(attr_val) if attr_val is not None else "-"
                         cell = ctk.CTkFrame(row_frame, fg_color="transparent")
                         cell.grid(row=0, column=grid_col, sticky="nsew")
                         cell.grid_columnconfigure(0, weight=1)
                         label = ctk.CTkLabel(cell, text=text, anchor="w", justify="left",
                                              font=("Arial", 12), text_color="#D0D0D0")
                         label.grid(row=0, column=0, sticky="nsew", padx=(20, 5), pady=3) # Reduced pady
            # Final UI Updates
            if self.on_page_change: self.on_page_change(self.current_page, self.total_pages)
            self._update_header_indicators(); self._update_select_all_checkbox_state()
        except Exception as e: print(f"Error loading table data: {str(e)}"); traceback.print_exc(); notification.show_error("Error Loading Data", f"{str(e)}")


    # --- Action Button Creation (Padding Adjusted) ---
    def _create_actions_frame(self, parent, engineer):
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.grid_columnconfigure((0, 1), weight=1, minsize=90)
        # Reduced vertical padding for buttons
        button_style = {"height": 28, "font": ("Arial", 12), "corner_radius": 5}
        details_btn = ctk.CTkButton(actions_frame, text="Details", command=lambda eng=engineer: self.edit_engineer(eng), fg_color="#2B5EA7", hover_color="#2573A7", **button_style)
        details_btn.grid(row=0, column=0, padx=(20, 5), pady=3, sticky="ew") # Reduced pady
        delete_btn = ctk.CTkButton(actions_frame, text="Delete", command=lambda eng=engineer: self.delete_engineer(eng), fg_color="#A72B2B", hover_color="#C0392B", **button_style)
        delete_btn.grid(row=0, column=1, padx=(5, 20), pady=3, sticky="ew") # Reduced pady
        return actions_frame

    # --- Select All / Row Selection Logic (Unchanged) ---
    def toggle_all_rows(self, select_all_state):
        ids_on_page = self.all_engineer_ids_on_current_page; changed = False
        if select_all_state:
            newly_selected = set(ids_on_page) - self.selected_rows
            if newly_selected: self.selected_rows.update(newly_selected); changed = True
        else:
            removed_count = len(self.selected_rows.intersection(ids_on_page))
            if removed_count > 0: self.selected_rows.difference_update(ids_on_page); changed = True
        if changed: self.load_data()
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
        self._update_select_all_checkbox_state()

    # --- Dialogs and Data Actions (Unchanged) ---
    def edit_engineer(self, engineer):
        dialog = EngineerDialog(self, self.session, engineer=engineer, on_save=self.load_data)

    # --- Other Methods (Unchanged) ---
    def set_rows_per_page(self, value):
        try:
            new_rows = int(value)
            if new_rows > 0: self.rows_per_page = new_rows; self.current_page = 1; self.load_data()
            else: notification.show_warning("Invalid Value", "Rows > 0.")
        except ValueError: notification.show_warning("Invalid Input", "Enter number.")
    def next_page(self):
        if self.current_page < self.total_pages: self.current_page += 1; self.load_data()
    def prev_page(self):
        if self.current_page > 1: self.current_page -= 1; self.load_data()
    def go_to_page(self, page_num):
        try:
            page = int(page_num)
            if 1 <= page <= self.total_pages: self.current_page = page; self.load_data()
            else: notification.show_warning("Invalid Page", f"Page must be 1-{self.total_pages}")
        except ValueError: notification.show_warning("Invalid Input", "Enter valid page number.")
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
        except Exception as e: notification.show_error("Error Fetching", f"{e}"); return []
    def delete_engineer(self, engineer):
        if not messagebox.askyesno("Confirm Delete", f"Delete {getattr(engineer, 'name', 'this engineer')}?"): return
        try:
            self.session.delete(engineer); self.session.commit()
            notification.show_success("Deleted", f"Engineer deleted.")
            self.selected_rows.discard(engineer.id); self.load_data()
        except Exception as e: self.session.rollback(); notification.show_error("Delete Error", f"{e}"); traceback.print_exc()
    def add_engineer(self):
        dialog = EngineerDialog(self, self.session, on_save=self.load_data)
    def delete_selected(self):
        if not self.selected_rows: notification.show_warning("No Selection", "Select engineers first."); return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(self.selected_rows)} selected engineer(s)?"): return
        count = 0
        try:
            engineers = self.session.query(Engineer).filter(Engineer.id.in_(self.selected_rows)).all()
            for engineer in engineers: self.session.delete(engineer); count += 1
            self.session.commit(); notification.show_success("Deleted", f"{count} engineer(s) deleted.")
            self.selected_rows.clear(); self.load_data()
        except Exception as e: self.session.rollback(); notification.show_error("Delete Error", f"{e}"); traceback.print_exc()