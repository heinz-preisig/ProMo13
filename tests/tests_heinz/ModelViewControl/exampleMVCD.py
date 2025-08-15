import sys
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLineEdit,
    QStyledItemDelegate, QMessageBox
)


# ----------------------------
# Model
# ----------------------------
class ListModel(QAbstractListModel):
    def __init__(self, items=None):
        super().__init__()
        self._items = items or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._items[index.row()]
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._items[index.row()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def add_item(self, item):
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(item)
        self.endInsertRows()

    def remove_item(self, row):
        if 0 <= row < len(self._items):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._items[row]
            self.endRemoveRows()


# ----------------------------
# Delegate
# ----------------------------
class ColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        if index.row() % 2 == 0:
            painter.fillRect(option.rect, QColor("#f0f0ff"))
        else:
            painter.fillRect(option.rect, QColor("#fff0f0"))

        text = index.data(Qt.DisplayRole)
        painter.drawText(option.rect.adjusted(5, 0, -5, 0), Qt.AlignVCenter | Qt.AlignLeft, text)
        painter.restore()

    def createEditor(self, parent, option, index):
        return QLineEdit(parent)

    def setEditorData(self, editor, index):
        editor.setText(index.data(Qt.DisplayRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), Qt.EditRole)


# ----------------------------
# View + Controller in One
# ----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 MVC + Delegate Example")

        # Model & View
        self.model = ListModel(["Item A", "Item B", "Item C"])
        self.list_view = QListView()
        self.list_view.setModel(self.model)

        # Delegate
        self.delegate = ColorDelegate()
        self.list_view.setItemDelegate(self.delegate)

        # Controls
        self.input_field = QLineEdit()
        self.add_button = QPushButton("Add")
        self.delete_button = QPushButton("Delete Selected")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.list_view)
        layout.addWidget(self.input_field)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connections
        self.add_button.clicked.connect(self.add_item)
        self.delete_button.clicked.connect(self.delete_item)

    def add_item(self):
        text = self.input_field.text().strip()
        if text:
            self.model.add_item(text)
            self.input_field.clear()
        else:
            QMessageBox.warning(self, "Warning", "Cannot add empty item.")

    def delete_item(self):
        selected = self.list_view.selectedIndexes()
        if selected:
            row = selected[0].row()
            self.model.remove_item(row)
        else:
            QMessageBox.warning(self, "Warning", "No item selected.")


# ----------------------------
# App Entry
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
