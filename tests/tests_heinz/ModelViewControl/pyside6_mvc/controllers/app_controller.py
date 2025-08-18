from PySide6.QtCore import QModelIndex, Qt, Signal, Slot
from PySide6.QtWidgets import QMessageBox


class AppController:
    """Controller for the application, managing the interaction between models and views."""
    
    def __init__(self, list_model, table_model, view, delegate):
        """Initialize the controller with models, view, and delegate.
        
        Args:
            list_model: The list model
            table_model: The table model
            view: The main window view
            delegate: The item delegate for rendering
        """
        self.list_model = list_model
        self.table_model = table_model
        self.view = view
        self.delegate = delegate
        
        # Set up the view with models and delegate
        self.view.set_models(self.list_model, self.table_model)
        self.view.set_delegate(self.delegate)
        
        # Connect view signals to controller methods
        self.view.add_item_requested.connect(self.add_list_item)
        self.view.add_row_requested.connect(self.add_table_row)
        self.view.delete_requested.connect(self.delete_selected)
        self.view.switch_mode_requested.connect(self.toggle_mode)
        
        # Set initial mode
        self.mode = self.view.LIST_MODE
    
    @property
    def mode(self):
        """Get the current view mode."""
        return self.view.mode
    
    @mode.setter
    def mode(self, new_mode):
        """Set the current view mode and update the UI accordingly."""
        self.view.mode = new_mode
    
    @Slot()
    def toggle_mode(self):
        """Toggle between list and table view modes."""
        if self.mode == self.view.LIST_MODE:
            self.mode = self.view.TABLE_MODE
        else:
            self.mode = self.view.LIST_MODE
    
    @Slot(str)
    def add_list_item(self, text):
        """Add an item to the list model.
        
        Args:
            text: The text of the item to add
        """
        if text:
            self.table_model.add_row(text, "")
    
    @Slot(str, str)
    def add_table_row(self, name, value):
        """Add a row to the table model.
        
        Args:
            name: The name for the new row
            value: The value for the new row
        """
        if name:  # Only require name, value can be empty
            self.table_model.add_row(name, value)
    
    @Slot()
    def delete_selected(self):
        """Delete the currently selected item(s)."""
        selected_indexes = self.view.get_selected_indexes()
        
        if not selected_indexes:
            QMessageBox.information(
                self.view,
                "No Selection",
                "Please select an item to delete.",
                QMessageBox.Ok
            )
            return
        
        # For multiple selection, we need to delete from bottom to top to preserve indices
        rows = sorted([index.row() for index in selected_indexes], reverse=True)
        
        for row in rows:
            self.table_model.remove_row(row)
