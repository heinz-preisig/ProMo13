from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from ..models import ListModel, TableModel
from ..views import MainWindow
from ..delegates import SoftHighlightDelegate


class AppController:
    """Controller that manages the interaction between models and views."""
    
    def __init__(self, model_list: ListModel, model_table: TableModel, 
                 view: MainWindow, delegate: SoftHighlightDelegate):
        """Initialize the controller with models, view, and delegate.
        
        Args:
            model_list: The list model to use
            model_table: The table model to use
            view: The main window view
            delegate: The delegate for custom item rendering
        """
        self.model_list = model_list
        self.model_table = model_table
        self.view = view
        self.delegate = delegate

        # Hook models & delegate to views
        self._setup_views()
        
        # Wire up UI controls
        self._connect_signals()
        
        # Start in LIST mode
        # self._mode = MainWindow.LIST_MODE
        # self._apply_mode()
    
    def _setup_views(self):
        """Set up the views with their models and delegates."""
        # self.view.listView.setModel(self.model_list)
        self.view.tableView.setModel(self.model_table)
        # self.view.listView.setItemDelegate(self.delegate)
        # self.view.tableView.setItemDelegate(self.delegate)
        # self.view.tableView.horizontalHeader().setStretchLastSection(True)
    
    def _connect_signals(self):
        """Connect UI signals to controller methods."""
        # self.view.switchButton.clicked.connect(self.toggle_mode)
        # self.view.deleteButton.clicked.connect(self.delete_selected)
        # self.view.listAddButton.clicked.connect(self.add_list_item)
        # self.view.tableAddButton.clicked.connect(self.add_table_row)

        pass
    def toggle_mode(self):
        """Toggle between list and table modes."""
        self.mode = MainWindow.TABLE_MODE if self.mode == MainWindow.LIST_MODE else MainWindow.LIST_MODE
    
    def _apply_mode(self):
        """Update the UI based on the current mode."""
        self.view.mode = self._mode
    
    def add_list_item(self):
        """Add a new item to the list."""
        text = self.view.listInput.text().strip()
        if not text:
            QMessageBox.warning(self.view, "Warning", "Item text cannot be empty.")
            return
        # Add to the table model with an empty value
        # The list model will update automatically via signals
        self.model_table.add_row(text, "")
        self.view.listInput.clear()
    
    def add_table_row(self):
        """Add a new row to the table."""
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
        """Delete the currently selected item(s)."""
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
    
    @property
    def mode(self) -> int:
        """Get the current mode (LIST_MODE or TABLE_MODE)."""
        return self._mode
    
    @mode.setter
    def mode(self, value: int) -> None:
        """Set the current mode and update the UI."""
        if value != self._mode:
            self._mode = value
            self._apply_mode()
