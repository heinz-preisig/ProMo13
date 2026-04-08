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

from Common.resources_icons import roundButton
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.EquationEditor_v01.resources import TOOLTIPS
from OntologyBuilder.EquationEditor_v01.resources import renderIndexListFromGlobalIDToInternal
from OntologyBuilder.EquationEditor_v01.ui_variabletable import Ui_Dialog


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
                 info_file,
                 show_buttons,
                 ):

        self.variables = variables
        self.indices = indices

        # Always handle networks as a list for consistency
        if isinstance(network, list):
            self.networks = network
            self.network = network[0] if network else network  # For compatibility
        else:
            self.networks = [network]
            self.network = network

        self.what = what
        self.info_file = info_file

        self.enabled_variable_types = enabled_variable_types
        self.hide_vars = hide_vars
        self.hide_columns = hide_columns

        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.reset_table()
        self.hide()

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # note: made table frameless
        self.setWindowFlags(
                self.windowFlags() |
                QtCore.Qt.FramelessWindowHint
                )

        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)

        #
        self.buttons = {
                "back"     : self.ui.pushFinished,
                "info"     : self.ui.pushInfo,
                "new"      : self.ui.pushNew,
                "port"     : self.ui.pushPort,
                "LaTex"    : self.ui.pushLaTex,
                "dot"      : self.ui.pushDot,
                "dot_graph": self.ui.pushDot,
                "next"     : self.ui.pushNext,
                }

        for button in self.buttons:
            self.buttons[button].hide()

        buttons = self.buttons
        for button_name in buttons:
            if button_name in show_buttons:
                roundButton(buttons[button_name], button_name, tooltip=buttons[button_name].toolTip())
                self.buttons[button_name].show()
            else:
                self.buttons[button_name].hide()

    def reset_table(self):
        self.variables.indexVariables()  # this was a hard one
        self.ui.tableVariable.clearContents()
        self.ui.tableVariable.setRowCount(0)
        self.makeTable()
        self.update()
        # if not self.info_file:
        #   self.ui.pushInfo.hide()
        # else:
        #   if "info" in self.buttons:
        #     self.ui.pushInfo.show()

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

        variable_ID_list = self.makeVariableIDList()

        if not variable_ID_list:
            return

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
        if self.what == 'interface_picking':
            # Only local network for interface picking
            networks = [self.network]
            print("table -- interface_picking")
        elif self.what == 'variable_editing':
            # For variable editing, only show variables from current network
            networks = [self.network]
            # Use basic variable space for editing
            variable_space = {}
            # print(f"DEBUG: Checking if network '{self.network}' exists in index_networks_for_variable")
            # print(f"DEBUG: Available networks: {list(self.variables.index_networks_for_variable.keys())}")
            if self.network in self.variables.index_networks_for_variable:
                # print(f"DEBUG: Network '{self.network}' found in index")
                variable_space[self.network] = {}
                # print(
                #     f"DEBUG: Variable classes in network: {list(self.variables.index_networks_for_variable[self.network].keys())}")
                for var_class in self.variables.index_networks_for_variable[self.network]:
                    variable_space[self.network][var_class] = set()
                    # print(
                    # f"DEBUG: Checking class '{var_class}' with {len(self.variables.index_networks_for_variable[self.network][var_class])} variables")
                    for v in self.variables.index_networks_for_variable[self.network][var_class]:
                        # print(
                        #     f"DEBUG: Checking variable {v}: type='{self.variables[v].type}', enabled_types={self.enabled_variable_types}")
                        if not self.enabled_variable_types or self.variables[v].type in self.enabled_variable_types:
                            # print(f"DEBUG: Adding variable {v} to space")
                            variable_space[self.network][var_class].add(v)
                        # else:
                        #     print(f"DEBUG: Filtering out variable {v}")
            else:
                print(f"DEBUG: Network '{self.network}' NOT found in index!")
            # print(f"DEBUG: variable_editing final space: {variable_space}")
            # print("table -- variable_editing")
        else:
            # Use the updated variableSpaces method for variable_picking
            variable_space, v_counter = self.variables.variableSpaces("variable_picking", self.network,
                                                                      self.enabled_variable_types)
            networks = list(variable_space.keys())

            print("table -- neither uses variableSpace")

        # Collect variables from all accessible networks
        for nw in networks:
            if nw in variable_space:
                for variable_type in variable_space[nw]:
                    for i in variable_space[nw][variable_type]:
                        variable_ID_list.add(i)

        # Handle interface variable creation when picking from other domains
        # if self.what == 'variable_picking':
        #   variable_ID_list = self._handleInterfaceVariableCreation(variable_ID_list)

        variable_dict = {}
        if variable_ID_list:
            for var_ID in variable_ID_list:
                var = self.variables[var_ID]
                # Add network prefix for cross-domain variables
                if var.network != self.network:
                    display_label = f"{var.network}!{var.label}"
                else:
                    display_label = var.label
                variable_dict[display_label] = var_ID
            variable_ID_list_sorted = []
            for var_symbol in sorted(variable_dict.keys()):
                variable_ID_list_sorted.append(variable_dict[var_symbol])
        else:
            variable_ID_list_sorted = []

        return variable_ID_list_sorted  # variable_ID_list

    def _handleInterfaceVariableCreation(self, variable_ID_list):
        """
        Create interface variables for cross-domain selections
        """
        interface_vars_to_add = set()
        vars_to_remove = set()

        for var_ID in variable_ID_list:
            var = self.variables[var_ID]

            # Skip if variable is from current domain or interface domain
            if var.network == self.network:
                continue

            if hasattr(self.variables, 'interface_domain') and \
                    self.variables.interface_domain and \
                    var.network == self.variables.interface_domain:
                continue

            # Create interface variable: domain_varname = varname
            interface_var_ID = self.variables.createInterfaceVariable(
                    var.network, var_ID, self.network
                    )

            interface_vars_to_add.add(interface_var_ID)
            vars_to_remove.add(var_ID)

        # Update the original list: remove cross-domain vars, add interface vars
        final_list = (variable_ID_list - vars_to_remove) | interface_vars_to_add

        return final_list

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
                    for t in getattr(v, 'tokens', []):  # Safe fallback for variables without tokens
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
                    self.__addQtTableItem(table, v.IRI, rowCount, 10)
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
        if not self.info_file:
            return
        msg_popup = UI_FileDisplayWindow(self.info_file)
        msg_popup.exec_()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def exit(self):
        return
