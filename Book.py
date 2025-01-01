import os
import zipfile
import xml.etree.ElementTree as ET
import shutil
import base64


class Book:
    def __init__(self, file_path):

        self.file_path = file_path
        self.author = "Неизвестно"
        self.title = "Неизвестно"
        self.cover = "default-book-cover.png"
        self.flag = False
        self.parse_file(file_path)

    def __str__(self):
        return f"Book: {self.title}, Author: {self.author}"

    def parse_epub(self, file_path):
        with zipfile.ZipFile(file_path, 'r') as epub:
            # Находим файл с метаданными (обычно content.opf в директории OEBPS)
            for file in epub.namelist():
                if file.endswith('content.opf'):
                    with epub.open(file) as content_file:
                        tree = ET.parse(content_file)
                        root = tree.getroot()
                        # Извлекаем метаданные (в пространстве имен: xmlns:dc)
                        ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
                        author = root.find('.//dc:creator', ns).text
                        title = root.find('.//dc:title', ns).text
                        self.author = author
                        self.title = title
                if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    self.flag = True
                    self.cover = epub.read(file)

    def parse_fb2(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        # fb2 обычно использует пространство имен для метаданных
        ns = {'fb2': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
        author_element = root.find('.//fb2:author', ns)
        author = " ".join([name_part.text for name_part in author_element.findall('./fb2:first-name', ns)] +
                          [name_part.text for name_part in author_element.findall('./fb2:last-name', ns)])
        title = root.find('.//fb2:book-title', ns).text
        cover_page = root.find(".//fb2:coverpage/fb2:image", namespaces=ns)
        if not cover_page:
            cover_id = cover_page.attrib['{http://www.w3.org/1999/xlink}href'].lstrip('#')
            binary_element = root.find(f".//fb2:binary[@id='{cover_id}']", namespaces=ns)
            cover_data = base64.b64decode(binary_element.text)
            self.flag = True
            self.cover = cover_data
        self.author = author
        self.title = title

    def parse_file(self, file_path):
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == '.epub':
            self.parse_epub(file_path)
        elif extension == '.fb2':
            self.parse_fb2(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
