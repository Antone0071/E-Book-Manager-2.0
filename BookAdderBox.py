import os
import shutil
from pathlib import Path

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPainter, QPen, QFontMetrics, QFont, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFileDialog


class BookAdderBox(QWidget):
    def __init__(self, app):
        super().__init__()
        self.box_min_size = (200, 250)
        self.app = app
        self.max_width = 300
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(*self.box_min_size)
        self.setStyleSheet("background: transparent;")

        # Create layout for BookBox
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        cover_label = QLabel(self)

        pixmap = QPixmap("icons/default-book-cover.png").scaled(self.box_min_size[0] - 20, self.box_min_size[1] - 80,
                                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)

        cover_label.setPixmap(pixmap)
        cover_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(cover_label)

        # Add title label
        title_label = QLabel("Добавить ещё книг", self)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setStyleSheet("color: black; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.adjust_box_size(title_label)

    def adjust_box_size(self, title_label):
        # Получаем размеры текста title и author
        title_metrics = QFontMetrics(title_label.font())

        title_width = title_metrics.boundingRect(title_label.text()).width()

        required_width = max(self.box_min_size[0], title_width + 20)
        required_width = min(required_width, self.max_width)
        required_height = int(self.box_min_size[1] * 1.3)
        self.setFixedSize(required_width, required_height)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            dst = os.path.abspath("storage")
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Выберите книги",
                dst,
                "Books (*.fb2 *.epub)"
            )
            if files:
                for file in files:
                    file_name = file.split("/")[-1]
                    if not dst.find(file_name):
                        src = os.path.abspath(file)
                        shutil.move(src, dst)
                self.app.restart_activation()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRect(5, 5, self.width() - 10, self.height() - 10)
        pen = QPen(Qt.blue)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, 15, 15)