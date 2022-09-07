#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI defining equations
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 03. 21"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
# from Common.common_resources import globalEquationID
# from Common.common_resources import globalVariableID
from Common.record_definitions import RecordEquation
from Common.record_definitions import makeCompletEquationRecord
from Common.record_definitions import makeCompleteVariableRecord
from Common.resources_icons import roundButton
from Common.single_list_selector_impl import SingleListSelector
# from OntologyBuilder.OntologyEquationEditor.resources import INSTANTIATE_EQ_NO
from OntologyBuilder.OntologyEquationEditor.resources import NEW_EQ
from OntologyBuilder.OntologyEquationEditor.resources import NEW_VAR
from OntologyBuilder.OntologyEquationEditor.resources import OPERATOR_SNIPS
from OntologyBuilder.OntologyEquationEditor.resources import PORT
from OntologyBuilder.OntologyEquationEditor.resources import TEMPLATES
from OntologyBuilder.OntologyEquationEditor.resources import UNDEF_EQ_NO
from OntologyBuilder.OntologyEquationEditor.resources import renderExpressionFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.resources import renderIndexListFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.resources import setValidator
from OntologyBuilder.OntologyEquationEditor.tpg import LexicalError
from OntologyBuilder.OntologyEquationEditor.tpg import SemanticError
from OntologyBuilder.OntologyEquationEditor.tpg import SyntacticError
from OntologyBuilder.OntologyEquationEditor.tpg import WrongToken
from OntologyBuilder.OntologyEquationEditor.ui_equations import Ui_Form
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_pick_impl import UI_VariableTablePick
from OntologyBuilder.OntologyEquationEditor.variable_framework import CompileSpace
from OntologyBuilder.OntologyEquationEditor.variable_framework import Expression
from OntologyBuilder.OntologyEquationEditor.variable_framework import IndexStructureError
from OntologyBuilder.OntologyEquationEditor.variable_framework import UnitError
from OntologyBuilder.OntologyEquationEditor.variable_framework import Units
from OntologyBuilder.OntologyEquationEditor.variable_framework import VarError
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidentList


class UI_Equations(QtWidgets.QWidget):
  """
  user interface for the equation definition
  """

  update_space_information = QtCore.pyqtSignal()
  def_given_variable = QtCore.pyqtSignal()

  def __init__(self,
               what,  # what: string "network" | "interface" | "intraface"
               variables,
               indices,
               network_for_variable,
               network_for_expression,
               variable_types_variable,
               variable_types_expression,
               enabled_variable_types=[],
               # global_name_space = True
               ):
    """
    Constructor
    """
    QtWidgets.QWidget.__init__(self)
    self.ui = Ui_Form()
    self.ui.setupUi(self)

    roundButton(self.ui.pushAccept, "accept")  # , tooltip="accept")
    roundButton(self.ui.pushDeleteEquation, "delete", tooltip="delete")
    roundButton(self.ui.pushCancel, "reject", tooltip="cancel")
    # roundButton(self.ui.pushResetInterface, "reset", tooltip="reset")

    self.ontology_container = variables.ontology_container
    self.hide()
    self.what = what
    self.variables = variables
    self.indices = indices
    self.index_definition_networks_for_variable = variables.index_definition_networks_for_variable[network_for_variable]
    _l = sorted(indices.keys())
    self.index_list = [indices[i]["aliases"]["internal_code"] for i in _l]
    self.network_for_variable = network_for_variable
    self.network_for_expression = network_for_expression
    # self.actual_network_for_expression = network_for_expression  # may change if equation is edited
    self.variable_types_variable = variable_types_variable
    self.variable_types_expression = variable_types_expression
    self.enabled_variable_types = enabled_variable_types
    # self.global_name_space = global_name_space

    self.equation_documentation = ""

    self.status_edit_expr = False
    self.status_new_variable = False
    self.status_new_equation = False

    # TODO: equation editing -- control when to allow editing of an equation. Currently it is not controlled over the
    #  network d.h. if one has defined a equation on macro as a second equation whilst the first was defined on
    #  physical, then the equation can be edited on physical even though it remains (now) on the macro layer.

    self.ui.labelNetwork.setText(network_for_variable)
    self.__makePickVariableTable()

    self.operator_table = SingleListSelector(thelist=OPERATOR_SNIPS)
    self.operator_table.hide()
    self.operator_table.newSelection.connect(self.__insertSnipp)

    self.resetEquationInterface()
    self.MSG = self.ui.textBrowser.setText
    self.appendMSG = self.ui.textBrowser.append
    self.MSG("ready")
    self.hide()
    self.ui.lineNewVariable.setFocus()

  def __makePickVariableTable(self):

    self.variable_tables = {}
    if self.what == "interface":  # CONNECTION_NETWORK_SEPARATOR in self.network_for_expression:
      [source, sink] = self.network_for_expression.split(CONNECTION_NETWORK_SEPARATOR)
      network = source
      enabled_var_types = {
              self.network_for_variable: self.variable_types_variable,
              source                   : self.variable_types_expression
              }
    elif self.what == "intraface":
      enabled_var_types = {
              self.network_for_variable  : self.variable_types_variable,
              self.network_for_expression: self.variable_types_expression
              }
      network = self.network_for_variable

    else:
      # RULE: the variables from the interconnection nodes that potentially connect are also included as sources
      if self.network_for_variable != self.network_for_expression:
        enabled_var_types = {
                self.network_for_variable  : self.variable_types_variable,
                self.network_for_expression: self.variable_types_expression
                }
      else:
        enabled_var_types = {
                self.network_for_expression: self.variable_types_expression
                }
      network = self.network_for_variable

    self.variable_tables[network] = UI_VariableTablePick('Pick variable symbol \nnetwork %s' % network,
                                                         self.variables,
                                                         self.indices,
                                                         network,
                                                         enabled_types=enabled_var_types[network],
                                                         hide_vars=[NEW_VAR],
                                                         hide_columns=[0, 6, 7],
                                                         )
    self.variable_tables[network].hide()
    self.variable_tables[network].picked.connect(self.__insertSnipp)
    # for nw in networks:   # there are two for intra faces but only one for all the others

  def closeEvent(self, event):
    try:
      self.ui_equationselector.close()
    except:
      pass
    try:
      self.ui_indices.close()
    except:
      pass
    # for nw in self.variable_tables:
    try:
      [self.variable_tables[nw].close() for nw in self.variable_tables]
    except:
      pass
    try:
      self.operator_table.close()
    except:
      pass
    self.close()

  @QtCore.pyqtSlot(str)
  def __insertSnipp(self, text):
    # print("debugging inserting snipp :", text)
    # TODO: fix templates
    try:
      starting, ending = self.text_range
    except:
      starting, ending = 0, 0
    t = str(self.ui.lineExpression.text())
    s = t[0:starting] + text + t[ending:]
    self.ui.lineExpression.setText(s)
    self.ui.lineExpression.setFocus(True)
    self.show()
    # self.ui.lineExpression.cursorWordBackward(False)
    # self.ui.lineExpression.cursorWordForward(False)

  def resetEquationInterface(self):
    self.__makePickVariableTable()
    self.ui_indices = SingleListSelector(self.index_list)
    self.ui_indices.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    self.ui_indices.newSelection.connect(self.__insertSnipp)
    # self.hide()
    self.ui.lineExpression.clear()
    self.ui.lineNewVariable.clear()
    self.ui.lineDocumentation.clear()
    self.ui.lineNewVariable.setFocus()
    # reg_ex =QtCore.QRegExp("[a-zA-Z_]\msg_box*")  #TODO: check on validator
    # validator = QtGui.QRegExpValidator(VAR_REG_EXPR, self.ui.lineNewVariable)
    # self.ui.lineNewVariable.setValidator(validator)
    setValidator(self.ui.lineNewVariable)
    self.ui.pushAccept.hide()
    # self.ui.groupEquationEditor.hide()
    self.ui_indices.hide()
    self.selected_variable_type = None
    self.selected_variable_ID = ''
    self.update()

  def setupNewVariable(self, variable_type):
    variable_type = str(variable_type)
    print("setup new variable: %s" % variable_type)
    self.resetEquationInterface()
    self.selected_variable_type = variable_type
    self.ui.groupEquationEditor.show()
    self.ui.lineExpression.hide()
    self.status_new_variable = True
    self.status_new_equation = True
    self.ui.pushDeleteEquation.hide()
    self.ui.lineNewVariable.setReadOnly(False)
    self.show()
    self.MSG("new variable")

  def setupNewEquation(self, variable_ID):
    self.selected_variable_type = self.variables[variable_ID].type
    self.setupEquationList(variable_ID)
    self.ui.groupEquationEditor.show()

    self.ui.lineNewVariable.setReadOnly(True)
    self.status_new_variable = False
    self.ui.pushAccept.hide()

    # self.ui.lineExpression.show()
    self.status_new_equation = True
    self.ui.lineDocumentation.show()
    self.MSG("new equation")

  def on_lineNewVariable_returnPressed(self):  # TODO: check on validator
    symbol = str(self.ui.lineNewVariable.text())  # RULE: changed from local name space to global name space
    # if self.global_name_space:
    #   test = self.variables.existSymbolGlobal(symbol)
    # else:
    test = self.variables.existSymbol(self.network_for_variable, symbol)
    if test:
      self.MSG("variable already defined")
      self.ui.lineExpression.hide()
      return
    self.MSG("variable symbol OK")
    self.ui.lineExpression.show()
    self.ui.lineExpression.setFocus()

  def on_lineExpression_returnPressed(self):
    # make variable available for checking in implicit (root) operator
    self.variables.to_define_variable_name = str(self.ui.lineNewVariable.text())

    if self.__checkExpression():
      self.ui.pushAccept.show()
    else:
      self.ui.pushAccept.hide()

  def on_lineExpression_cursorPositionChanged(self, old, new):
    starting = new
    ending = new
    if self.ui.lineExpression.hasSelectedText():
      text = str(self.ui.lineExpression.selectedText())
      starting = self.ui.lineExpression.selectionStart()
      ending = starting + len(text)
    self.text_range = starting, ending

  def on_lineExpression_textChanged(self, text):
    self.ui.pushAccept.hide()
    self.ui.pushDeleteEquation.hide()

  def on_lineNewVariable_textChanged(self, text):
    # print("debugging -- text change", text)
    if not self.status_new_variable:
      return
    # rule: changed from local name space to global name space
    # rule enable both
    # if self.global_name_space:
    #   test = self.variables.existSymbolGlobal(text)
    # else:
    test = self.variables.existSymbol(self.network_for_variable, text)
    if test:  # if :
      self.MSG("variable already defined")
    else:
      self.MSG("OK")
      return

  def __checkExpression(self):
    # print("debugging checking expression")
    print("   new variable : %s \n new equation :%s \n edit expression %s"
          % (self.status_new_variable, self.status_new_equation, self.status_edit_expr))
    s = str(self.ui.lineExpression.text())
    self.expr = s.strip()

    # expression must compile
    try:
      self.compile_space = CompileSpace(self.variables, self.indices, self.network_for_variable,
                                        self.network_for_variable, language="global_ID")
      expression = Expression(self.compile_space)
      self.checked_var = expression(self.expr)
      print('self.checked_var:  ', self.checked_var)

      if "PhysicalVariable" in str(self.checked_var.__class__):  # RULE: copy of variable is not allowed
        if self.network_for_variable == self.checked_var.network:  # RULE: that is if they belong to the same network
          self.MSG('cannot be a copy of a variable')
          return False

      # self.checked_var.incidence_list = expression.space.getIncidenceList()
      # print('variable from expression', self.checked_var, 'are :', self.checked_var.incidence_list)
      pretty_check_var_indices = renderIndexListFromGlobalIDToInternal(self.checked_var.index_structures, self.indices)
      pretty_check_var_units = str(self.checked_var.units.prettyPrint(mode="string"))
      if not self.status_new_variable:
        var = self.variables[self.selected_variable_ID]
        pretty_var_indices = renderIndexListFromGlobalIDToInternal(var.index_structures, self.indices)
        pretty_var_units = str(var.units.prettyPrint(mode="string"))

        if self.variables.inv_incidence_dictionary[self.selected_variable_ID] == []:
          pass  # all OK
        # elif self.checked_var.units == var.units:
        if self.checked_var.units == var.units:
          if self.checked_var.index_structures == var.index_structures:
            if self.checked_var.tokens == var.tokens:
              msg = "variable has \n" \
                    "- index structures : %s\n" \
                    "- units            : %s\n" \
                    "- tokens           : %s\n" % (pretty_var_indices, pretty_var_units, var.tokens)
              self.MSG(msg)
            else:
              msg = "missmatch of tokens \n" \
                    " - variable has   : %s\n" \
                    " - expression has : %s\n" \
                    % (self.checked_var.tokens, var.tokens)
          else:
            msg = "missmatch of index structures \n" \
                  " - variable has   : %s\n" \
                  " - expression has : %s\n" \
                  % (pretty_var_indices, pretty_check_var_indices)
            self.MSG(msg)
            return False
        else:
          diff_unit = []
          checked_var_units_list = self.checked_var.units.asList()
          var_units_list = var.units.asList()
          for i in range(len(checked_var_units_list)):
            diff_unit.append(checked_var_units_list[i] - var_units_list[i])
          units = Units(ALL=diff_unit)
          pretty_diff = units.prettyPrint(mode="string")

          msg = "missmatch of units     \n" \
                " - variable has   : %s \n" \
                " - expression has : %s \n" \
                " - difference is  : %s" \
                % (pretty_var_units, pretty_check_var_units, pretty_diff)
          self.MSG(msg)
          return False
      # else:
      # print("debugging : ", expression)
      msg = 'modified expression OK\n index struct: %s\n units: %s\n tokens: %s\n' % (
              pretty_check_var_indices, pretty_check_var_units, self.checked_var.tokens)
      self.MSG(msg)
      #       print("debugging: ", msg)

      return True

    except (VarError,
            SemanticError,
            SyntacticError,
            LexicalError,
            WrongToken,
            UnitError,
            IndexStructureError
            ) as _m:
      self.MSG('checked expression failed with error %s' % (_m))
      return False

  # ## Buttons ==============================

  def on_pushDeleteEquation_pressed(self):
    v = self.selected_variable
    v.removeEquation(self.current_eq_ID)  # remove from variable def
    # self.variables.index_equation_in_definition_network()
    self.variables.indexVariables()
    self.ontology_container.indexEquations()
    self.update_space_information.emit()
    self.close()

  def dummy(self, selected_list):
    pass

  def on_pushAccept_pressed(self):
    symbol = str(self.ui.lineNewVariable.text())
    documentation = str(self.ui.lineDocumentation.text())
    rhs = str(self.checked_var)
    incidence_list = makeIncidentList(rhs)
    equation_record = makeCompletEquationRecord(rhs=rhs,
                                                doc=documentation,
                                                network=self.network_for_expression,
                                                incidence_list=incidence_list
                                                )
    # Note: think about allowing for editing an equation. It easily destroys the sequence.
    # Note:   by adding a term with a variable that depends on "later" information......!!! (H)
    # incremental expansions
    # TODO: does not really cover all issues - if one changes an equation, all equations that depend on the variable
    #  would have to be re-done recursively.
    # TODO - so this implies that one can just as well do a graph analysis one one is done. Consequence is that the
    #  equation iri is not important at all in the context of ordering equations for maintaining the correct
    #  computations sequence
    # RULE: we do not care anymore maintaining the sequence. The bipartite graph analysis takes care of sequencing

    print("status new variable, new equation, edit expression", self.status_new_variable, self.status_new_equation,
          self.status_edit_expr)

    log = (self.status_new_variable, self.status_new_equation, self.status_edit_expr)
    # new variable true, true, false
    if (log == (True, True, True)) or (log == (True, True, False)):
      var_ID = self.variables.newProMoVariableIRI()
      equ_ID = self.variables.newProMoEquationIRI()  # globalEquationID(update=True)  # RULE: for global ID
      tokens = self.checked_var.tokens  # version_change: and this is the replacement

      variable_record = makeCompleteVariableRecord(var_ID,
                                                   label=symbol,
                                                   type=self.selected_variable_type,
                                                   network=self.network_for_variable,
                                                   doc=documentation,
                                                   index_structures=self.checked_var.index_structures,
                                                   units=self.checked_var.units,
                                                   equations={
                                                           equ_ID: equation_record
                                                           },
                                                   aliases={},
                                                   port_variable=False,
                                                   tokens=tokens,
                                                   )

      self.variables.addNewVariable(ID=var_ID, **variable_record)

    # new equation to existing variable false, true, false
    elif log == (False, True, False):
      var_ID = self.selected_variable_ID
      self.variables.addEquation(var_ID, equation_record)
      self.ontology_container.indexEquations()


    # edit equation false, false, true
    elif log == (False, False, True):
      var_ID = self.selected_variable_ID
      old_equ_ID = self.current_eq_ID
      # RULE: editing replaces the existing equation -- consquence - sequence is not retained.
      self.variables.replaceEquation(var_ID, old_equ_ID, equation_record)

    self.variables.indexVariables()
    self.ontology_container.indexEquations()
    self.update_space_information.emit()

    self.ui.groupEquationEditor.hide()
    self.resetEquationInterface()

    self.ui_indices.close()
    [self.variable_tables[nw].close() for nw in self.variable_tables]
    self.operator_table.close()

    self.hide()
    self.close()

  @staticmethod
  def __printDelete():
    print('going to delete')

  def __setupEditAndDelete(self):
    # TODO: set tooltips

    self.ui.pushDeleteEquation.hide()
    if self.current_alternative != NEW_EQ:
      equs_dict = self.variables[self.selected_variable_ID].equations
      eq_dict = equs_dict[self.current_eq_ID]
      self.current_expression = eq_dict["rhs"]
      if len(equs_dict) > 1:
        self.ui.pushDeleteEquation.show()
      rendered_expression = renderExpressionFromGlobalIDToInternal(self.current_expression, self.variables,
                                                                   self.indices)
      self.ui.lineExpression.setText(rendered_expression)
      self.ui.lineDocumentation.setText(eq_dict["doc"])
    else:
      e = RecordEquation()
      e["name"] = self.selected_variable.doc
      e["rhs"] = NEW_EQ
      self.ui.lineExpression.setText(e["rhs"])
      self.current_equation_name = e["name"]
      eq_IDs = sorted(self.variables[self.selected_variable_ID].equations.keys())
      if eq_IDs:
        doc = self.variables[self.selected_variable_ID].equations[eq_IDs[0]]["doc"]  # copy doc from the first equation
      else:
        doc = self.variables[self.selected_variable_ID].doc
      self.ui.lineDocumentation.setText(doc)

    self.ui.lineNewVariable.setText(self.variables[self.selected_variable_ID].label)
    self.ui.groupEquationEditor.show()
    self.show()

  def setupEquationList(self, variable_ID):
    ask_string = "%s"  # eq number
    ask_string += TEMPLATES["definition_delimiter"]
    ask_string += "%s"  # lhs
    ask_string += " " + TEMPLATES['Equation_definition_delimiter']
    ask_string += "%s"  # equ_rendered
    v = self.variables[variable_ID]
    self.selected_variable = v
    self.selected_variable_ID = variable_ID
    lhs = self.variables[variable_ID].label
    equation_list = sorted(v.equations.keys())
    # print('debugging - got dictionary')
    # _list = [UNDEF_EQ_NO + TEMPLATES['Equation_definition_delimiter'] + NEW_EQ]
    _list = [ask_string % (UNDEF_EQ_NO, lhs, NEW_EQ)]
    for alterntative in equation_list:
      rhs = self.variables[variable_ID].equations[alterntative]["rhs"]
      equ_rendered = renderExpressionFromGlobalIDToInternal(rhs, self.variables, self.indices)
      # _list.append(str(alterntative)
      #              + TEMPLATES["definition_delimiter"]
      #              + lhs
      #              + " "
      #              + TEMPLATES['Equation_definition_delimiter']
      #              + equ_rendered)
      _list.append(ask_string % (alterntative, lhs, equ_rendered))
    self.ui_equationselector = SingleListSelector(_list)
    self.ui_equationselector.show()
    self.ui_equationselector.newSelection.connect(self.__selectedEquation)

  def __selectedEquation(self, entry):
    # print('debugging got it', entry)
    eq_no, reminder = entry.split(TEMPLATES['definition_delimiter'], 1)
    _reminder, eq_string = reminder.split(TEMPLATES["Equation_definition_delimiter"])
    if eq_no != UNDEF_EQ_NO:
      self.current_eq_ID = int(eq_no)
      self.status_edit_expr = True
    self.current_alternative = eq_string
    self.status_new_equation = (eq_string == NEW_EQ)
    if eq_string == PORT:
      self.__defGivenVariable()
      return
    self.__setupEditEquation()

  def __setupEditEquation(self):
    self.__setupEditAndDelete()
    v = self.selected_variable
    self.ui.pushDeleteEquation.show()
    self.show()

  def __defGivenVariable(self):
    self.def_given_variable.emit()

  def on_pushPickVariables_pressed(self):
    [self.variable_tables[nw].show() for nw in self.variable_tables]

  def on_pushPickOperations_pressed(self):
    self.operator_table.show()

  def on_pushPickIndices_pressed(self):
    self.ui_indices.show()

  #
  # def on_pushResetInterface_pressed(self):
  #   self.resetEquationInterface()

  def on_pushCancel_pressed(self):
    self.resetEquationInterface()
    self.close()
