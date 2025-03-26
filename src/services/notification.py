import customtkinter as ctk
from PIL import Image, ImageDraw

class CustomNotification(ctk.CTkFrame):
    def __init__(self, message, icon_type="success", parent=None, auto_close=True, duration=2000):
        super().__init__(parent)
        self.configure(fg_color=("#2d325a", "#2d325a"))
        self.grid_columnconfigure(1, weight=1)
        
        # Create icon
        icon_size = 24
        icon_image = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon_image)
        
        if icon_type == "success":
            # Draw success icon
            draw.ellipse([2, 2, icon_size-4, icon_size-4], fill="#4CAF50")
            draw.line((8, 12, 12, 16), fill="white", width=2)
            draw.line((12, 16, 18, 8), fill="white", width=2)
        else:
            # Draw error icon
            draw.ellipse([2, 2, icon_size-4, icon_size-4], fill="#FF5252")
            draw.line((8, 8, 16, 16), fill="white", width=2)
            draw.line((8, 16, 16, 8), fill="white", width=2)
        
        self.icon_image = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(24, 24))
        self.icon_label = ctk.CTkLabel(self, text="", image=self.icon_image)
        self.icon_label.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Message label
        self.message_label = ctk.CTkLabel(self, text=message, text_color="white")
        self.message_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        if not auto_close:
            # Close button for error messages
            self.close_button = ctk.CTkButton(
                self, text="×", width=30, height=30,
                command=self.destroy,
                fg_color="transparent",
                text_color="white",
                hover_color=("#3d425a", "#3d425a")
            )
            self.close_button.grid(row=0, column=2, padx=(5, 10), pady=10)
        
        if auto_close:
            self.after(duration, self.destroy)

class NotificationService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.active_notifications = []
        self.notification_spacing = 10
    
    def close_all_notifications(self):
        for notification in self.active_notifications:
            if notification.winfo_exists():
                notification.destroy()
        self.active_notifications.clear()
    
    def _position_notification(self, notification):
        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        
        notification.update_idletasks()
        width = notification.winfo_width()
        height = notification.winfo_height()
        
        x = screen_width - width - 20
        y = 40
        
        # Adjust position based on existing notifications
        for existing in self.active_notifications:
            if existing.winfo_exists():
                y += existing.winfo_height() + self.notification_spacing
        
        notification.place(x=x, y=y)
        self.active_notifications.append(notification)
    
    def show_success(self, message, parent=None, duration=2000):
        notification = CustomNotification(
            message, icon_type="success",
            parent=parent, auto_close=True,
            duration=duration
        )
        self._position_notification(notification)
    
    def show_error(self, message, parent=None):
        notification = CustomNotification(
            message, icon_type="error",
            parent=parent, auto_close=False
        )
        self._position_notification(notification)

# Create a singleton instance
notification = NotificationService()
