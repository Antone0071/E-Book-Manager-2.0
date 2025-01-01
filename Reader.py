
"""Формат data: title, links"""
"""Создание нового окна с текстом из файла"""
from PyQt5.QtWidgets import QWidget


class Reader(QWidget):

    def __init__(self, title, data):
        super.__init__()
        self.setWindowTitle(title)
