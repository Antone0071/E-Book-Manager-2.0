import os
import shutil
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGridLayout, QScrollArea, QHBoxLayout,
                             QTreeWidget,
                             QTreeWidgetItem, QStackedWidget, QFileDialog, QMessageBox)

from Book import Book
from BookAdderBox import BookAdderBox
from BookBox import BookBox, execute_message_box
from CollectionAdder import CollectionAdder
from SettingsWindow import SettingsWindow


class FullScreenApp(QWidget):

    def list_creation(self, dir_path, flag=True):
        """Создаем список книг или коллекций."""
        listed = []
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        if flag:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if item_path.endswith(".epub") or item_path.endswith(".fb2"):
                    book = Book(item_path)
                    listed.append(book)
        else:
            for item in Path(dir_path).iterdir():
                if item.is_dir():
                    listed.append(item.name)
        return listed

    def __init__(self):
        super().__init__()
        self.collection_adder = None
        self.setWindowTitle("Book Library")
        self.setGeometry(200, 100, 1550, 890)
        self.setWindowIcon(QIcon("icons/default-book-cover.png"))
        self.columns = 6
        self.book_list_cache = []
        self.collection_pages = {}
        self.sidebar = QTreeWidget()
        self.library_layout = QGridLayout()
        self.pages = QStackedWidget()

        self.book_list = self.get_books()
        self.collection_list = self.list_creation("collections", flag=False)

        main_layout = QHBoxLayout(self)
        self.setup_sidebar()

        self.library_page = QWidget()
        self.library_layout = QGridLayout()
        self.library_page.setLayout(self.library_layout)
        self.populate_grid()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.library_page)
        self.pages.addWidget(scroll_area)

        for collection in self.collection_list:
            self.create_collection_page(collection)

        collection_adder_button = QPushButton()
        collection_adder_button.setIcon(QIcon("icons/new-collection-adder.png"))
        collection_adder_button.setText("Создать коллекцию")
        collection_adder_button.clicked.connect(self.collection_adder_activation)

        settings_button = QPushButton()
        settings_button.setIcon(QIcon("icons/settings.png"))
        settings_button.clicked.connect(self.settings_activation)

        restart_button = QPushButton()
        restart_button.setIcon(QIcon("icons/restart.png"))
        restart_button.clicked.connect(self.restart_activation)

        copy_collection_button = QPushButton()
        copy_collection_button.setIcon(QIcon("icons/new-collection-adder.png"))
        copy_collection_button.setText("Копировать коллекцию")
        copy_collection_button.clicked.connect(self.copy_collection_action)

        kill_collection_button = QPushButton()
        kill_collection_button.setIcon(QIcon("icons/minus.png"))
        kill_collection_button.setText("Удалить коллекцию")
        kill_collection_button.clicked.connect(self.kill_collection_action)

        sideboard = QVBoxLayout()
        down_sideboard = QHBoxLayout()
        sideboard.addWidget(self.sidebar)
        sideboard.addWidget(collection_adder_button)
        sideboard.addWidget(copy_collection_button)
        sideboard.addWidget(kill_collection_button)
        down_sideboard.addWidget(settings_button)
        down_sideboard.addWidget(restart_button)
        sideboard.addLayout(down_sideboard)

        main_layout.addLayout(sideboard)
        main_layout.addWidget(self.pages)

    def kill_collection_action(self):
        # Проверяем активную страницу
        current_index = self.pages.currentIndex()
        for collection_name, page_index in self.collection_pages.items():
            if page_index == current_index:
                source_dir = os.path.join("collections", collection_name)
                break
        else:
            execute_message_box("Внимание!", "Активная страница не является коллекцией!")
            return

        try:
            if QMessageBox.question(self, "", f"Вы уверены, что хотите удалить коллекцию '{collection_name}'?", QMessageBox.Yes | QMessageBox.No):
                shutil.rmtree(source_dir)
                self.restart_activation()
                self.pages.setCurrentWidget(self.pages.widget(0))

        except Exception as e:
            execute_message_box("Ошибка!", f"Не удалось удалить коллекцию: {str(e)}")

    def copy_collection_action(self):
        """Обработка нажатия кнопки 'Копировать коллекцию'."""

        # Проверяем активную страницу
        current_index = self.pages.currentIndex()
        for collection_name, page_index in self.collection_pages.items():
            if page_index == current_index:
                source_dir = os.path.join("collections", collection_name)
                break
        else:
            execute_message_box("Внимание!", "Активная страница не является коллекцией!")
            return

        # Открываем диалог выбора папки
        target_dir = QFileDialog.getExistingDirectory(self, "Выберите папку для копирования коллекции")

        if not target_dir:
            return  # Пользователь отменил выбор
        try:
            # Копируем коллекцию
            shutil.copytree(source_dir, os.path.join(target_dir, collection_name))
            execute_message_box("Успех", f"Коллекция '{collection_name}' успешно скопирована")
        except Exception as e:
            execute_message_box("Ошибка!", f"Не удалось скопировать коллекцию: {str(e)}")

    def get_books(self):
        if not self.book_list_cache:
            self.book_list_cache = self.list_creation("storage")
        return self.book_list_cache

    def setup_sidebar(self):
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setFixedWidth(150)
        self.sidebar.itemClicked.connect(self.sidebar_item_clicked)
        self.populate_sidebar()

    def populate_sidebar(self):
        self.sidebar.clear()
        library_item = QTreeWidgetItem(["Библиотека"])
        self.sidebar.addTopLevelItem(library_item)
        genres_item = QTreeWidgetItem(["Жанры"])
        self.sidebar.addTopLevelItem(genres_item)
        collection_group = QTreeWidgetItem(["Коллекции"])
        for collection in self.collection_list:
            collection_item = QTreeWidgetItem([collection])
            collection_group.addChild(collection_item)
        self.sidebar.addTopLevelItem(collection_group)

    def create_collection_page(self, collection_name):
        if collection_name in self.collection_pages:
            return
        collection_page = QWidget()
        collection_layout = QGridLayout()
        collection_page.setLayout(collection_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(collection_page)
        self.pages.addWidget(scroll_area)
        self.collection_pages[collection_name] = self.pages.count() - 1
        self.populate_collection_grid(collection_layout, collection_name)

    def populate_collection_grid(self, layout, collection_name):
        # Удаляем все существующие виджеты из макета
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Добавляем новые книги в коллекцию
        collection_path = os.path.join("collections", collection_name)
        books = self.list_creation(collection_path)
        cols = self.columns
        row = col = 0

        for book in books:
            book_box = BookBox(self, book)
            layout.addWidget(book_box, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def restart_activation(self):
        self.book_list_cache = []
        self.book_list = self.get_books()
        self.collection_list = self.list_creation("collections", flag=False)
        self.clear_library_layout()
        self.populate_grid()
        self.populate_sidebar()

        # Перезапуск всех страниц коллекций
        self.collection_pages.clear()
        for collection in self.collection_list:
            self.create_collection_page(collection)

    def clear_library_layout(self):
        for i in reversed(range(self.library_layout.count())):
            widget = self.library_layout.itemAt(i).widget()
            if widget:
                self.library_layout.removeWidget(widget)
                widget.deleteLater()

    def populate_grid(self):
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

    def sidebar_item_clicked(self, item, column):
        if item.parent() is None:
            if item.text(0) == "Библиотека":
                self.pages.setCurrentWidget(self.pages.widget(0))
        else:
            collection_name = item.text(0)
            if collection_name in self.collection_pages:
                self.pages.setCurrentIndex(self.collection_pages[collection_name])

    def collection_adder_activation(self):
        if self.collection_adder is not None:
            self.collection_adder.close()
            self.collection_adder.deleteLater()
        self.collection_adder = CollectionAdder(self)
        self.collection_adder.show()

    def settings_activation(self):
        self.settingsWindow = SettingsWindow()
        self.settingsWindow.show()
