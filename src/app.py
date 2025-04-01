import customtkinter as ctk
from PIL import Image, ImageDraw
from src.utils.db import init_database
from src.views import EngineerTable, EngineerDialog
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
        
        # Set this window as the main window for notifications
        notification.set_main_window(self)
        
        # Configure window
        self.title("Engineer Management System")
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set initial window size to 90% of screen size
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Calculate center position
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        # Set window size and position
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # Make window resizable
        self.resizable(True, True)
        
        # Set minimum window size
        self.minsize(1000, 600)
        
        # Configure grid with weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create SQLite database
        self.session = init_database()
        
        # Create sidebar with fixed width
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)  # Prevent sidebar from resizing
        
        # Configure sidebar grid
        self.sidebar.grid_rowconfigure(1, weight=1)  # Make nav_frame expandable
        self.sidebar.grid_columnconfigure(0, weight=1)
        
        # Profile section
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        profile_frame.grid_columnconfigure(0, weight=1)  # Center content
        
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
        
        profile_label = ctk.CTkLabel(profile_frame, text="", image=self.profile_photo)
        profile_label.grid(row=0, column=0, pady=(0, 10))
        
        # Profile name
        profile_name = ctk.CTkLabel(
            profile_frame,
            text="Admin User",
            font=("Arial Bold", 16),
            text_color="white",
            anchor="center"
        )
        profile_name.grid(row=1, column=0)
        
        # Profile role
        profile_role = ctk.CTkLabel(
            profile_frame,
            text="System Administrator",
            font=("Arial", 12),
            text_color="white",
            anchor="center"
        )
        profile_role.grid(row=2, column=0)
        
        # Navigation section
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        nav_frame.grid_columnconfigure(0, weight=1)
        
        # Navigation items
        nav_items = [
            ("Dashboard", "📊"),  # Chart for Dashboard
            ("Engineers", "👷"),  # Construction worker for Engineers
            ("Reports", "📄"),    # Document for Reports
            ("Settings", "⚙️"),   # Gear remains for Settings
            ("Import Data", "📂"), # Folder for Import File
            ("Companies", "🏢"),    # Office building for Company
            ("Projects", "📋"),    # Clipboard for Projects
            ("Saved Combinations", "💾"), # Save icon for Saved Companies
        ]   
        
        self.active_nav_item = None  # Track active navigation item
        
        for i, (text, icon) in enumerate(nav_items):
            # Create a frame for each nav item
            nav_item_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            nav_item_frame.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            nav_item_frame.grid_columnconfigure(1, weight=1)
            
            def create_hover_effect(frame, text, icon, command):
                def on_enter(e):
                    if self.active_nav_item != frame:
                        frame.configure(fg_color="gray20")
                        icon_label.configure(text_color="white")
                        text_label.configure(text_color="white")

                def on_leave(e):
                    if self.active_nav_item != frame:
                        frame.configure(fg_color="transparent")
                        icon_label.configure(text_color="gray70")
                        text_label.configure(text_color="gray70")

                def on_click(e):
                    # Remove active state from previous item
                    if self.active_nav_item:
                        self.active_nav_item.configure(fg_color="transparent")
                    frame.configure(fg_color="gray20")
                    self.active_nav_item = frame
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
        bottom_frame.grid(row=2, column=0, padx=20, pady=20, sticky="sew")  # stick to south
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        # Logout button
        logout_button = ctk.CTkButton(
            bottom_frame,
            text="Logout",
            command=self.logout,
            font=("Arial Bold", 13),
            height=35,
            width=160,  # Fixed width for buttons
            fg_color="#2980B9",
            hover_color="#2471A3"
        )
        logout_button.grid(row=0, column=0, pady=(0, 10))
        
        # Quit button
        quit_button = ctk.CTkButton(
            bottom_frame,
            text="Quit",
            command=self.quit,
            font=("Arial Bold", 13),
            height=35,
            width=160,  # Fixed width for buttons
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        quit_button.grid(row=1, column=0, pady=(0, 20))
        
        # Main content area
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Top toolbar with theme toggle and search
        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 10))
        toolbar.grid_columnconfigure(1, weight=1)  # Make search frame expand
        
        # Initialize theme
        self.is_dark_theme = True
        
        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            toolbar,
            text=MOON_ICON,  # Start with moon icon for dark theme
            width=40,
            height=35,
            command=self.toggle_theme,
            font=("Arial", 16),
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            corner_radius=8
        )
        self.theme_button.grid(row=0, column=0, padx=(5, 10))
        
        # Search frame
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search engineers...",
            height=35
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Add Engineer button
        add_button = ctk.CTkButton(
            search_frame,
            text="Add Engineer",
            command=self.add_engineer,
            height=35,
            font=("Arial Bold", 12)
        )
        add_button.grid(row=0, column=1)
        
        # Create engineer table
        self.engineer_table = EngineerTable(self.content, self.session)
        self.engineer_table.grid(row=1, column=0, sticky="nsew")
        
        # Create pagination frame
        pagination_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        pagination_frame.grid(row=2, column=0, sticky="ew", pady=(10, 20))  # Add bottom padding
        pagination_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        # Rows per page dropdown
        rows_label = ctk.CTkLabel(pagination_frame, text="Rows per page:")
        rows_label.grid(row=0, column=0, padx=5)
        
        rows_var = ctk.StringVar(value="10")
        rows_dropdown = ctk.CTkOptionMenu(
            pagination_frame,
            values=["5", "10", "20", "50"],
            variable=rows_var,
            command=lambda v: self.engineer_table.set_rows_per_page(int(v)),
            width=70
        )
        rows_dropdown.grid(row=0, column=1, padx=5)
        
        # Previous page button
        prev_btn = ctk.CTkButton(
            pagination_frame,
            text="Previous",
            command=self.engineer_table.prev_page,
            width=100
        )
        prev_btn.grid(row=0, column=2, padx=5)
        
        # Page info label
        self.page_label = ctk.CTkLabel(pagination_frame, text="Page 1 of 1")
        self.page_label.grid(row=0, column=3, padx=5)
        
        # Next page button
        next_btn = ctk.CTkButton(
            pagination_frame,
            text="Next",
            command=self.engineer_table.next_page,
            width=100
        )
        next_btn.grid(row=0, column=4, padx=5)
        
        # Set up page change callback
        self.engineer_table.set_page_change_callback(self.update_page_info)
        
        # Show engineers page by default
        self.show_engineers_page()

    def on_nav_button_click(self, text):
        if text == "Engineers":
            self.show_engineers_page()
        # Add other page handlers as needed

    def show_engineers_page(self):
        self.engineer_table.load_data()

    def add_engineer(self):
        dialog = EngineerDialog(self.session, on_save=self.engineer_table.load_data)
        dialog.grab_set()

    def on_search(self, event):
        self.engineer_table.apply_filter(self.search_entry.get())

    def update_page_info(self, current_page, total_pages):
        self.page_label.configure(text=f"Page {current_page} of {total_pages}")

    def toggle_theme(self):
        # Toggle between dark and light theme
        self.is_dark_theme = not self.is_dark_theme
        
        # Update appearance mode
        ctk.set_appearance_mode("dark" if self.is_dark_theme else "light")
        
        # Update theme button icon
        self.theme_button.configure(
            text=MOON_ICON if self.is_dark_theme else SUN_ICON
        )

    def logout(self):
        # Show confirmation dialog
        msg = CTkMessagebox(
            title="Confirm Logout",
            message="Are you sure you want to logout?",
            icon="question",
            option_1="Cancel",
            option_2="Logout"
        )
        
        if msg.get() == "Logout":
            self.destroy()
