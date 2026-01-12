from typing import List
from PyQt5 import QtGui
from PyQt5 import QtCore

from pprint import pprint as pp


class TreeBasesModel(QtGui.QStandardItemModel):
  def __init__(self, parent=None):
    super().__init__(parent)

  def load_data(self, data):
    self.clear()
    self._index_to_path = {}
    self._path_to_index = {}
    items = {}
    root = self.invisibleRootItem()

    # Define all possible entity types
    POSSIBLE_ENTITY_TYPES = [
        'constant|AE|signal',
        'constant|infinity|charge',
        'constant|infinity|energy',
        'constant|infinity|mass',
        'constant|infinity|species',
        'dynamic|ODE|signal',
        'dynamic|lumped|charge',
        'dynamic|lumped|energy',
        'dynamic|lumped|mass',
        'dynamic|lumped|species',
        'event|AE|signal',
        'event|distributed|charge',
        'event|distributed|energy',
        'event|distributed|mass',
        'event|distributed|species',
        'event|lumped|charge',
        'event|lumped|energy',
        'event|lumped|mass',
        'event|lumped|species'
    ]

    # Get unique internetworks from the data
    internetworks = set()
    for path in data:
        path_parts = path.split('.')
        if path_parts:
            internetworks.add(path_parts[0])

    # Add internetworks as first level
    for net in sorted(internetworks):
        net_item = QtGui.QStandardItem(net)
        net_item.setEditable(False)
        root.appendRow(net_item)
        items[net] = net_item

        # Add all possible entity types for this network
        for entity_type in sorted(POSSIBLE_ENTITY_TYPES):
            type_key = f"{net}.{entity_type}"
            type_item = QtGui.QStandardItem(entity_type)
            type_item.setEditable(False)
            type_item.setData({
                'network': net,
                'entity_type': entity_type,
                'is_entity_type': True
            }, QtCore.Qt.UserRole + 1)
            net_item.appendRow(type_item)
            
            # Store the mapping for selection handling
            index = self.indexFromItem(type_item)
            self._index_to_path[index] = entity_type
            self._path_to_index[entity_type] = index

    # Handle any remaining paths that don't follow the standard format
    for path in data:
        if path not in self._path_to_index.values():
            path_parts = path.split('.')
            if len(path_parts) >= 2:
                net = path_parts[0]
                parent = items.get(net, root)
                
                # Build the path
                path_so_far = net
                for i, part in enumerate(path_parts[1:], 1):
                    current_key = f"{path_so_far}.{part}" if i > 1 else f"{net}.{part}"
                    if current_key not in items:
                        item = QtGui.QStandardItem(part)
                        item.setEditable(False)
                        parent.appendRow(item)
                        items[current_key] = item
                    
                    parent = items.get(current_key, parent)
                    path_so_far = current_key
                
                # Store the mapping for fast lookups
                if parent != root:
                    index = self.indexFromItem(parent)
                    self._index_to_path[index] = path
                    self._path_to_index[path] = index

  def get_entity_type_data(self, index):
    """Get entity type data for the given index"""
    if not index.isValid():
        return None
        
    item = self.itemFromIndex(index)
    if not item:
        return None
        
    # Get the data we stored in load_data
    return item.data(QtCore.Qt.UserRole + 1)

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
