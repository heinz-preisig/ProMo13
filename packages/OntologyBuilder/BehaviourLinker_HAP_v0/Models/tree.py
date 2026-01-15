from typing import List
from PyQt5 import QtGui
from PyQt5 import QtCore

from pprint import pprint as pp

LEAF_DEPTH = 3


class TreeModel(QtGui.QStandardItemModel):
  def __init__(self, parent=None):
    super().__init__(parent)
    # Initialize dictionaries for path-index mapping
    self._index_to_path = {}
    self._path_to_index = {}

  def load_data(self, data):
    self.clear()
    # Clear existing mappings
    self._index_to_path.clear()
    self._path_to_index.clear()

    # Dictionary for fast lookup of existing items in the tree.
    items = {}

    root = self.invisibleRootItem()

    for path in data:
      parent = root
      path_nodes = path.split('.')

      for i, node in enumerate(path_nodes):
        # Each item is stored in the lookup dict using the tree path.
        key = '.'.join(path_nodes[:i+1])
        child = items.get(key)

        # If the item does not exist yet a new one is created.
        if child is None:
          child = QtGui.QStandardItem(node)
          child.setEditable(False)
          parent.appendRow(child)
          items[key] = child
          # For the fast lookups
          index = self.indexFromItem(child)
          self._index_to_path[index] = key
          self._path_to_index[key] = index

        parent = child

    # pp(self._index_to_path)

  def get_depth(self, index):
    """Gets how deep in the tree an item is.

    Depth is defined as how many nodes are between the current item and
    the top level items. The depth of top level items is 0.

    We use a lookup dict to find the path linked to an item. Then we can
    easily find the depth from the number of nodes in the path.

    Args:
        index (QModelIndex): index of the item we are querying for.

    Returns:
        Optional[int]: if the index is valid returns the depth of the
          item. Otherwise it returns None.
    """
    path = self._index_to_path.get(index)

    if path is None:
      return None

    return len(path.split(".")) - 1

  def flags(self, index):
    flags = super().flags(index)
    if self.get_depth(index) != LEAF_DEPTH:
      flags &= ~QtCore.Qt.ItemIsSelectable
      flags &= QtCore.Qt.NoFocus
    return flags

  def index_from_path(self, path):
    return self._path_to_index.get(path)

  def path_from_index(self, index):
    return self._index_to_path.get(index)

  def remove_element(self, index: QtCore.QModelIndex):
    item = self.itemFromIndex(index)
    parent = item.parent()

    if parent is not None:
      parent.removeRow(item.row())
      if parent.rowCount() == 0:
        self.remove_element(parent.index())

    path = self._index_to_path.pop(index, None)
    if path is not None:
      self._path_to_index.pop(path, None)
