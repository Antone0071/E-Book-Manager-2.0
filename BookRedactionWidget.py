import os
import shutil

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QFormLayout, QLabel, QSpacerItem, \
    QSizePolicy
import zipfile
import xml.etree.ElementTree as ET


class BookRedactionWidget(QtWidgets.QListWidget):
    """Добавить 3 поля ввода с уже введённым текстом из экземпляра. Кнопка отмены и сохранения:
 Отмена  - выход из окна без каких-либо изменений
 Сохранение - проход обработчиком событий по полям ввода, сверке и изменении данных по path экземпляра класса по необходимости"""

    def __init__(self, book, app):
        super(BookRedactionWidget, self).__init__()
        self.book = book
        self.app = app
        self.path = self.book.file_path
        self.move(700, 200)
        self.setFixedSize(800, 400)
        self.setWindowTitle("Редактирование " + book.title)

        main_layout = QVBoxLayout(self)

        books_redaction_layout = QFormLayout()

        self.title_line_edit = QLineEdit()
        self.title_line_edit.setText(self.book.title)

        title_label = QLabel("Название книги:")

        self.author_line_edit = QLineEdit()
        self.author_line_edit.setText(self.book.author)

        author_label = QLabel("Автор книги:")

        self.genre_line_edit = QLineEdit()
        self.genre_line_edit.setText(self.book.genre)

        genre_label = QLabel("Жанр книги:")

        books_redaction_layout.addRow(title_label, self.title_line_edit)
        books_redaction_layout.addRow(author_label, self.author_line_edit)
        books_redaction_layout.addRow(genre_label, self.genre_line_edit)

        button_layout = QHBoxLayout()

        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("background-color: blue")
        save_button.clicked.connect(self.save_changes)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.cancel_changes)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(books_redaction_layout)
        main_layout.addLayout(button_layout)

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Expanding)
        books_redaction_layout.addItem(spacer)

    def save_changes(self):

        if self.book.title != self.title_line_edit.text() or self.book.author != self.author_line_edit.text() or self.book.genre != self.genre_line_edit.text():
            if self.book.file_path.endswith(".epub"):
                self.parse_epub(self.book.file_path)

            elif self.book.file_path.endswith(".fb2"):
                self.parse_fb2(self.book.file_path)
            else:
                print("Формат данной книги не подлежит редактированию")
            self.app.restart_activation()
            self.close()

    def cancel_changes(self):
        self.close()

    def parse_epub(self, path):
        temp_dir = "temp_epub"
        new_epub_path = path.replace(".epub", "_updated.epub")

        # Распаковка архива
        with zipfile.ZipFile(path, "r") as epub:
            epub.extractall(temp_dir)

        opf_path = None
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith("content.opf"):
                    opf_path = os.path.join(root, file)
                    break

        if opf_path:
            # Редактирование файла content.opf
            tree = ET.parse(opf_path)
            root = tree.getroot()
            ns = {'dc': 'http://purl.org/dc/elements/1.1/'}

            title_element = root.find('.//dc:title', ns)
            author_element = root.find('.//dc:creator', ns)
            genre_element = root.find('.//dc:subject', ns)

            if title_element is not None:
                title_element.text = self.title_line_edit.text()
            if author_element is not None:
                author_element.text = self.author_line_edit.text()
            if genre_element is not None:
                genre_element.text = self.genre_line_edit.text()

            tree.write(opf_path, encoding="utf-8", xml_declaration=True)

        # Пересоздание ZIP-архива с сжатием
        with zipfile.ZipFile(new_epub_path, "w", compression=zipfile.ZIP_DEFLATED) as new_epub:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, temp_dir)
                    new_epub.write(file_path, archive_name)

        # Удаление временной директории
        shutil.rmtree(temp_dir)

        # Замена старого файла новым
        os.replace(new_epub_path, path)

    def parse_fb2(self, path):
        tree = ET.parse(path)
        root = tree.getroot()
        ns = {'fb2': 'http://www.gribuser.ru/xml/fictionbook/2.0'}

        # Редактирование имени автора
        author_element = root.find('.//fb2:author', ns)
        if author_element is not None:
            first_name = author_element.find('./fb2:first-name', ns)
            last_name = author_element.find('./fb2:last-name', ns)

            full_name = self.author_line_edit.text()
            if first_name is not None:
                first_name.text = full_name
            if last_name is not None:
                last_name.clear()  # Очистка last-name

        # Редактирование заголовка
        title = root.find('.//fb2:book-title', ns)
        if title is not None:
            title.text = self.title_line_edit.text()

        # Редактирование жанра
        genre = root.find('.//fb2:genre', ns)
        if genre is not None:
            genre.text = self.genre_line_edit.text()

        # Сохранение изменений
        tree.write(path, encoding="utf-8", xml_declaration=True)
