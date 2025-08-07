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

from PyQt5 import QtCore

from Common.common_resources import VARIABLE_TYPE_INTERFACES
from Common.pop_up_message_box import makeMessageBox
from Common.ui_show_equation_list_impl import UI_ShowVariableEquation

MAX_HEIGHT = 800

from Common.resources_icons import roundButton
from OntologyBuilder.OntologyEquationEditor.variable_table import VariableTable
from OntologyBuilder.OntologyEquationEditor.variable_framework import simulateDeletion


class UI_VariableTableDeleteEquation(VariableTable):
  """
  dialog for a variable
  emits a signal on completion

  columns are
    0 type
    1 symbol
    2 description / documentation
    3 tokens
    4 units
    5 indices
    6 equations
    7 delete
    8 network
    9 variable ID
    10 IRI
  """

  changed = QtCore.pyqtSignal(bool)

  def __init__(self,
               title,
               variables,
               indices,
               network,
               info_file=None,
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
    enabled_types = VARIABLE_TYPE_INTERFACES
    hide_vars = []
    hide_columns = [3]

    VariableTable.__init__(self,
                           title,
                           "variable_picking",
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
                   "info": roundButton(buttons["info"], "info", tooltip="information")
                   # "LaTex": roundButton(buttons["LaTex"], "LaTex", tooltip="make LaTeX document"),
                   # "dot": roundButton(buttons["dot"], "dot_graph", tooltip="show graph"),
                   }

    for b in buttons:
      if b not in showButtons:
        # print("debugging -- hide button", b)
        buttons[b].hide()

    self.hide_columns = hide_columns

    self.setToolTips("show")
    self.ui.tableVariable.setToolTip("show interface variables and allow for deletion")
    self.ui.tableVariable.setSortingEnabled(True)

  def on_tableVariable_itemClicked(self, item):

    column_count = self.ui.tableVariable.columnCount()
    row = item.row()
    column = item.column()
    item = self.ui.tableVariable.item
    data = {}
    for c in range(column_count):
      data[c] = item(row, c).text()
      # print("debugging -- chose:", c, str(data[c]))

    self.selected_variable_symbol = data[1]
    self.selected_variable_ID = data[9]
    # print("debugging -- selected ID:", self.selected_variable_ID, self.selected_variable_symbol)

    if column == 7:
      self.__showDeleteDialog(self.selected_variable_ID)

    elif column == 9:
      image_location = self.variables.ontology_container.latex_image_location
      list_equations = sorted(self.variables[self.selected_variable_ID].equations.keys())
      UI_ShowVariableEquation(list_equations, image_location,
                              mode="show",
                              prompt="all defined equations",
                              buttons=["reject", "accept"])

    return

  def __showDeleteDialog(self, selected_ID):
    port_variable = self.variables[selected_ID].port_variable
    if port_variable:
      reply = makeMessageBox("this is a port variable -- do you want to delete it ?", buttons=["NO", "YES"])
      if reply == 'NO':
        return

    var_symbol = self.variables[selected_ID].label
    msg = "deleting variable : %s" % var_symbol
    d_vars, d_equs, d_vars_text, d_equs_text = simulateDeletion(self.variables, selected_ID, self.indices)

    eqs = list(d_equs)
    loc = self.variables.ontology_container.latex_image_location
    if eqs == []:
      answer = makeMessageBox("no equations delete variable?", buttons=["YES", "NO"], default="NO", infotext="delete ?")
      delete = answer == "YES"

    else:
      dialog = UI_ShowVariableEquation(eqs, loc,
                                       mode="show",
                                       prompt="delete those equations?",
                                       buttons=["accept", "reject"])
      delete = dialog.answer == "accept"

    if delete:
      # print("debugging -- yes")
      self.__deleteVariable(d_vars, d_equs)
      self.reset_table()
      self.changed.emit(True)

  def __deleteVariable(self, d_vars, d_equs):
    print("going to delete: \n...variables:%s \n...equations %s" % (d_vars, d_equs))
    for v_id in d_equs:
      self.variables.removeEquation(v_id)
    for s in d_vars:
      self.variables.removeVariable(s)
    self.variables.indexVariables()  # indexEquationsInNetworks()
    self.reset_table()

  def on_pushFinished_pressed(self):
    self.close()

  def closeEvent(self, event):
    self.close()
