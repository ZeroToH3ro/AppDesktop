import customtkinter as ctk
from src.app import App

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = App()
    app.mainloop()