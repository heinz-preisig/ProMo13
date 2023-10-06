import copy

from PyQt5 import QtCore

from packages.Common.classes import entity
from packages.Common.classes import io
from packages.OntologyBuilder.BehaviourLinker.Models import entity_editor
from packages.OntologyBuilder.BehaviourLinker.Models import entity_generator
from packages.OntologyBuilder.BehaviourLinker.Models import image_list
from packages.OntologyBuilder.BehaviourLinker.Models import tree
from packages.OntologyBuilder.BehaviourLinker.Models.entity_merger import EntityMergerModel


class MainModel(QtCore.QObject):
  # Signals
  tree_changed = QtCore.pyqtSignal()

  # Methods
  def __init__(self):
    super().__init__()
    self.ontology_name = None
    self.ontology = None
    self.all_entities = None
    self.all_variables = None
    self.all_equations = None

    # PyQt models
    self.entity_tree_model = tree.TreeModel()
    self.entity_list_models = [
        image_list.ImageListModel(self),  # Integrators
        image_list.ImageListModel(self),  # Equations
        image_list.ImageListModel(self),  # Input_vars
        image_list.ImageListModel(self),  # Output_vars
        image_list.ImageListModel(self),  # Init_vars
        image_list.ImageListModel(self),  # Pending_vars
    ]

  def load_ontology(self, ontology_name):
    self.ontology_name = ontology_name

    # TODO: Remove when this is done in the equation composer
    io.generate_latex_images(ontology_name)

    # Loading data from files
    self.ontology = io.load_ontology_from_file(self.ontology_name)
    self.all_variables, _, self.all_equations = io.load_var_idx_eq_from_file(
        self.ontology_name
    )
    self.all_entities = io.load_entities_from_file(
        self.ontology_name,
        self.all_equations
    )

    self._update_tree_model()

  def load_entity(self, index: QtCore.QModelIndex):
    if not index.isValid():
      entity_data = [[]]*6
      self._update_entity_models(entity_data)
      return

    entity_id = self.entity_tree_model.path_from_index(index)

    current_entity = self.all_entities.get(entity_id)
    if current_entity is None:
      # TODO: Maybe make an exception here
      return False

    entity_data = [
        [self.all_equations[eq_id]
         for eq_id in current_entity.get_integrators_eq()],
        [self.all_equations[eq_id]
         for eq_id in current_entity.get_equations()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_input_vars()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_output_vars()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_init_vars()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_pending_vars()],
    ]
    self._update_entity_models(entity_data)

  def _update_entity_models(self, entity_data):
    for model, data in zip(self.entity_list_models, entity_data):
      model.load_data(data)

  def _update_tree_model(self):
    self.entity_tree_model.load_data(self.all_entities.keys())
    self.tree_changed.emit()

  def get_entity_generator_model(self):
    return entity_generator.EntityGeneratorModel(
        self.ontology,
        list(self.all_entities.keys())
    )

  def get_entity_editor_model(self, index):
    entity_id = self.entity_tree_model.path_from_index(index)
    return entity_editor.EntityEditorModel(
        copy.deepcopy(self.all_entities[entity_id]),
        self.all_variables,
        self.all_equations,
    )

  def add_entity(self, new_entity_id, bases):
    new_entity = None
    number_of_bases = len(bases)

    if number_of_bases == 1:
      new_entity = copy.deepcopy(self.all_entities[bases[0]])
    else:
      new_entity = entity.Entity(new_entity_id, self.all_equations)

    self.all_entities[new_entity_id] = new_entity
    self._update_tree_model()

    if number_of_bases > 1:
      base_entities = [self.all_entities[b] for b in bases]
      merge_completed = new_entity.start_merging_process(base_entities)
      if not merge_completed:
        return EntityMergerModel(new_entity, self.all_variables, self.all_equations)

    return None

  def update_entity(self, index, updated_entity):
    entity_id = self.entity_tree_model.path_from_index(index)
    if updated_entity != self.all_entities[entity_id]:
      self.all_entities[entity_id] = updated_entity
      self.load_entity(index)

  def delete_entity(self, index):
    entity_id = self.entity_tree_model.path_from_index(index)
    del self.all_entities[entity_id]
    # self.entity_tree_model.remove_element(index)
    self._update_tree_model()
    self.load_entity(QtCore.QModelIndex())

  def is_a_leaf(self, index):
    return self.entity_tree_model.get_depth(index) == tree.LEAF_DEPTH

  def save(self):
    io.save_entities_to_file(self.ontology_name, self.all_entities)
