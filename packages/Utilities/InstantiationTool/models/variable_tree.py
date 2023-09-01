from typing import List, Dict
from pprint import pprint as pp

from PyQt5 import QtGui
from PyQt5 import QtCore

from packages.Common.classes import variable


class VariableTreeModel(QtGui.QStandardItemModel):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.all_variables = {}
    self._id_to_index: Dict[str, QtGui.QStandardItem] = {}

  def load_data(
      self,
      all_variables: Dict[str, variable.Variable] = {},
      filtered_list: List[str] = [],
  ) -> None:
    self.clear()
    self._id_to_index.clear()

    self.all_variables = all_variables

    for var_id in filtered_list:
      child_item = QtGui.QStandardItem(var_id)
      png_path = self.all_variables.get(var_id).get_img_path()
      child_item.setData(png_path, QtCore.Qt.UserRole)
      # child_item.setCheckable(True)
      # child_item.setCheckState(Qt.Unchecked)
      self.appendRow(child_item)

      self._id_to_index[var_id] = self.indexFromItem(child_item)

    # def flags(self, index):
    #   flags = super().flags(index)
    #   if self.get_depth(index) != LEAF_DEPTH:
    #     flags &= ~QtCore.Qt.ItemIsSelectable
    #     flags &= QtCore.Qt.NoFocus
    #   return flags
