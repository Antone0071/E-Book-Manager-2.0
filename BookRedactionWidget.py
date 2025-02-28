import os
import shutil
import base64

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QFormLayout, QLabel, QSpacerItem, \
    QSizePolicy, QFileDialog
import zipfile
import xml.etree.ElementTree as ET

from BookBox import *


class BookRedactionWidget(QtWidgets.QListWidget):
    """Добавить 3 поля ввода с уже введённым текстом из экземпляра. Кнопка отмены и сохранения:
 Отмена  - выход из окна без каких-либо изменений
 Сохранение - проход обработчиком событий по полям ввода, сверке и изменении данных по path экземпляра класса по необходимости"""

    def __init__(self, book, app):
        super(BookRedactionWidget, self).__init__()
        self.book = book
        self.app = app
        self.path = self.book.file_path
        self.original_cover = self.book.cover
        self.move(565, 280)
        self.setFixedSize(800, 400)
        self.setWindowTitle("Редактирование " + book.title)
        self.setWindowIcon(QIcon("icons/default-book-cover.png"))
        self.cover_data = None

        main_layout = QVBoxLayout(self)

        middle_layout = QHBoxLayout()

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
        save_button.setStyleSheet("background-color: blue; color: white")
        save_button.clicked.connect(self.save_changes)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.cancel_changes)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        book_box_widget = RedactionBookBox(self.app, self.book, self)
        middle_layout.addWidget(book_box_widget)
        middle_layout.addLayout(books_redaction_layout)

        main_layout.addLayout(middle_layout)
        main_layout.addLayout(button_layout)

        spacer = QSpacerItem(20, 50, QSizePolicy.Minimum, QSizePolicy.Expanding)
        books_redaction_layout.addItem(spacer)

    def save_changes(self):

        title_changed = self.book.title != self.title_line_edit.text()
        author_changed = self.book.author != self.author_line_edit.text()
        genre_changed = self.book.genre != self.genre_line_edit.text()
        cover_changed = self.cover_data != None

        if title_changed or author_changed or genre_changed or cover_changed:
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

        with zipfile.ZipFile(path, "r") as epub:
            epub.extractall(temp_dir)

        opf_path = None
        cover_id = None
        cover_path = None

        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith("content.opf"):
                    opf_path = os.path.join(root, file)
                    break
            if opf_path:
                break

        if opf_path:
            tree = ET.parse(opf_path)
            root = tree.getroot()
            ns = {'opf': 'http://www.idpf.org/2007/opf',
                  'dc': 'http://purl.org/dc/elements/1.1/'}

            # Находим ID обложки
            meta_cover = root.find('.//opf:meta[@name="cover"]', namespaces=ns)
            if meta_cover is not None:
                cover_id = meta_cover.get("content")

            if not cover_id:
                item_cover = root.find('.//opf:item[@properties="cover-image"]', namespaces=ns)
                if item_cover is not None:
                    cover_id = item_cover.get('id')

            if cover_id:
                cover_item = root.find(f'.//opf:item[@id="{cover_id}"]', namespaces=ns)
                if cover_item is not None:
                    cover_path = os.path.join(temp_dir, "OEBPS", cover_item.get('href'))
                    cover_path = os.path.normpath(cover_path)

            title_element = root.find(".//dc:title", ns)
            author_element = root.find(".//dc:creator", ns)

            if title_element is not None:
                title_element.text = self.title_line_edit.text()
            if author_element is not None:
                author_element.text = self.author_line_edit.text()
            metadata = root.find(".//opf:metadata", ns)
            if metadata is not None:
                genre_element = metadata.find(".//dc:subject", ns)
                if genre_element is None:
                    genre_element = ET.Element("{http://purl.org/dc/elements/1.1/}subject")
                    metadata.append(genre_element)
                genre_element.text = self.genre_line_edit.text()

            tree.write(opf_path, encoding="utf-8", xml_declaration=True)

            if cover_path and self.cover_data:
                if os.path.exists(cover_path):
                    with open(cover_path, "wb") as image:
                        image.write(self.cover_data)
                else:
                    execute_message_box("Ошибка!", "Файл обложки не найден!")

        with zipfile.ZipFile(new_epub_path, "w", compression=zipfile.ZIP_DEFLATED) as new_epub:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, temp_dir)
                    new_epub.write(file_path, archive_name)

        shutil.rmtree(temp_dir)
        os.replace(new_epub_path, path)

    def parse_fb2(self, path):
        tree = ET.parse(path)
        root = tree.getroot()
        ns = {"fb2": "http://www.gribuser.ru/xml/fictionbook/2.0"}

        author_element = root.find(".//fb2:author", ns)
        if author_element is not None:
            first_name = author_element.find("./fb2:first-name", ns)
            last_name = author_element.find("./fb2:last-name", ns)

            full_name = self.author_line_edit.text()
            if first_name is not None:
                first_name.text = full_name
            if last_name is not None:
                last_name.clear()

        title = root.find(".//fb2:book-title", ns)
        if title is not None:
            title.text = self.title_line_edit.text()

        description = root.find(".//fb2:description", ns)
        if description is not None:
            genre_element = description.find(".//fb2:genre", ns)
            if genre_element is None:
                genre_element = ET.Element("{http://www.gribuser.ru/xml/fictionbook/2.0}genre")
                description.insert(0, genre_element)
            genre_element.text = self.genre_line_edit.text()

        cover_page = root.find(".//fb2:coverpage/fb2:image", namespaces=ns)
        if cover_page is not None and self.cover_data is not None:
            cover_id = cover_page.attrib["{http://www.w3.org/1999/xlink}href"].lstrip('#')
            binary_element = root.find(f".//fb2:binary[@id='{cover_id}']", namespaces=ns)
            binary_element.text = base64.b64encode(self.cover_data).decode("utf-8")

        tree.write(path, encoding="utf-8", xml_declaration=True)


class RedactionBookBox(QWidget):

    def __init__(self, app, book, parent):
        super().__init__()
        self.book = book
        self.app = app
        self.box_min_size = (200, 250)
        self.max_width = 300
        self.parent = parent
        self.init_ui()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            dst = os.path.abspath("storage")
            file, _ = QFileDialog.getOpenFileNames(
                self,
                "Выберите новую обложку",
                dst,
                "Covers (*.jpg *.jpeg *png)"
            )

            if file:
                cover_path = os.path.abspath(file[0])
                if os.path.exists(cover_path):
                    with open(cover_path, "rb") as img:
                        cover_data = img.read()
                    self.book.cover = cover_data
                    self.book.flag = True
                    self.parent.cover_data = cover_data
                    self.update_cover()

    def update_cover(self):
        """Обновляем виджет обложки"""
        cover_label = self.findChild(QLabel)

        if self.book.flag:
            pixmap = QPixmap()
            pixmap.loadFromData(self.book.cover)
            cover_label.setPixmap(pixmap)
            cover_label.setScaledContents(True)
        else:
            pixmap = QPixmap(self.book.cover).scaled(self.box_min_size[0], self.box_min_size[1] - 80,
                                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cover_label.setPixmap(pixmap)
        cover_label.setAlignment(Qt.AlignCenter)

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRect(5, 5, self.width() - 10, self.height() - 10)
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(rect)

    def __str__(self):
        return self.cover_data
