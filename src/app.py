import customtkinter as ctk
from PIL import Image, ImageDraw
import tkinter as tk # Import tkinter for StringVar

# Make sure EngineerTable is imported correctly
from src.views.engineer_table import EngineerTable
from src.views.engineer_dialog import EngineerDialog
from src.utils.db import init_database
from src.services.notification import notification
from CTkMessagebox import CTkMessagebox

# Constants
SIDEBAR_WIDTH = 200
ICON_SIZE = 20

# Theme icons
MOON_ICON = "🌙"
SUN_ICON = "☀️"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        notification.set_main_window(self)
        self.title("Engineer Management System")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.resizable(True, True)
        self.minsize(1000, 600) # Adjust minsize considering new columns

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.session = init_database()

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)
        # (Profile and Nav items code remains the same...)
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        profile_frame.grid_columnconfigure(0, weight=1)
        profile_size = 80
        profile_image = Image.new('RGB', (profile_size, profile_size), color='#2B2B2B')
        draw = ImageDraw.Draw(profile_image)
        draw.ellipse([0, 0, profile_size, profile_size], fill='#1F538D')
        draw.text((profile_size//2, profile_size//2), "A", fill='white', anchor='mm', font=None)
        self.profile_photo = ctk.CTkImage(light_image=profile_image, dark_image=profile_image, size=(profile_size, profile_size))
        profile_label = ctk.CTkLabel(profile_frame, text="", image=self.profile_photo)
        profile_label.grid(row=0, column=0, pady=(0, 10))
        profile_name = ctk.CTkLabel(profile_frame, text="Admin User", font=("Arial Bold", 16), text_color="white", anchor="center")
        profile_name.grid(row=1, column=0)
        profile_role = ctk.CTkLabel(profile_frame, text="System Administrator", font=("Arial", 12), text_color="white", anchor="center")
        profile_role.grid(row=2, column=0)
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_items = [("Dashboard", "📊"), ("Engineers", "👷"), ("Reports", "📄"), ("Settings", "⚙️"),
                     ("Import Data", "📂"), ("Companies", "🏢"), ("Projects", "📋"), ("Saved Combinations", "💾")]
        self.active_nav_item = None
        for i, (text, icon) in enumerate(nav_items):
            nav_item_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            nav_item_frame.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            nav_item_frame.grid_columnconfigure(1, weight=1)
            def create_hover_effect(frame, text, icon, command):
                # Simplified hover effect for brevity - keep your original if preferred
                icon_label = ctk.CTkLabel(frame, text=icon, font=("Arial", 16), width=30, fg_color="transparent", text_color=("gray10", "gray90"))
                icon_label.grid(row=0, column=0, padx=(5, 5))
                text_label = ctk.CTkLabel(frame, text=text, font=("Arial Bold", 13), fg_color="transparent", text_color=("gray10", "gray90"), anchor="w")
                text_label.grid(row=0, column=1, sticky="w")
                frame.bind("<Button-1>", lambda e, t=text: command(t))
                icon_label.bind("<Button-1>", lambda e, t=text: command(t))
                text_label.bind("<Button-1>", lambda e, t=text: command(t))
                frame.configure(cursor="hand2"); icon_label.configure(cursor="hand2"); text_label.configure(cursor="hand2")
            create_hover_effect(nav_item_frame, text, icon, self.on_nav_button_click)
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, padx=20, pady=20, sticky="sew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        logout_button = ctk.CTkButton(bottom_frame, text="Logout", command=self.logout, font=("Arial Bold", 13), height=35, width=160, fg_color="#2980B9", hover_color="#2471A3")
        logout_button.grid(row=0, column=0, pady=(0, 10))
        quit_button = ctk.CTkButton(bottom_frame, text="Quit", command=self.quit, font=("Arial Bold", 13), height=35, width=160, fg_color="#E74C3C", hover_color="#C0392B")
        quit_button.grid(row=1, column=0, pady=(0, 20))

        # --- Main Content Area ---
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(1, weight=1) # Allow table to expand
        self.content.grid_columnconfigure(0, weight=1) # Allow toolbar and table to expand horizontally

        # --- Top Toolbar ---
        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10)) # Use padx=0 for toolbar itself
        # Configure toolbar grid columns
        toolbar.grid_columnconfigure(0, weight=0) # Theme button
        toolbar.grid_columnconfigure(1, weight=1) # Search Entry
        toolbar.grid_columnconfigure(2, weight=0) # Filter Dropdown
        toolbar.grid_columnconfigure(3, weight=0) # Select All Button
        toolbar.grid_columnconfigure(4, weight=0) # Clear Selection Button
        toolbar.grid_columnconfigure(5, weight=0) # Add Engineer Button

        # Theme toggle button
        self.is_dark_theme = True
        self.theme_button = ctk.CTkButton(
            toolbar, text=MOON_ICON, width=40, height=35, command=self.toggle_theme,
            font=("Arial", 16), fg_color="transparent", hover_color=("gray70", "gray30"), corner_radius=8
        )
        self.theme_button.grid(row=0, column=0, padx=(5, 10))

        # Search Entry
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Enter value to filter by...", height=35)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        # Removed KeyRelease binding - filtering triggered by dropdown change
        # self.search_entry.bind("<KeyRelease>", self.on_search)

        # --- Filter Dropdown ---
        filter_options = ["Filter by...", "Company", "Technical Field", "Expertise", "Experience", "Rating", "Is PM"] # Add relevant filterable fields
        self.filter_var = tk.StringVar(value=filter_options[0])
        self.filter_menu = ctk.CTkOptionMenu(
            toolbar,
            values=filter_options,
            variable=self.filter_var,
            command=self.apply_app_filter, # Call filter function on change
            height=35,
            width=150 # Adjust width as needed
        )
        self.filter_menu.grid(row=0, column=2, padx=(0, 10))

        # --- Select All / Clear All Buttons ---
        select_all_button = ctk.CTkButton(
            toolbar, text="Select All (Page)", command=self.select_all_on_page, height=35, font=("Arial Bold", 12)
        )
        select_all_button.grid(row=0, column=3, padx=(0, 5))

        clear_sel_button = ctk.CTkButton(
            toolbar, text="Clear Selection", command=self.clear_selection, height=35, font=("Arial Bold", 12), fg_color="gray50", hover_color="gray40"
        )
        clear_sel_button.grid(row=0, column=4, padx=(0, 10))


        # Add Engineer button
        add_button = ctk.CTkButton(
            toolbar, text="Add Engineer", command=self.add_engineer, height=35, font=("Arial Bold", 12)
        )
        add_button.grid(row=0, column=5, padx=(0, 5))

        # --- Create engineer table ---
        self.engineer_table = EngineerTable(self.content, self.session)
        self.engineer_table.grid(row=1, column=0, sticky="nsew")

        # --- Create pagination frame ---
        pagination_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        pagination_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0)) # Reduced bottom padding
        # Adjust weights for better centering/distribution if needed
        pagination_frame.grid_columnconfigure(0, weight=1) # Label spacer left
        pagination_frame.grid_columnconfigure(1, weight=0) # Label
        pagination_frame.grid_columnconfigure(2, weight=0) # Dropdown
        pagination_frame.grid_columnconfigure(3, weight=2) # Spacer middle
        pagination_frame.grid_columnconfigure(4, weight=0) # Prev
        pagination_frame.grid_columnconfigure(5, weight=0) # Page info
        pagination_frame.grid_columnconfigure(6, weight=0) # Next
        pagination_frame.grid_columnconfigure(7, weight=1) # Label spacer right


        rows_label = ctk.CTkLabel(pagination_frame, text="Rows per page:")
        rows_label.grid(row=0, column=1, padx=(0,2))

        rows_var = tk.StringVar(value="10")
        rows_dropdown = ctk.CTkOptionMenu(
            pagination_frame, values=["5", "10", "20", "50"], variable=rows_var,
            command=lambda v: self.engineer_table.set_rows_per_page(int(v)), width=70
        )
        rows_dropdown.grid(row=0, column=2, padx=(0,20))

        prev_btn = ctk.CTkButton(pagination_frame, text="Previous", command=self.engineer_table.prev_page, width=100)
        prev_btn.grid(row=0, column=4, padx=5)

        self.page_label = ctk.CTkLabel(pagination_frame, text="Page 1 of 1")
        self.page_label.grid(row=0, column=5, padx=5)

        next_btn = ctk.CTkButton(pagination_frame, text="Next", command=self.engineer_table.next_page, width=100)
        next_btn.grid(row=0, column=6, padx=5)

        self.engineer_table.set_page_change_callback(self.update_page_info)

        # Initial load
        self.show_engineers_page()
        # Update pagination button states initially
        self.update_page_info(self.engineer_table.current_page, self.engineer_table.total_pages)


    def on_nav_button_click(self, text):
        if text == "Engineers":
            self.show_engineers_page()
        else:
            # Placeholder for other pages
            print(f"Navigate to {text} (not implemented)")
            # Clear content or show placeholder frame for other pages
            for widget in self.content.winfo_children():
                 # Keep toolbar, hide/destroy others like table and pagination
                 if isinstance(widget, EngineerTable) or widget == self.content.grid_slaves(row=2, column=0)[0]: # Find pagination frame better if needed
                     widget.grid_forget()


    def show_engineers_page(self):
        # Ensure table and pagination are visible
        self.engineer_table.grid(row=1, column=0, sticky="nsew")
        # Find pagination frame and grid it back if forgotten
        pagination_frame = self.content.grid_slaves(row=2, column=0)
        if pagination_frame:
            pagination_frame[0].grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.engineer_table.load_data()


    def add_engineer(self):
        # Pass self as parent for the dialog
        dialog = EngineerDialog(self, self.session, on_save=self.engineer_table.load_data)
        dialog.grab_set() # Make dialog modal

    # Removed on_search as filtering is now driven by dropdown
    # def on_search(self, event):
    #     self.engineer_table.apply_filter(self.search_entry.get())

    def apply_app_filter(self, selected_field):
        """Called when the filter dropdown selection changes."""
        search_term = self.search_entry.get()
        if selected_field == "Filter by...":
            # Clear specific filter if default option is chosen
             self.engineer_table.apply_specific_filter(None, "")
        else:
            # Apply filter for the selected field using the search term
            self.engineer_table.apply_specific_filter(selected_field, search_term)

    def update_page_info(self, current_page, total_pages):
        self.page_label.configure(text=f"Page {current_page} of {total_pages}")
        # Enable/disable buttons based on page (assuming buttons are stored/accessible)
        # Example: Find buttons and configure state (more robust way is to store button references)
        pagination_frame = self.page_label.master
        prev_btn = pagination_frame.grid_slaves(row=0, column=4)[0] # Find button by grid pos
        next_btn = pagination_frame.grid_slaves(row=0, column=6)[0] # Find button by grid pos
        prev_btn.configure(state="normal" if current_page > 1 else "disabled")
        next_btn.configure(state="normal" if current_page < total_pages else "disabled")


    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        ctk.set_appearance_mode("dark" if self.is_dark_theme else "light")
        self.theme_button.configure(text=MOON_ICON if self.is_dark_theme else SUN_ICON)

    def logout(self):
        msg = CTkMessagebox(title="Confirm Logout", message="Are you sure you want to logout?", icon="question", option_1="Cancel", option_2="Logout")
        if msg.get() == "Logout": self.destroy()

    # --- Methods to connect to table ---
    def select_all_on_page(self):
        if hasattr(self, 'engineer_table'):
            self.engineer_table.select_all_on_page()

    def clear_selection(self):
        if hasattr(self, 'engineer_table'):
            self.engineer_table.clear_selection()