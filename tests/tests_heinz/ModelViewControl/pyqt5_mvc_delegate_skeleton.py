#!/usr/bin/env python3
"""
PyQt5 MVC + Delegate Skeleton
- Two models: ListModel and TableModel
- One view that can dynamically switch between a QListView and QTableView
- Separate controller orchestrating all interactions
- Custom delegate that supports selection highlighting with a rounded, subtle gradient
- Headless unit tests that exercise the controller without showing any GUI

USAGE
-----
Run GUI normally:
    python pyqt5_mvc_delegate_skeleton.py

Run tests only (no GUI shown):
    python pyqt5_mvc_delegate_skeleton.py --test

This file keeps tests inline so you can drop it into any environment easily.
"""
import sys
import argparse
from typing import List, Any


import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    QAbstractTableModel,
    QModelIndex,
    QRectF,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QLinearGradient,
    QPainterPath,
)
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListView,
    QTableView,
    QPushButton,
    QLineEdit,
    QLabel,
    QStyledItemDelegate,
    QStyle,
    QStackedLayout,
    QMessageBox,
)


# ----------------------------
# MODELS
# ----------------------------
class ListModel(QAbstractListModel):
    def __init__(self, items: List[str] | None = None):
        super().__init__()
        self._items: List[str] = items or []

    # Required
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:  # type: ignore[override]
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            return self._items[index.row()]
        return None

    # Editing support
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:  # type: ignore[override]
        base = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.isValid():
            base |= Qt.ItemIsEditable
        return base

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:  # type: ignore[override]
        if role == Qt.EditRole and index.isValid():
            self._items[index.row()] = str(value)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    # Convenience API used by controller
    def add_item(self, text: str) -> None:
        insert_row = len(self._items)
        self.beginInsertRows(QModelIndex(), insert_row, insert_row)
        self._items.append(text)
        self.endInsertRows()

    def remove_row(self, row: int) -> None:
        if 0 <= row < len(self._items):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._items[row]
            self.endRemoveRows()


class TableModel(QAbstractTableModel):
    HEADER = ["Name", "Value"]

    def __init__(self, rows: List[list[str]] | None = None):
        super().__init__()
        self._rows: List[list[str]] = rows or []

    # Required
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return 2

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:  # type: ignore[override]
        if not index.isValid():
            return None
        r, c = index.row(), index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            return self._rows[r][c]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # type: ignore[override]
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADER[section]
        return section + 1

    # Editing support
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:  # type: ignore[override]
        base = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.isValid():
            base |= Qt.ItemIsEditable
        return base

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:  # type: ignore[override]
        if role == Qt.EditRole and index.isValid():
            r, c = index.row(), index.column()
            self._rows[r][c] = str(value)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    # Convenience API used by controller
    def add_row(self, name: str, value: str) -> None:
        r = len(self._rows)
        self.beginInsertRows(QModelIndex(), r, r)
        self._rows.append([name, value])
        self.endInsertRows()

    def remove_row(self, row: int) -> None:
        if 0 <= row < len(self._rows):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._rows[row]
            self.endRemoveRows()


# ----------------------------
# DELEGATE (custom paint + editors)
# ----------------------------
class SoftHighlightDelegate(QStyledItemDelegate):
    """A delegate that paints alternating rows but respects selection.
    Selected rows get a rounded rectangle with a gentle gradient.
    """

    def paint(self, painter: QPainter, option, index):  # type: ignore[override]
        painter.save()

        # Compute background
        if option.state & QStyle.State_Selected:
            rect = option.rect.adjusted(2, 2, -2, -2)
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), 6, 6)

            # Subtle gradient based on the palette highlight color
            base = option.palette.highlight().color()
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0.0, base.lighter(115))
            grad.setColorAt(1.0, base)
            painter.fillPath(path, grad)
            painter.setPen(option.palette.highlightedText().color())
        else:
            # Alternating row background
            bg = QColor("#f7f9fc") if index.row() % 2 == 0 else QColor("#ffffff")
            painter.fillRect(option.rect, bg)
            painter.setPen(option.palette.text().color())

        # Draw text with a small left padding
        text = str(index.data(Qt.DisplayRole))
        painter.drawText(option.rect.adjusted(8, 0, -8, 0), Qt.AlignVCenter | Qt.AlignLeft, text)

        painter.restore()

    # default editors from QStyledItemDelegate (QLineEdit for strings) are fine


# ----------------------------
# VIEW (widgets only, no business logic)
# ----------------------------
class MainWindow(QWidget):
    LIST_MODE = 0
    TABLE_MODE = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 MVC + Delegate Skeleton")

        # Top controls
        self.mode_label = QLabel("Mode: List")
        self.switch_btn = QPushButton("Switch to Table")
        self.delete_btn = QPushButton("Delete Selected")

        top = QHBoxLayout()
        top.addWidget(self.mode_label)
        top.addStretch(1)
        top.addWidget(self.switch_btn)
        top.addWidget(self.delete_btn)

        # Stack: List view + input, Table view + inputs
        self.stack = QStackedLayout()

        # List view page
        self.list_view = QListView()
        self.list_input = QLineEdit()
        self.list_input.setPlaceholderText("Add list item…")
        self.list_add_btn = QPushButton("Add Item")
        list_row = QHBoxLayout()
        list_row.addWidget(self.list_input)
        list_row.addWidget(self.list_add_btn)

        list_page = QWidget()
        list_v = QVBoxLayout(list_page)
        list_v.addWidget(self.list_view)
        list_v.addLayout(list_row)

        # Table view page
        self.table_view = QTableView()
        self.table_name_input = QLineEdit(); self.table_name_input.setPlaceholderText("Name…")
        self.table_value_input = QLineEdit(); self.table_value_input.setPlaceholderText("Value…")
        self.table_add_btn = QPushButton("Add Row")
        table_row = QHBoxLayout()
        table_row.addWidget(self.table_name_input)
        table_row.addWidget(self.table_value_input)
        table_row.addWidget(self.table_add_btn)

        table_page = QWidget()
        table_v = QVBoxLayout(table_page)
        table_v.addWidget(self.table_view)
        table_v.addLayout(table_row)

        # Add pages to stack
        self.stack.addWidget(list_page)   # index 0
        self.stack.addWidget(table_page)  # index 1

        # Root layout
        root = QVBoxLayout()
        root.addLayout(top)
        root.addLayout(self.stack)
        self.setLayout(root)


# ----------------------------
# CONTROLLER (wires everything)
# ----------------------------
class AppController:
    def __init__(self, model_list: ListModel, model_table: TableModel, view: MainWindow, delegate: SoftHighlightDelegate):
        self.model_list = model_list
        self.model_table = model_table
        self.view = view
        self.delegate = delegate

        # Hook models & delegate to views
        self.view.list_view.setModel(self.model_list)
        self.view.table_view.setModel(self.model_table)
        self.view.list_view.setItemDelegate(self.delegate)
        self.view.table_view.setItemDelegate(self.delegate)
        self.view.table_view.horizontalHeader().setStretchLastSection(True)

        # Wire controls
        self.view.switch_btn.clicked.connect(self.toggle_mode)
        self.view.delete_btn.clicked.connect(self.delete_selected)
        self.view.list_add_btn.clicked.connect(self.add_list_item)
        self.view.table_add_btn.clicked.connect(self.add_table_row)

        # Start in LIST mode
        self._mode = MainWindow.LIST_MODE
        self._apply_mode()

    # ----- Mode management -----
    def toggle_mode(self):
        self._mode = MainWindow.TABLE_MODE if self._mode == MainWindow.LIST_MODE else MainWindow.LIST_MODE
        self._apply_mode()

    def _apply_mode(self):
        if self._mode == MainWindow.LIST_MODE:
            self.view.stack.setCurrentIndex(MainWindow.LIST_MODE)
            self.view.mode_label.setText("Mode: List")
            self.view.switch_btn.setText("Switch to Table")
        else:
            self.view.stack.setCurrentIndex(MainWindow.TABLE_MODE)
            self.view.mode_label.setText("Mode: Table")
            self.view.switch_btn.setText("Switch to List")

    # ----- Actions (controller logic) -----
    def add_list_item(self):
        text = self.view.list_input.text().strip()
        if not text:
            QMessageBox.warning(self.view, "Warning", "Cannot add empty item.")
            return
        self.model_list.add_item(text)
        self.view.list_input.clear()

    def add_table_row(self):
        name = self.view.table_name_input.text().strip()
        value = self.view.table_value_input.text().strip()
        if not name and not value:
            QMessageBox.warning(self.view, "Warning", "Please enter a Name or Value.")
            return
        self.model_table.add_row(name, value)
        self.view.table_name_input.clear()
        self.view.table_value_input.clear()

    def delete_selected(self):
        if self._mode == MainWindow.LIST_MODE:
            selected = self.view.list_view.selectedIndexes()
            if not selected:
                QMessageBox.information(self.view, "Info", "Select a list item to delete.")
                return
            self.model_list.remove_row(selected[0].row())
        else:
            selected = self.view.table_view.selectedIndexes()
            if not selected:
                QMessageBox.information(self.view, "Info", "Select a table row to delete.")
                return
            # remove the first selected row (collapse multiple selection for simplicity)
            row = selected[0].row()
            self.model_table.remove_row(row)

    # Helpers for tests
    @property
    def mode(self) -> int:
        return self._mode


# ----------------------------
# MAIN
# ----------------------------
def run_gui():
    app = QApplication(sys.argv)

    list_model = ListModel(["Alpha", "Beta", "Gamma"])
    table_model = TableModel([["A", "1"], ["B", "2"], ["C", "3"]])

    view = MainWindow()
    delegate = SoftHighlightDelegate()
    controller = AppController(list_model, table_model, view, delegate)

    view.resize(700, 480)
    view.show()
    sys.exit(app.exec_())


# ----------------------------
# TESTS (headless, no .show())
# ----------------------------
import unittest

class TestController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure a QApplication exists for widgets/models, but don't show windows
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.list_model = ListModel(["One", "Two"])  # start with 2 items
        self.table_model = TableModel([["K", "10"], ["L", "20"]])
        self.view = MainWindow()
        self.delegate = SoftHighlightDelegate()
        self.controller = AppController(self.list_model, self.table_model, self.view, self.delegate)

    def test_initial_mode(self):
        self.assertEqual(self.controller.mode, MainWindow.LIST_MODE)
        self.assertEqual(self.view.stack.currentIndex(), MainWindow.LIST_MODE)

    def test_toggle_mode(self):
        self.controller.toggle_mode()
        self.assertEqual(self.controller.mode, MainWindow.TABLE_MODE)
        self.assertEqual(self.view.stack.currentIndex(), MainWindow.TABLE_MODE)

    def test_add_list_item(self):
        self.view.list_input.setText("Three")
        self.controller.add_list_item()
        self.assertEqual(self.list_model.rowCount(), 3)
        self.assertEqual(self.list_model.data(self.list_model.index(2), Qt.DisplayRole), "Three")

    def test_delete_list_item(self):
        # Select row 0 programmatically
        self.view.list_view.setCurrentIndex(self.list_model.index(0))
        self.controller.delete_selected()
        self.assertEqual(self.list_model.rowCount(), 1)
        self.assertEqual(self.list_model.data(self.list_model.index(0), Qt.DisplayRole), "Two")

    def test_add_table_row(self):
        self.controller.toggle_mode()  # switch to table mode
        self.view.table_name_input.setText("M")
        self.view.table_value_input.setText("30")
        self.controller.add_table_row()
        self.assertEqual(self.table_model.rowCount(), 3)
        idx = self.table_model.index(2, 0)
        self.assertEqual(self.table_model.data(idx, Qt.DisplayRole), "M")

    def test_delete_table_row(self):
        self.controller.toggle_mode()  # table mode
        # Select row 1, any column
        self.view.table_view.setCurrentIndex(self.table_model.index(1, 0))
        self.controller.delete_selected()
        self.assertEqual(self.table_model.rowCount(), 1)
        idx = self.table_model.index(0, 0)
        self.assertEqual(self.table_model.data(idx, Qt.DisplayRole), "K")

    def test_delegate_is_set(self):
        # Verify the same delegate instance is installed on both views
        self.assertIs(self.view.list_view.itemDelegate(), self.delegate)
        self.assertIs(self.view.table_view.itemDelegate(), self.delegate)


def run_tests() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestController)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="run unit tests and exit")
    args = parser.parse_args()

    if args.test:
        sys.exit(run_tests())
    else:
        run_gui()
