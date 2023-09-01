from dataclasses import dataclass
from typing import List, Dict, Optional
from pprint import pprint as pp

from PyQt5 import QtGui
from PyQt5 import QtCore

from packages.Common.classes import modeller_classes

NAME_ROLE = QtCore.Qt.UserRole
CLASS_ROLE = QtCore.Qt.UserRole + 1


class TopologyTreeModel(QtGui.QStandardItemModel):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.topology_objects: Dict[str, modeller_classes.TopologyObject] = {}
    self.var_id: str = ""
    self.typed_token: Optional[str] = ""
    self._id_to_index: Dict[str, QtCore.QModelIndex] = {}
    self._index_to_id: Dict[QtCore.QModelIndex, str] = {}

    self.flag_propagation_allowed = True
    self.setColumnCount(2)
    self.setHorizontalHeaderLabels(["Name", "Value"])

    self.itemChanged.connect(self.propagate_check_state)

  def empty_model(self):
    self.removeRows(0, self.rowCount())
    self._id_to_index.clear()
    self._index_to_id.clear()

  def load_data(
      self,
      topology_objects: Dict[str, modeller_classes.TopologyObject],
      filtered_list: List[str],
  ) -> None:
    """Loads the data into the model

    Load the model with items created using the data stored in the
    dictionary passed as argument. Previous items are deleted before the
    new ones are added.

    Args:
        components_data (Dict[str, Dict[str, str]]): Contains the data
          required to intialize each of the items that will be added to
          the model.
    """
    self.empty_model()

    self.components_data = components_data

    for item_id in self.components_data:
      self.add_ancestors(item_id)
      self.add_item(item_id)

  def add_ancestors(self, item_id: str) -> None:
    """Adds the ancestors of the item to the model

    This recursive function makes sure that the ancestors are always
    added to the model before their descendants. It will add all the
    items from the item represented by item_id to the root of the model
    as long as they are not already on the model.

    Args:
        item_id (str): Identifier of the item whose ancestors are being
                         added.
    """
    item_data = self.components_data.get(item_id)
    parent_id = item_data.get("parent")

    if parent_id not in self._id_to_index and parent_id is not None:
      self.add_ancestors(parent_id)
      self.add_item(parent_id)

  def add_item(self, item_id: str) -> None:
    """Adds an item to the model

    In the case where the item to add doesnt belong to the NodeComposite
    class, a second item is also added in the same row as the main item
    but in the second column. This item contains the instantiation value
    corresponding to the data of the item represented by item_id.

    The dictionaries _id_to_index and _index_to_id are populated after
    the item has been added.

    Args:
        item_id (str): Identifier of the item that is being added.
    """
    pp(self.topology_objects)
    main_item = QtGui.QStandardItem()
    main_item.setCheckable(True)
    main_item.setAutoTristate(True)

    item_obj = self.topology_objects.get(item_id)

    parent_id = item_obj.get_parent_id()
    main_item.setData(item_obj.get_name(), NAME_ROLE)
    main_item.setData(item_obj.get_modeller_class(), CLASS_ROLE)

    if parent_id is None:
      parent_item = self.invisibleRootItem()
    else:
      parent_index = self._id_to_index.get(parent_id)
      parent_item = self.itemFromIndex(parent_index)

    if isinstance(item_obj, modeller_classes.NodeComposite):
      parent_item.appendRow(main_item)
    else:
      instantiation_value = item_obj.get_instantiation_value(
          self.var_id, self.typed_token)
      if instantiation_value is None:
        instantiation_value = "--"

      print(instantiation_value)
      instantiation_item = QtGui.QStandardItem(instantiation_value)
      parent_item.appendRow([main_item, instantiation_item])

    main_item_index = self.indexFromItem(main_item)
    self._id_to_index[item_id] = main_item_index
    self._index_to_id[main_item_index] = item_id

  def propagate_check_state(self, item: QtGui.QStandardItem):
    if self.flag_propagation_allowed:
      self.flag_propagation_allowed = False
      self.propagate_check_state_down(item)

      if item.parent() is not None:
        self.propagate_check_state_up(item.parent())
      self.flag_propagation_allowed = True

  def propagate_check_state_down(self, item: QtGui.QStandardItem):
    check_state = item.checkState()
    for row in range(item.rowCount()):
      child_item = item.child(row)
      child_item.setCheckState(check_state)
      self.propagate_check_state_down(child_item)

  def propagate_check_state_up(self, item: QtGui.QStandardItem):
    any_checked = False
    any_unchecked = False
    any_partially_checked = False
    for row in range(item.rowCount()):
      child_item = item.child(row)
      if child_item.checkState() == QtCore.Qt.CheckState.Checked:
        any_checked = True
      if child_item.checkState() == QtCore.Qt.CheckState.Unchecked:
        any_unchecked = True
      if child_item.checkState() == QtCore.Qt.CheckState.PartiallyChecked:
        any_partially_checked = True

    if any_partially_checked or (any_checked and any_unchecked):
      item.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
    elif not any_checked:
      item.setCheckState(QtCore.Qt.CheckState.Unchecked)
    elif not any_unchecked:
      item.setCheckState(QtCore.Qt.CheckState.Checked)

    if item.parent() is not None:
      self.propagate_check_state_up(item.parent())

  #     # Dictionary for fast lookup of the tree path from an index and
  #     # viceversa.
  #   self._index_to_path = {}
  #   self._path_to_index = {}

  #   # Dictionary for fast lookup of existing items in the tree.
  #   items = {}

  #   root = self.invisibleRootItem()

  #   for path in data:
  #     parent = root
  #     path_nodes = path.split('.')

  #     for i, node in enumerate(path_nodes):
  #       # Each item is stored in the lookup dict using the tree path.
  #       key = '.'.join(path_nodes[:i+1])
  #       child = items.get(key)

  #       # If the item does not exist yet a new one is created.
  #       if child is None:
  #         child = QtGui.QStandardItem(node)
  #         child.setEditable(False)
  #         parent.appendRow(child)
  #         items[key] = child
  #         # For the fast lookups
  #         index = self.indexFromItem(child)
  #         self._index_to_path[index] = key
  #         self._path_to_index[key] = index

  #       parent = child

  #   # pp(self._index_to_path)

  # def get_depth(self, index):
  #   """Gets how deep in the tree an item is.

  #   Depth is defined as how many nodes are between the current item and
  #   the top level items. The depth of top level items is 0.

  #   We use a lookup dict to find the path linked to an item. Then we can
  #   easily find the depth from the number of nodes in the path.

  #   Args:
  #       index (QModelIndex): index of the item we are querying for.

  #   Returns:
  #       Optional[int]: if the index is valid returns the depth of the
  #         item. Otherwise it returns None.
  #   """
  #   path = self._index_to_path.get(index)

  #   if path is None:
  #     return None

  #   return len(path.split(".")) - 1

  # def flags(self, index):
  #   flags = super().flags(index)
  #   if self.get_depth(index) != LEAF_DEPTH:
  #     flags &= ~QtCore.Qt.ItemIsSelectable
  #     flags &= QtCore.Qt.NoFocus
  #   return flags

  # def index_from_path(self, path):
  #   return self._path_to_index.get(path)

  # def path_from_index(self, index):
  #   return self._index_to_path.get(index)

  # def remove_element(self, index: QtCore.QModelIndex):
  #   item = self.itemFromIndex(index)
  #   parent = item.parent()

  #   if parent is not None:
  #     parent.removeRow(item.row())
  #     if parent.rowCount() == 0:
  #       self.remove_element(parent.index())

  #   path = self._index_to_path.pop(index, None)
  #   if path is not None:
  #     self._path_to_index.pop(path, None)
