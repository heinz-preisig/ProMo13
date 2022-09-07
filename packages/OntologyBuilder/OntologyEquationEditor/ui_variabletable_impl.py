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

__author__ = "Preisig, Heinz A"

MAX_HEIGHT = 800

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.resources_icons import roundButton
# from Common.common_resources import globalVariableID
from Common.qt_resources import NO
from Common.qt_resources import YES
from Common.record_definitions import makeCompleteVariableRecord, makeCompletEquationRecord
from Common.single_list_selector_impl import SingleListSelector
from Common.ui_radio_selector_w_sroll_impl import UI_RadioSelector
from OntologyBuilder.OntologyEquationEditor.resources import ENABLED_COLUMNS, CODE
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidentList
from OntologyBuilder.OntologyEquationEditor.resources import NEW_VAR
from OntologyBuilder.OntologyEquationEditor.ui_documentation_impl import UI_DocumentationDialog
from OntologyBuilder.OntologyEquationEditor.ui_physunits_impl import UI_PhysUnitsDialog
from OntologyBuilder.OntologyEquationEditor.ui_symbol_impl import UI_SymbolDialog
from OntologyBuilder.OntologyEquationEditor.variable_framework import simulateDeletion
from OntologyBuilder.OntologyEquationEditor.variable_framework import Units
from OntologyBuilder.OntologyEquationEditor.variable_table import VariableTable
from Common.pop_up_message_box import makeMessageBox


class UI_VariableTableDialog(VariableTable):
  """
  dialog for a variable
  emits a signal on completion
  """

  completed = QtCore.pyqtSignal(str)
  picked = QtCore.pyqtSignal(str)
  new_variable = QtCore.pyqtSignal(str)
  new_equation = QtCore.pyqtSignal(int)
  deleted_symbol = QtCore.pyqtSignal(str)

  def __init__(self,
               title,
               variables,
               indices,
               tokens_on_networks,
               variable_types_on_networks,
               network,
               network_expression,
               choice,
               disabled_variables=[],
               hide_vars=[],
               hide_columns=[],
               info_file=None,
               hidden_buttons=[]):
    """
    constructs a dialog window based on QDialog
    @param title:     title string: indicates the tree's nature
    @param variables: physical variable.
    @network:      network type
    @my_types:      type of variables being processed

    control is done through the interface and additional functions:
    - enable_pick_contents : true or false
    - enable_selection : rows and columns

    signals:
    - picked : returns selected item text
    - completed : button finished has been pressed
    -
    """

    enabled_variable_types = [choice]
    self.variable_types_on_networks = variable_types_on_networks
    self.selected_variable_type = choice
    self.tokens_on_networks = tokens_on_networks

    VariableTable.__init__(self,
                           title,
                           "variables_definition",
                           variables,
                           indices,
                           network,
                           # variables.index_networks_for_variable,       # defines variable space
                           enabled_variable_types,
                           hide_vars,
                           hide_columns,
                           info_file=info_file
                           )

    buttons = self.buttons

    showButtons = {"back" :     roundButton(buttons["back"], "back", tooltip="go back"),
                   "info":    roundButton(buttons["info"], "info", tooltip="information"),
                   "new" :     roundButton(buttons["new"], "dependent_variable", tooltip="new dependent variable"),
                   "port":     roundButton(buttons["port"], "port", tooltip="new port variable"),
                   }

    for b in buttons:
      if b not in showButtons:
        buttons[b].hide()

    # version_change : hide token column
    self.hideColumn(3)

    self.network_expression = network_expression
    self.variable_list = []
    self.disabled_variables = disabled_variables
    self.variables_in_table = []
    self.label_ID_dict = {}  # for changing / choosing index set
    self.reset_table()

    self.enabled_columns = None
    self.selected_variable_symbol = None

    self.ui_symbol = UI_SymbolDialog()
    self.ui_symbol.finished.connect(self.reset_table)
    self.ui_units = UI_PhysUnitsDialog("new physical units")
    self.ui_units.finished.connect(self.reset_table)

    # self.setToolTips("edit")  # FIXME: this does not work. appears to be a pyqt issue.

  def show(self):
    self.reset_table()
    QtWidgets.QDialog.show(self)
    self.setToolTips("edit")
    self.raise_()

  def hideColumn(self, c):
    self.ui.tableVariable.hideColumn(c)

  def enable_column_selection(self, columns):
    self.enabled_columns = columns

  def protect_variable_type(self, variable_types):  # TODO may be useful
    self.protected_variable_types = variable_types

  def __showDeleteDialog(self, selected_ID):
    port_variable = self.variables[selected_ID].port_variable
    if port_variable:
      reply = makeMessageBox("this is a port variable -- do you want to delete it ?",buttons=["NO","YES"])
      if reply == 'NO':
        return

    var_symbol = self.variables[selected_ID].label
    msg = "deleting variable : %s" % var_symbol
    d_vars, d_equs, d_vars_text, d_equs_text = simulateDeletion(self.variables, selected_ID, self.indices)
    v = d_vars_text[1:-1].replace("\n", ",  ")
    e = d_equs_text.replace("\n", "\n   ")
    msg += "\n\nand consequently \n...variables:%s \n\n...equations %s" % (v, e)
    reply = makeMessageBox(msg, buttons=["NO", "YES"])
    if reply == "YES":
      # print("debugging -- yes")
      self.__deleteVariable(d_vars, d_equs)
      self.reset_table()

  def __deleteVariable(self, d_vars, d_equs):
    print("going to delete: \n...variables:%s \n...equations %s" % (d_vars, d_equs))
    for v_id in d_equs:
      self.variables.removeEquation(v_id)
    for s in d_vars:
      self.variables.removeVariable(s)
    self.variables.indexVariables()  # indexEquationsInNetworks()
    self.reset_table()

  def on_pushNew_pressed(self):
    self.__defineNewVarWithEquation()

  def on_pushPort_pressed(self):
    self.definePortVariable()

  def __change_variable_type_dialogue(self):
    variable_types = list(set(self.variable_types_on_networks[self.network]))
    self.selector = SingleListSelector(variable_types)
    self.selector.exec_()
    selection, button = self.selector.getSelection()
    if button == "left":
      return
    elif self.selected_variable_type == selection:
      return
    else:
      self.variables[self.selected_ID].shiftType(selection)
      self.variables.indexVariables()
      self.close()

  # def __showNewVariableDialog(self):
  #   msg = "new port variable ?"
  #   if self.has_port_variables:
  #     reply = QtWidgets.QMessageBox.question(self, "choose", msg, YES, NO)
  #   else:
  #     reply = NO
  #
  #   if reply == YES:
  #     print("yes")
  #     self.defineGivenVariable()
  #   elif reply == NO:
  #     print("no")
  #     self.__defineNewVarWithEquation()
  #   else:
  #     print("none")
  #   self.reset_table()

  def __defineNewVarWithEquation(self):
    self.new_variable.emit(self.selected_variable_type)

  ### table handling
  def on_tableVariable_itemClicked(self, item):

    # table control

    # columns are
    # 0 type --> new variable
    # 1 symbol
    # 2 description / documentation
    # 3 tokens
    # 4 units
    # 5 indices
    # 6 equations
    # 7 delete

    c = int(item.column())
    r = int(item.row())
    # print("debugg row chosen is: %s" % r)
    # print("debugg column chosen is: %s" % c)
    item = self.ui.tableVariable.item
    self.selected_variable_type = str(item(r, 0).text())  # DOC: here I know if a new dimension must be generated

    # picking only
    try:
      self.selected_variable_symbol = str(item(r, 1).text())   # in some circumstances this can be empty.
    except:
      return

    # get out if variable is disabled
    if self.selected_variable_symbol in self.disabled_variables:
      return

    # do not allow changing of units and index sets once in use or is defined via equation

    selected_ID = self.variables_in_table[r]
    self.selected_ID = selected_ID
    v = self.variables[selected_ID]

    print("debugging -- argument", selected_ID, self.variables.inv_incidence_dictionary[selected_ID])
    not_yet_used = (self.variables.inv_incidence_dictionary[selected_ID] == []) and \
                   (len(self.variables[selected_ID].equations.keys()) == 0)

    if c == 0:
      self.__change_variable_type_dialogue()
      return

    # execute requested command
    if c == 1:
      # print("clicked 1 - symbol ", self.selected_variable_symbol)
      self.__changeSymbol(v)
    elif c == 2:
      # print("clicked 2 - description ", v.doc)
      self.__changeDocumentation(v)
    elif c == 3:
      self.__changeToken(v)
      print("debugging token dialog")
    elif c == 4:
      print("clicked 4 - units ", v.units)
      if not_yet_used:
        self.__changeUnits(v)
    elif c == 5:
      print("clicked 5 - indexing ", v.index_structures)
      if not_yet_used:
        self.__changeIndexing(v)
    elif c == 6:
      # print("clicked 6 - equations ", selected_number_of_equations)
      self.new_equation.emit(selected_ID)
    elif c == 7:
      # print("clicked 7 - delete ")
      self.__showDeleteDialog(selected_ID)
    return

  def definePortVariable(self):
    var_ID = self.variables.newProMoVariableIRI()  # globalVariableID(update=True)
    #
    # NOTE: there is something fundamentally wrong as when using the default things go utterly wrong.. python ???
    variable_record = makeCompleteVariableRecord(var_ID,
                                                 label=NEW_VAR,
                                                 type=self.selected_variable_type,
                                                 network=self.network,
                                                 doc=NEW_VAR,
                                                 index_structures=[],
                                                 units=Units(),
                                                 equations={},
                                                 aliases={},
                                                 port_variable=True,
                                                 tokens=[],
                                                 )

    self.variables.addNewVariable(ID=var_ID, **variable_record)

    ## TODO: think about this once more -- problem is that one needs to define the variable first including units and dimensions. Thus a new function (button) must be used for this
    # # RULE: if we do not define a port variable in class <<state>>, automatically an instantiation is created.
    # if self.selected_variable_type != "state":
    #   var = self.variables[var_ID]
    #   value_internal = None
    #   for id in self.variables:
    #     if self.variables[id].label == "value":
    #       value_internal = self.variables[id].aliases["global_ID"]
    #
    #   var_string = var.aliases["global_ID"]
    #   if value_internal:
    #     rhs = CODE["global_ID"]["operator"]["Instantiate"] + \
    #                 CODE["global_ID"]["delimiter"]["("] + \
    #                 var_string + \
    #                 CODE["global_ID"]["delimiter"][","] + \
    #                 value_internal + \
    #                 CODE["global_ID"]["delimiter"][")"]
    #   else:
    #     rhs = CODE["global_ID"]["operator"]["Instantiate"] + \
    #           CODE["global_ID"]["delimiter"]["("] + \
    #           var_string + \
    #           CODE["global_ID"]["delimiter"][")"]

      # print("debugging")
      #
      # incidence_list = makeIncidentList(rhs)
      # equation_record = makeCompletEquationRecord(rhs,network=self.network,incidence_list=incidence_list)
      #
      # self.variables.addEquation(var_ID, equation_record)

    self.variables.indexVariables()
    self.reset_table()
    enabled_columns = ENABLED_COLUMNS["edit"]["constant"]
    self.enable_column_selection(enabled_columns)

  def __changeSymbol(self, variable): #, forbidden_symbols):
    forbidden_symbols = self.variables.index_accessible_variables_on_networks[self.network]#nameSpacesForVariableLabelGlobal
    # forbidden_symbols = []
    # for ID in self.variables_in_table:
    #   forbidden_symbols.append(self.variables[ID].label)
    self.ui_symbol.setUp(variable, forbidden_symbols)
    self.ui_symbol.show()

  def __changeUnits(self, phys_var):
    self.ui_units.setUp(phys_var)  # = UI_PhysUnitsDialog("new physical units", phys_var)
    # self.ui_units.finished.connect(self.reset_table)
    self.ui_units.show()

  def __changeDocumentation(self, phys_var):
    self.ui_documentation = UI_DocumentationDialog(phys_var)
    self.ui_documentation.finished.connect(self.reset_table)
    self.ui_documentation.show()

  def __changeIndexing(self, phys_var):  # TODO: when does this make sense ?
    self.phys_var = phys_var
    # version_change: the rule for the oonnection interfaces is too constraint
    if CONNECTION_NETWORK_SEPARATOR in phys_var.network:
      [source,sink] =  phys_var.network.split(CONNECTION_NETWORK_SEPARATOR)
      left_indices = set()
      right_indices = set()
      for id in self.indices:
        if source in self.indices[id]["network"]:
          left_indices.add(id)
        if sink in self.indices[id]["network"]:
          right_indices.add(id)
      joint_index = left_indices | right_indices
      index_structures_labels = []
      for id in joint_index:
        index_structures_labels.append(self.indices[id]["label"])

    else:
      self.label_ID_dict = self.__getIndexListPerNetwork(self.network)
      index_structures_labels = [self.indices[ind_ID]["label"] for ind_ID in self.label_ID_dict.keys()]


    try:
      del self.ui_selector
    except:
      pass
    self.ui_selector = UI_RadioSelector(index_structures_labels,
                                        phys_var.index_structures,
                                        allowed=5)  # RULE: number of allowed indices is currently 5
    self.ui_selector.newSelection.connect(self.__gotNewIndexStrucList)
    self.ui_selector.show()

  def __getIndexListPerNetwork(self, nw):
    label_ID_dict = {}
    for ind_ID in self.indices:
      for layer in self.indices[ind_ID]["network"]:
        if layer == nw:
          label_ID_dict[ind_ID] = self.indices[ind_ID]["label"]
    return label_ID_dict

  def __gotNewIndexStrucList(self, strucs_list):
    indexing_sets = [ind_ID for ind_ID in self.indices if self.indices[ind_ID][
      "label"] in strucs_list]
    self.phys_var.index_structures = indexing_sets
    self.reset_table()

  def __changeToken(self, phys_var):
    tokens = sorted(self.tokens_on_networks[self.network])
    if self.selected_variable_type == "constant":  # RULE: constants can be connected to tokens
      tokens_not_linked = tokens
    else:
      linked_tokens = self.variables.tokens_linked
      tokens_not_linked = []
      for token in tokens:
        if not linked_tokens[token]:
          tokens_not_linked.append(token)
      if len(tokens_not_linked) == 0:
        return
    print("debugging -- token list generation", tokens)
    self.phys_var = phys_var                          # used to change things
    try:
      del self.ui_selector
    except:
      pass
    self.ui_selector = UI_RadioSelector(tokens_not_linked,
                                        phys_var.tokens,
                                        allowed=1)  # RULE: number of allowed tokens is currently 1
    self.ui_selector.newSelection.connect(self.__gotNewTokens)
    self.ui_selector.show()

  def __gotNewTokens(self, token_list):
    print("debugging got tokens", token_list)
    self.phys_var.tokens = token_list
    self.reset_table()


  def on_pushFinished_pressed(self):
    self.closeEvent(None)

  def closeEvent(self, event):
    for ID in self.variables:
      if self.variables[ID].label == NEW_VAR:
        self.variables.removeVariable(ID)


    try:
      self.ui_symbol.close()
    except:
      pass

    try:
      self.ui_selector_tokens.close()
    except:
      pass

    try:
      self.ui_selector.close()
    except:
      pass

    try:
      self.ui_units.close()
    except:
      pass
    try:
      self.ui_documentation.close()
    except:
      pass


    self.completed.emit("close")

    self.close()
