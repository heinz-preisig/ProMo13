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

    def on_action_new_triggered(self) -> None:
        """Handles creating a new entity or editing an existing one.

        If an entity type is selected, creates a new instance of that type.
        If an existing entity is selected, creates a copy for a new instance.
        """
        print("\n===", "on_action_new_triggered called", "===")
        print(f"Stored item data: {hasattr(self, '_last_selected_item_data')}")

        if not hasattr(self, '_last_selected_item_data') or not self._last_selected_item_data:
            print("No item data available")
            QtWidgets.QMessageBox.warning(
                    self._view,
                    "No Selection",
                    "Please select an entity type to create a new instance or an existing entity to edit.\n"
                    "Click on an item in the tree view first."
                    )
            return

        item_data = self._last_selected_item_data
        print(f"Using stored item data: {item_data}")

        # Check if this is an existing entity (has entity data in UserRole + 3)
        entity_obj = item_data['index'].data(QtCore.Qt.UserRole + 3)
        if entity_obj is not None and hasattr(entity_obj, 'entity_name'):
            # Create a new instance based on the selected entity
            base_entity = entity_obj
            entity_type_path = ".".join(base_entity.entity_name.split('.')[:-1])  # Get the type path
            display_name = base_entity.entity_name.split('.')[-1]  # Get the base name
        else:
            base_entity = None
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

            # Get the display name for the prompt
            display_name = item_data.get('text', 'entity')
            if isinstance(display_name, str) and '|' in display_name:
                display_name = display_name.split('|')[-1]  # Get the last part if it's a path

        # Clean up the entity type path
        entity_type_path = entity_type_path.replace('charge_energy_mass', 'mass')
        entity_type_path = ".".join(part.strip() for part in entity_type_path.split(".") if part.strip())
        print(f"Processed entity type path: {entity_type_path}")

        # Prompt user for instance name
        name, ok = QtWidgets.QInputDialog.getText(
                self._view,
                "New Entity Instance",
                f"Enter a name for the new {display_name} instance:",
                QtWidgets.QLineEdit.Normal
                )

        if not ok or not name.strip():
            print("User cancelled or entered empty name")
            return  # User cancelled or entered empty name

        # Create the full entity ID by appending the instance name
        new_entity_id = f"{entity_type_path}.{name.strip()}"
        print(f"Creating new entity with ID: {new_entity_id}")

        try:
            if base_entity:
                # Create a copy of the existing entity
                import copy
                new_entity = copy.deepcopy(base_entity)
                new_entity.entity_name = new_entity_id
            else:
                # Create a new entity instance
                new_entity = Entity(
                        entity_name=new_entity_id,
                        all_equations=self._model.all_equations
                        )

            # Add the new entity to the model
            self._model.all_entities[new_entity_id] = new_entity
            self._model.current_entity_id = new_entity_id  # Set the current entity ID
            self._model._update_tree_model()

            print(f"Created new entity: {new_entity_id}")

            # Open the editor with the new entity
            self.edit_entity()

        except Exception as e:
            error_msg = f"Error creating new entity: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                    self._view,
                    "Error",
                    f"Failed to create entity: {str(e)}"
                    )

    def edit_entity(self) -> None:
        """Handle the edit entity action."""
        print("\n" + "=" * 50)
        print("=== edit_entity called ===")

        try:
            # Debug: Print current model state
            self.debug_model_state()

            # Get the current entity ID
            entity_id = getattr(self._model, 'current_entity_id', None)
            print(f"Current entity_id: {entity_id}")
            
            if not entity_id:
                QtWidgets.QMessageBox.warning(
                    self._view,
                    "No Entity Selected",
                    "Please select an entity to edit."
                )
                return

            # Verify the entity exists
            if entity_id not in self._model.all_entities:
                print(f"Entity {entity_id} not found in all_entities")
                QtWidgets.QMessageBox.warning(
                    self._view,
                    "Entity Not Found",
                    f"Could not find entity: {entity_id}"
                )
                return

            # Get the editor model
            print("Getting entity editor model...")
            dlg_model = self._model.get_entity_editor_model()
            print(f"Editor model created: {dlg_model is not None}")

            if not dlg_model:
                QtWidgets.QMessageBox.warning(
                    self._view,
                    "Error",
                    "Could not create editor for the selected entity."
                )
                return

            print("Creating editor view...")
            dlg_view = EntityEditorView(dlg_model, self._view)
            dlg_controller = EntityEditorController(dlg_model, dlg_view)

            print("Showing editor dialog...")
            result = dlg_view.exec_()

            if result == QtWidgets.QDialog.Accepted:
                print("Dialog accepted, updating entity...")
                # Ensure we have the latest entity_id in case it changed
                current_entity_id = getattr(self._model, 'current_entity_id', None)
                print(f"Updating entity with ID: {current_entity_id}")
                
                if current_entity_id is None:
                    raise ValueError("current_entity_id is None when trying to update entity")
                    
                # Get the updated entity from the dialog model
                updated_entity = dlg_model.editing_entity
                if not updated_entity:
                    raise ValueError("No entity data to update")
                    
                print(f"Updated entity name: {getattr(updated_entity, 'entity_name', 'N/A')}")
                
                # Update the entity in the model
                self._model.update_entity(current_entity_id, updated_entity)
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
