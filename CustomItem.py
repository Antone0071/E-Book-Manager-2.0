from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QAction


class CustomItem(QTreeWidgetItem):

    def __init__(self, name):
        super().__init__(name)

    def contextMenuEvent(self, event):
        # Создание контекстного меню
        menu = QMenu(self)
        
        menu.setStyleSheet("""
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

        # Добавление действий в меню
        rename_action = menu.addAction("Переименовать коллекцию")
        delete_action = menu.addAction("Удалить коллекцию")

        # Обработка выбранного действия
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == rename_action:
            self.rename_action_activation()
        elif action == delete_action:
            self.delete_action_activation()

    def rename_action_activation(self):
        pass

    def delete_action_activation(self):
        pass