#!/usr/local/bin/python3
# encoding: utf-8
"""
@summary:      An editor for designing ontologies in my context
@contact:      heinz.preisig@chemeng.ntnu.no
@requires:     Python 3 or higher
@since:        29.08.15
@version:      0.1
@change:       Aug 29, 2015
@author:       Preisig, Heinz A
@copyright:    2014 Preisig, Heinz A  All rights reserved.
"""

__author__ = 'Preisig, Heinz A'

MAX_HEIGHT = 800

from PyQt5 import QtCore

from Common.resources_icons import roundButton
from OntologyBuilder.OntologyEquationEditor.variable_table import VariableTable


class UI_VariableTablePick(VariableTable):
  """
  dialog for a variable
  emits a signal on completion
  """

  completed = QtCore.pyqtSignal(str)
  picked = QtCore.pyqtSignal(str)
  new_variable = QtCore.pyqtSignal(str)
  new_equation = QtCore.pyqtSignal(str, str)
  deleted_symbol = QtCore.pyqtSignal(str)

  def __init__(self,
               title,
               variables,
               indices,
               network,
               enabled_types=['ALL'],
               hide_vars=[],
               hide_columns=[],
               info_file=None,
               hidden=[]
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

    VariableTable.__init__(self,
                           title,
                           "variable_picking",
                           variables,
                           indices,
                           network,
                           # variables.index_accessible_variables_on_networks,
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
                   }

    for b in buttons:
      if b not in showButtons:
        buttons[b].hide()

    self.variable_list = []
    self.hide_columns = hide_columns

    self.setToolTips('pick')
    self.ui.tableVariable.setToolTip("click on row to copy variable to expression")
    self.ui.tableVariable.setSortingEnabled(True)

  def on_tableVariable_itemClicked(self, item):
    r = int(item.row())
    item = self.ui.tableVariable.item
    self.selected_variable_symbol = str(item(r, 1).text())
    self.picked.emit(self.selected_variable_symbol)
    return

  def on_tableVariable_itemDoubleClicked(self, item):
    print("debugging -- double click on item", item.row(), item.column())

  def on_pushFinished_pressed(self):
    self.close()

  def closeEvent(self, event):
    self.close()
