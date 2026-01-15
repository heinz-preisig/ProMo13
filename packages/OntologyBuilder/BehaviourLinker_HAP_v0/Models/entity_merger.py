import os
from typing import Dict

from PyQt5 import QtCore

from Common.classes import io
from Common.classes import equation
from Common.classes import variable
from Common.classes import entity

from Common import resource_initialisation

from OntologyBuilder.BehaviourLinker.Models import image_list


class EntityMergerModel(QtCore.QObject):
  variableChanged = QtCore.pyqtSignal(str)
  newDataLoaded = QtCore.pyqtSignal(bool)
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
    self.var_id = None

    self.equations_model = image_list.ImageListModel()

  def get_next_conflict(self):
    data = self.editing_entity.get_conflict()
    self._update_models(data)

    return data

  def solve_conflict(self, index):
    self.editing_entity.solve_conflict(self.var_id, index.data())

  def undo(self):
    data = self.editing_entity.undo_merging_step()
    self._update_models(data)

  def _update_models(self, data):
    if data is None:
      return

    self.var_id, assigned_equations = data

    # TODO: Remove this when the entity has instances of equations
    assigned_equations = [self.all_equations[eq_id]
                          for eq_id in assigned_equations]

    conflict_variable = self.all_variables[self.var_id]

    self.equations_model.load_data(assigned_equations)
    self.variableChanged.emit(conflict_variable.get_img_path())
    self.newDataLoaded.emit(self.editing_entity.is_undo_merge_possible())
