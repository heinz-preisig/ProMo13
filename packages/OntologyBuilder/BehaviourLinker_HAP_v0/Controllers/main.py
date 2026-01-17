import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
from Common.classes.entity import Entity

from Common.classes.io import get_available_ontologies
from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.entity_editor import (
    EntityEditorController,
)
from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.entity_generator import (
    EntityGeneratorController,
)
from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.entity_merger import (
    EntityMergerController,
)
from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import (
    ImageItemDelegate,
)
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.main import MainModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_editor import (
    EntityEditorView,
)
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_generator import (
    EntityGeneratorView,
)
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_merger import (
    EntityMergerView,
)
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.main import MainView
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.ontology_selector import (
    OntologySelectorView,
)
from common.components import starting_dialog


class MainController(QObject):
    def __init__(self, main_model: MainModel, main_view: MainView):
        super().__init__()

        self._model = main_model
        self._view = main_view

        self._view.ui.tree_entities.setModel(self._model.entity_tree_model)
        entity_views = [
            self._view.ui.list_integrators,
            self._view.ui.list_equations,
            self._view.ui.list_input,
            self._view.ui.list_output,
            self._view.ui.list_instantiate,
            self._view.ui.list_pending,
        ]

        for view, model in zip(
            entity_views, self._model.entity_list_models, strict=False
        ):
            view.setModel(model)
            delegate = ImageItemDelegate(view)
            view.setItemDelegate(delegate)

        # Connections from the View
        self._view.show_event_triggered.connect(self.on_show_event_triggered)

        selection_model = self._view.ui.tree_entities.selectionModel()
        
        # Disconnect any existing connections to avoid duplicates
        try:
            selection_model.currentChanged.disconnect()
        except TypeError:
            # No connections to disconnect
            pass

        self._last_selected_item_data = None

        def debug_selection_changed(current, previous):
            # Reset the stored data
            self._last_selected_item_data = None

            if not current.isValid():
                return

            try:
                # Get the item from the index
                model = current.model()
                if model is None:
                    return

                item = model.itemFromIndex(current)
                if item is None:
                    return

                # Check if this is a leaf node (entity type)
                is_leaf = item.rowCount() == 0

                # Store the item's data for later use
                self._last_selected_item_data = {
                    'text': item.text(),
                    'is_leaf': is_leaf,
                    'data': item.data(QtCore.Qt.UserRole + 1),  # Store the entity data
                    'index': current
                }

                # Load entity data when an item is selected (single click)
                try:
                    self._model.load_entity(current)
                except Exception:
                    pass

                # Update menu state
                try:
                    self._view.menu_items_state(current)
                except Exception:
                    pass

            except Exception:
                pass
        
        # Connect our debug handler
        selection_model.currentChanged.connect(debug_selection_changed)
        
        # Connect other signals
        self._view.ui.actionNew.triggered.connect(self.on_action_new_triggered)
        self._view.ui.tree_entities.doubleClicked.connect(self.on_tree_double_clicked)
        self._view.ui.actionEdit.triggered.connect(self.edit_entity)
        self._view.ui.actionDelete.triggered.connect(self.delete_entity)
        self._view.ui.actionSave.triggered.connect(self._model.save)
        # Connections from the Model
        self._model.tree_changed.connect(self._view.on_tree_changed)

    def on_show_event_triggered(self) -> None:
        """Launches a Dialog to get the ontology name.

        If the Dialog gets accepted it updates the model with the ontology
        name.
        """

        available_ontologies = self._model.get_available_ontologies()
        view = starting_dialog.StartingDialogView()
        controller = starting_dialog.StartingDialogController(
            view, available_ontologies
        )

        result = view.exec_()
        if result == QtWidgets.QDialog.Accepted:
            ontology_name = view.ui.selection_list.currentIndex().data()
            self._model.load_ontology(ontology_name)
        else:
            sys.exit()

    # def on_action_new_triggered(self) -> None:
    #     """Starts the process to create a new Entity instance.
    #
    #     The process:
    #     1. Gets the selected entity type from the tree view
    #     2. Prompts the user for an instance name
    #     3. Creates a new entity with the composed ID
    #     4. Opens the entity for editing
    #     """
    #     print("\n=== on_action_new_triggered called ===")
    #     print("Debug - Checking if method is being called")
    #
    #     # Get the current selection from the tree view
    #     selected_indexes = self._view.ui.tree_entities.selectedIndexes()
    #     print(f"Number of selected indexes: {len(selected_indexes)}")
    #
    #     if not selected_indexes:
    #         print("No selection found")
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "No Selection",
    #                 "Please select an entity type to create a new instance."
    #                 )
    #         return
    #
    #     current_index = selected_indexes[0]  # Get the first selected index
    #     print(f"Current index: {current_index.row()}, {current_index.column()} - Valid: {current_index.isValid()}")
    #
    #     # Get the current selection
    #     current_index = self._view.ui.tree_entities.currentIndex()
    #     if not current_index.isValid():
    #         QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "No Selection",
    #             "Please select an entity type to create a new instance."
    #         )
    #         return
    #
    #     # Get the item and check if it's a leaf node (entity type)
    #     item = self._view.ui.tree_entities.model().itemFromIndex(current_index)
    #     if not item or item.rowCount() > 0:  # Not a leaf node
    #         QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Invalid Selection",
    #             "Please select a specific entity type (leaf node) to create a new instance."
    #         )
    #         return
    #
    #     # Get the entity type path from the tree model
    #     model = self._view.ui.tree_entities.model()
    #     path = []
    #     index = current_index
    #
    #     # Walk up the tree to build the full path
    #     while index.isValid():
    #         path.insert(0, index.data())
    #         index = index.parent()
    #
    #     entity_type_path = ".".join(path)
    #
    #     # Prompt user for instance name
    #     name, ok = QtWidgets.QInputDialog.getText(
    #         self._view,
    #         "New Entity Instance",
    #         f"Enter a name for the new {path[-1]} instance:",
    #         QtWidgets.QLineEdit.Normal
    #     )
    #
    #     if not ok or not name.strip():
    #         return  # User cancelled or entered empty name
    #
    #     # Create the full entity ID by appending the instance name
    #     new_entity_id = f"{entity_type_path}.{name.strip()}"
    #
    #     print(f"Creating new entity with ID: {new_entity_id}")
    #
    #     # Add the new entity (empty bases list since we're not inheriting)
    #     dlg_merge_model = self._model.add_entity(new_entity_id, [])
    #     if dlg_merge_model is not None:
    #         dlg_merge_view = EntityMergerView(dlg_merge_model, self._view)
    #         dlg_merge_controller = EntityMergerController(
    #             dlg_merge_model, dlg_merge_view
    #         )
    #         result = dlg_merge_view.exec_()
    #         if result != QtWidgets.QDialog.Accepted:
    #             return  # User cancelled the merge dialog
    #
    #     # Select and edit the new entity
    #     index = self._model.entity_tree_model.index_from_path(new_entity_id)
    #     if index.isValid():
    #         self._view.ui.tree_entities.setCurrentIndex(index)
    #         self.edit_entity()
    #     else:
    #         QtWidgets.QMessageBox.warning(
    #             self._view,
    #             "Error",
    #             f"Could not find the newly created entity: {new_entity_id}"
    #         )

    # def on_action_new_triggered(self) -> None:
    #     """Starts the process to create a new Entity instance."""
    #     print("\n=== on_action_new_triggered called ===")
    #
    #     # First try to get the current index from the tree view
    #     current_index = self._view.ui.tree_entities.currentIndex()
    #     print(f"Current index from currentIndex(): {current_index.row() if current_index.isValid() else 'Invalid'}")
    #
    #     # If no current index, try to get it from the selection model
    #     if not current_index.isValid():
    #         selection_model = self._view.ui.tree_entities.selectionModel()
    #         if selection_model:
    #             current_index = selection_model.currentIndex()
    #             print(
    #                 f"Current index from selection model: {current_index.row() if current_index.isValid() else 'Invalid'}")
    #
    #     # If still no valid index, show an error
    #     if not current_index or not current_index.isValid():
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "No Selection",
    #                 "Please select an entity type to create a new instance.\n"
    #                 "Click on an item in the tree view first."
    #                 )
    #         return
    #
    #     # Get the item from the index
    #     model = current_index.model()
    #     if not model:
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Error",
    #                 "Could not get the model for the selected item."
    #                 )
    #         return
    #
    #     item = model.itemFromIndex(current_index)
    #     if not item:
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Error",
    #                 "Could not get the item from the selected index."
    #                 )
    #         return
    #
    #     # Check if it's a leaf node
    #     is_leaf = item.rowCount() == 0
    #     print(f"Is leaf node: {is_leaf}")
    #
    #     if not is_leaf:
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Invalid Selection",
    #                 "Please select a specific entity type (leaf node) to create a new instance."
    #                 )
    #         return
    #
    #     # Get the entity type path
    #     path = []
    #     index = current_index
    #     while index.isValid():
    #         path.insert(0, index.data())
    #         index = index.parent()
    #
    #     if not path:
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Error",
    #                 "Could not determine the entity type path."
    #                 )
    #         return
    #
    #     entity_type_path = ".".join(path)
    #     print(f"Entity type path: {entity_type_path}")
    #
    #     # Clean up the entity type path
    #     entity_type_path = entity_type_path.replace('charge_energy_mass', 'mass')
    #     entity_type_path = ".".join(part.strip() for part in entity_type_path.split(".") if part.strip())
    #     print(f"Processed entity type path: {entity_type_path}")
    #
    #     # Prompt user for instance name
    #     name, ok = QtWidgets.QInputDialog.getText(
    #             self._view,
    #             "New Entity Instance",
    #             f"Enter a name for the new {path[-1]} instance:",
    #             QtWidgets.QLineEdit.Normal
    #             )
    #
    #     if not ok or not name.strip():
    #         return  # User cancelled or entered empty name
    #
    #     # Create the full entity ID by appending the instance name
    #     new_entity_id = f"{entity_type_path}.{name.strip()}"
    #
    #     print(f"Creating new entity with ID: {new_entity_id}")
    #
    #     try:
    #         # Add the new entity (empty bases list since we're not inheriting)
    #         dlg_merge_model = self._model.add_entity(new_entity_id, [])
    #         if dlg_merge_model is not None:
    #             dlg_merge_view = EntityMergerView(dlg_merge_model, self._view)
    #             dlg_merge_controller = EntityMergerController(
    #                     dlg_merge_model, dlg_merge_view
    #                     )
    #             result = dlg_merge_view.exec_()
    #             if result != QtWidgets.QDialog.Accepted:
    #                 return  # User cancelled the merge dialog
    #
    #         # Select and edit the new entity
    #         index = self._model.entity_tree_model.index_from_path(new_entity_id)
    #         if index.isValid():
    #             self._view.ui.tree_entities.setCurrentIndex(index)
    #             self.edit_entity()
    #         else:
    #             QtWidgets.QMessageBox.warning(
    #                     self._view,
    #                     "Error",
    #                     f"Could not find the newly created entity: {new_entity_id}\n"
    #                     f"Available entities: {list(self._model.all_entities.keys())[:5]}..."
    #                     )
    #
    #     except Exception as e:
    #         QtWidgets.QMessageBox.critical(
    #                 self._view,
    #                 "Error",
    #                 f"Failed to create entity: {str(e)}"
    #                 )
    #         import traceback
    #         traceback.print_exc()

    # def on_action_new_triggered(self) -> None:
    #     """Starts the process to create a new Entity instance."""
    #     print("\n=== on_action_new_triggered called ===")
    #     print(f"Stored item data exists: {hasattr(self, '_last_selected_item_data')}")
    #
    #     if hasattr(self, '_last_selected_item_data'):
    #         print(f"Item data content: {self._last_selected_item_data}")
    #     else:
    #         print("No _last_selected_item_data attribute found")
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "No Selection",
    #                 "Please select an entity type to create a new instance.\n"
    #                 "Click on an item in the tree view first."
    #                 )
    #         return
    #
    #     item_data = self._last_selected_item_data
    #     print(f"Using stored item data: {item_data}")
    #
    #     # Check if it's a leaf node
    #     if not item_data.get('is_leaf', False):
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Invalid Selection",
    #                 "Please select a specific entity type (leaf node) to create a new instance."
    #                 )
    #         return
    #
    #     # Get the entity type path from the stored data
    #     entity_data = item_data.get('data')
    #     if not entity_data:
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Error",
    #                 "Could not get entity data from the selected item."
    #                 )
    #         return
    #
    #     # Handle the tuple format: ('entity_type', 'macroscopic', 'node', 'charge_energy_mass|constant|infinity')
    #     if isinstance(entity_data, tuple) and len(entity_data) > 1 and entity_data[0] == 'entity_type':
    #         entity_type_path = ".".join(entity_data[1:])  # Skip the 'entity_type' prefix
    #     else:
    #         entity_type_path = str(entity_data)
    #
    #     print(f"Entity type path from stored data: {entity_type_path}")
    #
    #     # Clean up the entity type path
    #     entity_type_path = entity_type_path.replace('charge_energy_mass', 'mass')
    #     entity_type_path = ".".join(part.strip() for part in entity_type_path.split(".") if part.strip())
    #     print(f"Processed entity type path: {entity_type_path}")
    #
    #     # Get the display name for the prompt
    #     display_name = item_data.get('text', 'entity')
    #     if isinstance(display_name, str) and '|' in display_name:
    #         display_name = display_name.split('|')[-1]  # Get the last part if it's a path
    #
    #     # Prompt user for instance name
    #     name, ok = QtWidgets.QInputDialog.getText(
    #             self._view,
    #             "New Entity Instance",
    #             f"Enter a name for the new {display_name} instance:",
    #             QtWidgets.QLineEdit.Normal
    #             )
    #
    #     if not ok or not name.strip():
    #         return  # User cancelled or entered empty name
    #
    #     # Create the full entity ID by appending the instance name
    #     new_entity_id = f"{entity_type_path}.{name.strip()}"
    #
    #     print(f"Creating new entity with ID: {new_entity_id}")
    #
    #     try:
    #         # Add the new entity (empty bases list since we're not inheriting)
    #         dlg_merge_model = self._model.add_entity(new_entity_id, [])
    #         if dlg_merge_model is not None:
    #             dlg_merge_view = EntityMergerView(dlg_merge_model, self._view)
    #             dlg_merge_controller = EntityMergerController(
    #                     dlg_merge_model, dlg_merge_view
    #                     )
    #             result = dlg_merge_view.exec_()
    #             if result != QtWidgets.QDialog.Accepted:
    #                 return  # User cancelled the merge dialog
    #
    #         # Select and edit the new entity
    #         index = self._model.entity_tree_model.index_from_path(new_entity_id)
    #         if index.isValid():
    #             self._view.ui.tree_entities.setCurrentIndex(index)
    #             self.edit_entity()
    #         else:
    #             QtWidgets.QMessageBox.warning(
    #                     self._view,
    #                     "Error",
    #                     f"Could not find the newly created entity: {new_entity_id}\n"
    #                     f"Available entities: {list(self._model.all_entities.keys())[:5]}..."
    #                     )
    #
    #     except Exception as e:
    #         QtWidgets.QMessageBox.critical(
    #                 self._view,
    #                 "Error",
    #                 f"Failed to create entity: {str(e)}"
    #                 )
    #         import traceback
    #         traceback.print_exc()

    # def on_action_new_triggered(self) -> None:
    #     """Starts the process to create a new Entity instance."""
    #     print("\n=== on_action_new_triggered called ===")
    #     print(f"Stored item data exists: {hasattr(self, '_last_selected_item_data')}")
    #
    #     if not hasattr(self, '_last_selected_item_data') or not self._last_selected_item_data:
    #         print("No item data available")
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "No Selection",
    #                 "Please select an entity type to create a new instance.\n"
    #                 "Click on an item in the tree view first."
    #                 )
    #         return
    #
    #     item_data = self._last_selected_item_data
    #     print(f"Using stored item data: {item_data}")
    #
    #     # Check if it's a leaf node
    #     if not item_data.get('is_leaf', False):
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Invalid Selection",
    #                 "Please select a specific entity type (leaf node) to create a new instance."
    #                 )
    #         return
    #
    #     # Get the entity type path from the stored data
    #     entity_data = item_data.get('data')
    #     if not entity_data:
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Error",
    #                 "Could not get entity data from the selected item."
    #                 )
    #         return
    #
    #     # Handle the tuple format: ('entity_type', 'macroscopic', 'node', 'charge_mass|constant|infinity')
    #     if isinstance(entity_data, tuple) and len(entity_data) > 1 and entity_data[0] == 'entity_type':
    #         # Skip the 'entity_type' prefix and join the rest with dots
    #         entity_type_path = ".".join(entity_data[1:])
    #     else:
    #         entity_type_path = str(entity_data)
    #
    #     print(f"Entity type path from stored data: {entity_type_path}")
    #
    #     # Clean up the entity type path
    #     entity_type_path = entity_type_path.replace('charge_energy_mass', 'mass')
    #     entity_type_path = ".".join(part.strip() for part in entity_type_path.split(".") if part.strip())
    #     print(f"Processed entity type path: {entity_type_path}")
    #
    #     # Get the display name for the prompt
    #     display_name = item_data.get('text', 'entity')
    #     if isinstance(display_name, str) and '|' in display_name:
    #         display_name = display_name.split('|')[-1]  # Get the last part if it's a path
    #
    #     # Prompt user for instance name
    #     name, ok = QtWidgets.QInputDialog.getText(
    #             self._view,
    #             "New Entity Instance",
    #             f"Enter a name for the new {display_name} instance:",
    #             QtWidgets.QLineEdit.Normal
    #             )
    #
    #     if not ok or not name.strip():
    #         return  # User cancelled or entered empty name
    #
    #     # Create the full entity ID by appending the instance name
    #     new_entity_id = f"{entity_type_path}.{name.strip()}"
    #
    #     print(f"Creating new entity with ID: {new_entity_id}")
    #
    #     try:
    #         # Add the new entity (empty bases list since we're not inheriting)
    #         dlg_merge_model = self._model.add_entity(new_entity_id, [])
    #         if dlg_merge_model is not None:
    #             dlg_merge_view = EntityMergerView(dlg_merge_model, self._view)
    #             dlg_merge_controller = EntityMergerController(
    #                     dlg_merge_model, dlg_merge_view
    #                     )
    #             result = dlg_merge_view.exec_()
    #             if result != QtWidgets.QDialog.Accepted:
    #                 return  # User cancelled the merge dialog
    #
    #         # Get the index for the new entity
    #         if hasattr(self._model, 'entity_tree_model') and hasattr(self._model.entity_tree_model, 'index_from_path'):
    #             index = self._model.entity_tree_model.index_from_path(new_entity_id)
    #             if index.isValid():
    #                 self._view.ui.tree_entities.setCurrentIndex(index)
    #                 self.edit_entity()
    #             else:
    #                 # If we can't find the exact index, try to select the parent
    #                 parent_path = ".".join(new_entity_id.split('.')[:-1])
    #                 parent_index = self._model.entity_tree_model.index_from_path(parent_path)
    #                 if parent_index.isValid():
    #                     self._view.ui.tree_entities.setCurrentIndex(parent_index)
    #                     self._view.ui.tree_entities.expand(parent_index)
    #                 QtWidgets.QMessageBox.information(
    #                         self._view,
    #                         "Entity Created",
    #                         f"Entity created but could not be selected in the tree.\n"
    #                         f"New entity ID: {new_entity_id}"
    #                         )
    #         else:
    #             QtWidgets.QMessageBox.warning(
    #                     self._view,
    #                     "Error",
    #                     "Could not find the newly created entity in the tree model.\n"
    #                     f"New entity ID: {new_entity_id}\n"
    #                     f"Available entities: {list(getattr(self._model, 'all_entities', {}).keys())[:5]}..."
    #                     )
    #
    #     except Exception as e:
    #         QtWidgets.QMessageBox.critical(
    #                 self._view,
    #                 "Error",
    #                 f"Failed to create entity: {str(e)}\n\n"
    #                 f"Entity ID: {new_entity_id}\n"
    #                 f"Entity type: {type(e).__name__}"
    #                 )
    #         print(f"Error creating entity: {str(e)}")
    #         import traceback
    #         traceback.print_exc()

    # def on_action_new_triggered(self) -> None:
    #     """Starts the process to create a new Entity instance."""
    #     print("\n=== on_action_new_triggered called ===")
    #     print(f"Stored item data exists: {hasattr(self, '_last_selected_item_data')}")
    #
    #     if not hasattr(self, '_last_selected_item_data') or not self._last_selected_item_data:
    #         print("No item data available")
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "No Selection",
    #                 "Please select an entity type to create a new instance.\n"
    #                 "Click on an item in the tree view first."
    #                 )
    #         return
    #
    #     item_data = self._last_selected_item_data
    #     print(f"Using stored item data: {item_data}")
    #
    #     # Check if it's a leaf node
    #     if not item_data.get('is_leaf', False):
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Invalid Selection",
    #                 "Please select a specific entity type (leaf node) to create a new instance."
    #                 )
    #         return
    #
    #     # Get the entity type path from the stored data
    #     entity_data = item_data.get('data')
    #     if not entity_data:
    #         QtWidgets.QMessageBox.warning(
    #                 self._view,
    #                 "Error",
    #                 "Could not get entity data from the selected item."
    #                 )
    #         return
    #
    #     # Handle the tuple format: ('entity_type', 'macroscopic', 'node', 'charge_mass|constant|infinity')
    #     if isinstance(entity_data, tuple) and len(entity_data) > 1 and entity_data[0] == 'entity_type':
    #         # Skip the 'entity_type' prefix and join the rest with dots
    #         entity_type_path = ".".join(entity_data[1:])
    #     else:
    #         entity_type_path = str(entity_data)
    #
    #     print(f"Entity type path from stored data: {entity_type_path}")
    #
    #     # Clean up the entity type path
    #     entity_type_path = entity_type_path.replace('charge_energy_mass', 'mass')
    #     entity_type_path = ".".join(part.strip() for part in entity_type_path.split(".") if part.strip())
    #     print(f"Processed entity type path: {entity_type_path}")
    #
    #     # Get the display name for the prompt
    #     display_name = item_data.get('text', 'entity')
    #     if isinstance(display_name, str) and '|' in display_name:
    #         display_name = display_name.split('|')[-1]  # Get the last part if it's a path
    #
    #     # Prompt user for instance name
    #     name, ok = QtWidgets.QInputDialog.getText(
    #             self._view,
    #             "New Entity Instance",
    #             f"Enter a name for the new {display_name} instance:",
    #             QtWidgets.QLineEdit.Normal
    #             )
    #
    #     if not ok or not name.strip():
    #         return  # User cancelled or entered empty name
    #
    #     # Create the full entity ID by appending the instance name
    #     new_entity_id = f"{entity_type_path}.{name.strip()}"
    #
    #     print(f"Creating new entity with ID: {new_entity_id}")
    #
    #     try:
    #         # Check if entity_tree_model is available
    #         if not hasattr(self._model, 'entity_tree_model') or self._model.entity_tree_model is None:
    #             raise AttributeError("Entity tree model is not initialized")
    #
    #         # Add the new entity (empty bases list since we're not inheriting)
    #         dlg_merge_model = self._model.add_entity(new_entity_id, [])
    #
    #         if dlg_merge_model is not None:
    #             dlg_merge_view = EntityMergerView(dlg_merge_model, self._view)
    #             dlg_merge_controller = EntityMergerController(
    #                     dlg_merge_model, dlg_merge_view
    #                     )
    #             result = dlg_merge_view.exec_()
    #             if result != QtWidgets.QDialog.Accepted:
    #                 return  # User cancelled the merge dialog
    #
    #         # Refresh the tree model to include the new entity
    #         self._view.on_tree_changed()
    #
    #         # Try to find and select the new entity
    #         print(f"\nTrying to find entity with path: {new_entity_id}")
    #         index = None
    #         parent_index = None
    #
    #         try:
    #             # Try to get the index for the new entity
    #             if hasattr(self._model.entity_tree_model, 'index_from_path'):
    #                 index = self._model.entity_tree_model.index_from_path(new_entity_id)
    #                 print(f"Index from path result: {index}")
    #
    #                 if index is not None and hasattr(index, 'isValid') and index.isValid():
    #                     print(f"Found index for {new_entity_id}")
    #                     self._view.ui.tree_entities.setCurrentIndex(index)
    #                     self.edit_entity()
    #                     return  # Successfully found and selected the entity
    #                 else:
    #                     print(f"Could not find index for {new_entity_id}")
    #
    #                     # Try to find the parent
    #                     parent_path = ".".join(new_entity_id.split('.')[:-1])
    #                     print(f"Trying parent path: {parent_path}")
    #                     parent_index = self._model.entity_tree_model.index_from_path(parent_path)
    #
    #                     if parent_index is not None and hasattr(parent_index, 'isValid') and parent_index.isValid():
    #                         print(f"Found parent index for {parent_path}")
    #                         self._view.ui.tree_entities.setCurrentIndex(parent_index)
    #                         self._view.ui.tree_entities.expand(parent_index)
    #                     else:
    #                         print(f"Could not find parent index for {parent_path}")
    #
    #             # Show success message
    #             QtWidgets.QMessageBox.information(
    #                     self._view,
    #                     "Entity Created",
    #                     f"Entity created successfully!\n"
    #                     f"New entity ID: {new_entity_id}\n\n"
    #                     f"Note: The entity was created but could not be automatically selected in the tree.\n"
    #                     f"Please navigate to it manually."
    #                     )
    #
    #         except Exception as e:
    #             print(f"Error while trying to select the new entity: {str(e)}")
    #             import traceback
    #             traceback.print_exc()
    #
    #             # Show success message even if selection failed
    #             QtWidgets.QMessageBox.information(
    #                     self._view,
    #                     "Entity Created",
    #                     f"Entity created successfully!\n"
    #                     f"New entity ID: {new_entity_id}\n\n"
    #                     f"Note: There was an error selecting the entity in the tree.\n"
    #                     f"Please navigate to it manually."
    #                     )
    #
    #     except Exception as e:
    #         QtWidgets.QMessageBox.critical(
    #                 self._view,
    #                 "Error",
    #                 f"Failed to create entity: {str(e)}\n\n"
    #                 f"Entity ID: {new_entity_id}\n"
    #                 f"Error type: {type(e).__name__}\n"
    #                 f"Model has entity_tree_model: {hasattr(self._model, 'entity_tree_model')}"
    #                 )
    #         print(f"Error creating entity: {str(e)}")
    #         import traceback
    #         traceback.print_exc()

    def on_action_new_triggered(self) -> None:
        """Starts the process to create a new Entity instance."""
        print("\n=== on_action_new_triggered called ===")
        print(f"Stored item data exists: {hasattr(self, '_last_selected_item_data')}")

        if not hasattr(self, '_last_selected_item_data') or not self._last_selected_item_data:
            print("No item data available")
            QtWidgets.QMessageBox.warning(
                    self._view,
                    "No Selection",
                    "Please select an entity type to create a new instance.\n"
                    "Click on an item in the tree view first."
                    )
            return

        item_data = self._last_selected_item_data
        print(f"Using stored item data: {item_data}")

        # Check if it's a leaf node
        if not item_data.get('is_leaf', False):
            QtWidgets.QMessageBox.warning(
                    self._view,
                    "Invalid Selection",
                    "Please select a specific entity type (leaf node) to create a new instance."
                    )
            return

        # Get the entity type path from the stored data
        entity_data = item_data.get('data')
        if not entity_data:
            QtWidgets.QMessageBox.warning(
                    self._view,
                    "Error",
                    "Could not get entity data from the selected item."
                    )
            return

        # Handle the tuple format: ('entity_type', 'macroscopic', 'node', 'charge_mass|constant|infinity')
        if isinstance(entity_data, tuple) and len(entity_data) > 1 and entity_data[0] == 'entity_type':
            # Skip the 'entity_type' prefix and join the rest with dots
            entity_type_path = ".".join(entity_data[1:])
        else:
            entity_type_path = str(entity_data)

        print(f"Entity type path from stored data: {entity_type_path}")

        # Clean up the entity type path
        entity_type_path = entity_type_path.replace('charge_energy_mass', 'mass')
        entity_type_path = ".".join(part.strip() for part in entity_type_path.split(".") if part.strip())
        print(f"Processed entity type path: {entity_type_path}")

        # Get the display name for the prompt
        display_name = item_data.get('text', 'entity')
        if isinstance(display_name, str) and '|' in display_name:
            display_name = display_name.split('|')[-1]  # Get the last part if it's a path

        # Prompt user for instance name
        name, ok = QtWidgets.QInputDialog.getText(
                self._view,
                "New Entity Instance",
                f"Enter a name for the new {display_name} instance:",
                QtWidgets.QLineEdit.Normal
                )

        if not ok or not name.strip():
            return  # User cancelled or entered empty name

        # Create the full entity ID by appending the instance name
        new_entity_id = f"{entity_type_path}.{name.strip()}"
        print(f"Creating new entity with ID: {new_entity_id}")

        try:
            # Create a new entity instance
            new_entity = Entity(
                    entity_name=new_entity_id,
                    all_equations=self._model.all_equations
                    )

            # Create editor model with the new entity
            from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_editor import EntityEditorModel
            dlg_model = EntityEditorModel(
                    editing_entity=new_entity,  # Changed from 'entity=' to 'editing_entity='
                    all_variables=self._model.all_variables,
                    all_equations=self._model.all_equations
                    )

            # Create and show the editor
            dlg_view = EntityEditorView(dlg_model, self._view)
            dlg_controller = EntityEditorController(dlg_model, dlg_view)

            result = dlg_view.exec_()

            if result == QtWidgets.QDialog.Accepted:
                # User clicked OK, add the entity to the model
                self._model.all_entities[new_entity_id] = new_entity
                self._model._update_tree_model()
                self._view.on_tree_changed()

                # Try to select the new entity
                try:
                    index = self._model.entity_tree_model.index_from_path(new_entity_id)
                    if index is not None and hasattr(index, 'isValid') and index.isValid():
                        self._view.ui.tree_entities.setCurrentIndex(index)
                        self._view.ui.tree_entities.expand(index.parent())
                except Exception as e:
                    print(f"Error selecting new entity: {e}")
                    import traceback
                    traceback.print_exc()

                QtWidgets.QMessageBox.information(
                        self._view,
                        "Entity Created",
                        f"Entity created successfully!\n"
                        f"New entity ID: {new_entity_id}"
                        )
            else:
                # User cancelled, don't add the entity
                QtWidgets.QMessageBox.information(
                        self._view,
                        "Entity Creation Cancelled",
                        "The new entity was not saved."
                        )

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                    self._view,
                    "Error",
                    f"Failed to create entity: {str(e)}\n\n"
                    f"Entity ID: {new_entity_id}\n"
                    f"Error type: {type(e).__name__}"
                    )
            print(f"Error creating entity: {str(e)}")
            import traceback
            traceback.print_exc()

    def edit_entity(self) -> None:
        """Handle the edit entity action."""
        print("\n" + "=" * 50)
        print("=== edit_entity called ===")

        try:
            # Debug: Print current model state
            self.debug_model_state()

            # Get the editor model
            print("Getting entity editor model...")
            dlg_model = self._model.get_entity_editor_model()

            print("Creating editor view...")
            dlg_view = EntityEditorView(dlg_model, self._view)
            dlg_controller = EntityEditorController(dlg_model, dlg_view)

            print("Showing editor dialog...")
            result = dlg_view.exec_()

            if result == QtWidgets.QDialog.Accepted:
                print("Dialog accepted, updating entity...")
                self._model.update_entity(None, dlg_model.editing_entity)
                print("Entity updated successfully")
            else:
                print("Dialog was cancelled")

        except Exception as e:
            error_msg = f"Error in edit_entity: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                    self._view,
                    "Edit Error",
                    error_msg
                    )

    def debug_model_state(self):
        """Print debug information about the current model state."""
        if not hasattr(self, '_model'):
            print("Model not initialized")
            return

        print("\n" + "=" * 50)
        print("=== DEBUG: Model State ===")
        print(f"Current entity ID: {getattr(self._model, 'current_entity_id', 'Not set')}")
        print(f"Number of entities: {len(getattr(self._model, 'all_entities', {}))}")

        if hasattr(self._model, 'entity_tree_model'):
            print(f"Entity tree model rows: {self._model.entity_tree_model.rowCount()}")

        # Print first few entity IDs if available
        all_entities = getattr(self._model, 'all_entities', {})
        if all_entities:
            print("\nFirst 5 entity IDs:")
            for i, (eid, e) in enumerate(all_entities.items()):
                if i >= 5:
                    break
                print(f"  {i + 1}. {eid} (type: {type(e).__name__})")
        else:
            print("\nNo entities found in model")

        print("=" * 50 + "\n")

    # def edit_entity(self) -> None:
    #     index = self._view.ui.tree_entities.currentIndex()
    #     dlg_model = self._model.get_entity_editor_model(index)
    #     dlg_view = EntityEditorView(dlg_model, self._view)
    #     dlg_controller = EntityEditorController(dlg_model, dlg_view)
    #
    #     result = dlg_view.exec_()
    #     if result == QtWidgets.QDialog.Accepted:
    #         self._model.update_entity(index, dlg_model.editing_entity)

    def delete_entity(self) -> None:
        # TODO: Maybe add safeguard.
        index = self._view.ui.tree_entities.currentIndex()
        self._model.delete_entity(index)

    def on_tree_double_clicked(self, index: QtCore.QModelIndex) -> None:
        """Handle double-click events on the tree view."""
        print("\n=== on_tree_double_clicked called ===")
        print(f"Index: {index.row()}, {index.column()} - Valid: {index.isValid()}")
        
        if not index.isValid():
            return
            
        try:
            # Get the item from the index
            model = index.model()
            if model is None:
                return
                
            item = model.itemFromIndex(index)
            if item is None:
                return
                
            # Check if this is a leaf node (entity type) by checking for children
            is_leaf = item.rowCount() == 0
            
            if is_leaf:
                print("Leaf node clicked - loading and editing entity")
                # First, load the entity data into the UI
                self._model.load_entity(index)
                # Then open the editor
                self.edit_entity()
            else:
                print("Non-leaf node clicked - expanding/collapsing")
                # Toggle expansion for non-leaf nodes
                if self._view.ui.tree_entities.isExpanded(index):
                    self._view.ui.tree_entities.collapse(index)
                else:
                    self._view.ui.tree_entities.expand(index)
                    
        except Exception as e:
            print(f"Error in on_tree_double_clicked: {e}")
            import traceback
            traceback.print_exc()
