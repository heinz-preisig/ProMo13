"""
Provides a PyQt5 model for storing variables in a GUI.

This custom model, `VariableTreeModel`, is used for storing variables
and their typed tokens in a hierarchical structure suitable for display
in a GUI.

The `VariableTreeModel` class extends `QtGui.QStandardItemModel` and
adds functionality for loading data from a dictionary of variables and a
dictionary of typed tokens per variable. It also emits a signal,
`top_item_checked`, whenever a new top-level item is checked.

Author: Alberto Rodriguez Fernandez
"""
from typing import Dict, Set, List

from PyQt5 import QtGui
from PyQt5 import QtCore

from packages.Common.classes import variable
from packages.shared_components import roles


CHECKED = QtCore.Qt.CheckState.Checked
UNCHECKED = QtCore.Qt.CheckState.Unchecked


class VariableTreeModel(QtGui.QStandardItemModel):
  """Stores the variables in a model.

  To be used by one or more views in the GUI.

  Public Methods:
      - :meth:`load_data`
      - :meth:`

  Signals:
      - top_item_checked(QModelIndex): emitted when a new top level item
       is checked.
  """

  top_item_checked = QtCore.pyqtSignal(QtCore.QModelIndex)

  def __init__(self, parent=None):
    super().__init__(parent)
    self._variables: Dict[str, variable.Variable] = {}
    self._typed_tokens_per_variable = {}
    # self._id_to_index: Dict[str, QtGui.QStandardItem] = {}

  def load_data(
      self,
      variables: Dict[str, variable.Variable],
      typed_token_per_variable: Dict[str, Set[str]],
  ) -> None:
    """Loads the data into the model.

    Args:
        variables (Dict[str, variable.Variable]): Top level items to be
         added.
        typed_token_per_variable (Dict[str, Set[str]]): The keys include
         the variables used as top level items. The values contain the
         sub items for each top level item.
    """
    self._variables = variables
    self._typed_tokens_per_variable = typed_token_per_variable

    self.clear()

    for var_id in self._variables:
      # Adding the top level items
      parent_item = QtGui.QStandardItem(var_id)
      png_path = self._variables[var_id].get_img_path()
      self.appendRow(parent_item)

      # TODO: Switch to use roles.py
      parent_item.setData(png_path, QtCore.Qt.UserRole)
      parent_item.setCheckable(True)
      self._set_check_state(parent_item, UNCHECKED)

      # Adding the sub items
      for typed_token in sorted(list(typed_token_per_variable[var_id])):
        child_item = QtGui.QStandardItem(typed_token)
        child_item.setCheckable(True)
        self._set_check_state(child_item, UNCHECKED)

        parent_item.appendRow(child_item)

    # self._id_to_index[var_id] = self.indexFromItem(parent_item)

  def _set_check_state(
      self,
      item: QtGui.QStandardItem,
      state: QtCore.Qt.CheckState,
  ):
    """Sets the check state for an item.

    It also stores that state to be used later. This is particulary
    useful when the checkbox of an item is clicked, in that case the
    checkState changes before the clicked signal is emitted so
    information about the previous state is no longer available.

    Args:
        item (QtGui.QStandardItem): Item to change.
        state (QtCore.Qt.CheckState): The new state.
    """
    item.setData(state, roles.LAST_CHECK_STATE_ROLE)
    item.setCheckState(state)

  def handle_check_state_change(self, index: QtCore.QModelIndex):
    """Handles the check state changes.

    The state changes are handled differently depending on the type of
    item, for more information check:

    * Top level: :meth:`_handle_top_level_item_check_state_change`
    * Sub items: :meth:`_handle_sub_item_check_state_change`

    Args:
        index (QtCore.QModelIndex): corresponds to the item whose state
         changes.
    """
    if index.parent() == QtCore.QModelIndex():
      self._handle_top_level_item_check_state_change(index)
    else:
      self._handle_sub_item_check_state_change(index)

  def _handle_top_level_item_check_state_change(
      self,
      index: QtCore.QModelIndex,
  ) -> None:
    """Handles the check state changes for top level items.

    One and only one top level item must be checked at any time. If that
    item has children then the first children is automatically checked. This
    ensures that there is always at least one sub item checked.

    Args:
        index (QtCore.QModelIndex): corresponds to the item whose state
         changes.

    Signals:
        top_item_checked: Emitted when a new top level item is checked.
    """
    item = self.itemFromIndex(index)

    # There is not unchecking for top level items
    if item.data(roles.LAST_CHECK_STATE_ROLE) == CHECKED:
      self._set_check_state(item, CHECKED)
      return

    # Only one top level can be checked
    parent_item = self.invisibleRootItem()
    for row in range(parent_item.rowCount()):
      self._set_check_state(parent_item.child(row), UNCHECKED)

    self._set_check_state(item, CHECKED)

    # The first sub item gets checked if it exists
    for row in range(item.rowCount()):
      self._set_check_state(item.child(row), UNCHECKED)

    if item.rowCount() > 0:
      self._set_check_state(item.child(0), CHECKED)

    # Signal that a new top item has been checked
    self.top_item_checked.emit(self.indexFromItem(item))

  def _handle_sub_item_check_state_change(self, index: QtCore.QModelIndex):
    """Handles the check state changes for sub items.

    There must be always at least one sub item checked. This means that
    checking an item is always allowed. For the unchecking operation a
    check needs to be performed to ensure that there is at least one
    other subitem checked.

    Args:
        index (QtCore.QModelIndex): corresponds to the item whose state
         changes.
    """
    item = self.itemFromIndex(index)

    # Checking operation
    if item.data(roles.LAST_CHECK_STATE_ROLE) == UNCHECKED:
      self._set_check_state(item, CHECKED)
      return

    # Unchecking operation
    parent_item = item.parent()
    currently_checked_items = 0
    for row in range(parent_item.rowCount()):
      if parent_item.child(row).data(roles.LAST_CHECK_STATE_ROLE) == CHECKED:
        currently_checked_items += 1

    # When the checkbox is clicked to uncheck an item, the state changes
    # before the clicked signal is emitted. In this case illegal
    # unchecks will be performed. The expressions under the else undo
    # those illegal unchecks.
    if currently_checked_items > 1:
      self._set_check_state(item, UNCHECKED)
    else:
      self._set_check_state(item, CHECKED)

  def get_checked_items(self) -> Dict[str, List[str]]:
    """Returns the checked items.

    Returns:
        Dict[str, List[str]]: The keys are the top level elements. The
         values are the checked sub items.
    """
    root = self.invisibleRootItem()
    checked_items = {}
    for row in range(root.rowCount()):
      top_level_item = root.child(row)
      if top_level_item.checkState() == CHECKED:
        checked_items[top_level_item.text()] = self._get_checked_sub_items(
            top_level_item
        )

    return checked_items

  def _get_checked_sub_items(
      self,
      top_level_item: QtGui.QStandardItem,
  ) -> List[str]:
    """Returns the checked sub items for a top level item.

    Args:
        top_level_item (QtGui.QStandardItem): top level item whose sub
         items are going to be queried.

    Returns:
        List[str]: data of all the sub items that are checked.
    """
    checked_sub_items = []
    for row in range(top_level_item.rowCount()):
      sub_item = top_level_item.child(row)
      if sub_item.checkState() == CHECKED:
        checked_sub_items.append(sub_item.text())

    return checked_sub_items
