import sys
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListView,
    QPushButton, QLineEdit, QStyledItemDelegate, QMessageBox
)
"""
Why this is real MVC:

Model = data storage + logic

View = only widgets, no data manipulation

Controller = the glue — handles events, updates the model, tells the view what to display

Delegate = mini-controller for each cell’s drawing/editing

Qt’s own docs treat the delegate as part of the “view” layer, but in practice it’s a cell-level controller."""

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
from PyQt5.QtWidgets import QStyle

"""
Check if the item is selected:
if option.state & QStyle.State_Selected:
If yes → Fill with option.palette.highlight() and set text color to highlightedText()

If no → Use alternating colors

Then draw the text with painter.setPen() so it has the right color in both cases
"""

class ColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()

        if option.state & QStyle.State_Selected:
            # Draw selection background
            painter.fillRect(option.rect, option.palette.highlight())
            text_color = option.palette.highlightedText().color()
        else:
            # Alternating background
            if index.row() % 2 == 0:
                painter.fillRect(option.rect, QColor("#f0f0ff"))
            else:
                painter.fillRect(option.rect, QColor("#fff0f0"))
            text_color = option.palette.text().color()

        # Draw the text
        painter.setPen(text_color)
        text = index.data(Qt.DisplayRole)
        painter.drawText(option.rect.adjusted(5, 0, -5, 0),
                         Qt.AlignVCenter | Qt.AlignLeft, text)

        painter.restore()


# ----------------------------
# View
# ----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 MVC + Delegate (Strict)")

        self.list_view = QListView()
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


# ----------------------------
# Controller
# ----------------------------
class Controller:
    def __init__(self, model, view, delegate):
        self.model = model
        self.view = view
        self.delegate = delegate

        # Connect model to view
        self.view.list_view.setModel(self.model)
        self.view.list_view.setItemDelegate(self.delegate)

        # Connect view signals to controller slots
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
# Entry Point
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = ListModel(["Item A", "Item B", "Item C"])
    view = MainWindow()
    delegate = ColorDelegate()
    controller = Controller(model, view, delegate)

    view.show()
    sys.exit(app.exec_())
