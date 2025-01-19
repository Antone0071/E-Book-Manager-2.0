from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget


class EpubReader(QWidget):

    def __init__(self, title, path):
        super(EpubReader, self).__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("icons/default-book-cover.png"))
        self.setGeometry(400, 100, 600, 800)
        self.path = path



    def init_ui(self):
        pass