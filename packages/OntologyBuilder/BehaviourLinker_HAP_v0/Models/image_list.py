from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel


class ImageListModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def load_data(self, data, pending=None):
        self.clear()

        for element in data:
            item = QStandardItem(element.get_id())
            item.setData(element.get_img_path(), Qt.UserRole)

            if pending is None:
                self.appendRow(item)
                continue

            if element in pending:
                item.setData(False, Qt.UserRole + 1)
            else:
                item.setData(True, Qt.UserRole + 1)

            self.appendRow(item)
