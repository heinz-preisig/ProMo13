import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject

from Common.classes.entity import Entity
from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.entity_editor import (
    EntityEditorController,
    )
from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import (
    ImageItemDelegate,
    )
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.main import MainModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_editor import (
    EntityEditorView,
    )
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.main import MainView
from common.components import starting_dialog
# In the imports section at the top of main.py
from .app_state import AppState
from .app_state import StateMachine


class MainController(QObject):
    def __init__(self, main_model: MainModel, main_view: MainView):
        super().__init__()

        self._model = main_model
        self._view = main_view

        # Load default ontology
        try:
            available_ontologies = self._model.get_available_ontologies()
            if available_ontologies:
                # Load the first available ontology by default
                self._model.load_ontology(available_ontologies[0])
            else:
                print("Warning: No ontologies found. The tree will be empty.")
        except Exception as e:
            print(f"Error loading ontology: {str(e)}")
            # Continue with empty model if loading fails

        # Rest of the initialization...
        self.state_machine = StateMachine(initial_state=AppState.IDLE)
        self._setup_state_handlers()

        # Rest of your existing initialization code
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

        # Debug: Print model status
        print(f"Model tree model: {hasattr(self._model, 'entity_tree_model')}")
        print(f"Model list models: {hasattr(self._model, 'entity_list_models')}")

        # Set the model on the view
        self._view.ui.tree_entities.setModel(self._model.entity_tree_model)
        print(f"Tree model set on view: {self._view.ui.tree_entities.model() is self._model.entity_tree_model}")

        # Debug: Check entity views
        entity_views = [
                self._view.ui.list_integrators,
                self._view.ui.list_equations,
                self._view.ui.list_input,
                self._view.ui.list_output,
                self._view.ui.list_instantiate,
                self._view.ui.list_pending,
                ]
        print(f"Number of entity views: {len(entity_views)}")
        print(f"Number of list models: {len(self._model.entity_list_models)}")

        # Connect UI signals
        self._connect_ui_signals()
        self._last_selected_item_data = None
        self._current_entity_id = None

        # Run debug methods
        self._debug_tree_model()
        self._debug_view_settings()

    def _debug_tree_model(self):
        """Debug method to print tree model contents."""
        model = self._view.ui.tree_entities.model()
        if not model:
            print("No model set on tree view")
            return

        print("\n=== Tree Model Debug ===")
        print(f"Model class: {model.__class__.__name__}")
        print(f"Row count (root): {model.rowCount()}")

        # Print first level items
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            data = index.data()
            print(f"Row {row}: {data}")

            # Print children if any
            child_count = model.rowCount(index)
            if child_count > 0:
                print(f"  Has {child_count} children")
                for child_row in range(child_count):
                    child_index = model.index(child_row, 0, index)
                    print(f"  - {child_index.data()}")

        print("======================\n")

    def _debug_view_settings(self):
        """Debug method to check view settings."""
        print("\n=== View Settings ===")
        print(f"View visible: {self._view.isVisible()}")
        print(f"Tree view visible: {self._view.ui.tree_entities.isVisible()}")
        print(f"Tree view enabled: {self._view.ui.tree_entities.isEnabled()}")
        print(f"Tree view has focus: {self._view.ui.tree_entities.hasFocus()}")
        print("===================\n")

    def _setup_state_handlers(self) -> None:
        """Set up state handlers for the state machine."""

        # IDLE state
        @self.state_machine.on_enter(AppState.IDLE)
        def enter_idle(kwargs):
            print("Entering IDLE state")
            self._view.ui.actionEdit.setEnabled(False)
            self._view.ui.actionDelete.setEnabled(False)

        # ENTITY_SELECTED state
        @self.state_machine.on_enter(AppState.ENTITY_SELECTED)
        def enter_entity_selected(kwargs):
            entity_id = kwargs.get('entity_id')
            print(f"Entering ENTITY_SELECTED state for {entity_id}")
            self._view.ui.actionEdit.setEnabled(True)
            self._view.ui.actionDelete.setEnabled(True)

        # EDITING_ENTITY state
        @self.state_machine.on_enter(AppState.EDITING_ENTITY)
        def enter_editing_entity(kwargs):
            entity_id = kwargs.get('entity_id')
            print(f"Entering EDITING_ENTITY state for {entity_id}")
            if entity_id:
                self.edit_entity()

        # State change handler
        self.state_machine.state_changed.connect(self._on_state_changed)

    def _connect_ui_signals(self) -> None:
        """Connect UI signals to state machine events."""
        # Tree selection changed
        selection_model = self._view.ui.tree_entities.selectionModel()
        try:
            selection_model.currentChanged.disconnect()
        except TypeError:
            pass  # No connections to disconnect
        selection_model.currentChanged.connect(self._on_tree_selection_changed)

        # Button clicks - Edit
        try:
            self._view.ui.actionEdit.triggered.disconnect()
        except TypeError:
            pass
        self._view.ui.actionEdit.triggered.connect(
                lambda: self.state_machine.transition_to(
                        AppState.EDITING_ENTITY,
                        entity_id=getattr(self, '_current_entity_id', None)
                        )
                )

        # Connect other signals with safe disconnection
        def safe_disconnect(signal):
            try:
                signal.disconnect()
            except (TypeError, RuntimeError):
                pass

        # New entity
        safe_disconnect(self._view.ui.actionNew.triggered)
        self._view.ui.actionNew.triggered.connect(self.on_action_new_triggered)

        # Double click
        safe_disconnect(self._view.ui.tree_entities.doubleClicked)
        self._view.ui.tree_entities.doubleClicked.connect(self.on_tree_double_clicked)

        # Delete
        safe_disconnect(self._view.ui.actionDelete.triggered)
        self._view.ui.actionDelete.triggered.connect(self.delete_entity)

        # Save
        safe_disconnect(self._view.ui.actionSave.triggered)
        self._view.ui.actionSave.triggered.connect(self._model.save)

        # Tree changed
        safe_disconnect(self._model.tree_changed)
        self._model.tree_changed.connect(self._view.on_tree_changed)

    def _on_state_changed(self, new_state: AppState, data: dict) -> None:
        """Handle state changes and update UI accordingly."""
        print(f"State changed to: {new_state.name}")

    def _on_tree_selection_changed(self, current: QtCore.QModelIndex, previous: QtCore.QModelIndex) -> None:
        """Handle tree selection changes."""
        if current.isValid():
            entity_id = current.data(QtCore.Qt.UserRole + 1)
            self._current_entity_id = entity_id

            # Store the item's data for later use
            try:
                item = current.model().itemFromIndex(current)
                is_leaf = item.rowCount() == 0
                self._last_selected_item_data = {
                        'text'   : item.text(),
                        'is_leaf': is_leaf,
                        'data'   : item.data(QtCore.Qt.UserRole + 1),
                        'index'  : current
                        }

                # Load entity data
                self._model.load_entity(current)

                # Update menu state
                self._view.menu_items_state(current)

                # Transition to ENTITY_SELECTED state
                self.state_machine.transition_to(
                        AppState.ENTITY_SELECTED,
                        entity_id=entity_id,
                        index=current
                        )
            except Exception as e:
                print(f"Error in selection changed: {e}")
                self.state_machine.transition_to(AppState.IDLE)
        else:
            self.state_machine.transition_to(AppState.IDLE)

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
        if not hasattr(self, '_last_selected_item_data') or not self._last_selected_item_data:
            print("No item data available")
            QtWidgets.QMessageBox.warning(
                    self._view,
                    "No Selection",
                    "Please select an entity type to create a new instance or an entity to copy.\n"
                    "Click on an item in the tree view first."
                    )
            return

        # Get the selected item data
        item_data = self._last_selected_item_data

        try:
            # Determine if this is a leaf node (entity type) or an entity instance
            is_leaf = item_data.get('is_leaf', False)

            if is_leaf:
                # For leaf nodes, create a new instance of the selected type
                base_entity_id = item_data.get('entity_id')
                if not base_entity_id:
                    raise ValueError("No entity ID found in selected item")

                # Prompt for new instance name
                new_entity_id, ok = QtWidgets.QInputDialog.getText(
                        self._view,
                        'New Instance',
                        'Enter a name for the new instance:',
                        QtWidgets.QLineEdit.Normal,
                        ''
                        )

                if not ok or not new_entity_id:
                    return  # User cancelled or entered an empty name

                # Create the new entity
                new_entity, merger_data = self._model.create_entity(
                        new_entity_id,
                        [base_entity_id]  # Single base entity
                        )

                # If merging is needed (for multiple inheritance), handle it
                if merger_data is not None:
                    self._handle_merging(new_entity, merger_data)
                else:
                    # No merging needed, add the entity to the model
                    self._model.add_entity_to_model(new_entity)
                    self._select_entity_in_tree(new_entity.entity_name)

            else:
                # For non-leaf nodes, open the entity editor for the selected entity
                entity_id = item_data.get('entity_id')
                if entity_id and entity_id in self._model.all_entities:
                    self.edit_entity()

        except Exception as e:
            error_msg = f"Error creating new entity: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                    self._view,
                    "Error",
                    error_msg
                    )

        item_data = self._last_selected_item_data
        print(f"Using stored item data: {item_data}")

        # Check if this is an existing entity (has entity data in UserRole + 3)
        entity_obj = item_data['index'].data(QtCore.Qt.UserRole + 3)
        if entity_obj is not None and hasattr(entity_obj, 'entity_name'):
            # Create a new instance based on the selected entity
            base_entity = entity_obj
            # For existing entities, we need to handle the full entity name properly
            parts = base_entity.entity_name.split('.')
            base_name = parts[-1]  # Get just the name part (after last dot)
            display_name = base_name.split('|')[-1] if '|' in base_name else base_name
            entity_type_path = ".".join(parts[:-1])  # Everything before the last dot
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

            # Handle the tuple format: ('entity_type', 'macroscopic', 'node', 'charge_energy_mass|constant|infinity')
            if isinstance(entity_data, tuple) and len(entity_data) > 1 and entity_data[0] == 'entity_type':
                # For entity types, the last part is the full type spec (e.g., 'charge_energy_mass|constant|infinity')
                entity_type_path = ".".join(entity_data[1:-1])  # Skip 'entity_type' and the last part
                type_spec = entity_data[-1]  # This is the full type spec with tokens
                display_name = type_spec.split('|')[-1]  # Get the last part as display name
                # Reconstruct the full path with the type spec
                entity_type_path = f"{entity_type_path}.{type_spec}" if entity_type_path else type_spec
            else:
                # For other cases, use the string representation
                entity_type_path = str(entity_data)
                display_name = item_data.get('text', 'entity')
                if '|' in display_name:
                    display_name = display_name.split('|')[-1]

        # Clean up the entity type path by removing any empty parts
        entity_type_path = ".".join(part.strip() for part in entity_type_path.split(".") if part.strip())

        # If we have a base entity, use its type as the entity type path
        if base_entity and hasattr(base_entity, 'entity_type'):
            entity_type_path = base_entity.entity_type
            print(f"Using base entity type: {entity_type_path}")
        else:
            print(f"Using entity type path: {entity_type_path}")

        # Prompt user for instance name
        name, ok = QtWidgets.QInputDialog.getText(
                self._view,
                "New Entity Instance",
                f"Enter a name for the new {display_name} instance:",
                QtWidgets.QLineEdit.Normal
                )

        if not ok or not name.strip():
            print("User cancelled or entered empty name")
            return

        # Determine the new entity ID based on whether we have a base entity or type path
        if base_entity:
            # If we have a base entity, construct the ID from its components
            parts = base_entity.entity_name.split('.')
            if len(parts) >= 3:
                # Extract network and category from the base entity
                network = parts[0]
                category = parts[1]

                # Get the full type part (everything after network.category)
                type_part = parts[2]

                # The new entity ID should be: network.category.type_part|name
                new_entity_id = f"{network}.{category}.{type_part}.{name.strip()}"
                print(f"Creating new variant with ID: {new_entity_id}")
            else:
                # Fallback to simple appending if the base entity name doesn't have the expected format
                new_entity_id = f"{base_entity.entity_name}|{name.strip()}"
                print(f"Creating new variant (fallback) with ID: {new_entity_id}")

            # Create a new entity with the same type and properties as the base entity
            new_entity = Entity(
                    entity_name=new_entity_id,
                    all_equations=base_entity.all_equations,
                    index_set=base_entity.index_set,
                    integrators=dict(base_entity.integrators),
                    var_eq_forest=[dict(tree) for tree in base_entity.var_eq_forest],
                    init_vars=list(base_entity.init_vars),
                    input_vars=list(base_entity.input_vars),
                    output_vars=list(base_entity.output_vars)
                    )

            # Manually copy over additional attributes that might be needed
            if hasattr(base_entity, 'entity_type'):
                new_entity.entity_type = base_entity.entity_type
            if hasattr(base_entity, 'is_reservoir'):
                new_entity.is_reservoir = base_entity.is_reservoir

            print(f"Created new variant from: {base_entity.entity_name}")
        else:
            # If no base entity, use the entity_type_path directly
            new_entity_id = f"{entity_type_path}.{name.strip()}"
            print(f"Creating new base entity with ID: {new_entity_id}")

            # Handle multi-token types (e.g., 'charge_energy_mass|constant|infinity')
            if '|' in entity_type_path:
                # Extract the base type (part before the first '|')
                base_type = entity_type_path.split('|')[0]
                # Try to find the base entity
                base_entity = self._model.all_entities.get(base_type)

                if base_entity:
                    # Create a new entity with the same type and properties as the base entity
                    new_entity = Entity(
                            entity_name=new_entity_id,
                            all_equations=base_entity.all_equations,
                            index_set=base_entity.index_set,
                            integrators=dict(base_entity.integrators),
                            var_eq_forest=[dict(tree) for tree in base_entity.var_eq_forest],
                            init_vars=list(base_entity.init_vars),
                            input_vars=list(base_entity.input_vars),
                            output_vars=list(base_entity.output_vars)
                            )
                    # Manually copy over additional attributes that might be needed
                    if hasattr(base_entity, 'entity_type'):
                        new_entity.entity_type = base_entity.entity_type
                    if hasattr(base_entity, 'is_reservoir'):
                        new_entity.is_reservoir = base_entity.is_reservoir
                    print(f"Created new entity from multi-token base: {base_type}")
                else:
                    # If base entity not found, create a new one with the full type path
                    new_entity = Entity(
                            entity_name=new_entity_id,
                            all_equations=self._model.all_equations
                            )
                    print(f"Created new base entity with multi-token type: {entity_type_path}")
            else:
                # Create a new entity instance
                new_entity = Entity(
                        entity_name=new_entity_id,
                        all_equations=self._model.all_equations
                        )
                print(f"Created new base entity: {new_entity_id}")

        try:
            print(f"Created new entity in memory: {new_entity_id}")

            # Create and show the editor
            from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.entity_editor import EntityEditorController
            from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_editor import EntityEditorModel
            from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_editor import EntityEditorView

            # Create editor components
            editor_model = EntityEditorModel(
                    editing_entity=new_entity,
                    all_variables=self._model.all_variables,
                    all_equations=self._model.all_equations
                    )
            editor_view = EntityEditorView(model=editor_model, parent=self._view)
            editor_controller = EntityEditorController(editor_model, editor_view)

            # Show the editor dialog
            result = editor_view.exec_()

            # Only add the entity if the dialog was accepted
            if result == QtWidgets.QDialog.Accepted:
                # Use the model's method to add the entity and update the tree
                self._model.add_entity_to_model(new_entity)
                self._model.current_entity_id = new_entity_id
                self._handle_merging(new_entity, self._model.get_merger_data())
                print(f"Entity {new_entity_id} added to model after editor confirmation")

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

    def _handle_merging(self, new_entity: 'Entity', merger_data: dict) -> None:
        """Handle the entity merging process.

        Args:
            new_entity: The new entity being created
            merger_data: Dictionary containing the merger state
        """
        from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_merger import EntityMergerView

        # Create and configure the merger view
        view = EntityMergerView(merger_data, self._view)

        # Connect signals
        view.equation_selected.connect(
                lambda idx: self._model.solve_conflict(merger_data, idx)
                )
        view.undo_requested.connect(
                lambda: self._model.undo_merger_step(merger_data)
                )
        view.accepted.connect(
                lambda: self._on_merging_completed(new_entity, view)
                )
        view.rejected.connect(
                lambda: self._on_merging_cancelled(new_entity, view)
                )

        # Show the dialog
        view.show()

        # Load the first conflict
        conflict = self._model.get_next_conflict(merger_data)
        if not conflict:
            # No conflicts, complete the merge
            self._on_merging_completed(new_entity, view)
            return

    def _on_merging_completed(self, new_entity: 'Entity', view: 'QtWidgets.QDialog' = None) -> None:
        """Handle completion of the merging process.

        Args:
            new_entity: The entity that was created
            view: The merger view dialog (optional)
        """
        try:
            self._model.add_entity_to_model(new_entity)
            self._select_entity_in_tree(new_entity.entity_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                    self._view,
                    "Error",
                    f"Failed to add merged entity: {str(e)}"
                    )
        finally:
            if view:
                view.deleteLater()

    def _on_merging_cancelled(self, new_entity: 'Entity', view: 'QtWidgets.QDialog') -> None:
        """Handle cancellation of the merging process.

        Args:
            new_entity: The entity being created
            view: The merger view dialog
        """
        # Clean up the temporary entity
        if hasattr(new_entity, 'cleanup'):
            new_entity.cleanup()
        if view:
            view.deleteLater()

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
