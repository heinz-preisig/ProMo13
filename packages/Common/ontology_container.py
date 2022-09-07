#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 ontology container
===============================================================================

handles all operations on the ontology container

This is ontology container version 3

Changes: 2015-01-15 Preisig, H A  change file structure

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2014. 08. 14"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__version__ = "7.00"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os as OS
import os.path
from collections import OrderedDict

from copy import copy

from PyQt5 import QtWidgets

from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.common_resources import M_None
from Common.common_resources import TEMPLATE_ARC_APPLICATION
from Common.common_resources import TEMPLATE_INTERCONNECTION_NETWORK, TEMPLATE_INTRACONNECTION_NETWORK, TEMPLATE_INTRACONNECTION_PAIRS
from Common.common_resources import TEMPLATE_INTER_NODE_OBJECT
from Common.common_resources import TEMPLATE_INTRA_NODE_OBJECT
from Common.common_resources import TEMPLATE_INTRA_NODE_OBJECT_WITH_TOKEN
from Common.common_resources import TEMPLATE_NODE_OBJECT
from Common.common_resources import TEMPLATE_NODE_OBJECT_WITH_TOKEN
from Common.common_resources import getData
from Common.common_resources import invertDict
from Common.common_resources import putDataOrdered
from Common.common_resources import saveWithBackup
from Common.common_resources import walkBreathFirstFnc
from Common.common_resources import walkDepthFirstFnc
from Common.pop_up_message_box import makeMessageBox
from Common.qt_resources import NO
from Common.qt_resources import OK
from Common.qt_resources import YES
from Common.record_definitions import Interface
from Common.record_definitions import OntologyContainerFile
from Common.record_definitions import RecordVariable
from Common.record_definitions import VariableFile
from Common.record_definitions_equation_linking import VariantRecord
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.resource_initialisation import ONTOLOGY_VERSION
from Common.resource_initialisation import VARIABLE_EQUATIONS_VERSION
from OntologyBuilder.OntologyEquationEditor.resources import CODE
from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES
from OntologyBuilder.OntologyEquationEditor.resources import renderExpressionFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.variable_framework import Units


def findID(indices, name):
  ID = None
  for id in indices:
    if indices[id]["label"] == name:
      ID = id
      break
  return ID


def makeIndexAliases(index, index_counter, label):
  for language in LANGUAGES["aliasing"]:  # RULE" blank is the delimiter used for splitting the string
    if language == "global_ID":
      s = CODE[language]["index"] % index_counter
      index["aliases"][language] = s  # .strip(" ") # that's not a good idea.
    else:
      index["aliases"][language] = label


def makeIndices(ontology_container):
  """
  generate a index for each
  - node   -- for state
  - diff_node -- for differential state
  - arc    -- for transport
  (- token  -- not needed)
  - typed token
  - conversion
  - node x  typed token
  - diff_node x  typed token
  - arc x  typed token
  - node x conversion
  - conversion x species

  :param ontology_container:
  :return: indices
  """

  from Common.record_definitions import RecordIndex
  from OntologyBuilder.OntologyEquationEditor.resources import CODE
  from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES
  from OntologyBuilder.OntologyEquationEditor.resources import TEMPLATES
  from Common.record_definitions import RecordBlockIndex

  typed_token_definition_nw = ontology_container.typed_token_definition_nw
  token_associated_with_typed_token = ontology_container.token_associated_with_typed_token

  indices = {}
  index_counter = 0
  inverse_lookup = {}

  # nodes and arcs =====================================================================================
  for component in ["node", "arc"]:  # RULE: hard wired components --- the same as in the first stage
    definition_network = "root"  # rule root is root ...
    index = RecordIndex()
    index["label"] = component
    index["network"] = ontology_container.heirs_network_dictionary[definition_network]
    index_counter += 1  # indices.add(**index)
    indices[index_counter] = index
    makeIndexAliases(indices[index_counter], index_counter, component[0].capitalize())

  # typed tokens =======================================================================================
  for typed_token in typed_token_definition_nw:
    definition_network = typed_token_definition_nw[typed_token]
    index = RecordIndex()
    index["label"] = typed_token
    index["network"] = ontology_container.heirs_network_dictionary[definition_network]
    index["tokens"] = ontology_container.token_associated_with_typed_token[typed_token]
    index_counter += 1  # indices.add(**index)
    indices[index_counter] = index

    makeIndexAliases(indices[index_counter], index_counter, typed_token[0].capitalize())

  # conversion of typed tokens =========================================================================
  for typed_token in ontology_container.converting_tokens:
    definition_network = typed_token_definition_nw[typed_token]
    index = RecordIndex()
    label = TEMPLATES["conversion_label"] % typed_token  # [0].capitalize()
    index["label"] = label
    index["network"] = ontology_container.heirs_network_dictionary[definition_network]
    index["tokens"] = ontology_container.converting_tokens[
      typed_token]  # ontology_container.token_associated_with_typed_token[typed_token]
    index_counter += 1
    indices[index_counter] = index
    makeIndexAliases(indices[index_counter], index_counter, TEMPLATES["conversion_alias"] % typed_token[0].capitalize())

  # block indices =====================================================================================
  # node | arc & typed tokens ===================
  for component in ["node", "arc"]:
    index_outer_ID = findID(indices, component)  # inverse_lookup[component]
    for typed_token in typed_token_definition_nw:
      definition_network = typed_token_definition_nw[typed_token]
      index = RecordBlockIndex()
      index_inner_ID = findID(indices, typed_token)  # inverse_lookup[typed_token]
      label = TEMPLATES["block_index"] % (component, typed_token)
      index["label"] = label
      index["network"] = ontology_container.heirs_network_dictionary[definition_network]
      index["indices"] = [index_outer_ID, index_inner_ID]
      index["tokens"] = ontology_container.token_associated_with_typed_token[typed_token]
      index_counter += 1
      indices[index_counter] = index
      index_outer_language = indices[index_outer_ID]["aliases"]["internal_code"]
      index_inner_language = indices[index_inner_ID]["aliases"]["internal_code"]
      for language in LANGUAGES["aliasing"]:
        if language == "global_ID":
          s = CODE[language]["block_index"] % index_counter
          index["aliases"][language] = s  # s.strip(" ")
        else:
          index["aliases"][language] = CODE[language]["block_index"] % (index_outer_language, index_inner_language)

  # node & conversion
  component = "node"
  index_outer_ID = findID(indices, component)  # inverse_lookup[component]
  for typed_token in ontology_container.converting_tokens:
    definition_network = typed_token_definition_nw[typed_token]
    index_inner = TEMPLATES["conversion_label"] % typed_token
    index = RecordBlockIndex()
    index_inner_ID = findID(indices, index_inner)  # inverse_lookup[typed_token]
    label = TEMPLATES["block_index"] % (component, index_inner)
    index["label"] = label
    index["network"] = ontology_container.heirs_network_dictionary[definition_network]
    index["indices"] = [index_outer_ID, index_inner_ID]
    driving_token = ontology_container.converting_tokens[typed_token]
    index["tokens"] = driving_token  # ontology_container.token_associated_with_typed_token[typed_token]
    index_counter += 1
    indices[index_counter] = index
    index_outer_language = indices[index_outer_ID]["aliases"]["internal_code"]
    index_inner_language = indices[index_inner_ID]["aliases"]["internal_code"]
    for language in LANGUAGES["aliasing"]:
      if language == "global_ID":
        s = CODE[language]["index"] % index_counter
        index["aliases"][language] = s  # .strip(" ")
      else:
        index["aliases"][language] = CODE[language]["block_index"] % (index_outer_language, index_inner_language)

  # conversion & typed tokens
  # index_outer_ID = findID(indices, component)  # inverse_lookup[component]
  for typed_token in ontology_container.converting_tokens:
    definition_network = typed_token_definition_nw[typed_token]
    index_outer = TEMPLATES["conversion_label"] % typed_token
    index_outer_ID = findID(indices, index_outer)
    index_inner = typed_token
    index = RecordBlockIndex()
    index_inner_ID = findID(indices, index_inner)  # inverse_lookup[typed_token]
    label = TEMPLATES["block_index"] % (index_outer, index_inner)
    index["label"] = label
    index["network"] = ontology_container.heirs_network_dictionary[definition_network]
    index["indices"] = [index_outer_ID, index_inner_ID]
    driving_token = ontology_container.converting_tokens[typed_token]
    index["tokens"] = [ontology_container.token_associated_with_typed_token[typed_token], driving_token]
    index_counter += 1
    indices[index_counter] = index
    index_outer_language = indices[index_outer_ID]["aliases"]["internal_code"]
    index_inner_language = indices[index_inner_ID]["aliases"]["internal_code"]
    for language in LANGUAGES["aliasing"]:
      if language == "global_ID":
        s = CODE[language]["index"] % index_counter
        index["aliases"][language] = s  # .strip(" ")
      else:
        index["aliases"][language] = CODE[language]["block_index"] % (index_outer_language, index_inner_language)

  return indices


class OntologyContainer():
  """
  store ontology in configuration files.
  """

  def __init__(self, ontology_name, make_indices=False):
    """
    Constructor

      key words :
        structure  relates to structure components
        behaviour  links structure component to equations
        typing     provides attributes to generate typed structure components
        action     actions defined for the components

        @param ontology_location: location of the ontology, a path
    """

    # get the named ontology
    self.ontology_location = DIRECTORIES["ontology_location"] % ontology_name
    self.ontology_name = ontology_name
    self.ontology_file = FILES["ontology_file"] % ontology_name
    print('Ontology file: ', self.ontology_file)
    self.ontology_container = getData(self.ontology_file)

    if "version" not in self.ontology_container:
      if "ontology_tree" not in self.ontology_container:
        dummy_ontology = self.ontology_container
        self.ontology_container = {}
        self.ontology_container["ontology_tree"] = dummy_ontology
      self.ontology_container["version"] = ONTOLOGY_VERSION

    # NOTE: here we can check for older versions

    self.ontology_tree = self.ontology_container["ontology_tree"]
    # self.interfaces = self.ontology_container["interfaces"]

    #
    # if "equation_assignment" in self.ontology_container:
    #   self.equation_assignment = self.ontology_container["equation_assignment"]
    # else:
    #   self.equation_assignment = {
    #         "node"     : {},
    #         "arc"      : {},
    #         "interface": {},
    #         }

    self.rules = self.ontology_container["rules"]  #

    #
    # TODO: converting tokens
    file = FILES["typed_token_file"] % ontology_name  # FILES["converting_tokens_file"] % ontology_name
    self.converting_tokens = getData(file)  # ................................... make available as part of the ontology

    self.ontology_hierarchy = self.__makeOntologyHierarchy()  # .................... constructs hierarchy network labels
    self.networks = walkBreathFirstFnc(self.ontology_tree, "root")

    self.list_leave_networks = self.__makeListOfLeaveNames()  # ................................ list of all leave nodes

    self.list_inter_branches, \
    self.list_inter_branches_pairs, \
    self.intra_domains = self.__makeListInterBranches()  # ..............inter domains --> where tokens can be exchanged

    self.interconnection_network_dictionary, \
    self.intraconnection_network_dictionary = self.__makeConnectionNetworks()  # ...... dict(connection network) of dict

    self.list_interconnection_networks = sorted(self.interconnection_network_dictionary.keys())
    self.list_intraconnection_networks = sorted(self.intraconnection_network_dictionary.keys())

    """ 
       variable_types_on_networks: dict
         #<networks>
           value : list of variable types/classes
           
        variable_types_on_networks_per_component: dict
          #<network> : dict
            #<component> (graph|node|arc) 
              value : list of variable types/classes per component
        variable_types_on_interfaces: dict
          #<interface>: dict
            value: list of variable types/classes
        variable_types_on_networks_and_interfaces: dict
          #<interface> & <network> : dict
             value: list of variable types/classes
    """

    self.variable_types_on_networks, \
    self.variable_types_on_networks_per_component = self.__makeVariableTypeListsNetworks()  # TODO: per_component is
    # not used

    self.entity_behaviours = self.__readVariableAssignmentToEntity()

    self.interfaces = self.__setupInterfaces()

    self.variable_types_on_interfaces = self.__makeVariableTypeListInterfaces()
    self.variable_types_on_intrafaces = self.__makeVariableTypeListIntraFaces()

    # ............................................  dict(network) of sets of networks that are below the hashtag network
    self.heirs_network_dictionary = self.__makeAllWhoInherit()
    self.interface_networks_accessible_to_networks_dictionary = \
      self.__makeInterfaceNetworksAccessibleToNetworksDictionary()
    self.tokens_on_networks = self.__makeTokensOnNetworks()  # ..................... dict(network) of tokens on networks
    self.tokens = self.__makeTokenList()  # ......................................................... global list of all
    #
    self.token_typedtoken_on_networks = self.__make_nw_token_typedtoken_dict()  # .. tokens and typed tokens per network
    #
    self.node_type_list = self.__makeNodeTypesList()  # ........................... global list of node types (dynamics)
    self.node_types_in_networks = self.__makeNodeTypesInNetworksDict()  # ....... dict(leave networks) of lists of node
    #
    #
    self.arc_type_list = self.__makeArcTypesList()  # ............. coded list of coded arc types token|mechanism|nature

    self.object_key_list_networks, \
    self.object_key_list_intra, \
    self.object_key_list_inter, \
    self.keys_networks_tokens = self.__makeObjectKeyLists()

    # self.arc_types_in_leave_networks_list_coded = self.__makeArcTypesInLeaveNetworksDictCoded()
    # self.node_types_in_leave_networks_list_coded = self.__makeNodeTypesInLeaveNetworksDictCoded()

    self.list_node_objects_on_networks, \
    self.list_node_objects_on_networks_with_tokens, \
    self.list_node_objects_on_intra_networks, \
    self.list_node_objects_on_intra_networks_with_token, \
    self.list_node_objects_on_inter_networks, \
    self.list_arc_objects_on_networks, \
    self.list_network_node_objects, \
    self.list_network_node_objects_with_token, \
    self.list_intra_node_objects, \
    self.list_intra_node_objects_with_token, \
    self.list_inter_node_objects, \
    self.list_arc_objects, \
    self.list_reduced_network_node_objects, \
    self.list_reduced_network_arc_objects, \
    self.list_inter_node_objects_tokens = self.__makeNodeObjectList()

    self.arc_types_in_networks_tuples = self.__makeArcTypesInNetworks()
    self.arc_info_dictionary = self.__makeArcTypeDictionary()  # TODO check usage  -->  done is used check structure
    self.arc_info_allnetworks_dict = self.__make_arc_type_network_dict()  # TODO: check usage

    self.token_definition_nw, \
    self.typed_token_definition_nw, \
    self.token_associated_with_typed_token = self.__makeDefinitionNetworkDictionaries()
    self.typed_token_refining_token = invertDict(self.token_associated_with_typed_token)

    self.variables, \
    self.indices, \
    self.variable_record_filter, \
    self.version, \
    self.ProMoIRI = self.readVariables()

    self.node_arc_SubClasses = self.readNodeArcAssignments()

    if self.indices == {}:  # DOC: make indices if they do not yet exist
      self.indices = makeIndices(self)
      try:
        self.indices = makeIndices(self)
      except:
        reply = QtWidgets.QMessageBox.question(None, "exception",
                                               "There are problems with generating the indices probably missing the "
                                               "definition of refined tokens for example token mass refined by species"
                                               " --- continue ?",
                                               OK, NO)
        if reply in [OK, YES]:
          pass
        else:
          exit(-1)

    else:
      for i in self.indices:
        def_network = self.indices[i]["network"][0]
        self.indices[i]["network"] = self.heirs_network_dictionary[def_network]

    self.indexEquations()

  def indexEquations(self):
    self.equation_dictionary = self.__makeEquationDictionary()
    self.equation_variable_dictionary = self.__makeEquationVariableDictionary()
    self.equations, \
    self.equation_information, \
    self.equation_inverse_index = self.__makeEquationAndIndexLists()

  def checkForRule(self, rule):
    """
    checking for what rules exit in the ontology
    """
    # fixing changing the ontology adding rule "variable_classes_being_state_variables"
    if rule not in self.rules:
      return False
    else:
      return True

  # def setRule(self, rule, value):
  #   self.rules[rule] = value
  #   self.writeMe()

    #   self.rules["variable_classes_being_state_variables"] = None
    # if "name_space" not in self.rules:
    #   answ = makeMessageBox(message="use GLOBAL name space?",
    #                         buttons=["YES", "NO"],
    #                         infotext="choose if the equation ontology is based on a global name space or a discipline local one")
    #   print("choice", answ)
    #   if answ == "YES":
    #     print("chosen yes ")
    #   else:
    #     print("chosen no ")
    #   exit()

  def __setupInterfaces(self):
    # RULE: by default all variable classes from the left network are available

    list_networks = self.list_inter_branches_pairs
    interfaces = {}
    for network in list_networks:
      # if network not in self.list_inter_branches_pairs: #self.interfaces:
      left_nw, right_nw = network.split(CONNECTION_NETWORK_SEPARATOR)
      # left_nw = list_networks[network]["left"]
      # right_nw = list_networks[network]["right"]
      left_variable_types = self.variable_types_on_networks[left_nw]

      interfaces[network] = Interface(network, left_nw, right_nw, left_variable_types)

    # print("debugging -- interface definitions")
    return interfaces

  #####################
  def __makeObjectKeyLists(self):

    keys_networks = []
    keys_networks_tokens = []
    networks = self.networks

    # we make all combinations first
    for nw in networks:
      node_types = list(self.ontology_tree[nw]["structure"]["node"].keys())
      for node_type in node_types:
        natures = self.ontology_tree[nw]["structure"]["node"][node_type]
        for nature in natures:
          tokens = list(self.ontology_tree[nw]["structure"]["token"].keys())
          typed_tokens = []
          for token in tokens:
            typed_tokens.extend(self.ontology_tree[nw]["structure"]["token"][token])
          tokens.extend(typed_tokens)
          for token in tokens:
            keys_networks.append((nw, "node", node_type, nature, token))
          tokens = list(self.ontology_tree[nw]["structure"]["token"].keys())
          for token in tokens:
            keys_networks_tokens.append((nw, "node", node_type, nature, token))
          if len(tokens) > 1:
            keys_networks_tokens.append((nw, "node", node_type, nature, tokens))

      arc_info = self.ontology_tree[nw]["structure"]["arc"]
      tokens = list(arc_info.keys())
      for token in tokens:
        arc_info = self.ontology_tree[nw]["structure"]["arc"]
        mechanisms = arc_info[token]
        for mechanism in mechanisms:
          arc_info = self.ontology_tree[nw]["structure"]["arc"]
          natures = arc_info[token][mechanism]
          for nature in natures:
            keys_networks.append((nw, "arc", mechanism, nature, token))

    keys_intra = []
    for intra_nw in self.intraconnection_network_dictionary:
      left = self.intraconnection_network_dictionary[intra_nw]["left"]
      # right = self.intraconnection_network_dictionary[intra_nw]["right"]
      # keys_intra.append((intra_nw, "intra", left, right))
      tokens = list(self.ontology_tree[left]["structure"]["token"].keys())
      for token in tokens:
        keys_intra.append((intra_nw, "intra", token))

    keys_inter = []
    for inter_nw in self.list_inter_branches_pairs:  # interconnection_network_dictionary:
      # left = self.interconnection_network_dictionary[inter_nw]["left"]
      # right = self.interconnection_network_dictionary[inter_nw]["right"]
      # keys_inter.append((inter_nw, "inter", left, right))
      inter_token = self.interfaces[inter_nw]["token"]
      keys_inter.append((inter_nw, "inter", inter_token))

    return keys_networks, keys_intra, keys_inter, keys_networks_tokens

  def __makeNodeObjectList(self):
    """
    list of nodes per network (dynamics|nature)
    list of arcs per network (
    """
    nodeObjects_on_networks = {}
    nodeObjects_on_networks_with_token = {}
    nodeObjects_on_intra_networks = {}
    nodeObjects_on_intra_networks_with_token = {}
    nodeObjects_on_inter_networks = {}

    set_node_objects_on_networks = set()
    set_node_objects_on_networks_with_token = set()
    set_node_objects_on_intra_networks = set()
    set_node_objects_on_intra_networks_with_token = set()
    set_node_objects_on_inter_networks = set()
    arcObjects_on_networks = {}
    set_arc_objects = set()

    for nw in self.networks:
      nodeObjects_on_networks[nw] = set()
      nodeObjects_on_networks_with_token[nw] = set()
      arcObjects_on_networks[nw] = set()

    for nw in self.list_intraconnection_networks:
      nodeObjects_on_intra_networks[nw] = set()
      nodeObjects_on_intra_networks_with_token[nw] = set()
      arcObjects_on_networks[nw] = set()

    for nw in self.list_inter_branches_pairs:  # list_interconnection_networks:
      nodeObjects_on_inter_networks[nw] = set()
      arcObjects_on_networks[nw] = set()

    for nw, component, a, nature, token in self.object_key_list_networks:
      if component == "node":
        dynamics = a
        dummy = TEMPLATE_NODE_OBJECT % (dynamics, nature)
        nodeObjects_on_networks[nw].add(dummy)
        set_node_objects_on_networks.add(dummy)

        dummy = TEMPLATE_NODE_OBJECT_WITH_TOKEN % (dynamics, nature, token)
        nodeObjects_on_networks_with_token[nw].add(dummy)
        set_node_objects_on_networks_with_token.add(dummy)


      elif component == "arc":
        mechanism = a
        dummy = TEMPLATE_ARC_APPLICATION % (token, mechanism, nature)
        arcObjects_on_networks[nw].add(dummy)
        set_arc_objects.add(dummy)

    for nw, nature, token in self.object_key_list_intra:
      dummy = TEMPLATE_INTRA_NODE_OBJECT % (nature)
      nodeObjects_on_intra_networks[nw].add(dummy)
      set_node_objects_on_intra_networks.add(dummy)
      dummy = TEMPLATE_INTRA_NODE_OBJECT_WITH_TOKEN % (nature, token)
      nodeObjects_on_intra_networks_with_token[nw].add(dummy)
      set_node_objects_on_intra_networks_with_token.add(dummy)

      pass

    # print("debugging")

    for nw, nature, token in self.object_key_list_inter:
      dummy = TEMPLATE_INTER_NODE_OBJECT % (nature)
      nodeObjects_on_inter_networks[nw].add(dummy)
      set_node_objects_on_inter_networks.add(dummy)
      mechanism = self.interfaces[nw]["mechanism"]
      nature = self.interfaces[nw]["nature"]
      dummy = TEMPLATE_ARC_APPLICATION % (token, mechanism, nature)
      set_arc_objects.add(dummy)
      pass

    list_node_objects_on_networks = {}
    list_node_objects_on_networks_with_tokens = {}
    for nw in nodeObjects_on_networks:
      list_node_objects_on_networks[nw] = sorted(nodeObjects_on_networks[nw])
      list_node_objects_on_networks_with_tokens[nw] = sorted(nodeObjects_on_networks_with_token[nw])

    list_node_objects_on_intra_networks = {}
    list_node_objects_on_intra_networks_with_token = {}
    for nw in nodeObjects_on_intra_networks:
      list_node_objects_on_intra_networks[nw] = sorted(nodeObjects_on_intra_networks[nw])
      list_node_objects_on_intra_networks_with_token[nw] = sorted(nodeObjects_on_intra_networks_with_token[nw])

    list_node_objects_on_inter_networks = {}
    for nw in nodeObjects_on_inter_networks:
      list_node_objects_on_inter_networks[nw] = sorted(nodeObjects_on_inter_networks[nw])

    list_arc_objects_on_networks = {}
    for nw in arcObjects_on_networks:
      list_arc_objects_on_networks[nw] = sorted(arcObjects_on_networks[nw])

    list_network_node_objects = sorted(set_node_objects_on_networks)
    list_network_node_objects_with_token = sorted(set_node_objects_on_networks_with_token)
    list_intra_node_objects = sorted(set_node_objects_on_intra_networks)
    list_intra_node_objects_with_token = sorted(set_node_objects_on_intra_networks_with_token)
    list_inter_node_objects = sorted(set_node_objects_on_inter_networks)
    list_arc_objects = sorted(set_arc_objects)

    list_reduced_network_node_objects = {}
    for nw in self.list_inter_branches:
      network_node_list = list_node_objects_on_networks[nw]
      list_reduced_network_node_objects[nw] = []
      for i in network_node_list:
        if "constant" not in i:  # RULE: reservoirs (time-scale constant) have no state
          list_reduced_network_node_objects[nw].append(i)

    list_reduced_network_arc_objects = {}
    for nw in self.list_inter_branches:
      network_arc_list = list_arc_objects_on_networks[nw]
      list_reduced_network_arc_objects[nw] = []
      for i in network_arc_list:
        list_reduced_network_arc_objects[nw].append(i)

    list_inter_node_objects_tokens = {}

    for nw in self.list_inter_branches:
      list_inter_node_objects_tokens[nw] = []
      s = "%s|%s|%s"

      node_types = list(self.ontology_tree[nw]["structure"]["node"].keys())
      for node_type in node_types:
        natures = self.ontology_tree[nw]["structure"]["node"][node_type]
        for nature in natures:
          tokens = list(self.ontology_tree[nw]["structure"]["token"].keys())
          for token in tokens:
            ss = s % (node_type, nature, token)
            list_inter_node_objects_tokens[nw].append(ss)
          if len(tokens) > 1:
            r = str(tokens).strip("'[]").replace("'", "").replace(", ", "_")
            ss = s % (node_type, nature, r)
            list_inter_node_objects_tokens[nw].append(ss)

    return \
      list_node_objects_on_networks, \
      list_node_objects_on_networks_with_tokens, \
      list_node_objects_on_intra_networks, \
      list_node_objects_on_intra_networks_with_token, \
      list_node_objects_on_inter_networks, \
      list_arc_objects_on_networks, \
      list_network_node_objects, \
      list_network_node_objects_with_token, \
      list_intra_node_objects, \
      list_intra_node_objects_with_token, \
      list_inter_node_objects, \
      list_arc_objects, \
      list_reduced_network_node_objects, \
      list_reduced_network_arc_objects, \
      list_inter_node_objects_tokens

  ########################

  def __make_nw_token_typedtoken_dict(self):
    dnary = {}
    for nw in list(self.ontology_tree.keys()):
      dnary[nw] = {}
      for token in self.ontology_tree[nw]["structure"]["token"]:
        dnary[nw][token] = []
        if self.ontology_tree[nw]["structure"]["token"][token]:
          dnary[nw][token].append(self.ontology_tree[nw]["structure"]["token"][token][0])

    invertDict
    return dnary

  def __makeOntologyHierarchy(self):

    ontology_in_hiearchy = {}
    for nw in list(self.ontology_tree.keys()):
      p = ""
      for child in reversed(self.ontology_tree[nw]["parents"]):
        if p == "":
          p = child
          p_list = [child]
        else:
          p += '_' + child
          p_list.append(child)
      if p == "":
        p_list = [self.ontology_tree[nw]["name"]]
      else:
        p += "_" + self.ontology_tree[nw]["name"]
        p_list.append(self.ontology_tree[nw]["name"])
      ontology_in_hiearchy[nw] = p_list
    return ontology_in_hiearchy

  def __makeConnectionNetworks(self):

    intraconnectionNetworks = {}
    interconnectionNetworks = {}
    network_leaves = self.list_leave_networks
    n_leaves = len(network_leaves)
    for i in range(0, n_leaves):
      for j in range(i + 1, n_leaves):
        # connection_nws.append((network_leaves[i], network_leaves[j]))
        l = network_leaves[i]
        r = network_leaves[j]
        l_type = self.ontology_tree[l]["type"]
        r_type = self.ontology_tree[r]["type"]
        type = "inter"
        # RULE: both connected networks being intra --> intraface
        # TODO: needs a check on common ancestor network
        if (l_type == "intra") & (r_type == "intra"):
          type = "intra"
        if type == "inter":
          cnw = TEMPLATE_INTRACONNECTION_NETWORK % (l, r)
          interconnectionNetworks[cnw] = {
                  "left" : l,
                  "right": r,
                  "type" : type
                  }
          cnw = TEMPLATE_INTRACONNECTION_NETWORK % (r, l)  # NOTE: left-right right-left both are enabled
          interconnectionNetworks[cnw] = {
                  "left" : r,
                  "right": l,
                  "type" : type
                  }
        else:
          cnw = TEMPLATE_INTRACONNECTION_NETWORK % (l, r)
          intraconnectionNetworks[cnw] = {
                  "left" : l,
                  "right": r,
                  "type" : type
                  }
          cnw = TEMPLATE_INTRACONNECTION_NETWORK % (l, l)
          intraconnectionNetworks[cnw] = {
                  "left" : l,
                  "right": l,
                  "type" : type
                  }
          cnw = TEMPLATE_INTRACONNECTION_NETWORK % (r, r)
          intraconnectionNetworks[cnw] = {
                  "left" : r,
                  "right": r,
                  "type" : type
                  }
      l = network_leaves[i]
      r = network_leaves[i]
      type = "intra"
      # RULE: but intraconnections within are enabled
      cnw = TEMPLATE_INTRACONNECTION_NETWORK % (l, r)
      intraconnectionNetworks[cnw] = {
              "left" : l,
              "right": r,
              "type" : type
              }
      cnw = TEMPLATE_INTRACONNECTION_NETWORK % (l, l)
      intraconnectionNetworks[cnw] = {
              "left" : l,
              "right": l,
              "type" : type
              }
      cnw = TEMPLATE_INTRACONNECTION_NETWORK % (r, r)
      intraconnectionNetworks[cnw] = {
              "left" : r,
              "right": r,
              "type" : type
              }

    return interconnectionNetworks, intraconnectionNetworks

  def __makeListOfLeaveNames(self):
    leaves = []
    for domain in self.ontology_tree:
      if self.ontology_tree[domain]["children"] == []:
        leaves.append(self.ontology_tree[domain]["name"])
    return sorted(leaves)

  def __makeListInterBranches(self):
    """
    extracts the inter branches from the tree
    """
    interbranches = []
    nodes = walkBreathFirstFnc(self.ontology_tree, "root")

    for n in nodes:
      # print("debugging -- node", n)
      last = n
      if self.ontology_tree[n]["type"] == "inter":
        children = self.ontology_tree[n]["children"]
        if not children:
          interbranches.append(n)
        else:
          inter = []
          for c in children:
            if self.ontology_tree[c]["type"] == "inter":
              inter.append(1)
            else:
              inter.append(0)
          if 0 in inter:
            if 1 in inter:
              print("error -- problems with inter definitions -- mixed branches")
            else:
              interbranches.append(last)
      elif self.ontology_tree[last]["type"] == "inter":
        interbranches.append(last)

    interbranch_pairs = []
    l = len(interbranches)
    for i in range(0, l):
      for j in range(i, l):
        if i != j:  # Note: interconnections are unidirectional thus we need both ways
          pair = TEMPLATE_INTRACONNECTION_PAIRS % (interbranches[i], interbranches[j])
          interbranch_pairs.append(pair)
          pair = TEMPLATE_INTRACONNECTION_PAIRS % (interbranches[j], interbranches[i])
          interbranch_pairs.append(pair)

    # print("debugging -- end interbranches", interbranches)
    # print("debugging -- end interbranch_pairs", interbranch_pairs)
    intra_domains = {}
    for i in interbranches:
      intra_domains[i] = copy(walkDepthFirstFnc(self.ontology_tree, i))

    return interbranches, interbranch_pairs, intra_domains

  def __makeVariableTypeListsNetworks(self):
    variable_types_on_networks = {}
    variable_types_on_networks_per_component = {}

    # networks
    for nw in self.networks:
      variable_types_on_networks[nw] = []
      variable_types_on_networks_per_component[nw] = {}
      for component in self.ontology_tree[nw]["behaviour"]:
        variable_types_on_networks[nw].extend(self.ontology_tree[nw]["behaviour"][component])
        # RULE : no state if there is no token
        if self.ontology_tree[nw]["structure"]["token"] != {}:
          variable_types_on_networks_per_component[nw][component] = self.ontology_tree[nw]["behaviour"][component]
        else:
          if component == "node":
            # RULE: state is required
            try:
              index = self.ontology_tree[nw]["behaviour"][component].index("state")
              variable_types_on_networks_per_component[nw][component] = self.ontology_tree[nw]["behaviour"][component][
                                                                        :index]
            except:
              pass
          elif component == "graph":
            variable_types_on_networks_per_component[nw][component] = self.ontology_tree[nw]["behaviour"][component]
          else:
            variable_types_on_networks_per_component[nw][component] = []  # no variables if there is no tok

    return variable_types_on_networks, \
           variable_types_on_networks_per_component

  def __makeVariableTypeListInterfaces(self):

    variable_types_on_interfaces = {}
    for nw in self.list_inter_branches_pairs:  # interfaces:  # ADDED:
      variable_types_on_interfaces[nw] = self.interfaces[nw][
        "internal_variable_classes"]  # RULE: interfaces have only one variable class

    return variable_types_on_interfaces

  def __makeVariableTypeListIntraFaces(self):
    # connection networks
    variable_types = {}
    for cnw in self.intraconnection_network_dictionary:
      # variable_types_on_networks[cnw] = []
      variable_types[cnw] = {}
      nw_left = self.intraconnection_network_dictionary[cnw]["left"]
      nw_right = self.intraconnection_network_dictionary[cnw]["right"]
      variable_types[cnw] = sorted(
              set(self.variable_types_on_networks[nw_left]) | set(self.variable_types_on_networks[nw_right]))

    return variable_types

  def __makeVariableTypeListInterFaces(self, variable_types_on_networks):
    variable_types = {}
    for cnw in self.interfaces:  # interconnection_network_dictionary:
      variable_types_on_networks[cnw] = []
      variable_types[cnw] = {}
      # l = self.interconnection_network_dictionary[cnw]["left"]
      # r = self.interconnection_network_dictionary[cnw]["right"]
      l = self.interfaces[cnw]["left_network"]
      r = self.interfaces[cnw]["right_network"]

      vars = self.ontology_tree[l]["behaviour"]["node"]
      variable_types[cnw]["left"] = vars
      variable_types[cnw]["right"] = self.ontology_tree[r]["behaviour"]["node"]
    return variable_types

  def __makeAllWhoInherit(self):
    heirs = {}
    for nw in self.networks:
      heirs[nw] = walkDepthFirstFnc(self.ontology_tree, nw)
    # print(heirs[nw])
    return heirs

  def __makeTokensOnNetworks(self):
    tokens_on_networks = {}
    for nw in self.networks:
      tokens_on_networks[nw] = list(self.ontology_tree[nw]["structure"]["token"].keys())
    return tokens_on_networks

  def __makeTokenList(self):
    tokens = set()
    for nw in self.networks:
      for token in self.tokens_on_networks[nw]:
        tokens.add(token)
    return sorted(tokens)

  def __makeTypedTokensOnNetworks(self):
    # rule: only one typed token per network
    # TODO: we must allow for several typed tokens in a network (species , secondary states ...)

    typed_tokens_on_networks = {}
    for nw in self.networks:
      typed_tokens_on_networks[nw] = []
      for token in self.ontology_tree[nw]["structure"]["token"]:
        if self.ontology_tree[nw]["structure"]["token"][token]:
          typed_tokens_on_networks[nw].append(self.ontology_tree[nw]["structure"]["token"][token][0])
        else:  # Already taken care of
          pass
    return typed_tokens_on_networks

  def __makeInterfaceNetworksAccessibleToNetworksDictionary(self):

    d = {}
    for nw in self.networks:
      d[nw] = []
      for inter_nw in self.interfaces:
        right_network = self.interfaces[inter_nw]["right_network"]
        if nw in self.heirs_network_dictionary[right_network]:
          d[nw].append(inter_nw)
    return d

  def __makeNodeTypesList(self):
    """
    collects all node types in a list
    :return: list of node types
    """
    s = []
    for nw in self.list_leave_networks:
      s.extend(list(self.ontology_tree[nw]["structure"]["node"].keys()))
    node_type_list = list(set(s))
    node_type_list.sort()
    return node_type_list

  def __makeArcTypesList(self):
    arcs = self.__makeArcTypesInLeaveNetworksDictCoded()
    leave_nws = self.list_leave_networks
    all_arcs = []
    for nw in leave_nws:
      all_arcs.extend(arcs[nw])
    for cnw in self.list_inter_branches_pairs:  # interconnection_network_dictionary:
      all_arcs.extend(arcs[cnw])
    return sorted(set(all_arcs))

  def __makeNodeTypesInNetworksDict(self):
    # RULE: this is a generation rule for graph objects nodes
    leave_nws = self.list_leave_networks
    nodetypes = OrderedDict()
    for nw in leave_nws:
      nodetypes[nw] = list(self.ontology_tree[nw]["structure"]["node"].keys())
    return nodetypes

  def __makeArcTypesInLeaveNetworksDictCoded(self):
    # RULE: this is a generation rule for graph objects arcs -- the term "transport" can be obtained from behaviour
    # Rule: continue -- arc self.ontology[nw]['behaviour']['arc'][0]  but may have to be more
    # RULE: continue -- current approach hard wired the term 'transport'

    arcs = {}
    for nw in self.list_leave_networks:
      arcs_in_network = []
      for token in self.ontology_tree[nw]["structure"]["arc"]:
        for mechanism in self.ontology_tree[nw]["structure"]["arc"][token]:
          if isinstance(self.ontology_tree[nw]["structure"]["arc"][token], list):
            # RULE: requiring both mechanism and nature to be given,
            # TODO: this becomes obsolete
            nature = M_None
            arcs_in_network.append(TEMPLATE_ARC_APPLICATION % (token, mechanism, nature))
          else:
            for nature in self.ontology_tree[nw]["structure"]["arc"][token][mechanism]:
              arcs_in_network.append(TEMPLATE_ARC_APPLICATION % (token, mechanism, nature))
      arcs[nw] = sorted(set(arcs_in_network))

    for cnw in self.list_inter_branches_pairs:  # interconnection_network_dictionary:  # NOTE: the token is the same
      # for all interfaces
      arcs_in_network = []
      # RULE: fixed wired connection from and to interface
      inter_token = self.interfaces[cnw]["token"]
      mechanism = self.interfaces[cnw]["mechanism"]
      nature = self.interfaces[cnw]["nature"]
      arcs_in_network.append(TEMPLATE_ARC_APPLICATION % (inter_token, mechanism, nature))
      arcs[cnw] = sorted(set(arcs_in_network))

    return arcs  # arc_type_list

  def __makeArcTypesInNetworks(self):

    arcs = {}
    for nw in self.networks:
      arcs_in_network = []
      for token in self.ontology_tree[nw]["structure"]["arc"]:
        for mechanism in self.ontology_tree[nw]["structure"]["arc"][token]:
          if isinstance(self.ontology_tree[nw]["structure"]["arc"][token], list):
            # RULE: requiring both mechanism and nature to be given,
            # TODO: this becomes obsolete
            nature = M_None
            arcs_in_network.append((token, mechanism, nature))
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>ooops")
          else:
            for nature in self.ontology_tree[nw]["structure"]["arc"][token][mechanism]:
              arcs_in_network.append((token, mechanism, nature))
      arcs[nw] = sorted(set(arcs_in_network))
    return arcs  # arc_type_list

  def __makeArcTypeDictionary(self):
    arc_type_dict = {}
    for nw in self.list_leave_networks:
      arc_type_dict[nw] = {}
      for token in list(self.ontology_tree[nw]["structure"]["arc"].keys()):
        arc_type_dict[nw][token] = {}
        for mech in self.ontology_tree[nw]["structure"]["arc"][token]:
          arc_type_dict[nw][token][mech] = self.ontology_tree[nw]["structure"]["arc"][token][mech]
    return arc_type_dict

  def __make_arc_type_network_dict(self):
    arc_type_dict = {}
    for nw in self.networks:
      arc_type_dict[nw] = {}
      for token in list(self.ontology_tree[nw]["structure"]["arc"].keys()):
        arc_type_dict[nw][token] = {}
        for mech in self.ontology_tree[nw]["structure"]["arc"][token]:
          arc_type_dict[nw][token][mech] = self.ontology_tree[nw]["structure"]["arc"][token][mech]
    return arc_type_dict

  def __makeTypedTokensInNetworksDict(self):
    s_active_typed_tokens_in_nw = {}
    passive_typed_tokens_in_nw = {}
    for nw in self.networks:
      s_active_typed_tokens_in_nw[nw] = set()
      passive_typed_tokens_in_nw[nw] = []
      for token in self.ontology_tree[nw]["structure"]["token"]:
        typed_token_list = self.ontology_tree[nw]["structure"]["token"][token]
        if typed_token_list != []:
          for typed_token in typed_token_list:
            # RULE: tokens are of the type passive and active -- passive has the string "_info" in its id
            if "info" in token:
              passive_typed_tokens_in_nw[nw].append(typed_token)
            else:
              [s_active_typed_tokens_in_nw[nw].add(i) for i in self.ontology_tree[nw]["structure"]["token"][token]]
              # RULE: only one active token can be typed, but the typed token may appear in several tokens (control)
      if len(s_active_typed_tokens_in_nw[nw]) > 1:
        print(">>>>>>>>>>>>>>>. error: more than one typed token in network : ", nw, token,
              self.ontology_tree[nw]["structure"]["token"])

    active_typed_tokens_in_nw = {}
    for nw in self.networks:
      active_typed_tokens_in_nw[nw] = list(s_active_typed_tokens_in_nw[nw])
    return active_typed_tokens_in_nw, passive_typed_tokens_in_nw

  def __makeTypedTokenList(self):
    active_typed_token_in_nw, passive_typed_token_in_nw = self.__makeTypedTokensInNetworksDict()
    typed_token_set = set()
    for nw in active_typed_token_in_nw:
      [typed_token_set.add(i) for i in active_typed_token_in_nw[nw]]
    for nw in passive_typed_token_in_nw:
      [typed_token_set.add(i) for i in passive_typed_token_in_nw[nw]]
    return sorted(typed_token_set)

  def __makeDefinitionNetworkDictionaries(self):
    token_definition_nw = {}  # hash is token
    typed_token_definition_nw = {}  # hash is typed token
    token_associated_with_typed_token = {}
    for token in self.tokens:
      for nw in self.networks:
        if token in self.token_typedtoken_on_networks[nw]:
          if token not in token_definition_nw:
            token_definition_nw[token] = nw
            # print("debugging - found first location of token %s in %s"%(token, nw))
          if self.token_typedtoken_on_networks[nw] != []:
            for typed_token in self.token_typedtoken_on_networks[nw][token]:
              if typed_token not in typed_token_definition_nw:
                typed_token_definition_nw[typed_token] = nw
              token_associated_with_typed_token[typed_token] = token
              # print("debugging - found first location of typed token %s in token %s in network %s"%(typed_token,
              # token, nw))
    return token_definition_nw, typed_token_definition_nw, token_associated_with_typed_token

  def __makeEquationDictionary(self):
    equation_dictionary = {}
    for var_ID in self.variables:
      for eq_ID in self.variables[var_ID]["equations"]:
        equation_dictionary[eq_ID] = self.variables[var_ID]["equations"][eq_ID]
    return equation_dictionary

  def __makeEquationVariableDictionary(self):
    equation_variable_dictionary = {}
    for var_ID in self.variables:
      for eq_ID in self.variables[var_ID]["equations"]:
        equation_variable_dictionary[eq_ID] = (var_ID, self.variables[var_ID]["equations"][eq_ID])
    return equation_variable_dictionary

  def __readVariableAssignmentToEntity(self):
    f = FILES["variable_assignment_to_entity_object"] % self.ontology_name
    if not os.path.exists(f):
      entity_behaviours = None

    # loaded_entity_behaviours = getData(f)
    data = getData(f)
    entity_behaviours = VariantRecord()  # make empty structure
    if data:
      loaded_entity_behaviours = data["behaviours"]
      # self.node_arc_associations = data["associations"]

      if loaded_entity_behaviours:
        for entity_str_ID in loaded_entity_behaviours:  # careful there may not be all entities at least during
          # developments
          if loaded_entity_behaviours[entity_str_ID]:
            dummy = VariantRecord()
            data = loaded_entity_behaviours[entity_str_ID]
            for atr in dummy:
              if atr not in data:
                data[atr] = None
            tree = {}
            for treeStrID in data["tree"]:
              tree[int(treeStrID)] = data["tree"][treeStrID]
            data["tree"] = tree

            nodes = {}
            for nodeStrID in data["nodes"]:
              nodes[int(nodeStrID)] = data["nodes"][nodeStrID]
            data["nodes"] = nodes

            entity_behaviours[entity_str_ID] = VariantRecord(tree=data["tree"],
                                                             nodes=data["nodes"],
                                                             IDs=data["IDs"],
                                                             root_variable=data["root_variable"],
                                                             blocked_list=data["blocked"],
                                                             buddies_list=data["buddies"],
                                                             to_be_inisialised=data["to_be_initialised"])
    return entity_behaviours

  def __makeEquationAndIndexLists(self):

    equations = []
    equation_information = {}
    equation_inverse_index = {}
    equation_variable_dictionary = self.equation_variable_dictionary
    count = -1
    for eq_ID in equation_variable_dictionary:
      count += 1
      var_ID, equation = equation_variable_dictionary[eq_ID]
      var_type = self.variables[var_ID]["type"]
      nw_eq = self.variables[var_ID]["network"]

      rendered_expressions = renderExpressionFromGlobalIDToInternal(
              equation["rhs"],
              self.variables,
              self.indices)

      rendered_variable = self.variables[var_ID]["aliases"]["internal_code"]
      equation_label = "%s := %s" % (rendered_variable, rendered_expressions)

      # equations[eq_ID] = (var_ID, var_type, nw_eq, rendered_equation, pixelled_equation)
      equations.append(equation_label)
      equation_inverse_index[eq_ID] = count
      equation_information[count] = (eq_ID, var_ID, var_type, nw_eq, equation_label)
    return equations, equation_information, equation_inverse_index

  def addVariable(self, ID, **args):
    self.variables[ID]={}
    for i in args:
      self.variables[ID][i]=args[i]

  def writeMe(self):

    # container = OrderedDict({
    #       "version"            : ONTOLOGY_VERSION,
    #       "ontology_tree"      : self.ontology_tree,
    #       "interfaces"         : self.interfaces,
    #       "equation_assignment": self.equation_assignment
    #       })

    container = OntologyContainerFile(ONTOLOGY_VERSION)
    for hash in list(container.keys()):
      container[hash] = self.__getattribute__(hash)

    saveWithBackup(self.ontology_file)

  def writeVariables(self, variables, indices, ProMoIRI):
    """
    The data are assumed to be a dictionary (ordered)
    Extraction is included as a method in the Variable class
    :param data: input data
    :return:
    """
    # RULE: The file name carries also the version at least for the time being
    f_name = FILES["variables_file"] % self.ontology_name

    data = VariableFile(variables, indices, VARIABLE_EQUATIONS_VERSION, self.ProMoIRI)

    saveWithBackup(data, f_name)  # NOTE: every saving generates a backup file -- enables scrolling back
    # putData(data, f_name)

  def readVariables(self):
    """
    main issue here is to handle the versions. For the time beigning it is to go from version 6 to version 7
    # version conversion: v6 to v7
    :return: variables
    """
    # print ("----------------------")

    variables_f_name = FILES["variables_file"] % self.ontology_name
    variables_f_name_v7 = FILES["variables_file_v7"] % self.ontology_name
    variable_record_filter = set(list(RecordVariable().keys()))  # minimal configuration

    if OS.path.exists(variables_f_name):
      return self.__readVariablesEquationFile(variable_record_filter, variables_f_name)

    # shift from version 7 to version 8
    elif OS.path.exists(variables_f_name_v7):
      variables, indices, variable_record_filter, version, ProMoIRI = self.__readVariablesEquationFile(
              variable_record_filter, variables_f_name_v7)
      for ID in variables:
        if len(variables[ID]["equations"].keys()) == 0:
          variables[ID]["port_variable"] = True
        else:
          variables[ID]["port_variable"] = False
      return variables, indices, variable_record_filter, version, ProMoIRI


    else:
      msg = "There is no variable file \n-- run foundation editor again and save information\n-- to generate an empty " \
            "" \
            "" \
            "" \
            "" \
            "variable file"

      reply = QtWidgets.QMessageBox.warning(QtWidgets.QWidget(), "ProMo", msg, QtWidgets.QMessageBox.Ok)
      if reply == OK:
        exit(-1)

  def readNodeArcAssignments(self):
    # print("debugging -- read node assignments")

    assignment_file_name = FILES["variable_assignment_to_entity_object"] % self.ontology_name
    if OS.path.exists(assignment_file_name):
      data = self.__readVariableAssignmentFile(assignment_file_name)
      return data
    else:
      return None


    # msg = "There is no variable file \n-- run foundation editor again and save information\n-- to generate an empty " \
    #       "" \
    #       "" \
    #       "" \
    #       "" \
    #       "variable file"
    #
    # reply = QtWidgets.QMessageBox.warning(QtWidgets.QWidget(), "ProMo", msg, QtWidgets.QMessageBox.Ok)
    # if reply == OK:
    #   exit(-1)

  def __readVariablesEquationFile(self, variable_record_filter, variables_f_name):
    data = getData(variables_f_name)
    variables_raw = data["variables"]
    version = data["version"]
    indices_raw = data["indices"]
    ProMoIRI_raw = data["Ontology_global_IDs"]
    for ID in variables_raw:
      try:
        ad = sorted(variables_raw[ID].keys())
      except:
        ad = []
        pass
      variable_record_filter.update(ad)  # TODO: do we still need this ?
    # print("debugging read variables filter:", filter)
    variables = {}
    for ID in variables_raw:
      u = eval(variables_raw[ID]["units"])
      a = Units(ALL=u)
      variables_raw[ID]["units"] = a
      e = eval(variables_raw[ID]["equations"])
      variables_raw[ID]["equations"] = e
      aliases = eval(variables_raw[ID]["aliases"])
      variables_raw[ID]["aliases"] = aliases
      variables_raw[ID]["index_structures"] = eval(variables_raw[ID]["index_structures"])
      try:
        variables_raw[ID]["tokens"] = eval(variables_raw[ID]["tokens"])
      except:
        variables_raw[ID][
          "tokens"] = []  # todo: not sure when it goes wrong. Not defining token results in "" as tokens
      # token_raw = variables_raw[ID]["tokens"]
      # if token_raw == "":
      #   variables_raw[ID]["tokens"]  = []
      # else:
      #   variables_raw[ID]["tokens"] = eval(token_raw)
      # convert from 8 to 8.1 adding tokens
      # if "tokens" not in variables_raw[ID]:
      #   variables_raw[ID]["tokens"] = ""
      variables[int(ID)] = variables_raw[ID]
    indices = {}
    for i in indices_raw:  # DOC: indices are stored in a dictionary with the hash being the enumeration integer
      # for the index
      indices[int(i)] = indices_raw[i]
    ProMoIRI = {}
    for i in ProMoIRI_raw:
      ProMoIRI[i] = int(ProMoIRI_raw[i])
    return variables, indices, variable_record_filter, version, ProMoIRI

  def __readVariableAssignmentFile(self, file_name):
    data = getData(file_name)
    return data
