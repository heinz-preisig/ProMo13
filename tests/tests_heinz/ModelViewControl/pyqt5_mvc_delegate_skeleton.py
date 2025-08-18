#!/usr/bin/env python3
"""
PyQt5 MVC + Delegate Skeleton with UI File
- Two models: ListModel and TableModel
- One view that can dynamically switch between a QListView and QTableView
- Separate controller orchestrating all interactions
- Custom delegate that supports selection highlighting with a rounded, subtle gradient
- Headless unit tests that exercise the controller without showing any GUI
- UI defined in a separate .ui file for better maintainability

USAGE
-----
Run GUI normally:
    python pyqt5_mvc_delegate_skeleton.py

Run tests only (no GUI shown):
    python pyqt5_mvc_delegate_skeleton.py --test

Run with verbose output:
    python pyqt5_mvc_delegate_skeleton.py --verbose
"""

import os
import sys
import argparse
from typing import List, Any, Optional
from pathlib import Path

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
    QStackedWidget,
    QMessageBox,
    QMainWindow,
)
from PyQt5 import uic


# ----------------------------
# MODELS
# ----------------------------
class ListModel(QAbstractListModel):
    def __init__(self, table_model):
        super().__init__()
        self._table_model = table_model
        # Connect to table model's signals to keep in sync
        self._table_model.rowsAboutToBeRemoved.connect(self._on_table_rows_removed)
        self._table_model.rowsInserted.connect(self._on_table_rows_inserted)
        self._table_model.dataChanged.connect(self._on_table_data_changed)

    def _on_table_rows_removed(self, parent, first, last):
        self.beginRemoveRows(QModelIndex(), first, last)
        self.endRemoveRows()

    def _on_table_rows_inserted(self, parent, first, last):
        self.beginInsertRows(QModelIndex(), first, last)
        self.endInsertRows()

    def _on_table_data_changed(self, top_left, bottom_right, roles):
        # Forward the data changed signal with adjusted indices
        top_left = self.index(top_left.row())
        bottom_right = self.index(bottom_right.row())
        self.dataChanged.emit(top_left, bottom_right, roles)

    # Required
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._table_model.rowCount()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return None
            
        # Get the name from the first column of the table model
        table_index = self._table_model.index(index.row(), 0)
        return self._table_model.data(table_index, role)

    # Editing support
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.EditRole and index.isValid():
            table_index = self._table_model.index(index.row(), 0)
            return self._table_model.setData(table_index, value, role)
        return False

    # Convenience API used by controller
    def add_item(self, text: str) -> None:
        # Add a new row with the text in the first column and empty second column
        self._table_model.add_row(text, "")

    def remove_row(self, row: int) -> None:
        self._table_model.remove_row(row)


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
        insert_row = len(self._rows)
        self.beginInsertRows(QModelIndex(), insert_row, insert_row)
        self._rows.append([str(name), str(value)])
        self.endInsertRows()
        # Emit dataChanged for the new row to ensure views update
        top_left = self.index(insert_row, 0)
        bottom_right = self.index(insert_row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [])

    def remove_row(self, row: int) -> None:
        if 0 <= row < len(self._rows):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._rows.pop(row)
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
class MainWindow(QMainWindow):
    LIST_MODE = 0
    TABLE_MODE = 1
    
    def __init__(self):
        super().__init__()
        
        # Load the UI file
        ui_file = os.path.join(os.path.dirname(__file__), 'ui', 'main_window.ui')
        uic.loadUi(ui_file, self)
        
        # Store references to widgets for easier access
        self.modeLabel = self.findChild(QLabel, 'modeLabel')
        self.switchButton = self.findChild(QPushButton, 'switchButton')
        self.deleteButton = self.findChild(QPushButton, 'deleteButton')
        self.stackedWidget = self.findChild(QStackedWidget, 'stackedWidget')
        
        # List view page widgets
        self.listView = self.findChild(QListView, 'listView')
        self.listInput = self.findChild(QLineEdit, 'listInput')
        self.listAddButton = self.findChild(QPushButton, 'listAddButton')
        
        # Table view page widgets
        self.tableView = self.findChild(QTableView, 'tableView')
        self.tableNameInput = self.findChild(QLineEdit, 'tableNameInput')
        self.tableValueInput = self.findChild(QLineEdit, 'tableValueInput')
        self.tableAddButton = self.findChild(QPushButton, 'tableAddButton')
        
        # Set initial mode
        self._mode = self.LIST_MODE
        
    @property
    def mode(self):
        return self._mode
        
    @mode.setter
    def mode(self, value):
        self._mode = value
        self._apply_mode()
        
    def _apply_mode(self):
        if self._mode == self.LIST_MODE:
            self.modeLabel.setText("Mode: List")
            self.switchButton.setText("Switch to Table")
            self.stackedWidget.setCurrentIndex(0)
        else:
            self.modeLabel.setText("Mode: Table")
            self.switchButton.setText("Switch to List")
            self.stackedWidget.setCurrentIndex(1)


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
        self.view.listView.setModel(self.model_list)
        self.view.tableView.setModel(self.model_table)
        self.view.listView.setItemDelegate(self.delegate)
        self.view.tableView.setItemDelegate(self.delegate)
        self.view.tableView.horizontalHeader().setStretchLastSection(True)

        # Wire controls
        self.view.switchButton.clicked.connect(self.toggle_mode)
        self.view.deleteButton.clicked.connect(self.delete_selected)
        self.view.listAddButton.clicked.connect(self.add_list_item)
        self.view.tableAddButton.clicked.connect(self.add_table_row)

        # Start in LIST mode
        self._mode = MainWindow.LIST_MODE
        self._apply_mode()

    # ----- Mode management -----
    def toggle_mode(self):
        self._mode = MainWindow.TABLE_MODE if self._mode == MainWindow.LIST_MODE else MainWindow.LIST_MODE
        self._apply_mode()

    def _apply_mode(self):
        if self._mode == MainWindow.LIST_MODE:
            self.view.stackedWidget.setCurrentIndex(MainWindow.LIST_MODE)
            self.view.modeLabel.setText("Mode: List")
            self.view.switchButton.setText("Switch to Table")
        else:
            self.view.stackedWidget.setCurrentIndex(MainWindow.TABLE_MODE)
            self.view.modeLabel.setText("Mode: Table")
            self.view.switchButton.setText("Switch to List")

    # ----- Actions (controller logic) -----
    def add_list_item(self):
        text = self.view.listInput.text().strip()
        if not text:
            QMessageBox.warning(self.view, "Warning", "Item text cannot be empty.")
            return
        # Add to the table model with an empty value
        # The list model will update automatically via signals
        self.model_table.add_row(text, "")
        self.view.listInput.clear()

    def add_table_row(self):
        name = self.view.tableNameInput.text().strip()
        value = self.view.tableValueInput.text().strip()
        if not name:
            QMessageBox.warning(self.view, "Warning", "Name cannot be empty.")
            return
        # Add to the table model
        # The list model will update automatically via signals
        self.model_table.add_row(name, value)
        self.view.tableNameInput.clear()
        self.view.tableValueInput.clear()

    def delete_selected(self):
        if self._mode == MainWindow.LIST_MODE:
            selected = self.view.listView.selectedIndexes()
            if not selected:
                QMessageBox.information(self.view, "Info", "Select a list item to delete.")
                return
            # Remove the selected row from the table model
            # (the list model will update automatically via signals)
            self.model_table.remove_row(selected[0].row())
        else:
            selected = self.view.tableView.selectedIndexes()
            if not selected:
                QMessageBox.information(self.view, "Info", "Select a table row to delete.")
                return
            # Remove the selected row from the table model
            # (the list model will update automatically via signals)
            self.model_table.remove_row(selected[0].row())

    # Helpers for tests
    @property
    def mode(self) -> int:
        return self._mode


# ----------------------------
# MAIN
# ----------------------------
def run_gui():
    app = QApplication(sys.argv)
    
    # Set application style for better look
    app.setStyle('Fusion')
    
    # Create the table model with sample data
    table_model = TableModel([["Alpha", ""], ["Beta", ""], ["Gamma", ""]])
    
    # Create the list model that wraps the table model
    list_model = ListModel(table_model)
    
    # Create and show the main window
    view = MainWindow()
    
    # Create delegate for custom item rendering
    delegate = SoftHighlightDelegate()
    
    # Create controller to manage the application logic
    controller = AppController(list_model, table_model, view, delegate)
    
    # Set initial window size and show
    view.setWindowTitle("PyQt5 MVC + Delegate Example")
    view.resize(700, 500)
    view.show()
    
    # Start the event loop
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
        self.assertEqual(self.view.stackedWidget.currentIndex(), MainWindow.LIST_MODE)

    def test_toggle_mode(self):
        self.controller.toggle_mode()
        self.assertEqual(self.controller.mode, MainWindow.TABLE_MODE)
        self.assertEqual(self.view.stackedWidget.currentIndex(), MainWindow.TABLE_MODE)

    def test_add_list_item(self):
        self.view.listInput.setText("Three")
        self.controller.add_list_item()
        self.assertEqual(self.list_model.rowCount(), 3)
        self.assertEqual(self.list_model.data(self.list_model.index(2), Qt.DisplayRole), "Three")

    def test_delete_list_item(self):
        # Select row 0 programmatically
        self.view.listView.setCurrentIndex(self.list_model.index(0))
        self.controller.delete_selected()
        self.assertEqual(self.list_model.rowCount(), 1)
        self.assertEqual(self.list_model.data(self.list_model.index(0), Qt.DisplayRole), "Two")

    def test_add_table_row(self):
        self.controller.toggle_mode()  # switch to table mode
        self.view.tableNameInput.setText("M")
        self.view.tableValueInput.setText("30")
        self.controller.add_table_row()
        self.assertEqual(self.table_model.rowCount(), 3)
        idx = self.table_model.index(2, 0)
        self.assertEqual(self.table_model.data(idx, Qt.DisplayRole), "M")

    def test_delete_table_row(self):
        self.controller.toggle_mode()  # table mode
        # Select row 1, any column
        self.view.tableView.setCurrentIndex(self.table_model.index(1, 0))
        self.controller.delete_selected()
        self.assertEqual(self.table_model.rowCount(), 1)
        idx = self.table_model.index(0, 0)
        self.assertEqual(self.table_model.data(idx, Qt.DisplayRole), "K")

    def test_delegate_is_set(self):
        # Verify the same delegate instance is installed on both views
        self.assertIs(self.view.listView.itemDelegate(), self.delegate)
        self.assertIs(self.view.tableView.itemDelegate(), self.delegate)


def run_tests() -> int:
    # Suppress Qt debug output during tests
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false"
    
    # Initialize QApplication for tests if not already done
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Run the tests
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestController)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Clean up QApplication
    if QApplication.instance():
        QApplication.quit()
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PyQt5 MVC + Delegate Example")
    parser.add_argument("--test", action="store_true", help="run unit tests and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="enable verbose output")
    args = parser.parse_args()

    if args.test:
        sys.exit(run_tests())
    else:
        # Run the GUI application
        if not args.verbose:
            # Suppress Qt debug output in production
            os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false"
        run_gui()
