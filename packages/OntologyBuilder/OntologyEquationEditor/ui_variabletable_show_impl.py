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

from Common.pop_up_message_box import makeMessageBox
from Common.ui_show_equation_list_impl import UI_ShowVariableEquation

MAX_HEIGHT = 800

import os
from PyQt5 import QtWidgets

from Common.resources_icons import roundButton
from Common.common_resources import DIRECTORIES
from OntologyBuilder.OntologyEquationEditor.resources import AnalyseBiPartiteGraph
from OntologyBuilder.OntologyEquationEditor.resources import makeLatexDoc
from OntologyBuilder.OntologyEquationEditor.resources import showPDF
from OntologyBuilder.OntologyEquationEditor.variable_table import VariableTable



class UI_VariableTableShow(VariableTable):
  """
  dialog for a variable
  emits a signal on completion
  """

  def __init__(self,
               title,
               ontology_container,  #
               variables,
               network,
               enabled_types=['ALL'],
               hide_vars=[],
               hide_columns=[3],
               info_file=None,
               hidden=[],
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
    self.ontology_name = ontology_container.ontology_name
    self.ontology_container = ontology_container

    VariableTable.__init__(self,
                           title,
                           "variable_picking",
                           variables,
                           ontology_container.indices,
                           network,
                           enabled_types,
                           hide_vars,
                           hide_columns,
                           info_file=info_file
                           )

    buttons = self.buttons

    showButtons = {"back": roundButton(buttons["back"], "back", tooltip="go back"),
                   "LaTex": roundButton(buttons["LaTex"], "LaTex", tooltip="make LaTeX document"),
                   "dot": roundButton(buttons["dot"], "dot_graph", tooltip="show graph"),
                   }

    for b in buttons:
      if b not in showButtons:
        # print("debugging -- hide button", b)
        buttons[b].hide()

    buttons["LaTex"].hide()
    buttons["dot"].hide()

    self.hide_columns = hide_columns

    self.setToolTips("show")
    self.ui.tableVariable.setToolTip("click on row to copy variable to expression")
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


    if column == 9:
      image_location = self.variables.ontology_container.latex_image_location
      list_equations = sorted(self.variables[self.selected_variable_ID].equations.keys())

      # UI_ShowVariableEquation(list_equations, image_location,
      #                         mode="show",
      #                         prompt="These are the equations:",
      #                         buttons=["back"])

      list_equations = sorted(self.variables[self.selected_variable_ID].equations.keys())
      if len(list_equations) == 0:
        makeMessageBox("there are no equation", buttons=["OK"])
        self.buttons["LaTex"].hide()
        self.buttons["dot"].hide()
      else:
        self.buttons["LaTex"].show()
        self.buttons["dot"].show()

        UI_ShowVariableEquation(list_equations, image_location,
                                mode="show",
                                prompt="These are the equations:",
                                buttons=["back"])
    return

  def on_pushLaTex_pressed(self):
    # print("debugging -- generate latex table", self.selected_variable_symbol)

    assignments, dot_graph_file, file_name = self.__makeDotGraph()
    makeLatexDoc(file_name, assignments, self.ontology_container, dot_graph_file)
    self.buttons["dot"].show()

  def __makeDotGraph(self):
    var_equ_tree_graph, assignments = AnalyseBiPartiteGraph(self.selected_variable_ID,
                                                            self.ontology_container,
                                                            self.ontology_name,
                                                            [],
                                                            "%s_graph"%self.selected_variable_symbol)
    # var_equ_tree_graph.render_expression_to_list()
    var_equ_tree_graph.render()
    dot_graph_file = var_equ_tree_graph.outputFile + ".pdf"
    file_name = self.selected_variable_symbol
    return assignments, dot_graph_file, file_name

  def on_pushDot_pressed(self):
    list_equations = sorted(self.variables[self.selected_variable_ID].equations.keys())
    if len(list_equations) == 0:
      makeMessageBox("there are no equation", buttons=["OK"])
      return
    assignments, dot_graph_file, file_name = self.__makeDotGraph()
    showPDF(dot_graph_file)
    # print("debugging -- generate graph")

  @staticmethod
  def __addQtTableItem(tab, s, row, col):
    item = QtWidgets.QTableWidgetItem(s)
    tab.setRowCount(row + 1)
    tab.setItem(row, col, item)

  def on_tableVariable_itemDoubleClicked(self, item):
    column_count = self.ui.tableVariable.columnCount()
    row = item.row()
    item = self.ui.tableVariable.item
    data = {}
    for c in range(column_count):
      data[c] = item(row, c).text()
      # print("debugging -- chose:", c, str(data[c]))
    self.selected_variable_ID = data[9]
    # print("debugging -- selected ID:", self.selected_variable_ID)

  def on_pushFinished_pressed(self):
    self.close()

  def closeEvent(self, event):
    self.close()
