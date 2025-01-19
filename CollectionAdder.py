import os.path
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel, QFormLayout, QLineEdit, QListWidget, \
    QScrollArea, QHBoxLayout, QFrame, QDialog, QMessageBox, QCheckBox
from BookBox import *


class CollectionAdder(QWidget):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Создатель коллекций")
        self.move(650, 200)
        self.setFixedSize(600, 500)
        self.setWindowIcon(QIcon("icons/default-book-cover.png"))

        self.selected_books = []

        collection_adder_layout = QVBoxLayout(self)

        collection_title_label = QLabel("Название коллекции:")
        self.collection_title_line_edit = QLineEdit()

        collection_adder_button = QPushButton("Принять")
        collection_adder_button.clicked.connect(self.accept_collection)

        self.copy_check_box = QCheckBox()
        self.copy_check_box.setText("Книги будут полностью перемещены")
        self.copy_check_box.setCheckState(Qt.Checked)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QFrame()
        self.books_layout = QHBoxLayout(container)
        container.setLayout(self.books_layout)
        scroll_area.setWidget(container)

        self.populate_list()

        collection_adder_layout.addWidget(collection_title_label)
        collection_adder_layout.addWidget(self.collection_title_line_edit)
        collection_adder_layout.addWidget(scroll_area)
        collection_adder_layout.addWidget(self.copy_check_box)
        collection_adder_layout.addWidget(collection_adder_button)

    def populate_list(self):
        """Заполняем горизонтальный список книг"""
        book_list = self.app.book_list
        for book in book_list:
            book_box = BookBox(self.app, book)
            book_box.mousePressEvent = lambda e, b=book_box: self.toggle_selection(b)
            self.books_layout.addWidget(book_box)

    def toggle_selection(self, book_box):
        """Выделяет/снимает выделение с книги"""
        if book_box.flag:
            book_box.flag = False
            self.selected_books.remove(book_box.book)
            book_box.setStyleSheet("background: transparent; border: none;")
        else:
            book_box.flag = True
            self.selected_books.append(book_box.book)
            book_box.setStyleSheet("""
                border: 2px solid blue;
                border-radius: 10px;
            """)

    def accept_collection(self):
        """Обработка выбранных книг"""
        collection_name = self.collection_title_line_edit.text()
        if not collection_name:
            execute_message_box("Ошибка!", "Название коллекции не задано!")
            return

        if not self.selected_books:
            execute_message_box("Ошибка!", "Нет выбранных книг!")
            return

        if not os.path.isdir("collections"):
            os.mkdir("collections")

        chars = r"\?/*:|+"
        dir_name = str.maketrans("", "", chars)
        dir_name = collection_name.translate(dir_name)
        if not os.path.isdir(f"collections/{dir_name}"):
            os.mkdir(f"collections/{dir_name}")
            if self.copy_check_box.isChecked():
                for book in self.selected_books:
                    shutil.move(book.file_path, f"collections/{dir_name}")
            else:
                for book in self.selected_books:
                    shutil.copy(book.file_path, f"collections/{dir_name}")
                self.app.collection_list = self.app.list_creation("collections", flag=False)
                self.app.populate_sidebar()
                self.app.collection_pages = {}
                for collection in self.app.collection_list:
                    self.app.create_collection_page(collection)
                self.close()
            execute_message_box("Сообщение", f"Создана коллекция {collection_name}")
        else:
            execute_message_box("Ошибка!", f"Коллекция по директории '{dir_name}' уже существует!")


def execute_message_box(title, txt):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(txt)
    msg_box.setWindowIcon(QIcon("icons/default-book-cover.png"))
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
