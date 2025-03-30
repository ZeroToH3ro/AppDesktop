import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime

class DatePicker(ctk.CTkFrame):
    def __init__(self, master, label="", default_date=None):
        super().__init__(master)
        
        if label:
            self.label = ctk.CTkLabel(self, text=label)
            self.label.pack(side="left", padx=5)
        
        # Create the date entry widget
        self.date_entry = DateEntry(
            self,
            width=12,
            background='#2b2b2b',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',  # Changed to consistent ISO format
            selectbackground='#1f538d',
            selectforeground='white',
            normalbackground='#2b2b2b',
            normalforeground='white',
            weekendbackground='#333333',
            weekendforeground='white',
            headersbackground='#333333',
            headersforeground='white'
        )
        self.date_entry.pack(side="left", padx=5)
        
        if default_date:
            self.set(default_date)
    
    def get(self):
        """Get the selected date in YYYY-MM-DD format"""
        try:
            date = self.date_entry.get_date()
            return date.strftime("%Y-%m-%d")
        except Exception:
            return ""
    
    def set(self, date_str):
        """Set the date. Accepts either YYYY-MM-DD or YY.MM.DD format"""
        if not date_str:
            return
            
        try:
            if len(date_str) == 8:  # YY.MM.DD format
                date_obj = datetime.strptime(date_str, "%y.%m.%d")
            elif len(date_str) == 10:  # YYYY-MM-DD format
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                return
            self.date_entry.set_date(date_obj)
        except (ValueError, TypeError):
            # Invalid date format, keep current date
            pass

class PeriodPicker(ctk.CTkFrame):
    def __init__(self, master, label=""):
        super().__init__(master)
        
        if label:
            self.label = ctk.CTkLabel(self, text=label)
            self.label.pack(side="left", padx=5)
        
        # Start date picker
        self.start_date = DatePicker(self)
        self.start_date.pack(side="left")
        
        # Separator
        self.separator = ctk.CTkLabel(self, text="-")
        self.separator.pack(side="left", padx=2)
        
        # End date picker
        self.end_date = DatePicker(self)
        self.end_date.pack(side="left")
    
    def get(self):
        start = self.start_date.get()
        end = self.end_date.get()
        if start and end:
            return f"{start} - {end}"
        return ""
    
    def set(self, period_str):
        if period_str and " - " in period_str:
            try:
                start_str, end_str = period_str.split(" - ")
                self.start_date.set(start_str)
                self.end_date.set(end_str)
            except ValueError:
                pass
