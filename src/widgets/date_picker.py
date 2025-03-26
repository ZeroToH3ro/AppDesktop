import customtkinter as ctk
from datetime import datetime
import calendar
import tkinter as tk

class DatePicker(ctk.CTkFrame):
    def __init__(self, master, command=None):
        super().__init__(master)
        self.command = command
        self.current_date = datetime.now()
        self.selected_date = self.current_date
        
        # Create main layout
        self.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        
        # Month and Year selector
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, columnspan=7, sticky="ew", padx=5, pady=5)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Previous month button
        self.prev_button = ctk.CTkButton(
            self.header_frame, text="<", width=30,
            command=self.previous_month
        )
        self.prev_button.grid(row=0, column=0, padx=5)
        
        # Month and year label
        self.month_year_label = ctk.CTkLabel(
            self.header_frame,
            text=self.current_date.strftime("%B %Y")
        )
        self.month_year_label.grid(row=0, column=1)
        
        # Next month button
        self.next_button = ctk.CTkButton(
            self.header_frame, text=">", width=30,
            command=self.next_month
        )
        self.next_button.grid(row=0, column=2, padx=5)
        
        # Weekday headers
        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(weekdays):
            ctk.CTkLabel(self, text=day).grid(row=1, column=i, padx=2, pady=2)
        
        self.update_calendar()
    
    def update_calendar(self):
        # Clear existing calendar buttons
        for widget in self.grid_slaves():
            if isinstance(widget, ctk.CTkButton) and widget.grid_info()["row"] > 1:
                widget.destroy()
        
        # Update month/year label
        self.month_year_label.configure(
            text=self.current_date.strftime("%B %Y")
        )
        
        # Get calendar for current month
        cal = calendar.monthcalendar(
            self.current_date.year,
            self.current_date.month
        )
        
        # Create date buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = ctk.CTkButton(
                        self, text=str(day),
                        width=30, height=30,
                        command=lambda d=day: self.select_date(d)
                    )
                    btn.grid(row=week_num + 2, column=day_num, padx=2, pady=2)
                    
                    # Highlight current date
                    if (day == self.current_date.day and
                        self.current_date.month == datetime.now().month and
                        self.current_date.year == datetime.now().year):
                        btn.configure(fg_color="blue")
                    
                    # Highlight selected date
                    if (day == self.selected_date.day and
                        self.current_date.month == self.selected_date.month and
                        self.current_date.year == self.selected_date.year):
                        btn.configure(fg_color="green")
    
    def select_date(self, day):
        self.selected_date = datetime(
            self.current_date.year,
            self.current_date.month,
            day
        )
        if self.command:
            self.command(self.selected_date)
        self.update_calendar()
    
    def previous_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(
                year=self.current_date.year - 1,
                month=12
            )
        else:
            self.current_date = self.current_date.replace(
                month=self.current_date.month - 1
            )
        self.update_calendar()
    
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(
                year=self.current_date.year + 1,
                month=1
            )
        else:
            self.current_date = self.current_date.replace(
                month=self.current_date.month + 1
            )
        self.update_calendar()
    
    def get_date(self):
        return self.selected_date.strftime("%Y-%m-%d")
    
    def set_date(self, date_str):
        try:
            self.selected_date = datetime.strptime(date_str, "%Y-%m-%d")
            self.current_date = self.selected_date
            self.update_calendar()
        except ValueError:
            pass
