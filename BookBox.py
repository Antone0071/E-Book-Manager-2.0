import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPen, QFontMetrics
from PyQt5.QtCore import Qt, QRect

from BookRedactionWidget import BookRedactionWidget


class BookBox(QWidget):
    def __init__(self, app, book):
        super().__init__()
        self.bookRedactionWidget = None
        self.book = book
        self.app = app
        self.box_min_size = (200, 250)
        self.max_width = 300
        self.init_ui()
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

        self.addInCollectionAction = QtWidgets.QAction("Добавить в...", self)
        self.contextMenu.addAction(self.addInCollectionAction)

        self.redactAction = QtWidgets.QAction("Редактировать информацию", self)
        self.contextMenu.addAction(self.redactAction)

        self.deleteAction = QtWidgets.QAction("Удалить книгу", self)
        self.contextMenu.addAction(self.deleteAction)

        self.redactAction.triggered.connect(self.redact_action_activation)
        self.deleteAction.triggered.connect(self.delete_action_activation)
        self.openAction.triggered.connect(self.open_action_activation)

    def open_action_activation(self):
        pass

    def redact_action_activation(self):
        if self.bookRedactionWidget is not None:
            self.bookRedactionWidget.close()
            self.bookRedactionWidget.deleteLater()
        self.bookRedactionWidget = BookRedactionWidget(self.book, self.app)
        self.bookRedactionWidget.show()

    def delete_action_activation(self):
        self.asking = QMessageBox()
        self.asking.setText(f"Вы уверены, что хотите удалить '{self.book.title}'?")
        self.asking.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.asking.setDefaultButton(QMessageBox.No)
        self.asking.setWindowTitle("Судьба книги")

        result = self.asking.exec_()

        if result == QMessageBox.Yes:
            os.remove(self.book.file_path)
            self.app.restart_activation()

    def contextMenuEvent(self, event):
        self.contextMenu.exec_(event.globalPos())

    def init_ui(self):
        self.setFixedSize(*self.box_min_size)
        self.setStyleSheet("background: transparent;")

        # Create layout for BookBox
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        cover_label = QLabel(self)
        if self.book.flag:
            pixmap = QPixmap()
            pixmap.loadFromData(self.book.cover)
            cover_label.setScaledContents(True)
        else:
            pixmap = QPixmap(self.book.cover).scaled(self.box_min_size[0] - 20, self.box_min_size[1] - 80,
                                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)

        cover_label.setPixmap(pixmap)
        cover_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(cover_label)

        # Add title label
        title_label = QLabel(self.book.title, self)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setStyleSheet("color: black; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Add author label
        author_label = QLabel(self.book.author, self)
        author_label.setFont(QFont("Arial", 9))
        author_label.setStyleSheet("color: black; background: transparent;")
        author_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_label)

        self.adjust_box_size(title_label, author_label)

    def adjust_box_size(self, title_label, author_label):
        # Получаем размеры текста title и author
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
            print(f"Title: {self.book.title}")
        #elif e.button() == Qt.RightButton:


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRect(5, 5, self.width() - 10, self.height() - 10)
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, 15, 15)