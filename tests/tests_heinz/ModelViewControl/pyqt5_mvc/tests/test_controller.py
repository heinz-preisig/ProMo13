import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QApplication, QMessageBox

# Set up the application before importing models and controller
app = QApplication([])

from ..models import TableModel, ListModel
from ..views import MainWindow
from ..delegates import SoftHighlightDelegate
from ..controllers import AppController


class TestController(unittest.TestCase):
    """Test cases for the AppController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create models with sample data
        self.table_model = TableModel([["A", "1"], ["B", "2"]])
        self.list_model = ListModel(self.table_model)
        
        # Create a mock view
        self.view = MainWindow()
        
        # Create a real delegate
        self.delegate = SoftHighlightDelegate()
        
        # Create the controller
        self.controller = AppController(
            self.list_model, self.table_model, self.view, self.delegate
        )
        
        # Patch QMessageBox to prevent actual dialogs from showing during tests
        self.msgbox_patcher = patch('PyQt5.QtWidgets.QMessageBox')
        self.mock_msgbox = self.msgbox_patcher.start()
        self.mock_msgbox.return_value = MagicMock()
        self.mock_msgbox.information.return_value = QMessageBox.Ok
        self.mock_msgbox.warning.return_value = QMessageBox.Ok
    
    def tearDown(self):
        """Clean up after each test."""
        self.msgbox_patcher.stop()
    
    def test_initial_mode(self):
        """Test that the controller starts in list mode."""
        self.assertEqual(self.controller.mode, MainWindow.LIST_MODE)
        self.assertEqual(self.view.stackedWidget.currentIndex(), MainWindow.LIST_MODE)
    
    def test_toggle_mode(self):
        """Test toggling between list and table modes."""
        # Initial state
        self.assertEqual(self.controller.mode, MainWindow.LIST_MODE)
        
        # Toggle to table mode
        self.controller.toggle_mode()
        self.assertEqual(self.controller.mode, MainWindow.TABLE_MODE)
        self.assertEqual(self.view.stackedWidget.currentIndex(), MainWindow.TABLE_MODE)
        
        # Toggle back to list mode
        self.controller.toggle_mode()
        self.assertEqual(self.controller.mode, MainWindow.LIST_MODE)
        self.assertEqual(self.view.stackedWidget.currentIndex(), MainWindow.LIST_MODE)
    
    def test_add_list_item(self):
        """Test adding an item through the list interface."""
        # Set up the input text
        self.view.listInput.setText("New Item")
        
        # Call the method directly (we'll test the signal connection separately)
        self.controller.add_list_item()
        
        # Check that the item was added to both models
        self.assertEqual(self.list_model.rowCount(), 3)
        self.assertEqual(self.table_model.rowCount(), 3)
        self.assertEqual(self.list_model.data(self.list_model.index(2)), "New Item")
        self.assertEqual(self.table_model.data(self.table_model.index(2, 0)), "New Item")
        self.assertEqual(self.table_model.data(self.table_model.index(2, 1)), "")
        
        # Check that the input was cleared
        self.assertEqual(self.view.listInput.text(), "")
    
    def test_add_table_row(self):
        """Test adding a row through the table interface."""
        # Set up the input fields
        self.view.tableNameInput.setText("New Name")
        self.view.tableValueInput.setText("New Value")
        
        # Call the method directly
        self.controller.add_table_row()
        
        # Check that the row was added to both models
        self.assertEqual(self.table_model.rowCount(), 3)
        self.assertEqual(self.list_model.rowCount(), 3)
        self.assertEqual(self.table_model.data(self.table_model.index(2, 0)), "New Name")
        self.assertEqual(self.table_model.data(self.table_model.index(2, 1)), "New Value")
        self.assertEqual(self.list_model.data(self.list_model.index(2)), "New Name")
        
        # Check that the inputs were cleared
        self.assertEqual(self.view.tableNameInput.text(), "")
        self.assertEqual(self.view.tableValueInput.text(), "")
    
    def test_delete_selected_list_mode(self):
        """Test deleting a selected item in list mode."""
        # Set up a selection in the list view
        self.view.listView.setCurrentIndex(self.list_model.index(0))
        
        # Call the method directly
        self.controller.delete_selected()
        
        # Check that the item was removed from both models
        self.assertEqual(self.list_model.rowCount(), 1)
        self.assertEqual(self.table_model.rowCount(), 1)
        self.assertEqual(self.list_model.data(self.list_model.index(0)), "B")
    
    def test_delete_selected_table_mode(self):
        """Test deleting a selected row in table mode."""
        # Switch to table mode
        self.controller.mode = MainWindow.TABLE_MODE
        
        # Set up a selection in the table view
        self.view.tableView.setCurrentIndex(self.table_model.index(0, 0))
        
        # Call the method directly
        self.controller.delete_selected()
        
        # Check that the row was removed from both models
        self.assertEqual(self.table_model.rowCount(), 1)
        self.assertEqual(self.list_model.rowCount(), 1)
        self.assertEqual(self.table_model.data(self.table_model.index(0, 0)), "B")
