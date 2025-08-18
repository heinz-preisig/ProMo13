import unittest
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import QApplication

# Import models first to avoid circular imports
from ..models import TableModel, ListModel

# Create QApplication instance if it doesn't exist
app = QApplication.instance() or QApplication([])


class TestModels(unittest.TestCase):
    """Test cases for the data models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.table_model = TableModel([["A", "1"], ["B", "2"]])
        self.list_model = ListModel(self.table_model)
    
    def test_table_model_initialization(self):
        """Test that the table model initializes with the correct data."""
        self.assertEqual(self.table_model.rowCount(), 2)
        self.assertEqual(self.table_model.columnCount(), 2)
        self.assertEqual(self.table_model.data(self.table_model.index(0, 0)), "A")
        self.assertEqual(self.table_model.data(self.table_model.index(0, 1)), "1")
    
    def test_table_model_add_row(self):
        """Test adding a row to the table model."""
        self.table_model.add_row("C", "3")
        self.assertEqual(self.table_model.rowCount(), 3)
        self.assertEqual(self.table_model.data(self.table_model.index(2, 0)), "C")
        self.assertEqual(self.table_model.data(self.table_model.index(2, 1)), "3")
    
    def test_table_model_remove_row(self):
        """Test removing a row from the table model."""
        self.table_model.remove_row(0)
        self.assertEqual(self.table_model.rowCount(), 1)
        self.assertEqual(self.table_model.data(self.table_model.index(0, 0)), "B")
    
    def test_list_model_initialization(self):
        """Test that the list model initializes with data from the table model."""
        self.assertEqual(self.list_model.rowCount(), 2)
        self.assertEqual(self.list_model.data(self.list_model.index(0)), "A")
        self.assertEqual(self.list_model.data(self.list_model.index(1)), "B")
    
    def test_list_model_add_item(self):
        """Test adding an item to the list model."""
        self.list_model.add_item("C")
        self.assertEqual(self.list_model.rowCount(), 3)
        self.assertEqual(self.list_model.data(self.list_model.index(2)), "C")
        # Verify the table model was also updated
        self.assertEqual(self.table_model.rowCount(), 3)
        self.assertEqual(self.table_model.data(self.table_model.index(2, 0)), "C")
    
    def test_list_model_remove_row(self):
        """Test removing a row from the list model."""
        self.list_model.remove_row(0)
        self.assertEqual(self.list_model.rowCount(), 1)
        self.assertEqual(self.list_model.data(self.list_model.index(0)), "B")
        # Verify the table model was also updated
        self.assertEqual(self.table_model.rowCount(), 1)
        self.assertEqual(self.table_model.data(self.table_model.index(0, 0)), "B")
    
    def test_sync_between_models(self):
        """Test that changes to the table model are reflected in the list model."""
        # Add a row to the table model
        self.table_model.add_row("C", "3")
        self.assertEqual(self.list_model.rowCount(), 3)
        self.assertEqual(self.list_model.data(self.list_model.index(2)), "C")
        
        # Remove a row from the table model
        self.table_model.remove_row(0)
        self.assertEqual(self.list_model.rowCount(), 2)
        self.assertEqual(self.list_model.data(self.list_model.index(0)), "B")
        
        # Update data in the table model
        self.table_model.setData(self.table_model.index(0, 0), "X")
        self.assertEqual(self.list_model.data(self.list_model.index(0)), "X")
