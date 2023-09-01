import os
import copy
import logging
from typing import Dict, List, Optional

from PyQt5 import QtCore

from packages.Common.classes import io
from packages.Common.classes import entity
from packages.Common.classes import modeller_classes

from packages.Utilities.InstantiationTool.models import variable_tree
from packages.Utilities.InstantiationTool.models import topology_tree


class InvalidEntityError(Exception):
  """The entity doesn't exist"""
  pass


class MainModel(QtCore.QObject):
  # Signals
  variable_tree_changed = QtCore.pyqtSignal()
  topology_tree_changed = QtCore.pyqtSignal()

  # Methods
  def __init__(self):
    super().__init__()

    self.ontology_name = None
    self.all_entities = None
    self.all_variables = None
    self.all_equations = None  # TODO: Check if I really need to store this
    self.all_indices = None
    self.topology_objects = None

    self.required_variables = []
    self.optional_variables = []

    self.variable_tree_model = variable_tree.VariableTreeModel()
    self.topology_tree_model = topology_tree.TopologyTreeModel()

    self.variable_filter_string = None
    self.variable_show_uninstantiated_only = False

  def load_ontology(self, ontology_name: str, model_name: str) -> None:
    self.ontology_name = ontology_name

    var_idx_eq = io.load_var_idx_eq_from_file(ontology_name)
    self.all_variables, self.all_indices, self.all_equations = var_idx_eq

    self.all_entities = io.load_entities_from_file(
        self.ontology_name,
        self.all_equations
    )
    self.topology_objects = io.load_model_from_file(
        ontology_name,
        model_name,
        self.all_entities,
    )
    self._discover_required_variables()
    self._update_variable_tree_model()

    if self.required_variables:
      self._update_topology_tree_model(self.required_variables[0])

  def _discover_required_variables(self):
    used_entities: Dict[str, entity.Entity] = {}
    for top_obj_id, top_obj in self.topology_objects.items():
      # Composite nodes dont have an associated entity
      if isinstance(top_obj, modeller_classes.NodeComposite):
        continue

      ent_name = top_obj.get_entity_name()
      # TODO: Move this and the test case to io.load_model
      if ent_name not in self.all_entities:
        raise InvalidEntityError

      used_entities.setdefault(ent_name, self.all_entities[ent_name])

    required_variables = set()
    for ent in used_entities.values():
      required_variables.update(ent.get_init_vars())

    self.required_variables = sorted(required_variables)

  def _update_variable_tree_model(self):
    filtered_list = self._filter_variables()
    self.variable_tree_model.load_data(self.all_variables, filtered_list)
    self.variable_tree_changed.emit()

  def _filter_variables(self) -> List[str]:
    # TODO: Implement this
    filtered_list = self.required_variables
    return filtered_list

  def on_variables_selected(self, selected: QtCore.QItemSelection) -> None:
    selected_indexes = selected.indexes()
    var_list = [index.data() for index in selected_indexes]
    self._update_topology_tree_model(var_list)

  def _update_topology_tree_model(self, var_list: List[str]):
    filtered_list = self._filter_topology_objects(var_list)
    self.topology_tree_model.load_data(self.topology_objects, filtered_list)
    self.topology_tree_changed.emit()

  def _filter_topology_objects(self, var_list: List[str]) -> List[str]:
    # TODO: Add filtering for checkbox and searchbar
    filtered_topology_objects = set()
    for var_id in var_list:
      for top_obj_id, top_obj in self.topology_objects.items():
        if isinstance(top_obj, modeller_classes.NodeComposite):
          continue
        # print(top_obj_id)
        # print(top_obj.get_entity_name())
        if top_obj.contains_init_var(var_id):
          filtered_topology_objects.add(top_obj_id)

    return sorted(filtered_topology_objects)
