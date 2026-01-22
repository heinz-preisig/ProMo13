from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import ImageItemDelegate
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.image_list import ImageListModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import variable_selection_ui


class VariableSelectionView(QtWidgets.QDialog):

    def __init__(self, variables, parent=None):
        super().__init__(parent)
        
        print("\n=== DEBUG: VariableSelectionView.__init__ ===")
        print(f"Received {len(variables)} variables")
        for i, var in enumerate(variables[:3], 1):  # Print first 3 variables for debugging
            print(f"  Variable {i}: {var}")
            print(f"    Type: {type(var)}")
            if hasattr(var, 'get_id'):
                print(f"    ID: {var.get_id()}")
            if hasattr(var, 'get_img_path'):
                print(f"    Image path: {var.get_img_path()}")
        if len(variables) > 3:
            print(f"  ... and {len(variables) - 3} more variables")

        # Set up the user interface
        self.ui = variable_selection_ui.Ui_variable_selection()
        self.ui.setupUi(self)

        # Create and configure the model
        self.model = ImageListModel()
        print("Loading variables into model...")
        self.model.load_data(variables)  # Load the variables using the proper method
        
        print(f"Model row count after loading: {self.model.rowCount()}")
        
        # Set the model on the view
        self.ui.list_variables.setModel(self.model)
        
        print("Setting up delegate...")
        delegate = ImageItemDelegate(self.ui.list_variables)
        self.ui.list_variables.setItemDelegate(delegate)

        # Only enable accept button if we have valid items
        has_items = self.model.rowCount() > 0
        print(f"Has items: {has_items}")
        self.ui.pbutton_accept.setEnabled(has_items)
        
        # Select first item if available
        if has_items:
            print("Selecting first item...")
            self.ui.list_variables.setCurrentIndex(self.model.index(0, 0))
        else:
            print("No items to select")
            
        # Print model data for debugging
        self._debug_print_model_data()

        # Connect signals
        self.ui.list_variables.doubleClicked.connect(self.accept)
        self.ui.pbutton_accept.clicked.connect(self.accept)
        self.ui.pbutton_cancel.clicked.connect(self.reject)
        
    def _debug_print_model_data(self):
        """Print model data for debugging purposes."""
        print("\n=== Model Data ===")
        print(f"Model has {self.model.rowCount()} rows")
        for row in range(min(5, self.model.rowCount())):  # Print first 5 rows
            index = self.model.index(row, 0)
            item = self.model.itemFromIndex(index)
            if item:
                print(f"Row {row}: {item.text()}")
                print(f"  Data (UserRole): {item.data(Qt.UserRole)}")
                print(f"  Data (UserRole+1): {item.data(Qt.UserRole + 1) if item.data(Qt.UserRole + 1) else 'None'}")
        print("==================\n")
