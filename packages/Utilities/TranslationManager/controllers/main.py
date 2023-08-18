import os

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from views.main import MainView
from models.main import MainModel

# TODO: Remove this when integrating with the main program.
from dataclasses import dataclass
import json


@dataclass
class TranslationInfo:
  variable_with_index: str
  variable_no_index: str
  index: str
  addition: str
  substraction: str
  negation: str
  expand_product: str
  khatri_rao: str
  reduce_product: str
  block_reduce_product: str
  power: str
  parentheses: str
  exp: str
  log: str
  ln: str
  sqrt: str
  sin: str
  cos: str
  tan: str
  asin: str
  acos: str
  atan: str
  abs: str
  neg: str
  diffspace: str
  left: str
  right: str
  inv: str
  sign: str
  par_diff: str
  total_diff: str
  product: str
  integral: str


class MainController(QObject):
  def __init__(self, main_model: MainModel, main_view: MainView):
    super().__init__()

    self._model = main_model
    self._view = main_view

    view_files = self._view.ui.list_files
    # model_files = self._model.model_files

    # view_files.setModel(model_files)
    # delegate = ImageItemDelegate(view)
    # view.setItemDelegate(delegate)

    # Connections from the View
    self._view.show_event_triggered.connect(self.on_show_event_triggered)
    # Connections from the Model

  def on_show_event_triggered(self):
    """Launches a Dialog to get the ontology name.

    If the Dialog gets accepted it updates the model with the ontology
    name.
    """
    dlg = LanguageSelectorView(
        self.get_available_languages(),
        self._view
    )

    result = dlg.exec_()
    if result == QtWidgets.QDialog.Accepted:
      language_name = dlg.ui.list_languages.currentIndex().data()
      language_data = self.get_language_data(language_name)
      self._model.update_language_data(language_data)

  def get_available_languages(self):
    # TODO: Move this to the IO module. Probably merge it with the ontology one.
    location = "resources/language_configurations"
    directories = [
        f.path
        for f in os.scandir(location)
        if f.is_dir() and not f.name.startswith('.')
    ]
    language_names = [
        os.path.splitext(os.path.basename(o))[0]
        for o in directories
    ]

    return language_names

  def get_language_data(self, language_name: str):
    # TODO: Move this to the IO module. Probably merge it with the ontology one.
    path = f"resources/language_configurations/{language_name}"
    with open(path, "r", encoding="utf-8",) as file:
      data = json.load(file)

    language_data = TranslationInfo(**data)

    return language_data

    # def on_action_new_triggered(self):
    #   """Starts the process to create a new Entity.

    #   The process consists of two parts.
    #     1. Generates a new entity by selecting type, network, token(s),
    #       mechanism, nature and finally a name. At the end an entity id is
    #       created based on the decisions made.
    #     2. The newly created entity is edited to add the required
    #       variables and equations.
    #   """
    #   dlg_gen_model = self._model.get_entity_generator_model()
    #   dlg_gen_view = EntityGeneratorView(dlg_gen_model, self._view)
    #   dlg_gen_controller = EntityGeneratorController(dlg_gen_model, dlg_gen_view)

    #   result = dlg_gen_view.exec_()
    #   if result == QtWidgets.QDialog.Rejected:
    #     return

    #   new_entity_id = dlg_gen_model.new_entity_id
    #   all_bases = dlg_gen_model.summary.stringList()[5]
    #   bases = []
    #   if all_bases != "":
    #     bases = all_bases.split("*")

    #   dlg_merge_model = self._model.add_entity(new_entity_id, bases)
    #   if dlg_merge_model is not None:
    #     dlg_merge_view = EntityMergerView(dlg_merge_model, self._view)
    #     dlg_merge_controller = EntityMergerController(
    #         dlg_merge_model, dlg_merge_view)

    #     result = dlg_merge_view.exec_()

    #   index = self._model.entity_tree_model.index_from_path(new_entity_id)
    #   self._view.ui.tree_entities.setCurrentIndex(index)

    #   self.edit_entity()

    # def edit_entity(self):
    #   index = self._view.ui.tree_entities.currentIndex()
    #   dlg_model = self._model.get_entity_editor_model(index)
    #   dlg_view = EntityEditorView(dlg_model, self._view)
    #   dlg_controller = EntityEditorController(dlg_model, dlg_view)

    #   result = dlg_view.exec_()
    #   if result == QtWidgets.QDialog.Accepted:
    #     self._model.update_entity(index, dlg_model.editing_entity)

    # def delete_entity(self):
    #   # TODO: Maybe add safeguard.
    #   index = self._view.ui.tree_entities.currentIndex()
    #   self._model.delete_entity(index)

    # def on_tree_double_clicked(self, index: QtCore.QModelIndex):
    #   if self._model.is_a_leaf(index):
    #     self.edit_entity()
