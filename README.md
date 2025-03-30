# AppDesktop

A desktop application for managing engineer information built with Python and CustomTkinter.

## Project Structure

```
AppDesktop/
├── main.py              # Application entry point
├── requirements.txt     # Project dependencies
├── src/
│   ├── app.py          # Main application window
│   ├── models/         # Database models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── engineer.py
│   ├── views/          # UI components
│   │   ├── __init__.py
│   │   ├── engineer_table.py
│   │   ├── engineer_detail.py
│   │   └── engineer_dialog.py
│   ├── services/       # Business logic and services
│   ├── utils/          # Utility functions
│   │   └── db.py
│   └── widgets/        # Reusable UI widgets
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Features

- Modern dark/light theme support
- Engineer information management
  - Add/Edit/Delete engineers
  - View detailed engineer information
  - Search and filter engineers
- SQLite database for data persistence
- Responsive UI with pagination
- Profile and role management
