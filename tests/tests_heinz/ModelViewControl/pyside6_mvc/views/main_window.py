from PySide6.QtCore import Qt, Signal, Slot, QFile, QIODevice
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QStackedWidget, QListView, QTableView,
    QFormLayout, QSizePolicy, QVBoxLayout, QApplication
)
from PySide6.QtUiTools import QUiLoader
import os
import sys


class MainWindow(QMainWindow):
    """Main window for the application."""
    
    # View modes
    LIST_MODE = 0
    TABLE_MODE = 1
    
    # Signals
    add_item_requested = Signal(str)  # For list view
    add_row_requested = Signal(str, str)  # For table view (name, value)
    delete_requested = Signal()
    switch_mode_requested = Signal()
    
    def __init__(self, parent=None):
        """Initialize the main window."""
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("PySide6 MVC + Delegate Example")
        self.resize(800, 600)
        
        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create a layout for the central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create mode label and switch button
        self.mode_label = QLabel("List View")
        self.main_layout.addWidget(self.mode_label)
        
        # Create a horizontal layout for buttons
        self.button_layout = QHBoxLayout()
        
        # Create switch and delete buttons
        self.switch_button = QPushButton("Switch to Table")
        self.delete_button = QPushButton("Delete Selected")
        
        self.button_layout.addWidget(self.switch_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.delete_button)
        
        self.main_layout.addLayout(self.button_layout)
        
        # Create a stacked widget for list and table views
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create list view page
        self.list_page = QWidget()
        self.list_layout = QVBoxLayout(self.list_page)
        
        # List view and input
        self.list_view = QListView()
        self.list_layout.addWidget(self.list_view)
        
        # Input for list
        self.list_input_layout = QHBoxLayout()
        self.list_input = QLineEdit()
        self.list_input.setPlaceholderText("Enter item text...")
        self.list_add_button = QPushButton("Add Item")
        
        self.list_input_layout.addWidget(self.list_input)
        self.list_input_layout.addWidget(self.list_add_button)
        self.list_layout.addLayout(self.list_input_layout)
        
        # Add list page to stacked widget
        self.stacked_widget.addWidget(self.list_page)
        
        # Create table view page
        self.table_page = QWidget()
        self.table_layout = QVBoxLayout(self.table_page)
        
        # Table view
        self.tableView = QTableView()
        self.table_layout.addWidget(self.tableView)
        
        # Form for table input
        self.table_form = QFormLayout()
        
        self.table_name_input = QLineEdit()
        self.table_name_input.setPlaceholderText("Name")
        self.table_value_input = QLineEdit()
        self.table_value_input.setPlaceholderText("Value")
        
        self.table_form.addRow("Name:", self.table_name_input)
        self.table_form.addRow("Value:", self.table_value_input)
        
        self.table_add_button = QPushButton("Add Row")
        
        self.table_layout.addLayout(self.table_form)
        self.table_layout.addWidget(self.table_add_button)
        
        # Add table page to stacked widget
        self.stacked_widget.addWidget(self.table_page)
        
        # Set initial mode
        self._mode = self.LIST_MODE
        self.update_ui_for_mode()
        
        # Connect signals
        self.setup_connections()
    
    def setup_connections(self):
        """Set up signal connections."""
        self.switch_button.clicked.connect(self.switch_mode_requested)
        self.delete_button.clicked.connect(self.delete_requested)
        self.list_add_button.clicked.connect(self.on_add_item_clicked)
        self.table_add_button.clicked.connect(self.on_add_row_clicked)
        self.list_input.returnPressed.connect(self.on_add_item_clicked)
        self.table_name_input.returnPressed.connect(self.on_add_row_clicked)
        self.table_value_input.returnPressed.connect(self.on_add_row_clicked)
    
    @property
    def mode(self):
        """Get the current view mode."""
        return self._mode
    
    @mode.setter
    def mode(self, new_mode):
        """Set the current view mode and update the UI accordingly."""
        if new_mode != self._mode:
            self._mode = new_mode
            self.update_ui_for_mode()
    
    def update_ui_for_mode(self):
        """Update the UI based on the current mode."""
        if self.mode == self.LIST_MODE:
            self.stacked_widget.setCurrentIndex(0)
            self.mode_label.setText("List View")
            self.switch_button.setText("Switch to Table")
            self.list_input.setFocus()
        else:
            self.stacked_widget.setCurrentIndex(1)
            self.mode_label.setText("Table View")
            self.switch_button.setText("Switch to List")
            self.table_name_input.setFocus()
    
    @Slot()
    def on_add_item_clicked(self):
        """Handle the add item button click in list mode."""
        text = self.list_input.text().strip()
        if text:
            self.add_item_requested.emit(text)
            self.list_input.clear()
    
    @Slot()
    def on_add_row_clicked(self):
        """Handle the add row button click in table mode."""
        name = self.table_name_input.text().strip()
        value = self.table_value_input.text().strip()
        
        if name:  # Only require name, value can be empty
            self.add_row_requested.emit(name, value)
            self.table_name_input.clear()
            self.table_value_input.clear()
    
    def clear_inputs(self):
        """Clear all input fields."""
        self.list_input.clear()
        self.table_name_input.clear()
        self.table_value_input.clear()
    
    def set_models(self, list_model, table_model):
        """Set the models for the list and table views."""
        self.list_view.setModel(list_model)
        self.tableView.setModel(table_model)
    
    def set_delegate(self, delegate):
        """Set the item delegate for the list and table views."""
        self.list_view.setItemDelegate(delegate)
        self.tableView.setItemDelegateForColumn(0, delegate)  # Only first column for now
    
    def get_selected_indexes(self):
        """Get the currently selected indexes in the current view."""
        if self.mode == self.LIST_MODE:
            return self.list_view.selectedIndexes()
        else:
            return self.tableView.selectedIndexes()
