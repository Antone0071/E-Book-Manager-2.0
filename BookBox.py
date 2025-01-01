from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPen, QFontMetrics
from PyQt5.QtCore import Qt, QSize, QRect


class BookBox(QWidget):
    def __init__(self, book, box_min_size=(200, 250), max_width=300):
        super().__init__()
        self.book = book
        self.box_min_size = box_min_size
        self.max_width = max_width
        self.init_ui()

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRect(5, 5, self.width() - 10, self.height() - 10)
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, 15, 15)