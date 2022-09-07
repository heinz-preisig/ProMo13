#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Base (foundation) ontology editor
===============================================================================

This editor generates the domain tree with two branches in each node:
- structure settling structural components of the model representation also serving as the basis for the bookkeeping
- behaviour defining the variable classes
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2019. 01. 04"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "7.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# TODO: handle differential indices differently states and frames generate a differential space automatically ! danger !

import os as OS
from collections import OrderedDict
from copy import copy
from copy import deepcopy
from distutils.dir_util import copy_tree

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.common_resources import getData
from Common.common_resources import getOntologyName
# from Common.common_resources import globalEquationID # NOTE: removed for the time being. IDs are now local to ontology
# from Common.common_resources import globalVariableID # NOTE: removed for the time being. IDs are now local to ontology
from Common.common_resources import makeTreeView
from Common.common_resources import putData
from Common.common_resources import putDataOrdered
from Common.common_resources import saveBackupFile
from Common.pop_up_message_box import makeMessageBox
from Common.radio_selector_impl import RadioSelector
from Common.record_definitions import OntologyContainerFile
from Common.record_definitions import RecordProMoIRI
from Common.record_definitions import VariableFile
from Common.resource_initialisation import checkAndFixResources
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.resource_initialisation import ONTOLOGY_VERSION
from Common.resource_initialisation import VARIABLE_EQUATIONS_VERSION
from Common.resources_icons import getIcon
from Common.resources_icons import roundButton
from Common.ui_string_dialog_impl import UI_String
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.OntologyFoundationEditor.editor_foundation_ontology_gui import Ui_MainWindow
from OntologyBuilder.OntologyFoundationEditor.onto_graph_creator import makeOntologyDotGraph


# RULE: defining the tree structure, and its components
class Behaviour(OrderedDict):
  def __init__(self):
    super().__init__()
    self["graph"] = []
    self["node"] = []
    self["arc"] = []


class Structure(OrderedDict):
  def __init__(self):
    super().__init__()
    self["node"] = OrderedDict()
    self["arc"] = OrderedDict()
    self["token"] = OrderedDict()

  def addArc(self, token):
    self["arc"][token] = {}  # hash -- mechanism  & value nature (distributed, lumped)


class Ontology(OrderedDict):

  def __init__(self, name=None, type='intra', parent_ontology=None):
    super().__init__()
    self["name"] = name  # string
    self["type"] = type  # string
    if parent_ontology == None:
      self["structure"] = Structure()
      self["behaviour"] = Behaviour()
      self["parents"] = []
    else:  # first one -- the root of the tree
      self["structure"] = deepcopy(parent_ontology["structure"])  # inherit down the branch
      self["behaviour"] = deepcopy(parent_ontology["behaviour"])  # inherit down the branch
      a = [parent_ontology["name"]]
      b = copy(parent_ontology["parents"])
      a.extend(b)
      self["parents"] = a

    self["children"] = []  # ontologies

  def addChild(self, child):
    self["children"].append(child)  # ontologies

  def importOntologyNode(self, node):
    for i in node:
      self[i] = deepcopy(node[i])


def askForString(prompt, placeholdertext="", limiting_list=[]):  #
  ui_ask = UI_String(prompt, placeholdertext=placeholdertext, limiting_list=limiting_list)
  ui_ask.exec_()
  model_name = ui_ask.getText()
  return model_name


# =====================================================================================================================

class UI_EditorFoundationOntology(QtWidgets.QMainWindow):

  # potential_issues : Note : is the order important. Adding a network does leave us unordered compared to the old
  #  approach....???

  def __init__(self):
    QtWidgets.QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    roundButton(self.ui.pushInfo, "info", tooltip="information")
    roundButton(self.ui.pushGraph, "dot_graph", tooltip="make ProMo ontology graphs")
    roundButton(self.ui.pushSave, "save", tooltip="save ProMo base ontology")

    ontology_name, ontologies = getOntologyName(new=True, task="task_ontology_foundation", left_icon="new")

    self.ontology = OntologyContainerFile(ONTOLOGY_VERSION)
    self.ontology_tree = self.ontology["ontology_tree"]
    self.root = "root"  # RULE: root of tree is called "root"
    self.lock_delete = False
    self.saved_ontology = False
    new_variable_file = False

    if not ontology_name:  # RULE: No ontology chosen -- ask for new ontology
      ui_ask = UI_String("give new ontology name ", "ontology name", limiting_list=ontologies)
      ui_ask.exec_()
      ontology_name = ui_ask.getText()
      if not ontology_name:  # RULE: no new ontology -- exit
        OS._exit(-1)

      # RULE: make new infrastructure for new ontology
      self.ontology_dir = DIRECTORIES["ontology_location"] % ontology_name
      checkAndFixResources(ontology_name)  # TODO : can be extended when needed

      try:
        self.logo.close()
      except:
        pass

      self.__createRoot()
      self.ontology_dir = DIRECTORIES["ontology_location"] % ontology_name
      self.__writeMessage("make directory tree %s" % self.ontology_dir)
      src = DIRECTORIES["new_ontology_starting_set"]
      copy_tree(src, self.ontology_dir)
      self.ontology_file = FILES["ontology_file"] % ontology_name
      # self.__makeOntology()

    else:  # edit
      self.ontology_file = FILES["ontology_file"] % ontology_name

      # RULE: if variable file exists then delete & rename is to be blocked
      variable_file = FILES["variables_file"] % ontology_name

      self.new_variable_file = False
      if OS.path.exists(variable_file):
        # print("debugging -- found equation file", variable_file)
        # reply = QtWidgets.QMessageBox.question(self, "choose",
        #                                        "There is a variable file \n -- do you want to delete it and restart "
        #                                        "the whole process?",
        #                                        NO, YES )
        reply = makeMessageBox("There is a variable file \n -- do you want to delete it and restart "
                               "the whole process?", ["NO", "YES"])
        if reply == "YES":
          self.lock_delete = False
          old, new, next = saveBackupFile(variable_file)
          self.__writeMessage("variable file has been renamed from %s to %s" % (old, new))
          self.new_variable_file = True
        else:
          self.lock_delete = True

      else:
        self.__writeMessage("did not find equation file %s" % variable_file)
        self.lock_delete = False
        self.new_variable_file = True

    self.__makeOntology()

    # setup rules for index generation
    if "network_enable_adding_indices" not in self.ontology["rules"]:
      self.ontology["rules"]["network_enable_adding_indices"] = {}
    for nw in sorted(self.ontology_tree.keys()):
      if nw not in self.ontology["rules"]["network_enable_adding_indices"]:
        self.ontology["rules"]["network_enable_adding_indices"][nw] = False

    self.ontology_name = ontology_name

    # lock_file = FILES["lock_file"] % ontology_name  # TODO: one could do without the lock file -- check
    # if self.lock_delete:
    #   f = open(lock_file, "w")
    #   f.write("update index files")
    #   f.close()

    # else:
    #   if OS.path.exists(lock_file):
    #     OS.remove(lock_file)

    ### initialisations  ===========
    self.current_network = None
    self.current_structure_component = None
    self.current_behaviour_component = None
    self.current_behaviour_variable = None
    self.current_structure_variable = None
    self.current_structure_extension_variable = None
    self.current_arc_token = None

    self.branches = ["structure", "behaviour"]
    self.branch = self.branches[self.ui.tabWidget.currentIndex()]
    #
    # actions for state entry
    self.__automaton()

    #  silly problem with single click and double click on listView widget
    self.click_count = 1
    self.clickTimer = QtCore.QTimer()

    # icons for buttons
    plus_icon = getIcon("+")
    minus_icon = getIcon("-")
    self.ui.pushNewStructureElement.setIcon(plus_icon)
    self.ui.pushNewBehaviourElement.setIcon(plus_icon)
    self.ui.pushNewStructureElementExtension.setIcon(plus_icon)
    self.ui.pushDeleteStructureElement.setIcon(minus_icon)
    self.ui.pushDeleteBehaviourElement.setIcon(minus_icon)
    self.ui.pushDeleteStructureElementExtension.setIcon(minus_icon)

    # sizing of buttons
    size = self.ui.pushNewStructureElement.sizeHint()
    self.ui.pushNewStructureElement.resize(size)

    self.radio = {
            "structure_node" : None,
            "structure_arc"  : None,
            "structure_token": None,
            "behaviour_graph": None,
            "behaviour_node" : None,
            "behaviour_arc"  : None
            }

    # starting up ===============
    # self.__makeTreeView()

    self.tree_items = makeTreeView(self.ui.treeWidget, self.ontology_tree)
    self.__indexVariableClasses()
    self.__ui_status("start")
    if self.new_variable_file:
      self.__ui_status("new_variable_file")

  def __makeOntology(self):
    if OS.path.exists(self.ontology_file):
      raw_ontology_container = getData(self.ontology_file)  # from json file
      for key in raw_ontology_container:
        if key == "ontology_tree":
          raw_ontology = raw_ontology_container["ontology_tree"]  # this needs to be "massaged"
        else:
          self.ontology[key] = raw_ontology_container[key]  # just copy - do not touch

      for o in raw_ontology:
        self.ontology_tree[o] = Ontology()
        self.ontology_tree[o].importOntologyNode(raw_ontology[o])


    else:
      self.__createRoot()
    self.__writeMessage("preparing ontology")

    self.__addFixedRules()  # RULE: here we add the rule system for the time being

  def __automaton(self):
    """
    Sets the hidden/show for the various GUI items -- thus enables selective control of the interface.
    what is in the lists is hidden -- everything else is shown.
    :return:
    """
    ui = self.ui
    actions = {  #
            "0"                                : [  #
                    ui.groupBoxFile,
                    ui.pushSave,
                    ui.treeWidget,
                    ui.tabWidget,
                    ui.groupBoxNetwork,
                    ui.radioButtonInter,
                    ui.radioButtonIntra,
                    ui.pushAddChild,
                    ui.pushRemoveChild,
                    ui.groupBoxStructureComponents,
                    ui.groupBoxBehaviourComponents,
                    ui.listViewStructure,
                    ui.listViewStructureExtension,
                    ui.listViewBehaviour,
                    ui.pushNewBehaviourElement,
                    ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    ui.radioButtonHasPortVariables,
                    ui.radioButtonIsEnableAddingIndex,
                    ],
            "start"                            : [  #
                    ui.groupBoxFile,
                    ui.pushSave,
                    ui.tabWidget,
                    ui.groupBoxNetwork,
                    ui.radioButtonHasPortVariables,
                    ui.radioButtonIsEnableAddingIndex,
                    ],
            "new_variable_file"                : [
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    ui.tabWidget,
                    ui.groupBoxNetwork,
                    # ui.radioButtonHasPortVariables,
                    ],
            "removed_branch"                   : [  #
                    ui.tabWidget,
                    ui.groupBoxNetwork,
                    # ui.radioButtonHasPortVariables,
                    ],
            "network_selected"                 : [  #
                    ui.listViewStructure,
                    ui.listViewStructureExtension,
                    ui.listViewBehaviour,
                    ui.pushNewBehaviourElement,
                    ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    ui.radioButtonHasPortVariables,
                    # ui.radioButtonIsEnableAddingIndex,
                    ],
            "network_selected_no_tokens"       : [  #
                    ui.listViewStructure,
                    ui.listViewStructureExtension,
                    ui.listViewBehaviour,
                    ui.radioButtonStructureArc,
                    ui.pushNewBehaviourElement,
                    ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "add_child_selected"               : [  #
                    ui.groupBoxNetwork,
                    ui.tabWidget,
                    ui.radioButtonHasPortVariables,
                    ],
            "block_delete"                     : [  #
                    ui.pushRemoveChild,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_selected"               : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.tabWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupBoxStructureComponents,
                    ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    ui.listViewBehaviour,
                    ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    # ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    ui.radioButtonHasPortVariables,
                    ui.radioButtonIsEnableAddingIndex,
                    ],
            "behaviour_selected"               : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.tabWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    # ui.pushDeleteBehaviourElement,
                    # ui.widgetToken,
                    ui.radioButtonHasPortVariables,
                    ui.radioButtonIsEnableAddingIndex,
                    ],
            "structure_node_selected"          : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_token_selected"         : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_node_prop_selected"     : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    # ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_token_prop_selected"    : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_node_prop_ext_selected" : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    # ui.pushDeleteStructureElementExtension,
                    # ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_token_prop_ext_selected": [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    # ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_arc_selected"           : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    # ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_arc_token_selected"     : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    # ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_arc_token_prop_selected": [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    # ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "structure_arc_prop_ext_selected"  : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    ui.listViewBehaviour,
                    ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    # ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    # ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "behaviour_component_selected"     : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    ui.radioButtonHasPortVariables,
                    ui.radioButtonIsEnableAddingIndex,
                    ],
            "behaviour_prop_selected"          : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    # ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    ui.radioButtonHasPortVariables,
                    ui.radioButtonIsEnableAddingIndex,
                    ],
            "behaviour_prop_selected_node"     : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupChildDefine,
                    # ui.groupBoxStructure,
                    # ui.groupBoxBehaviour,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    ui.pushNewStructureElementExtension,
                    ui.pushDeleteStructureElement,
                    ui.pushDeleteStructureElementExtension,
                    # ui.pushDeleteBehaviourElement,
                    ui.widgetToken,
                    # ui.radioButtonHasPortVariables,
                    ],
            "saved"                            : [  #
                    # ui.groupBoxFile,
                    # ui.pushSave,
                    # ui.treeWidget,
                    ui.tabWidget,
                    # ui.groupBoxNetwork,
                    # ui.radioButtonInter,
                    # ui.radioButtonIntra,
                    # ui.pushAddChild,
                    # ui.pushRemoveChild,
                    # ui.groupBoxStructureComponents,
                    # ui.groupBoxBehaviourComponents,
                    # ui.listViewStructure,
                    # ui.listViewStructureExtension,
                    # ui.listViewBehaviour,
                    # ui.pushNewBehaviourElement,
                    # ui.pushNewStructureElement,
                    # ui.pushNewStructureElementExtension,
                    # ui.pushDeleteStructureElement,
                    # ui.pushDeleteStructureElementExtension,
                    # ui.pushDeleteBehaviourElement,
                    # ui.widgetToken,
                    ui.radioButtonHasPortVariables,
                    ui.radioButtonIsEnableAddingIndex,
                    ],
            }
    self.actions = actions
    self.labels = {
            "0"                              : {
                    "structure": "",
                    "extension": ""
                    },
            "start"                          : {
                    "structure": "",
                    "extension": ""
                    },
            "structure_node_selected"        : {
                    "structure": "dynamics",
                    "extension": "distribution nature"
                    },
            "structure_token_selected"       : {
                    "structure": "token",
                    "extension": "refinement"
                    },
            "structure_arc_selected"         : {
                    "structure": "mechanism",
                    "extension": "nature"
                    },
            "structure_arc_token_selected"   : {
                    "structure": "mechanism",
                    "extension": "nature"
                    },
            "structure_arc_prop_ext_selected": {
                    "structure": "mechanism",
                    "extension": "nature"
                    },
            }

  def __createRoot(self):

    model_name = "root"
    self.current_network = model_name
    self.__writeMessage("create root: %s" % model_name)
    self.ontology_tree[model_name] = Ontology(model_name, None, None)

  def __makeTreeDepthFirstList(self, branch_root, nodes):

    if branch_root not in nodes:
      nodes.append(branch_root)
    if self.ontology_tree[branch_root]["children"] != []:
      for child in self.ontology_tree[branch_root]["children"]:
        self.__makeTreeDepthFirstList(child, nodes)  ###ooops cannot be nodes=nodes !!!
    else:
      return nodes

    return nodes

  # def __makeTreeView(self):
  #   self.ui.treeWidget.clear()
  #   self.tree_items = {}
  #   networks = list(self.ontology_tree.keys())
  #   root = self.root
  #   self.tree_items[root] = self.__addItemToTreeWidget(None, root)
  #   self.tree_items[root].name = self.ontology_tree[root]["name"]
  #   for nw in networks:
  #     if nw != root:
  #       parent = root
  #       child = self.ontology_tree[nw]["name"]
  #       nodes = []
  #       [nodes.append(n) for n in self.ontology_tree[nw]["parents"][::-1]]
  #       nodes.append(child)
  #       for child in nodes:
  #         if child in self.tree_items:
  #           parent = child
  #         else:
  #           parent_item = self.tree_items[parent]
  #           self.tree_items[child] = self.__addItemToTreeWidget(parent_item, child)
  #           self.tree_items[child].name = self.ontology_tree[child]["name"]
  #           parent = child
  #
  #   self.ui.treeWidget.expandAll()
  #   return

  def __indexVariableClasses(self):
    self.variables = OrderedDict()

    treeDpethFirstList = self.__makeTreeDepthFirstList(self.root, [])

    if not treeDpethFirstList:
      return

    for nw in treeDpethFirstList:
      self.variables[nw] = []
      for branch in ["structure", "behaviour"]:
        for component in self.ontology_tree[nw][branch]:
          if branch == "structure":
            if component == "arc":
              for token in self.ontology_tree[nw][branch][component]:
                for variable in self.ontology_tree[nw][branch][component][token]:
                  v = "%s-%s-%s-%s" % (branch, component, token, variable)
                  self.variables[nw].append(v)
                  for mechanism in self.ontology_tree[nw][branch][component][token][variable]:
                    v = "%s-%s-%s-%s-%s" % (branch, component, token, variable, mechanism)
                    self.variables[nw].append(v)
            else:
              for variable in self.ontology_tree[nw][branch][component]:
                v = "%s-%s-%s" % (branch, component, variable)
                self.variables[nw].append(v)
                for extension in self.ontology_tree[nw][branch][component][variable]:
                  v = "%s-%s-%s-%s" % (branch, component, variable, extension)
                  self.variables[nw].append(v)
          else:
            for component_ in self.ontology_tree[nw][branch]:
              for variable in self.ontology_tree[nw][branch][component_]:
                v = "%s-%s-%s" % (branch, component_, variable)
                self.variables[nw].append(v)

  # def __addItemToTreeWidget(self, parent, nodeID):
  #
  #   name = str(nodeID)
  #   item = QtGui.QTreeWidgetItem(parent, None)
  #   item.nodeID = nodeID
  #   item.setText(0, name)
  #   item.setSelected(True)
  #
  #   k = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable \
  #     # | QtCore.Qt.ItemIsEditable
  #   item.setFlags(k)
  #
  #   item.setSelected(False)
  #
  #   self.ui.treeWidget.addTopLevelItem(item)
  #
  #   return item

  def __setInterIntra(self, what):
    self.ontology_tree[self.current_network]["type"] = what

  def __makeList(self, what_list_view, the_list):
    """
    list generator
    :param what_list_view: gui component
    :param the_list: the list to be inserted
    :return:
    """
    what_list_view.clear()
    what_list_view.addItems(the_list)

  def __whichComponent(self, current_branch):
    for i in self.radio:
      if self.radio[i]:
        branch, component = i.split("_")
        if branch == current_branch:
          return component
    self.__writeMessage("error - no such radio button")
    return None

  def __writeMessage(self, message):
    self.ui.msgWindow.clear()
    self.ui.msgWindow.setText(message)

  def __switchNetwork(self, network):
    tree_item = self.tree_items[network]
    self.ui.treeWidget.setCurrentItem(tree_item)
    self.current_network = network
    self.__on_network_selected()

  def __findAndSwitchToDefinitionNetwork(self, v):
    parents = self.ontology_tree[self.current_network]["parents"]
    for nw in reversed(parents):
      if nw in self.variables:
        for v_nw in self.variables[nw]:
          if v == v_nw:
            return nw  # first one it is

  # def __single_click(self, call_slot):
  #
  #   if self.click_count == 2:
  #     # print("debugging -- do nothing")
  #     self.click_count = 1
  #   else:
  #     self.clickTimer.start(300)
  #     QtWidgets.QWidget.connect(self.clickTimer, QtCore.SIGNAL("timeout()"), call_slot)
  #     self.call_slot_single_click = call_slot
  #
  # def __double_clicked(self, call_slot_double_click):
  #   self.__single_click(self.__click_reset)
  #   # print("debugging -- double click ", self.clickTimer.isActive())
  #   QtWidgets.QWidget.disconnect(self.clickTimer, QtCore.SIGNAL("timeout()"), self.call_slot_single_click)
  #   self.click_count = 2
  #   self.clickTimer.stop()
  #   self.__on_listViewX_clicked(call_slot_double_click)
  #
  # def __click_reset(self):
  #   self.clickTimer.stop()
  #   self.click_count = 1
  #   QtWidgets.QWidget.disconnect(self.clickTimer, QtCore.SIGNAL("timeout()"), self.call_slot_single_click)

  # def __on_listViewX_clicked(self, listView):  # TODO :  check this for what it is doing if anything....?
  #
  #   variable_name = listView.currentItem().text()
  # print("name name      :", variable_name)
  # print("variables      :", self.variables[variable_name])
  # # print("structure clicked current network:",self.current_network)
  # network, component = self.variables[variable_name]
  #
  # tree_depth_first_list = self.__makeTreeDepthFirstList()
  # # for nw in tree_depth_first_list:
  #
  # tree_item = self.tree_items[network]
  # self.ui.treeWidget.setCurrentItem(tree_item)
  # self.current_network = network
  # self._on_nework_selected()

  def __clearLayout(self, layout):
    while layout.count():
      child = layout.takeAt(0)
      if child.widget() is not None:
        child.widget().deleteLater()
      elif child.layout() is not None:
        self.__clearLayout(child.layout())

  def __makeAndAddSelector(self, group_name, what, receiver, index, layout, autoexclusive=True):
    """

    :param group_name: name of the group of radio buttons to be added
    :param what: list of labels for the radio buttons --> also identifier
    :param receiver: receiver slot, thus a method
    :param index: string or integer -- if string it must be a radio button identifier,
                                      if number then it is the index in the list of radio buttons,
                                      if -1 no button is checked
    :param layout: a horizontal layout box
    :param autoexclusive: true or false
    :return: the radio selecter QWidget
    """
    radio_selector = RadioSelector()
    list_of_choices = []
    counter = 0
    layout.addWidget(radio_selector)
    for item in what:
      list_of_choices.append((str(counter), item, receiver))
      counter += 1
    if not list_of_choices:
      return None

    radio_selector.addListOfChoices(group_name, list_of_choices, index, autoexclusive=autoexclusive)
    return radio_selector

  def __clearRadioButtons(self):
    r_list = []
    if self.branch == "structure":
      r_list = [self.ui.radioButtonBehaviourArc,
                self.ui.radioButtonBehaviourGraph,
                self.ui.radioButtonBehaviourNode]
    elif self.branch == "behaviour":
      r_list = [self.ui.radioButtonStructureArc,
                self.ui.radioButtonStructureNode,
                self.ui.radioButtonStructureToken]
    for r in r_list:
      r.setChecked(False)

  def __ui_status(self, status):
    print("debugging -- status:", status)
    for i in self.actions["0"]:
      if i in self.actions[status]:
        i.hide()
      else:
        i.show()
    if self.branch:
      self.__clearRadioButtons()

    if self.branch == "structure":
      if status in self.labels:
        for i in self.labels:
          self.ui.labelStructure.setText(self.labels[status]["structure"])
          self.ui.labelStructureExtension.setText(self.labels[status]["extension"])

    if self.lock_delete:
      for i in self.actions["block_delete"]:
        i.hide()

  #### event handling

  @QtCore.pyqtSlot(str)
  def on_comboInterconnectionNetworks_activated(self, choice):
    left_nw = self.interconnection_network_dictionary[choice]["left"]
    right_nw = self.interconnection_network_dictionary[choice]["right"]
    vars_types = self.saved_ontology_container.variable_types_on_interconnection_networks_left_right
    print("debugging -- left, right", left_nw, right_nw)
    print("deugging -- var-types", vars_types[choice])
    left_variable_types = self.saved_ontology_container.variable_types_on_networks[left_nw]
    root_variable_types = self.saved_ontology_container.variable_types_on_networks["root"]
    enabled_set = set(left_variable_types) - set(root_variable_types)
    print("debugging -- left variables classes:", left_variable_types)
    print("debugging -- enabled_set classes:", enabled_set)

    pass

  # def on_treeWidget_itemSelectionChanged(self,index):  # TODO: gave a pyqt error: missing 1 required positional
  #  argument: 'index'
  #   print("debugging : entered")
  #   self.on_treeWidget_clicked(index)

  def on_treeWidget_clicked(self, index):  # state network_selected
    self.current_network = self.ui.treeWidget.currentItem().name
    print("debugging -- current network selected: ", self.current_network)

    self.__on_network_selected()

  def on_pushInfo_pressed(self):
    msg_popup = UI_FileDisplayWindow(FILES["info_ontology_foundation_editor"])
    msg_popup.exec_()

  def on_pushGraph_pressed(self):
    makeOntologyDotGraph(self.ontology_tree, self.ontology_name, show="write")

  def __addFixedRules(self):  # RULE: fixed rules

    # RULE: main rules
    RULES = {
            "variable_classes_having_port_variables": [],
            "variable_classes_being_state_variables": [],
            "numerical_value"                       : "value",
            "nodes_allowing_token_injection"        : ["constant"],
            "nodes_allowing_token_conversion"       : ["dynamic", "event"],
            "nodes_allowing_token_transfer"         : ["intraface"],
            "name_space"                            : None,
            }

    rules = self.ontology["rules"]
    for r in RULES:
      if r not in rules:
        rules[r] = RULES[r]


    # if not rules["name_space"]:
    #   answ = makeMessageBox(message="use GLOBAL name space?",
    #                             buttons=["YES", "NO"],
    #                             infotext="choose if the equation ontology is based on a global name space or a discipline local one""message")
    #   if answ == "YES":
    #     print("chosen yes ")
    #     rules["name_space"] = True
    #   else:
    #     print("chosen no ")
    #     rules["name_space"] = False
    # rules["name_space"] = False

  def on_pushSave_pressed(self):
    self.__ui_status("saved")
    self.__addFixedRules()
    saveBackupFile(self.ontology_file)
    putDataOrdered(self.ontology, self.ontology_file)

    if self.new_variable_file:
      variables_f_name = FILES["variables_file"] % self.ontology_name
      # NOTE: do not delete the below
      # globalVariableID(update=False, reset=True)  # RULE: for a new variable file reset global variable ID
      # globalEquationID(update=False, reset=True)  # RULE: and global equation ID
      variables = {}
      indices = {}
      ProMoIRI = RecordProMoIRI()
      data = VariableFile(variables, indices, VARIABLE_EQUATIONS_VERSION, ProMoIRI)
      putData(data, variables_f_name)
      self.__writeMessage("ontology file written and new data file generated : %s" % variables_f_name)
    else:
      self.__writeMessage("ontology file written")

  def on_pushAddChild_pressed(self):
    self.__ui_status("add_child_selected")
    models = list(self.ontology_tree.keys())
    model_name = askForString("give new network name or exit ", "name for new child", limiting_list=models)
    if not model_name:
      self.__ui_status("network_selected")
      return
    if model_name in self.ontology_tree:
      self.__writeMessage("error -- name -- %s -- is already defined" % model_name)
      return

    print("model name: ", model_name)
    self.ontology_tree[self.current_network].addChild(model_name)
    self.ontology_tree[model_name] = Ontology(model_name, 'intra', self.ontology_tree[self.current_network])
    # self.__makeTreeView()
    self.tree_items = makeTreeView(self.ui.treeWidget, self.ontology_tree)

  def on_pushRemoveChild_pressed(self):
    # print("debugging -- remove child from ", self.current_network)
    deleting = []
    for nw in self.ontology_tree:
      if self.current_network in self.ontology_tree[nw]["parents"]:
        # print("debugging -- delete : ", nw)
        deleting.append(nw)

    for nw in deleting:  # delete branch below
      del self.ontology_tree[nw]

    print("deugging -- delete : ", self.current_network)
    parent = self.ontology_tree[self.current_network]["parents"][0]
    self.ontology_tree[parent]["children"].remove(
            self.current_network)  # remove from children list of the parent node

    del self.ontology_tree[self.current_network]  # finally delete node itself
    # self.__makeTreeView()
    self.tree_items = makeTreeView(self.ui.treeWidget, self.ontology_tree)
    self.__ui_status("removed_branch")

  def __on_network_selected(self):

    if self.ontology_tree[self.current_network]["structure"]["token"] == {}:
      self.__ui_status("network_selected_no_tokens")
    else:
      self.__ui_status("network_selected")

    self.ui.listViewStructure.clear()
    self.ui.listViewStructureExtension.clear()
    self.ui.listViewBehaviour.clear()
    self.ui.listViewStructureExtension.clear()

    self.on_radioButtonBehaviourGraph_toggled(self.radio["behaviour_graph"])
    self.on_radioButtonBehaviourNode_toggled(self.radio["behaviour_node"])
    self.on_radioButtonBehaviourArc_toggled(self.radio["behaviour_arc"])

    self.on_radioButtonStructureToken_toggled(self.radio["structure_token"])
    self.on_radioButtonStructureNode_toggled(self.radio["structure_node"])
    self.on_radioButtonStructureArc_toggled(self.radio["structure_arc"])

    inter_intra = self.ontology_tree[self.current_network]["type"]
    if inter_intra == "inter":
      self.ui.radioButtonInter.setChecked(True)
    else:
      self.ui.radioButtonIntra.setChecked(True)

    # is adding indices enabled?
    if self.current_network not in self.ontology["rules"]["network_enable_adding_indices"]:
      self.ontology["rules"]["network_enable_adding_indices"][self.current_network] = False
    self.ui.radioButtonIsEnableAddingIndex.setChecked(
            self.ontology["rules"]["network_enable_adding_indices"][self.current_network])

  def on_radioButtonInter_toggled(self, position):
    what = "intra"
    if position:
      what = "inter"
    self.__setInterIntra(what)

  def on_radioButtonIntra_toggled(self, position):
    what = "inter"
    if position:
      what = "intra"
    self.__setInterIntra(what)

  def on_radioButtonStructureNode_toggled(self, position):
    self.radio["structure_node"] = position
    if position:
      self.current_structure_component = "node"
      # print("debugging -- structure node")
      the_list = sorted(self.ontology_tree[self.current_network]["structure"]["node"].keys())
      self.__makeList(self.ui.listViewStructure, the_list)
      self.__ui_status("structure_node_selected")

  def on_radioButtonStructureArc_toggled(self, position):
    self.radio["structure_arc"] = position
    if position:
      self.current_structure_component = "arc"
      # print("debugging -- structure arc")

      token_list = sorted(self.ontology_tree[self.current_network]["structure"]["token"].keys())

      self.__clearLayout(self.ui.horizontalLayoutToken)

      self.radio_selectors_token = self.__makeAndAddSelector("tokens",
                                                             token_list,
                                                             self.radioReceiverArcToken, -1,
                                                             self.ui.horizontalLayoutToken)
      self.__ui_status("structure_arc_selected")

  def radioReceiverArcToken(self, token_class, token, token_string, toggle):
    if toggle:
      # print("radioReceiverArcDistribution: reciever class %s, radio token %s. token_string %s" % (
      # token_class, token, token_string))
      self.current_arc_token = token_string

      the_list = sorted(self.ontology_tree[self.current_network]["structure"]["arc"][token_string].keys())
      self.__makeList(self.ui.listViewStructure, the_list)
      self.__ui_status("structure_arc_token_selected")

  def on_radioButtonStructureToken_toggled(self, position):
    self.radio["structure_token"] = position
    if position:
      # print("structure token")
      self.current_structure_component = "token"
      the_list = sorted(self.ontology_tree[self.current_network]["structure"]["token"].keys())
      self.__makeList(self.ui.listViewStructure, the_list)
      self.__ui_status("structure_token_selected")

  def on_radioButtonHasPortVariables_toggled(self, position):
    # print("debugging -- radio button position: ", position)
    variable_classes_having_port_variables = set(self.ontology["rules"]["variable_classes_having_port_variables"])
    if position:
      variable_classes_having_port_variables.add(self.current_behaviour_variable)
    else:
      variable_classes_having_port_variables.difference_update()
    self.ontology["rules"]["variable_classes_having_port_variables"] = sorted(
            variable_classes_having_port_variables)

  def on_radioButtonIsEnableAddingIndex_toggled(self, position):
    print("debugging -- radio button position: ", position)
    self.ontology["rules"]["network_enable_adding_indices"][self.current_network] = position

    # variable_classes_being_state_variables = set(self.ontology["rules"]["variable_classes_being_state_variables"])
    # if position:
    #   variable_classes_being_state_variables.add(self.current_behaviour_variable)
    # else:
    #   variable_classes_being_state_variables.difference_update()
    # self.ontology["rules"]["variable_classes_being_state_variables"] = sorted(
    #         variable_classes_being_state_variables)

  def on_radioButtonBehaviourNode_toggled(self, position):
    self.radio["behaviour_node"] = position
    if position:
      self.current_behaviour_component = "node"
      # print("debugging -- behaviour node")
      the_list = sorted(self.ontology_tree[self.current_network]["behaviour"]["node"])
      self.__makeList(self.ui.listViewBehaviour, the_list)
      self.__ui_status("behaviour_component_selected")

  def on_radioButtonBehaviourArc_toggled(self, position):
    self.radio["behaviour_arc"] = position
    if position:
      self.current_behaviour_component = "arc"
      # print("debugging -- behaviour arc")
      the_list = sorted(self.ontology_tree[self.current_network][self.branch][self.current_behaviour_component])
      self.__makeList(self.ui.listViewBehaviour, the_list)
      self.__ui_status("behaviour_component_selected")

  def on_radioButtonBehaviourGraph_toggled(self, position):
    self.radio["behaviour_graph"] = position
    if position:
      self.current_behaviour_component = "graph"
      # print("debugging -- behaviour graph")
      the_list = sorted(self.ontology_tree[self.current_network]["behaviour"]["graph"])
      self.__makeList(self.ui.listViewBehaviour, the_list)
      self.__ui_status("behaviour_component_selected")

  def on_listViewStructure_clicked(self):
    variable_name = self.ui.listViewStructure.currentItem().text()
    self.current_structure_variable = variable_name
    component = self.__whichComponent("structure")
    ###self.__single_click(self.__click_reset)
    if component == "arc":
      # get token
      # tokens = self.radio_selectors_token.getListOfCheckedLabelInGroup("tokens")
      token = self.current_arc_token  # tokens[0]
      the_list = self.ontology_tree[self.current_network]["structure"][component][token][variable_name]
      self.__ui_status("structure_arc_token_prop_selected")
    elif component == "node":
      the_list = sorted(self.ontology_tree[self.current_network]["structure"][component][variable_name])
      self.__ui_status("structure_node_prop_selected")
    else:
      self.__ui_status("structure_token_prop_selected")
      the_list = sorted(self.ontology_tree[self.current_network]["structure"][component][variable_name])
    self.__makeList(self.ui.listViewStructureExtension, the_list)

  def on_listViewStructure_doubleClicked(self):
    ###self.__double_clicked(self.ui.listViewStructure)
    self.current_structure_variable = self.ui.listViewStructure.currentItem().text()
    if self.current_structure_component == "arc":
      v = "%s-%s-%s-%s" % (self.branch, self.current_structure_component, self.current_arc_token,
                           self.current_structure_variable)
    else:
      v = "%s-%s-%s" % (self.branch, self.current_structure_component, self.current_structure_variable)
    nw = self.__findAndSwitchToDefinitionNetwork(v)
    # print("debugging -- set network:", nw, "variable ", v)
    if nw:  # root yields None
      self.__switchNetwork(nw)

  def on_listViewStructureExtension_clicked(self):
    variable_name = self.ui.listViewStructureExtension.currentItem().text()
    self.current_structure_extension_variable = variable_name
    print("debugging -- extension selected : ", variable_name)
    component = self.__whichComponent("structure")
    ###self.__single_click(self.__click_reset)
    if component == "node":
      self.__ui_status("structure_node_prop_ext_selected")
    elif component == "token":
      self.__ui_status("structure_token_prop_ext_selected")
    else:
      self.__ui_status("structure_arc_prop_ext_selected")

  def on_listViewStructureExtension_doubleClicked(self):
    ###self.__double_clicked(self.ui.listViewStructureExtension)
    self.current_structure_extension_variable = self.ui.listViewStructureExtension.currentItem().text()
    if self.current_structure_component == "arc":
      v = "%s-%s-%s-%s-%s" % (self.branch, self.current_structure_component, self.current_arc_token,
                              self.current_structure_variable, self.current_structure_extension_variable)
      # print("debugging -- came arc way")
    else:
      # print("debugging -- came the other way")
      v = "%s-%s-%s-%s" % (self.branch, self.current_structure_component, self.current_structure_variable,
                           self.current_structure_extension_variable)
    nw = self.__findAndSwitchToDefinitionNetwork(v)
    # print("debugging -- set network:", nw, "variable ", v)
    if nw:  # root yields None
      self.__switchNetwork(nw)

  def on_listViewBehaviour_clicked(self):
    variable_name = self.ui.listViewBehaviour.currentItem().text()
    self.current_behaviour_variable = variable_name
    ### self.__single_click(self.__click_reset)

    variable_name = self.ui.listViewBehaviour.currentItem().text()
    # print("debugging -- behaviour selected : ", variable_name)
    # print("debugging -- selected component :",self.current_behaviour_component )
    if self.current_behaviour_component in ["node",
                                            "graph",
                                            "arc"]:  # ....RULE: variable classes related to node and graph may
      # RULE: ---continued-- have port variables
      self.__ui_status("behaviour_prop_selected_node")
      if self.current_behaviour_variable in self.ontology["rules"]["variable_classes_having_port_variables"]:
        self.ui.radioButtonHasPortVariables.setChecked(True)
      else:
        self.ui.radioButtonHasPortVariables.setChecked(False)

      if self.current_behaviour_variable in self.ontology["rules"]["variable_classes_being_state_variables"]:
        self.ui.radioButtonIsEnableAddingIndex.setChecked(True)
      else:
        self.ui.radioButtonIsEnableAddingIndex.setChecked(False)

    else:
      self.__ui_status("behaviour_prop_selected")

  def on_listViewBehaviour_doubleClicked(self):
    ###self.__double_clicked(self.ui.listViewBehaviour)
    v = "%s-%s-%s" % (self.branch, self.current_behaviour_component, self.current_behaviour_variable)
    nw = self.__findAndSwitchToDefinitionNetwork(v)
    # print("debugging -- set network:", nw)
    if nw:
      self.__switchNetwork(nw)

  @QtCore.pyqtSlot(int)
  def on_tabWidget_currentChanged(self, index):
    self.branch = self.branches[self.ui.tabWidget.currentIndex()]
    # print("debugging -- selected new branch :", self.branch, index)
    if index == 0:
      self.__ui_status("structure_selected")
    elif index == 1:
      self.__ui_status("behaviour_selected")

  def on_pushNewBehaviourElement_pressed(self):
    new_element = askForString("new behaviour element")
    if not new_element: return
    # print("debugging -- new behaviour element", new_element)
    # print("debugging -- branch %s -- component %s -- new element %s"
    #       % (self.branch, self.current_behaviour_component, new_element))

    nw_list = self.__makeTreeDepthFirstList(self.current_network, [])
    # print("debugging -- ", self.current_network, '----', nw_list)

    for nw in nw_list:
      o = self.ontology_tree[nw] \
        [self.branch] \
        [self.current_behaviour_component]
      if new_element not in o:
        o.append(new_element)

    the_list = sorted(self.ontology_tree[self.current_network][self.branch][self.current_behaviour_component])
    self.__makeList(self.ui.listViewBehaviour, the_list)
    self.__ui_status("behaviour_component_selected")
    self.__indexVariableClasses()

  def on_pushNewStructureElement_pressed(self):
    new_element = askForString("new structure element")
    if not new_element: return
    if self.current_structure_component == "arc":
      # print("debugging -- branch %s -- token %s -- component %s -- new element %s"
      #       % (self.branch, self.current_arc_token, self.current_structure_component, new_element))

      nw_list = (self.__makeTreeDepthFirstList(self.current_network, []))
      for nw in nw_list:
        self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component] \
          [self.current_arc_token] \
          [new_element] = []

      the_list = sorted(self.ontology_tree[self.current_network] \
                          [self.branch] \
                          [self.current_structure_component] \
                          [self.current_arc_token])

    else:
      # print("debugging -- branch %s -- component %s -- new element %s"
      #       % (self.branch, self.current_structure_component, new_element))

      nw_list = (self.__makeTreeDepthFirstList(self.current_network, []))
      for nw in nw_list:
        self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component] \
          [new_element] = []

      if self.current_structure_component == "token":
        for nw in nw_list:
          self.ontology_tree[nw][self.branch]["arc"][new_element] = {}

      the_list = sorted(self.ontology_tree[self.current_network][self.branch][self.current_structure_component])

    self.__makeList(self.ui.listViewStructure, the_list)
    self.__indexVariableClasses()

    if self.current_structure_component == "arc":
      self.__ui_status("structure_arc_token_selected")
    elif self.current_structure_component == "node":
      self.__ui_status("structure_node_selected")
    else:
      self.__ui_status("structure_token_selected")

  def on_pushNewStructureElementExtension_pressed(self):
    new_element = askForString("new structure extension element")
    if not new_element: return
    if self.current_structure_component == "arc":
      nw_list = (self.__makeTreeDepthFirstList(self.current_network, []))
      for nw in nw_list:
        o = self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component] \
          [self.current_arc_token] \
          [self.current_structure_variable]
        if new_element not in o:
          o.append(new_element)
        if nw == self.current_network:
          the_list = sorted(o)


    else:
      nw_list = (self.__makeTreeDepthFirstList(self.current_network, []))
      for nw in nw_list:
        o = self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component] \
          [self.current_structure_variable]
        if new_element not in o:
          o.append(new_element)
        if nw == self.current_network:
          the_list = sorted(o)

    self.__indexVariableClasses()
    self.__makeList(self.ui.listViewStructureExtension, the_list)

  def on_pushDeleteStructureElement_pressed(self):
    self.on_listViewStructure_doubleClicked()

    delete_element = self.current_structure_variable
    nw_list = (self.__makeTreeDepthFirstList(self.current_network, []))
    # print("debugging -- deleting structure element ", delete_element)
    # if delete_element == "token":
    #   print("debugging -- token ", delete_element)
    # print("debugging --  in network list :", nw_list)
    if self.current_structure_component == "arc":
      for nw in nw_list:
        o = self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component] \
          [self.current_arc_token]
        if delete_element in o:
          o.pop(delete_element)
        if nw == self.current_network:
          the_list = sorted(o)

    else:

      for nw in nw_list:
        o = self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component]
        if delete_element in o:
          o.pop(delete_element)
        if nw == self.current_network:
          the_list = sorted(o)

    if self.current_structure_component == "token":
      for nw in nw_list:
        o = self.ontology_tree[nw] \
          [self.branch] \
          ["arc"]
        if delete_element in o:
          o.pop(delete_element)
        # if nw == self.current_network:
        #   the_list = sorted(o)

    self.__indexVariableClasses()
    self.__makeList(self.ui.listViewStructure, the_list)
    self.__makeList(self.ui.listViewStructureExtension, [])

  def on_pushDeleteStructureElementExtension_pressed(self):
    self.on_listViewStructureExtension_doubleClicked()
    new_element = self.current_structure_extension_variable
    nw_list = (self.__makeTreeDepthFirstList(self.current_network, []))
    if self.current_structure_component == "arc":
      for nw in nw_list:
        o = self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component] \
          [self.current_arc_token] \
          [self.current_structure_variable]
        if new_element in o:
          o.remove(new_element)
        if nw == self.current_network:
          the_list = sorted(o)
    else:
      for nw in nw_list:
        o = self.ontology_tree[nw] \
          [self.branch] \
          [self.current_structure_component] \
          [self.current_structure_variable]
        if new_element in o:
          o.remove(new_element)
        if nw == self.current_network:
          the_list = sorted(o)

    self.__indexVariableClasses()
    self.__makeList(self.ui.listViewStructureExtension, the_list)

  def on_pushDeleteBehaviourElement_pressed(self):

    self.on_listViewBehaviour_doubleClicked()

    nw_list = (self.__makeTreeDepthFirstList(self.current_network, []))
    for nw in nw_list:
      o = self.ontology_tree[nw][self.branch][self.current_behaviour_component]
      o.remove(self.current_behaviour_variable)
      if nw == self.current_network:
        the_list = sorted(o)

    self.__makeList(self.ui.listViewBehaviour, the_list)
    self.__ui_status("behaviour_component_selected")
    self.__indexVariableClasses()
