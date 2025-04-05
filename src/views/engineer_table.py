import customtkinter as ctk
import tkinter as tk
from tkinter import Menu, messagebox
import sqlalchemy
# Import specific types if needed for filtering/display logic based on your model
from sqlalchemy import func, asc, desc, String as SQLString, Integer as SQLInteger, Boolean as SQLBoolean, Date as SQLDate, Float as SQLFloat
# Make sure Base is imported if Engineer inherits from it and it's needed here, otherwise remove
# from .base import Base # Or wherever your Base is defined
import math
import traceback

# Imports from your actual project structure:
# ==========================================
# !!! IMPORTANT: Ensure these lines are uncommented and point to your actual files !!!
from src.models.engineer import Engineer # <<< Make sure this import is correct and active
from .engineer_dialog import EngineerDialog # <<< Make sure this import is correct and active
# from src.services.notification import notification # <<< If you use a custom notification service
# ==========================================


# --- Simple Notification Function ---
# (Using messagebox as fallback)
def show_notification(parent, message, title="Notification", type="info"):
    """Show a notification message to the user"""
    print(f"Notification ({type}): {title} - {message}")
    # Replace with your actual notification service call if available
    # try:
    #    if type == "info": notification.show_info(...)
    #    ...
    # except Exception:
    #    # Fallback if custom notification fails
    if type == "info": messagebox.showinfo(title, message, parent=parent)
    elif type == "warning": messagebox.showwarning(title, message, parent=parent)
    elif type == "error": messagebox.showerror(title, message, parent=parent)
    else: messagebox.showinfo(title, message, parent=parent)


# --- EngineerTable Class ---
class EngineerTable(ctk.CTkFrame):
    """
    A CustomTkinter frame that displays Engineer data in a sortable, filterable,
    paginated table with selection capabilities. Adapted for the specific Engineer model.
    """
    def __init__(self, parent, session, on_page_change=None):
        """
        Initializes the EngineerTable.

        Args:
            parent: The parent widget.
            session: The SQLAlchemy session object for database interaction.
            on_page_change (callable, optional): A callback function executed
                when the page changes. It receives (current_page, total_pages).
                Defaults to None.
        """
        super().__init__(parent, fg_color="transparent")

        # --- Validate Session and Engineer Import ---
        # Basic check to catch the error early if Engineer wasn't imported
        try:
            # Attempt to access an attribute that should exist on the mapped class
            _ = Engineer.id
        except NameError:
             # This error occurs if 'Engineer' is not defined in the current scope
             errmsg = "CRITICAL ERROR: 'Engineer' class not found. Ensure 'from src.models.engineer import Engineer' is correct and active."
             print(errmsg)
             messagebox.showerror("Initialization Error", errmsg, parent=parent)
             # Optionally, disable the widget or raise an exception
             # For now, just print and show error, but widget might be unusable
             # raise ImportError(errmsg) # Or handle more gracefully
        except AttributeError:
             # This might occur if 'Engineer' is defined but not a mapped SQLAlchemy class
             # Or if the dummy class is still present and lacks the '.id' attribute correctly
             errmsg = "ERROR: Imported 'Engineer' class does not appear to be a valid SQLAlchemy model (missing 'id' attribute?)."
             print(errmsg)
             messagebox.showerror("Initialization Error", errmsg, parent=parent)


        self.session = session
        self.on_page_change = on_page_change
        self.current_page = 1
        self.rows_per_page = 10
        self.total_pages = 1
        self.selected_rows = set()
        self.all_engineer_ids_on_current_page = []

        # --- State Variables ---
        self.sort_column = None
        self.sort_direction = None
        self.column_filters = {}
        self._resize_job = None
        self.header_widgets = {}
        self._current_menu = None
        self.column_visibility = {}

        # --- Column Definitions (ADAPTED to your Engineer model) ---
        self.columns = [
            {"name": "Select",          "width": 50, "weight": 0, "min_width": 50,  "sortable": False, "filterable": False, "hideable": False, "select_all": True},
            {"name": "ID",              "width": 50, "weight": 0, "min_width": 50,  "db_field": "id",                  "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Name",            "width": 130,"weight": 3, "min_width": 100, "db_field": "name",                "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Company",         "width": 120,"weight": 2, "min_width": 100, "db_field": "company_name",        "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "DoB",             "width": 90, "weight": 0, "min_width": 90,  "db_field": "date_of_birth",       "sortable": True,  "filterable": False, "hideable": True}, # Filter disabled for date example
            {"name": "Technical Field", "width": 120,"weight": 2, "min_width": 100, "db_field": "field_name",          "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Expertise",       "width": 120,"weight": 2, "min_width": 100, "db_field": "evaluation_target",   "sortable": True,  "filterable": True,  "hideable": True},
            {"name": "Is PM",           "width": 60, "weight": 0, "min_width": 60,  "db_field": "selected",            "sortable": True,  "filterable": True,  "hideable": True}, # ADDED: Mapped to 'selected' field
            {"name": "Experience",      "width": 90, "weight": 1, "min_width": 80,  "db_field": "experience",          "sortable": True,  "filterable": False, "hideable": True}, # db_field='experience'(String), filterable=False
            {"name": "Actions",         "width": 180,"weight": 0, "min_width": 180, "sortable": False, "filterable": False, "hideable": False}
        ]
        self.column_visibility = {col['name']: True for col in self.columns}

        # --- UI Constants ---
        self.vertical_padding = 5
        self.base_left_padding = 15
        self.row_color_1 = "#282828"
        self.row_color_2 = "#242424"
        self.row_hover_color = "#383838"
        self.header_bg_color = "#252525"
        self.header_border_color = "#404040"
        self.content_bg_color = "#1E1E1E"
        self.text_color_primary = "#E0E0E0"
        self.text_color_secondary = "#B0B0B0"
        self.data_font = ("Arial", 12)
        self.header_font = ("Arial Bold", 12)

        # --- Layout Setup ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header Frame ---
        self.header_frame = ctk.CTkFrame(self, fg_color=self.header_bg_color, corner_radius=8,
                                         border_width=1, border_color=self.header_border_color)
        self.header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(10, 0))
        self.header_frame.grid_rowconfigure(0, weight=0)

        # --- Table Container ---
        self.table_container = ctk.CTkFrame(self, fg_color=self.content_bg_color, corner_radius=8)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(1, weight=0)
        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=0)

        # --- Canvas ---
        self.canvas = tk.Canvas(self.table_container, bg=self.content_bg_color, borderwidth=0, highlightthickness=0)

        # --- Scrollbars ---
        self.h_scrollbar = ctk.CTkScrollbar(self.table_container, orientation="horizontal", command=self.canvas.xview)
        self.v_scrollbar = ctk.CTkScrollbar(self.table_container, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        # --- Grid Canvas & Scrollbars ---
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # --- Content Frame (Inside Canvas) ---
        self.content_frame = ctk.CTkFrame(self.canvas, fg_color=self.content_bg_color)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", tags="content_frame")

        # --- Loading Indicator ---
        self.loading_label = ctk.CTkLabel(self.table_container, text="Loading...", font=("Arial", 14), text_color=self.text_color_secondary)

        # --- Bind Events ---
        self.content_frame.bind("<Configure>", self._on_content_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # Bind mouse wheel scrolling (consider platform differences if needed)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) # Windows/Mac
        self.canvas.bind_all("<Button-4>", lambda e: self._on_mousewheel(e)) # Linux scroll up
        self.canvas.bind_all("<Button-5>", lambda e: self._on_mousewheel(e)) # Linux scroll down


        # --- Initial Draw ---
        self._redraw_headers()
        self.bind("<Configure>", self._on_resize)
        # Load data only if Engineer class seems valid
        if 'Engineer' in globals() or 'Engineer' in locals():
             try:
                 _ = Engineer.id # Re-check before initial load
                 self.after(100, self.load_data)
             except (NameError, AttributeError):
                 print("Skipping initial data load due to Engineer class issue.")
        else:
             print("Skipping initial data load because 'Engineer' class is not defined.")


    # --- Mouse Wheel Scrolling ---
    def _on_mousewheel(self, event):
        """Handles mouse wheel events to scroll the canvas vertically."""
        delta = 0
        # Linux uses event.num
        if hasattr(event, 'num') and event.num == 4: delta = -1
        elif hasattr(event, 'num') and event.num == 5: delta = 1
        # Windows/macOS use event.delta
        elif hasattr(event, 'delta'): delta = -1 if event.delta > 0 else 1

        v_scroll_info = self.v_scrollbar.get()
        is_scrollable = v_scroll_info[0] > 0.0 or v_scroll_info[1] < 1.0
        if is_scrollable and delta != 0:
             # Use delta directly as number of units
             self.canvas.yview_scroll(delta, "units")

    # --- Canvas/Content Frame Configuration ---
    def _on_content_frame_configure(self, event=None):
        """Updates the canvas scrollregion when the content_frame size changes."""
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox: self.canvas.configure(scrollregion=bbox)

    def _on_canvas_configure(self, event=None):
        """Adjusts the width of the content_frame to match the canvas width."""
        canvas_width = self.canvas.winfo_width()
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

    # --- Resize Handling ---
    def _on_resize(self, event=None):
        """Debounces resize events."""
        if self._resize_job: self.after_cancel(self._resize_job)
        self._resize_job = self.after(50, self._perform_resize)

    def _perform_resize(self):
        """Calculates and applies new column widths."""
        if not self.winfo_exists(): return
        parent_width = self.winfo_width()
        available_width = parent_width - 20 # Adjust based on actual container padding
        if not self.header_frame.winfo_exists(): return

        visible_columns = [c for c in self.columns if self.column_visibility[c['name']]]
        if not visible_columns: return

        total_weight = sum(col["weight"] for col in visible_columns if col["weight"] > 0)
        fixed_width_total = sum(col["min_width"] for col in visible_columns if col["weight"] == 0)
        total_min_width = sum(col["min_width"] for col in visible_columns)
        effective_width = max(available_width, total_min_width)
        weighted_available = effective_width - fixed_width_total
        min_weighted_width = sum(col["min_width"] for col in visible_columns if col["weight"] > 0)
        width_per_weight = max(0, weighted_available - min_weighted_width) / total_weight if total_weight > 0 else 0

        current_grid_col = 0
        actual_total_width = 0
        for col in self.columns:
            if not self.column_visibility[col['name']]: continue
            if col["weight"] > 0:
                new_width = max(col["min_width"], int(col["min_width"] + col["weight"] * width_per_weight))
            else:
                new_width = col["min_width"]
            # Configure column minsize and weight in both header and content frames
            self.header_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=col['weight'])
            self.content_frame.grid_columnconfigure(current_grid_col, minsize=new_width, weight=col['weight'])
            actual_total_width += new_width
            current_grid_col += 1

        # Adjust content frame width inside canvas
        canvas_width = self.canvas.winfo_width()
        content_frame_width = max(actual_total_width, canvas_width)
        self.canvas.itemconfig(self.canvas_frame_id, width=content_frame_width)
        # Update scroll region after resize calculations
        self.after(10, self._on_content_frame_configure)

    # --- Header Creation ---
    def _redraw_headers(self):
        """Clears and redraws the header widgets."""
        for widget in self.header_frame.winfo_children(): widget.destroy()
        self.header_widgets.clear()

        header_button_style = {"fg_color": "transparent", "hover_color": "#353535",
                               "text_color": self.text_color_primary, "font": self.header_font,
                               "anchor": "w", "height": 28, "corner_radius": 0, "border_width": 0}
        current_grid_col = 0
        for col_info in self.columns:
            col_name = col_info['name']
            # Skip configuration and widget creation for hidden columns
            if not self.column_visibility[col_name]:
                self.header_frame.grid_columnconfigure(current_grid_col, weight=0, minsize=0, pad=0)
                self.content_frame.grid_columnconfigure(current_grid_col, weight=0, minsize=0, pad=0)
                continue # Don't increment grid col index

            # Container for padding
            container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
            container.grid(row=0, column=current_grid_col, sticky="ew", padx=0, pady=0)
            container.grid_columnconfigure(0, weight=1)

            # Create widget (Checkbox or Button)
            if col_name == "Select":
                select_all_var = tk.BooleanVar()
                select_all_cb = ctk.CTkCheckBox(container, text="", variable=select_all_var,
                                                command=lambda: self.toggle_all_rows(select_all_var.get()),
                                                width=20, height=20, fg_color="#1f538d", hover_color="#3b8ed0",
                                                border_color="#4F4F4F", corner_radius=3)
                select_all_cb.grid(row=0, column=0, sticky="w", padx=(self.base_left_padding, 0), pady=self.vertical_padding)
                self.header_widgets[col_name] = {"widget": select_all_cb, "var": select_all_var, "container": container}
            else:
                header_button = ctk.CTkButton(container, text=col_name, **header_button_style)
                header_button.grid(row=0, column=0, sticky="w", padx=(self.base_left_padding, 5), pady=self.vertical_padding)
                self.header_widgets[col_name] = {'widget': header_button, "container": container}
                # Configure interactivity
                is_interactive = col_info.get('sortable', False) or col_info.get('filterable', False) or col_info.get('hideable', True)
                if is_interactive and col_name != "Actions":
                    header_button.configure(command=lambda c=col_name: self._show_header_menu(c), cursor="hand2")
                else:
                    header_button.configure(hover=False, command=None, cursor="")

            # Configure column properties on the parent frames
            self.header_frame.grid_columnconfigure(current_grid_col, weight=col_info['weight'], minsize=col_info['min_width'])
            self.content_frame.grid_columnconfigure(current_grid_col, weight=col_info['weight'], minsize=col_info['min_width'])
            current_grid_col += 1 # Increment only for visible columns

        # Schedule updates after drawing
        self.after(50, self._perform_resize)
        self.after(55, self._update_header_indicators)

    # --- Header Menu, Sort, Filter, Visibility ---
    def _show_header_menu(self, column_name):
        """Displays a context menu for a header button."""
        if self._current_menu and self._current_menu.winfo_exists(): self._current_menu.destroy()
        col_info = next((c for c in self.columns if c['name'] == column_name), None)
        if not col_info or column_name not in self.header_widgets: return
        button = self.header_widgets[column_name].get('widget')
        if not isinstance(button, ctk.CTkButton): return

        menu = Menu(button, tearoff=0, background="#333333", foreground="#FFFFFF",
                    activebackground="#444444", activeforeground="#FFFFFF", relief="flat", borderwidth=0,
                    font=("Arial", 11))

        # Add menu items based on column capabilities
        if col_info.get('sortable'):
            menu.add_command(label="Sort Ascending", command=lambda: self._set_sort(column_name, 'asc'))
            menu.add_command(label="Sort Descending", command=lambda: self._set_sort(column_name, 'desc'))
            if self.sort_column == column_name:
                menu.add_separator()
                menu.add_command(label="Clear Sort", command=lambda: self._set_sort(None, None))
            menu.add_separator()

        if col_info.get('filterable'): # Check filterable flag from self.columns
            filter_text = self.column_filters.get(column_name, "")
            filter_label = f"Filter..." if not filter_text else f"Filter: '{filter_text}'"
            menu.add_command(label=filter_label, command=lambda: self._prompt_filter(column_name))
            if filter_text:
                menu.add_command(label="Clear Filter", command=lambda: self._clear_column_filter(column_name))
            menu.add_separator()
        else: # Add disabled filter option if not filterable
             menu.add_command(label="Filter (N/A)", state="disabled")
             menu.add_separator()

        if col_info.get('hideable', True):
             menu.add_command(label="Hide Column", command=lambda: self._toggle_column_visibility(column_name, False))
             menu.add_separator()
        menu.add_command(label="Show/Hide Columns...", command=self._show_column_chooser)

        # Display menu
        button.update_idletasks()
        menu.post(button.winfo_rootx() + 5, button.winfo_rooty() + button.winfo_height())
        self._current_menu = menu

    def _set_sort(self, column_name, direction):
        """Sets sorting and reloads data."""
        self.sort_column = column_name
        self.sort_direction = direction
        self.current_page = 1
        self.load_data()

    def _update_header_indicators(self):
        """Updates header button text with indicators."""
        for name, data in self.header_widgets.items():
            widget = data.get('widget')
            if isinstance(widget, ctk.CTkButton) and widget.winfo_exists():
                col_info = next((c for c in self.columns if c['name'] == name), None)
                if not col_info: continue
                base_text = name; sort_indicator = ""; menu_indicator = ""
                if name == self.sort_column: sort_indicator = " ▲" if self.sort_direction == 'asc' else " ▼"
                is_interactive = col_info.get('sortable', False) or col_info.get('filterable', False) or col_info.get('hideable', True)
                if is_interactive and name != "Actions": menu_indicator = "…"
                widget.configure(text=base_text + sort_indicator + menu_indicator)

    def _prompt_filter(self, column_name):
        """Gets filter input from user if column is filterable."""
        col_info = next((c for c in self.columns if c['name'] == column_name), None)
        # Double check filterable status before showing dialog
        if not col_info or not col_info.get('filterable'):
            show_notification(self, f"Column '{column_name}' cannot be filtered.", "Filter Error", "warning")
            return

        dialog = ctk.CTkInputDialog(text=f"Enter filter text for {column_name}:", title=f"Filter {column_name}")
        filter_value = dialog.get_input()
        if filter_value is not None: self.apply_specific_filter(column_name, filter_value.strip())

    def _clear_column_filter(self, column_name):
        """Clears filter for a specific column."""
        self.apply_specific_filter(column_name, "")

    def apply_specific_filter(self, field_name, filter_value):
        """Applies a single column filter if the column is filterable."""
        col_info = next((c for c in self.columns if c["name"] == field_name), None)
        if not col_info and field_name is not None:
            print(f"Warning: Invalid filter field '{field_name}'")
            return
        # Ensure column is actually filterable before applying
        if field_name and not col_info.get('filterable'):
             print(f"Warning: Attempted to apply filter to non-filterable column '{field_name}'.")
             # Optionally notify user, but menu should prevent this
             # show_notification(self, f"Column '{field_name}' cannot be filtered.", "Filter Error", "warning")
             return

        # Logic for applying/clearing the filter
        filter_changed = False
        if field_name and filter_value: # Set/update filter
            if self.column_filters.get(field_name) != filter_value:
                 self.column_filters.clear() # Current logic: only one filter active
                 self.column_filters[field_name] = filter_value
                 filter_changed = True
        elif field_name in self.column_filters: # Clear specific filter
             del self.column_filters[field_name]
             filter_changed = True # Changed if a filter was removed
        # No need for the 'clear all' case here, handled by clear_all_filters()

        if filter_changed:
            print(f"Applying filter(s): {self.column_filters}")
            self.current_page = 1 # Reset page when filters change
            self.load_data()

    def _toggle_column_visibility(self, column_name, visible):
        """Hides or shows a column."""
        visible_count = sum(1 for v in self.column_visibility.values() if v)
        if not visible and visible_count <= 1:
            show_notification(self, "Cannot hide the last visible column.", "Action Denied", "warning")
            return
        if self.column_visibility.get(column_name) != visible:
            self.column_visibility[column_name] = visible
            self._redraw_table_layout() # Redraw needed for visibility changes

    def _show_column_chooser(self):
        """Displays dialog to toggle column visibility."""
        dialog = ctk.CTkToplevel(self); dialog.title("Show/Hide Columns"); dialog.transient(self); dialog.grab_set(); dialog.geometry("300x400")
        vars = {}; scrollable_frame = ctk.CTkScrollableFrame(dialog, label_text="Select columns to display"); scrollable_frame.pack(padx=10, pady=10, fill="both", expand=True)
        row_index = 0
        # Iterate through defined columns to create checkboxes
        for col in self.columns:
            name = col['name']
            if col.get('hideable', True): # Only show checkboxes for hideable columns
                var = tk.BooleanVar(value=self.column_visibility[name])
                cb = ctk.CTkCheckBox(scrollable_frame, text=name, variable=var)
                cb.grid(row=row_index, column=0, sticky="w", padx=10, pady=(2, 5))
                vars[name] = var
                row_index += 1

        def apply_changes():
            changed = False; new_vis_state = dict(self.column_visibility)
            # Update visibility state based on checkboxes
            for name, var in vars.items():
                if new_vis_state[name] != var.get():
                    new_vis_state[name] = var.get()
                    changed = True

            # Validate: Ensure at least one column remains visible
            future_visible_count = sum(1 for is_visible in new_vis_state.values() if is_visible)
            if changed and future_visible_count == 0:
                 show_notification(dialog, "You must keep at least one column visible.", "Visibility Error", "warning")
                 return # Prevent applying changes

            # Apply if changes were made
            if changed:
                self.column_visibility = new_vis_state
                self._redraw_table_layout() # Redraw required for visibility change

            dialog.destroy() # Close dialog

        # Dialog buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent"); btn_frame.pack(pady=(5, 10), fill="x", padx=10); btn_frame.grid_columnconfigure((0, 1), weight=1)
        apply_btn = ctk.CTkButton(btn_frame, text="Apply", command=apply_changes); apply_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, fg_color="gray"); cancel_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _redraw_table_layout(self):
        """Clears content, redraws headers, reloads data. Used after visibility changes."""
        for widget in self.content_frame.winfo_children(): widget.destroy()
        self._redraw_headers() # This reconfigures columns based on new visibility
        self.after(10, self.load_data) # Reload data into the new layout

    # --- Data Loading ---
    def load_data(self):
        """Fetches and displays data based on current state."""
        # --- Check if Engineer class is available ---
        if 'Engineer' not in globals() and 'Engineer' not in locals():
             print("Error: 'Engineer' class not defined. Cannot load data.")
             show_notification(self, "Setup Error: Engineer model not available.", "Load Data Error", "error")
             # Optionally clear the table area
             for widget in self.content_frame.winfo_children(): widget.destroy()
             error_label = ctk.CTkLabel(self.content_frame, text="Error: Engineer model not loaded.", text_color="red")
             error_label.pack(pady=20)
             return # Stop loading process

        # --- Show Loading Indicator ---
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.update_idletasks()
        num_visible_columns = sum(1 for v in self.column_visibility.values() if v)

        try:
            # --- Clear Previous Data ---
            for widget in self.content_frame.winfo_children(): widget.destroy()
            self.all_engineer_ids_on_current_page.clear()

            # --- Build Query (Using the imported Engineer model) ---
            # Ensure 'Engineer' here refers to your imported SQLAlchemy model
            base_query = self.session.query(Engineer)
            query = base_query

            # --- Apply Filters ---
            filter_clauses = []
            for col_name, filter_value in self.column_filters.items():
                 if not filter_value: continue
                 column_info = next((c for c in self.columns if c["name"] == col_name), None)
                 # Check if column is valid, filterable, and mapped
                 if column_info and column_info.get("filterable") and column_info.get("db_field"):
                     db_field_name = column_info["db_field"]
                     # Get the actual SQLAlchemy Column object from the imported Engineer class
                     model_attr = getattr(Engineer, db_field_name, None)
                     if model_attr is not None: # Ensure the attribute exists on the model
                         try:
                             # Get the column type directly from the SQLAlchemy attribute
                             attr_type = model_attr.type

                             # Apply filter based on type
                             if isinstance(attr_type, (SQLString, sqlalchemy.types.Text)):
                                 filter_clauses.append(model_attr.ilike(f"%{filter_value}%"))
                             elif isinstance(attr_type, SQLInteger):
                                 if filter_value.isdigit(): filter_clauses.append(model_attr == int(filter_value))
                                 else: filter_clauses.append(sqlalchemy.sql.false()) # No match if not a digit
                             elif isinstance(attr_type, SQLFloat):
                                 try: filter_clauses.append(model_attr == float(filter_value))
                                 except ValueError: filter_clauses.append(sqlalchemy.sql.false()) # No match if not float
                             elif isinstance(attr_type, SQLBoolean):
                                 f_val_lower = filter_value.lower()
                                 if f_val_lower in ['true', 'yes', '1']: filter_clauses.append(model_attr == True)
                                 elif f_val_lower in ['false', 'no', '0']: filter_clauses.append(model_attr == False)
                                 else: filter_clauses.append(sqlalchemy.sql.false()) # No match if invalid boolean text
                             elif isinstance(attr_type, SQLDate):
                                 # Implement date filtering if needed (currently disabled in self.columns)
                                 pass

                         except AttributeError as ae:
                              # This might happen if getattr returns something unexpected, or .type is missing
                              print(f"Warning: Could not get SQLAlchemy type for filter field '{db_field_name}'. Error: {ae}. Falling back to string filter.")
                              # Fallback to string filter might be okay sometimes
                              filter_clauses.append(model_attr.ilike(f"%{filter_value}%"))
                         except Exception as filter_err:
                             print(f"Error applying filter for column '{col_name}': {filter_err}")
                             traceback.print_exc()
            # Add filters to the query
            if filter_clauses: query = query.filter(sqlalchemy.and_(*filter_clauses))

            # --- Apply Sorting ---
            if self.sort_column:
                col_info = next((c for c in self.columns if c['name'] == self.sort_column), None)
                if col_info and col_info.get('sortable') and col_info.get('db_field'):
                    db_field = col_info['db_field']
                    # Get the SQLAlchemy Column object
                    model_attr = getattr(Engineer, db_field, None)
                    if model_attr is not None:
                         try:
                             sort_func = asc if self.sort_direction == 'asc' else desc
                             # Apply sorting using the Column object
                             query = query.order_by(sort_func(model_attr))
                         except Exception as sort_err:
                             print(f"Error applying sort for column '{self.sort_column}': {sort_err}")
                             traceback.print_exc()

            # --- Count and Paginate ---
            try: total_count = query.count()
            except Exception as count_e: print(f"Count Error: {count_e}"); traceback.print_exc(); total_count = 0

            self.total_pages = max(1, math.ceil(total_count / self.rows_per_page) if self.rows_per_page > 0 else 1)
            if self.current_page > self.total_pages: self.current_page = self.total_pages
            offset = (self.current_page - 1) * self.rows_per_page

            # --- Fetch Data ---
            engineers = query.offset(offset).limit(self.rows_per_page).all()
            self.all_engineer_ids_on_current_page = [eng.id for eng in engineers if eng.id is not None]

            # --- Get Visible Columns Map ---
            visible_columns_data = [(i, col) for i, col in enumerate(self.columns) if self.column_visibility[col['name']]]
            current_grid_col_map = {col['name']: idx for idx, (original_idx, col) in enumerate(visible_columns_data)}
            num_visible_columns = len(current_grid_col_map)

            # --- Insert Data Rows ---
            if not engineers: # Display placeholder if no results
                placeholder_label = ctk.CTkLabel(self.content_frame, text="No engineers found matching your criteria.", text_color=self.text_color_secondary, font=("Arial", 14), anchor="center")
                self.content_frame.grid_rowconfigure(0, weight=1); self.content_frame.grid_columnconfigure(0, weight=1)
                placeholder_label.grid(row=0, column=0, columnspan=max(1, num_visible_columns), sticky="nsew", padx=20, pady=40)
            else: # Populate rows with data
                self.content_frame.grid_rowconfigure(0, weight=0); self.content_frame.grid_columnconfigure(0, weight=0) # Reset placeholder grid config
                for row_idx, engineer in enumerate(engineers):
                    row_color = self.row_color_1 if row_idx % 2 == 0 else self.row_color_2
                    row_frame = ctk.CTkFrame(self.content_frame, fg_color=row_color, corner_radius=0)
                    # Configure columns within the row frame
                    for grid_col_idx, col_name in enumerate(current_grid_col_map.keys()):
                         col_info = next(c for c in self.columns if c['name'] == col_name)
                         row_frame.grid_columnconfigure(grid_col_idx, minsize=col_info['min_width'], weight=col_info['weight'])
                    row_frame.grid(row=row_idx, column=0, columnspan=num_visible_columns, sticky="ew", pady=(0, 1))

                    # --- Hover effect bindings ---
                    def create_enter_handler(rf): return lambda e: rf.configure(fg_color=self.row_hover_color)
                    def create_leave_handler(rf, rc): return lambda e: rf.configure(fg_color=rc)
                    enter_handler = create_enter_handler(row_frame)
                    leave_handler = create_leave_handler(row_frame, row_color)
                    row_frame.bind("<Enter>", enter_handler)
                    row_frame.bind("<Leave>", leave_handler)
                    # Bind hover to common child widgets
                    for child_widget_type in ("CTkLabel", "CTkButton", "CTkCheckBox", "CTkFrame"):
                        row_frame.bind_class(child_widget_type, "<Enter>", enter_handler, add="+")
                        row_frame.bind_class(child_widget_type, "<Leave>", leave_handler, add="+")

                    # --- Place cell content ---
                    for original_col_index, col_info in enumerate(self.columns):
                         col_name = col_info['name']
                         if not self.column_visibility[col_name]: continue # Skip hidden
                         grid_col = current_grid_col_map[col_name] # Get current grid index

                         # Cell container for padding
                         cell_container = ctk.CTkFrame(row_frame, fg_color="transparent")
                         cell_container.grid(row=0, column=grid_col, sticky="ew", padx=0, pady=0)
                         cell_container.grid_columnconfigure(0, weight=1)

                         # Create widget based on column type
                         if col_name == "Select":
                             checkbox_var = tk.BooleanVar(value=(engineer.id in self.selected_rows))
                             checkbox = ctk.CTkCheckBox(cell_container, text="", variable=checkbox_var, command=lambda eng_id=engineer.id: self.toggle_row_selection(eng_id), width=20, height=20, fg_color="#1f538d", hover_color="#3b8ed0", border_color="#4F4F4F", corner_radius=3)
                             checkbox.grid(row=0, column=0, sticky="w", padx=(self.base_left_padding, 0), pady=self.vertical_padding)
                         elif col_name == "Actions":
                             actions_frame = self._create_actions_frame(cell_container, engineer)
                             actions_frame.grid(row=0, column=0, sticky="ew", padx=(self.base_left_padding, 5), pady=(self.vertical_padding // 2))
                         elif col_info.get("db_field"):
                             attr_val = getattr(engineer, col_info["db_field"], "-") # Get data from engineer object
                             # Format data for display
                             if isinstance(attr_val, bool): text = "Yes" if attr_val else "No" # Handles 'selected' field for 'Is PM' column
                             elif isinstance(attr_val, (int, float)): text = str(attr_val)
                             elif hasattr(attr_val, 'strftime'): # Date/datetime
                                 try: text = attr_val.strftime('%Y-%m-%d')
                                 except (ValueError, TypeError): text = str(attr_val) # Fallback
                             else: text = str(attr_val) if attr_val is not None else "-" # Default string conversion
                             # Create label
                             label = ctk.CTkLabel(cell_container, text=text, anchor="w", justify="left", font=self.data_font, text_color=self.text_color_primary)
                             label.grid(row=0, column=0, sticky="w", padx=(self.base_left_padding, 5), pady=self.vertical_padding)

            # --- Final UI Updates ---
            if self.on_page_change: self.on_page_change(self.current_page, self.total_pages)
            self._update_header_indicators()
            self._update_select_all_checkbox_state()
            # Update scroll region after layout changes
            self.content_frame.update_idletasks()
            self.after(10, self._on_content_frame_configure)

        # --- Exception Handling ---
        except Exception as e:
            print(f"Error loading table data: {str(e)}")
            print(traceback.format_exc())
            # Display error in table area
            for widget in self.content_frame.winfo_children(): widget.destroy()
            error_label = ctk.CTkLabel(self.content_frame, text=f"Error loading data:\n{str(e)}", text_color="red", font=("Arial", 12), anchor="center", justify="center")
            self.content_frame.grid_rowconfigure(0, weight=1); self.content_frame.grid_columnconfigure(0, weight=1)
            error_label.grid(row=0, column=0, columnspan=max(1, num_visible_columns), sticky="nsew", padx=20, pady=40)
            # Show notification popup
            try: show_notification(self, f"Could not load engineer data.\n{str(e)}", "Error Loading Data", "error")
            except Exception as ne: print(f"--- ERROR IN NOTIFICATION SERVICE ---"); print(f"Original error: {e}"); print(f"Notification error: {ne}"); traceback.print_exc(); messagebox.showerror("Error Loading Data", f"Could not load engineer data.\n{str(e)}\n\n(Notification service also failed)", parent=self)
        finally:
             # --- Hide Loading Indicator ---
             self.loading_label.place_forget()

    # --- Action Button Creation ---
    def _create_actions_frame(self, parent, engineer):
        """Creates action buttons frame (View/Edit, Delete)."""
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.grid_columnconfigure((0, 1), weight=1, minsize=80) # Configure button columns
        button_style = {"height": 28, "font": ("Arial", 11), "corner_radius": 5}
        # View/Edit Button
        details_btn = ctk.CTkButton(actions_frame, text="View/Edit", command=lambda eng=engineer: self.show_details_or_edit(eng), fg_color="#2B5EA7", hover_color="#2573A7", **button_style)
        details_btn.grid(row=0, column=0, padx=(0, 5), pady=1, sticky="ew")
        # Delete Button
        delete_btn = ctk.CTkButton(actions_frame, text="Delete", command=lambda eng=engineer: self.delete_engineer(eng), fg_color="#A72B2B", hover_color="#C0392B", **button_style)
        delete_btn.grid(row=0, column=1, padx=(5, 0), pady=1, sticky="ew")

        # --- Bind hover for row effect persistence ---
        row_frame = parent.master # Assumes parent is cell_container
        try: # Determine original row color
            grid_info = row_frame.grid_info(); row_idx = grid_info['row']; actual_row_color = self.row_color_1 if row_idx % 2 == 0 else self.row_color_2
        except Exception: actual_row_color = self.row_color_2 # Fallback
        # Create handlers
        def create_enter_handler(rf): return lambda e: rf.configure(fg_color=self.row_hover_color)
        def create_leave_handler(rf, rc): return lambda e: rf.configure(fg_color=rc)
        enter_handler = create_enter_handler(row_frame); leave_handler = create_leave_handler(row_frame, actual_row_color)
        # Bind to buttons
        for btn in (details_btn, delete_btn):
             btn.bind("<Enter>", enter_handler)
             btn.bind("<Leave>", leave_handler)
        return actions_frame

    # --- Selection Logic ---
    def toggle_all_rows(self, select_all_state):
        """Selects/deselects all rows on the current page."""
        ids_on_page = set(self.all_engineer_ids_on_current_page); changed = False
        if select_all_state: newly_selected = ids_on_page - self.selected_rows;
        else: to_deselect = self.selected_rows.intersection(ids_on_page)
        # Update selection set
        if select_all_state and newly_selected: self.selected_rows.update(newly_selected); changed = True
        elif not select_all_state and to_deselect: self.selected_rows.difference_update(to_deselect); changed = True
        # Reload data to update visuals if changed
        if changed: self.load_data()

    def _update_select_all_checkbox_state(self):
        """Updates the header 'Select All' checkbox state."""
        select_all_widget_data = self.header_widgets.get("Select")
        if select_all_widget_data:
            select_all_var = select_all_widget_data.get("var")
            if select_all_var:
                ids_on_page = set(self.all_engineer_ids_on_current_page)
                if not ids_on_page: select_all_var.set(False) # No items on page
                elif ids_on_page.issubset(self.selected_rows): select_all_var.set(True) # All items selected
                else: select_all_var.set(False) # Some or none selected

    def toggle_row_selection(self, engineer_id):
        """Toggles selection for a single row ID."""
        if engineer_id in self.selected_rows: self.selected_rows.remove(engineer_id)
        else: self.selected_rows.add(engineer_id)
        self._update_select_all_checkbox_state() # Update header checkbox state

    # --- Dialogs and Data Actions ---
    def show_details_or_edit(self, engineer):
        """Shows the EngineerDialog for viewing/editing."""
        # Assumes EngineerDialog is imported or defined
        dialog = EngineerDialog(self, self.session, engineer=engineer, on_save=self.load_data)

    def add_engineer(self):
        """Shows the EngineerDialog to add a new engineer."""
        # Assumes EngineerDialog is imported or defined
        dialog = EngineerDialog(self, self.session, engineer=None, on_save=self.load_data)

    # --- Methods for External Control Buttons ---
    def select_all_on_page(self):
        """Selects all engineers currently visible on the page."""
        ids_on_page = set(self.all_engineer_ids_on_current_page); newly_selected = ids_on_page - self.selected_rows
        if newly_selected:
            self.selected_rows.update(ids_on_page)
            self.load_data() # Reload to show changes
            show_notification(self, f"Selected all {len(ids_on_page)} engineers on this page.", "Selection Update", "info")
        else:
            show_notification(self, "All engineers on this page were already selected.", "Selection Info", "info")

    def clear_selection(self):
        """Clears the entire selection across all pages."""
        if self.selected_rows:
            self.selected_rows.clear()
            self.load_data() # Reload to show changes
            show_notification(self, "Selection cleared.", "Selection Update", "info")
        else:
            show_notification(self, "No engineers were selected.", "Selection Info", "info")

    # --- Other Public Methods (Pagination, Settings, etc.) ---
    def set_rows_per_page(self, value):
        """Sets the number of rows displayed per page."""
        try: new_rows = int(value)
        except ValueError: show_notification(self, "Invalid number for rows per page.", "Invalid Input", "warning"); return
        # Apply change only if value is valid and different
        if new_rows > 0 and self.rows_per_page != new_rows:
            self.rows_per_page = new_rows
            self.current_page = 1 # Reset to first page
            self.load_data()
        elif new_rows <= 0:
            show_notification(self, "Rows per page must be greater than 0.", "Invalid Value", "warning")

    def next_page(self):
        """Navigates to the next page if possible."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def prev_page(self):
        """Navigates to the previous page if possible."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def go_to_page(self, page_num):
        """Navigates to a specific page number."""
        try: page = int(page_num)
        except ValueError: show_notification(self, "Invalid page number.", "Invalid Input", "warning"); return
        # Navigate only if page is valid and different from current
        if 1 <= page <= self.total_pages and self.current_page != page:
            self.current_page = page
            self.load_data()
        elif not (1 <= page <= self.total_pages):
            show_notification(self, f"Page number must be between 1 and {self.total_pages}.", "Invalid Page", "warning")

    def clear_all_filters(self):
        """Clears all active column filters."""
        if self.column_filters:
            self.column_filters.clear()
            self.current_page = 1 # Reset to first page
            self.load_data()
            show_notification(self, "All column filters cleared.", "Filters Cleared", "info")
        else:
            show_notification(self, "No active filters to clear.", "Filters Info", "info")

    def reset_view(self):
        """ Resets filters, sorting, column visibility to defaults, and goes to page 1. """
        # Determine if any non-default state exists
        visibility_changed = any(not v for name, v in self.column_visibility.items() if next((c for c in self.columns if c['name'] == name), {}).get('hideable', True))
        filters_active = bool(self.column_filters)
        sorting_active = bool(self.sort_column)
        page_not_first = self.current_page != 1
        needs_reset = visibility_changed or filters_active or sorting_active or page_not_first

        if not needs_reset:
             show_notification(self, "Table view is already in the default state.", "View Info", "info")
             return

        # Reset state variables
        self.column_filters.clear()
        self.sort_column = None
        self.sort_direction = None
        needs_redraw = False
        if visibility_changed:
            # Reset visibility to default (all True)
            self.column_visibility = {col['name']: True for col in self.columns}
            needs_redraw = True # Visibility change requires header redraw

        self.current_page = 1 # Always go to page 1 on reset

        # Apply changes: Redraw layout if visibility changed, otherwise just reload data
        if needs_redraw:
             self._redraw_table_layout()
        else:
             self.load_data()
        show_notification(self, "Table view reset to default.", "View Reset", "info")

    def set_page_change_callback(self, callback):
        """Sets the callback function for page changes."""
        self.on_page_change = callback

    def get_selected_engineer_ids(self):
        """Returns a set of IDs of the selected engineers."""
        return set(self.selected_rows) # Return a copy

    def get_selected_engineers(self):
        """Fetches and returns the Engineer objects corresponding to the selected IDs."""
        if not self.selected_rows: return []
        try:
            # Ensure IDs are valid integers before querying
            valid_ids = [id_ for id_ in self.selected_rows if isinstance(id_, int)]
            if not valid_ids: return []
            # Fetch engineers using the SQLAlchemy session and the imported Engineer class
            return self.session.query(Engineer).filter(Engineer.id.in_(valid_ids)).all()
        except NameError: # Catch if Engineer class is not defined
             show_notification(self, "Setup Error: Engineer model not available for fetching.", "Fetch Error", "error")
             return []
        except Exception as e: # Catch other potential DB or SQLAlchemy errors
            show_notification(self, f"DB Error fetching selected engineers: {e}", "Fetch Error", "error")
            traceback.print_exc()
            return []

    def delete_engineer(self, engineer):
        """Deletes a single engineer after confirmation."""
        # Confirm with the user
        if not messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete engineer '{getattr(engineer, 'name', 'N/A')}' (ID: {getattr(engineer, 'id', 'N/A')})?",
                                   parent=self):
            return # User cancelled

        try:
            self.session.delete(engineer) # Delete from session
            self.session.commit()         # Commit changes to DB
            show_notification(self, f"Engineer '{engineer.name}' deleted successfully.", "Deletion Successful", "info")
            # Remove from selection if present and reload data
            self.selected_rows.discard(engineer.id)
            self.load_data()
        except Exception as e:
            self.session.rollback() # Rollback DB changes on error
            show_notification(self, f"Error deleting engineer: {e}", "Delete Error", "error")
            traceback.print_exc()

    def delete_selected(self):
        """Deletes all currently selected engineers after confirmation."""
        if not self.selected_rows:
            show_notification(self, "Please select one or more engineers to delete.", "No Selection", "warning")
            return

        selected_count = len(self.selected_rows)
        # Confirm with the user
        if not messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete the {selected_count} selected engineer(s)?",
                                   parent=self):
            return # User cancelled

        deleted_count = 0
        try:
            # Ensure IDs are valid integers
            valid_ids = [id_ for id_ in self.selected_rows if isinstance(id_, int)]
            if not valid_ids:
                 show_notification(self, "No valid engineer IDs selected for deletion.", "Delete Error", "error")
                 return

            # --- Perform Deletion ---
            # Use bulk delete for efficiency if cascading isn't needed or handled by DB
            # Ensure 'Engineer' refers to the imported model class
            deleted_count = self.session.query(Engineer).filter(Engineer.id.in_(valid_ids)).delete(synchronize_session=False)
            # Note: synchronize_session=False is often faster but might require session.expire_all()
            # if you need the session to reflect the deletions immediately without a refresh.
            # If you have complex cascades handled by SQLAlchemy ORM events,
            # you might need to fetch and delete individually instead.
            # Example: Fetch and delete approach
            # engineers_to_delete = self.session.query(Engineer).filter(Engineer.id.in_(valid_ids)).all()
            # if engineers_to_delete:
            #     for engineer in engineers_to_delete:
            #         self.session.delete(engineer)
            #     deleted_count = len(engineers_to_delete)

            self.session.commit() # Commit the transaction
            show_notification(self, f"Successfully deleted {deleted_count} engineer(s).", "Deletion Successful", "info")

            # Clear selection and reload data
            self.selected_rows.clear()
            self.load_data()

        except NameError: # Catch if Engineer class is not defined
             show_notification(self, "Setup Error: Engineer model not available for deletion.", "Delete Error", "error")
             self.session.rollback() # Rollback any partial changes
        except Exception as e: # Catch other potential DB or SQLAlchemy errors
            self.session.rollback() # Rollback DB changes on error
            show_notification(self, f"Error deleting selected engineers: {e}", "Delete Error", "error")
            traceback.print_exc()
            # Optionally reload data even on error to reflect potential partial success/failure
            self.load_data()

