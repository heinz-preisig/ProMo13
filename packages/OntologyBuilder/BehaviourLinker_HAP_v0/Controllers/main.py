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
from ..Models.entity_editor import EntityEditorModel
from ..Controllers.entity_editor import EntityEditorController

ID_COMPONENTS_TREE = {0: "network",
                      1: "category",
                      2: "entity_type",
                      3: "entity_instance "}

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
        """Handle tree selection changes.
        
        Only loads entity data when an actual entity is selected, not for containers
        like networks, arcs, or nodes.
        """
        if not current.isValid():
            self.state_machine.transition_to(AppState.IDLE)
            return

        try:
            # Get the item and its data
            item = current.model().itemFromIndex(current)
            if not item:
                self.state_machine.transition_to(AppState.IDLE)
                return

            # Get the entity data (if any)
            entity_data = item.data(QtCore.Qt.UserRole + 1)
            self._current_entity_id = entity_data if entity_data else None

            # Store the item's data for later use
            is_leaf = item.rowCount() == 0
            self._last_selected_item_data = {
                'text': item.text(),
                'is_leaf': is_leaf,
                'data': entity_data,
                'index': current
            }

            # Only try to load entity data if this is an actual entity
            if entity_data and isinstance(entity_data, str) and '|' in entity_data and '.' in entity_data:
                # This looks like an entity ID (e.g., 'control.node.signal|constant|AE')
                try:
                    self._model.load_entity(current)
                    self.state_machine.transition_to(
                        AppState.ENTITY_SELECTED,
                        entity_id=entity_data,
                        index=current
                    )
                except Exception as e:
                    print(f"Error loading entity data: {e}")
                    self.state_machine.transition_to(AppState.IDLE)
            else:
                # For non-entity items (networks, arcs, nodes), just update the UI
                # but don't try to load entity data
                self.state_machine.transition_to(AppState.IDLE)

            # Update menu state based on selection
            self._view.menu_items_state(current)

        except Exception as e:
            print(f"Error in selection changed: {e}")
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
        try:
            if not hasattr(self, '_last_selected_item_data') or not self._last_selected_item_data:
                QtWidgets.QMessageBox.warning(
                    self._view,
                    "No Selection",
                    "Please select an entity type to create a new instance.",
                    QtWidgets.QMessageBox.Ok
                )
                return

            item_data = self._last_selected_item_data
            print(f"Using stored item data: {item_data}")

            # Initialize variables
            base_entity = None
            base_entity_id = None
            display_name = "entity"

            # Check if this is an existing entity (has entity data in UserRole + 3)
            entity_obj = item_data['index'].data(QtCore.Qt.UserRole + 3)
            if entity_obj is not None and hasattr(entity_obj, 'entity_name'):
                # Create a new instance based on the selected entity
                base_entity = entity_obj
                base_entity_id = base_entity.entity_name
                parts = base_entity_id.split('.')
                display_name = parts[-1].split('|')[-1] if '|' in parts[-1] else parts[-1]
            else:
                # Handle entity type selection
                entity_data = item_data.get('data')
                if not entity_data:
                    QtWidgets.QMessageBox.warning(
                        self._view,
                        "Error",
                        "Could not get entity data from the selected item."
                    )
                    return

                # Handle entity type format: ('entity_type', 'control', 'node', 'signal|constant|AE')
            if isinstance(entity_data, tuple) and len(entity_data) > 1 and entity_data[0] == 'entity_type':
                # For format: ('entity_type', 'control', 'node', 'signal|constant|AE')
                if len(entity_data) >= 4 and '|' in entity_data[3]:
                    # Handle special case with pipe-separated type
                    domain, category, entity_type = entity_data[1:4]
                    name = entity_type.split('|')[-1]  # Take the last part after the last pipe
                    base_entity_id = f"{domain}.{category}.{entity_type}"
                    display_name = name
                else:
                    # Handle regular entity type format
                    parts = list(entity_data[1:])  # Skip the first 'entity_type' element
                    while len(parts) < 3:
                        parts.append('unknown')
                    domain, etype, name = parts[:3]
                    base_entity_id = f"{domain}.{etype}.{name}"
                    display_name = name.split('|')[-1] if '|' in name else name
                    return

            if not base_entity_id:
                QtWidgets.QMessageBox.warning(
                    self._view,
                    "Error",
                    "Could not determine base entity ID."
                )
                return

            # Check if we need to create the entity type first
            if base_entity_id not in self._model.all_entities:
                # This is a new entity type, create it
                try:
                    # Create the entity type with default values
                    from Common.classes.entity import Entity
                    entity_type = Entity(
                        entity_name=base_entity_id,
                        all_equations=self._model.all_equations
                    )
                    entity_type.entity_type = base_entity_id
                    
                    # Add to model
                    self._model.all_entities[base_entity_id] = entity_type
                    print(f"Created new entity type: {base_entity_id}")
                    
                except Exception as e:
                    error_msg = f"Failed to create entity type {base_entity_id}: {str(e)}"
                    print(error_msg)
                    QtWidgets.QMessageBox.critical(
                        self._view,
                        "Error",
                        error_msg
                    )
                    return

            # Prompt for new instance name
            new_entity_id, ok = QtWidgets.QInputDialog.getText(
                self._view,
                'New Instance',
                f'Enter a name for the new {display_name} instance:',
                QtWidgets.QLineEdit.Normal,
                ''
            )
            
            if ok and new_entity_id:  # Only proceed if user didn't cancel and entered a name
                try:
                    # Create the entity but don't add it to the model yet
                    new_entity, merger_data = self._model.create_entity(
                        new_entity_id,
                        [base_entity_id]  # Single base entity
                    )

                    # If merging is needed (for multiple inheritance), handle it
                    if merger_data is not None:
                        self._handle_merging(new_entity, merger_data)
                    else:
                        # Create editor components
                        editor_model = EntityEditorModel(new_entity, self._model.all_variables, self._model.all_equations)
                        editor_view = EntityEditorView(editor_model, self._view)
                        editor_controller = EntityEditorController(editor_model, editor_view)
                        
                        # Show the editor dialog
                        result = editor_view.exec_()
                        
                        if result == QtWidgets.QDialog.Accepted:
                            # Only add to model if user accepted the changes
                            self._model.add_entity_to_model(new_entity)
                            self._model._update_tree_model()
                            self._select_entity_in_tree(new_entity.entity_name)
                            self._model.current_entity_id = new_entity.entity_name
                            print("New entity created and added to model")
                        else:
                            # User cancelled, don't add to model
                            print("Entity creation cancelled by user")
                except Exception as e:
                    error_msg = f"Error creating entity: {str(e)}"
                    print(error_msg)
                    import traceback
                    traceback.print_exc()
                    QtWidgets.QMessageBox.critical(
                        self._view,
                        "Error",
                        error_msg
                    )
            return

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self._view,
                "Error",
                error_msg
            )
            return

        # Entity creation completed successfully
        print("Entity created successfully")

    def _select_entity_in_tree(self, entity_id: str) -> None:
        """Select an entity in the tree view by its ID.
        
        Args:
            entity_id: The ID of the entity to select
        """
        # Find the index of the entity in the tree model
        model = self._view.ui.tree_entities.model()
        if not model:
            return
            
        # Search through the model for the entity
        def find_index(parent_index):
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)
                item_data = index.data(QtCore.Qt.UserRole)
                if item_data and 'entity_id' in item_data and item_data['entity_id'] == entity_id:
                    return index
                
                # Recursively search children
                child_index = find_index(index)
                if child_index.isValid():
                    return child_index
                    
            return QtCore.QModelIndex()
            
        # Start search from root
        index = find_index(QtCore.QModelIndex())
        if index.isValid():
            # Select and expand the item
            self._view.ui.tree_entities.setCurrentIndex(index)
            self._view.ui.tree_entities.expand(index)
            
        # Update the current entity ID
        self._current_entity_id = entity_id

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

            # Get the entity object
            entity_obj = self._model.all_entities[entity_id]

            # Debug: Print entity details
            print(f"Entity type: {type(entity_obj).__name__}")
            print(f"Entity attributes: {[attr for attr in dir(entity_obj) if not attr.startswith('__')]}")

            # Get all variables and equations
            all_variables = self._model.all_variables
            all_equations = self._model.all_equations
            
            print(f"\n=== DEBUG: Variable and Equation Counts ===")
            print(f"Total variables in model: {len(all_variables)}")
            print(f"Total equations in model: {len(all_equations)}")
            
            if all_variables:
                print("\nFirst 5 variables:")
                for i, (var_id, var) in enumerate(list(all_variables.items())[:5]):
                    print(f"  {i + 1}. {var_id} (type: {type(var)})")
                    if hasattr(var, 'get_variables'):
                        print(f"     Has get_variables() method")
            
            if all_equations:
                print("\nFirst 5 equations:")
                for i, (eq_id, eq) in enumerate(list(all_equations.items())[:5]):
                    print(f"  {i + 1}. {eq_id} (type: {type(eq)})")
                    if hasattr(eq, 'lhs') and eq.lhs:
                        print(f"     LHS: {eq.lhs}")

            # Create and show the full EntityEditor
            print("Creating EntityEditor...")
            from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_editor import EntityEditorModel
            from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_editor import EntityEditorView
            from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.entity_editor import EntityEditorController
            
            print("Creating EntityEditor components...")
            # Create the model, view, and controller for the entity editor
            editor_model = EntityEditorModel(entity_obj, all_variables, all_equations)
            editor_view = EntityEditorView(editor_model, self._view)
            editor_controller = EntityEditorController(editor_model, editor_view)
            
            print("Showing editor dialog...")
            result = editor_view.exec_()

            if result == QtWidgets.QDialog.Accepted:
                print("Dialog accepted, updating entity...")

                # Update the model and refresh the view
                if hasattr(self, '_current_entity_id') and self._current_entity_id:
                    # Get the current index before any updates
                    current_index = self._view.ui.tree_entities.currentIndex()

                    # Force a complete refresh of the tree model
                    if hasattr(self._model, '_update_tree_model'):
                        self._model._update_tree_model()

                    # Reselect the current entity
                    self._select_entity_in_tree(self._current_entity_id)

                    # Force an update of the entity data display
                    if current_index.isValid():
                        self._on_tree_selection_changed(current_index, QtCore.QModelIndex())

                    print("Entity view updated successfully")
                else:
                    print("No current entity ID found to update")
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
