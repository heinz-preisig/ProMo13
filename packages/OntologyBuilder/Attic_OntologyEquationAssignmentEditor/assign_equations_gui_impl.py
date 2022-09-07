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
# __since__ = "03.05.2019"
__since__ = "24.09.2020"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "8.01"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtWidgets

from Common.common_resources import getOntologyName
from Common.common_resources import putData
from Common.ontology_container import OntologyContainer
from Common.qt_resources import clearLayout
from Common.resource_initialisation import checkAndFixResources
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.resources_icons import roundButton
from Common.ui_radio_selector_w_sroll_impl import UI_RadioSelector
from OntologyBuilder.Attic_OntologyEquationAssignmentEditor.assign_equations_gui import Ui_MainWindow
from OntologyBuilder.OntologyEquationEditor.resources import AnalyseBiPartiteGraph
from OntologyBuilder.OntologyEquationEditor.resources import renderExpressionFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidenceDictionaries


class UI_EditorEquationAssignment(QtWidgets.QMainWindow):
  rules = {  # RULE : what variable class in what network for nodes and arcs
          "nodes": {
                  "physical": "state",
                  "control" : "state",
                  "intra"   : "state",
                  "inter"   : "get",
                  },
          "arcs" : {
                  "physical": "transport",
                  "control" : "dataflow",
                  "inter"   : "get"
                  }
          }

  def __init__(self):
    QtWidgets.QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.ontology_name = getOntologyName(task="task_entity_generation")
    self.ontology_dir = DIRECTORIES["ontology_location"] % self.ontology_name
    self.ontology_file = FILES["ontology_file"] % self.ontology_name

    roundButton(self.ui.pushInfo, "info", tooltip="information")
    roundButton(self.ui.pushSave, "save", tooltip="save ProMo base ontology")
    roundButton(self.ui.pushGraphNode, "dot_graph", tooltip="show graph")

    checkAndFixResources(self.ontology_name, stage="ontology_stage_2")

    self.ontology_container = OntologyContainer(self.ontology_name)
    self.incidence_dictionary, self.inv_incidence_dictionary = makeIncidenceDictionaries(
            self.ontology_container.variables)

    self.reduced_network_node_list = self.ontology_container.list_reduced_network_node_objects #__makeNodeLists()
    self.reduced_arc_list = self.ontology_container.list_reduced_network_arc_objects # self.__makeArcLists()

    self.radio_selectors = {}
    self.__makeCombosNetworks()

    self.current_equation_IDs = {}  # hash: radio button index     value: equation_ID_str
    self.ui.tabWidget.setCurrentIndex(0)
    self.current_tab = 0
    self.tabs = ["node", "arc", "intra", "inter"]

    self.selected_node = None
    self.selected_arc = None
    self.selected_intra = None
    self.selected_inter = None
    self.selected_arc_network = None
    self.selected_node_network = None

    self.assignments = {}

    self.__makeEquationList()

  def __makeCombosNetworks(self):
    # networks = self.ontology_container.list_leave_networks
    list_inter_branches = self.ontology_container.list_inter_branches
    self.ui.comboNodeNetworks.addItems(list_inter_branches)
    self.ui.comboArcNetworks.addItems(list_inter_branches)
    pass

  # def __makeNodeLists(self):
  #   reduced_network_node_list = {}
  #   # global_node_set = set()
  #   for nw in self.ontology_container.list_inter_branches:
  #     network_node_list = self.ontology_container.list_node_objects_on_networks[nw]  #
  #     # list_node_objects_on_networks_with_tokens[nw]
  #     reduced_network_node_list[nw] = []
  #     for i in network_node_list:
  #       if "constant" not in i:  # RULE: reservoirs (time-scale constant) have no state
  #         reduced_network_node_list[nw].append(i)
  #         # if i not in global_node_set:
  #         #   global_node_set.add(i)
  #
  #   # print("debugging -- network nodes", reduced_network_node_list)
  #   self.reduced_network_node_list = reduced_network_node_list
  #
  # def __makeArcLists(self):
  #   reduced_arc_list = {}
  #   global_arc_set = set()
  #   for nw in self.ontology_container.list_inter_branches:
  #     network_arc_list = self.ontology_container.list_arc_objects_on_networks[nw]
  #     reduced_arc_list[nw] = []
  #     for i in network_arc_list:
  #       reduced_arc_list[nw].append(i)
  #       if i not in global_arc_set:
  #         global_arc_set.add(i)
  #
  #   # print("debugging -- arcs", reduced_arc_list)
  #   self.reduced_arc_list = reduced_arc_list

  def __makeNodeSelector(self):
    node_list = self.reduced_network_node_list[self.selected_node_network]
    self.radio_selectors["networks"] = self.__makeSelector(node_list,
                                                           self.radioReceiverNodes,
                                                           -1,  # RULE: none selected initially
                                                           self.ui.verticalLayoutNodeTop)

  def __makeArcSelector(self):
    arc_list = self.reduced_arc_list[self.selected_arc_network]

    self.radio_selectors["arcs"] = self.__makeSelector(arc_list,
                                                       self.radioReceiverArcs,
                                                       -1,
                                                       self.ui.verticalLayoutArcTop)

  # def __makeEquationDictionary(self):
  #   for var_ID in self.ontology_container.variables:
  #     for eq_ID in self.ontology_container.variables[var_ID]["equations"]:
  #       self.equation_variable_dictionary[eq_ID] = (var_ID, self.ontology_container.variables[var_ID]["equations"][
  #       eq_ID])

  @staticmethod
  def __makeSelector(what, receiver, index, layout, allowed=1):

    height = layout.parent().size().height()
    clearLayout(layout)
    radio_selector = UI_RadioSelector(what, [index], allowed=allowed, maxheight=height)
    radio_selector.newSelection.connect(receiver)
    layout.addWidget(radio_selector)

    return radio_selector

  def __makeNodeEquationSelector(self):
    self.selected_node_network = self.ui.comboNodeNetworks.currentText()
    var_type = "state"
    if self.selected_node_network == "inter":
      var_type = self.rules["nodes"]["inter"]
    radio_item_set = set()

    nw = self.selected_node_network
    if nw in self.ontology_container.networks:
      nws = list(self.ontology_container.ontology_tree[nw]["parents"])
      nws.append(nw)
      for p_nw in nws:
        if p_nw in self.rendered_equation:
          if var_type in self.rendered_equation[p_nw]:
            for var_ID in self.rendered_equation[p_nw][var_type]:
              add_to = set(self.rendered_equation[p_nw][var_type][var_ID])
              radio_item_set = radio_item_set | add_to
    radio_item_list = sorted(radio_item_set)

    # print("debugging -- item list", radio_item_list)
    self.radio_selectors["node_equations"] = self.__makeSelector(radio_item_list,
                                                                 self.radioReceiverNodeEquations,
                                                                 -1,  # RULE: none selected initially
                                                                 self.ui.verticalLayoutNodeBottom,
                                                                 )

  def __makeArcEquationSelector(self):
    self.selected_arc_network = self.ui.comboArcNetworks.currentText()
    nw = self.selected_arc_network
    var_type = self.rules["arcs"]["physical"]
    if nw in ["control", "inter"]:
      var_type = self.rules["arcs"][nw]

    radio_item_set = set()

    if nw in self.ontology_container.networks:
      nws = list(self.ontology_container.ontology_tree[nw]["parents"])
      nws.append(nw)
      for p_nw in nws:
        if p_nw in self.rendered_equation:
          if var_type in self.rendered_equation[p_nw]:
            for var_ID in self.rendered_equation[p_nw][var_type]:
              add_to = set(self.rendered_equation[p_nw][var_type][var_ID])
              radio_item_set = radio_item_set | add_to
    radio_item_list = sorted(radio_item_set)

    # print("debugging -- item list", radio_item_list)
    self.radio_selectors["node_equations"] = self.__makeSelector(radio_item_list,
                                                                 self.radioReceiverArcEquations,
                                                                 -1,  # RULE: none selected initially
                                                                 self.ui.verticalLayoutArcBottom,
                                                                 )

  def __makeEquationList(self):

    self.inverse_dictionary = {}  # hash: label, value: (var_ID, eq_ID)

    equation_list = {}
    rendered_equation_list = {}
    self.inverse_dictionary = {}

    # for component in self.rules:
    # for nw in self.ontology_container.networks: #rules[component]:
    equation_variable_dictionary = self.ontology_container.equation_variable_dictionary
    for eq_ID in equation_variable_dictionary:
      var_ID, equation = equation_variable_dictionary[eq_ID]
      var_type = self.ontology_container.variables[var_ID]["type"]
      nw = self.ontology_container.variables[var_ID]["network"]

      if nw not in equation_list:
        equation_list[nw] = {}
      if nw not in rendered_equation_list:
        rendered_equation_list[nw] = {}

      if var_type not in equation_list[nw]:
        equation_list[nw][var_type] = {}
        rendered_equation_list[nw][var_type] = {}
      equation_list[nw][var_type][eq_ID] = (var_ID, var_type, equation["rhs"], equation["network"])

      # for var_type in equation_list[nw]:
      #   for eq_ID in equation_list[nw][var_type]:
      #     print(eq_ID, " -- ", equation_list[nw][var_type][eq_ID])

      rendered_expressions = renderExpressionFromGlobalIDToInternal(
              equation["rhs"],
              self.ontology_container.variables,
              self.ontology_container.indices)

      rendered_variable = self.ontology_container.variables[equation_list[nw][var_type][eq_ID][0]]["aliases"][
        "internal_code"]

      # print("debugging -- rendered equation info", rendered_variable, rendered_expressions[var_type][eq_ID])
      s = "%s := %s" % (rendered_variable, rendered_expressions)
      # radio_item_list.append(s)
      # print("debugging variable class")
      if var_ID not in rendered_equation_list[nw][var_type]:
        rendered_equation_list[nw][var_type][var_ID] = []
      rendered_equation_list[nw][var_type][var_ID].append(s)

      self.inverse_dictionary[s] = (var_ID, eq_ID)
      self.rendered_equation = rendered_equation_list

      # print("debugging -- end of make equation list")

  def analyseBiPartiteGraph(self, object, var_ID):
    obj = object.replace("|", "_")
    blocked = []
    self.assignments[object] = {}
    self.var_equ_tree, self.assignments[object]["base"] = AnalyseBiPartiteGraph(var_ID,
                                                                                self.ontology_container,
                                                                                self.ontology_name,
                                                                                blocked,
                                                                                obj)

  def on_comboNodeNetworks_currentTextChanged(self, network):
    # print("debugging -- node network", network)
    self.selected_node_network = network
    self.__makeNodeSelector()

  def on_comboArcNetworks_currentTextChanged(self, network):
    # print("debugging -- arc network", network)
    self.selected_arc_network = network
    self.__makeArcSelector()

  def on_pushSave_pressed(self):
    print("debugging -- save file")
    # self.ontology_container.writeVariables()

    f = FILES["variable_assignment_to_entity_object"] % self.ontology_name
    putData(self.assignments, f)

  def on_pushGraphNode_pressed(self):
    if self.var_equ_tree:
      self.var_equ_tree.view()

  def on_pushInfo_pressed(self):
    print("debugging -- display info file")

  def on_tabWidget_currentChanged(self, index):
    # print("debugging -- new tab", index)
    self.current_tab = index

  def radioReceiverNodes(self, checked):
    if checked:
      [self.selected_node] = checked
      print("debugging -- nodes", self.selected_node)
      self.__makeNodeEquationSelector()
      pass

  def radioReceiverArcs(self, checked):

    if checked:
      [self.selected_arc_network] = checked
      print("debugging -- arcs", self.selected_arc_network)
      self.__makeArcEquationSelector()
      pass

  def radioReceiverIntra(self, checked):

    if checked:
      self.selected_intra = checked
      print("debugging -- intra")
      pass

  def radioReceiverInter(self, checked):

    if checked:
      self.selected_inter = checked
      print("debugging -- inter")
      pass

  def radioReceiverNodeEquations(self, checked):

    print("debugging -- node equations checked", checked)
    [equ_text] = checked
    var_ID, equ_ID = self.inverse_dictionary[equ_text]
    print("debugging -- equation no", var_ID, equ_ID)
    print("debugging -- network ", self.selected_node_network)
    self.analyseBiPartiteGraph(self.selected_node, var_ID)
    pass

  def radioReceiverArcEquations(self, checked):

    print("debugging -- arc equations checked", checked)
    [equ_text] = checked
    var_ID, equ_ID = self.inverse_dictionary[equ_text]
    print("debugging -- equation no", var_ID, equ_ID)
    print("debugging -- network ", self.selected_arc_network)
    self.analyseBiPartiteGraph(self.selected_arc, var_ID)
    pass
