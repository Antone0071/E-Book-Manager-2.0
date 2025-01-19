import os
import shutil

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPen, QFontMetrics, QIcon
from PyQt5.QtCore import Qt, QRect

from BookRedactionWidget import BookRedactionWidget
from EpubReader import EpubReader
from Fb2Reader import Fb2Reader


class BookBox(QWidget):
    def __init__(self, app, book):
        super().__init__()
        self.reader = None
        self.asking = None
        self.bookRedactionWidget = None
        self.flag = False
        self.book = book
        self.app = app
        self.box_min_size = (200, 250)
        self.max_width = 300
        self.init_ui()


    def open_action_activation(self):
        if self.reader is not None:
            execute_message_box("Внимание!" "Открытие новой книги невозможно, пока старая не закрыта!")
        else: self.parse_book()

    def parse_book(self):
        if self.book.file_path.endswith(".fb2"):
            #self.reader = Fb2Reader(self.book.title, self.book.file_path)
            execute_message_box("Внимание!", "Ридер для fb2 формата ещё не реализован! Ждите!")
        elif self.book.file_path.endswith(".epub"):
            execute_message_box("Внимание!", "Ридер для epub формата ещё не реализован! Ждите!")
            #self.reader = EpubReader(self.book.title, self.book.file_path)
        else:
            execute_message_box("Внимание!", "Это как вообще?")
            return
        #self.reader.show()

    def redact_action_activation(self):
        if self.bookRedactionWidget is not None:
            self.bookRedactionWidget.close()
            self.bookRedactionWidget.deleteLater()
        self.bookRedactionWidget = BookRedactionWidget(self.book, self.app)
        self.bookRedactionWidget.show()

    def delete_action_activation(self):
        if self.asking is not None:
            self.asking.close()
        self.asking = QMessageBox()
        self.asking.setText(f"Вы уверены, что хотите удалить '{self.book.title}'?")
        self.asking.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.asking.setDefaultButton(QMessageBox.No)
        self.asking.setWindowTitle("Судьба книги")

        result = self.asking.exec_()

        if result == QMessageBox.Yes:
            os.remove(self.book.file_path)
            self.deleteLater()
            self.app.restart_activation()

    def contextMenuEvent(self, event):
        self.group_collections_menu.clear()
        for collection in self.app.collection_list:
            collection_add_action = QtWidgets.QAction(collection, self)
            collection_add_action.triggered.connect(lambda checked, collection_name=collection: self.add_to_collection(collection_name))
            self.group_collections_menu.addAction(collection_add_action)
        self.contextMenu.exec_(event.globalPos())

    def add_to_collection(self, collection_name):
        # Определяем путь к файлу в коллекции
        collection_path = os.path.join("collections", collection_name)
        target_path = os.path.join(collection_path, os.path.basename(self.book.file_path))

        # Проверяем, существует ли файл в коллекции
        if os.path.exists(target_path):
            execute_message_box("Ошибка!", "Вы не можете добавить книгу в коллекцию! Она и так в ней!")
            return

        # Если файла нет, выполняем копирование
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)  # Создаем папку коллекции, если она отсутствует

        shutil.copy(self.book.file_path, target_path)
        self.app.restart_activation()
        execute_message_box("Успех!", f"Копирование '{self.book.title}' в коллекцию {collection_name} прошло успешно")

    def init_ui(self):
        self.setFixedSize(*self.box_min_size)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(5)

        cover_label = QLabel(self)
        if self.book.flag:
            pixmap = QPixmap()
            pixmap.loadFromData(self.book.cover)
            cover_label.setScaledContents(True)
        else:
            pixmap = QPixmap(self.book.cover).scaled(self.box_min_size[0], self.box_min_size[1] - 80,
                                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)

        cover_label.setPixmap(pixmap)
        cover_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(cover_label)

        title_label = QLabel(self.book.title, self)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setStyleSheet("color: black; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        author_label = QLabel(self.book.author, self)
        author_label.setFont(QFont("Arial", 9))
        author_label.setStyleSheet("color: black; background: transparent;")
        author_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_label)

        self.adjust_box_size(title_label, author_label)

        self.contextMenu = QtWidgets.QMenu(self)
        self.contextMenu.setStyleSheet("""
                    QMenu {
                        background-color: white; 
                        color: black; 
                        border: 1px solid lightgray;
                    }
                    QMenu::item {
                        background-color: transparent;
                    }
                    QMenu::item:selected { 
                        background-color: #add8e6; /* Голубой */
                        color: black; 
                    }
                """)

        self.openAction = QtWidgets.QAction("Открыть", self)
        self.contextMenu.addAction(self.openAction)

        self.group_collections_menu = self.contextMenu.addMenu("Добавить в...")

        self.redactAction = QtWidgets.QAction("Редактировать информацию", self)
        self.contextMenu.addAction(self.redactAction)

        self.deleteAction = QtWidgets.QAction("Удалить книгу", self)
        self.contextMenu.addAction(self.deleteAction)

        self.redactAction.triggered.connect(self.redact_action_activation)
        self.deleteAction.triggered.connect(self.delete_action_activation)
        self.openAction.triggered.connect(self.open_action_activation)

    def adjust_box_size(self, title_label, author_label):
        title_metrics = QFontMetrics(title_label.font())
        author_metrics = QFontMetrics(author_label.font())

        title_width = title_metrics.boundingRect(self.book.title).width()
        author_width = author_metrics.boundingRect(self.book.author).width()

        required_width = max(self.box_min_size[0], title_width + 20, author_width + 20)
        required_width = min(required_width, self.max_width)
        required_height = int(self.box_min_size[1] * 1.3)
        self.setFixedSize(required_width, required_height)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.flag = not self.flag

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRect(5, 5, self.width() - 10, self.height() - 10)
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(rect)


def execute_message_box(title, txt):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(txt)
    msg_box.setWindowIcon(QIcon("icons/default-book-cover.png"))
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
