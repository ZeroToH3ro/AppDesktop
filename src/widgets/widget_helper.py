import customtkinter as ctk

class WidgetHelper:
    @staticmethod
    def create_section_header(parent, text, row):
        """Create a section header label."""
        header = ctk.CTkLabel(parent, text=text, font=("Arial", 14, "bold"))
        header.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))
        return row + 1

    @staticmethod
    def create_entry_row(parent, label, row):
        """Create a labeled entry row."""
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return entry

    @staticmethod
    def create_textbox_row(parent, label, row, height):
        """Create a labeled textbox row."""
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="nw")
        textbox = ctk.CTkTextbox(parent, height=height)
        textbox.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
        return textbox

    @staticmethod
    def add_relationship_section(parent, title, row, add_method, items_getter):
        """
        Create a relationship section with add button.
        Returns the next available row number.
        """
        row = WidgetHelper.create_section_header(parent, title, row)
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        setattr(parent, f"{title.lower().replace(' ', '_')}_frame", frame)
        setattr(parent, f"{title.lower().replace(' ', '_')}", [])
        ctk.CTkButton(
            frame, text=f"Add {title.rstrip('s')}", command=lambda: add_method(frame)
        ).pack(pady=5)
        setattr(parent, f"get_{title.lower().replace(' ', '_')}", items_getter)
        return row + 1
