#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2014. 08. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import subprocess
from collections import OrderedDict

from jinja2 import Environment  # sudo apt-get install python-jinja2
from jinja2 import FileSystemLoader
from pydotplus.graphviz import Cluster
from pydotplus.graphviz import Dot
from pydotplus.graphviz import Edge
from pydotplus.graphviz import Node
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QSizePolicy

from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.common_resources import getData
from Common.common_resources import getOntologyName
from Common.common_resources import makeTreeView
from Common.common_resources import putData
from Common.common_resources import saveBackupFile
from Common.common_resources import UI_String
from Common.common_resources import VARIABLE_TYPE_INTERFACES
from Common.ontology_container import OntologyContainer
from Common.record_definitions import makeCompletEquationRecord
from Common.record_definitions import makeCompleteVariableRecord
from Common.record_definitions import RecordIndex
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.resources_icons import getIcon
from Common.resources_icons import roundButton
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.OntologyEquationEditor.resources import CODE
from OntologyBuilder.OntologyEquationEditor.resources import ENABLED_COLUMNS
from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES, revertInterfaceVariableName, makeInterfaceVariableName
# from OntologyBuilder.OntologyEquationEditor.resources import make_variable_equation_pngs
from OntologyBuilder.OntologyEquationEditor.resources import renderExpressionFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.tpg import LexicalError
from OntologyBuilder.OntologyEquationEditor.tpg import SemanticError
from OntologyBuilder.OntologyEquationEditor.tpg import SyntacticError
from OntologyBuilder.OntologyEquationEditor.tpg import WrongToken
from OntologyBuilder.OntologyEquationEditor.ui_aliastableindices_impl import UI_AliasTableIndices
from OntologyBuilder.OntologyEquationEditor.ui_aliastablevariables_impl import UI_AliasTableVariables
from OntologyBuilder.OntologyEquationEditor.ui_equations_impl import UI_Equations
from OntologyBuilder.OntologyEquationEditor.ui_interface_variable_pick_impl import UI_VariableTableInterfacePick
from OntologyBuilder.OntologyEquationEditor.ui_ontology_design import Ui_OntologyDesigner
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_impl import UI_VariableTableDialog
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_show_impl import UI_VariableTableShow
from OntologyBuilder.OntologyEquationEditor.variable_framework import IndexStructureError
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeCompiler
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidenceDictionaries
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidentList
from OntologyBuilder.OntologyEquationEditor.variable_framework import UnitError
from OntologyBuilder.OntologyEquationEditor.variable_framework import VarError
from OntologyBuilder.OntologyEquationEditor.variable_framework import Variables  # Indices
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_instantiate import UI_VariableTableInterfaceInstantiate

# RULE: fixed wired for initialisation -- needs to be more generic
INITIALVARIABLE_TYPES = {
        "initialise" : ["state", "frame"],
        "connections": ["constant", "transposition"]
        }

CHOOSE_NETWORK = "choose network"
CHOOSE_INTER_CONNECTION = "choose INTER connection"
CHOOSE_INTRA_CONNECTION = "choose INTRA connection"


class EditorError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg


class UiOntologyDesign(QMainWindow):
  """
  Main window for the ontology design:
  """

  def __init__(self):
    """
    The editor has  the structure of a wizard,  thus goes through several steps
    to define the ontology.
    - get the base ontology that provides the bootstrap procedure.
    - construct the index sets that are used in the definition of the different
      mathematical objects
    - start building the ontology by defining the state variables
    """

    # set up dialog window with new title
    QMainWindow.__init__(self)
    self.ui = Ui_OntologyDesigner()
    self.ui.setupUi(self)
    # self.ui.pushBack.setIcon(getIcon('^'))
    self.ui.pushWrite.setIcon(getIcon('->'))
    self.setWindowTitle("OntologyFoundationEditor Design")
    roundButton(self.ui.pushInfo, "info", tooltip="information")
    roundButton(self.ui.pushCompile, "compile", tooltip="compile")

    roundButton(self.ui.pushShowVariables, "variable_show", tooltip="show variables")
    roundButton(self.ui.pushWrite, "save", tooltip="save")
    roundButton(self.ui.pushMakeAllVarEqPictures, "equation",
                tooltip="prepare all variables & equations for generating pictures")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")

    self.radio = [
            self.ui.radioVariables,
            self.ui.radioVariablesAliases,
            self.ui.radioIndicesAliases,
            ]
    [i.hide() for i in self.radio]

    self.ui.groupFiles.hide()
    self.ui.groupVariables.hide()
    self.ui.pushInstantiate.hide()

    try:
      assert os.path.exists(DIRECTORIES["ontology_repository"])
    except:
      print("directory %s does not exist" % DIRECTORIES["ontology_repository"])

    self.ontology_name = getOntologyName(task="task_ontology_equations")
    if not self.ontology_name:
      exit(-1)

    ### set up editor =================================================
    self.current_network = None  # holds the current ontology space name
    self.current_variable_type = None
    self.edit_what = None
    self.state = None  # holds this programs state

    # get ontology
    self.ontology_location = DIRECTORIES["ontology_location"] % str(self.ontology_name)
    self.ontology_container = OntologyContainer(self.ontology_name)
    self.ui.groupOntology.setTitle("ontology : %s" % self.ontology_name)
    # works only for colour and background not font size and font style
    # style = "QGroupBox:title {color: rgb(1, 130, 153);}" # not supported: font-size: 48pt;  background-color:
    # yellow; font-style: italic}"
    # self.ui.groupOntology.setStyleSheet(style)

    self.variable_types_on_networks = self.ontology_container.variable_types_on_networks
    # self.variable_types_on_networks_per_component = self.ontology_container.variable_types_on_networks_per_component
    self.converting_tokens = self.ontology_container.converting_tokens

    self.rules = self.ontology_container.rules
    self.ontology_hierarchy = self.ontology_container.ontology_hierarchy
    self.networks = self.ontology_container.networks
    self.interconnection_nws = self.ontology_container.interconnection_network_dictionary
    self.intraconnection_nws = self.ontology_container.intraconnection_network_dictionary
    self.intraconnection_nws_list = list(self.intraconnection_nws.keys())
    self.interconnection_nws_list = self.ontology_container.list_inter_branches_pairs  # list(
    # self.interconnection_nws.keys())

    self.indices = self.ontology_container.indices  # readIndices()  # indices
    self.variables = Variables(self.ontology_container)
    self.variables.importVariables(self.ontology_container.variables,
                                   self.indices)  # also link the indices for compilation

    self.state = "edit"

    # setup for next GUI-phase
    [i.show() for i in self.radio]
    self.ui.pushAddIndex.hide()

    makeTreeView(self.ui.treeWidget, self.ontology_container.ontology_tree)
    self.ui.combo_InterConnectionNetwork.clear()
    self.ui.combo_IntraConnectionNetwork.clear()
    self.ui.combo_InterConnectionNetwork.addItems(sorted(self.interconnection_nws_list))
    nws = self.ontology_container.networks
    self.ui.combo_IntraConnectionNetwork.addItems(nws)  # intraconnection_nws_list))

    self.ui.combo_InterConnectionNetwork.show()
    self.ui.combo_IntraConnectionNetwork.show()
    self.ui.groupFiles.hide()
    self.ui.groupEdit.hide()

    # prepare for compiled versions
    self.compiled_equations = {language: {} for language in LANGUAGES["compile"]}
    self.compiled_equations[LANGUAGES["global_ID_to_internal"]] = {}
    self.compiled_variable_labels = {}

    self.compile_only = True

    # if not self.ontology_container.checkForRule("name_space"):
    #   answer = makeMessageBox(
    #           message="the nature of the name space handling must be defined -- run OntologyFoundationDesigner",
    #           buttons=["OK"]
    #           )
    #   exit(-1)
    # else:
    #   self.global_name_space = self.ontology_container.rules["name_space"]

    # self.__compile("latex")
    # self.__compile("python")
    # self.__compile("cpp")
    # self.__compile("matlab")

    # self.__makeDotGraphs()
    # print("debugging -- global name space", self.global_name_space)
    # if self.global_name_space:
    #   answer = makeMessageBox(message="this is a global name space ontology do you want to change it",
    #                           buttons=["yes", "no"],
    #                           infotext="Gives you a possibility of the change to local name spaces -- for the time being one cannot change the other way around")
    #   if answer == "YES":
    #     self.__changeFromGlobalToLocal()
    return

  def on_pushInfo_pressed(self):
    msg_popup = UI_FileDisplayWindow(FILES["info_ontology_equation_editor"])
    msg_popup.exec_()

  def on_radioVariables_pressed(self):
    self.__checkRadios("variables")
    self.__hideTable()
    self.ui.groupVariables.show()
    if self.current_network:
      self.ui.groupEdit.show()
      self.ui.combo_EditVariableTypes.show()
      self.__writeMessage("edit variables/equations")
    else:
      self.__writeMessage("select variable type first")

  def on_radioVariablesAliases_pressed(self):
    self.__checkRadios("variable_aliases")
    self.__hideTable()
    self.__writeMessage("edit variable alias table")
    self.ui.groupVariables.show()
    self.ui.groupEdit.hide()
    self.ui.combo_EditVariableTypes.hide()
    if self.current_network:
      self.__setupVariablesAliasTable()
    else:
      self.__writeMessage("select variable type first")
      # self.ui.radioVariablesAliases.setDown(False)

  def on_radioIndicesAliases_pressed(self):
    self.__checkRadios("indices_aliases")
    self.__hideTable()
    self.__writeMessage("edit alias table")
    self.ui.groupVariables.hide()
    self.__setupIndicesAliasTable()


  def on_pushAddIndex_pressed(self):
    print("debugging __ adding index")
    indices = self.ontology_container.indices

    exist_list = []
    for i in indices:
      exist_list.append(indices[i]["label"])

    print("debugging -- labels:", exist_list)

    new_index = None
    while not (new_index):
      ui_ask = UI_String("give index name ", "index name or exit", limiting_list=exist_list)
      ui_ask.exec_()
      new_index = ui_ask.getText()
      print("new model name defined", new_index)
      if not new_index:
        return

      # adding index
      index = RecordIndex()
      index["label"] = new_index
      index["network"] = self.variables.ontology_container.heirs_network_dictionary[self.current_network]
      index_counter = len(indices) + 1
      indices[index_counter] = index
      for language in LANGUAGES["aliasing"]:
        indices[index_counter]["aliases"][language] = new_index

      language = LANGUAGES["global_ID"]
      s = CODE[language]["index"] % index_counter
      a = s  # .strip(" ")              # TODO: when we "compile" we have to add a space again. See reduceProduct.
      indices[index_counter]["aliases"][language] = a

      print("debugging -- new index defined:", new_index)


  def on_pushInstantiate_pressed(self):
    # print("debugging -- not yet implemented pushInstantiate")
    variables_not_instantiated = self.variables.indexInstantiated(self.current_network)
    enabled_var_types = self.variable_types_on_networks[self.current_network]
    self.variables.indexVariables()
    self.pick_instantiate = UI_VariableTableInterfaceInstantiate("All not instantiated variables",
                                          self.variables,
                                          self.indices,
                                          self.current_network,
                                          enabled_types = enabled_var_types,
                                          hide_vars =  [],
                                          hide_columns = [3],
                                          info_file = None,
                                          variable_IDs = variables_not_instantiated
                                          )
    self.pick_instantiate.picked.connect(self.__makeInstantiationEquation)
    self.pick_instantiate.exec_()

  def on_pushCompile_pressed(self):
    # self.__checkRadios("compile")
    # self.compile_only = True
    for l in LANGUAGES["code_generation"]:
      try:
        self.__compile(l)
      except (EditorError) as error:
        self.__writeMessage(error.msg)

    self.__compile("latex")
    self.__writeMessage("finished latex document")

    self.__makeRenderedOutput()

  def on_pushShowVariables_pressed(self):
    # print("debugging -- make variable table")
    if self.current_network in self.ontology_container.interfaces:
      print("debugging")
      enabled_var_types = VARIABLE_TYPE_INTERFACES
    else:
      enabled_var_types = self.variable_types_on_networks[self.current_network]
    variable_table = UI_VariableTableShow("All defined variables",
                                          self.ontology_container,
                                          self.variables,
                                          self.current_network,
                                          enabled_var_types,
                                          [],
                                          [3],
                                          None,
                                          ["info", "new", "port", "LaTex", "dot"]
                                          )
    variable_table.exec_()

  def on_pushMakeAllVarEqPictures_pressed(self):
    # self.variables.changes["equations"].changedAll()
    # self.variables.changes["variables"].changedAll()
    if not self.compiled_variable_labels:
      self.__writeMessage("compile first")
      self.on_pushCompile_pressed()

    self.__writeMessage("wait for completion of compilation")

    self.__makeVariableEquationPictures()

  def on_pushExit_pressed(self):
    self.close()

  def on_pushFinished_pressed(self):
    print("debugging -- got here")

  def on_radioGraph_clicked(self):
    self.__hideTable()
    self.ui.combo_EditVariableTypes.clear()
    self.ui.combo_EditVariableTypes.addItems(
            self.ontology_container.ontology_tree[self.current_network]["behaviour"]["graph"])

  def on_radioNode_clicked(self):
    self.__hideTable()
    self.ui.combo_EditVariableTypes.clear()
    self.ui.combo_EditVariableTypes.addItems(
            self.ontology_container.ontology_tree[self.current_network]["behaviour"]["node"])

  def on_radioArc_clicked(self):
    self.__hideTable()
    self.ui.combo_EditVariableTypes.clear()
    self.ui.combo_EditVariableTypes.addItems(
            self.ontology_container.ontology_tree[self.current_network]["behaviour"]["arc"])

  def on_treeWidget_clicked(self, index):  # state network_selected
    self.current_network = str(self.ui.treeWidget.currentItem().name)
    self.__writeMessage("current network selected: %s" % self.current_network)
    # print(">>> ", self.ui.radioVariablesAliases.isDown(), self.ui.radioVariablesAliases.isChecked())
    if self.ui.radioVariablesAliases.isChecked():
      # self.ui.radioVariablesAliases.setDown(False)
      self.on_radioVariablesAliases_pressed()
    elif self.ui.radioVariables.isChecked():
      self.__setupEdit("networks")
      self.ui.groupEdit.show()
      self.ui.combo_EditVariableTypes.show()
      self.on_radioVariables_pressed()
      if self.ontology_container.rules["network_enable_adding_indices"][self.current_network]:
        # print("debugging -- show add index")
        self.ui.pushAddIndex.show()
      else:
        self.ui.pushAddIndex.hide()
    self.ui.pushInstantiate.show()

  @QtCore.pyqtSlot(str)
  def on_combo_InterConnectionNetwork_activated(self, choice):
    self.__hideTable()
    self.current_network = str(choice)
    self.state = "inter_connections"
    if self.ui.radioVariablesAliases.isChecked():
      self.on_radioVariablesAliases_pressed()
    else:
      #   if self.global_name_space:
      #     try:
      #       self.dialog_interface.close()
      #     except:
      #       pass
      # return
      # else:
      #   self.__setupEdit("interface")
      # self.__setupEdit("interface")
      self.__setupEditInterface()
      self.__showFilesControl()

  @QtCore.pyqtSlot(str)  # combo_IntraConnectionNetwork
  def on_combo_IntraConnectionNetwork_activated(self, choice):
    self.__hideTable()
    self.current_network = str(choice)
    self.state = "intra_connections"
    self.__setupEdit("intraface")

  @QtCore.pyqtSlot(int)
  def on_tabWidget_currentChanged(self, which):
    print("debugging -- changed tab")
    self.ui.combo_EditVariableTypes.hide()

  def __setupEditInterface(self):
    left_nw = self.ontology_container.interfaces[self.current_network]["left_network"]
    right_nw = self.ontology_container.interfaces[self.current_network]["right_network"]
    self.equations = self.ontology_container.equations
    self.equation_information = self.ontology_container.equation_information
    self.equation_inverse_index = self.ontology_container.equation_inverse_index
    print("debugging -- left and right network:", left_nw, right_nw)
    set_left_variables = set()
    enabled_var_classes = list(self.variables.index_accessible_variables_on_networks[left_nw].keys())

    # RULE: what to hide -- all that have already be put into the interface
    already_defined_variables, not_yet_defined_variables = self.__alreadyDefinedVariables()

    for var_class in enabled_var_classes:
      for var_ID in self.variables.index_accessible_variables_on_networks[left_nw][var_class]:
        set_left_variables.add(var_ID)
    print("debugging -- variable lists", set_left_variables)  # , set_right_variables)

    # if self.global_name_space:
    #   self.__writeMessage("define link")
    #   self.__writeMessage("currently not possible")
    # self.dialog_interface = UI_SourceSinkLinking(left_nw, sorted(set_left_variables), right_nw, sorted(set_right_variables), list_link_equations, self.variables)
    # self.dialog_interface.selected.connect(self.makeLinkEquation)
    # self.dialog_interface.delete_equ.connect(self.deleteLinkEquation)
    # self.dialog_interface.exec_()

    # else:
    self.pick = UI_VariableTableInterfacePick("make interface cut equation",
                                              self.variables, self.indices,
                                              self.current_network,
                                              hide_vars=already_defined_variables,
                                              enabled_types=enabled_var_classes)
    self.pick.picked.connect(self.__makeLinkEquation)
    self.pick.exec_()
    # self.show_interface_variables = UI_VariableTableInterfacePick("show interface variables",
    #                                           self.variables, self.indices,
    #                                           self.current_network,
    #                                           hide_vars=not_yet_defined_variables,
    #                                           enabled_types=enabled_var_classes)
    # self.show_interface_variables.exec_()

    # print("debugging pick table")

  def __alreadyDefinedVariables(self):
    already_defined_variables = set()
    all_variables_in_interface = set()
    for var_ID in self.variables:
      symbol = self.variables[var_ID].label
      all_variables_in_interface.add(symbol)
      if self.variables[var_ID].network == self.current_network:
        already_defined_variables.add(symbol)
        symbol = revertInterfaceVariableName(symbol)
        already_defined_variables.add(symbol)
    not_yet_defined_variables = all_variables_in_interface - already_defined_variables
    already_defined_variables = list(already_defined_variables)
    not_yet_defined_variables = list(not_yet_defined_variables)
    return already_defined_variables, not_yet_defined_variables

  def __makeLinkEquation(self, var_ID):

    variables = self.ontology_container.variables
    self.variables[var_ID].language = "global_ID"
    rhs = str(self.variables[var_ID])
    symbol = self.variables[var_ID].label
    index_structures = self.variables[var_ID].index_structures
    units = self.variables[var_ID].units
    tokens = []

    # TODO: this variable class/type should be centralised. Is currently hard wired in more than one place.
    variable_type = VARIABLE_TYPE_INTERFACES

    incident_list = [str(var_ID)]
    link_equation = makeCompletEquationRecord(rhs=rhs,
                                              type="interface_link_equation",
                                              network=self.current_network,
                                              doc="interface equation",
                                              incidence_list=incident_list)
    new_var_ID = self.variables.newProMoVariableIRI()
    new_equ_ID = self.variables.newProMoEquationIRI()  # globalEquationID(update=True)  # RULE: for global ID

    variable_record = makeCompleteVariableRecord(new_var_ID,
                                                 label=makeInterfaceVariableName(symbol),
                                                 type=variable_type,
                                                 network=self.current_network,
                                                 doc="link variable %s to interface %s" % (
                                                         symbol, self.current_network),
                                                 index_structures=index_structures,
                                                 units=units,
                                                 equations={
                                                         new_equ_ID: link_equation
                                                         },
                                                 aliases={},
                                                 port_variable=False,
                                                 tokens=tokens,
                                                 )

    self.variables.addNewVariable(ID=new_var_ID, **variable_record)

    self.ontology_container.indexEquations()
    self.variables.indexVariables()
    self.pick.close()
    self.__setupEditInterface()

    print("debugging -- link_equation", link_equation)

    # vars_types_on_network_variable = self.ontology_container.interfaces[nw]["internal_variable_classes"]
    # self.ui.combo_EditVariableTypes.clear()
    # self.ui.combo_EditVariableTypes.addItems(vars_types_on_network_variable)
    # network_for_variable = nw
    # network_for_expression = nw  # self.ontology_container.interfaces[nw]["left_network"]
    # network_variable_source = self.ontology_container.interfaces[nw]["left_network"]
    # vars_types_on_network_expression = self.ontology_container.interfaces[nw]["left_variable_classes"]

  def deleteLinkEquation(self, equ_ID, var_ID):
    print("debugging -- deleting equation ", var_ID, equ_ID)
    self.variables[var_ID].removeEquation(equ_ID)
    self.ontology_container.indexEquations()

  def __setupEdit(self, what):
    """

    @param what: string "network" | "interface" | "intraface"
    @return: None
    """

    self.__hideTable()

    nw = self.current_network

    if what == "interface":
      vars_types_on_network_variable = self.ontology_container.interfaces[nw]["internal_variable_classes"]
      self.ui.combo_EditVariableTypes.clear()
      self.ui.combo_EditVariableTypes.addItems(vars_types_on_network_variable)
      network_for_variable = nw
      network_for_expression = nw  # self.ontology_container.interfaces[nw]["left_network"]
      # network_variable_source = self.ontology_container.interfaces[nw]["left_network"]
      vars_types_on_network_expression = self.ontology_container.interfaces[nw]["left_variable_classes"]
    elif what in "intraface":
      network_for_variable = nw  # self.intraconnection_nws[nw]["right"]
      _types = self.ontology_container.variable_types_on_networks

      #### building site: what shall be the rule for defining the intrafaces.
      # _left = self.intraconnection_nws[nw]["left"]
      # _right = self.intraconnection_nws[nw]["right"]
      # _set = set(_types[_left]) | set(_types[_right])
      _set = _types[nw]
      network_for_expression = nw
      # network_for_expression = list(_set) #self.intraconnection_nws[nw]["left"]  # NOTE: this should be all from
      #  both sides
      # network_variable_source = network_for_expression
      # vars_types_on_network_variable = self.ontology_container.variable_types_on_networks[network_for_variable]
      # RULE: NOTE: the variable types are the same on the left, the right and the boundary -- at least for the time
      # being
      vars_types_on_network_variable = sorted(_set)  # self.ontology_container.variable_types_on_networks[
      # network_for_expression]
      self.ui.combo_EditVariableTypes.clear()
      self.ui.combo_EditVariableTypes.addItems(vars_types_on_network_variable)
      vars_types_on_network_expression = sorted(
              _set)  # self.ontology_container.variable_types_on_networks[network_for_expression]
    else:
      self.ui.radioNode.toggle()
      self.on_radioNode_clicked()
      network_for_variable = nw
      network_for_expression = nw

      vars_types_on_network_variable = sorted(self.ontology_container.variable_types_on_networks[network_for_variable])

      interface_variable_list = []
      oc = self.variables.ontology_container
      for nw in oc.heirs_network_dictionary[network_for_expression]:
        for inter_nw in oc.interfaces:  # oc.interconnection_network_dictionary:
          # if oc.interconnection_network_dictionary[inter_nw]["right"] == nw:
          if oc.interfaces[inter_nw]["right_network"] == nw:
            interface_variable_list.append(inter_nw)
          # print("debugging -- inter_nw", inter_nw)

      network_variable_source = network_for_expression
      vars_types_on_network_expression = sorted(
              self.ontology_container.variable_types_on_networks[network_variable_source])
      for nw in interface_variable_list:
        for var_type in self.ontology_container.variable_types_on_interfaces[nw]:
          vars_types_on_network_expression.append(var_type)
      vars_types_on_network_expression = list(set(vars_types_on_network_expression))

    self.ui_eq = UI_Equations(what,  # what: string "network" | "interface" | "intraface"
                              self.variables,
                              self.indices,
                              network_for_variable,
                              network_for_expression,
                              vars_types_on_network_variable,
                              vars_types_on_network_expression,
                              # global_name_space=self.global_name_space
                              )
    self.ui_eq.update_space_information.connect(self.__updateVariableTable)

    self.ui.combo_EditVariableTypes.show()
    self.__showFilesControl()

  def __hideTable(self):
    if "table_variables" in self.__dir__():
      self.table_variables.hide()
    if "table_aliases_i" in self.__dir__():
      self.table_aliases_i.close()
    if "table_aliases_v" in self.__dir__():
      self.table_aliases_v.close()

  @QtCore.pyqtSlot(str)
  def on_combo_EditVariableTypes_activated(self, selection):
    selection = str(selection)
    if selection == "choose":
      return

    self.current_variable_type = selection
    self.ui.groupEdit.show()
    self.__setupVariableTable()
    self.table_variables.show()

    self.ui.combo_EditVariableTypes.show()
    self.__showFilesControl()

  def on_pushWrite_pressed(self):
    filter = self.ontology_container.variable_record_filter
    variables = self.variables.extractVariables(filter)
    self.ontology_container.writeVariables(variables, self.indices, self.variables.ProMoIRI)
    self.state = 'edit'

    self.compile_only = False

    for l in LANGUAGES["compile"]:  # ["code_generation"]:
      try:
        self.__compile(l)
      except (EditorError) as error:
        self.__writeMessage(error.msg)

    self.__makeRenderedOutput()

  def __makeRenderedOutput(self):
    self.__writeMessage("generating variable and equation pictures")
    language = LANGUAGES["global_ID_to_internal"]
    incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(self.variables)
    e_name = FILES["coded_equations"] % (self.ontology_location, language)

    for equ_ID in sorted(incidence_dictionary):
      lhs_var_ID, incidence_list = incidence_dictionary[equ_ID]
      expression_ID = self.variables[lhs_var_ID].equations[equ_ID]["rhs"]
      network = self.variables[lhs_var_ID].equations[equ_ID]["network"]
      var_label = self.variables[lhs_var_ID].label
      expression = renderExpressionFromGlobalIDToInternal(expression_ID, self.variables, self.indices)
      self.compiled_equations[language][equ_ID] = {
              "lhs"    : var_label,
              "network": network,
              "rhs"    : expression
              }

    putData(self.compiled_equations[language], e_name)

    e_name = FILES["coded_equations"] % (self.ontology_location, "just_list_internal_format")
    e_name = e_name.replace(".json", ".txt")
    file = open(e_name, 'w')
    for equ_ID in sorted(incidence_dictionary):
      e = self.compiled_equations[language][equ_ID]
      file.write("%s :: %s = %s\n" % (equ_ID, e["lhs"], e["rhs"]))
    file.close()

    # print("debugging --- rendered version", e_name)

  def __compile(self, language):

    incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(self.variables)
    e_name = FILES["coded_equations"] % (self.ontology_location, language)

    for equ_ID in sorted(incidence_dictionary):
      # if equ_ID == 87:
      #   print("debugging -- eq 87")
      lhs_var_ID, incidence_list = incidence_dictionary[equ_ID]
      expression_ID = self.variables[lhs_var_ID].equations[equ_ID]["rhs"]
      network = self.variables[lhs_var_ID].equations[equ_ID]["network"]
      self.variables[lhs_var_ID].setLanguage(language)
      compiled_label = str(self.variables[lhs_var_ID])
      expression = renderExpressionFromGlobalIDToInternal(expression_ID, self.variables, self.indices)
      if "Root" in expression:
        self.variables.to_define_variable_name = self.variables[lhs_var_ID].label  # aliases["global_ID"]
      compiler = makeCompiler(self.variables, self.indices, lhs_var_ID, equ_ID, language=language)

      try:
        # print("debugging --  expression being translated into language %s:"%language, expression)
        res = str(compiler(expression))
        self.compiled_equations[language][equ_ID] = {
                "variable_ID": lhs_var_ID,
                "lhs"        : compiled_label,  # var_label,
                "network"    : network,
                "rhs"        : res
                }

      except (SemanticError,
              SyntacticError,
              LexicalError,
              WrongToken,
              UnitError,
              IndexStructureError,
              VarError,
              ) as _m:
        print('checked expression failed %s : %s = %s -- %s' % (
                equ_ID, self.variables[lhs_var_ID].label, expression, _m))

        compiler = makeCompiler(self.variables, self.indices, lhs_var_ID, equ_ID, language=language, verbose=100)
        try:
          res = compiler(expression)  # NOTE: for debugging
        except:
          pass
          exit(-1)

    putData(self.compiled_equations[language], e_name)

    # if language == "latex":
    #   print("debugging -- processing latex")
    for var_ID in self.variables:  # used in internally
      self.variables[var_ID].setLanguage(language)
      compiled_label = str(self.variables[var_ID])
      if var_ID not in self.compiled_variable_labels:
        self.compiled_variable_labels[var_ID] = {}
      self.compiled_variable_labels[var_ID][language] = compiled_label

    if language == "latex":
      self.__makeLatexDocument()
      # put compiled variable labels into a separate file for convenience -- used in dot graph
      compiled_latex_variable_labels = {}
      for var_ID in self.variables:
        compiled_latex_variable_labels[var_ID] = self.compiled_variable_labels[var_ID]["latex"]
      v_name = FILES["coded_variables"] % (self.ontology_location, "latex")
      putData(compiled_latex_variable_labels, v_name)

    self.__makeOWLFile()

  def __makeOWLFile(self):

    this_dir = os.path.dirname(os.path.abspath(__file__))

    # OWL.tex
    # names_names = []

    j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
    body = j2_env.get_template(FILES["OWL_template"]).render(variables=self.variables, ProMo="ProMo",
                                                             ontology=self.ontology_name)  # self.networks)
    f_name = FILES["OWL_variables"] % self.ontology_name
    f = open(f_name, 'w')
    f.write(body)
    f.close()

  def __cleanStrings(self, string):
    cleaned_string = string.replace("_", " ").title()
    return cleaned_string

  def __makeLatexDocument(self):

    # latex
    #
    print('=============================================== make latex ================================================')
    # language = "latex"
    this_dir = os.path.dirname(os.path.abspath(__file__))

    eqs = self.__getAllEquationsPerType("latex")

    # main.tex
    names_names_for_variables = []
    # if self.global_name_space:
    #   nw_list = self.networks + self.intraconnection_nws_list  # + self.interconnection_nws_list
    # else:
    nw_list = self.networks + self.intraconnection_nws_list + self.interconnection_nws_list
    for nw in nw_list:
      names_names_for_variables.append(str(nw).replace(CONNECTION_NETWORK_SEPARATOR, '--'))

    e_types = sorted(self.variables.equation_type_list)
    e_types_cleaned = []
    for e in e_types:
      e_types_cleaned.append(self.__cleanStrings(e))

    j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
    body = j2_env.get_template(FILES["latex_template_main"]).render(ontology=names_names_for_variables,
                                                                    equationTypes=e_types_cleaned)  # self.networks)
    f_name = FILES["latex_main"] % self.ontology_name
    f = open(f_name, 'w')
    f.write(body)
    f.close()

    for nw in self.networks + self.interconnection_nws_list + self.intraconnection_nws_list:
      index_dictionary = self.variables.index_definition_network_for_variable_component_class
      # contents = 0
      # for c in index_dictionary[nw]:
      #   contents += len(index_dictionary[nw][c])
      # if contents > 0:
      j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
      body = j2_env.get_template(FILES["latex_template_variables"]).render(variables=self.variables,
                                                                           compiled_labels=self.compiled_variable_labels,
                                                                           index=index_dictionary[nw])
      name = str(nw).replace(CONNECTION_NETWORK_SEPARATOR, '--')
      f_name = FILES["latex_variables"] % (self.ontology_location, name)
      f = open(f_name, 'w')
      f.write(body)
      f.close()

    print("debugging tex rep")
    for e_type in self.variables.equation_type_list:
      _s = sorted(eqs[e_type].keys())
      print("debugging -- equation type", e_type)
      j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
      completed_template = j2_env.get_template(FILES["latex_template_equations"]). \
        render(equations=eqs[e_type], sequence=_s)
      o = self.__cleanStrings(str(e_type))
      f_name = FILES["latex_equations"] % (self.ontology_location, str(o))
      f = open(f_name, 'w')
      f.write(completed_template)
      f.close()

    location = DIRECTORIES["latex_main_location"] % self.ontology_location
    f_name = FILES["latex_shell_var_equ_doc_command_exec"] % self.ontology_location
    documentation_file = FILES["latex_documentation"] % self.ontology_name
    if not self.compile_only:
      saveBackupFile(documentation_file)
    self.__writeMessage("busy making var/eq images")
    args = ['sh', f_name, location]
    print('ARGS: ', args)
    make_it = subprocess.Popen(
            args,
            # start_new_session=True,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE
            )
    out, error = make_it.communicate()
    # print("debugging -- ", out, error)

    # self.__makeDotGraphs()
    # self.__makeVariableEquationPictures(language)

  def progress_dialog(self, message):
    "https://www.programcreek.com/python/example/108099/PyQt5.QtWidgets.QProgressDialog"
    prgr_dialog = QProgressDialog()
    prgr_dialog.setFixedSize(300, 50)
    prgr_dialog.setAutoFillBackground(True)
    prgr_dialog.setWindowModality(QtCore.Qt.WindowModal)
    prgr_dialog.setWindowTitle('Please wait')
    prgr_dialog.setLabelText(message)
    prgr_dialog.setSizeGripEnabled(False)
    prgr_dialog.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    prgr_dialog.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
    prgr_dialog.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
    prgr_dialog.setModal(True)
    prgr_dialog.setCancelButton(None)
    prgr_dialog.setRange(0, 0)
    prgr_dialog.setMinimumDuration(50)
    prgr_dialog.setMaximum(1000)
    prgr_dialog.setAutoClose(False)
    return prgr_dialog

  def __makeInstantiationEquation(self, var_ID):

    value = "V_0"
    for ID in self.variables:
      if self.variables[ID].label == "value":
        value_ID = ID
        value = self.variables[ID].aliases["global_ID"]


    self.variables[var_ID].language = "global_ID"
    variable_compiled = self.variables[var_ID].aliases['global_ID']
    rhs = CODE["global_ID"]["Instantiate"]%(variable_compiled, value )

    # TODO: this variable class/type should be centralised. Is currently hard wired in more than one place.
    variable_type = VARIABLE_TYPE_INTERFACES

    incident_list = [str(var_ID)]
    link_equation = makeCompletEquationRecord(rhs=rhs,
                                              type="instantiation_equation",
                                              network=self.current_network,
                                              doc="instantiation equation",
                                              incidence_list=incident_list)

    self.variables.addEquation(var_ID, link_equation)

    self.ontology_container.indexEquations()
    self.pick_instantiate.close()
    self.on_pushInstantiate_pressed()
    # self.variables.indexVariables()
    # self.__setupEditInterface()

  def __makeVariableEquationPictures(self):

    # make_it.wait()
    # Note: make the png variable and equation files

    # msg_box = wait()
    # msg_box.exec()
    self.progress_dialog("compiling")
    self.make_variable_equation_pngs()  # self.variables, self.ontology_container)
    # self.__writeMessage("Wrote {} output".format(language), append=True)
    self.__writeMessage("compilation completed")

  def __getAllEquationsPerType(self, language):
    eqs = {}
    for e_type in self.variables.equation_type_list:  # split into equation types
      eqs[e_type] = OrderedDict()
    for var_ID in self.variables:
      for equ_ID in self.variables[var_ID].equations:
        eq = self.variables[var_ID].equations[equ_ID]
        this_eq_type = eq["type"]  # equation_type
        eqs[this_eq_type][equ_ID] = {}
        eqs[this_eq_type][equ_ID]["rhs"] = self.compiled_equations[language][equ_ID][
          "rhs"]  # [var_ID][equ_ID][language]
        eqs[this_eq_type][equ_ID]["lhs"] = self.compiled_variable_labels[var_ID][language]
        if eq["doc"] == "":
          eq["doc"] = "var doc : %s" % self.variables[var_ID].doc
        eqs[this_eq_type][equ_ID]["doc"] = eq["doc"].replace("_", " ")  # self.variables[ID].doc
        eqs[this_eq_type][equ_ID]["var_ID"] = var_ID
        eqs[this_eq_type][equ_ID]["var_network"] = self.variables[var_ID].network
        eqs[this_eq_type][equ_ID]["network"] = eq["network"]
    return eqs

  def __makeDotGraphs(self):
    # http://www.graphviz.org/doc/info/colors.html

    vt_colour = ['white', 'yellow', 'darkolivegreen1', 'salmon', 'tan',
                 'tomato', 'cyan', 'green', 'grey',
                 'lightcyan', 'lightcyan1', 'lightcyan2',
                 'lightcyan3', 'lightcyan4',
                 ]

    dot_graph = {}
    s_nw_vt = "%s___%s"

    vt_colours = {}
    var_types = set()
    for nw in self.networks:
      [var_types.add(vt)
       for vt in self.ontology_container.variable_types_on_networks[nw]]

    var_types = list(var_types)
    for i in range(len(var_types)):
      vt_colours[var_types[i]] = vt_colour[i]

    for nw in self.networks:
      dot_graph[nw] = Dot(graph_name=nw, label=nw,
                          # suppress_disconnected=True,
                          rankdir='LR')

      vt_cluster = {}
      vt_count = 0
      for vt in self.ontology_container.variable_types_on_networks[nw]:
        vt_cluster[vt] = Cluster(graph_name=s_nw_vt % (nw, vt),
                                 suppress_disconnected=False,
                                 label=vt,
                                 rankdir='LR')
        for v_ID in self.variables.getVariablesForTypeAndNetwork(vt, nw):
          v_name = str(v_ID)
          v_node = Node(name=v_name,
                        style='filled',
                        fillcolor=vt_colours[vt],
                        penwidth=3,
                        fontsize=12,
                        label=self.variables[v_ID].label)
          vt_cluster[vt].add_node(v_node)
        for v_ID, e_ID in self.variables.index_equation_in_definition_network[nw]:
          if self.variables[v_ID].type == vt:
            e_node = Node(name=e_ID,
                          shape='box',
                          style='filled',
                          fillcolor='pink',
                          fontsize=12)
            vt_cluster[vt].add_node(e_node)
            equation = self.variables[v_ID].equations[e_ID]["rhs"]
            for i_ID in makeIncidentList(equation):
              edge = Edge(src=e_ID, dst=i_ID,
                          splines='ortho')
              dot_graph[nw].add_edge(edge)
            # v_name = self.variables[v_ID].label
            # e_name = str(self.variables[v_ID].equations[e_ID])
            edge = Edge(src=e_ID, dst=v_ID,
                        splines='ortho')
            vt_cluster[vt].add_edge(edge)
        vt_count += 1
        dot_graph[nw].add_subgraph(vt_cluster[vt])
      f_name = FILES["ontology_graphs_ps"] % (self.ontology_location, nw)

      # dot_graph[nw].write_ps(f_name, )  # prog='fdp')
      # f_name2 = DIRECTORIES["ontology_graphs_dot"] % (self.ontology_location, nw)
      # dot_graph[nw].write(f_name2, format='raw')

      try:
        dot_graph[nw].write_ps(f_name, )  # prog='fdp')
        f_name2 = FILES["ontology_graphs_dot"] % (self.ontology_location, nw)
        dot_graph[nw].write(f_name2, format='raw')
      except:
        print("cannot generate dot graph", f_name)

    # print("debugging ferdig med det - no of colours") # %s - %s"%(nw_count, vt_count))

  def update_tables(self):
    variable_type = self.current_variable_type
    print(">>> udating table :", variable_type)
    self.tables["variables"][variable_type].reset_table()
    self.ui_eq.variable_table.reset_table()

  def finished_edit_table(self, what):
    # print("finished editing table : ", what)
    # self.__makeAliasDictionary()  # check if all variables are defined
    self.__showFilesControl()
    try:
      self.table_aliases_i.close()
    except:
      pass
    try:
      self.table_aliases_v.close()
    except:
      pass
    try:
      self.ui_eq.close()
    except:
      pass

  def __showFilesControl(self):
    self.ui.groupEdit.show()
    self.ui.groupFiles.show()
    self.ui.pushWrite.show()

  def make_variable_equation_pngs(self):  # , variables, ontology_container):
    """
    generates pictures of the equations extracting the latex code from the latex equation file
    """
    self.make_equation_pngs()
    self.make_variable_pngs()

  def make_equation_pngs(self, source=None, ID=None):
    """
    undefined source takes the data from the compiled file, thus the equations_latex.json file
    otherwise it is taken from the variables dictionary being physical variables
    """
    ontology_name = self.ontology_container.ontology_name
    ontology_location = DIRECTORIES["ontology_location"] % ontology_name
    f_name = FILES["pnglatex"]
    header = self.__makeHeader(ontology_name)

    if not source:
      eqs = {}
      latex_file = os.path.join(DIRECTORIES["ontology_location"] % ontology_name, "equations_latex.json")
      latex_translations = getData(latex_file)
      for eq_ID_str in latex_translations:
        eq_ID = int(eq_ID_str)
        if ID:
          e = latex_translations[ID]
          eqs[ID] = r"%s = %s" % (e["lhs"], e["rhs"])
          break
        else:
          e = latex_translations[eq_ID_str]
          eqs[eq_ID] = r"%s = %s" % (e["lhs"], e["rhs"])

    for eq_ID in eqs:
      out = os.path.join(ontology_location, "LaTeX", "equation_%s.png" % eq_ID)
      args = ['bash', f_name, "-P5", "-H", header, "-o", out, "-f", eqs[eq_ID],
              ontology_location]

      try:  # reports an error after completing the last one -- no idea
        make_it = subprocess.Popen(
                args,
                start_new_session=True,
                # restore_signals=False,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE
                )
        out, error = make_it.communicate()
      except:
        print("equation generation failed")
        pass

  def make_variable_pngs(self, source=None, ID=None):
    ontology_name = self.ontology_container.ontology_name
    variables = self.ontology_container.variables

    f_name = FILES["pnglatex"]
    ontology_location = DIRECTORIES["ontology_location"] % ontology_name
    header = self.__makeHeader(ontology_name)
    for var_ID in variables:

      out = os.path.join(ontology_location, "LaTeX", "variable_%s.png" % var_ID)

      var_latex = self.compiled_variable_labels[var_ID]["latex"]

      if (not ID) or (var_ID == ID):
        args = ['bash', f_name, "-P5", "-H", header, "-o", out, "-f", var_latex,  # lhs[var_ID],
                ontology_location]

        try:  # reports an error after completing the last one -- no idea
          make_it = subprocess.Popen(
                  args,
                  start_new_session=True,
                  restore_signals=False,
                  # stdout=subprocess.PIPE,
                  # stderr=subprocess.PIPE
                  )
          out, error = make_it.communicate()
          # print("debugging -- made:", var_ID)
        except:
          print("debugging -- failed to make:", var_ID)
          pass

  def __makeHeader(self, ontology_name):
    header = FILES["latex_png_header_file"] % ontology_name
    # if not os.path.exists(header):                  # removed when copying an ontology tree --> generate
    header_file = open(header, 'w')
    # RULE: make header for equation and variable latex compilations.
    # math packages
    # \usepackage{amsmath}
    # \usepackage{amssymb}
    # \usepackage{calligra}
    # \usepackage{array}
    # \input{../../Ontology_Repository/HAP_playground_02_extend_ontology/LaTeX/resources/defs.tex}
    header_file.write(r"\usepackage{amsmath}")
    header_file.write(r"\usepackage{amssymb}")
    header_file.write(r"\usepackage{calligra}")
    header_file.write(r"\usepackage{array}")
    header_file.write(r"\input{../../Ontology_Repository/%s/LaTeX/resources/defs.tex}" % ontology_name)
    header_file.close()
    return header

  def closeEvent(self, event):
    self.close_children(event)
    self.close()

  def close_children(self, event):
    try:
      self.table_variables.close()
    except:
      pass
    try:
      self.table_aliases_v.close()
    except:
      pass
    try:
      self.table_aliases_i.close()
    except:
      pass
    try:
      self.dialog_interface.close()
    except:
      pass
    try:
      self.ui_eq.closeEvent(event)
    except:
      pass

  def __setupVariableTable(self):
    choice = self.current_variable_type
    if self.current_network in self.interconnection_nws:
      # if self.global_name_space:
      #   network_variable = self.current_network  # self.interconnection_nws[self.current_network]["right"]
      #   network_expression = network_variable  # self.interconnection_nws[self.current_network]["left"]
      # else:
      network_variable = self.interconnection_nws[self.current_network]["right"]
      network_expression = self.interconnection_nws[self.current_network]["left"]
    elif self.current_network in self.intraconnection_nws:
      # if self.global_name_space:
      #   network_variable = self.current_network  # self.intraconnection_nws[self.current_network]["right"]
      #   network_expression = self.current_network  # self.intraconnection_nws[self.current_network]["left"]
      # else:
      network_variable = self.intraconnection_nws[self.current_network]["right"]
      network_expression = self.intraconnection_nws[self.current_network]["left"]
    else:
      network_variable = self.current_network
      network_expression = self.current_network

    if choice[0] == "*":
      hide = ["port"]
    elif choice not in self.rules["variable_classes_having_port_variables"]:
      hide = ["port"]
    else:
      hide = []
    hide.extend(["LaTex", "dot", "next"])
    self.table_variables = UI_VariableTableDialog("create & edit variables",
                                                  self.variables,
                                                  self.indices,
                                                  self.ontology_container.tokens_on_networks,
                                                  self.variable_types_on_networks,
                                                  network_variable,
                                                  network_expression,
                                                  choice,
                                                  info_file=FILES["info_ontology_variable_table"],
                                                  hidden_buttons=hide,
                                                  )
    self.table_variables.show()  # Note: resolved tooltip settings, did not work during initialisation of table (
    # ui_variabletable_implement)

    # for choice in choice:
    try:
      enabled_columns = ENABLED_COLUMNS[self.state][choice]
    except:
      enabled_columns = ENABLED_COLUMNS[self.state]["others"]
    self.table_variables.enable_column_selection(enabled_columns)

    # self.ui_eq.def_given_variable.connect(self.table_variables.defineGivenVariable)
    self.table_variables.completed.connect(self.finished_edit_table)
    self.table_variables.new_variable.connect(self.ui_eq.setupNewVariable)
    self.table_variables.new_equation.connect(self.ui_eq.setupNewEquation)

  def __updateVariableTable(self):
    self.table_variables.close()
    self.__setupVariableTable()
    self.table_variables.show()

  def __setupVariablesAliasTable(self):

    # variables = self.variables.getVariableList(self.current_network)
    variables_ID_list = self.variables.index_definition_networks_for_variable[self.current_network]
    if variables_ID_list:
      self.table_aliases_v = UI_AliasTableVariables(self.variables,
                                                    self.current_network)  # , self.aliases_v[self.current_network])
      # self.table_aliases_v.completed.connect(self.__updateAliases_Variables)
      self.table_aliases_v.completed.connect(self.finished_edit_table)
      self.table_aliases_v.show()
      # self.variables.changes["variables"].changedAll()
      # self.variables.changes["equations"].changedAll()
      OK = True
    else:
      self.__writeMessage(" no variables in this network %s" % self.current_network)
      OK = False
    return OK

  def __setupIndicesAliasTable(self):
    # print("gotten here")
    self.table_aliases_i = UI_AliasTableIndices(self.indices)  # , self.aliases_i)
    self.table_aliases_i.completed.connect(self.__updateAliases_Indices)
    self.table_aliases_i.completed.connect(self.finished_edit_table)
    self.table_aliases_i.show()

  def __writeMessage(self, message, append=False):
    if not append:
      self.ui.msgWindow.clear()
    self.ui.msgWindow.setText(message)
    # self.show()
    # self.ui.msgWindow.show()
    self.ui.msgWindow.update()

  def __updateAliases_Variables(self):
    pass

  def __updateAliases_Indices(self):
    pass
    # self.ontology_container.indices = self.indices

  def __checkRadios(self, active):

    radios_ui = [self.ui.radioVariables, self.ui.radioVariablesAliases,
                 self.ui.radioIndicesAliases]
    radios = ["variables", "variable_aliases", "indices_aliases"]
    which = radios.index(active)
    for ui in radios_ui:
      ui.setChecked(False)
    radios_ui[which].setChecked(True)

  def __changeFromGlobalToLocal(self):
    # print("not yet implemented __changeFromGlobalToLocal")
    found = False
    for equ_ID in self.ontology_container.equation_variable_dictionary:
      variable_ID, equation = self.ontology_container.equation_variable_dictionary[equ_ID]
      incidence_list = equation["incidence_list"]
      variable_network = self.variables[variable_ID].network
      for v_str_ID in incidence_list:
        v_ID = int(v_str_ID)
        network_v = self.variables[v_ID].network
        if variable_network != network_v:
          for i in self.interconnection_nws:
            left_nw, right_nw = i.split(CONNECTION_NETWORK_SEPARATOR)
            if (variable_network == left_nw):
              if (network_v == right_nw):
                print("inter", i)
                print("networks", variable_network, network_v)
                print("change name space", variable_ID, variable_network, v_ID, network_v)
                # TODO: introduce code for generating a cut equation and delete the direct link equation.
                found = True
