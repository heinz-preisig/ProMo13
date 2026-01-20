from typing import List

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListView

from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_generator import EntityGeneratorModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_generator import EntityGeneratorView
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.insert_str import InsertStrView


# TODO List
# 1. Animations for the list.
# 2. Fix animations skip when next/prev buttons are pressed fast.
# 3. Probably change so Arc/Node is first in the entity name.


class EntityGeneratorController(QtCore.QObject):
  def __init__(self, model: EntityGeneratorModel, view: EntityGeneratorView):
    super().__init__()

    self._model = model
    self._view = view

    self.stacked_views: List[QListView] = [
            None,
            self._view.ui.list_network,
            self._view.ui.list_token,
            self._view.ui.list_mechanism,
            self._view.ui.list_nature,
            ]

    for i in range(1, 5):
      self.stacked_views[i].setModel(self._model.stacked_models[i])

    self._view.ui.tree_bases.setModel(self._model.tree_bases_model)

    # Connecting signal -> slots
    # Signals from the View
    self._view.ui.pbutton_next.clicked.connect(self.on_next_button_clicked)
    self._view.ui.pbutton_previous.clicked.connect(self.on_previous_button_clicked)
    self._view.ui.pbutton_cancel.clicked.connect(self._view.reject)
    self._view.ui.pbutton_finish.clicked.connect(self.on_finish_button_clicked)

    for i in range(1, 5):
      self.stacked_views[i].selectionModel().selectionChanged.connect(self.on_list_selection_change)
      self.stacked_views[i].doubleClicked.connect(self.on_next_button_clicked)

    # Signals from the Model
    self._model.tree_changed.connect(self._view.on_tree_changed)

  def on_next_button_clicked(self):
    current_page = self._view.ui.stackedWidget.currentIndex()

    new_value = None
    if current_page == 0:
      if self._view.ui.rbutton_node.isChecked():
        new_value = "node"
      else:
        new_value = "arc"
    else:
      new_value = self.stacked_views[current_page].selectedIndexes()

    self._model.update_summary(current_page, new_value)
    self._model.update_stacked_models(current_page + 1)

    self._view.next_page()

  def on_previous_button_clicked(self):
    self._view.previous_page()
    self.on_list_selection_change()

  def on_finish_button_clicked(self):
    print("\n=== on_finish_button_clicked started ===")
    
    # Update the summary model with the selected bases.
    new_value = self._view.ui.tree_bases.selectedIndexes()
    current_page = self._view.ui.stackedWidget.currentIndex()
    self._model.update_summary(current_page, new_value)

    # Get the entity name from the model
    entity_name = self._model.get_entity_name()
    if not entity_name:
        entity_name = "NewEntity"  # Default name if not set

    print(f"Initial entity name: {entity_name}")

    # Show the dialog to confirm the entity name
    used_names = self._model.get_used_names()
    forbidden_names = [name.lower() for name in used_names]
    print(f"Used names: {used_names}")

    dlg = InsertStrView(
        "Entity name",
        "Insert a name for the new entity:",
        forbidden_names,
        self._view
    )
    dlg.ui.ledit_input.setText(entity_name)  # Pre-fill with suggested name
    
    result = dlg.exec_()
    if result == QtWidgets.QDialog.Accepted:
        final_name = dlg.ui.ledit_input.text().strip()
        print(f"User entered name: {final_name}")
        
        if not final_name:
            QtWidgets.QMessageBox.warning(
                self._view, 
                "Invalid Name", 
                "Entity name cannot be empty."
            )
            return
            
        try:
            print("\n--- Creating entity ---")
            print(f"Model has main_model: {hasattr(self._model, 'main_model')}")
            if hasattr(self._model, 'main_model'):
                print(f"Current entities in main model: {list(self._model.main_model.all_entities.keys())}")
            
            # Create the entity (but don't add it to the model yet)
            new_entity, merger_model = self._model.create_entity(final_name)
            print(f"Entity created, type: {type(new_entity).__name__}")
            
            # If merging is needed, show the merger dialog
            if merger_model is not None:
                print("Merger model created, showing merger dialog")
                from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_merger import EntityMergerView
                merger_view = EntityMergerView(merger_model)
                if merger_view.exec_() != QtWidgets.QDialog.Accepted:
                    print("User cancelled merge")
                    return  # User cancelled the merge
            
            print("\n--- Showing entity editor ---")
            # Now show the entity editor
            from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.entity_editor import EntityEditorController
            from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_editor import EntityEditorModel
            from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_editor import EntityEditorView
            
            # Create editor components
            editor_model = EntityEditorModel(new_entity)
            editor_view = EntityEditorView()
            editor_controller = EntityEditorController(editor_model, editor_view)
            
            # Show the editor
            editor_result = editor_view.exec_()
            print(f"Editor dialog result: {editor_result} (Accepted: {editor_result == QtWidgets.QDialog.Accepted})")
            
            if editor_result == QtWidgets.QDialog.Accepted:
                print("\n--- Adding entity to model ---")
                # User accepted the editor, add to model
                if hasattr(self._model, 'main_model'):
                    print("Adding entity to main model")
                    self._model.main_model.add_entity_to_model(new_entity)
                    print(f"Entity added to model: {final_name}")
                    self._view.accept()
                else:
                    # Fallback if main_model is not available
                    print("No main_model, using fallback")
                    self._model.add_entity_name(final_name)
                    if hasattr(self._model, 'update_tree'):
                        self._model.update_tree()
                    self._view.accept()
            else:
                print("User cancelled the editor")
            
        except RuntimeError as e:
            print(f"Runtime error: {str(e)}")
            QtWidgets.QMessageBox.critical(
                self._view,
                "Error",
                f"Failed to create entity: {str(e)}"
            )
        except Exception as e:
            import traceback
            print(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            QtWidgets.QMessageBox.critical(
                self._view,
                "Unexpected Error",
                f"An unexpected error occurred: {str(e)}"
            )
    else:
        print("User cancelled the name dialog")
    
    print("=== on_finish_button_clicked completed ===\n")

  def on_list_selection_change(self):
    current_page = self._view.ui.stackedWidget.currentIndex()
    if current_page != 0:
      selection = self.stacked_views[current_page].selectedIndexes()

    self._view.ui.pbutton_next.setEnabled(bool(selection))
