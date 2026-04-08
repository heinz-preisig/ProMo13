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

from Common.common_resources import VARIABLE_TYPE_INTERFACE
from Common.record_definitions import makeCompletEquationRecord
from Common.record_definitions import makeCompleteVariableRecord
from Common.resources_icons import roundButton
from Common.single_list_selector_impl import SingleListSelector
from Common.ui_show_equation_list_impl import UI_ShowVariableEquation
from OntologyBuilder.EquationEditor_v01.resources import CODE
from OntologyBuilder.EquationEditor_v01.resources import NEW_EQ
from OntologyBuilder.EquationEditor_v01.resources import NEW_VAR
from OntologyBuilder.EquationEditor_v01.resources import OPERATOR_SNIPS
from OntologyBuilder.EquationEditor_v01.resources import PORT
from OntologyBuilder.EquationEditor_v01.resources import dateString
from OntologyBuilder.EquationEditor_v01.resources import renderExpressionFromGlobalIDToInternal
from OntologyBuilder.EquationEditor_v01.resources import renderIndexListFromGlobalIDToInternal
from OntologyBuilder.EquationEditor_v01.resources import setValidator
from OntologyBuilder.EquationEditor_v01.tpg import LexicalError
from OntologyBuilder.EquationEditor_v01.tpg import SemanticError
from OntologyBuilder.EquationEditor_v01.tpg import SyntacticError
from OntologyBuilder.EquationEditor_v01.tpg import WrongToken
from OntologyBuilder.EquationEditor_v01.ui_equations import Ui_Form
from OntologyBuilder.EquationEditor_v01.ui_variabletable_pick_impl import UI_VariableTablePick
from OntologyBuilder.EquationEditor_v01.variable_framework import CompileSpace
from OntologyBuilder.EquationEditor_v01.variable_framework import EquationDeleteError
from OntologyBuilder.EquationEditor_v01.variable_framework import Expression
from OntologyBuilder.EquationEditor_v01.variable_framework import IndexStructureError
from OntologyBuilder.EquationEditor_v01.variable_framework import UnitError
from OntologyBuilder.EquationEditor_v01.variable_framework import Units
from OntologyBuilder.EquationEditor_v01.variable_framework import VarError
from OntologyBuilder.EquationEditor_v01.variable_framework import makeCompilerForNetwork
from OntologyBuilder.EquationEditor_v01.variable_framework import makeIncidentList


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

        self.setWindowFlags(
                self.windowFlags() |
                QtCore.Qt.WindowStaysOnTopHint |
                QtCore.Qt.FramelessWindowHint |
                QtCore.Qt.Dialog
                )

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        roundButton(self.ui.pushAccept, "accept", tooltip="accept")
        roundButton(self.ui.pushDeleteEquation, "delete", tooltip="delete")
        roundButton(self.ui.pushCancel, "reject", tooltip="cancel")

        self.ontology_container = variables.ontology_container
        self.hide()
        self.what = what
        self.variables = variables
        self.indices = indices
        self.index_definition_networks_for_variable = variables.index_definition_networks_for_variable[
            network_for_variable]
        _l = sorted(indices.keys())
        self.index_list = [indices[i]["aliases"]["internal_code"] for i in _l]
        self.network_for_variable = network_for_variable
        self.network_for_expression = network_for_expression
        self.variable_types_variable = variable_types_variable
        self.variable_types_expression = variable_types_expression
        self.enabled_variable_types = enabled_variable_types

        self.equation_documentation = ""

        self.status_edit_expr = False
        self.status_new_variable = False
        self.status_new_equation = False

        self.to_define_latex_alias = ""

        # TODO: equation editing -- control when to allow editing of an equation. Currently it is not controlled over the
        #  network d.h. if one has defined a equation on macro as a second equation whilst the first was defined on
        #  physical, then the equation can be edited on physical even though it remains (now) on the macro layer.

        self.ui.labelNetwork.setText(network_for_variable)

        self.operator_table = SingleListSelector(thelist=OPERATOR_SNIPS)
        self.operator_table.hide()
        self.operator_table.newSelection.connect(self.__insertSnipp)

        self.resetEquationInterface()
        self.MSG = self.ui.textBrowser.setText
        self.appendMSG = self.ui.textBrowser.append
        self.MSG("ready")
        self.hide()
        self.ui.lineNewVariable.setFocus()

        self.ui.pushPickIndices.hide()  # NOTE: disabled -- little used

    def __makePickVariableTable(self):

        self.variable_tables = {}

        enabled_var_types = {
                self.network_for_expression: self.variable_types_expression
                }
        network = self.network_for_variable
        which = "variable_picking"

        # Create networks list: current domain + interface domain (if exists)
        networks = [network]
        if hasattr(self.variables, 'interface_domain') and self.variables.interface_domain:
            networks.append(self.variables.interface_domain)

        # Create single table that handles multiple networks
        self.variable_tables[network] = UI_VariableTablePick('Pick variable symbol \nnetwork %s' % network,
                                                             self.variables,
                                                             self.indices,
                                                             networks[0],  # Pass first network as primary network
                                                             networks=networks,  # Pass multiple networks
                                                             enabled_types=enabled_var_types[network],
                                                             hide_vars=[NEW_VAR],
                                                             hide_columns=[0, 6, 7],
                                                             which=which,
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

        # Convert variable ID to variable label for display
        display_text = text
        if text in self.variables:
            # It's a variable ID, use its label
            display_text = self.variables[text].label
        elif "!" in text:
            # It's already in network!variable format, use as-is
            display_text = text

        t = str(self.ui.lineExpression.text())
        s = t[0:starting] + display_text + t[ending:]
        self.ui.lineExpression.setText(s)
        self.ui.lineExpression.setFocus(True)
        self.show()

    def resetEquationInterface(self):

        self.status_new_variable, self.status_new_equation, self.status_edit_expr = (False, False,
                                                                                     False)  # reset status
        self.ui_indices = SingleListSelector(self.index_list, alternative=True,
                                             left=("reject", "reject", "show"),
                                             right=("accept", "accept", "show"))

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
        v = self.variables[variable_ID]
        self.selected_variable_type = v.type
        self.setupEquationList(variable_ID)
        self.ui.groupEquationEditor.show()

        self.ui.lineNewVariable.setReadOnly(True)
        self.status_new_variable = False
        self.ui.pushAccept.hide()

        self.ui.labelLaTex.show()
        self.ui.lineEditLatex.show()
        self.ui.lineEditLatex.setText(v.aliases["latex"])

        self.status_new_equation = True
        self.ui.lineDocumentation.show()
        self.MSG("new equation")

    def on_lineNewVariable_returnPressed(self):  # TODO: check on validator
        symbol = str(self.ui.lineNewVariable.text())
        test = self.variables.existSymbol(self.network_for_variable, symbol)
        if test:
            self.MSG("variable already defined")
            self.ui.lineExpression.hide()
            return

        self.to_define_latex_alias = str(self.ui.lineNewVariable.text())
        self.ui.labelLaTex.show()
        self.ui.lineEditLatex.setText(self.to_define_latex_alias)

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
            # makeCompilerForNetwork(self.variables, self.indices, )
            self.compile_space = CompileSpace(self.variables, self.indices, self.network_for_variable,
                                              self.network_for_variable, language="global_ID")
            expression = Expression(self.compile_space)
            self.checked_var = expression(self.expr)
            # print('self.checked_var:  ', self.checked_var)  # Commented out due to language attribute error

            if "PhysicalVariable" in str(self.checked_var.__class__):  # RULE: copy of variable is not allowed
                if self.network_for_variable == self.checked_var.network:  # RULE: that is if they belong to the same network
                    self.MSG('cannot be a copy of a variable')
                    return False

            pretty_check_var_indices = renderIndexListFromGlobalIDToInternal(self.checked_var.index_structures,
                                                                             self.indices)
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
                        # if self.checked_var.tokens == var.tokens:
                        msg = "variable has \n" \
                              "- index structures : %s\n" \
                              "- units            : %s\n" \
                              "- tokens           : %s\n" % (pretty_var_indices, pretty_var_units, var.tokens)
                        self.MSG(msg)
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

            msg = 'modified expression OK\n index struct: %s\n units: %s\n \n' % (
                    pretty_check_var_indices, pretty_check_var_units)
            self.MSG(msg)

            # check memory for all variables
            try:
                incide_list = makeIncidentList(str(self.checked_var))
            except AttributeError:
                # Handle missing language attribute - use variable ID instead
                incide_list = [self.checked_var.ID] if hasattr(self.checked_var, 'ID') else []
            memory_value_set = set()
            self.memory = None

            for v in incide_list:
                memory = self.variables[v].memory
                if memory:
                    memory_value_set.add(memory)
                    pass
            if len(memory_value_set) > 1:

                msg = "memory variable mismatch\n"
                for v in incide_list:
                    msg += "- variable %s has memory variable %s\n" % (self.variables[v].label,
                                                                       self.variables[v].memory)
                self.MSG(msg)

                raise VarError(msg)

            elif len(memory_value_set) == 1:
                self.memory = list(memory_value_set)[0]

            print("debugging: ", msg)

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
        try:
            v.removeEquation(self.current_eq_ID)  # remove from variable def
        except EquationDeleteError:
            return
        self.variables.indexVariables()
        self.ontology_container.indexEquations()
        self.update_space_information.emit()
        self.close()

    def dummy(self, selected_list):
        pass

    def on_pushAccept_pressed(self):
        symbol = str(self.ui.lineNewVariable.text())
        documentation = str(self.ui.lineDocumentation.text())
        rhs = str(self.checked_var)  # Revert to original - the str() issue should be fixed elsewhere
        incidence_list = makeIncidentList(rhs)

        # ====================== make residual equation =============================
        is_root = CODE["global_ID"]["function"]["Root"] in rhs
        if is_root:
            # Rule: root equation -- generate residual representation
            self.__makeRootResidualEquation(rhs)

        # now add the latex version of the expression
        compilers = {}
        for language in ["latex", "global_ID"]:
            compilers[language] = makeCompilerForNetwork(self.variables,
                                                         self.indices,
                                                         self.network_for_variable,
                                                         self.network_for_variable,
                                                         language=language,
                                                         verbose=0)

        expression_global = str(compilers["global_ID"](self.expr))
        expression_latex = str(compilers["latex"](self.expr))

        rhs_dic = {
                "global_ID": expression_global,
                "latex"    : expression_latex
                }  # str(self.expression_latex)}

        if self.status_new_variable:
            var_ID = self.variables.newProMoVariableIRI()
        else:
            var_ID = self.selected_variable_ID

        equation_record = makeCompletEquationRecord(rhs=rhs_dic, network=self.network_for_expression, doc=documentation,
                                                    incidence_list=incidence_list, created=dateString())
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

            equ_ID = self.variables.newProMoEquationIRI()  # globalEquationID(update=True)  # RULE: for global ID
            tokens = []

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
                                                         memory=self.memory,
                                                         )

            self.variables.addNewVariable(ID=var_ID, **variable_record)

        # new equation to existing variable false, true, false
        elif log == (False, True, False):
            self.variables.addEquation(var_ID, equation_record)
            self.ontology_container.indexEquations()

        # edit equation false, false, true
        elif (log == (False, False, True)) or (log == (False, True, True)):
            old_equ_ID = self.current_eq_ID
            # RULE: editing replaces the existing equation -- consquence - sequence is not retained.
            self.variables.replaceEquation(var_ID, old_equ_ID, equation_record)

        else:
            self.MSG("wrong logics")

        alias = self.ui.lineEditLatex.text()
        self.variables.changeVariableAlias(var_ID, "latex", alias)


        # print("debugging -- alias", alias)
        self.variables.indexVariables()
        self.ontology_container.indexEquations()
        self.update_space_information.emit()

        self.ui.groupEquationEditor.hide()
        self.resetEquationInterface()

        self.ui_indices.close()
        try:
            [self.variable_tables[nw].close() for nw in self.variable_tables]
        except:
            pass
        self.operator_table.close()

        self.hide()
        self.close()

    def __makeRootResidualEquation(self, rhs: str):
        root_argument = rhs.split(" ")[3]
        # equations = self.variables[root_argument].equations
        v = self.variables[root_argument]
        argument = v.label
        equation_list = sorted(v.equations.keys())
        loc = self.variables.ontology_container.latex_image_location
        dialog = UI_ShowVariableEquation(equation_list, loc,
                                         mode="select",
                                         prompt="select an equation for the residual formation -- a must",
                                         buttons=[])

        root = CODE["internal_code"]["Root"]
        minus = CODE["internal_code"]["-"]
        equation = v.equations[dialog.answer]["rhs"]["global_ID"]
        expression_network = v.equations[equ_ID]["network"]
        equation_rendered = renderExpressionFromGlobalIDToInternal(equation,
                                                                   self.variables,
                                                                   self.indices,
                                                                   expression_network)
        second = CODE["internal_code"]["bracket"] % equation_rendered
        new_argument = minus % (argument, second)
        self.expr = root % new_argument

        pass


    @staticmethod
    def __printDelete():
        print('going to delete')

    def __setupEditAndDelete(self):
        # TODO: set tooltips

        self.ui.pushDeleteEquation.hide()
        if self.current_alternative != NEW_EQ:
            equs_dict = self.variables[self.selected_variable_ID].equations
            eq_dict = equs_dict[self.current_eq_ID]
            self.current_expression = eq_dict["rhs"]["global_ID"]
            equation_network = eq_dict["network"]
            if len(equs_dict) > 1:
                self.ui.pushDeleteEquation.show()
            rendered_expression = renderExpressionFromGlobalIDToInternal(self.current_expression,
                                                                         self.variables,
                                                                         self.indices,
                                                                         equation_network)
            self.ui.lineExpression.setText(rendered_expression)
            self.ui.lineDocumentation.setText(eq_dict["doc"])
        else:
            self.ui.lineExpression.setText(NEW_EQ)
            self.current_equation_name = self.selected_variable.doc
            eq_IDs = sorted(self.variables[self.selected_variable_ID].equations.keys())
            if eq_IDs:
                doc = self.variables[self.selected_variable_ID].equations[eq_IDs[0]][
                    "doc"]  # copy doc from the first equation
            else:
                doc = self.variables[self.selected_variable_ID].doc
            self.ui.lineDocumentation.setText(doc)

        self.ui.lineNewVariable.setText(self.variables[self.selected_variable_ID].label)
        self.ui.groupEquationEditor.show()
        self.show()

    def setupEquationList(self, variable_ID):
        v = self.variables[variable_ID]
        self.selected_variable = v
        self.selected_variable_ID = variable_ID
        # lhs = self.variables[variable_ID].label
        equation_list = sorted(v.equations.keys())
        loc = self.variables.ontology_container.latex_image_location
        dialog = UI_ShowVariableEquation(equation_list, loc,
                                         mode="select",
                                         prompt="new equation or edit selection ?",
                                         buttons=["back", "new"])
        if dialog.answer == "new":
            self.__selectedEquation("new")
        elif dialog.answer == "back":
            return
        else:
            self.__selectedEquation(dialog.answer)
            return

    def __selectedEquation(self, entry):
        print('debugging got it', entry)
        if entry == "new" or entry == []:
            self.current_alternative = NEW_EQ
        else:
            self.current_eq_ID = entry  # eq_no
            self.status_edit_expr = True
            rhs = self.selected_variable.equations[entry]["rhs"]["global_ID"]
            equation_network = self.selected_variable.equations[entry]["network"]
            equ_rendered = renderExpressionFromGlobalIDToInternal(rhs,
                                                                  self.variables,
                                                                  self.indices,
                                                                  equation_network)
            self.current_alternative = equ_rendered

        self.status_new_equation = (entry == NEW_EQ)
        if entry == PORT:
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
        self.__makePickVariableTable()
        for nw in self.variable_tables:
            self.variable_tables[nw].show()

    def on_pushPickOperations_pressed(self):
        self.operator_table.show()

    def on_pushPickIndices_pressed(self):
        self.ui_indices.show()

    def on_pushCancel_pressed(self):
        self.resetEquationInterface()
        self.close()

    def mousePressEvent(self, event):  # Note: makes it movable
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):  # Note: makes it movable
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
