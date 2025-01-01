import sys
from PyQt5.QtWidgets import QApplication
from FullscreenApp import FullScreenApp
import qdarktheme


def display_tab(self, index):
    self.pages.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = FullScreenApp()
    #qdarktheme.setup_theme()
    main_window.show()
    sys.exit(app.exec_())