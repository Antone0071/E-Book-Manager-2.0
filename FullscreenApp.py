from PyQt5.QtWidgets import QGridLayout, QScrollArea, QLineEdit, QFormLayout
import BookBox
from Book import *
from BookBox import *


def list_creation():
    """Перебор файлов в storage, обработка через Book, создание списка и возврат"""
    book_list = []
    try:
        for item in os.listdir("storage"):
            item_path = os.path.join("storage", item)
            if item_path.endswith(".epub") or item_path.endswith(".fb2"):
                book = Book(item_path)
                book_list.append(book)
    except FileNotFoundError:
        print("Error: 'storage' directory not found.")
    return book_list


class FullScreenApp(QWidget):
    def __init__(self):
        super().__init__()
        self.previous_width = self.width()
        self.setWindowTitle("Book Library")
        #self.move(450, 100)
        #self.setFixedSize(980, 890)
        self.setGeometry(250, 100, 1405, 890)
        self.columns = 6
        self.book_list = list_creation()

        # Main layout
        main_layout = QHBoxLayout(self)

        # Sidebar menu
        sidebar = QListWidget()
        sidebar.setFixedWidth(150)
        sidebar.addItem(QListWidgetItem("Library"))
        sidebar.addItem(QListWidgetItem("Settings"))
        sidebar.currentRowChanged.connect(self.display_tab)

        # Stacked widget for pages
        self.pages = QStackedWidget()

        # Library tab
        library_page = QWidget()
        self.library_layout = QGridLayout(library_page)
        self.setLayout(self.library_layout)
        self.populate_grid()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(library_page)
        self.pages.addWidget(scroll_area)

        # Settings tab (empty for now)
        settings_page = QWidget()
        settings_layout = QFormLayout(settings_page)
        settings_layout.addWidget(QLabel("Settings Page"))
        self.pages.addWidget(settings_page)

        column_settings_line_edit = QLineEdit()
        column_settings_line_edit.setText(str(self.columns))

        column_settings_label = QLabel("Max count of book per row: ")

        settings_layout.addRow(column_settings_label, column_settings_line_edit)

        # Add sidebar and pages to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

    def display_tab(self, index):
        self.pages.setCurrentIndex(index)

    def show_book_quantity(self):
        return len(self.book_list)

    def resizeEvent(self, event):
        """Обработчик обновления окна"""
        super().resizeEvent(event)
        self.get_columns()
        new_columns = self.columns
        self.clear_library_layout()
        if new_columns != self.columns:
            self.columns = new_columns
            self.populate_grid()
        else:
            self.stretch_grid()

    def clear_library_layout(self):
        for i in reversed(range(self.library_layout.count())):
            box = self.library_layout.itemAt(i).widget()
            if box:
                self.library_layout.removeWidget(box)

    def stretch_grid(self):
        """Заполняет сетку виджетами на основе текущего размера окна."""
        self.get_columns()
        cols = self.columns
        row = col = 0
        for book in self.book_list:
            book_box = BookBox(book)
            self.library_layout.addWidget(book_box, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def populate_grid(self):
        """Заполняет сетку виджетами на основе текущего размера окна."""
        # Размещаем виджеты в сетке
        cols = self.columns
        row = col = 0
        for book in self.book_list:
            book_box = BookBox(book)
            self.library_layout.addWidget(book_box, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def get_columns(self):
        self.columns = max(2, self.width() // 220 - 1)