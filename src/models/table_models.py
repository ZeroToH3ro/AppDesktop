from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QColor
from src.models.engineer import Engineer
from src.services.translator import translator

class EngineerTableModel(QAbstractTableModel):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.engineers = []
        self.filtered_engineers = []
        self.filter_text = ""
        self.page_size = 10
        self.current_page = 0
        self.selected_rows = set()
        self.header_keys = ["id", "name", "birth_date", "address", "company", "technical_grade"]
        self.update_headers()
        self.load_data()
        
    def update_headers(self):
        """Update table headers based on current language"""
        self.headers = [
            "ID",
            translator.translate("name"),
            translator.translate("birth_date"),
            translator.translate("address"),
            translator.translate("company"),
            translator.translate("technical_grade")
        ]
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            engineers = self.get_visible_engineers()
            if not engineers or index.row() >= len(engineers):
                return None
                
            engineer = engineers[index.row()]
            if index.column() == 0:
                return str(engineer.id)
            elif index.column() == 1:
                return engineer.person_name
            elif index.column() == 2:
                return engineer.birth_date
            elif index.column() == 3:
                return engineer.address
            elif index.column() == 4:
                return engineer.associated_company
            elif index.column() == 5:
                if engineer.technical_grades and 'grade' in engineer.technical_grades:
                    return engineer.technical_grades['grade'][0]
                return ""
        
        elif role == Qt.TextAlignmentRole:
            if index.column() == 0:  # ID column
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                return QColor("#1e2433")
            return QColor("#262b40")
            
        elif role == Qt.ForegroundRole:
            return QColor("#ffffff")
            
        elif role == Qt.CheckStateRole and index.column() == 0:
            if index.row() in self.selected_rows:
                return Qt.Checked
            return Qt.Unchecked

        return None
        
    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and index.column() == 0:
            if value == Qt.Checked:
                self.selected_rows.add(index.row())
            else:
                self.selected_rows.discard(index.row())
            self.dataChanged.emit(index, index)
            return True
        return False
        
    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def load_data(self):
        self.engineers = self.session.query(Engineer).all()
        self.apply_filter()
        
    def apply_filter(self, filter_text=""):
        self.filter_text = filter_text.lower()
        if not self.filter_text:
            self.filtered_engineers = self.engineers.copy()
        else:
            self.filtered_engineers = [
                engineer for engineer in self.engineers
                if (self.filter_text in str(engineer.id).lower() or
                    self.filter_text in (engineer.person_name or "").lower() or
                    self.filter_text in (engineer.address or "").lower() or
                    self.filter_text in (engineer.associated_company or "").lower() or
                    (engineer.technical_grades and 
                     self.filter_text in str(engineer.technical_grades.get('grade', [''])[0]).lower()))
            ]
        self.current_page = 0
        self.selected_rows.clear()
        self.layoutChanged.emit()
        
    def set_page(self, page):
        if page >= 0 and page <= self.page_count() - 1:
            self.current_page = page
            self.layoutChanged.emit()
            
    def set_page_size(self, size):
        self.page_size = size
        self.current_page = 0
        self.layoutChanged.emit()
            
    def page_count(self):
        if not self.filtered_engineers:
            return 1
        return max(1, (len(self.filtered_engineers) + self.page_size - 1) // self.page_size)
    
    def get_visible_engineers(self):
        start = self.current_page * self.page_size
        end = min(start + self.page_size, len(self.filtered_engineers))
        if start >= len(self.filtered_engineers):
            return []
        return self.filtered_engineers[start:end]

    def rowCount(self, parent=None):
        return min(self.page_size, len(self.get_visible_engineers()))

    def columnCount(self, parent=None):
        return len(self.header_keys)

    def get_selected_engineers(self):
        """Return list of selected engineers"""
        engineers = self.get_visible_engineers()
        return [engineers[row] for row in self.selected_rows if row < len(engineers)]
