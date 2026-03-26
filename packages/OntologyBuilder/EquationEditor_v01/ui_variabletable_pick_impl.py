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
from OntologyBuilder.EquationEditor_v01.variable_table import VariableTable


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
                 networks=None,
                 enabled_types=['ALL'],
                 hide_vars=[],
                 hide_columns=[],
                 info_file=None,
                 hidden=[],
                 which="variable_picking",
                 ):
        """
        constructs a dialog window based on QDialog for picking variables
        @param title:     title string: indicates the tree's nature
        @param variables: physical variable.
        @param network:      network type (deprecated, use networks instead)
        @param networks:     list of network types (new parameter)
        @my_types:      type of variables being processed

        control is done through the interface and additional functions:
        - enable_pick_contents : true or false
        - enable_seclection : rows and columns

        signals:
        - picked : returns selected item text
        - completed : button finished has been pressed
        -
        """

        # Support both old single network and new multiple networks
        if networks is not None:
            self.networks = networks
            self.network = networks[0] if networks else network  # For compatibility
        else:
            self.networks = [network]
            self.network = network

        VariableTable.__init__(self,
                               title,
                               which,
                               variables,
                               indices,
                               self.networks,  # Pass networks instead of single network
                               enabled_types,
                               hide_vars,
                               hide_columns,
                               info_file=info_file,
                               show_buttons=["back"],
                               )
        buttons = self.buttons

        showButtons = {
                "back": roundButton(buttons["back"], "back", tooltip="go back"),
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

        # Get the variable ID from column 9 (hidden column with ID)
        var_ID = str(item(r, 9).text())

        # Check if this is an interface variable by looking at its network
        var = self.variables[var_ID]

        # If variable is from interface domain, use its label directly
        # If variable is from another domain, create/get interface variable name
        if hasattr(var, 'network') and var.network == 'interface':
            # This is already an interface variable - return its ID
            self.selected_variable_symbol = str(item(r, 9).text())  # Get ID from hidden column
        else:
            # This is a cross-domain variable, create interface variable and return its ID
            source_domain = var.network
            source_label = var.label
            interface_var_name = f"{source_domain}_{source_label}"

            # Create interface variable to get its ID
            interface_var_ID = self.variables.createInterfaceVariable(
                    source_domain, var_ID, self.network
                    )

            # Return the interface variable ID (V_8), not the name (physical_V)
            self.selected_variable_symbol = interface_var_ID

        self.picked.emit(self.selected_variable_symbol)
        return

    # def on_tableVariable_itemDoubleClicked(self, item):
    #   print("debugging -- double click on item", item.row(), item.column())

    def on_pushFinished_pressed(self):
        self.close()

    def closeEvent(self, event):
        self.close()
