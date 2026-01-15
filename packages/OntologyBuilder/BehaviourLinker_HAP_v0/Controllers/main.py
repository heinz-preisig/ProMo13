import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot

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
        
        # Connect selection changed signal with debug logging
        selection_model = self._view.ui.tree_entities.selectionModel()
        
        # Disconnect any existing connections to avoid duplicates
        try:
            selection_model.currentChanged.disconnect()
        except TypeError:
            # No connections to disconnect
            pass
            
        # Add debug prints to track signal emissions
        def debug_selection_changed(current, previous):
            print(f"\n=== Selection Changed ===")
            print(f"Previous: {previous.row()}, {previous.column()} - Valid: {previous.isValid()}")
            print(f"Current: {current.row()}, {current.column()} - Valid: {current.isValid()}")
            
            # Call load_entity first
            try:
                print("Calling _model.load_entity...")
                self._model.load_entity(current)
            except Exception as e:
                print(f"Error in load_entity: {e}")
                import traceback
                traceback.print_exc()
            
            # Then update menu state
            try:
                print("Updating menu state...")
                self._view.menu_items_state(current)
            except Exception as e:
                print(f"Error in menu_items_state: {e}")
                import traceback
                traceback.print_exc()
        
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
        """Starts the process to create a new Entity.

        The process consists of two parts.
          1. Generates a new entity by selecting type, network, token(s),
            mechanism, nature and finally a name. At the end an entity id is
            created based on the decisions made.
          2. The newly created entity is edited to add the required
            variables and equations.
        """
        dlg_gen_model = self._model.get_entity_generator_model()
        dlg_gen_view = EntityGeneratorView(dlg_gen_model, self._view)
        dlg_gen_controller = EntityGeneratorController(dlg_gen_model, dlg_gen_view)

        result = dlg_gen_view.exec_()
        if result == QtWidgets.QDialog.Rejected:
            return

        new_entity_id = dlg_gen_model.new_entity_id
        all_bases = dlg_gen_model.summary.stringList()[5]
        bases = []
        if all_bases != "":
            bases = all_bases.split("*")

        dlg_merge_model = self._model.add_entity(new_entity_id, bases)
        if dlg_merge_model is not None:
            dlg_merge_view = EntityMergerView(dlg_merge_model, self._view)
            dlg_merge_controller = EntityMergerController(
                dlg_merge_model, dlg_merge_view
            )

            result = dlg_merge_view.exec_()

        index = self._model.entity_tree_model.index_from_path(new_entity_id)
        self._view.ui.tree_entities.setCurrentIndex(index)

        self.edit_entity()

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
        if self._model.is_a_leaf(index):
            self.edit_entity()
