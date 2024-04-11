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

import copy
import os
import time
from datetime import datetime
from pathlib import Path
import subprocess
import sys

from jinja2 import Environment  # sudo apt-get install python-jinja2
from jinja2 import FileSystemLoader
from pydotplus.graphviz import Cluster
from pydotplus.graphviz import Dot
from pydotplus.graphviz import Edge
from pydotplus.graphviz import Node
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

import constants
from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.common_resources import getOntologyName
from Common.common_resources import makeTreeView
from Common.common_resources import putData
from Common.common_resources import saveBackupFile
from Common.common_resources import UI_GetString
from Common.common_resources import VARIABLE_TYPE_INTERFACES
from Common.ontology_container import OntologyContainer
from Common.pop_up_message_box import makeMessageBox
from Common.record_definitions import makeCompletEquationRecord
from Common.record_definitions import makeCompleteVariableRecord
from Common.record_definitions import RecordIndex
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.resources_icons import roundButton
from Common.ui_radio_buttons_impl import RadioSelectorDialog
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.OntologyEquationEditor.resources import CODE
from OntologyBuilder.OntologyEquationEditor.resources import dateString
from OntologyBuilder.OntologyEquationEditor.resources import ENABLED_COLUMNS
from OntologyBuilder.OntologyEquationEditor.resources import ID_prefix
from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES
# from OntologyBuilder.OntologyEquationEditor.resources import makeInterfaceVariableName
from OntologyBuilder.OntologyEquationEditor.resources import renderExpressionFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.resources import revertInterfaceVariableName
from OntologyBuilder.OntologyEquationEditor.resources import sortingVariableAndEquationKeys
from OntologyBuilder.OntologyEquationEditor.resources import TEMPLATES
from OntologyBuilder.OntologyEquationEditor.tpg import LexicalError
from OntologyBuilder.OntologyEquationEditor.tpg import SemanticError
from OntologyBuilder.OntologyEquationEditor.tpg import SyntacticError
from OntologyBuilder.OntologyEquationEditor.tpg import WrongToken
from OntologyBuilder.OntologyEquationEditor.ui_aliastableindices_impl import UI_AliasTableIndices
from OntologyBuilder.OntologyEquationEditor.ui_aliastablevariables_impl import UI_AliasTableVariables
from OntologyBuilder.OntologyEquationEditor.ui_equations_impl import UI_Equations
from OntologyBuilder.OntologyEquationEditor.ui_interface_variable_pick_impl import UI_VariableTableInterfacePick
from OntologyBuilder.OntologyEquationEditor.ui_ontology_design import Ui_OntologyDesigner
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_delete_equation_impl import UI_VariableTableDeleteEquation
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_impl import UI_VariableTableDialog
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_instantiate import UI_VariableTableInterfaceInstantiate
from OntologyBuilder.OntologyEquationEditor.ui_variabletable_show_impl import UI_VariableTableShow
from OntologyBuilder.OntologyEquationEditor.variable_framework import CompileSpace
from OntologyBuilder.OntologyEquationEditor.variable_framework import Expression
from OntologyBuilder.OntologyEquationEditor.variable_framework import IndexStructureError
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeCompiler
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidenceDictionaries
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidentList
from OntologyBuilder.OntologyEquationEditor.variable_framework import UnitError
from OntologyBuilder.OntologyEquationEditor.variable_framework import VarError
from OntologyBuilder.OntologyEquationEditor.variable_framework import Variables  # Indices

# Note: keep
# from Common.classes.io import translate_equations  # must be last

# RULE: fixed wired for initialisation -- needs to be more generic
INITIALVARIABLE_TYPES = {
    "initialise": ["state", "frame"],
    "connections": ["constant", "transposition"]
}

CHOOSE_NETWORK = "choose network"
CHOOSE_INTER_CONNECTION = "choose INTER connection"
CHOOSE_INTRA_CONNECTION = "choose INTRA connection"

# RULE: we constrain interface networks to only exist to the CENTER_NETWORK
# TODO: needs to become part of the foundation ontology

CENTRE_NETWORKS = ["macroscopic", "info_processing"]


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

    # needs mousePressEvent and mouseMoveEvent

    self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

    self.ui = Ui_OntologyDesigner()
    self.ui.setupUi(self)
    self.setWindowTitle("OntologyFoundationEditor Design")
    roundButton(self.ui.pushInfo, "info", tooltip="information")
    roundButton(self.ui.pushCompile, "compile", tooltip="compile")

    roundButton(self.ui.pushShowVariables,
                "variable_show", tooltip="show variables")
    roundButton(self.ui.pushWrite, "save", tooltip="save")
    roundButton(self.ui.pushShowPDF, "PDF",
                tooltip="show pdf variable equation documentation")
    roundButton(self.ui.pushExit, "off", tooltip="exit")
    roundButton(self.ui.pushMakeInterfaceEquations, "plus",
                "display table for generating new interface equations")
    roundButton(self.ui.pushShowInterfaceEquations, "edit",
                "display table of defined interface equations")

    self.ui.pushShowVariables.hide()
    self.radio = [
        self.ui.radioVariables,
        self.ui.radioVariablesAliases,
        self.ui.radioIndicesAliases,
        self.ui.pushMakeInterfaceEquations,
        self.ui.pushShowInterfaceEquations,
    ]
    [i.hide() for i in self.radio]

    self.ui.pushShowPDF.hide()
    self.ui.groupVariables.hide()
    # self.ui.pushInstantiate.hide()  #TODO: eliminate?
    self.ui.groupEdit.hide()

    try:
      assert os.path.exists(DIRECTORIES["ontology_repository"])
    except:
      print("directory %s does not exist" % DIRECTORIES["ontology_repository"])

    self.ontology_name = getOntologyName(task="task_ontology_equations")
    if not self.ontology_name:
      exit(-1)

    # set up editor =================================================
    self.current_network = None  # holds the current ontology space name
    self.current_variable_type = None
    self.edit_what = None
    self.state = None  # holds this programs state

    self.starttime = dateString()

    # get ontology
    self.ontology_location = DIRECTORIES["ontology_location"] % str(
        self.ontology_name)
    self.ontology_container = OntologyContainer(self.ontology_name)
    self.ui.groupOntology.setTitle("ontology : %s" % self.ontology_name)

    self.variable_types_on_networks = self.ontology_container.variable_types_on_networks
    self.converting_tokens = self.ontology_container.converting_tokens

    self.rules = self.ontology_container.rules
    self.ontology_hierarchy = self.ontology_container.ontology_hierarchy
    self.networks = self.ontology_container.networks
    self.interconnection_nws = self.ontology_container.interconnection_network_dictionary
    self.intraconnection_nws = self.ontology_container.intraconnection_network_dictionary
    self.intraconnection_nws_list = list(self.intraconnection_nws.keys())

    # RULE: constrain interconnections to in and out of centre domain
    self.interconnection_nws_list = []
    for nw in self.ontology_container.list_inter_branches_pairs:
      for c in CENTRE_NETWORKS:
        if c in nw:
          if nw not in self.interconnection_nws_list:
            self.interconnection_nws_list.append(nw)

    self.indices = self.ontology_container.indices
    self.variables = Variables(self.ontology_container)
    # link the indices for compilation
    self.variables.importVariables(
        self.ontology_container.variables, self.indices)

    self.initial_variable_list = sorted(self.variables.keys())
    self.initial_equation_list = sorted(
        self.ontology_container.equation_dictionary.keys())
    self.state = "edit"

    # setup for next GUI-phase
    [i.show() for i in self.radio]
    self.ui.pushAddIndex.hide()

    makeTreeView(self.ui.treeWidget, self.ontology_container.ontology_tree)
    self.ui.combo_InterConnectionNetwork.clear()
    self.ui.combo_InterConnectionNetwork.addItems(
        sorted(self.interconnection_nws_list))

    self.ui.combo_InterConnectionNetwork.show()

    # prepare for compiled versions
    # issue: remove compiled_equations. It is currently used in generating a file with the rendered equations
    self.compiled_equations = {language: {}
                               for language in LANGUAGES["compile"]}
    self.compiled_equations[LANGUAGES["global_ID_to_internal"]] = {}
    self.compiled_variable_labels = {}

    self.compile_only = True

    return

  def on_pushInfo_pressed(self):
    msg_popup = UI_FileDisplayWindow(FILES["info_ontology_equation_editor"])
    msg_popup.exec_()

  def on_radioVariables_pressed(self):
    self.__checkRadios("variables")
    self.__hideTable()
    self.ui.groupVariables.show()
    if self.current_network:
      # self.ui.groupEdit.show()
      self.ui.combo_EditVariableTypes.show()
      self.writeMessage("edit variables/equations")
    else:
      self.writeMessage("select variable type first")

  def on_radioVariablesAliases_pressed(self):
    self.__checkRadios("variable_aliases")
    self.__hideTable()
    self.writeMessage("edit variable alias table")
    self.ui.groupVariables.show()
    self.ui.groupEdit.hide()
    self.ui.combo_EditVariableTypes.hide()
    if self.current_network:
      self.__setupVariablesAliasTable()
    else:
      self.writeMessage("select variable type first")

  def on_radioIndicesAliases_pressed(self):
    self.__checkRadios("indices_aliases")
    self.__hideTable()
    self.writeMessage("edit alias table")
    self.ui.groupVariables.hide()
    self.__setupIndicesAliasTable()

  def on_pushMakeInterfaceEquations_pressed(self):
    print("debugging -- radioMakeInterfaceEquations")
    self.__setupEditInterface()
    self.__showFilesControl()
    self.ui.pushShowVariables.show()

  def on_pushShowInterfaceEquations_pressed(self):
    print("debugging -- radioShowInterfaceEquations")
    hide = (["LaTex", "dot", "next", "port"])
    self.table_variables = UI_VariableTableDeleteEquation("delete interface equations",
                                                          self.variables,
                                                          self.indices,
                                                          self.current_network,
                                                          info_file=FILES["info_ontology_variable_table"],
                                                          )
    self.table_variables.show()

  def on_pushAddIndex_pressed(self):
    print("debugging __ adding index")
    indices = self.ontology_container.indices

    exist_list = []
    for i in indices:
      exist_list.append(indices[i]["label"])

    print("debugging -- labels:", exist_list)

    new_index = None
    while not (new_index):
      ui_ask = UI_GetString("give index name ",
                            "index name or exit", limiting_list=exist_list)
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
      indexID = ID_prefix["index"] + "%s" % index_counter
      indices[indexID] = index
      # indices[index_counter] = index
      for language in LANGUAGES["aliasing"]:
        indices[indexID]["aliases"][language] = new_index

      language = LANGUAGES["global_ID"]
      s = CODE[language]["index"] % index_counter
      a = s
      indices[indexID]["aliases"][language] = a

      print("debugging -- new index defined:", new_index)

  # NOTE: was activated with instantiate -- removed
  def __make_InterfaceEquation(self):
    variables_not_instantiated = self.variables.indexInstantiated(
        self.current_network)
    enabled_var_types = self.variable_types_on_networks[self.current_network]
    self.variables.indexVariables()
    self.pick_instantiate = UI_VariableTableInterfaceInstantiate("All not instantiated variables",
                                                                 self.variables,
                                                                 self.indices,
                                                                 self.current_network,
                                                                 enabled_types=enabled_var_types,
                                                                 hide_vars=[],
                                                                 hide_columns=[
                                                                     3],
                                                                 info_file=None,
                                                                 variable_IDs=variables_not_instantiated
                                                                 )
    self.pick_instantiate.picked.connect(self.__makeInstantiationEquation)
    self.pick_instantiate.exec_()

  def on_pushCompile_pressed(self):

    # make latex lhs
    self.__makeLHSCompliedLabels("latex")

    # make latex rhs and put into container
    self.__compile("latex")

    self.updateLatexImages()

    self.__makeLatexDocument()
    self.ui.pushShowPDF.show()
    self.writeMessage("finished latex document")

    self.__makeOWLFile()
    self.writeMessage("finished owl document")

    self.__makeRenderedOutput()
    self.writeMessage("finished rendered document")

  def on_pushShowVariables_pressed(self):
    if self.current_network in self.ontology_container.interfaces:
      enabled_var_types = [VARIABLE_TYPE_INTERFACES]
    else:
      enabled_var_types = self.variable_types_on_networks[self.current_network]
      enabled_var_types.append(VARIABLE_TYPE_INTERFACES)

    # update incidence dictionaries
    self.updateLatexImages()

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

  def on_pushExit_pressed(self):
    variable_list = sorted(self.variables.keys())
    equation_list = sorted(self.ontology_container.equation_dictionary.keys())

    modified = False
    for v in self.variables:
      modified = self.starttime < self.variables[v].modified
      # print("debugg -- modified")
      break

    if variable_list != self.initial_variable_list:
      modified = True
    if equation_list != self.initial_equation_list:
      modified = True

    if modified:
      response = makeMessageBox(
          "things have changed\ndo you want to exit?", default="cancel")
      if response == "OK":
        self.close()
        return
      else:
        return
    else:
      self.close()
      return

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
    self.writeMessage("current network selected: %s" % self.current_network)
    if self.ui.radioVariablesAliases.isChecked():
      self.on_radioVariablesAliases_pressed()
    elif self.ui.radioVariables.isChecked():
      self.__setupEdit("networks")
      self.ui.groupEdit.show()
      self.ui.combo_EditVariableTypes.show()
      self.on_radioVariables_pressed()
      if self.ontology_container.rules["network_enable_adding_indices"][self.current_network]:
        self.ui.pushAddIndex.show()
      else:
        self.ui.pushAddIndex.hide()
        self.ui.groupEdit.show()
    # self.ui.pushInstantiate.show()
    self.ui.pushShowVariables.show()

  @QtCore.pyqtSlot(str)
  def on_combo_InterConnectionNetwork_activated(self, choice):
    self.__hideTable()
    self.current_network = str(choice)
    self.state = "inter_connections"
    if self.ui.radioVariablesAliases.isChecked():
      self.on_radioVariablesAliases_pressed()
    else:
      pass
      self.ui.pushMakeInterfaceEquations.show()
      self.ui.pushShowInterfaceEquations.show()
      # self.__setupEdit("interface")
      # self.__setupEditInterface()
      # self.__showFilesControl()
      self.ui.pushShowVariables.show()

  @QtCore.pyqtSlot(int)
  def on_tabWidget_currentChanged(self, which):
    print("debugging -- changed tab", which)
    self.ui.pushShowVariables.hide()
    self.current_network = None
    self.ui.combo_EditVariableTypes.hide()
    self.ui.treeWidget.clearSelection()

    self.ui.groupEdit.hide()

    self.ui.pushMakeInterfaceEquations.hide()
    self.ui.pushShowInterfaceEquations.hide()

  def __setupEditInterface(self):
    left_nw = self.ontology_container.interfaces[self.current_network]["left_network"]
    right_nw = self.ontology_container.interfaces[self.current_network]["right_network"]
    self.equations = self.ontology_container.equations
    print("debugging -- left and right network:", left_nw, right_nw)
    set_left_variables = set()
    enabled_var_classes = list(
        self.variables.index_accessible_variables_on_networks[left_nw].keys())

    # RULE: what to hide -- all that have already be put into the interface
    already_defined_variables, not_yet_defined_variables, all_variables_imported = self.__alreadyDefinedVariables()

    for var_class in enabled_var_classes:
      for var_ID in self.variables.index_accessible_variables_on_networks[left_nw][var_class]:
        set_left_variables.add(var_ID)
    # print("debugging -- variable lists", set_left_variables)

    source, sink = self.current_network.split(CONNECTION_NETWORK_SEPARATOR)
    self.pick = UI_VariableTableInterfacePick("make interface cut equation",
                                              self.variables, self.indices,
                                              source,  # self.current_network,
                                              hide_vars=already_defined_variables | all_variables_imported,
                                              enabled_types=enabled_var_classes)
    self.pick.picked.connect(self.__makeLinkEquation)
    self.pick.exec_()

  def __alreadyDefinedVariables(self):
    already_defined_variables = set()
    all_variables_in_interface = set()
    all_variables_imported = set()
    for var_ID in self.variables:
      symbol = self.variables[var_ID].label
      all_variables_in_interface.add(symbol)
      if self.variables[var_ID].imported:
        all_variables_imported.add(symbol)
      if self.variables[var_ID].network == self.current_network:
        already_defined_variables.add(symbol)
        symbol = revertInterfaceVariableName(symbol)
        already_defined_variables.add(symbol)
    not_yet_defined_variables = all_variables_in_interface - already_defined_variables
    return already_defined_variables, not_yet_defined_variables, all_variables_imported

  def __makeLinkEquation(self, var_ID):
    """
    generates interface related equations
    rules:
    - if left domain is macro and right is control,
    -- if left source is node, map from node
    -- if left source is arc, map from arc
    - if left domain is control and right is ard,
    -- map from node to interface & interface to arc
    - if left domain is macro and right is not control
    -- if left source is node, map from node & map back to node
    -- if left source is arc, map from arc & map pack to arc
    Parameters
    ----------
    var_ID

    Returns
    -------

    """

    left_nw = self.ontology_container.interfaces[self.current_network]["left_network"]
    right_nw = self.ontology_container.interfaces[self.current_network]["right_network"]

    variable_types_right_nw = self.ontology_container.variable_types_on_networks_per_component[
        right_nw]["node"]

    variable = self.variables[var_ID]
    label = variable.label
    type = variable.type
    node_index_ID = "I_1"
    arc_index_ID = "I_2"

    from_centre = left_nw in CENTRE_NETWORKS
    to_centre = right_nw in CENTRE_NETWORKS
    from_node = node_index_ID in variable.index_structures
    from_arc = arc_index_ID in variable.index_structures

    # constants
    F_NI_source_ID = constants.FixedVariables.INCIDENCE_MATRIX_NI_SOURCE
    F_NI_sink_ID = constants.FixedVariables.INCIDENCE_MATRIX_NI_SINK
    F_AI_source_ID = constants.FixedVariables.INCIDENCE_MATRIX_AI_SOURCE
    F_AI_sink_ID = constants.FixedVariables.INCIDENCE_MATRIX_AI_SINK
    S_Ip_ID = constants.FixedVariables.SELECTION_MATRIX_I_INPUT
    S_Iq_ID = constants.FixedVariables.SELECTION_MATRIX_I_OUTPUT
    F_NI_source = self.variables[F_NI_source_ID].label
    F_NI_sink = self.variables[F_NI_sink_ID].label
    F_AI_source = self.variables[F_AI_source_ID].label
    F_AI_sink = self.variables[F_AI_sink_ID].label
    S_Ip = self.variables[S_Ip_ID].label
    S_Iq = self.variables[S_Iq_ID].label

    interface_variable = TEMPLATES["interface_variable"] % label
    while self.variables.existSymbol(self.current_network, interface_variable):
      interface_variable = TEMPLATES["interface_variable"] % interface_variable

    # RULE: keep information on if it came from node or arc and from the centre
    if from_centre:
      source = "node"
      if from_node:
        F = F_NI_source
      elif from_arc:
        F = F_AI_source
        source = "arc"
      else:
        source = None
        dialog = makeMessageBox(message="no source neither arc or node -- cannot build interface",
                                buttons=["OK"], default="OK", )
        return

      # ....................................eq 27
      left_to_interface = "%s * %s" % (F, label)
      interface_to_right = "(%s . %s ) * %s" % (F_NI_sink,
                                                interface_variable, S_Ip)  # eq 29

    elif to_centre:
      if variable.memory:
        to_node = variable.memory == "node"
        to_arc = variable.memory == "arc"
      else:
        answer = makeMessageBox("what is the target, node or arc", buttons=None, custom_buttons=[
                                ("node", "accept"), ("arc", "accept")], default="node")
        if answer == "node":
          to_node = True
          to_arc = False
        else:
          to_arc = True
          to_node = False

      if to_node:
        F = F_NI_source
        source = "node"
        variable_types_right_nw = self.ontology_container.variable_types_on_networks_per_component[
            right_nw]["node"]
      elif to_arc:
        F = F_AI_source
        source = "arc"
        variable_types_right_nw = self.ontology_container.variable_types_on_networks_per_component[
            right_nw]["arc"]
      else:
        dialog = makeMessageBox(
            "neither going to node or arc ???", buttons=["OK"], default="OK")
        return

      left_to_interface = "reduceSum((( %s * %s ) . %s), q )" % (
          F_NI_source, label, S_Iq)
      interface_to_right = "%s * %s" % (F, interface_variable)

    variable_definition_network = self.current_network
    expression_definition_network = self.current_network

  # step1 generate compilers
    compile_space_global_ID = CompileSpace(self.variables, self.indices, variable_definition_network, expression_definition_network,
                                           language="global_ID")
    compiler_global_ID = Expression(compile_space_global_ID, verbose=0)

    compile_space_latex = CompileSpace(self.variables, self.indices, variable_definition_network, expression_definition_network,
                                       language="latex")
    compiler_latex = Expression(compile_space_latex, verbose=0)

# step2: make left-to-interface
    x = compiler_global_ID(left_to_interface)
    left_to_interface_compiled_global_ID_units = x.units
    left_to_interface_compiled_global_ID_index_structures = x.index_structures
    left_to_interface_compiled_global_ID = str(x)
    left_to_interface_compiled_latex = str(compiler_latex(left_to_interface))
    rhs_dic = {"global_ID": left_to_interface_compiled_global_ID,
               "latex": left_to_interface_compiled_latex}
    incidence_list = makeIncidentList(left_to_interface_compiled_global_ID)

    new_var_ID = self.variables.newProMoVariableIRI()
    new_equ_ID = self.variables.newProMoEquationIRI()

    left_to_interface_equation_record = makeCompletEquationRecord(rhs=rhs_dic, type="interface_link_equation",
                                                                  network=self.current_network,
                                                                  doc="interface equation", incidence_list=incidence_list)

    # # RULE: keep information on if it came from node or arc and from the centre
    # if from_centre:
    #   source = "node"
    #   if from_arc:
    #     source = "arc"
    # else:
    #   source = None

    left_interface_variable_record = makeCompleteVariableRecord(new_var_ID,
                                                                label=interface_variable,
                                                                type=VARIABLE_TYPE_INTERFACES,
                                                                network=self.current_network,
                                                                doc="link variable %s to interface %s with source:%s" % (
                                                                    interface_variable, self.current_network, source),
                                                                index_structures=left_to_interface_compiled_global_ID_index_structures,
                                                                units=left_to_interface_compiled_global_ID_units,
                                                                equations={
                                                                    new_equ_ID: left_to_interface_equation_record
                                                                },
                                                                aliases={},
                                                                port_variable=False,
                                                                tokens=[],
                                                                memory=source,
                                                                imported=True,
                                                                )
    self.variables.addNewVariable(
        ID=new_var_ID, **left_interface_variable_record)

    self.variables.indexVariables()
    # fix latex for variable
    left_interface_variable_record["aliases"]["latex"] = interface_variable.replace(
        "_", "\_")

  # step3: make interface-to-right
    dialog = RadioSelectorDialog(variable_types_right_nw, parent=self)
    # dialog.exec_()
    variable_type = dialog.selection

    y = compiler_global_ID(interface_to_right)
    interface_to_right_compiled_global_ID = str(y)
    interface_to_right_compiled_global_ID_units = y.units
    interface_to_right_compiled_global_ID_index_structures = y.index_structures
    interface_to_right_compiled_latex = str(compiler_latex(interface_to_right))
    rhs_dic = {"global_ID": interface_to_right_compiled_global_ID,
               "latex": interface_to_right_compiled_latex}
    incidence_list = makeIncidentList(interface_to_right_compiled_global_ID)

    new_var_ID = self.variables.newProMoVariableIRI()
    new_equ_ID = self.variables.newProMoEquationIRI()

    left_to_interface_equation_record = makeCompletEquationRecord(rhs=rhs_dic, type="interface_link_equation",
                                                                  network=right_nw,
                                                                  doc="interface equation", incidence_list=incidence_list)

    right_interface_variable_record = makeCompleteVariableRecord(new_var_ID,
                                                                 label=label,
                                                                 type=variable_type,  # VARIABLE_TYPE_INTERFACES,
                                                                 network=right_nw,
                                                                 doc="link variable %s to interface %s" % (
                                                                     interface_variable, right_nw),
                                                                 index_structures=interface_to_right_compiled_global_ID_index_structures,
                                                                 units=interface_to_right_compiled_global_ID_units,
                                                                 equations={
                                                                     new_equ_ID: left_to_interface_equation_record
                                                                 },
                                                                 aliases={},
                                                                 port_variable=False,
                                                                 tokens=[],
                                                                 memory=source,
                                                                 imported=True,
                                                                 )
    self.variables.addNewVariable(
        ID=new_var_ID, **right_interface_variable_record)

    self.ontology_container.indexEquations()
    self.variables.indexVariables()
    self.pick.close()
    self.__setupEditInterface()

    # print("debugging -- link_equation", link_equation)

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
      vars_types_on_network_variable = self.ontology_container.interfaces[
          nw]["internal_variable_classes"]
      network_for_variable = nw
      network_for_expression = nw
      vars_types_on_network_expression = self.ontology_container.interfaces[
          nw]["left_variable_classes"]
    else:
      self.ui.radioNode.toggle()
      self.on_radioNode_clicked()
      network_for_variable = nw
      network_for_expression = nw

      vars_types_on_network_variable = sorted(
          self.ontology_container.variable_types_on_networks[network_for_variable])

      interface_variable_list = []
      oc = self.variables.ontology_container
      for nw in oc.heirs_network_dictionary[network_for_expression]:
        for inter_nw in oc.interfaces:
          if oc.interfaces[inter_nw]["right_network"] == nw:
            interface_variable_list.append(inter_nw)

      network_variable_source = network_for_expression
      vars_types_on_network_expression = sorted(
          self.ontology_container.variable_types_on_networks[network_variable_source])
      for nw in interface_variable_list:
        for var_type in self.ontology_container.variable_types_on_interfaces[nw]:
          vars_types_on_network_expression.append(var_type)
      vars_types_on_network_expression = list(
          set(vars_types_on_network_expression))

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
    # self.ui.groupEdit.show()
    self.__setupVariableTable()
    self.table_variables.show()

    self.ui.combo_EditVariableTypes.show()
    self.__showFilesControl()

  def on_pushWrite_pressed(self):
    filter = makeCompleteVariableRecord("dummy").keys()
    variables = self.variables.extractVariables(filter)
    self.ontology_container.writeVariables(
        variables, self.indices, self.variables.ProMoIRI)
    self.state = 'edit'

    self.compile_only = False

    self.on_pushCompile_pressed()
    self.starttime = dateString()
    self.initial_variable_list = sorted(self.variables.keys())
    self.initial_equation_list = sorted(
        self.ontology_container.equation_dictionary.keys())

  def updateLatexImages(self):
    (self.ontology_container.incidence_dictionary,
     self.ontology_container.inv_incidence_dictionary) = makeIncidenceDictionaries(
        self.ontology_container.variables)
    self.writeMessage("generating images")
    self.generateLatexImages(self.ontology_name, self.ontology_container)
    self.writeMessage("finished")

  def __makeRenderedOutput(self):
    """idea is to ease the repetition of inputting equations by writing them on a file."""
    self.writeMessage("generating variable and equation pictures")
    language = LANGUAGES["global_ID_to_internal"]
    incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(
        self.variables)
    e_name = FILES["coded_equations"] % (self.ontology_location, language)

    for equ_ID in sorted(incidence_dictionary):
      lhs_var_ID, incidence_list = incidence_dictionary[equ_ID]
      expression_ID = self.variables[lhs_var_ID].equations[equ_ID]["rhs"]["global_ID"]
      network = self.variables[lhs_var_ID].equations[equ_ID]["network"]
      var_label = self.variables[lhs_var_ID].label
      expression = renderExpressionFromGlobalIDToInternal(
          expression_ID, self.variables, self.indices)
      self.compiled_equations[language][equ_ID] = {
          "lhs": var_label,
          "network": network,
          "rhs": expression
      }

    putData(self.compiled_equations[language], e_name)

    e_name = FILES["coded_equations"] % (
        self.ontology_location, "just_list_internal_format")
    e_name = e_name.replace(".json", ".txt")
    file = open(e_name, 'w')
    for equ_ID in sorted(incidence_dictionary):
      e = self.compiled_equations[language][equ_ID]
      file.write("%s :: %s = %s\n" % (equ_ID, e["lhs"], e["rhs"]))
    file.close()

  def __compile(self, language):

    # hash is equation ID, value is tuple lhs varID and incidence list of varID
    incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(
        self.variables)

    # make lhs in the given language
    self.__makeLHSCompliedLabels(language)

    for equ_ID in sorted(incidence_dictionary):
      lhs_var_ID, incidence_list = incidence_dictionary[equ_ID]
      self.__compileEquation(equ_ID, language, lhs_var_ID)

  def __compileEquation(self, equ_ID, language, lhs_var_ID):
    expression_ID = self.variables[lhs_var_ID].equations[equ_ID]["rhs"]["global_ID"]
    expression = renderExpressionFromGlobalIDToInternal(
        expression_ID, self.variables, self.indices)
    if "Root" in expression:
      self.variables.to_define_variable_name = self.variables[lhs_var_ID].label
    compiler = makeCompiler(self.variables, self.indices,
                            lhs_var_ID, equ_ID, language=language)
    try:
      res = str(compiler(expression))
      self.ontology_container.variables[lhs_var_ID]["equations"][equ_ID]["rhs"][language] = res

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

  def __makeLHSCompliedLabels(self, language):
    for varID in self.variables:
      compiled_label = self.__makeLHSCompiledLabel(language, varID)
      self.ontology_container.variables[varID]["compiled_lhs"][language] = compiled_label

  def __makeLHSCompiledLabel(self, language, varID):
    self.variables[varID].setLanguage(language)
    compiled_label = str(self.variables[varID])
    return compiled_label

  def __makeOWLFile(self):

    this_dir = os.path.dirname(os.path.abspath(__file__))

    j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
    body = j2_env.get_template(FILES["OWL_template"]).render(variables=self.variables, ProMo="ProMo",
                                                             ontology=self.ontology_name)
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

    # clean up network notation in equations
    nw_that_has_equation_cleaned = set()
    for e_type in eqs:
      for e in eqs[e_type]:
        nw = eqs[e_type][e]["network"]
        # nw_that_has_equation.add(nw)
        nw_cleaned = nw.replace(CONNECTION_NETWORK_SEPARATOR, '--')
        nw_that_has_equation_cleaned.add(nw_cleaned)

    # networks with defined variables:
    set_nw_that_have_variables_cleaned = set()
    for v in self.variables:
      vnw = self.variables[v].network
      snw = vnw
      if CONNECTION_NETWORK_SEPARATOR in vnw:
        snw = vnw.replace(CONNECTION_NETWORK_SEPARATOR, "--")
      set_nw_that_have_variables_cleaned.add(snw)
      # set_nw_that_have_variables.add(snw)

    list_nw_that_have_variables = []
    for nw in self.ontology_container.heirs_network_dictionary["root"]:
      if nw in set_nw_that_have_variables_cleaned:
        list_nw_that_have_variables.append(nw)

    # first main nw then inter networks
    list_nw_that_has_equation_cleaned = []
    for nw in nw_that_has_equation_cleaned:
      if "--" not in nw:
        list_nw_that_has_equation_cleaned.append(nw)
    for nw in nw_that_has_equation_cleaned:
      if "--" in nw:
        list_nw_that_has_equation_cleaned.append(nw)

    # clean up equation
    e_types = sorted(self.variables.equation_type_list)
    e_types_cleaned = []
    for e in e_types:
      e_types_cleaned.append(self.__cleanStrings(e))

    # networks_to_be_documented = list(set_nw_that_have_variables_cleaned or set(list_nw_that_has_equation_cleaned))
    nws = set(list_nw_that_have_variables + list_nw_that_has_equation_cleaned)
    sorted_list_networks_to_be_documented = []
    for nw in self.ontology_container.heirs_network_dictionary["root"]:
      if nw in nws:
        if nw not in sorted_list_networks_to_be_documented:
          sorted_list_networks_to_be_documented.append(nw)
    for nw in nws:
      if "--" in nw:
        sorted_list_networks_to_be_documented.append(nw)

    j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
    body = j2_env.get_template(FILES["latex_template_main"]).render(ontology=sorted_list_networks_to_be_documented,
                                                                    # networks_to_be_documented, #list_nw_that_have_variables, #list_nw_that_has_equation_cleaned,
                                                                    equationTypes=e_types_cleaned)
    f_name = FILES["latex_main"] % self.ontology_name
    f = open(f_name, 'w')
    f.write(body)
    f.close()

    index_dictionary = self.variables.index_definition_network_for_variable_component_class

    for nw in nws:  # list_nw_that_have_variables:  # nw_that_has_equation:
      j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
      snw = nw
      if "--" in nw:
        snw = nw.replace("--", CONNECTION_NETWORK_SEPARATOR)
      body = j2_env.get_template(FILES["latex_template_variables"]).render(variables=self.variables,
                                                                           index=index_dictionary[snw])
      name = nw  # str(nw).replace(CONNECTION_NETWORK_SEPARATOR, '--')
      f_name = FILES["latex_variables"] % (self.ontology_location, name)
      f = open(f_name, 'w')
      f.write(body)
      f.close()

    print("debugging tex rep")
    for e_type in self.variables.equation_type_list:
      _s = sortingVariableAndEquationKeys(eqs[e_type].keys())
      print("debugging -- equation type", e_type)
      j2_env = Environment(loader=FileSystemLoader(this_dir), trim_blocks=True)
      completed_template = j2_env.get_template(FILES["latex_template_equations"]). \
          render(equations=eqs[e_type], sequence=_s)
      o = self.__cleanStrings(str(e_type))
      f_name = FILES["latex_equations"] % (self.ontology_location, str(o))
      f = open(f_name, 'w')
      f.write(completed_template)
      f.close()


    documentation_file = FILES["latex_documentation"] % self.ontology_name
    if not self.compile_only:
      saveBackupFile(documentation_file)
    self.writeMessage("busy making var/eq images")

    f_name = FILES["latex_main"] % self.ontology_name
    latex_folder_path = Path(DIRECTORIES["latex_doc_location"] % self.ontology_name)

    p = QtCore.QProcess()
    p.startDetached("pdflatex", [ "-interaction=nonstopmode", f_name], str(latex_folder_path) )

    self.__cleanDirectories()

    self.__makeDotGraphs()

  def on_pushShowPDF_pressed(self):

    location = DIRECTORIES["latex_main_location"] % self.ontology_location
    path = Path(location + "/main.pdf")
    if sys.platform.startswith('linux'):
      subprocess.Popen(['xdg-open', str(path)])
    elif sys.platform.startswith('win32'):
      subprocess.Popen(['start', str(path)], shell=True)
    # f_name = FILES["latex_shell_show_pdf"] % self.ontology_location
    # p = QtCore.QProcess()
    # p.startDetached("sh", [f_name, location])

  def __makeInstantiationEquation(self, var_ID):

    value = "V_0"
    for ID in self.variables:
      if self.variables[ID].label == "value":
        value_ID = ID
        value = self.variables[ID].aliases["global_ID"]

    # self.variables[var_ID].language = "global_ID"
    variable_compiled = self.variables[var_ID].aliases['global_ID']
    rhs_internal = CODE["global_ID"]["Instantiate"] % (
        variable_compiled, value)

    variable_latex = self.variables[var_ID].aliases['latex']
    rhs_latex = CODE["latex"]["Instantiate"] % (variable_latex, value)

    rhs_dic = {"global_ID": rhs_internal,
               "latex": rhs_latex}

    # TODO: this variable class/type should be centralised. Is currently hard wired in more than one place.
    variable_type = VARIABLE_TYPE_INTERFACES

    incident_list = [str(var_ID)]
    link_equation = makeCompletEquationRecord(rhs=rhs_dic, type="instantiation_equation",
                                              network=self.current_network,
                                              doc="instantiation equation", incidence_list=incident_list)

    self.variables.addEquation(var_ID, link_equation)

    self.ontology_container.indexEquations()
    self.pick_instantiate.close()
    self.__make_InterfaceEquation()

  def __getAllEquationsPerType(self, language):
    eqs = {}
    for e_type in self.variables.equation_type_list:  # split into equation types
      eqs[e_type] = {}  # OrderedDict()

    eq_dic = self.ontology_container.makeEquationDictionary()
    for equ_ID in eq_dic:
      e_type = eq_dic[equ_ID]["type"]
      eq_record = eq_dic[equ_ID]

      eqs[e_type][equ_ID] = {}
      eqs[e_type][equ_ID]["rhs"] = eq_record["rhs"][language]
      eqs[e_type][equ_ID]["lhs"] = eq_record["lhs"][language]
      eqs[e_type][equ_ID]["doc"] = eq_record["doc"].replace("_", " ")
      var_ID = eq_record["lhs"]["global_ID"]  # var_ID
      eqs[e_type][equ_ID]["var_ID"] = var_ID
      eqs[e_type][equ_ID]["var_network"] = self.ontology_container.variables[var_ID]["network"]
      eqs[e_type][equ_ID]["network"] = eq_record["network"]

    return eqs

  def __makeDotGraphs(self):
    # http://www.graphviz.org/doc/info/colors.html

    vt_colour = ['white', 'yellow', 'darkolivegreen1', 'salmon', 'tan',
                 'tomato', 'cyan', 'green', 'grey',
                 'lightcyan', 'lightcyan1', 'lightcyan2', 'lightcyan3', 'lightcyan4',
                 'seagreen', 'seagreen1', 'seagreen2', 'seagreen3', 'seagreen4',
                 'skyblue', 'skyblue1', 'skyblue2', 'skyblue3', 'skyblue4',
                 'violetred', 'violetred1', 'violetred2', 'violetred4',
                 'yellow', 'yellow1', 'yellow2', 'yellow3', 'yellow4',
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
        # for v_ID, e_ID in self.variables.index_equation_in_definition_network[nw]:
        for v_ID in self.variables:
          if nw == self.variables[v_ID].network:
            for e_ID in self.variables[v_ID].equations:
              if self.variables[v_ID].type == vt:
                e_node = Node(name=e_ID,
                              shape='box',
                              style='filled',
                              fillcolor='pink',
                              fontsize=12)
                vt_cluster[vt].add_node(e_node)
                equation = self.variables[v_ID].equations[e_ID]["rhs"]["global_ID"]
                for i_ID in makeIncidentList(equation):
                  edge = Edge(src=e_ID, dst=i_ID,
                              splines='ortho')
                  dot_graph[nw].add_edge(edge)
                edge = Edge(src=e_ID, dst=v_ID,
                            splines='ortho')
                vt_cluster[vt].add_edge(edge)
        vt_count += 1
        dot_graph[nw].add_subgraph(vt_cluster[vt])
      f_name = FILES["ontology_graphs_ps"] % (self.ontology_location, nw)

      try:
        dot_graph[nw].write_ps(f_name, )  # prog='fdp')
        f_name2 = FILES["ontology_graphs_dot"] % (self.ontology_location, nw)
        dot_graph[nw].write(f_name2, format='raw')
      except:
        print("cannot generate dot graph", f_name)

  def update_tables(self):
    variable_type = self.current_variable_type
    print(">>> udating table :", variable_type)
    self.tables["variables"][variable_type].reset_table()
    self.ui_eq.variable_table.reset_table()

  def finished_edit_table(self, what):

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
    # self.ui.groupEdit.show()
    # self.ui.groupFiles.show()
    self.ui.pushWrite.show()

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
    # if self.current_network in self.interconnection_nws:
    #   network_variable = self.interconnection_nws[self.current_network]["right"]
    #   network_expression = self.interconnection_nws[self.current_network]["left"]
    # elif self.current_network in self.intraconnection_nws:
    #   network_variable = self.intraconnection_nws[self.current_network]["right"]
    #   network_expression = self.intraconnection_nws[self.current_network]["left"]
    # else:
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
    self.table_variables.show()

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
    self.updateLatexImages()
    self.table_variables.close()
    self.__setupVariableTable()
    self.table_variables.show()

  def __setupVariablesAliasTable(self):

    variables_ID_list = self.variables.index_definition_networks_for_variable[
        self.current_network]
    if variables_ID_list:
      self.table_aliases_v = UI_AliasTableVariables(self.variables,
                                                    self.current_network)
      self.table_aliases_v.completed.connect(self.finished_edit_table)
      self.table_aliases_v.show()
      OK = True
    else:
      self.writeMessage(" no variables in this network %s" %
                        self.current_network)
      OK = False
    return OK

  def __setupIndicesAliasTable(self):
    self.table_aliases_i = UI_AliasTableIndices(self.indices)
    self.table_aliases_i.completed.connect(self.finished_edit_table)
    self.table_aliases_i.show()

  def writeMessage(self, message, append=True):
    if not append:
      self.ui.msgWindow.clear()
    self.ui.msgWindow.setText(message)
    self.ui.msgWindow.update()

  def __checkRadios(self, active):

    radios_ui = [self.ui.radioVariables, self.ui.radioVariablesAliases,
                 self.ui.radioIndicesAliases]
    radios = ["variables", "variable_aliases", "indices_aliases"]
    which = radios.index(active)
    for ui in radios_ui:
      ui.setChecked(False)
    radios_ui[which].setChecked(True)

  def __changeFromGlobalToLocal(self):
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
                print("change name space", variable_ID,
                      variable_network, v_ID, network_v)
                # TODO: introduce code for generating a cut equation and delete the direct link equation.
                found = True

  def __cleanDirectories(self):

    original_work_dir = os.getcwd()
    time.sleep(2.0)   # Note: delay execution to give the opering system time to register files

    latex_folder_path = Path(DIRECTORIES["latex_doc_location"] % self.ontology_name)
    os.chdir(latex_folder_path)
    types_to_b_removed = [".aux", ".log", ".dvi", ".out"]
    for f in os.listdir():
      for t in types_to_b_removed:
        if t in f:
          os.remove(f)

    os.chdir(original_work_dir)

  def generateLatexImages(self, ontology_name, ontology_container):

    variables = ontology_container.variables
    equations = ontology_container.equation_dictionary
    incidence_dictionary = ontology_container.incidence_dictionary
    inv_incidence_dictionary = ontology_container.inv_incidence_dictionary

    latex_folder_path = Path(DIRECTORIES["latex_doc_location"] % ontology_name)

    latex_info = {}
    modified_vars = []
    for var_id in variables:
      var_png_file_path = latex_folder_path / (var_id + ".png")
      if os.path.exists(var_png_file_path):  # .exists():
        png_mod_date = datetime.fromtimestamp(
            var_png_file_path.stat().st_mtime)
        modified = variables[var_id]["modified"]
        date_format = "%Y-%m-%d %H:%M:%S"
        var_mod_date = datetime.strptime(modified, date_format)
        if png_mod_date > var_mod_date:
          continue

      variables[var_id]["compiled_lhs"]["latex"] = self.__makeLHSCompiledLabel(
          "latex", var_id)
      var_latex_alias = variables[var_id]["compiled_lhs"]["latex"]
      latex_info[var_id] = "$" + var_latex_alias + "$"
      modified_vars.append(var_id)

    for eq_id in equations:  # , eq in all_equations.items():
      eq_png_file_path = latex_folder_path / (eq_id + ".png")
      if eq_png_file_path.exists():
        png_mod_date = datetime.fromtimestamp(eq_png_file_path.stat().st_mtime)
        modified = equations[eq_id]["modified"]
        date_format = "%Y-%m-%d %H:%M:%S"
        eq_mod_date = datetime.strptime(modified, date_format)
        if png_mod_date > eq_mod_date:
          continue
      (var_id, _) = incidence_dictionary[eq_id]
      lhs = variables[var_id]["compiled_lhs"]["latex"]

      self.__compileEquation(eq_id, "latex", var_id)
      rhs = equations[eq_id]["rhs"]["latex"]
      latex_info[eq_id] = "$" + lhs + "=" + rhs + "$"

    # pick up the equations that are modified due to changing variable
    for var_ID in modified_vars:
      for eq_id in inv_incidence_dictionary[var_ID]:
        (var_id, _) = incidence_dictionary[eq_id]
        lhs = variables[var_id]["compiled_lhs"]["latex"]
        self.__compileEquation(eq_id, "latex", var_id)
        rhs = equations[eq_id]["rhs"]["latex"]
        latex_info[eq_id] = "$" + lhs + "=" + rhs + "$"
      for eq_id in list(self.variables[var_ID].equations.keys()):
        lhs = variables[var_ID]["compiled_lhs"]["latex"]
        self.__compileEquation(eq_id, "latex", var_ID)
        rhs = equations[eq_id]["rhs"]["latex"]
        latex_info[eq_id] = "$" + lhs + "=" + rhs + "$"

    original_work_dir = os.getcwd()
    os.chdir(latex_folder_path)
    #
    for file_name, latex_alias in latex_info.items():
      f = open(file_name + ".tex", "w")  # as f:
      f.write("\\documentclass[border=2pt]{standalone}\n")
      f.write("\\usepackage{amsmath}\n")
      f.write("\\begin{document}\n")
      f.write(latex_alias)
      f.write("\\end{document}\n")
      f.close()

      print("......................................................................................................................")

      p = QtCore.QProcess()
      # p.startDetached("sh", ["resources/make_images.sh", file_name])
      tex_file = file_name + ".tex"
      png_file = file_name + ".png"
      dvi_file = file_name + ".dvi"
      path = str(latex_folder_path)
      status = p.execute("latex", ["-interaction=nonstopmode",tex_file])
      if status == 0:
        pp = QtCore.QProcess()
        pars = [ "-D",  "300", "-T", "tight", "-norawps", "-z", "9", "-bg", "Transparent", "-o", png_file, dvi_file ]
        (pstatus,pID) = pp.startDetached("dvipng", pars, path )
        print("cwd", os.getcwd(), "--", tex_file, png_file)
        if not pstatus:
          print("failed to generate png", png_file)
        else:
          print("generated png", png_file)
    os.chdir(original_work_dir)

  def mousePressEvent(self, event):
    self.oldPos = event.globalPos()

  def mouseMoveEvent(self, event):
    delta = QtCore.QPoint(event.globalPos() - self.oldPos)
    self.move(self.x() + delta.x(), self.y() + delta.y())
    self.oldPos = event.globalPos()
