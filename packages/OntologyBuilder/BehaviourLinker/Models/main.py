import copy
from typing import Optional

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

    self._update_interfaces()

    self._update_tree_model()

  def _update_interfaces(self):
    interface_entities = [
      ent
      for ent_name, ent in self.all_entities.items()
      if ent.is_interface_ent()
    ]
    interface_equations = {
      eq_id
      for eq_id, eq in self.all_equations.items()
      if eq.is_interface_eq()
    }

    for ent in interface_entities:
      main_eq_id = ent.get_equations()[0]

      # Delete the entity if there is not an interface equation
      if main_eq_id not in interface_equations:
        del self.all_entities[ent.entity_name]
        continue

      # TODO: Check for modification dates to see if the entity needs to be updated.
      update_needed = True
      if update_needed:
        new_ent = self.create_entity_from_eq(main_eq_id, ent)
        self.all_entities[ent.entity_name] = new_ent

      interface_equations.remove(main_eq_id)

    for eq_id in interface_equations:
      new_ent = self.create_entity_from_eq(eq_id)
      self.all_entities[new_ent.entity_name] = new_ent

    io.save_entities_to_file(self.ontology_name, self.all_entities)

  def create_entity_from_eq(
      self,
      eq_id: str,
      base_entity: Optional[entity.Entity] = None,
  ) -> entity.Entity:

    eq = self.all_equations[eq_id]

    output_var_id = eq.get_main_var_id()
    input_var_id = eq.get_incidence_list(output_var_id)[0]

    if base_entity is None:
      output_var_alias = self.all_variables[output_var_id].get_alias("internal_code")
      input_var_alias = self.all_variables[input_var_id].get_alias("internal_code")

      new_ent = entity.Entity(
        f"{eq.network} ({input_var_alias} -> {output_var_alias})",
        self.all_equations,
      )
    else:
      new_ent = entity.Entity(
          base_entity.entity_name,
          self.all_equations,
          base_entity.index_set,
        )

    new_ent.set_input_var(input_var_id, True)
    new_ent.set_output_var(output_var_id, True)
    new_ent.generate_var_eq_forest({output_var_id: [eq_id]})
    new_ent.update_var_eq_tree()

    return new_ent




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
