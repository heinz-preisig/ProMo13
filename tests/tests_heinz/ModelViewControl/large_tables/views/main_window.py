"""
https://www.pythonguis.com/tutorials/qtableview-modelviews-numpy-pandas/
"""
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTableView


class MainWindow(QMainWindow):
  """Main application window with a stacked widget for list and table views."""

  # LIST_MODE = 0
  # TABLE_MODE = 1

  def __init__(self):
    """Initialize the main window and load the UI."""
    super().__init__()

    # Load the UI file
    ui_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'main_window.ui'
            )
    uic.loadUi(ui_file, self)

    # Store references to widgets for easier access
    self._find_widgets()
    pass
    # Set initial mode

  def _find_widgets(self):
    """Find and store references to all UI widgets."""
    self.tableView = self.findChild(QTableView, 'tableView')
    # Top bar widgets
    # self.modeLabel = self.findChild(QLabel, 'modeLabel')
    # self.switchButton = self.findChild(QPushButton, 'switchButton')
    # self.deleteButton = self.findChild(QPushButton, 'deleteButton')
    #
    # # Stacked widget
    # self.stackedWidget = self.findChild(QStackedWidget, 'stackedWidget')
    #
    # # List view page widgets
    # self.listView = self.findChild(QListView, 'listView')
    # self.listInput = self.findChild(QLineEdit, 'listInput')
    # self.listAddButton = self.findChild(QPushButton, 'listAddButton')
    #
    # # Table view page widgets
    # self.tableView = self.findChild(QTableView, 'tableView')
    # self.tableNameInput = self.findChild(QLineEdit, 'tableNameInput')
    # self.tableValueInput = self.findChild(QLineEdit, 'tableValueInput')
    # self.tableAddButton = self.findChild(QPushButton, 'tableAddButton')

  # @property
  # def mode(self) -> int:
  #     """Get the current view mode (LIST_MODE or TABLE_MODE)."""
  #     return self._mode
  #
  # @mode.setter
  # def mode(self, value: int) -> None:
  #     """Set the current view mode and update the UI accordingly."""
  #     if value != self._mode:
  #         self._mode = value
  #         self._apply_mode()
  #
  # def _apply_mode(self) -> None:
  #     """Update the UI to reflect the current mode."""
  #     if self._mode == self.LIST_MODE:
  #         self.stackedWidget.setCurrentIndex(self.LIST_MODE)
  #         self.modeLabel.setText("Mode: List")
  #         self.switchButton.setText("Switch to Table")
  #     else:
  #         self.stackedWidget.setCurrentIndex(self.TABLE_MODE)
  #         self.modeLabel.setText("Mode: Table")
  #         self.switchButton.setText("Switch to List")
