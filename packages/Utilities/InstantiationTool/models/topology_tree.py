"""
Module-level docstring

This module contains the implementation of a custom PyQt5 model to store
topology objects.

Author: Alberto Rodriguez Fernandez
"""

from operator import mod
from typing import Dict, List, Optional

from PyQt5 import QtCore, QtGui

from packages.shared_components import roles
from src.common import old_topology

CHECKED = QtCore.Qt.CheckState.Checked
UNCHECKED = QtCore.Qt.CheckState.Unchecked
PARTIALLY_CHECKED = QtCore.Qt.CheckState.PartiallyChecked


# TODO: Make the items be added always in the same order
class TopologyTreeModel(QtGui.QStandardItemModel):
    """Stores the variables in a model

    To be used as a model for one or more views in the GUI.
    """

    check_box_state_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_topology_objects: dict[str, old_topology.TopologyObject] = {}
        self._index_from_id: dict[str, QtCore.QModelIndex] = {}
        self._id_from_index: dict[QtCore.QModelIndex, str] = {}

        self.flag_propagation_allowed = True
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["Name"])

        self.itemChanged.connect(self._propagate_check_state)

    def empty_model(self):
        self.removeRows(0, self.rowCount())
        self._index_from_id.clear()
        self._id_from_index.clear()

    def get_index_from_id(self, top_obj_id: str) -> QtCore.QModelIndex | None:
        return self._index_from_id.get(top_obj_id)

    def get_number_of_items(
        self, parent_index: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> int:
        total = 0
        for row in range(self.rowCount(parent_index)):
            index = self.index(row, 0, parent_index)
            total += 1
            total += self.get_number_of_items(index)

        return total

    def load_data(
        self,
        all_topology_objects: dict[str, old_topology.TopologyObject],
        filtered_list: list[str],
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

        self._all_topology_objects = all_topology_objects

        for top_obj_id in filtered_list:
            self._add_ancestors(top_obj_id)
            self._add_item(top_obj_id)

    def _add_ancestors(self, item_id: str) -> None:
        """Adds the ancestors of the item to the model

        This recursive function makes sure that the ancestors are always
        added to the model before their descendants. It will add all the
        items from the item represented by item_id to the root of the model
        as long as they are not already on the model.

        Args:
            item_id (str): Identifier of the item whose ancestors are being
                             added.
        """
        parent_id = self._all_topology_objects[item_id].parent_id

        if parent_id not in self._index_from_id and parent_id is not None:
            self._add_ancestors(parent_id)
            self._add_item(parent_id)

    def _add_item(self, item_id: str) -> None:
        """Adds an item to the model

        The dictionaries _id_to_index and _index_to_id are populated after
        the item has been added.

        Args:
            item_id (str): Identifier of the item that is being added.
        """
        item_obj = self._all_topology_objects[item_id]

        parent_id = item_obj.parent_id

        main_item = QtGui.QStandardItem()
        main_item.setData(item_id, roles.ID_ROLE)
        main_item.setData(item_obj.name, roles.NAME_ROLE)
        main_item.setData(item_obj.__class__.__name__, roles.CLASS_ROLE)

        main_item.setCheckable(True)
        main_item.setAutoTristate(True)

        if parent_id is None:
            parent_item = self.invisibleRootItem()
        else:
            parent_index = self._index_from_id.get(parent_id)
            parent_item = self.itemFromIndex(parent_index)

        parent_item.appendRow(main_item)

        main_item_index = self.indexFromItem(main_item)
        self._index_from_id[item_id] = main_item_index
        self._id_from_index[main_item_index] = item_id

    def _propagate_check_state(self, item: QtGui.QStandardItem):
        """Propagates the check state of an item.

        This method first propagates the check state down to all children of
        the item using the helper method `_propagate_check_state_down`.
        Then, if the item has a parent, it propagates the check state up to
        the parent using the helper method `_propagate_check_state_up`.

        Args:
            item (QtGui.QStandardItem): The item whose check state is to be
             propagated.
        """
        # This flag prevents an infinite loop due the item_changed signal
        # being emitted every time a propagated change occurs.
        if self.flag_propagation_allowed:
            self.flag_propagation_allowed = False

            self._propagate_check_state_down(item)

            if item.parent() is not None:
                self._propagate_check_state_up(item.parent())

            # Only emitted for the triggering change
            self.check_box_state_changed.emit()

            self.flag_propagation_allowed = True

    def _propagate_check_state_down(self, item: QtGui.QStandardItem):
        """Propagates the check state of an item down to all its children.

        Helper method for `_propagate_check_state`. This method sets the
        check state of all children of the item to the check state of the
        item. It does this recursively for each child.

        Args:
            item (QtGui.QStandardItem): The item whose check state is to be
             propagated down.
        """
        check_state = item.checkState()
        for row in range(item.rowCount()):
            child_item = item.child(row)
            child_item.setCheckState(check_state)
            self._propagate_check_state_down(child_item)

    def _propagate_check_state_up(self, item: QtGui.QStandardItem):
        """Propagates the check state of an item up to its parent.

        Helper method for `_propagate_check_state`. This method sets the
        check state of the parent based on the check states of its children.
            - If any child is partially checked or if some children are
             checked and others are unchecked, the parent is set to
             partially checked.
            - If all children are unchecked, the parent is set to unchecked.
            - If all children are checked, the parent is set to checked.

        This is done recursively for each parent.

        Args:
            item (QtGui.QStandardItem): The item whose check state is to be
             propagated up.
        """
        any_checked = False
        any_unchecked = False
        any_partially_checked = False
        for row in range(item.rowCount()):
            child_item = item.child(row)
            if child_item.checkState() == CHECKED:
                any_checked = True
            if child_item.checkState() == UNCHECKED:
                any_unchecked = True
            if child_item.checkState() == PARTIALLY_CHECKED:
                any_partially_checked = True

        if any_partially_checked or (any_checked and any_unchecked):
            item.setCheckState(PARTIALLY_CHECKED)
        elif not any_checked:
            item.setCheckState(UNCHECKED)
        elif not any_unchecked:
            item.setCheckState(CHECKED)

        if item.parent() is not None:
            self._propagate_check_state_up(item.parent())

    def get_checked_items(self, parent=None) -> list[str]:
        checked_items = []
        if parent is None:
            parent = self.invisibleRootItem()

        for row in range(parent.rowCount()):
            child = parent.child(row)
            child_id = child.data(roles.ID_ROLE)

            if (
                not isinstance(
                    self._all_topology_objects[child_id], old_topology.NodeComposite
                )
                and child.checkState() == CHECKED
            ):
                checked_items.append(child_id)

            if child.hasChildren():
                checked_items.extend(self.get_checked_items(child))

        return checked_items

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
