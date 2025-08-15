import sys
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListView, QPushButton, QLineEdit, QMessageBox


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
# View
# ----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 MVC Example")

        # View elements
        self.list_view = QListView()
        self.input_field = QLineEdit()
        self.add_button = QPushButton("Add")
        self.delete_button = QPushButton("Delete Selected")

        layout = QVBoxLayout()
        layout.addWidget(self.list_view)
        layout.addWidget(self.input_field)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)


# ----------------------------
# Controller
# ----------------------------
class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Set up view connections
        self.view.list_view.setModel(self.model)
        self.view.add_button.clicked.connect(self.add_item)
        self.view.delete_button.clicked.connect(self.delete_item)

    def add_item(self):
        text = self.view.input_field.text().strip()
        if text:
            self.model.add_item(text)
            self.view.input_field.clear()
        else:
            QMessageBox.warning(self.view, "Warning", "Cannot add empty item.")

    def delete_item(self):
        selected = self.view.list_view.selectedIndexes()
        if selected:
            row = selected[0].row()
            self.model.remove_item(row)
        else:
            QMessageBox.warning(self.view, "Warning", "No item selected.")


# ----------------------------
# App entry point
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = ListModel(["Item 1", "Item 2"])
    view = MainWindow()
    controller = Controller(model, view)

    view.show()
    sys.exit(app.exec_())
