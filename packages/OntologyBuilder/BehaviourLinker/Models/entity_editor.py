import os
from typing import Dict

from PyQt5 import QtCore

from packages.Common.classes import io
from packages.Common.classes import equation
from packages.Common.classes import variable
from packages.Common.classes import entity

from packages.Common import resource_initialisation

from packages.OntologyBuilder.BehaviourLinker.Models.variable_editor import VariableEditorModel
from packages.OntologyBuilder.BehaviourLinker.Models import image_list


class EntityEditorModel(QtCore.QObject):
  variableChecked = QtCore.pyqtSignal(bool)

  # Methods
  def __init__(
      self,
      editing_entity: entity.Entity,
      all_variables: Dict[str, variable.Variable],
      all_equations: Dict[str, equation.Equation],
  ):
    super().__init__()
    self.editing_entity = editing_entity
    self.all_variables = all_variables
    self.all_equations = all_equations

    self.variables_model = image_list.ImageListModel()
    self.equations_model = image_list.ImageListModel()

    self.view_all = True

    self.update_variables_model()
    self.update_equations_model()

  def on_view_all_changed(self, view_all: bool):
    self.view_all = view_all
    self.update_variables_model()

  def update_variables_model(self):
    entity_variables = self.editing_entity.get_variables()
    pending_variables = self.editing_entity.get_pending_vars()

    if not self.view_all:
      entity_variables = pending_variables

    # TODO: Remove this when the entity stores objects instead of strings
    entity_variables = [self.all_variables[var_id]
                        for var_id in entity_variables]
    pending_variables = [self.all_variables[var_id]
                         for var_id in pending_variables]

    self.variables_model.load_data(entity_variables, pending_variables)

  def update_equations_model(self):
    entity_equations = self.editing_entity.get_equations()
    # TODO: Remove this when the entity stores objects instead of strings
    entity_equations = [self.all_equations[eq_id]
                        for eq_id in entity_equations]
    self.equations_model.load_data(entity_equations)

  def get_variable_editor_model(self, index):
    var_id = index.data()
    return VariableEditorModel(
        self.editing_entity,
        self.all_variables[var_id],
        self.all_variables,
        self.all_equations,
    )

  def check_variable(self, index):
    var_id = index.data()
    is_top_level = self.editing_entity.is_var_top_level(var_id)
    self.variableChecked.emit(is_top_level)

  def changes_from_delete_var(self, index):
    var_id = index.data()

    self.editing_entity.set_output_var(var_id, False)

    changes = self.editing_entity.generate_var_eq_forest({})
    # TODO: Remove when the entity contain instances instead of str
    changes[0] = [self.all_variables[var_id] for var_id in changes[0]]
    changes[2] = [self.all_variables[var_id] for var_id in changes[2]]
    changes[1] = [self.all_equations[eq_id] for eq_id in changes[1]]
    changes[3] = [self.all_equations[eq_id] for eq_id in changes[3]]

    self.editing_entity.set_output_var(var_id, True)

    return changes

  def accept_changes(self, index):
    var_id = index.data()

    self.editing_entity.set_output_var(var_id, False)
    self.editing_entity.set_init_var(var_id, False)

    self.editing_entity.update_var_eq_tree()

    self.update_variables_model()
    self.update_equations_model()

  def get_unused_variables(self):
    ent_type = self.editing_entity.entity_name.split(".")[1]
    all_vars = {
        var_id
        for var_id, var in self.all_variables.items()
        if var.is_eligible("", ent_type, "")
    }
    entity_vars = set(self.editing_entity.get_variables())
    # TODO Change when the entity has var instances.
    unused_vars = [self.all_variables[var_id]
                   for var_id in sorted(list(all_vars - entity_vars))]

    return unused_vars

  def add_new_output_var(self, var_id):
    self.editing_entity.set_output_var(var_id, True)
    self.editing_entity.generate_var_eq_forest({var_id: []})
    self.editing_entity.update_var_eq_tree()

    self.update_variables_model()
    item = self.variables_model.findItems(var_id)[0]

    return self.variables_model.indexFromItem(item)
