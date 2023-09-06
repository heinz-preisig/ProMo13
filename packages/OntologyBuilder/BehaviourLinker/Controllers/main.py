from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from packages.Common.classes import file_io

from packages.OntologyBuilder.BehaviourLinker.Views.main import MainView
from packages.OntologyBuilder.BehaviourLinker.Models.main import MainModel
from packages.OntologyBuilder.BehaviourLinker.Delegates.image_list import ImageItemDelegate

from packages.OntologyBuilder.BehaviourLinker.Views.ontology_selector import OntologySelectorView

from packages.OntologyBuilder.BehaviourLinker.Views.entity_generator import EntityGeneratorView
from packages.OntologyBuilder.BehaviourLinker.Controllers.entity_generator import EntityGeneratorController

from packages.OntologyBuilder.BehaviourLinker.Views.entity_editor import EntityEditorView
from packages.OntologyBuilder.BehaviourLinker.Controllers.entity_editor import EntityEditorController

from packages.OntologyBuilder.BehaviourLinker.Views.entity_merger import EntityMergerView
from packages.OntologyBuilder.BehaviourLinker.Controllers.entity_merger import EntityMergerController


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
        self._view.ui.list_pending
    ]

    for view, model in zip(entity_views, self._model.entity_list_models):
      view.setModel(model)
      delegate = ImageItemDelegate(view)
      view.setItemDelegate(delegate)

    # Connections from the View
    self._view.show_event_triggered.connect(self.on_show_event_triggered)
    self._view.ui.tree_entities.selectionModel().currentChanged.connect(
        self._model.load_entity
    )
    self._view.ui.tree_entities.selectionModel().currentChanged.connect(
        self._view.menu_items_state
    )
    self._view.ui.actionNew.triggered.connect(self.on_action_new_triggered)
    self._view.ui.tree_entities.doubleClicked.connect(
        self.on_tree_double_clicked)
    self._view.ui.actionEdit.triggered.connect(self.edit_entity)
    self._view.ui.actionDelete.triggered.connect(self.delete_entity)
    self._view.ui.actionSave.triggered.connect(self._model.save)
    # Connections from the Model
    self._model.tree_changed.connect(self._view.on_tree_changed)

  def on_show_event_triggered(self):
    """Launches a Dialog to get the ontology name.

    If the Dialog gets accepted it updates the model with the ontology
    name.
    """
    dlg = OntologySelectorView(
        file_io.get_available_ontologies(),
        self._view
    )

    result = dlg.exec_()
    if result == QtWidgets.QDialog.Accepted:
      ontology_name = dlg.ui.list_ontologies.currentIndex().data()
      self._model.load_ontology(ontology_name)

  def on_action_new_triggered(self):
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
          dlg_merge_model, dlg_merge_view)

      result = dlg_merge_view.exec_()

    index = self._model.entity_tree_model.index_from_path(new_entity_id)
    self._view.ui.tree_entities.setCurrentIndex(index)

    self.edit_entity()

  def edit_entity(self):
    index = self._view.ui.tree_entities.currentIndex()
    dlg_model = self._model.get_entity_editor_model(index)
    dlg_view = EntityEditorView(dlg_model, self._view)
    dlg_controller = EntityEditorController(dlg_model, dlg_view)

    result = dlg_view.exec_()
    if result == QtWidgets.QDialog.Accepted:
      self._model.update_entity(index, dlg_model.editing_entity)

  def delete_entity(self):
    # TODO: Maybe add safeguard.
    index = self._view.ui.tree_entities.currentIndex()
    self._model.delete_entity(index)

  def on_tree_double_clicked(self, index: QtCore.QModelIndex):
    if self._model.is_a_leaf(index):
      self.edit_entity()
