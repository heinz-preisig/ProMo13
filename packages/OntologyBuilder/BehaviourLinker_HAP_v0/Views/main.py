from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from OntologyBuilder.BehaviourLinker.Views.Compiled_UIs import main_ui
from OntologyBuilder.BehaviourLinker.Models.main import MainModel


class MainView(QtWidgets.QMainWindow):
  show_event_triggered = QtCore.pyqtSignal()

  def __init__(self, main_model: MainModel):
    super().__init__()

    # Set up the user interface from Designer
    self.ui = main_ui.Ui_MainWindow()
    self.ui.setupUi(self)

    self._model = main_model

    # Set up tree view
    self.ui.tree_entities.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
    self.ui.tree_entities.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    
    # Install event filter to capture all mouse events
    self.ui.tree_entities.viewport().installEventFilter(self)
    
    # Set initial UI state
    self.ui.menuEntity.setFocus()
    self.ui.actionEdit.setEnabled(False)
    self.ui.actionDelete.setEnabled(False)
    
  def eventFilter(self, source, event):
    """Handle events from the tree view."""
    if (source is self.ui.tree_entities.viewport() and 
        event.type() == QtCore.QEvent.MouseButtonPress):
        index = self.ui.tree_entities.indexAt(event.pos())
        if index.isValid():
            print(f"\n=== Mouse click detected at {event.pos()} on item: {index.row()}, {index.column()}")
            # Manually set the current index to ensure selection
            self.ui.tree_entities.setCurrentIndex(index)
            # Force an update of the selection model
            selection_model = self.ui.tree_entities.selectionModel()
            if selection_model:
                selection_model.select(index, QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Rows)
                # Emit the currentChanged signal manually
                selection_model.currentChanged.emit(index, QtCore.QModelIndex())
    
    # Let the default event processing continue
    return super().eventFilter(source, event)

  def showEvent(self, event) -> None:
    super().showEvent(event)
    self.show_event_triggered.emit()

  def on_tree_changed(self):
    print("\n=== on_tree_changed called ===")
    try:
        # Expand all items first
        self.ui.tree_entities.expandAll()
        
        # Get the selection model
        selection_model = self.ui.tree_entities.selectionModel()
        if selection_model is None:
            print("Error: Could not get selection model")
            return
            
        # Clear any existing selection
        selection_model.clearSelection()
        
        # Set the selection mode to SingleSelection if not already set
        if self.ui.tree_entities.selectionMode() != QtWidgets.QAbstractItemView.SingleSelection:
            self.ui.tree_entities.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # Set the selection behavior to select rows if not already set
        if self.ui.tree_entities.selectionBehavior() != QtWidgets.QAbstractItemView.SelectRows:
            self.ui.tree_entities.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        # Ensure the view is set up to emit signals
        self.ui.tree_entities.setUpdatesEnabled(True)
        
        print("Tree view updated and ready for selection")
        
    except Exception as e:
        print(f"Error in on_tree_changed: {e}")
        import traceback
        traceback.print_exc()

  def menu_items_state(self, index: QtCore.QModelIndex):
    try:
      # Debug print to confirm the method is called
      print(f"menu_items_state called with index: {index.row()}, {index.column()} - Valid: {index.isValid()}")
      
      # Only enable edit/delete if it's a valid index and it's a leaf node
      is_leaf = False
      if index.isValid():
        model = index.model()
        if model is not None:
          item = model.itemFromIndex(index)
          if item is not None:
            # Check if this is a leaf node (no children)
            is_leaf = item.rowCount() == 0
      
      self.ui.actionEdit.setEnabled(index.isValid() and is_leaf)
      self.ui.actionDelete.setEnabled(index.isValid() and is_leaf)
      
    except Exception as e:
      print(f"Error in menu_items_state: {e}")
      import traceback
      traceback.print_exc()
      # Make sure to disable actions on error
      self.ui.actionEdit.setEnabled(False)
      self.ui.actionDelete.setEnabled(False)
