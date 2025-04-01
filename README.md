# AppDesktop

A modern desktop application for managing engineers and their information, built with Python and CustomTkinter.

## Features

- 📊 Dashboard for quick overview
- 👷‍♂️ Comprehensive engineer management
- 📄 Report generation and management
- ⚙️ System settings and configuration
- 📁 Import/Export functionality
- 🏢 Company management
- 📋 Project tracking
- 💾 Saved combinations management

## Project Structure

```
AppDesktop/
├── main.py              # Application entry point
├── requirements.txt     # Project dependencies
├── src/
│   ├── app.py          # Main application window and layout
│   ├── models/         # Database models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── engineer.py
│   ├── views/          # UI components
│   │   ├── __init__.py
│   │   ├── engineer_table.py
│   │   ├── engineer_dialog.py
│   │   └── engineer_detail.py
│   ├── services/       # Business logic and services
│   │   ├── __init__.py
│   │   └── notification.py
│   ├── utils/          # Utility functions
│   │   └── db.py
│   └── widgets/        # Reusable UI widgets
```

## Setup

1. Create and activate a virtual environment:
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

## Features Overview

### User Interface
- Modern, responsive design with CustomTkinter
- Dark/Light theme support
- Intuitive sidebar navigation
- Responsive table layout for engineer data
- Pagination and rows-per-page control

### Engineer Management
- Comprehensive engineer information management
- Add/Edit/Delete functionality
- Search and filtering capabilities
- Pagination for large datasets

### Notifications
- Success/error notifications
- Toast-style message display
- Custom styling for different notification types

## Tech Stack

- Python 3.12+
- CustomTkinter for UI components
- SQLite for data storage
- Pillow for image handling

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
