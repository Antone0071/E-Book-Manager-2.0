from PyQt5.QtWidgets import QWidget


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 100, 600, 890)