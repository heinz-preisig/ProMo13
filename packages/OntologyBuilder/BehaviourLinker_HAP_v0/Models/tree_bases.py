from typing import List
from PyQt5 import QtGui
from PyQt5 import QtCore

from pprint import pprint as pp


class TreeBasesModel(QtGui.QStandardItemModel):
  def __init__(self, parent=None):
    super().__init__(parent)

  def load_data(self, data):
    self.clear()
    # Dictionary for fast lookup of the tree path from an index and
    # viceversa.
    self._index_to_path = {}
    self._path_to_index = {}

    # Dictionary for fast lookup of existing items in the tree.
    items = {}

    root = self.invisibleRootItem()

    for path in data:
      parent = root
      path_nodes = path.split('.')
      tokens = path_nodes[2].split("|")[0]
      subpath = [tokens, path_nodes[-1]]

      # print(subpath)
      for i, node in enumerate(subpath):
        # Each item is stored in the lookup dict using the tree path.
        key = '.'.join(subpath[:i+1])
        child = items.get(key)

        # If the item does not exist yet a new one is created.
        if child is None:
          child = QtGui.QStandardItem(node)
          child.setEditable(False)
          parent.appendRow(child)
          items[key] = child

        parent = child

      # For the fast lookups
      index = self.indexFromItem(child)
      self._index_to_path[index] = path
      self._path_to_index[path] = index

    # pp(self._index_to_path)

  def flags(self, index):
    flags = super().flags(index)
    root_index = self.indexFromItem(self.invisibleRootItem())

    if index.parent() == root_index:
      flags &= ~QtCore.Qt.ItemIsSelectable
      flags &= QtCore.Qt.NoFocus
    return flags

  def index_from_path(self, path):
    return self._path_to_index.get(path)

  def path_from_index(self, index):
    return self._index_to_path.get(index)
