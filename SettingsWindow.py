from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 100, 600, 890)
        self.setWindowIcon(QIcon("icons/default-book-cover.png"))
        self.setWindowTitle("Настройки")

        main_layout = QVBoxLayout(self)