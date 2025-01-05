import PyQt5.QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGridLayout, QScrollArea, QMessageBox, QLineEdit, QFormLayout, QHBoxLayout, QPushButton, QStackedWidget, QListWidget, QListWidgetItem
import BookBox
from Book import *
from BookAdderBox import BookAdderBox
from BookBox import *
from SettingsWindow import SettingsWindow


def list_creation():
    """Перебор файлов в storage, обработка через Book, создание списка и возврат"""
    book_list = []

    if not os.path.isdir("storage"):
        os.mkdir("storage")
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
        self.setWindowTitle("Book Library")
        #self.move(450, 100)
        #self.setFixedSize(980, 890)
        self.setGeometry(250, 100, 1405, 890)
        self.setWindowIcon(QIcon("icons/default-book-cover.png"))
        self.columns = 6
        self.book_list = list_creation()

        # Main layout
        main_layout = QHBoxLayout(self)

        # Sidebar menu
        sidebar = QListWidget()
        sidebar.setFixedWidth(150)
        sidebar.addItem(QListWidgetItem("Library"))

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

        settings_button = QPushButton()
        settings_button.setIcon(QIcon("icons/settings.png"))
        settings_button.clicked.connect(self.settings_activation)
        settings_button.setFixedWidth(sidebar.width()//2 - 5)

        restart_button = QPushButton()
        restart_button.setIcon(QIcon("icons/restart.png"))
        restart_button.clicked.connect(self.restart_activation)
        restart_button.setFixedWidth(sidebar.width()//2 - 5)

        sideboard = QVBoxLayout()
        down_sideboard = QHBoxLayout()
        sideboard.addWidget(sidebar)
        down_sideboard.addWidget(settings_button)
        down_sideboard.addWidget(restart_button)
        sideboard.addLayout(down_sideboard)

        # Add sidebar and pages to main layout
        main_layout.addLayout(sideboard)
        main_layout.addWidget(self.pages)

    def restart_activation(self):
        self.book_list = list_creation()
        self.clear_library_layout()
        self.populate_grid()

    def display_tab(self, index):
        self.pages.setCurrentIndex(index)

    def show_book_quantity(self):
        return len(self.book_list)

    def settings_activation(self):
        self.settingsWindow = SettingsWindow()
        self.settingsWindow.show()

    def resizeEvent(self, event):
        """Обработчик обновления окна"""
        super().resizeEvent(event)
        self.get_columns()
        new_columns = self.columns
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
        self.clear_library_layout()
        self.get_columns()
        cols = self.columns
        row = col = 0
        for book in self.book_list:
            book_box = BookBox(self, book)
            self.library_layout.addWidget(book_box, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        adder_box = BookAdderBox(self)
        self.library_layout.addWidget(adder_box, row, col)

    def populate_grid(self):
        """Заполняет сетку виджетами на основе текущего размера окна."""
        # Размещаем виджеты в сетке
        self.clear_library_layout()
        cols = self.columns
        row = col = 0
        for book in self.book_list:
            book_box = BookBox(self, book)
            self.library_layout.addWidget(book_box, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        adder_box = BookAdderBox(self)
        self.library_layout.addWidget(adder_box, row, col)

    def get_columns(self):
        self.columns = max(2, self.width() // 220 - 1)
