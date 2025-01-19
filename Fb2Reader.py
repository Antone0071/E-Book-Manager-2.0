import os
import shutil
import base64
from io import BytesIO
from chardet import UniversalDetector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PIL import Image

class Fb2Reader(QWidget):

    def __init__(self, title, path):
        super(Fb2Reader, self).__init__()
        self.title = title
        self.path = path
        self.temp_dir = None
        self.body = None
        self.cover_image_path = None
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("icons/default-book-cover.png"))
        self.setGeometry(400, 100, 600, 800)

        try:
            self.create_temp_dir()
            self.process_file()
            self.init_ui()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{str(e)}")

    def create_temp_dir(self):
        self.temp_dir = self.title
        os.makedirs(self.temp_dir, exist_ok=True)

    def detect_charset(self, file_path):
        detector = UniversalDetector()
        with open(file_path, 'rb') as fh:
            for line in fh:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
        result = detector.result
        if not result or 'encoding' not in result or not result['encoding']:
            result['encoding'] = 'utf-8'
        return result['encoding']

    def process_file(self):
        temp_file_path = os.path.join(self.temp_dir, "temp.txt")
        shutil.copy(self.path, temp_file_path)

        charset = self.detect_charset(temp_file_path)
        if charset != 'utf-8':
            with open(temp_file_path, 'r', encoding=charset) as file:
                content = file.read()
            with open(temp_file_path, 'w', encoding='utf-8') as file:
                file.write(content)

        with open(temp_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        self.extract_body(content)
        self.extract_images(content)

    def extract_body(self, content):
        try:
            start = content.index("<body>")
            end = content.rindex("</body>") + 7
            self.body = content[start:end]
        except ValueError:
            self.body = "<p>Body content not found</p>"

    def extract_images(self, content):
        start_bin = content.find("<binary")
        end_bin = content.rfind("</binary>")

        if start_bin != -1 and end_bin != -1 and start_bin < end_bin:
            end_bin += 9
            bin_content = content[start_bin:end_bin]
            while True:
                next_bin = bin_content.find("<binary")
                last_bin = bin_content.find("</binary>")

                if next_bin == -1 or last_bin == -1:
                    break

                last_bin += 9
                binary_el = bin_content[next_bin:last_bin]
                bin_content = bin_content.replace(binary_el, "")
                binary_el = binary_el.replace("</binary>", "")
                find_string = binary_el.index(">")
                tag = binary_el[:find_string + 1]
                binary_el = binary_el.replace(tag, "")

                image_name = tag.split("id=")[1].split("\"")[1]
                decoded_bytes = base64.b64decode(binary_el)

                try:
                    img = Image.open(BytesIO(decoded_bytes))
                    output_path = os.path.join(self.temp_dir, image_name)
                    img.save(output_path)

                    if not self.cover_image_path:  # Use the first image as the cover
                        self.cover_image_path = output_path
                except IOError:
                    continue

    def init_ui(self):
        layout = QVBoxLayout()
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        if self.cover_image_path:
            cover_label = QLabel(self)
            pixmap = QPixmap(self.cover_image_path).scaled(self.width(), self.height() // 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cover_label.setPixmap(pixmap)
            cover_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(cover_label)

        body_label = QLabel(self)
        body_label.setTextFormat(Qt.RichText)
        body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        body_label.setText(self.body)
        content_layout.addWidget(body_label)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def closeEvent(self, event):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        super(Fb2Reader, self).closeEvent(event)