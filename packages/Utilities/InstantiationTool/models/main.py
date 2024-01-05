import os
import copy
import logging
from typing import Dict, List, Optional, cast

from PyQt5 import QtCore

from packages.Common.classes import io
from packages.Common.classes import entity
from packages.Common.classes import modeller_classes

from packages.Utilities.InstantiationTool.models import variable_tree
from packages.Utilities.InstantiationTool.models import topology_tree

from pprint import pprint as pp


class InvalidEntityError(Exception):
  """The entity doesn't exist"""
  pass


class MainModel(QtCore.QObject):
  # Signals
  variable_tree_changed = QtCore.pyqtSignal()
  topology_tree_changed = QtCore.pyqtSignal()
  selection_changed = QtCore.pyqtSignal(bool)

  # Methods
  def __init__(self):
    super().__init__()

    self._ontology_name = ""
    self._model_name = ""
    self._all_entities = {}
    self._all_variables = {}
    self._all_equations = {}  # TODO: Check if I really need to store this
    self._all_indices = {}
    self._all_topology_objects = {}

    self._required_variables = []
    self._optional_variables = []

    # Possible typed tokens for each variable in the model.
    self._typed_tokens_per_variable = {}

    self.variable_tree_model = variable_tree.VariableTreeModel()
    self.topology_tree_model = topology_tree.TopologyTreeModel()

    # The selection state is store in these variables.
    self._is_variable_selected = False
    self._is_topology_object_selected = False

    self._variable_filter_string = None
    self._variable_show_uninstantiated_only = False

  def load_ontology_info(self, ontology_name: str, model_name: str) -> None:
    self._ontology_name = ontology_name
    self._model_name = model_name

    var_idx_eq = io.load_var_idx_eq_from_file(self._ontology_name)
    self._all_variables, self._all_indices, self._all_equations = var_idx_eq

    self._all_entities = io.load_entities_from_file(
        self._ontology_name,
        self._all_equations
    )
    self._all_topology_objects = io.load_model_from_file(
        self._ontology_name,
        self._model_name,
        self._all_entities,
    )
    self._discover_required_variables()
    self._update_variable_tree_model()

    # if self._required_variables:
    #   self._update_topology_tree_model(self._required_variables[0])

  def _discover_required_variables(self):
    used_entities: Dict[str, entity.Entity] = {}
    for top_obj in self._all_topology_objects.values():
      # Composite nodes dont have an associated entity
      if isinstance(top_obj, modeller_classes.NodeComposite):
        continue

      top_obj = cast(modeller_classes.EntityContainer, top_obj)

      ent_name = top_obj.get_entity_name()
      # TODO: Move this and the test case to io.load_model
      if ent_name not in self._all_entities:
        raise InvalidEntityError

      self._find_typed_tokens_per_variable(
          top_obj,
          self._all_entities[ent_name]
      )

      used_entities.setdefault(ent_name, self._all_entities[ent_name])

    required_variables = set()
    for ent in used_entities.values():
      required_variables.update(ent.get_init_vars())

    self._required_variables = sorted(required_variables)

  def _find_typed_tokens_per_variable(
      self,
      top_obj: modeller_classes.EntityContainer,
      ent: entity.Entity
  ) -> None:
    for var_id in ent.get_variables():
      # TODO: Extend to the other typed tokens
      if var_id not in self._typed_tokens_per_variable:
        self._typed_tokens_per_variable[var_id] = set()

      if "I_3" in self._all_variables[var_id].index_structures:
        self._typed_tokens_per_variable[var_id].update(
            set(top_obj.typed_tokens["mass"])
        )

  def _update_variable_tree_model(self):
    """Loads the necessary data into the model

    The list of variables is filtered and the result is loaded into the
    model. At the end a signal is emited to notify that the data in the
    model changed.
    """
    filtered_variables = {
        var_id: self._all_variables[var_id]
        for var_id in self._filter_variables()
    }

    self.variable_tree_model.load_data(
        filtered_variables,
        self._typed_tokens_per_variable
    )
    self.variable_tree_changed.emit()

  def _filter_variables(self) -> List[str]:
    # TODO: Implement this
    filtered_list = self._required_variables
    return filtered_list

  def on_variables_selected(
      self,
      index: QtCore.QModelIndex
  ) -> None:
    """Updates the checked status of the variable_tree_model.

    It also triggers an update on the topology_tree_model.
     See :meth:`_update_topology_tree_model`.

    Args:
        index (QtCore.QModelIndex): Index that triggers the update.
    """
    self.variable_tree_model.handle_check_state_change(index)

    selected_variables = self.variable_tree_model.get_checked_items()
    self._update_topology_tree_model(selected_variables)

    self._check_selection_status()

  def on_topology_tree_model_check_box_changed(self):
    # checked_items = self.topology_tree_model.get_checked_items()
    # self._is_topology_object_selected = bool(checked_items)

    self._check_selection_status()

  def _check_selection_status(self):
    is_variable_selected = bool(self.variable_tree_model.get_checked_items())
    is_topology_object_selected = bool(
        self.topology_tree_model.get_checked_items()
    )

    is_selection_complete = (is_variable_selected and
                             is_topology_object_selected)

    self.selection_changed.emit(is_selection_complete)

  def _update_topology_tree_model(
      self,
      variables_selected: Dict[str, List[str]],
  ) -> None:
    """Updates the topology tree model.

    The model is updated and only topology objects that contain at least
    one of the variables in the variable list passed as argument are 
    added. If the variable have any typed tokens selected, the topology
    objects also need to have at least one of the typed tokens to be
    included. 

    The filtering is done in :meth:`_filter_topology_objects`.

    Args:
        var_list (Dict[str,List[str]]): Variables used for filtering.
    """
    filtered_ids = self._filter_topology_objects(variables_selected)

    self.topology_tree_model.load_data(
        self._all_topology_objects, filtered_ids)
    self.topology_tree_changed.emit()

  def _filter_topology_objects(
      self,
      variables_selected: Dict[str, List[str]],
  ) -> List[str]:
    """Filters all_topology_objects

    The filtering is done at several levels. The main one uses a dict of
    variables and typed tokens to get only the topology objects that
    contain at least one of the variables with at least one of its typed
    tokens.

    Args:
        var_list (Dict[str, List[str]]): The keys are the variable ids.
         The valus are the corresponding typed tokens.

    Returns:
        List[str]: Ids of the Topology Objects that pass the filter.
    """
    # TODO: Add filtering for checkbox and searchbar
    filtered_topology_objects = set()
    for var_id, typed_tokens in variables_selected.items():
      for top_obj_id, top_obj in self._all_topology_objects.items():
        if isinstance(top_obj, modeller_classes.NodeComposite):
          continue

        top_obj = cast(modeller_classes.EntityContainer, top_obj)

        # If there are types tokens the topology object needs to contain
        # at least one of them
        if typed_tokens:
          typed_token_condition = bool(
              set(typed_tokens) & set(top_obj.typed_tokens["mass"])
          )
        else:
          typed_token_condition = True

        # Main filter: contains variable + typed token
        if top_obj.contains_init_var(var_id) and typed_token_condition:
          filtered_topology_objects.add(top_obj_id)

    return sorted(filtered_topology_objects)

  def instantiate(self, instantiation_value: str) -> None:
    instantiated_top_obj = self.topology_tree_model.get_checked_items()
    instantiated_variables = self.variable_tree_model.get_checked_items()

    for top_obj_id in instantiated_top_obj:
      for var_id, typed_tokens in instantiated_variables.items():
        top_obj = self._all_topology_objects[top_obj_id]
        top_obj = cast(modeller_classes.EntityContainer, top_obj)

        top_obj.set_instantiation_value(
            var_id,
            typed_tokens,
            instantiation_value
        )

    # for top_obj_id, top_obj in self._all_topology_objects.items():
    #   if isinstance(top_obj, modeller_classes.EntityContainer):
    #     pp(top_obj_id)
    #     pp(top_obj.instantiated_variables)

  def save_topology_objects(self):
    io.save_model_to_file(
        self._ontology_name,
        self._model_name,
        self._all_topology_objects,
    )
