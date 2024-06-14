#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
  commander for ModelComposer
===============================================================================
  main switch board of Process Modeller


__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL"
__version__ = "5.01"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

"""

import copy
import os
from collections import deque
from collections import OrderedDict
from pathlib import Path
from pprint import pp
from typing import List
from typing import Optional
from typing import Tuple

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from typing_extensions import TypedDict

import Common.common_resources as CR
import ModelBuilder.ModelComposer.resources as R
from Common.automata_objects import GRAPH_EDITOR_STATES
from Common.common_resources import askForModelFileGivenOntologyLocation
from Common.common_resources import NODE_COMPONENT_SEPARATOR
from Common.graphics_objects import INTERFACE
from Common.graphics_objects import INTRAFACE
from Common.graphics_objects import LOCATION_PARAMETERS
from Common.graphics_objects import NAMES
from Common.graphics_objects import OBJECTS_with_state
from Common.graphics_objects import STATES
from Common.graphics_objects import TOOLTIP_TEMPLATES
from Common.qt_resources import BUTTON_NAMES
from Common.record_definitions import Interface
from Common.resource_initialisation import FILES
from Common.ui_get_string_impl import UI_GetString
from Common.ui_radio_selector_w_sroll_impl import UI_RadioSelector
from ModelBuilder.ModelComposer.instantiation_dialog_HAP_impl import InstantiationDialog
from ModelBuilder.ModelComposer.modeller_graphcomponents import Arc_Edge
from ModelBuilder.ModelComposer.modeller_graphcomponents import Knot
from ModelBuilder.ModelComposer.modeller_graphcomponents import Node
from ModelBuilder.ModelComposer.modeller_graphcomponents import NodeView
from ModelBuilder.ModelComposer.modeller_model_data import ModelContainer
from ModelBuilder.ModelComposer.modeller_model_data import ModelGraphicsData
from ModelBuilder.ModelComposer.modeller_model_data import ROOTID
from ModelBuilder.ModelComposer.variant_selection_impl import extract
from ModelBuilder.ModelComposer.variant_selection_impl import splitApplication
from ModelBuilder.ModelComposer.variant_selection_impl import splitEntity
from ModelBuilder.ModelComposer.variant_selection_impl import VariantGUI
from packages.Common.classes import entity
from packages.Common.classes import io
from packages.Common.classes import modeller_classes
from packages.Common.classes.io import load_entities_from_file
from packages.Common.classes.io import load_var_idx_eq_from_file

EDITOR_PHASES = list(GRAPH_EDITOR_STATES.keys())


# global methods --------------------------------------------------------------

def debugPrint(source, what):
  print(source, ": ", what)


class VariableInfo(TypedDict):
  """Creates a new type for a dictionary that stores info about a var"""
  id: str
  same_in_all_nodes: bool
  value: Optional[float]


class Commander(QtCore.QObject):
  """
  main switch board
  """

  def __init__(self, mainWin):
    """
    connect the main mainWin containing the main GUI
    @param mainWin: main GUI window
    """

    QtCore.QObject.__init__(self)
    self.main = mainWin
    self.showMouseActions = mainWin.showMouseAction
    self.cursors = R.ModellerCursor()
    self.intraconnections_dictionary = self.main.ontology.intraconnection_network_dictionary
    self.interconnections_dictionary = self.main.ontology.interconnection_network_dictionary

    # graphics view
    self.scene = None
    self.view = None

    #  interface behaviour
    self.__loadAutomata()

    # model container - start with a root node
    self.current_ID_node_or_arc = ROOTID
    self.model_container = ModelContainer(
            self.main.networks, self.main.ontology)

    # Loading Equations and Entities in the new form.
    self.all_variables, _, all_equations = load_var_idx_eq_from_file(
            self.main.ontology_name
            )
    self.all_entities = load_entities_from_file(
            self.main.ontology_name, all_equations)

    # initial commander state
    self.state_nodes = {}
    self.state_arcs = {}
    self.current_application = R.M_None
    self.step = 0  # event counter
    self.resetGroups()
    self.arc_group = []
    self.library_model_name = ""  # current library model file name
    self.schnipsel_file = None
    self.modified = False

    self.selected_entity_behaviour = None

    # handling connections - arcs
    self.selected_arcID = None
    self.arcSourceID = None
    self.end_to_move = None  # "source" or "sink" to be moved
    # EDITOR_PHASES[0]  # "topology"
    self.editor_phase = self.main.editor_phase

    # RULE: default editor phase is the first in the list
    self.editor_state = GRAPH_EDITOR_STATES[self.editor_phase][0]
    self.current_object_state = STATES[self.editor_phase]["nodes"][0]
    self.current_application = R.M_None

    # connect graphics data
    self.graphics_data = self.main.graphics_DATA

    rootID = ROOTID
    self.state_nodes[rootID] = STATES[self.editor_phase]["nodes"][0]
    self.__makeViewAndScene(rootID)
    self.currently_viewed_node = rootID

  def __loadAutomata(self):
    automata = CR.getData(self.main.automata_working_file_spec)
    self.mouse_automata = automata["mouse"]
    self.key_automata = automata["key"]

    self.inverse_key_automata = {}

    for phase in self.key_automata:
      self.inverse_key_automata[phase] = {}
      for key in self.key_automata[phase]:
        state = self.key_automata[phase][key]["state"]
        self.inverse_key_automata[phase][state] = key

  # interface to graphics  ------------------------------------------------------

  def processGUIEvent(self, event_type, item, pressed, position=None):
    """
    executes automata dependent on event type
     - dummy event (event on dummy item) : do nothing
     - keyboard : keyboard automaton
     - GUI : no automaton yet
     - mouse : mouse automaton
    @param event_type:  in {keyboard, GUI, mouse}
    @param item:        graphics item on which event occurred
    @param pressed:     what mouse button was pressed
    @param position:    at what position
    """

    # print("  item : ", item, item.__class__, "ShapePannel" in str(item.__class__) )

    #  TODO: circumvent problems after deleting objects and changing editor mode via GUI control interface
    if "ShapePannel" in str(item.__class__):
      self.recover_item = item

    self.current_ID_node_or_arc = item.getGraphObjectID()  # graphics_root_object

    self.main.writeStatus("")

    #
    # RULE selecting a primitive node or arc may imply changing networks
    # try:  # circumvent problems after deleting objects and changing editor mode via GUI control interface
    graphics_root_object = item.parent.graphics_root_object
    state = self.getGraphObjectState(graphics_root_object)
    if graphics_root_object == NAMES["node"]:
      network = self.model_container["nodes"][self.current_ID_node_or_arc]["network"]
      named_network = self.model_container["nodes"][self.current_ID_node_or_arc]["named_network"]
      # node_type = self.model_container["nodes"][self.current_ID_node_or_arc]["type"]
      # variant = self.model_container["nodes"][self.current_ID_node_or_arc]["variant"]
      # print("node simple network:", network)
      if network in self.main.networks:
        self.main.setNetwork(network, named_network)
      # self.main.setNodeType(node_type)
      # self.main.setNodeVariant(variant)
    if graphics_root_object == NAMES["connection"]:
      network = self.model_container["arcs"][self.current_ID_node_or_arc]["network"]
      named_network = self.model_container["arcs"][self.current_ID_node_or_arc]["named_network"]
      # print("node simple network:", network)
      if network in self.main.networks:
        self.main.setNetwork(network, named_network)

    self.current_object_state = state

    self.current_item = item  # broadcast item

    # ======== keyboard

    if event_type in ["keyboard", "controlboard"]:
      # print("updateGraph", "key event", pressed, list(self.key_automata[self.editor_phase].keys()))
      if pressed not in list(self.key_automata[self.editor_phase].keys()):
        print(">>>> commander -- key %s not recognised" % pressed)
        # print("updateGraph", "key event", pressed, "not in ", list(self.key_automata[self.editor_phase].keys()))
        return

      next_state = self.key_automata[self.editor_phase][pressed]["state"]
      action = self.key_automata[self.editor_phase][pressed]["output"]

      if event_type == "keyboard":  # break dead lock with setting only for keyboard 'controlboard' couples to here
        self.main.setKeyAutomatonState(pressed)

      # ======================================================================
      # # RULE: change of editor state is always applied on the panel
      # for i in self.scene.items():
      #   if NAMES["panel"] in dir(i):
      #     if (i.graphics_root_object == NAMES["panel"]):
      #       if (i.decoration == NAMES["root"]):
      #         item = i
      # ======================================================================

    # ========= GUI
    elif event_type == "GUI":
      action = "zoom in"
      next_state = "-"

    # ======== mouse
    elif event_type == "mouse":
      # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.
      if self.editor_phase in ["topology", "token_topology", "equation_topology"]:
        #
        # RULE: topology automaton operates on root object type and state independent of the network
        graphics_root_object = item.parent.graphics_root_object
        decoration = item.decoration
        application = item.application
        object_str = self.getObjectStr(
                application, decoration, graphics_root_object, state)

        mouse_automaton = self.mouse_automata[self.editor_phase]

        if object_str not in mouse_automaton[self.editor_state].keys():
          print("process event -- object %s not active" % object_str)
          print("              -- keys %s", mouse_automaton.keys())
          return
        else:
          event = BUTTON_NAMES[pressed]
          next_state = mouse_automaton[self.editor_state][object_str][event]["state"]
          action = mouse_automaton[self.editor_state][object_str][event]["output"]

          if next_state != "-":
            if next_state in list(self.inverse_key_automata[self.editor_phase].keys()):
              this_key = self.inverse_key_automata[self.editor_phase][next_state]
              self.main.setKeyAutomatonState(this_key)

          self.__reportEvent(state, next_state, action, object_str, event)

    # ============ error
    else:
      print("updateGraph",
            "commander.processGUIEvent: event handling error")

    if next_state != "-":
      self.editor_state = next_state

    pars = {
            "nodeID": item.parent.ID,
            "action": action,
            "object": item.decoration,
            "pos"   : position,
            "file"  : "-",
            "failed": False,
            }
    if graphics_root_object in [NAMES["connection"], NAMES["right arc"], NAMES["left arc"]]:
      pars["arc"] = item.parent.getArcID()

    pars = self.__c00_executeCommand(pars)

    return pars

  def getGraphObjectState(self, graphics_root_object):
    # print("getGraphObjectState  object ", graphics_root_object, self.current_ID_node_or_arc)
    if graphics_root_object in OBJECTS_with_state:
      if graphics_root_object in [NAMES["node"], NAMES["intraface"], NAMES["interface"]]:
        state = self.state_nodes[self.current_ID_node_or_arc]
      elif graphics_root_object == NAMES["connection"]:
        state = self.state_arcs[self.current_ID_node_or_arc]
      else:
        state = R.M_None
    else:
      state = R.M_None
    self.current_object_state = state
    return state

  def processMainEvent(self, pars):
    """
    processes events generated by the main window,
    the main interface component
    @param pars:
    for list see __c00_executeCommand
    @user: main window
    """
    self.__c00_executeCommand(pars)

  def getTheCursor(self, graphics_root_object, decoration, application, state):
    object_str = self.getObjectStr(
            application, decoration, graphics_root_object, state)

    if object_str not in self.mouse_automata[self.editor_phase][self.editor_state]:
      cursor = "undefined"
      actionR = ""
      actionL = ""
    else:
      cursor = self.mouse_automata[self.editor_phase][self.editor_state][object_str]["cursor"]
      actionL = self.mouse_automata[self.editor_phase][self.editor_state][object_str]["left"]["output"]
      actionR = self.mouse_automata[self.editor_phase][self.editor_state][object_str]["right"]["output"]

    self.showMouseActions(graphics_root_object, decoration,
                          self.cursors.getBixMap(cursor), actionL, actionR)

    return self.cursors[cursor]

  def getObjectStr(self, application, decoration, graphics_root_object, state):
    r, d, a, s = self.graphics_data.getActiveObjectRootDecorationState(self.editor_phase,
                                                                       graphics_root_object,
                                                                       decoration,
                                                                       application,
                                                                       state)
    object_str = str((r, d, s))
    return object_str

    # GUI and model interface -----------------------------------------------------

  def makeThisCurrentNode(self, nodeID):
    """
    opens, if not yet open, and puts node window on top
    @param nodeID: node ID
    """
    pars = {}
    pars["nodeID"] = nodeID
    pars["action"] = "zoom in"
    self.__c00_executeCommand(pars)

  # internal methods and model interface ---------------------------------------

  # internal methods -----------------------------------------------------------

  def __c00_executeCommand(self, pars):
    """
    Command handling
    @param pars: dictionary
    - "action" : action to be taken
    - "nodeID" : node ID
    - "object" : selected graph object
    - "pos"    : position
    - "file"   : file identifier
    - "arc"    : arc ID
    - "network": network name
    - "state"  : state inforation for injection for example
    """

    action = pars["action"]

    # self.stateIndicator(self.editor_state)
    if action == "None":
      res = {"failed": False}
    elif action == "-":
      res = {"failed": False}
    elif action == "zoom in":
      res = self.__c01_makeThisCurrentNode(pars["nodeID"])
    elif action == "add node":
      res = self.__c02_addNode(pars["pos"])
    elif action == "delete node":
      res = self.__c03_deleteNode(pars["nodeID"])
    elif action == "group nodes":
      res = self.__c04_groupNodes(pars["pos"])
    elif action == "explode node":
      res = self.__c05_explodeNode(pars["nodeID"])
    elif action == "begin arc":
      res = self.__c06_beginArc(pars["nodeID"])
    elif action == "add arc":
      res = self.__c07_addTheArc(pars["nodeID"])
    elif action == "remove arc":
      res = self.__c08_removeArc(pars["arc"])
    elif action == "re-direct arc":
      res = self.__c09_reconnectArc(pars["object"])
    elif action == "change arc":
      res = self.__c10_changeArc(pars["nodeID"])
    elif action == "insert knot":
      res = self.__c11_insertKnot()
    elif action == "remove knot":
      res = self.__c12_removeKnot()
    elif action == "make a copy":
      res = self.__c13_makeCopy(pars["nodeID"])
    elif action == "load from file":
      res = self.__c14_insertModelFromFile(pars["file"])
    elif action == "reset":
      res = self.__c15_reset()
    elif action == "name node":
      res = self.__c16_editName(pars["nodeID"])
    elif action == "library file":
      res = self.__c21_setCurrentLibFile(pars["file"])
    elif action == "map&save model":
      res = self.__c22_mapAndSaveModel(self.model_container, pars["file"])
    elif action == "save model":
      res = self.__c23_saveData(self.model_container, pars["file"])
    elif action == "insert model":
      res = self.__c25_insertSchnipsel(pars["pos"])
    elif action == "shift editor phase":
      res = self.__c26_shiftEditorPhase(pars["phase"])
    elif action == "select node":
      res = self.__c27_selectNode(pars["nodeID"])
    elif action == "inject":
      res = self.__c28_injectTypedTokensOrConversions(pars["nodeID"])
    elif action == "compute token distribution":
      res = self.__c31_computeTypedTokenDomains()
    elif action == "instantiate":
      res = self.__c52__InstantiateObject(pars)
    else:
      action = "-"
      res = {"failed": False}

    if res["failed"]:
      return

    if action in ["new model", "map&save model", "save model", "make a copy"]:
      self.modified = False
    elif action in ["add node", "delete node", "group nodes",
                    "explode node", "add arc", "remove arc",
                    "insert knot", "remove knot",
                    "insert model"]:
      self.modified = True  # TODO: handling of the modified to be completed
    self.main.markModifiedModel(self.modified)

    par_dic = res.copy()  # copy results into par list
    par_dic["viewed node"] = self.current_ID_node_or_arc

    return res

  def __c02_addNode(self, pos, network=None):
    """
    command: add node
    @param pos: position  QtPoint
    @return: dictionary
            "new node":           newnodeID,
            "network":            network
            "arc closed":         arcs_closed,
            "arc open at sink":   arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":             False
    """

    x, y = pos.x(), pos.y()

    if not network:
      network = self.main.current_network  # default
      named_network = self.main.current_named_network

      node_type = self.main.selected_node_type[self.main.current_network]
      node_class = NAMES["node"]

      node_characteristics, app = node_type.split(NODE_COMPONENT_SEPARATOR)
      if "intra" in node_characteristics:
        node_class = NAMES["intraface"]  # constructionsite;
        self.main.writeStatus(
                "cannot be inserted -- this is done automatically")

    else:
      node_class = NAMES["branch"]
      node_type = NAMES["branch"]
      named_network = NAMES["branch"]
      node_characteristics = ""

    features = self.applyNodeDefinitionRules(node_characteristics)

    if not network == "composite":
      current_inter_branch = None
      for inter_branch in self.main.ontology.list_inter_branches:
        for domain in self.main.ontology.intra_domains[inter_branch]:
          print("debugging -- ", inter_branch, domain)
          if network == domain:
            current_inter_branch = inter_branch
            break
      print("debugging -- found:", current_inter_branch, network)
      if not current_inter_branch:
        self.__abortNodeGeneration("no current item defined")
        return {"failed": True}

      node_type = self.main.selected_node_type[self.main.current_network]

      entities = list(self.main.ontology.node_arc_SubClasses.keys())
      selections = extract(entities,
                           filter_and=[
                                   current_inter_branch, "node", node_type],
                           filter_or=[],
                           filter_not=CR.CONNECTION_NETWORK_SEPARATOR)

      if not selections:
        self.__abortNodeGeneration("no entity defined")
        return {"failed": True}
      elif len(selections) == 1:
        entity_selection = selections[0]
      else:
        dia = VariantGUI(selections)
        dia.exec_()
        entity_selection = dia.selection

      if not entity_selection:
        self.__abortNodeGeneration("no entity selected")
        return {"failed": True}

      nw, node_or_arc, application, variant = splitEntity(entity_selection)
    else:
      variant = "composite"
      entity_selection = ""

    state = STATES[self.editor_phase]["nodes"][0]
    decoration_positions = ModelGraphicsData(node_class,
                                             x, y,  # this sets the initial position
                                             self.graphics_data,
                                             self.editor_phase,
                                             node_type,
                                             state)

    newnodeID = self.model_container.addChild(self.current_ID_node_or_arc,
                                              decoration_positions,
                                              network,
                                              named_network,
                                              node_class,
                                              node_type,
                                              features=features,
                                              variant=variant,
                                              entity_name=entity_selection)

    self.state_nodes[newnodeID] = STATES[self.editor_phase]["nodes"][0]

    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "new node": newnodeID,
            "failed"  : False
            }

  def __addBoundaryNode(self, pos, boundary, application, network, named_connection_network, entity_name):
    """
    command: add node
    @param pos: position  QtPoint
    @return: dictionary
            "new node":           newnodeID,
            "network":            network
            "arc closed":         arcs_closed,
            "arc open at sink":   arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":             False
    """

    x, y = pos.x(), pos.y()

    # network = self.main.current_network
    # named_network = self.main.named_network_dictionary[network]

    # RULE: node type for boundary is constraint to event dynamic

    nw, node_or_arc, application, variant = splitEntity(entity_name)
    token, mechanism, nature = splitApplication(application)

    features = None
    if boundary in [NAMES["intraface"], NAMES["arc node"]]:  # note: now the same as arc_node
      features = self.applyNodeDefinitionRules(NAMES["intraface"])
      features.append(token)
      features.append(NAMES["intraface"])
    elif boundary == NAMES["interface"]:
      application = self.main.ontology.list_inter_node_objects[0]
      features = self.applyNodeDefinitionRules("interface")
    else:
      print("fatal error no such boundary: ", boundary)

    node_class = boundary

    state = STATES[self.editor_phase]["nodes"][0]
    decoration_positions = ModelGraphicsData(node_class,
                                             x, y,  # this sets the initial position
                                             self.graphics_data,
                                             self.editor_phase,
                                             application,
                                             state)

    newnodeID = self.model_container.addChild(self.current_ID_node_or_arc,
                                              decoration_positions,
                                              network,
                                              named_connection_network,
                                              node_class,
                                              application,
                                              features=features,
                                              variant=variant,
                                              entity_name=entity_name)
    self.state_nodes[newnodeID] = state  # STATES[self.editor_phase]["nodes"][0]

    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "new node": newnodeID,
            "failed"  : False
            }

  def __c03_deleteNode(self, nodeID):
    """
    command: remove node nodeID
    @param nodeID: node ID
    @return: dictionary
            "deleted nodes": deleted_nodes,
            "deleted arcs":  deleted_arcs,
            "changed arcs":  changed_arcs,
            "failed": False
    """

    del_nodes = self.model_container.deleteNode(nodeID)

    print("deleting node %s on scene %s" %
          (nodeID, self.currently_viewed_node))

    for n in reversed(del_nodes):
      try:
        del self.state_nodes[n]
      except:
        pass

    self.redrawCurrentScene()

    return {"failed": False}

  def __c04_groupNodes(self, pos):
    """
    command: grouping and moving of nodes dependent on the event node
    if the event node is where the group is located, the group is "grouped"
    if the event node is another node, the group is moved.

    @note: The moving cannot be done to
    - any member (including subtrees) of the group
    - to a node which has an arc to a member of the group

    @param pos: position on where to locate the new node when grouping

    @return: dictionary
            "old node":   old_node,
            "new node":    nodeID,
            "moved nodes": moved_nodes,
            "failed":      False
    """
    #  groups if event node is the same as target node
    if not self.node_group:
      res = {}
      res["failed"] = True
      return res

    nodeGroupIDS = []
    for n in self.node_group:
      nodeGroupIDS.append(n.ID)

    arcGroupIDs = []
    for a in self.arc_group:
      arcGroupIDs.append(a.ID)

    # print("group - node group IDs:", nodeGroupIDS)

    pars = self.__c02_addNode(pos, network="composite")
    newNodeID = pars["new node"]
    self.model_container.groupNodes(newNodeID, nodeGroupIDS)
    for n in nodeGroupIDS:
      self.state_nodes[n] = STATES[self.editor_phase]["nodes"][0]

    for a in arcGroupIDs:
      self.state_arcs[a] = STATES[self.editor_phase]["arcs"][0]

    # clear selection
    self.resetGroups()

    self.model_container["nodes"][newNodeID]["class"] = NAMES["branch"]
    self.model_container["nodes"][newNodeID]["type"] = NAMES["branch"]

    parentID = self.model_container["ID_tree"].getImmediateParent(newNodeID)
    self.__redrawScene(parentID)

    return {
            "failed": False
            }

  def __c05_explodeNode(self, nodeID):
    """
    command: explode a node, inverse of grouping
    @param nodeID: node ID
    @return: dictionary
            "exploded node" : nodeID,
            "moved nodes"   : set,
            "failed": False
    """
    #  explode node

    parentID = self.model_container.explodeNode(nodeID)

    self.__redrawScene(parentID)

    return {
            "exploded node": nodeID,
            "failed"       : False
            }

  def __c01_makeThisCurrentNode(self, nodeID):
    """
    Command: flip page and show current node
    report nodes arcs etc
    @param nodeID: node ID
    @return: dictionary
            "viewed node": nodeID,
            "failed":      False
    """
    #        print "__c09_makeThisCurrentNode", ">__c09_makeThisCurrentNode>", nodeID

    # self.__resetNodeStatesAndSelectedArc()
    self.__redrawScene(nodeID)

    return {
            "viewed node": nodeID,
            "failed"     : False
            }

  def __c06_beginArc(self, nodeID):
    """
    begin generating an arc. Marks a node as begin point for arc.
    @param nodeID: node ID
    @return: dictionary
            "selected source": nodeID,
            "failed":          False
    """
    #  start an arc
    self.state_nodes[nodeID] = "selected"
    # nw = self.main.current_network
    self.arcSourceID = nodeID  # used in addThe Arc
    self.current_ID_node_or_arc = self.model_container["ID_tree"].getImmediateParent(nodeID)

    source = self.model_container["nodes"][nodeID]
    L_fromBoundary = source["class"] in [NAMES["intraface"], NAMES["interface"]]
    if L_fromBoundary:
      missing_input_arc, missing_output_arc = self.model_container.checkforMissingBoundaryArcs()
      L_inputMissing =  nodeID in missing_input_arc
      L_outputMissing = nodeID in missing_output_arc

      if L_inputMissing and L_outputMissing:
        return self.__abortArcGeneration("node arc is isolated -- delete !")

      arcs_out, arcs_in = self.model_container.getArcsInAndOutOfNode(nodeID)
      children = self.model_container["ID_tree"].getLeaves(0)
      if L_inputMissing:
        # get output properties
        existing_arc = arcs_out[0]
      else:
        # get input properties
        existing_arc = arcs_in[0]

      this_arc = self.model_container["arcs"][existing_arc]
      token = this_arc["token"]
      mechanism = this_arc["mechanism"]
      nature = this_arc["nature"]
      variant = this_arc["variant"]
      network = this_arc["network"]
      named_network = this_arc["named_network"]

      for child in children:
        if source["type"] in [NAMES["intraface"], NAMES["interface"]]:
          if child is not nodeID:
            self.state_nodes[child] = "block"

        if token not in self.model_container["nodes"][nodeID]["entity_id"]:
          self.state_nodes[child] = "blocked"

    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "selected source": nodeID,
            "failed"         : False
            }

  def __c07_addTheArc(self, toNodeID):
    """
    Command: add arc from marked node to "toNodeID" node completes what started with begin arc
    @param toNodeID: destination node ID
    @return: dictionary
            "added arc":  arcID,
            "source node": self.selected_node.getNodeID(),
            "sink node":   toNodeID,
            "failed":      False
    """

    # L_differentDomains = False
    # L_fromBoundary = False
    # L_toBoundary = False
    # L_outputMissing = None
    # L_inputMissing = None

    # get source & sink, domains and node classes
    fromNodeID = self.arcSourceID

    source = self.model_container["nodes"][fromNodeID]
    sink = self.model_container["nodes"][toNodeID]
    parent_nodeID_source = self.model_container["ID_tree"].getImmediateParent(self.arcSourceID)
    self.current_ID_node_or_arc = parent_nodeID_source  # insert on source side

    # find intra domains ------------------------------------------------------------------------------
    source_intra_domain = None
    sink_intra_domain = None
    for d in self.main.ontology.intra_domains:
      if sink["network"] in self.main.ontology.intra_domains[d]:
        sink_intra_domain = d
      if source["network"] in self.main.ontology.intra_domains[d]:
        source_intra_domain = d

    if (source_intra_domain == None) or (sink_intra_domain == None):
      self.__abortArcGeneration("there is as serious problem with the ontology")

    # intra or inter -----------------------------------------------------------------------------------
    L_differentDomains = source_intra_domain != sink_intra_domain

    L_fromBoundary = source["class"] in [NAMES["intraface"], NAMES["interface"]]
    L_toBoundary = sink["class"] in [NAMES["intraface"], NAMES["interface"]]

    if L_fromBoundary and L_toBoundary:
      return self.__abortArcGeneration("boundary to boundary is not allowed")

    if L_fromBoundary or L_toBoundary:
      # insert missing arc
      if L_fromBoundary:
        arcs_out, arcs_in = self.model_container.getArcsInAndOutOfNode(fromNodeID)
      elif L_toBoundary:
        arcs_out, arcs_in = self.model_container.getArcsInAndOutOfNode(toNodeID)
      else:
        arcs_out = arcs_in = []
      missing_input_arc, missing_output_arc = self.model_container.checkforMissingBoundaryArcs()
      L_inputMissing = False
      L_outputMissing = False
      if fromNodeID in missing_input_arc:
        # fromNode points to boundary thus fromNode will be sink for the arc
        L_inputMissing = True
        insertArcSource = toNodeID
        insertArcSink = fromNodeID
      elif toNodeID in missing_input_arc:
        # toNode point is boundary
        L_inputMissing = True
        insertArcSource = fromNodeID
        insertArcSink = toNodeID
      elif fromNodeID in missing_output_arc:
        # fromNode is boundary
        L_outputMissing = False
        insertArcSource = fromNodeID
        insertArcSink = toNodeID
      elif toNodeID in missing_output_arc:
        # toNode is boundary
        L_outputMissing = False
        insertArcSource = toNodeID
        insertArcSink = fromNodeID
      else:
        self.main.writeStatus("no input no output ????")
        return self.__abortArcGeneration("no input no output ????")

      print("debugging -- insert missing arc")

      if L_inputMissing and L_outputMissing:
        return self.__abortArcGeneration("node arc is isolated -- delete !")

      if L_inputMissing:
        # get output properties
        existing_arc = arcs_out[0]
      else:
        # get input properties
        existing_arc = arcs_in[0]

      this_arc = self.model_container["arcs"][existing_arc]
      token = this_arc["token"]
      mechanism = this_arc["mechanism"]
      nature = this_arc["nature"]
      variant = this_arc["variant"]
      network = this_arc["network"]
      named_network = this_arc["named_network"]

      arcID, views_with_arc = self.model_container.addArc(insertArcSource, insertArcSink,
                                                          network,
                                                          named_network,
                                                          mechanism,
                                                          token,
                                                          nature,
                                                          variant=variant)



    else:
      # insert full arc

      # get entity

      named_connection_network = CR.TEMPLATE_CONNECTION_NETWORK % (source["named_network"], sink["named_network"])

      selected_tokens, _, entities = self.__getAllowedTokens(sink, source)
      if L_differentDomains:# named connection network
        # connection of two networks
        connection_network = CR.TEMPLATE_CONNECTION_NETWORK % (source_intra_domain, sink_intra_domain)
        ands = [connection_network, ]
        ors = []
      else:
        ands = [source_intra_domain, "arc"]
        ors = [selected_tokens]

      # get possible entities --------------------------------------------------------------------------
      selections = extract(entities, filter_and=ands, filter_or=ors, filter_not=[])

      if len(selections) == 1:
        selected_entity = selections[0]
      elif len(selections) == 0:
        return self.__abortArcGeneration("there is no entity defined")
      else:
        dialogue = VariantGUI(selections)
        dialogue.exec_()
        selected_entity = dialogue.selection

      if not selected_entity:
        return self.__abortArcGeneration("there was no entity")

      if L_differentDomains:
        # get interface properties
        boundary = NAMES["interface"]
        dummy_Interface = Interface(
                "label", "left_network", "right_network", "left_variable_classes")
        token = dummy_Interface["token"]
        mechanism = dummy_Interface["mechanism"]
        nature = dummy_Interface["nature"]
        variant = "interface"  # RULE: variant is being fixed for the time being
        application = CR.TEMPLATE_ARC_APPLICATION % (token, mechanism, nature)
      else:
        # get intraface properties
        boundary = NAMES["arc node"]
        nw, node_or_arc, application, variant = splitEntity(selected_entity)
        token, mechanism, nature = splitApplication(application)
        connection_network = self.main.current_network

      pos = self.__getMidPoint(fromNodeID, toNodeID)
      pars = self.__addBoundaryNode(pos, boundary, application,
                                   connection_network, named_connection_network, selected_entity)
      newnodeID = pars["new node"]
      self.model_container["nodes"][newnodeID]["transfer_constraints"][token] = [ ]

      arcID, views_with_arc = self.model_container.addArc(fromNodeID, newnodeID,
                                                          source["network"],
                                                          source["named_network"],
                                                          mechanism,
                                                          token,
                                                          nature,
                                                          variant=variant)

      arcID, views_with_arc = self.model_container.addArc(newnodeID, toNodeID,
                                                          sink["network"],
                                                          sink["named_network"],
                                                          mechanism,
                                                          token,
                                                          nature,
                                                          variant=variant)


    # if not L_differentDomains:  # two different domains
    #   print("debugging two different domains --> ")
    #   insert_interface = True
    #
    # # are we in the physical domain ---------------------------------------------------------------------
    # source_domain_physical = source["network"] in self.main.ontology.heirs_network_dictionary["physical"]
    # sink_domain_physical = sink["network"] in self.main.ontology.heirs_network_dictionary["physical"]
    #
    # # named connection network
    # named_connection_network = CR.TEMPLATE_CONNECTION_NETWORK % (source["named_network"], sink["named_network"])
    #
    # # connection of two networks
    # connection_network = CR.TEMPLATE_CONNECTION_NETWORK % (source_intra_domain, sink_intra_domain)
    #
    # # nature of the connection
    # selected_token, _, entities = self.__getAllowedTokens(sink, source)
    # both_in_physics_domain = sink_domain_physical and source_domain_physical
    #
    # # or any other domain
    # if both_in_physics_domain:
    #   # print("debugging -- insert normal arc in the corresponding intra domain")
    #   insert_physics_arc = True
    #   source_is_arc_node = (source["class"] == NAMES["arc node"])
    #   sink_is_arc_node = (sink["class"] == NAMES["arc node"])
    #   if sink_is_arc_node and source_is_arc_node:  # rule: boundary to boundary is forbidden
    #     self.__abortArcGeneration("you cannot connect boundaries to boundaries")
    #     return {"failed": True}
    #
    #   if source_is_arc_node:
    #     arcs_out, arcs_in = self.model_container.getArcsInAndOutOfNode(fromNodeID)
    #   elif sink_is_arc_node:
    #     arcs_out, arcs_in = self.model_container.getArcsInAndOutOfNode(toNodeID)
    #   else:
    #     arcs_out = arcs_in = []
    #
    #
    #   reverse = False
    #   if source_is_arc_node or sink_is_arc_node:
    #     missing_input_arc, missing_output_arc = self.model_container.checkforMissingBoundaryArcs()
    #     if fromNodeID in missing_input_arc:
    #       make_new_input_arc = True
    #       reverse = True  # reverse
    #       arc_node_ID = fromNodeID
    #       existing_arc = arcs_out[0]
    #       # get output info
    #     elif fromNodeID in missing_output_arc:
    #       make_new_output_arc = True
    #       reverse = False  # "do not reverse"
    #       arc_node_ID = fromNodeID
    #       existing_arc = arcs_in[0]
    #       # get input arc info
    #     elif toNodeID in missing_input_arc:
    #       make_new_input_arc = True
    #       reverse = False  # "do not reverse"
    #       arc_node_ID = toNodeID
    #       existing_arc = arcs_out[0]
    #       # get output arc info
    #     elif toNodeID in missing_output_arc:
    #       make_new_output_arc = True
    #       arc_node_ID = toNodeID
    #       existing_arc = arcs_in[0]
    #       reverse = True
    #       # get output arc info
    #     else:
    #       make_new_input_arc = True      &&&&&&&&&&&&
    #       make_new_output_arc = True
    #     print("debugging -- got here")
    #
    # selected_variant = None
    # if not arc_node_ID:
    #   if insert_physics_arc:  # RULE: physics arcs have intrafaces
    #     ands = [source_intra_domain, "arc"]
    #     ors = [selected_token]
    #   elif insert_interface:
    #     ands = [connection_network, ]
    #     ors = []
    #   else:  # RULE: non-physics arcs have no intraface
    #     ands = [source_intra_domain, "arc"]
    #     ors = [selected_token]
    #
    #   # get possible entities --------------------------------------------------------------------------
    #   selections = extract(entities, filter_and=ands, filter_or=ors, filter_not=[])
    #
    #   if len(selections) == 1:
    #     selected_entity = selections[0]
    #   elif len(selections) == 0:
    #     return self.__abortArcGeneration("there is no entity defined")
    #   else:
    #     dialogue = VariantGUI(selections)
    #     dialogue.exec_()
    #     selected_entity = dialogue.selection
    #
    #   if not selected_entity:
    #     return self.__abortArcGeneration("there was no entity")
    # # else:
    # #   selected_variant = self.model_container["arcs"][existing_arc]["variant"]
    #
    # if insert_physics_arc:
    #   if make_new_input_arc or make_new_output_arc:
    #     this_arc = self.model_container["arcs"][existing_arc]
    #     token = this_arc["token"]
    #     mechanism =  this_arc["mechanism"]
    #     nature = this_arc["nature"]
    #     variant = this_arc["variant"]
    #   else:
    #     boundary = NAMES["arc node"]
    #     nw, node_or_arc, application, variant = splitEntity(selected_entity)
    #     token, mechanism, nature = splitApplication(application)
    #     connection_network = self.main.current_network
    # elif insert_interface:
    #   boundary = NAMES["interface"]
    #   dummy_Interface = Interface(
    #           "label", "left_network", "right_network", "left_variable_classes")
    #   token = dummy_Interface["token"]
    #   mechanism = dummy_Interface["mechanism"]
    #   nature = dummy_Interface["nature"]
    #   variant = "interface"  # RULE: variant is being fixed for the time being
    #   application = CR.TEMPLATE_ARC_APPLICATION % (token, mechanism, nature)
    # else:
    #   boundary = None
    #   application = None
    #   mechanism = None
    #   nature = None
    #   variant = None
    #   token = None
    #
    # pos = self.__getMidPoint(fromNodeID, toNodeID)
    #
    # if (insert_physics_arc or insert_interface):
    #   if not(make_new_output_arc or make_new_input_arc):
    #     pars = self.__addBoundaryNode(pos, boundary, application,
    #                                   connection_network, named_connection_network, selected_entity)
    #     newnodeID = pars["new node"]
    #
    #   if make_new_input_arc:
    #     if reverse:
    #       newnodeID = fromNodeID
    #       source_node = toNodeID
    #     else:
    #       newnodeID = toNodeID
    #       source_node = fromNodeID
    #   else:
    #     source_node = self.arcSourceID
    #   arcID, views_with_arc = self.model_container.addArc(source_node, newnodeID,
    #                                                       source["network"],
    #                                                       source["named_network"],
    #                                                       mechanism,
    #                                                       token,
    #                                                       nature,
    #                                                       variant=variant)
    #   # used in colouring
    #   self.model_container["nodes"][newnodeID]["transfer_constraints"][token] = [
    #           ]
    #
    # else:
    #   newnodeID = fromNodeID
    #
    # if make_new_output_arc:
    #   if reverse:
    #     newnodeID = toNodeID
    #     toNodeID = fromNodeID
    #   else:
    #     newnodeID = fromNodeID
    #
    # if make_new_output_arc:
    #   arcID, views_with_arc = self.model_container.addArc(newnodeID, toNodeID,
    #                                                       sink["network"],
    #                                                       sink["named_network"],
    #                                                       mechanism,
    #                                                       token,
    #                                                       nature,
    #                                                       variant=variant)

    self.state_nodes[self.arcSourceID] = STATES[self.editor_phase]["arcs"][0]
    self.arcSourceID = None

    self.clearSelectedNodes()
    self.clearBlockedNodes()

    self.current_ID_node_or_arc = self.model_container["ID_tree"].getImmediateParent(toNodeID)

    self.model_container.updateTokensInAllDomains()
    self.model_container.updateTypedTokensInAllDomains()
    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "added arc": arcID,
            "sink node": toNodeID,
            "failed"   : False
            }

# ======================================================
    # insert_interface = False
    # insert_physics_arc = False
    # make_new_input_arc = False
    # make_new_output_arc = False
    # arc_node_ID = None
    # existing_arc = None
    #
    # fromNodeID = self.arcSourceID
    #
    # source = self.model_container["nodes"][fromNodeID]
    # sink = self.model_container["nodes"][toNodeID]
    # # entities = list(self.main.ontology.node_arc_SubClasses.keys())
    #
    # parent_nodeID_source = self.model_container["ID_tree"].getImmediateParent(self.arcSourceID)
    # self.current_ID_node_or_arc = parent_nodeID_source  # insert on source side
    #
    # # find intra domains ------------------------------------------------------------------------------
    # source_intra_domain = None
    # sink_intra_domain = None
    # for d in self.main.ontology.intra_domains:
    #   if sink["network"] in self.main.ontology.intra_domains[d]:
    #     sink_intra_domain = d
    #   if source["network"] in self.main.ontology.intra_domains[d]:
    #     source_intra_domain = d
    #
    # if (source_intra_domain == None) or (sink_intra_domain == None):
    #   self.__abortArcGeneration("there is as serious problem with the ontology")
    #
    # # intra or inter -----------------------------------------------------------------------------------
    # same_intra_domain = source_intra_domain == sink_intra_domain
    #
    # if not same_intra_domain:  # two different domains
    #   print("debugging two different domains --> ")
    #   insert_interface = True
    #
    # # are we in the physical domain ---------------------------------------------------------------------
    # source_domain_physical = source["network"] in self.main.ontology.heirs_network_dictionary["physical"]
    # sink_domain_physical = sink["network"] in self.main.ontology.heirs_network_dictionary["physical"]
    #
    # # named connection network
    # named_connection_network = CR.TEMPLATE_CONNECTION_NETWORK % (source["named_network"], sink["named_network"])
    #
    # # connection of two networks
    # connection_network = CR.TEMPLATE_CONNECTION_NETWORK % (source_intra_domain, sink_intra_domain)
    #
    # # nature of the connection
    # selected_token, _, entities = self.__getAllowedTokens(sink, source)
    # both_in_physics_domain = sink_domain_physical and source_domain_physical
    #
    # # or any other domain
    # if both_in_physics_domain:
    #   # print("debugging -- insert normal arc in the corresponding intra domain")
    #   insert_physics_arc = True
    #   source_is_arc_node = (source["class"] == NAMES["arc node"])
    #   sink_is_arc_node = (sink["class"] == NAMES["arc node"])
    #   if sink_is_arc_node and source_is_arc_node:  # rule: boundary to boundary is forbidden
    #     self.__abortArcGeneration("you cannot connect boundaries to boundaries")
    #     return {"failed": True}
    #
    #   if source_is_arc_node:
    #     arcs_out, arcs_in = self.model_container.getArcsInAndOutOfNode(fromNodeID)
    #   elif sink_is_arc_node:
    #     arcs_out, arcs_in = self.model_container.getArcsInAndOutOfNode(toNodeID)
    #   else:
    #     arcs_out = arcs_in = []
    #
    #
    #   reverse = False
    #   if source_is_arc_node or sink_is_arc_node:
    #     missing_input_arc, missing_output_arc = self.model_container.checkforMissingBoundaryArcs()
    #     if fromNodeID in missing_input_arc:
    #       make_new_input_arc = True
    #       reverse = True  # reverse
    #       arc_node_ID = fromNodeID
    #       existing_arc = arcs_out[0]
    #       # get output info
    #     elif fromNodeID in missing_output_arc:
    #       make_new_output_arc = True
    #       reverse = False  # "do not reverse"
    #       arc_node_ID = fromNodeID
    #       existing_arc = arcs_in[0]
    #       # get input arc info
    #     elif toNodeID in missing_input_arc:
    #       make_new_input_arc = True
    #       reverse = False  # "do not reverse"
    #       arc_node_ID = toNodeID
    #       existing_arc = arcs_out[0]
    #       # get output arc info
    #     elif toNodeID in missing_output_arc:
    #       make_new_output_arc = True
    #       arc_node_ID = toNodeID
    #       existing_arc = arcs_in[0]
    #       reverse = True
    #       # get output arc info
    #     else:
    #       make_new_input_arc = True      &&&&&&&&&&&&
    #       make_new_output_arc = True
    #     print("debugging -- got here")
    #
    # selected_variant = None
    # if not arc_node_ID:
    #   if insert_physics_arc:  # RULE: physics arcs have intrafaces
    #     ands = [source_intra_domain, "arc"]
    #     ors = [selected_token]
    #   elif insert_interface:
    #     ands = [connection_network, ]
    #     ors = []
    #   else:  # RULE: non-physics arcs have no intraface
    #     ands = [source_intra_domain, "arc"]
    #     ors = [selected_token]
    #
    #   # get possible entities --------------------------------------------------------------------------
    #   selections = extract(entities, filter_and=ands, filter_or=ors, filter_not=[])
    #
    #   if len(selections) == 1:
    #     selected_entity = selections[0]
    #   elif len(selections) == 0:
    #     return self.__abortArcGeneration("there is no entity defined")
    #   else:
    #     dialogue = VariantGUI(selections)
    #     dialogue.exec_()
    #     selected_entity = dialogue.selection
    #
    #   if not selected_entity:
    #     return self.__abortArcGeneration("there was no entity")
    # # else:
    # #   selected_variant = self.model_container["arcs"][existing_arc]["variant"]
    #
    # if insert_physics_arc:
    #   if make_new_input_arc or make_new_output_arc:
    #     this_arc = self.model_container["arcs"][existing_arc]
    #     token = this_arc["token"]
    #     mechanism =  this_arc["mechanism"]
    #     nature = this_arc["nature"]
    #     variant = this_arc["variant"]
    #   else:
    #     boundary = NAMES["arc node"]
    #     nw, node_or_arc, application, variant = splitEntity(selected_entity)
    #     token, mechanism, nature = splitApplication(application)
    #     connection_network = self.main.current_network
    # elif insert_interface:
    #   boundary = NAMES["interface"]
    #   dummy_Interface = Interface(
    #           "label", "left_network", "right_network", "left_variable_classes")
    #   token = dummy_Interface["token"]
    #   mechanism = dummy_Interface["mechanism"]
    #   nature = dummy_Interface["nature"]
    #   variant = "interface"  # RULE: variant is being fixed for the time being
    #   application = CR.TEMPLATE_ARC_APPLICATION % (token, mechanism, nature)
    # else:
    #   boundary = None
    #   application = None
    #   mechanism = None
    #   nature = None
    #   variant = None
    #   token = None
    #
    # pos = self.__getMidPoint(fromNodeID, toNodeID)
    #
    # if (insert_physics_arc or insert_interface):
    #   if not(make_new_output_arc or make_new_input_arc):
    #     pars = self.__addBoundaryNode(pos, boundary, application,
    #                                   connection_network, named_connection_network, selected_entity)
    #     newnodeID = pars["new node"]
    #
    #   if make_new_input_arc:
    #     if reverse:
    #       newnodeID = fromNodeID
    #       source_node = toNodeID
    #     else:
    #       newnodeID = toNodeID
    #       source_node = fromNodeID
    #   else:
    #     source_node = self.arcSourceID
    #   arcID, views_with_arc = self.model_container.addArc(source_node, newnodeID,
    #                                                       source["network"],
    #                                                       source["named_network"],
    #                                                       mechanism,
    #                                                       token,
    #                                                       nature,
    #                                                       variant=variant)
    #   # used in colouring
    #   self.model_container["nodes"][newnodeID]["transfer_constraints"][token] = [
    #           ]
    #
    # else:
    #   newnodeID = fromNodeID
    #
    # if make_new_output_arc:
    #   if reverse:
    #     newnodeID = toNodeID
    #     toNodeID = fromNodeID
    #   else:
    #     newnodeID = fromNodeID
    #
    # if make_new_output_arc:
    #   arcID, views_with_arc = self.model_container.addArc(newnodeID, toNodeID,
    #                                                       sink["network"],
    #                                                       sink["named_network"],
    #                                                       mechanism,
    #                                                       token,
    #                                                       nature,
    #                                                       variant=variant)
    #
    # self.state_nodes[self.arcSourceID] = STATES[self.editor_phase]["arcs"][0]
    # self.arcSourceID = None
    #
    # self.clearSelectedNodes()
    # self.clearBlockedNodes()
    #
    # self.current_ID_node_or_arc = self.model_container["ID_tree"].getImmediateParent(toNodeID)
    #
    # self.model_container.updateTokensInAllDomains()
    # self.model_container.updateTypedTokensInAllDomains()
    # self.__redrawScene(self.current_ID_node_or_arc)
    #
    # return {
    #         "added arc": arcID,
    #         "sink node": toNodeID,
    #         "failed"   : False
    #         }

  def __getMidPoint(self, fromNodeID, toNodeID):
    parent_nodeID_source = self.model_container["ID_tree"].getImmediateParent(
            fromNodeID)
    x_source = self.model_container["scenes"][parent_nodeID_source]["nodes"][fromNodeID]["position_x"]
    y_source = self.model_container["scenes"][parent_nodeID_source]["nodes"][fromNodeID]["position_y"]
    parent_nodeID_sink = self.model_container["ID_tree"].getImmediateParent(
            toNodeID)
    x_sink = self.model_container["scenes"][parent_nodeID_sink]["nodes"][toNodeID]["position_x"]
    y_sink = self.model_container["scenes"][parent_nodeID_sink]["nodes"][toNodeID]["position_y"]
    x_mid = x_sink + (x_source - x_sink) / 2
    y_mid = y_sink + (y_source - y_sink) / 2
    pos = QtCore.QPoint(x_mid, y_mid)
    return pos

  def __insetArcWithBoundary(self, source_node_ID, sink_node_ID, boundary, application, connection_network, named_connection_network):

    pos = self.__getMidPoint(source_node_ID, sink_node_ID)

    pars = self.__addBoundaryNode(
            pos, boundary, application, connection_network, named_connection_network)

  def __getAllowedTokens(self, sink, source):
    # find possible tokens left and right from the entities
    variant_source = source["variant"]
    type_source = source["type"]
    variant_sink = sink["variant"]
    type_sink = sink["type"]
    entities = list(self.main.ontology.node_arc_SubClasses.keys())
    source_entity = extract(entities, filter_and=[variant_source, type_source], filter_or=[
            ], filter_not=[])  # this should yield only one
    sink_entity = extract(entities, filter_and=[
            variant_sink, type_sink], filter_or=[], filter_not=[])  # ditto
    _, _, application, _ = splitEntity(source_entity[0])
    s_token, _, _, = splitApplication(application)
    _, _, application, _ = splitEntity(sink_entity[0])
    t_token, _, _, = splitApplication(application)
    source_tokens = s_token.split(CR.TOKEN_DELIMITER)
    sink_tokens = t_token.split(CR.TOKEN_DELIMITER)
    allowed_tokens = list(set(source_tokens) | set(sink_tokens))

    if len(allowed_tokens) == 1:
      selected_token = allowed_tokens[0]
    else:
      dialog = UI_RadioSelector(allowed_tokens, checked=[], allowed=1)
      dialog.exec_()
      selected_token = dialog.checked
      if not selected_token:
        return self.__abortArcGeneration("error >>> not token chosen")

    return selected_token, application, entities

  def __abortArcGeneration(self, msg):
    self.__resetNodeStatesAndSelectedArc()
    self.main.writeStatus(msg)
    self.__redrawScene(self.current_ID_node_or_arc)
    return {"failed": True}

  def __abortNodeGeneration(self, msg):
    self.__resetNodeStatesAndSelectedArc()
    self.main.writeStatus(msg)
    return {"failed": True}

  def __c11_insertKnot(self):
    """
    Command: insert knot into edge pointed to
    @postcondition: self.current_item.parentItem() must be an edge
    @return: dictionary
            "arc" : arcID,
            "failed" : False
    """

    #  insert knot in the middle
    edge = self.current_item.parent
    arcID = edge.arcID

    nodeA = edge.source
    nodeB = edge.dest
    # print("inser knot source dest:", nodeA.graphics_root_object,  nodeB.graphics_root_object)
    #
    middlePoint = edge.getMidPoint()
    position = middlePoint.x(), middlePoint.y()

    sourcePoint = nodeA.pos()
    s_x = sourcePoint.x()
    s_y = sourcePoint.y()
    destPoint = nodeB.pos()
    d_x = destPoint.x()
    d_y = destPoint.y()

    # sourceCoordinates, sinkCoordinates = self.model_container.getArcGraphicalData(self.current_ID_node_or_arc, arcID)
    # position = (sinkCoordinates[0]+sourceCoordinates[0])/2 , (sinkCoordinates[1]+sourceCoordinates[1])/2
    # s_x = sourceCoordinates[0]
    # s_y = sourceCoordinates[1]
    # d_x = sinkCoordinates[0]
    # d_y = sinkCoordinates[1]

    knot_list = self.model_container["scenes"][self.currently_viewed_node]["arcs"][arcID]
    # print("node list", knot_list)
    if len(knot_list) > 0:
      if nodeA.graphics_root_object == NAMES["elbow"]:
        if nodeB.graphics_root_object == NAMES["elbow"]:
          indexA = knot_list.index((s_x, s_y))
          indexB = knot_list.index((d_x, d_y))
        else:
          indexA = knot_list.index((s_x, s_y))
          indexB = -1
      else:
        if nodeB.graphics_root_object == NAMES["elbow"]:
          indexA = -1
          indexB = knot_list.index((d_x, d_y))

    else:
      indexA = -1
      indexB = -1

    # print("indices ", indexA, indexB)

    self.model_container.insertKnot(
            self.currently_viewed_node, arcID, indexA, indexB, position)

    self.redrawCurrentScene()
    # print("debugging -- knots")

    return {
            "arc"   : arcID,
            "failed": False
            }

  def __c08_removeArc(self, arcID):
    """
    Command: remove specified arc
    @param arcID: arc ID
    @return: dictionary
            "arc" : arcID,
            "failed": False
    """
    #  remove the identified arc
    #        print "__c14_removeArc", "remove arc ", arcID
    # check if this an arc that connects to an intraface or an interface
    arcs_to_delete = [arcID]

    # rule: delete both related arcs that are connected to an intraface
    intraface_interface_possibly_to_delete = None
    for node in self.model_container["nodes"]:
      if self.model_container["nodes"][node]["class"] == NAMES["intraface"]:
        arcs = self.model_container.getArcsConnectedToNode(node)
        if arcID in arcs:
          print("delete found an intraface")
          token1 = self.model_container["arcs"][arcID]["token"]
          mech1 = self.model_container["arcs"][arcID]["mechanism"]
          nature1 = self.model_container["arcs"][arcID]["nature"]
          for arcID2 in arcs:
            if arcID != arcID2:
              token2 = self.model_container["arcs"][arcID2]["token"]
              mech2 = self.model_container["arcs"][arcID2]["mechanism"]
              nature2 = self.model_container["arcs"][arcID2]["nature"]
              if (token1 == token2) and (mech1 == mech2) and (nature1 == nature2):
                arcs_to_delete.append(arcID2)
                intraface_interface_possibly_to_delete = node
      elif self.model_container["nodes"][node]["class"] == NAMES["interface"]:
        arcs = self.model_container.getArcsConnectedToNode(node)
        if arcID in arcs:
          print("delete found an interface")
          arcs_to_delete = arcs
          intraface_interface_possibly_to_delete = node

    # TODO: once a node has no arcs, it has no tokens thus the affected nodes need to be updated
    for arc in arcs_to_delete:
      self.model_container.deleteArc(arc)
      print("remove arc ", arc, " from ", self.currently_viewed_node)
      del self.state_arcs[arc]

    if intraface_interface_possibly_to_delete:
      arcs = self.model_container.getArcsConnectedToNode(
              intraface_interface_possibly_to_delete)
      if len(arcs) == 0:
        self.__c03_deleteNode(intraface_interface_possibly_to_delete)
      else:
        self.redrawCurrentScene()
    else:
      self.redrawCurrentScene()
    return {
            "arc"   : arcID,
            "failed": False
            }

  def __c12_removeKnot(self):
    """
    Command: remove knot
    @postcondition: self.current_item.parentItem() must be a knot
    @return: dictionary
            "arc": arcID,
            "failed": False
    """
    knot = self.current_item.parent
    self.model_container.removeKnot(self.currently_viewed_node, knot.arcID,
                                    knot.pos().x(), knot.pos().y())
    self.redrawCurrentScene()

    return {
            "arc"   : knot.arcID,
            "failed": False
            }

  def __c09_reconnectArc(self, pointer_object_name):
    """
    Command: starts reconnecting an existing arc
    @param pointer_object_name: is a end-pointer on the edge
    @return: dictionary
            "arc" :        self.selected_arcID,
            "target node": S_ID,
            "failed":      False
    """
    #  each edge =section of an arc between two knots, is direction sensitive
    #  it is the node closer to which knot one points to
    #  that is being selected, that is if it is not an open arc

    # todo: one cn now reconnect to another network -- must be disabled

    item = self.current_item
    self.selected_arcID = item.parent.getArcID()
    self.state_arcs[self.selected_arcID] = "selected"

    if NAMES["tail"] in pointer_object_name:
      self.end_to_move = "source"
      # str(self.model_container[
      node_to_block = (
              self.model_container["arcs"][self.selected_arcID]["sink"])
      # "arcs"][self.selected_arcID]["sink"]) #HAP: str --> int
    elif NAMES["head"] in pointer_object_name:
      self.end_to_move = "sink"
      # str(self.model_container[
      node_to_block = (
              self.model_container["arcs"][self.selected_arcID]["source"])
      # "arcs"][self.selected_arcID]["source"]) #HAP: str --> int

    self.state_nodes[node_to_block] = "selected"

    self.__resetNodeStatesAndSelectedArc()
    self.redrawCurrentScene()

    return {
            # "target node": S_ID,
            "failed": False
            }

  def __c10_changeArc(self, C_ID):
    """
    Command: change specified arc
    @param C_ID: new node"s ID where specified end of the arc is
                re-connected
    @postcondition: self.selected_arcID must contain an arc object's ID
    @return: dictionary
            "arc":               self.selected_arcID,
            "old source & sink": (old_source, old_sink),
            "new source & sink": (fromNode, toNode),
            "failed":            False
    """
    #  changing arc
    #  requires an
    #  - new nodeID: C_ID
    #  - arcID which was identified before being in self.selected_arcID
    #  - information if it is the source or the sink to be changed

    self.model_container.changeArc(self.selected_arcID,
                                   self.end_to_move,
                                   C_ID)

    self.state_arcs[self.selected_arcID] = STATES[self.editor_phase]["arcs"][0]
    nodeID = self.model_container["ID_tree"].getImmediateParent(C_ID)

    # revokes isolation of the current network
    self.__resetNodeStatesAndSelectedArc()
    self.__redrawScene(nodeID)

    return {
            "failed": False
            }

  def __c13_makeCopy(self, nodeID):
    """
    Command: make a copy of the subtree with the root nodeID
    @param nodeID: node ID of subtree's root
    @return: combined dictionaries
           containing: from model
                "root":     root,
                "node map": node_map,
                "arc map":  arc_map
            and __c22:
                "saved file": f,
                "failed": False
            and
                "new root" : nodeID
    """

    # get schnipsel name -- rule: new or used
    schnipsel_name_to_be_saved, new_model = askForModelFileGivenOntologyLocation(self.main.ontology_name,
                                                                                 left_icon="reject",
                                                                                 left_tooltip="reject",
                                                                                 right_icon="accept",
                                                                                 right_tooltip="accept",
                                                                                 alternative=True)

    container = self.model_container.extractSubtree(nodeID)

    schnipsel_file = FILES["model_file"] % (
            self.main.ontology_name, schnipsel_name_to_be_saved)
    model_directory = os.path.dirname(schnipsel_file)
    if not os.path.exists(model_directory):
      os.makedirs(model_directory)
    container.write(schnipsel_file)

    ff = os.path.basename(schnipsel_file)
    name, ext = os.path.splitext(ff)
    dir = os.path.dirname(schnipsel_file)
    new_model_file_path = os.path.join(dir, "%s_new%s" % (name, ext))
    self.__c24_save_new_model_file(container, new_model_file_path)

    self.main.writeStatus("saved schnipsel to %s" % new_model_file_path)
    self.schnipsel_file = schnipsel_file
    self.main.setSchnipsel(schnipsel_name_to_be_saved)

    res_dic = {}
    res_dic["new root"] = nodeID
    res_dic["failed"] = False

    return res_dic  # result from saving

  def __c14_insertModelFromFile(self, model_file):
    """
    Command: insert a model
    @return: dictionary
            "inserted nodes": nodes_on_root,
            "inserted arcs":  arcs,
            "node map":       node_map,
            "arc map":        arc_map,
            "arc closed": arcs_closed,
            "arc open at sink": arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":         False,
    """
    #  insert file as shown in main window

    if not model_file:
      self.main.writeStatus("no model defined")
      return

    f = model_file
    self.model_container.makeFromFile(f)
    self.main.named_network_dictionary = self.model_container["named_networks"]
    self.main.makeNamedNetworkBrushes()

    self.model_container.updateTokensInAllDomains()
    self.model_container.updateTypedTokensInAllDomains()

    self.__redrawScene(self.current_ID_node_or_arc)

    self._load_instantiation_values(f)

    return {
            "failed": False,
            }

  def _load_instantiation_values(self, model_file):
    ontology_name = self.model_container.ontology.ontology_name
    # TODO: Get the model name from somewhere else.
    model_name = Path(model_file).parent.name
    print(model_name)

    all_topology_objects = io.load_topology_objects(
            ontology_name,
            model_name,
            self.all_entities,
            )

    # TODO: Remove when InstInfo only comes from the new model file
    for _, node_info in self.model_container["nodes"].items():
      node_info["instantiated_variables"] = {}

    # Loading the instantiation information if it exists
    for top_obj_id, top_obj in all_topology_objects.items():
      number_id = int(top_obj_id.split("_")[1])
      if isinstance(top_obj, modeller_classes.EntityContainer):
        node = self.model_container["nodes"][number_id]
        node["instantiated_variables"] = top_obj.to_json()[
          "instantiated_variables"]

  def __c15_reset(self):
    """
    Command: reset from current operation
        - de-select selected nodes and arcs
        - deletes group
    @return: dictionary
            "failed": False
    """

    self.__resetNodeStatesAndSelectedArc()

    self.redrawCurrentScene()
    self.editor_state = GRAPH_EDITOR_STATES[self.editor_phase][0]

    return {"failed": False}

  def __c16_editName(self, nodeID):
    # NOTE: breaks the strict command design would need to be changed to receive a name from the protocol or
    # NOTE: an empty name then asking one for live change
    name = self.model_container["nodes"][nodeID]["name"]
    variant = self.model_container["nodes"][nodeID]["variant"]
    if name == "default":  # Note: set the default name
      name = "%s - %s" % (nodeID, variant)
    string_dialog = UI_GetString("new node name", "node name")
    string_dialog.setText(name)
    string_dialog.exec_()
    name = string_dialog.getText()
    self.__changeName(name)

    self.model_container["nodes"][nodeID]["name"] = name

    return {"failed": False}

  def __c21_setCurrentLibFile(self, schnipsel_file):
    """
    Command: set current schnipsel_file name
    @param name: schnipsel_file
    @return: dictionary
            "failed":       False
    """
    self.schnipsel_file = schnipsel_file
    return {
            "failed": False
            }

  # TODO this is obsolete model is always mapped just save maps!
  def __c22_mapAndSaveModel(self, model, f):
    """
    Command: map and save model.
    This remaps the whole model tree starting with root being 0 consecutive
    renumbering the nodes.
    @param model: model object
    @param f: file name
    @return: dictionary
           containing: from model
                "root":     root,
                "node map": node_map,
                "arc map":  arc_map
            and :
                "saved file": f,
                "failed": False
    """

    self.__c23_saveData(model, f)

    # print("__c22_mapAndSaveModel", "__map and save model in commander to file :", f)

    return {"failed": False}  # res_dic

  def __c23_saveData(self, model, f):
    """
    Command: save data on file f
    @param model: model object
    @param f: file name
    @return: dictionary
            "saved file": f,
            "failed": False
    """
    #
    # print("debugging -- library model name: ", self.library_model_name)
    # print("debugging -- model container   : ", self.model_container)
    ff = os.path.basename(f)
    name, ext = os.path.splitext(ff)
    dir = os.path.dirname(f)
    f_flat = os.path.join(dir, "%s_flat%s" % (name, ext))
    new_model_file_path = os.path.join(dir, "%s_new%s" % (name, ext))

    # NOTE: switched off node mapping 2024-01-29
    node_map = self.model_container.write(f)
    self.model_container.makeAndWriteFlatTopology(f_flat)
    self.__c24_save_new_model_file(self.model_container, new_model_file_path)

    # mapped_currently_viewed_node = node_map[int(self.currently_viewed_node)]   # NOTE: switched off node mapping 2024-01-29
    # self.currently_viewed_node = (mapped_currently_viewed_node)  # NOTE: switched off node mapping 2024-01-29
    self.__redrawScene(self.currently_viewed_node)

    # incomplete_nodes, incomplete_arcs = self.checkIfAllVariablesAreInitialsed()
    # if incomplete_nodes or incomplete_arcs:
    #   makeMessageBox("incomplete nodes %s\nincomplete arcs %s" %
    #                  (incomplete_nodes, incomplete_arcs), buttons=["OK"])

    # print("debugging -- __c23_saveData",
    #       "--------- currently node viewed : %s ---> %s" % (self.currently_viewed_node, mapped_currently_viewed_node))
    # print("debugging -- __c23_saveData", "--------- saved graph file:", f)
    return {
            "saved file": f,
            "failed"    : False
            }

  def __c24_save_new_model_file(self, model_container, new_model_file_path: str):
    pp(model_container["ID_tree"])
    pp(model_container["nodes"])
    pp(model_container["arcs"])

    all_topology_objects = {}
    map_number_id_to_str_id = {}

    # Adding main info to the topology objects
    for number_id, node_info in model_container["nodes"].items():
      data = {}
      if node_info["class"] == "node_composite":
        identifier = f"N_{str(number_id)}"
        data["identifier"] = identifier
        data["name"] = str(node_info["name"])
        all_topology_objects[identifier] = modeller_classes.NodeComposite(
                **data
                )

        map_number_id_to_str_id[number_id] = identifier
      elif (
              node_info["class"] == "node_simple" or
              node_info["class"] == "node_arc"
      ):
        data["name"] = str(node_info["name"])
        data["instantiated_variables"] = {}
        for var_id, inst_info in node_info["instantiated_variables"].items():
          data["instantiated_variables"][var_id] = {
                  eval(key): value
                  for key, value in inst_info.items()
                  }

        entity_id = node_info["entity_id"]
        data["entity_instance"] = self.all_entities[entity_id]

        if "tokens" in node_info:
          data["tokens"] = list(node_info["tokens"].keys())
          data["typed_tokens"] = copy.deepcopy(node_info["tokens"])
        else:
          data["tokens"] = []
          data["typed_tokens"] = {}

        data["network"] = node_info["network"]
        data["named_network"] = node_info["named_network"]

        data["parent_id"] = None

        if node_info["class"] == "node_simple":
          if "conversions" in node_info:
            data["conversions"] = node_info["conversions"]
          else:
            data["conversions"] = None

          identifier = f"N_{str(number_id)}"
          data["identifier"] = identifier
          all_topology_objects[identifier] = modeller_classes.NodeSimple(
                  **data
                  )
        else:
          identifier = f"A_{str(number_id)}"
          data["identifier"] = identifier
          all_topology_objects[identifier] = modeller_classes.Arc(
                  **data
                  )

        map_number_id_to_str_id[number_id] = data["identifier"]

    # After all ids have been converted we add parent and children id
    id_tree = model_container["ID_tree"]
    for number_id, node_info in model_container["nodes"].items():
      current_id = map_number_id_to_str_id[number_id]
      ancestors_number_id = id_tree[number_id]["ancestors"]
      if ancestors_number_id:
        parent_id = map_number_id_to_str_id[ancestors_number_id[0]]
        all_topology_objects[current_id].parent_id = parent_id

      if isinstance(
              all_topology_objects[current_id],
              modeller_classes.NodeComposite,
              ):
        children_number_ids = id_tree[number_id]["children"]
        children_ids = [
                map_number_id_to_str_id[child_number_id]
                for child_number_id in children_number_ids
                ]
        all_topology_objects[current_id].children_ids = children_ids

    # Adding the connection info from the arcs
    for connection_info in model_container["arcs"].values():
      source_number_id = connection_info["source"]
      sink_number_id = connection_info["sink"]

      source_id = map_number_id_to_str_id[source_number_id]
      sink_id = map_number_id_to_str_id[sink_number_id]

      all_topology_objects[source_id].add_outgoing_connection(sink_id)

    ontology_name = model_container.ontology.ontology_name
    model_name = self.library_model_name

    io.save_topology_objects(
            ontology_name,
            model_name,
            all_topology_objects,
            new_model_file_path,
            )

  def __c25_insertSchnipsel(self, position):
    """
    Command: insert a model
    @return: dictionary
            "inserted nodes": nodes_on_root,
            "inserted arcs":  arcs,
            "node map":       node_map,
            "arc map":        arc_map,
            "arc closed": arcs_closed,
            "arc open at sink": arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":         False,
            "library file":   self.library_model_name
    """
    #  insert file as shown in main window

    if not self.schnipsel_file:
      self.main.writeStatus("no schnipsel defined")
      return {"failed": True}

    f = self.schnipsel_file
    if not os.path.exists(f):
      self.main.writeStatus("no such file %s" % f)
      return {"failed": True}

    tree, node_map, arc_map, node_offset, parent_ID = \
      self.model_container.addFromFile(f, self.current_ID_node_or_arc,
                                       position,
                                       self.graphics_data,
                                       self.editor_phase)

    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "failed"      : False,
            "library file": self.library_model_name
            }

  def __c27_selectNode(self, nodeID):
    """
    selects and unselects
    :param nodeID: node ID as string
    :return:
    """
    # print("debugging -- selecting node")
    node_type = self.model_container["nodes"][nodeID]["class"]
    if node_type in [NAMES["node"], NAMES["intraface"]]:
      ancestors = self.model_container["ID_tree"].getAncestors(nodeID)
      parentID = ancestors[0]
      if self.state_nodes[nodeID] == "selected":
        self.node_group.remove(nodeID)
        self.state_nodes[nodeID] = "enabled"
      else:
        self.node_group.add(nodeID)
        self.state_nodes[nodeID] = "selected"
      if node_type in [NAMES["intraface"]]:
        self.selected_intraface_node = nodeID  # TODO: check if needed | actie
      self.__redrawScene(parentID)

    if node_type in [NAMES["branch"]]:
      self.__resetNodeStatesAndSelectedArc()
      self.__redrawScene(nodeID)

    return {"failed": False}

  def __c28_injectTypedTokensOrConversions(self, nodeID):
    self.node_group.add(nodeID)
    select = self.main.state_inject_or_constrain_or_convert
    if select == "inject":
      self.main.injectTypedTokens()
    elif select == "convert":
      self.main.injectConversions()
    elif select == "constrain":
      self.main.injectTypedTokenTransferConstraints()
    return {"failed": False}

  def __c31_computeTypedTokenDomains(self):

    print("__c31_computeTypedTokenDomains -- not yet implemented")
    return {"failed": False}

  def __c41_makeInterface(self):
    print("__c41_makeInterface -- not yet implemented")
    self.variables = self.main.ontology.variables

  def __c51_AssignBehaviour(self):
    print("__c51_AssignBehaviour -- not yet implemented")

  def __c52__InstantiateObject(self, pars):
    """Handles the instantiation process.

    There are three main cases depending on the object to instantiate:

      # Single node.
      # Composite node.
      # Selection of nodes (single and/or composite)

    In cases 2 and 3 the group of nodes to be instantiated can be:

      * Same type of nodes (same entity). All non-required variables
        have the same instantiation state in all nodes.
      * Same type of nodes (same entity). At least one non-required
        variable has different instantiation state in one of the nodes.
      * Different type of nodes (different entities).

    Depending on the situation two types of instantiation can be
      performed:

      # Full instantiation: All variables can be instantiated. Allowed
          for:

        * Single node.
        * Composite and Selection if the nodes share the same type
          (entity) and all non-required variables have the same
          instantiation state in all nodes.
      # Partial instantiation: Only "required" variables can be
        instantiated. Used for all the other cases where there are
        differences between the nodes to be instantiated.

    Args:
        pars (* ): _description_

    Returns:
        _type_: _description_
    """
    # Pretty print for debug

    # pp(pars)
    # node_id = pars["nodeID"]
    # nodes_to_instantiate= []
    # node_groups = {}
    #
    # # dictionary node_group[entity_ID][node] = {variable: value}
    #
    #
    # if self.node_group == set():
    #   mode = "single"
    #   if node_id > 0:
    #     nodes_to_instantiate.append(node_id)
    #   else:
    #     print("Nothing to instantiate.")
    #     return {"failed": True}
    # else:
    #   for node in self.node_group:
    #     nodes_to_instantiate.append(node.ID)
    #
    # instances = {}
    # for node_id in nodes_to_instantiate:
    #   entity_ID = self._get_entity_name_from_node(node_id)
    #   if entity_ID not in node_groups:
    #     node_groups[entity_ID] =[node_id]
    #   entity = self.all_entities[entity_ID]
    #   init_vars = entity.get_init_vars()
    #   for v in init_vars:
    #     instances[v] = self.model_container["nodes"][node_id]["instantiated_variables"]
    #     # if instances[v]:
    #     #   dlg = InstantiationDlg(
    #     #           var_data_all,
    #     #           entity_behaviour,
    #     #           self.all_variables,
    #     #           single_node_instantiation,
    #     #           self.main,
    #     #           )
    #
    # # =========================================================

    nodes_to_instantiate = []
    if "arc" in pars:
      print("debugg -- instantiate arc")
      arcs_to_instantiate = [pars["arc"]]
    else:
      nodes_selection = set()

      if self.node_group == set():
        mode = "single"
        node_id = pars["nodeID"]
        if node_id > 0:
          nodes_selection.add(node_id)
        else:
          print("Nothing to instantiate.")
          return {"failed": True}
      else:
        for node in self.node_group:
          nodes_selection.add(node.ID)

      nodes_to_instantiate = self.nodes_to_be_instantiated(nodes_selection)

      vars_to_instantiate = self.node_vars_to_be_instantiated(
              nodes_to_instantiate)

      vars_instantiated = self.node_vars_being_instantiated(
              nodes_to_instantiate)

      dialog = InstantiationDialog(
              vars_to_instantiate, vars_instantiated, self.all_variables)
      dialog.setWindowTitle("define parameters for nodes %s" %
                            nodes_to_instantiate)
      dialog.exec_()

      newly_instantiated = dialog.newly_instantiated

      for var_id in newly_instantiated:
        for node_id in nodes_to_instantiate:
          entity = self.get_entity_node(node_id)
          try:
            vars = entity.init_vars
          except:
            print("error -- this is a problem with node ", node_id)
          if var_id in vars:
            if var_id in newly_instantiated:
              self.model_container["nodes"][node_id]["instantiated_variables"][var_id] = newly_instantiated[var_id]
      pass

      # ==============================  arcs =========================================
      arcs_to_instantiate = self.arcs_to_be_instantiated(nodes_to_instantiate)
      # print("debugg - arcs", arcs_to_instantiate)

    # --
    vars_to_instantiate = self.arc_vars_to_instantiate(arcs_to_instantiate)
    vars_instantiated = self.arc_vars_being_instantiated(arcs_to_instantiate)

    # --

    if vars_to_instantiate:
      dialog = InstantiationDialog(
              vars_to_instantiate, vars_instantiated, self.all_variables)
      dialog.setWindowTitle("define parameters for arcs: %s" %
                            arcs_to_instantiate)
      dialog.exec_()

      newly_instantiated = dialog.newly_instantiated

      for var_id in newly_instantiated:
        for arc_id in arcs_to_instantiate:
          entity = self.get_entity_arc(arc_id)
          vars = entity.init_vars
          if var_id in vars:
            if var_id in newly_instantiated:
              self.model_container["arcs"][arc_id]["instantiated_variables"][var_id] = newly_instantiated[var_id]
    pass

    self.checkIfAllVariablesAreInitialsed()

    return {"failed": False}

  def arc_vars_being_instantiated(self, arcs_to_instantiate):
    vars_instantiated = {}
    for arc_id in arcs_to_instantiate:
      values = self.model_container["arcs"][arc_id]["instantiated_variables"]
      for var_id in values:
        if var_id not in vars_instantiated:
          vars_instantiated[var_id] = {values[var_id]}
        else:
          vars_instantiated[var_id].add(values[var_id])
      pass
    return vars_instantiated

  def arc_vars_to_instantiate(self, arcs_to_instantiate):
    # make a dictionary: hash: variable ID, value: list of node IDs with this variable
    vars_to_instantiate = {}
    for arc_id in arcs_to_instantiate:
      entity = self.get_entity_arc(arc_id)
      if entity:
        vars = entity.init_vars
        for v in vars:
          if v not in vars_to_instantiate:
            vars_to_instantiate[v] = [arc_id]
          else:
            vars_to_instantiate[v].append(arc_id)
        pass
    return vars_to_instantiate

  def arcs_to_be_instantiated(self, nodes_to_instantiate):
    arcs_to_instantiate = set()
    for node_id in nodes_to_instantiate:
      for arc_id in self.model_container["arcs"]:
        if node_id == self.model_container["arcs"][arc_id]["source"]:
          for n_id in nodes_to_instantiate:
            if n_id == self.model_container["arcs"][arc_id]["sink"]:
              arcs_to_instantiate.add(arc_id)
    return arcs_to_instantiate

  def node_vars_being_instantiated(self, nodes_to_instantiate):
    vars_instantiated = {}
    for node_id in nodes_to_instantiate:
      values = self.model_container["nodes"][node_id]["instantiated_variables"]
      for var_id in values:
        if var_id not in vars_instantiated:
          vars_instantiated[var_id] = {values[var_id]}
        else:
          vars_instantiated[var_id].add(values[var_id])
      pass
    return vars_instantiated

  def node_vars_to_be_instantiated(self, nodes_to_instantiate):
    # make a dictionary: hash: variable ID, value: list of node IDs with this variable
    vars_to_instantiate = {}
    for node_id in nodes_to_instantiate:
      entity = self.get_entity_node(node_id)
      if entity:
        vars = entity.init_vars
        for v in vars:
          if v not in vars_to_instantiate:
            vars_to_instantiate[v] = [node_id]
          else:
            vars_to_instantiate[v].append(node_id)
        pass
    return vars_to_instantiate

  def nodes_to_be_instantiated(self, nodes_selection):
    # Using a queue to get all the simple nodes inside composite nodes.
    nodes_to_instantiate = set()
    node_queue = deque(nodes_selection)
    while node_queue:
      node_id = node_queue.popleft()
      node_class = self.model_container["nodes"][node_id]["class"]
      if node_class in ["node_simple", 'node_intraface']:
        nodes_to_instantiate.add(node_id)
      elif node_class == "node_composite":
        children = self.model_container["ID_tree"].getLeaves(
                node_id)  # getChildren(node_id)
        for i in children:
          node_class = self.model_container["nodes"][i]["class"]
          if node_class == "node_simple":
            nodes_to_instantiate.add(i)
    return nodes_to_instantiate

  def get_entity_node(self, node_id):
    entity_ID = self._get_entity_name_from_node(node_id)
    if not entity_ID:
      return None
    entity = self.all_entities[entity_ID]
    return entity

  def get_entity_arc(self, arc_id):
    entity_ID = self._get_entity_name_from_arc(arc_id)
    if not entity_ID:
      return None
    entity = self.all_entities[entity_ID]
    return entity

  def checkIfAllVariablesAreInitialsed(self):
    nodes = self.model_container["ID_tree"].getAllLeaveNodes()
    arcs = sorted(self.model_container["arcs"].keys())

    incomplete_nodes = {}
    node_vars_must_instantiate = {}
    arc_vars_must_be_instantitate = {}

    for node_id in nodes:
      vars_being_instantiated = sorted(
              self.node_vars_being_instantiated([node_id]))
      node_vars_must_instantiate[node_id] = sorted(
              self.node_vars_to_be_instantiated([node_id]))

      not_instantiated = set(node_vars_must_instantiate[node_id]) - \
                         set(vars_being_instantiated)
      if not_instantiated:
        incomplete_nodes[node_id] = not_instantiated

    incomplete_arcs = {}
    for arc_id in arcs:
      vars_being_instantiated = sorted(
              self.arc_vars_being_instantiated([arc_id]))
      arc_vars_must_be_instantitate[arc_id] = sorted(
              self.arc_vars_to_instantiate([arc_id]))
      not_instantiated = set(arc_vars_must_be_instantitate[arc_id]) - \
                         set(vars_being_instantiated)
      if not_instantiated:
        incomplete_arcs[arc_id] = not_instantiated

    print("incomplete nodes: %s" % incomplete_nodes)
    print("incomplete arcs:  %s" % incomplete_arcs)

    self.main.writeStatus("incomplete nodes: %s\nincomplete arcs: %s" % (
            incomplete_nodes, incomplete_arcs))

    for node_id in self.model_container["nodes"]:
      instances = self.model_container["nodes"][node_id]["instantiated_variables"]
      vars_in_the_list = list(instances.keys())
      for var_ID in vars_in_the_list:
        if var_ID not in node_vars_must_instantiate[node_id]:
          instances.pop(var_ID)
          print("node pop", var_ID)

    for arc_id in self.model_container["arcs"]:
      instances = self.model_container["arcs"][arc_id]["instantiated_variables"]
      vars_in_the_list = list(instances.keys())
      for var_ID in vars_in_the_list:
        if var_ID not in arc_vars_must_be_instantitate[arc_id]:
          instances.pop(var_ID)
          print("arc pop", var_ID)

    return incomplete_nodes, incomplete_arcs

  # TODO: check if code is still used
  def _get_instantiation_variables(
          self,
          nodes_to_instantiate: List[int],
          ) -> Tuple[Optional[entity.Entity], List[VariableInfo]]:
    """Finds the variables that will be instantiated.

    The variables that will be instantiated depend on:

      * Type of entities linked to the nodes.

        * Same type.
        * Different type.

      * Individual variables that have already been instantiated.

        * The variable has not been instantiated in any node.
        * The variable has been instantiated in all nodes with the same
          value.
        * The variable has been instantiated in all nodes with different
          values.
        * The variable has been instantiated only in some nodes.

    There are two types of instantiation:

      * Full instantiation: All variables in the entity linked to the
        nodes can be instantiated.
      * Partial instantiation: Only required variables can be
        instantiated.

    If the nodes correspond to different entities we do partial
    instantiation.

    If the nodes correspond to the same entity, the variables that are
    not "required" need to be checked. If the instantiation state
    (whether the variable has been instantiated or not) of at least one
    of them is not the same in all nodes then we do partial
    instantiation. Else we do full instantiation.

    Args:
      nodes_to_instantiate (list[int]): List of nodes that will be
      instantiated.

    Returns:
      Tuple[Optional[entity.Entity], List[VariableInfo]]: Contains
        information about the variables that will be instantiated:

        * First element: Is None if partial instantiation is to be
          carried. Otherwise it contains the information of the entity
          linked to all nodes.
        * Second: Each element contains the data of a single variable
          with the following fields.

          * id (str): The variable id.
          * same_in_all_nodes (bool): True if the variable has been
            instantiated with the same value in all nodes or has not
            been instantiated in any. False otherwise.
          * value (Optional[float]): The value of the variable if it has
            been instantiated with the same value in all nodes.
            None otherwise.

    """
    var_data_all = []
    entity_required_variables = []
    entity_name = self._get_entity_name_from_node(nodes_to_instantiate[0])
    entity_behaviour = self.all_entities[entity_name]

    # Checking if all nodes correspond to the same entity and storing
    # the required variables for the entity linked to each node.
    nodes_are_same_entity = True
    for node_id in nodes_to_instantiate:
      name = self._get_entity_name_from_node(node_id)
      if name != entity_name:
        nodes_are_same_entity = False

      entity = self.all_entities[name]
      entity_required_variables.append(
              # entity.get_variables_to_instantiate()[0])
              entity.get_init_vars())

    if nodes_are_same_entity:
      # Getting data for the required variables
      _, var_data_all = self._get_var_data(
              entity_required_variables[0],
              nodes_to_instantiate,
              )

      # # Getting data for the rest of the variables
      # other_variables=entity_behaviour.get_variables_to_instantiate()[1]

      # full_instantiation, temp_var_data=self._get_var_data(
      #     other_variables,
      #     nodes_to_instantiate,
      # )

      # If all non-required variables are not in the same instantiation
      # state only partial instantiation will be done.
      # if full_instantiation:
      #   var_data_all.extend(temp_var_data)
      # else:
      #   entity_behaviour=None
      # TODO Add a dialog informing and maybe giving options to
      # continue or cancel
    else:
      entity_behaviour = None
      # Only required variables that are present in all the nodes can be
      # instantiated. This is always a partial instantiation.
      set_list_required_variables = [
              set(item) for item in entity_required_variables
              ]
      common_variables = list(
              set.intersection(*set_list_required_variables)
              )

      _, var_data_all = self._get_var_data(
              common_variables,
              nodes_to_instantiate,
              )

    return (entity_behaviour, var_data_all)

  def _get_var_data(
          self,
          var_list: List[str],
          node_list: List[int],
          ) -> Tuple[bool, List[VariableInfo]]:
    """Returns the data for variables in nodes.

    Also checks for each variable if its instantiation state is the same
    in all nodes.

    Args:
      var_list (List[str]): Ids of the variables which data is required.
      node_list (List[int]): Only need the data of the variables in
        these nodes.

    Returns:
      Tuple[bool, List[VariableInfo]]: Each element corresponds to:

        * First: True if all variables have the same instantiation state
          in all nodes. False otherwise.
        * Second: Each element contains the data of a single variable
          with the following fields.

          * id (str): The variable id.
          * same_in_all_nodes (bool): True if the variable has been
            instantiated with the same value in all nodes or has not
            been instantiated in any. False otherwise.
          * value (Optional[float]): The value of the variable if it has
            been instantiated with the same value in all nodes. None
            otherwise.
    """
    var_data = []
    all_same_instantiation_state = True
    for var_id in var_list:
      same_instantiation_state, var_info = self._check_var_for_selected_nodes(
              var_id,
              node_list,
              )

      var_data.append(var_info)
      if not same_instantiation_state:
        all_same_instantiation_state = False

    return all_same_instantiation_state, var_data

  def _check_var_for_selected_nodes(
          self,
          var_id: str,
          nodes: List[int],
          ) -> Tuple[bool, VariableInfo]:
    """Checks the value of a variable in different nodes.

    Args:
      var_id (str): Id of the variable.
      nodes (List[int]): List of node ids.

    Returns:
      Tuple[bool, VariableInfo]: Each element corresponds to:

        * First: True if the instantiation state (instantiated or not)
          is the same in all nodes. False otherwise.

        * Second: Information about the variable with the following
          fields:

          * id (str): The variable id.
          * same_in_all_nodes (bool): True if the variable has been
            instantiated with the same value in all nodes or has not
            been instantiated in any. False otherwise.
          * value (float or None): The value of the variable if it has
            been instantiated with the same value in all nodes.
            None otherwise.
    """
    first_var_value = self._get_instantiation_value(var_id, nodes[0])
    var_have_same_value = True
    is_a_value_none = False

    for node_id in nodes:
      current_var_value = self._get_instantiation_value(var_id, node_id)
      if first_var_value != current_var_value:
        var_have_same_value = False
      if current_var_value == None:
        is_a_value_none = True

    var_info = {}
    var_info["id"] = var_id

    if var_have_same_value:
      var_info["same_in_all_nodes"] = True
      if first_var_value:
        var_info["value"] = first_var_value[var_id]
      else:
        var_info["value"] = None
    else:
      var_info["same_in_all_nodes"] = False
      var_info["value"] = None

      if is_a_value_none:
        return (False, var_info)

    return (True, var_info)

  def _get_instantiation_value(
          self,
          var_id: str,
          node_id: int
          ) -> Optional[float]:
    """Returns the instantiation value of a variable in a node.

    Args:
      var_id (str): Id of the variable.
      node_id (int): Id of the node.

    Returns:
      float: The stored value for the variable in the specified node or None
        if nothing have been stored yet.
    """
    # TODO Change to `var_id` when the int & str problem is fixed.
    if int(var_id.replace("V_", "")) not in self.main.ontology.variables:
      pass  # TODO Code behaviour when the variable file changed

    # node_id = str(node_id)  # TODO Remove when the int & str problem is fixed.
    values = {}
    vars = self.model_container["nodes"][node_id]["instantiated_variables"]
    if var_id not in vars:
      values = None
    else:
      values[var_id] = vars[var_id]

    return values
    # if node_id in values:
    #   if var_id in values[node_id]:
    #     return values[node_id][var_id]
    #
    # return None

  def _set_instantiation_value(
          self,
          var_id: str,
          var_value: Optional[float],
          node_id: int
          ) -> None:
    """Save the instantiation value of a variable in a node.

    Args:
        var_id (str): Id of the variable.
        var_value (Optional[float]): Value of the variable or None if
          no value has been assigned yet.
        node_id (int): Id of the node.
    """
    # TODO Remove when the int & str problem is fixed.
    node_id = str(node_id)
    nodes = self.model_container["instantiation_info"]["nodes"]
    if node_id not in nodes:
      nodes[node_id] = {}

    nodes[node_id][var_id] = var_value

  def _get_entity_name_from_node(self, node_id: str) -> entity.Entity:
    """Gets the entity associated to a node.

    Args:
        node_id (str): Id of the node.

    Returns:
        entity.Entity: Entity associated to the node.
    """
    entity_type = self.model_container["nodes"][node_id]["type"]
    entity_nw = self.model_container["nodes"][node_id]["network"]
    entity_class = self.model_container["nodes"][node_id]["class"]

    if entity_class in [NAMES["intraface"], NAMES["interface"]]:
      return None

    entity_domain = self._get_entity_domain(entity_nw)
    tokens = sorted(self.model_container["nodes"][node_id]["tokens"].keys())
    # if not tokens:
    #   return "no tokens defined"
    entity_variant = self.model_container["nodes"][node_id]["variant"]

    for t in tokens:
      ent_name = f"{entity_domain}.node.{t}|{entity_type}.{entity_variant}"
      if ent_name in self.all_entities:
        return ent_name
      else:
        return None

  def _get_entity_domain(self, entity_nw):
    nws = list(self.model_container.ontology.intra_domains.keys())
    for nw in nws:
      if entity_nw in self.model_container.ontology.intra_domains[nw]:
        entity_domain = self.model_container.ontology.intra_domains[nw][0]
    return entity_domain

  def _get_entity_name_from_arc(self, arc_id: str):

    arc = self.model_container["arcs"][arc_id]
    entity_mechanism = arc["mechanism"]
    entity_nature = arc["nature"]
    entity_nw = arc["network"]
    token = arc["token"]
    entity_variant = arc["variant"]
    entity_domain = self._get_entity_domain(entity_nw)
    ent_name = f"{entity_domain}.arc.{token}|{entity_mechanism}|{entity_nature}.{entity_variant}"
    if ent_name in self.all_entities:
      return ent_name
    else:
      return None

  # def __getEntityBehaviour(self, nodeID):
  #   selected_entity_behaviour = None
  #   entity_behaviours = self.model_container.ontology.entity_behaviours
  #   entity = self.model_container["nodes"][nodeID]["type"]
  #   entity_nw = self.model_container["nodes"][nodeID]["network"]

  #   entity_variant = self.model_container["nodes"][nodeID]["variant"]

  #   # print(entity_behaviours)
  #   #RULE: intra have no parameters -- hopefully
  #   if entity != "intra":
  #     nws = list(self.model_container.ontology.intra_domains.keys())
  #     for nw in nws:
  #       if entity_nw in self.model_container.ontology.intra_domains[nw]:
  #         entity_domain = self.model_container.ontology.intra_domains[nw][0]
  #     tokens = sorted(self.model_container["nodes"][nodeID]["tokens"].keys())
  #     entity_objects = []
  #     for t in tokens:
  #       # RULE: we pick the default version. For the time being there is no choice given
  #       entity_objects.append("%s.node.%s|%s.%s" % (entity_domain, entity, t, entity_variant))

  #     for obj in entity_objects:
  #       for ent in sorted(entity_behaviours.keys()):
  #         if obj in ent:
  #           print("found it", ent)
  #           # selected_entity_behaviour = entity_behaviours[ent]
  #           selected_entity_behaviour = ent
  #   # TODO Check if this was used somewhere else. Returning name of the entity instead of
  #   #      object for now
  #   return selected_entity_behaviour

  # ===================================================================
  def __setName(self, node, name):
    node_ID = self.current_ID_node_or_arc
    # if node.ID == 1:
    #   print("debugging")
    variant = self.model_container["nodes"][node.ID]["variant"]

    if name == CR.DEFAULT:
      name = "%s -- %s" % (str(node.ID), variant)
    for i in list(node.getItemList().keys()):
      if "name" == i:
        node.modifyComponentAppearance(i, ("setText", name))
        nodeID = node.ID
        try:
          # note: interface is not always up-to-date
          self.dialog.changeNodeName(nodeID, name)
        except:
          pass

  def __makeViewAndScene(self, nodeID):
    self.__setupScene(nodeID)
    self.__setupView(nodeID)
    self.__putEnvironment(nodeID)

  def __changeName(self, name):  # connected to c16_editName
    nodeID = self.current_ID_node_or_arc
    self.model_container["nodes"][nodeID]["name"] = name

    self.__redrawScene(self.currently_viewed_node)

  def __resetNodeStatesAndSelectedArc(self):
    self.arcSourceID = None
    for n in self.state_nodes:
      self.state_nodes[n] = STATES[self.editor_phase]["nodes"][0]
    for a in self.state_arcs:
      if self.state_arcs[a] == "selected":
        self.state_arcs[a] = STATES[self.editor_phase]["arcs"][0]
    self.resetGroups()
    self.clearSelectedNodes()
    self.selected_intraface_node = None

  def __reportEvent(self, state, next_state, action, item_type, event):
    """
    report mouse event in logging view
    @param state:      current state of automaton
    @param next_state: next state
    @param action:     action to be taken
    @param item_type:  item type
    @param event:      event
    """
    """
    """
    s = ("\n" + str(self.step) +
         "- state: " + state +
         "\t- next_state: " + next_state +
         "\n" + str(self.step) +
         "- object: " + item_type +
         "\t- event: " + event +
         "\n" + str(self.step) +
         "\t- action: " + action)
    self.main.logger.onUpdateStandardOutput(s)
    pass

  def __drawNode(self, x, y, ID, graphics_root_object, application):
    node = Node(ID, graphics_root_object, application,
                x, y, self.scene, self.view, self)
    if graphics_root_object == NAMES["node"]:  # only add to simple nodes
      if (graphics_root_object not in [INTRAFACE, INTERFACE]) or ():
        indicator = self.__makeIndicators(ID)
        print("draw node %s indicators %s " % (ID, indicator))
        for i in indicator:
          name = indicator[i]["name"]
          type = indicator[i]["type"]
          x = indicator[i]["position_x"]
          y = indicator[i]["position_y"]
          rgba_colour = indicator[i]["colour"]
          if type == NAMES["indicator token"]:
            node.addIndicatorDot(name, x, y, rgba_colour)
          else:
            node.addIndicatorText(name, x, y, indicator[i]["label"])

    # RULE: tool tip for root objects
    if graphics_root_object in [NAMES["node"], NAMES["reservoir"], NAMES["arc node"]]:
      # add tool tip
      data = self.model_container["nodes"][ID]
      s = "<nobr> <b> node: %s <b> </nobr><br/>" % ID
      for d in data:
        s += "<nobr> %s -- %s </nobr><br/>" % (d, data[d])
      # s = TOOLTIP_TEMPLATES["nodes"] % (
      #         data["network"],
      #         data["named_network"],
      #         data["type"],
      #         data["tokens"])
      # if "conversions" in data:
      #   s.join("<br>%s" % data["conversions"])
      # print("debugging -- tool tip:", s)
      node.setToolTip(s)

    if graphics_root_object == NAMES["intraface"]:
      # add tool tip
      data = self.model_container["nodes"][ID]
      s = "<nobr> <b> intraface: %s <b> </nobr><br/>" % ID
      for d in data:
        s += "<nobr> %s -- %s </nobr><br/>" % (d, data[d])
      # s = TOOLTIP_TEMPLATES["intraface"] % (data["network"],
      #                                       data["named_network"],
      #                                       data["type"],
      #                                       data["tokens_left"],
      #                                       data["tokens_right"]
      #                                       )

      node.setToolTip(s)

    self.scene.addItem(node)
    # Note: in a new model this is an integer 0
    name = str(self.model_container["nodes"][ID][NAMES["name"]])
    if name == None:
      print("debugging")
    if name == "0":  # NOTE: here we set the root's name
      name = self.main.model_name
      self.model_container["nodes"][ID][NAMES["name"]] = name
    self.__setName(node, name)
    return node

  def __drawArc(self, arcID, fromNode, toNode, arc_type):
    # if self.editor_phase == "token_topology":
    #   print("debugging -- draw arc")
    arc = Arc_Edge(arcID,
                   fromNode, toNode,
                   arc_type,
                   self.scene,
                   self.view,
                   self)

    data = self.model_container["arcs"][arcID]
    s = "<nobr> <b> arc: %s <b> </nobr><br/>" % arcID
    for d in data:
      s += "<nobr> %s -- %s </nobr><br/>" % (d, data[d])

    # s = TOOLTIP_TEMPLATES["arc"] % (data["network"],
    #                                 data["named_network"],
    #                                 data["mechanism"],
    #                                 data["nature"],
    #                                 data["token"],
    #                                 data["typed_tokens"],
    #                                 )
    arc.setToolTip(s)

    self.scene.addItem(arc)

    return

  def __setupView(self, nodeID):
    """
    set up a new view for node nodeID
    @param nodeID: node ID
    """

    del self.view

    v = self.main.ui.graphicsView
    scene = self.scene
    v.setScene(scene)
    v.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
    v.setRenderHint(QtGui.QPainter.Antialiasing)
    v.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
    v.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
    v.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
    self.view = v
    scene.update()
    self.view.update()

  def __putEnvironment(self, nodeID):
    """
    put the environment on node nodeID
    The graphical representation of the environment is generated every time it is not stored in the
    data file. Thus the location of the ancestors and siblings is autogenerated
    in contrast to the location of the child nodes. Their location is being stored in the model file.

    This will enable to re-size the view dynamically.

    @param nodeID: node ID
    """
    # for the generation of the environment get first the geometry from the base graphical data generator

    root_data = self.graphics_data.getData(self.editor_phase, NAMES["panel"],
                                           NAMES["root"], self.current_application, R.M_None)
    ancestors_panel_data = self.graphics_data.getData(self.editor_phase, NAMES["panel"],
                                                      NAMES["left panel"], self.current_application, R.M_None)
    width_anchestors_panel = ancestors_panel_data["width"]
    siblings_pannel_data = self.graphics_data.getData(self.editor_phase, NAMES["panel"],
                                                      NAMES["right panel"], self.current_application, R.M_None)
    width_siblings_panel = siblings_pannel_data["width"]

    # set size of panels
    width_view = self.main.ui.graphicsView.width()
    height_view = self.main.ui.graphicsView.height()

    x_view = self.view.rect().x()
    y_view = self.view.rect().y()

    x = x_view - width_view / 2 - 5  # transformation and adjustment for frame
    y = y_view - height_view / 2 - 5

    MARGIN_X = 0
    MARGIN_Y = 0

    w_root = width_view - width_anchestors_panel - width_siblings_panel - 2 * MARGIN_X
    x_root = x + width_anchestors_panel + MARGIN_X
    h_root = height_view - 2 * MARGIN_Y
    y_root = y + MARGIN_Y

    root_data["position_x"] = x_root
    root_data["position_y"] = y_root
    root_data["width"] = w_root
    root_data["height"] = h_root
    ancestors_panel_data["position_x"] = x
    ancestors_panel_data["position_y"] = y
    ancestors_panel_data["height"] = h_root
    siblings_pannel_data["position_x"] = x + width_view - width_siblings_panel
    siblings_pannel_data["position_y"] = y
    siblings_pannel_data["height"] = h_root
    self.view.offset = QtCore.QPoint(x, y)  # transformation of rubber band

    #  setup environment
    ancestors = self.model_container["ID_tree"].getAncestors(nodeID)
    siblings = self.model_container["ID_tree"].getSiblings(nodeID)

    if nodeID not in self.state_nodes:
      self.state_nodes[nodeID] = STATES[self.editor_phase]["nodes"][0]
    env = NodeView(nodeID, self)
    self.scene.addItem(env)

    dy_connector = LOCATION_PARAMETERS["connector_offset"]
    dy_ancestor = LOCATION_PARAMETERS["ancestor_offset"]
    dy_sibling = LOCATION_PARAMETERS["sibling_offset"]
    x_ancestors = x + width_anchestors_panel
    y_ancestors = - height_view / 2 + dy_ancestor
    self.__addAncestors(nodeID, ancestors, x_ancestors, y_ancestors)
    x_siblings = + width_view / 2 - width_siblings_panel
    y_siblings = - height_view / 2 + dy_sibling
    self.__addSiblings(nodeID, siblings, x_siblings, y_siblings)
    x_connector = 0
    y_connector = - height_view / 2 + dy_connector
    self.__drawNode(x_connector, y_connector, nodeID,
                    NAMES["connector"], self.current_application)

  def __addAncestors(self, nodeID, ancestors, x_o, y_o):
    counter = 0
    h = LOCATION_PARAMETERS["ancestor_spacing"]  # 50

    for i in reversed(ancestors):
      y = y_o + 25 + counter * h
      node = self.__drawNode(
              x_o, y, i, NAMES["parent"], self.current_application)

      data = self.model_container["nodes"][i]
      s = TOOLTIP_TEMPLATES["ancestor"] % data["name"]
      node.setToolTip(s)
      counter = counter + 1

  def __addSiblings(self, nodeID, siblings, x_o, y_o):
    counter = 0

    h = LOCATION_PARAMETERS["sibling_spacing"]  # h = 50
    for i in siblings:
      y = y_o + 25 + counter * h
      node = self.__drawNode(
              x_o, y, i, NAMES["sibling"], self.current_application)
      data = self.model_container["nodes"][i]
      s = TOOLTIP_TEMPLATES["sibling"] % data["name"]
      node.setToolTip(s)
      counter = counter + 1
      counter = counter + 1

  def __setupScene(self, nodeID):
    """
    set up a scene for node nodeID
    @param nodeID: node ID
    """

    del self.scene

    scene_width = self.main.ui.graphicsView.width()
    scene_height = self.main.ui.graphicsView.height()

    adjust = 10
    scene = QtWidgets.QGraphicsScene(self.main)  # tie on to main widget
    # TODO check which one works better
    scene.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
    scene.setItemIndexMethod(QtWidgets.QGraphicsScene.BspTreeIndex)
    scene.setSceneRect(float(-scene_width / 2.0), -float(scene_height / 2.0),
                       float(scene_width - adjust), float(scene_height - adjust))
    self.scene = scene

  def __delScene(self, nodeID):
    """
    delete a scene
    @param nodeID: node ID
    """
    self.scene = None
    pass

  def __getObjectFromScene(self, scene_object, sceneID, OID):
    # for O in self.scenes[sceneID].items():
    for O in self.scene.items():
      StrO = str(O.__class__)
      t = StrO.split(".")[-1]  # get last bit
      tt = t.split("'")[0]  # remove '>
      if scene_object == tt:
        if O.ID == OID:
          return O
    return None

  def __makeIndicators(self, ID):
    indicator = OrderedDict()
    tokens = self.model_container.getTokensInNode(ID)
    if not tokens:
      return indicator

    pos = {}
    x_ = LOCATION_PARAMETERS["token_indicators"]["x"]
    y_ = LOCATION_PARAMETERS["token_indicators"]["y"]
    dx = LOCATION_PARAMETERS["token_indicators"]["dx"]
    dy = LOCATION_PARAMETERS["token_indicators"]["dy"]

    for token in tokens:
      pos[token] = (x_, y_)
      x_ = x_ + dx
      y_ = y_ + dy

    # print("make indicators ", self.main.typedTokens[self.main.current_network])
    for token in self.model_container["nodes"][ID]["tokens"]:
      # RULE: interface tokens are not shown
      if token in self.main.ontology.tokens:

        name = token
        # NOTE: if you get an error here then you need to add a token colour above
        colour = self.main.TOKENS[token]['colour']  # rgba_colour[token]
        x, y = pos[token]
        # print("set tokens token %s, x: %s, y: %s" % (token, x, y))
        indicator[name] = {
                "name"      : name,
                "position_x": x,
                "position_y": y,
                "colour"    : colour,
                "type"      : NAMES["indicator token"]
                }

        typed_tokens = self.model_container["nodes"][ID]["tokens"][token]
        y_t = copy.copy(y) - 25
        for typed_token in typed_tokens:
          name = "%s-%s" % (token, typed_token)
          colour = self.main.TOKENS[token]['colour']
          y_t = y_t - 15
          indicator[name] = {
                  "name"      : name,
                  "position_x": x - 10,
                  "position_y": y_t,
                  "colour"    : colour,
                  "type"      : NAMES["indicator typed token"],
                  "label"     : typed_token
                  }
          pass

    # print("indicator definition:", indicator)
    return indicator

  def __redrawScene(self, nodeID, debug=False):
    """
    redraw a scene
    @param nodeID: node ID
    """

    # print("begin redraw scene")
    self.currently_viewed_node = nodeID
    self.applyControlAccessRules()
    self.__makeViewAndScene(nodeID)

    if debug:
      print("start redraw node ", nodeID)

    # check for missing arcs
    missing_input_arc, missing_output_arc = self.model_container.checkforMissingBoundaryArcs()

    children = self.model_container["ID_tree"].getChildren(nodeID)

    # self.state_nodes[2]= "selected"
    # nodes
    for child in children:
      graph_object_class = self.model_container["nodes"][child]["class"]
      application = self.model_container["nodes"][child]["type"]
      self.__drawNode(0, 0, child, graph_object_class, application)

    # arcs
    arcs_on_scene = list(self.model_container["scenes"][nodeID]["arcs"].keys())
    for arcID in arcs_on_scene:
      if arcID not in self.state_arcs:
        self.state_arcs[arcID] = STATES[self.editor_phase]["arcs"][0]

      fromNodeID = self.model_container["arcs"][arcID]["source"]
      toNodeID = self.model_container["arcs"][arcID]["sink"]
      nodes_IDs = self.model_container["ID_tree"].getNodes()

      if fromNodeID not in nodes_IDs:
        self.state_arcs[arcID] = "open"
      else:
        if self.model_container["ID_tree"].getChildren(fromNodeID) != []:
          self.state_arcs[arcID] = "open"
      if toNodeID not in nodes_IDs:
        self.state_arcs[arcID] = "open"
      else:
        if self.model_container["ID_tree"].getChildren(toNodeID) != []:
          self.state_arcs[arcID] = "open"

      subarc = self.model_container.getArcOnNodeScene(arcID)
      sourceID, sinkID = subarc[nodeID]
      fromNode = self.__getObjectFromScene("Node", nodeID, sourceID)
      toNode = self.__getObjectFromScene("Node", nodeID, sinkID)

      arc_type = NAMES["connection"]
      if self.model_container["nodes"][sourceID]["class"] in [NAMES["arc node"],
                                                              NAMES["intraface"],
                                                              NAMES["interface"]]:
        arc_type = NAMES["right arc"]
      if self.model_container["nodes"][sinkID]["class"] in [NAMES["arc node"],
                                                            NAMES["intraface"],
                                                            NAMES["interface"]]:
        arc_type = NAMES["left arc"]

      no_knots = len(self.model_container["scenes"][nodeID]["arcs"][arcID])
      if no_knots != 0:
        last_knot = None
        fNode = fromNode
        for k in range(no_knots):
          (x, y) = self.model_container["scenes"][nodeID]["arcs"][arcID][k]
          knot = Knot(k, arcID, x, y, self.scene, self.view, self)
          data = self.model_container["arcs"][arcID]
          s = '<b> %s - %s <b><br>%s <br>%s <br>%s - %s ' % (data["network"],
                                                             data["named_network"],
                                                             data["mechanism"],
                                                             data["nature"],
                                                             data["token"],
                                                             data["typed_tokens"],
                                                             )
          knot.setToolTip(s)

          # collision check for knots only
          for i in self.scene.items():
            if (knot.collidesWithItem(i)):
              # print("collision:", i.graphics_root_object)
              if i.graphics_root_object in [NAMES["intraface"],
                                            NAMES["interface"],
                                            NAMES["branch"],
                                            NAMES["node"],
                                            NAMES["elbow"],
                                            NAMES["connector"],
                                            NAMES["left arc"],
                                            NAMES["right arc"],
                                            ]:
                print("collision execute avoidance:", i.graphics_root_object)
                x_ = knot.x()
                y_ = knot.y()
                width = knot.boundingRect().width()
                x = x_ + width
                y = y_ + width
                knot.setY(y)
                knot.setX(x)

                self.model_container.updateKnotPosition(self.currently_viewed_node, arcID,
                                                        k,
                                                        x, y)

          self.scene.addItem(knot)
          if k > 0:
            fNode = last_knot
          tNode = knot
          self.__drawArc(arcID, fNode, tNode, arc_type)
          last_knot = knot
        self.__drawArc(arcID, last_knot, toNode, arc_type)

      else:
        self.__drawArc(arcID, fromNode, toNode, arc_type)

  def __ruleNodeAccessTopologyAcrossNetworks(self):
    viewed_node = self.currently_viewed_node

    children = self.model_container["ID_tree"].getChildren(viewed_node)

    for child in children:  # set the default when not defined
      if child not in self.state_nodes:
        self.state_nodes[child] = STATES[self.editor_phase]["nodes"][
          0]  # RULE: the first in the list is the default usually "enabled"  # default is enabled

    self.clearBlockedNodes()

    # RULE: Boundary -> only one connection per token for the respective network

    for node in children:
      # network_node = self.model_container["nodes"][node][NAMES["network"]]
      node_class = self.model_container["nodes"][node]["class"]
      if node_class == NAMES["intraface"]:
        pass
        # arcs_connected_to_node = self.model_container.getArcsConnectedToNode(
        #     node)
        # # print("intraface %s , connected arcs %s -- token %s" % (node, arcs_connected_to_node, token))
        #
        # # if token is in the intraface - allow for only two connections
        #
        # if self.state_nodes[node] == "selected":
        #   return  # when connecting it comes through here twice so this is the second time
        #
        # intraface_node = self.model_container["nodes"][node][NAMES["network"]]
        # try:
        #   network_left, network_right = intraface_node.split(
        #       CR.CONNECTION_NETWORK_SEPARATOR)  # NETWORK_SEPARATOR)
        # except:
        #   network_left = intraface_node
        #   network_right = network_left
        # # network_tokens_left = self.main.tokens_on_networks[network_left]["type"]
        # tokens = set()
        # left = set(self.model_container["nodes"][node]["tokens_left"].keys())
        # right = set(self.model_container["nodes"][node]["tokens_right"].keys())
        # tokens = left.union(right)
        #
        # # are there existing connections ?
        # arc_IDs = list(self.model_container["arcs"].keys())
        # mech_left = self.main.selected_transfer_mechanism[network_left]
        # mech_right = self.main.selected_transfer_mechanism[network_right]
        # if arc_IDs:
        #   for arc in arc_IDs:
        #     mechanism = self.model_container["arcs"][arc]["mechanism"]
        #   if mech_left != mech_right:
        #     # error is handled in adding the arcs when going through an intraface
        #     # print(">>>>>>>>>>>>>>>>> error -- the two mechanisms must be the same" ,"mechanisms left and right:",
        #     # mech_left, mech_right)
        #     pass
        #   else:
        #     if self.main.selected_token[self.main.editor_phase][network_left] in tokens:
        #       if mech_left != mechanism:
        #         self.state_nodes[node] = "enabled"
        #       else:
        #         self.state_nodes[node] = "blocked"
        #     else:
        #       self.state_nodes[node] = "enabled"

  def __ruleNodeAccessInNetworkOnly(self):
    # str(self.model_container[
    nodeID = (self.model_container["arcs"]
    [self.selected_arcID][self.end_to_move])
    # "arcs"][self.selected_arcID][self.end_to_move]) #HAP:str --> int

    source_network = self.model_container["nodes"][nodeID][NAMES["network"]]
    children = self.model_container["ID_tree"].getChildren(
            self.currently_viewed_node)

    for child in children:
      network = self.model_container["nodes"][child][NAMES["network"]]
      if self.state_nodes[child] != "selected":
        if network != source_network:
          self.state_nodes[child] = "blocked"
        else:
          self.state_nodes[child] = "enabled"  # default is enabled

  def __ruleNodeAccessTypedTokensInject(self):
    # print("debugging -- token control inject rule")

    #
    # RULE: only constant systems can receive tokens in a given network
    # RULE: do not block the selected nodes but only if token is in present
    # SOMETHING IS FISHY here

    children = self.model_container["ID_tree"].getChildren(
            self.currently_viewed_node)
    tokens = self.main.tokens_on_networks[self.main.current_network]
    for child in children:  # set the default (initialisation, import etc.)
      if child not in self.state_nodes:
        self.state_nodes[child] = "blocked"  # default is blocked
    for node in children:
      self.__enableNodeOnRule(node, "nodes_allowing_token_injection")

  def __ruleNodeAccessTypedTokensConvert(self):
    # RULE: only simple nodes in a given network
    # RULE: do not block the selected nodes

    children = self.model_container["ID_tree"].getChildren(
            self.currently_viewed_node)

    for node in children:
      self.__enableNodeOnRule(node, "nodes_allowing_token_conversion")

  def __enableNodeOnRule(self, node, rule):
    self.state_nodes[node] = "blocked"  # default is blocked
    network = self.model_container["nodes"][node]["network"]
    if network == self.main.current_network:
      node_data = self.model_container["nodes"][node]
      node_type = node_data["type"]
      if NODE_COMPONENT_SEPARATOR in node_type:
        l = node_type.split(NODE_COMPONENT_SEPARATOR)
        if len(l) == 2:
          [node_component, app] = l
        elif len(l) == 3:
          [token, mechanism, nature] = l  # Note: this is an arc node
          self.state_nodes[node] = "blocked"
          return
      else:
        node_component = node_type
      if node_component in self.main.ontology.rules[rule]:
        self.state_nodes[node] = "enabled"

  def __ruleNodeAccessTypedTokensConstrain(self):
    #
    # RULE: transfer constraints - only for boundaries with equal token on either side
    # RULE: do not block the selected nodes

    children = self.model_container["ID_tree"].getChildren(
            self.currently_viewed_node)

    # for child in children:  # set the default (initialisation, import etc.)
    #   if child not in self.state_nodes:
    #     self.state_nodes[child] = "blocked"  # default is blocked

    for node in children:
      if self.state_nodes[node] != "selected":
        self.state_nodes[node] = "blocked"
        # TODO:  token is the key -- must only
        if NAMES["intraface"] == self.model_container["nodes"][node]["class"]:
          #  be one

          if (self.model_container["nodes"][node]["tokens_left"].keys() ==
              self.model_container["nodes"][node]["tokens_right"].keys()) or \
                  (self.main.selected_token[self.main.editor_phase][self.main.current_network] in
                   self.model_container["nodes"][node]["tokens_left"].keys()):
            self.state_nodes[node] = "enabled"
    pass

  def __ruleNodeAccessUndetermined(self):
    #
    # RULE: if the state is not known, then everything is blocked

    children = self.model_container["ID_tree"].getChildren(
            self.currently_viewed_node)

    for node in children:
      self.state_nodes[node] = "blocked"
    pass

  def __clearNodes(self, fromwhat):
    children = self.model_container["ID_tree"].getChildren(
            self.currently_viewed_node)

    for node in children:
      if self.state_nodes[node] == fromwhat:
        # "enabled"
        self.state_nodes[node] = STATES[self.main.current_network]["nodes"][0]

  def resetGroups(self):
    self.node_group = set()
    self.knot_group = set()
    # self.__checkNodeGroup()

  def setDefaultEditorState(self):
    # RULE: first state in the list is default
    self.editor_state = GRAPH_EDITOR_STATES[self.editor_phase][0]
    for event in self.key_automata[self.editor_phase]:
      if self.editor_state == self.key_automata[self.editor_phase][event]["state"]:
        self.main.setKeyAutomatonState(event)
        break

  # RULE: the first in the list is the default usually "enabled"  # default is enabled
  def resetNodeStates(self):
    # viewed_node = self.currently_viewed_node
    # children = self.model_container["ID_tree"].getChildren(viewed_node)
    # for child in children:  # set the default (initialisation, import etc.)
    #   self.state_nodes[child] = STATES[self.editor_phase]["nodes"][0]
    # return

    nodes = self.model_container["ID_tree"].getNodes()
    for node in nodes:  # set the default (initialisation, import etc.)
      self.state_nodes[node] = STATES[self.editor_phase]["nodes"][0]
    return

  def applyNodeDefinitionRules(self, nodetype):

    features = set()
    for rule in list(self.main.ontology.rules.keys()):
      if rule == "nodes_allowing_token_injection":
        if nodetype in self.main.ontology.rules[rule]:
          features.add("has_tokens")
          features.add("accepts_inject_of_typed_tokens")
      if rule == "nodes_allowing_token_conversion":
        if nodetype in self.main.ontology.rules[rule]:
          features.add("has_tokens")
          features.add("has_conversion")
      if rule == "nodes_allowing_token_transfer":
        if nodetype in self.main.ontology.rules[rule]:
          features.add("has_tokens")
          # features.add(NAMES["intraface"])

    return sorted(features)

  def applyControlAccessRules(self):
    phase = self.editor_phase
    state = self.editor_state
    # network = self.main.current_network
    # named_network = self.main.current_named_network

    # print("debugging -- access rules editor phase & state :", phase, state)
    # print("debugging -- access rules editor network & named network :", network, named_network)

    # token_control = self.main.control_tools.index
    # typed_token_control = self.main.control_typed_tokens.index

    if phase == EDITOR_PHASES[0]:
      if state == "re-connect_arc":
        self.__ruleNodeAccessInNetworkOnly()
      # elif state == "insert":
      #   return
      else:
        self.__ruleNodeAccessTopologyAcrossNetworks()
    elif phase == EDITOR_PHASES[1]:
      select = self.main.state_inject_or_constrain_or_convert
      if select == "inject":
        self.__ruleNodeAccessTypedTokensInject()
      elif select == "convert":
        self.__ruleNodeAccessTypedTokensConvert()
      elif select == "constrain":
        self.__ruleNodeAccessTypedTokensConstrain()
      else:
        self.__ruleNodeAccessUndetermined()

  def redrawCurrentScene(self):
    # print("redraw scene initialising", self.initialising)
    if self.main.initialising:
      return
    # if "currently_viewed_node" not in dir(self):
    #   return
    self.__redrawScene(self.currently_viewed_node)

  def clearBlockedNodes(self):
    self.__clearNodes("blocked")

  def clearSelectedNodes(self):
    self.__clearNodes("selected")

  def blockNodesInNetworkInViewedNode(self, network):
    for node in self.model_container["scenes"]:
      if network == self.model_container["nodes"]:
        self.state_nodes[node] = "blocked"

  def setPanelAsCurrentItem(self):
    self.current_item = None
    for i in self.scene.items():
      if (i.graphics_root_object == NAMES["panel"]):
        if "decoration" in dir(i):
          if (i.decoration == NAMES["root"]):
            self.current_item = i
            # print("----- setting current item to panel")
    return self.current_item
