#!/usr/local/bin/python3
# encoding: utf-8
"""
@summary:      An editor for designing ontologies in my context
@contact:      heinz.preisig@chemeng.ntnu.no
@requires:     Python 3 or higher
@since:        01.12.19
@version:      0.1
@change:       01.12.19
@author:       Preisig, Heinz A
@copyright:    2019 Preisig, Heinz A  All rights reserved.
"""

__author__ = 'Preisig, Heinz A'

MAX_HEIGHT = 800
MAX_WIDTH = 1000

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.common_resources import VARIABLE_TYPE_INTERFACES
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.OntologyEquationEditor.resources import TOOLTIPS
from OntologyBuilder.OntologyEquationEditor.resources import renderIndexListFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.ui_variabletable import Ui_Dialog


class VariableTable(QtWidgets.QDialog):
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
               what,
               variables,
               indices,
               network,
               enabled_variable_types,
               hide_vars,
               hide_columns,
               info_file):

    self.variables = variables
    self.indices = indices
    self.network = network
    self.what = what
    self.info_file = info_file
    if what == "variable_picking":  # NOTE: Python issue. Is not updated when making table. ???
      self.variable_space = variables.index_accessible_variables_on_networks
    else:
      try:
        self.variable_space = variables.index_networks_for_variable
      except:
        self.variables.indexVariables()
    # self.variable_space = variable_space
    self.enabled_variable_types = enabled_variable_types
    self.hide_vars = hide_vars
    self.hide_columns = hide_columns

    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    # self.ui.labelNetwork.setText(title)
    self.setWindowTitle(title)
    self.reset_table()
    self.hide()

    #
    self.buttons = {
            "back" : self.ui.pushFinished,
            "info" : self.ui.pushInfo,
            "new"  : self.ui.pushNew,
            "port" : self.ui.pushPort,
            "LaTex": self.ui.pushLaTex,
            "dot"  : self.ui.pushDot,
            "next" : self.ui.pushNext,
            }

  def reset_table(self):
    self.variables.indexVariables()  # this was a hard one
    self.ui.tableVariable.clearContents()
    self.ui.tableVariable.setRowCount(0)
    self.makeTable()
    self.update()
    if not self.info_file:
      self.ui.pushInfo.hide()
    else:
      self.ui.pushInfo.show()

  def setToolTips(self, mode):
    rows = self.ui.tableVariable.rowCount()
    cols = self.ui.tableVariable.columnCount()
    for c in range(cols):
      c_item = self.ui.tableVariable.horizontalHeaderItem(c)
      c_t = c_item.text()
      for r in range(rows):
        r_item = self.ui.tableVariable.item(r, c)
        if r_item:
          r_item.setToolTip(TOOLTIPS[mode][c_t])
          # print("table %s ----- for row %s and column %s"%(mode, r,c))
        else:
          # print("table %s error for row %s and column %s"%(mode, r,c))
          pass

  def makeTable(self):
    # Note: variable space generation has been centralised
    self.variable_space = self.variables.variableSpaces(self.what, self.network, self.enabled_variable_types)

    # # NOTE: fix since update did not work.
    # if self.what == "variable_picking":
    #   self.variable_space = self.variables.variableSpaces(self.what, self.network, self.enabled_variable_types) #self.variables.index_accessible_variables_on_networks
    # elif self.what == "interface_picking": #RULE: variable space for interface is the left variables
    #
    # # NOTE: that's to cruel
    # # left_nw, right_nw = self.network.split(CONNECTION_NETWORK_SEPARATOR)
    # # self.variable_space[self.network] = self.variables.index_networks_for_variable[left_nw]
    #
    # # NOTE: that's probably right
    #   self.variable_space={}
    #   self.variable_space[self.network] = {}
    #   for i in self.enabled_variable_types:
    #     self.variable_space[self.network][i] =[]
    #   for ID in self.variables:
    #     v = self.variables[ID]
    #     left_nw, right_nw = self.network.split(CONNECTION_NETWORK_SEPARATOR)
    #     if v.network == left_nw:
    #       self.variable_space[self.network][v.type].append(ID)
    #
    # else:
    #   self.variable_space = self.variables.index_networks_for_variable

    variable_ID_list = self.makeVariableIDList()

    table = self.ui.tableVariable

    variable_ID_list = self.populateTable(table, variable_ID_list)

    self.variables_in_table = list(variable_ID_list)

    for c in self.hide_columns:
      self.ui.tableVariable.hideColumn(c)

    # fitting window
    table.resizeColumnsToContents()
    table.resizeRowsToContents()
    t = self.__tabSizeHint()
    table.resize(t)
    x = t.width() + table.x() + 12
    y = table.y() + table.height() + 12
    s = QtCore.QSize(x, y)
    self.resize(s)

  def makeVariableIDList(self):
    variable_ID_list = set()
    nw = self.network
    for variable_type in self.variable_space[nw]:  # self.variables.index_accessible_variables_on_networks[nw]:
      if variable_type in self.enabled_variable_types:
        # for i in self.variables.index_accessible_variables_on_networks[nw][variable_type]:
        for i in self.variable_space[nw][variable_type]:
          variable_ID_list.add(i)
    return variable_ID_list

  def populateTable(self, table, variable_ID_list):
    table.clearContents()
    rowCount = 0
    if not variable_ID_list:
      if rowCount == 0:  # Note: only add one for an empty list
        self.__addQtTableItem(table, self.enabled_variable_types[0], rowCount, 0)
        rowCount += 1
      variable_ID_list = []
    else:
      for ID in variable_ID_list:
        symbol = self.variables[ID].label
        if symbol not in self.hide_vars:
          v = self.variables[ID]
          index_structures_labels = renderIndexListFromGlobalIDToInternal(v.index_structures, self.indices)
          # print("debugging -- adding variable ", ID, symbol)
          self.__addQtTableItem(table, v.type, rowCount, 0)
          self.__addQtTableItem(table, symbol, rowCount, 1)
          self.__addQtTableItem(table, v.doc, rowCount, 2)
          toks = ""
          for t in v.tokens:
            toks += t.strip("[],")
            toks += ","
          toks = toks[:-1]  # remove last ,
          self.__addQtTableItem(table, toks, rowCount, 3)
          self.__addQtTableItem(table, v.units.prettyPrintUIString(), rowCount, 4)
          # index_structures_labels = [self.indices[ind_ID]["label"] for ind_ID in v.index_structures]
          self.__addQtTableItem(table, str(index_structures_labels), rowCount, 5)
          _l = len(v.equations)
          self.__addQtTableItem(table, str(_l), rowCount, 6)
          self.__addQtTableItem(table, 'x', rowCount, 7)
          self.__addQtTableItem(table, v.network, rowCount, 8)
          self.__addQtTableItem(table, str(ID), rowCount, 9)
          rowCount += 1
    return variable_ID_list

  def hideVars(self, list_of_IDs):
    for id in self.variables_in_table:
      if id in list_of_IDs:
        index = self.variables_in_table.index(id)
        self.ui.tableVariable.hideRow(index)

  def __tabSizeHint(self):
    tab = self.ui.tableVariable
    width = 0
    for i in range(tab.columnCount()):
      width += tab.columnWidth(i)
    width += tab.verticalHeader().sizeHint().width()
    width += tab.frameWidth() * 2
    if width > MAX_WIDTH:
      width += tab.verticalScrollBar().sizeHint().width()
    width -= 0  # NOTE: manual fix

    height = 0
    for i in range(tab.rowCount()):
      height += tab.rowHeight(i)
    height += tab.horizontalHeader().sizeHint().height()
    height += tab.frameWidth() * 2
    if height > MAX_HEIGHT:
      height += tab.horizontalScrollBar().sizeHint().height()
    height -= 0  # NOTE: manual fix

    return QtCore.QSize(width, min(height, MAX_HEIGHT))

  @staticmethod
  def __addQtTableItem(tab, s, row, col):
    item = QtWidgets.QTableWidgetItem(s)
    tab.setRowCount(row + 1)
    tab.setItem(row, col, item)

  def on_pushInfo_pressed(self):
    msg_popup = UI_FileDisplayWindow(self.info_file)
    msg_popup.exec_()
