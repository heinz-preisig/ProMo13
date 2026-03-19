#!/usr/local/bin/python3
# encoding: utf-8
"""
@summary:      An editor for designing ontologies in my context
@contact:      heinz.preisig@chemeng.ntnu.no
@requires:     Python 3 or higher
@since:        2022-05-25
@version:      0.1
@change:       2022-05-25
@author:       Preisig, Heinz A
@copyright:    2022 Preisig, Heinz A  All rights reserved.
"""

__author__ = 'Preisig, Heinz A'

MAX_HEIGHT = 800

from PyQt5 import QtCore

from Common.resources_icons import roundButton
from OntologyBuilder.OntologyEquationEditor.variable_table import VariableTable


class UI_VariableTableInterfaceInstantiate(VariableTable):
  """
  dialog for a variable to be instantiated with a value
  emits a signal on completion
  """
  #
  # completed = QtCore.pyqtSignal(str)
  picked = QtCore.pyqtSignal(int)
  # new_variable = QtCore.pyqtSignal(str)
  # new_equation = QtCore.pyqtSignal(str, str)
  # deleted_symbol = QtCore.pyqtSignal(str)

  def __init__(self,
               title,
               variables,
               indices,
               network,
               enabled_types=['ALL'],
               hide_vars=[],
               hide_columns=[],
               info_file=None,
               variable_IDs = []
               ):
    """
    constructs a dialog window based on QDialog for picking variables
    @param title:     title string: indicates the tree's nature
    @param variables: physical variable.
    @network:      network type
    @my_types:      type of variables being processed

    control is done through the interface and additional functions:
    - enable_pick_contents : true or false
    - enable_seclection : rows and columns

    signals:
    - picked : returns selected item text
    - completed : button finished has been pressed
    -
    """

    self.variable_IDs = variable_IDs
    self.hide_columns = hide_columns

    VariableTable.__init__(self,
                           title,
                           "instantiate",
                           variables,
                           indices,
                           network,
                           enabled_types,
                           hide_vars,
                           hide_columns,
                           info_file=info_file
                           )
    buttons = self.buttons

    showButtons = {"back": roundButton(buttons["back"], "back", tooltip="go back"),
                   # "info": roundButton(buttons["info"], "info", tooltip="information"),
                   # "new" : roundButton(buttons["new"], "dependent_variable", tooltip="new dependent variable"),
                   # "port": roundButton(buttons["port"], "port", tooltip="new port variable"),
                   # "next": roundButton(buttons["next"], "next", tooltip="show defined interface variables")
                   }

    for b in buttons:
      if b not in showButtons:
        buttons[b].hide()

    self.variable_list = []

    self.setToolTips('pick')
    self.ui.tableVariable.setToolTip("click on row to copy variable to expression")
    self.ui.tableVariable.setSortingEnabled(True)

  def on_tableVariable_itemClicked(self, item):
    row = int(item.row())
    item = self.ui.tableVariable.item
    var_ID = int(item(row,9).text())
    self.picked.emit(var_ID)
    return

  def makeVariableIDList(self):
    return self.variable_IDs

  def on_pushFinished_pressed(self):
    self.close()

  def closeEvent(self, event):
    self.close()
