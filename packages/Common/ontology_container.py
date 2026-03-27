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

import itertools
import json
import os as OS
from collections import OrderedDict
from copy import copy
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from PyQt5 import QtWidgets

from Common.classes.equation import Equation
from Common.classes.io import load_entities_from_file  # todo: eliminate
from Common.classes.io import load_var_idx_eq_from_file  # todo: eliminate
from Common.common_resources import M_None
from Common.common_resources import PROMO_IRI_PREFIX
from Common.common_resources import TEMPLATE_ARC_APPLICATION
from Common.common_resources import TEMPLATE_INTER_NODE_OBJECT
from Common.common_resources import TEMPLATE_INTRA_NODE_OBJECT
from Common.common_resources import TEMPLATE_INTRA_NODE_OBJECT_WITH_TOKEN
from Common.common_resources import TEMPLATE_NODE_OBJECT
from Common.common_resources import TEMPLATE_NODE_OBJECT_WITH_TOKEN
from Common.common_resources import TEMPLATE_INTRACONNECTION_PAIRS
from Common.common_resources import TEMPLATE_INTRACONNECTION_NETWORK
from Common.common_resources import VARIABLE_TYPE_INTERFACE
from Common.common_resources import getData
from Common.common_resources import invertDict
from Common.common_resources import saveWithBackup
from Common.common_resources import walkBreathFirstFnc
from Common.common_resources import walkDepthFirstFnc
from Common.graphics_objects import NAMES
from Common.qt_resources import OK
from Common.record_definitions import Interface
from Common.record_definitions import VariableFile
from Common.record_definitions import makeCompleteVariableRecord
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.resource_initialisation import ONTOLOGY_VERSION
from Common.resource_initialisation import VARIABLE_EQUATIONS_VERSION
from OntologyBuilder.EquationEditor_v01.resources import ID_prefix
from OntologyBuilder.EquationEditor_v01.resources import LANGUAGES
from OntologyBuilder.EquationEditor_v01.variable_framework import Units

# RULE: we constrain interface networks to only exist to the CENTER_NETWORK

CENTRE_NETWORKS = ["macroscopic", "info_processing"]


def findID(indices, name):
    ID = None
    for id in indices:
        if indices[id]["label"] == name:
            ID = id
            break
    return ID


def makeIndexAliases(index, index_counter, label):
    # RULE" blank is the delimiter used for splitting the string
    for language in LANGUAGES["aliasing"]:
        if language == "global_ID":
            s = index_counter  # CODE[language]["index"] % index_counter
            index["aliases"][language] = s  # .strip(" ") # that's not a good idea.
        else:
            index["aliases"][language] = label

        

def makeIndices(ontology_container):
    """
    generate a index for each
    - node   -- for state
    - diff_node -- for differential state
    - arc    -- for transport
    - typed token
    - conversion
    - interface
    - input  (handle interfaces)
    - output (handle interfaces)

    :param ontology_container:
    :return: indices
    """

    from Common.record_definitions import RecordIndex
    from OntologyBuilder.EquationEditor_v01.resources import TEMPLATES

    typed_token_definition_nw = ontology_container.typed_token_definition_nw

    indices = {}
    index_counter = 0

    # nodes and arcs =====================================================================================
    # RULE: hard wired components --- the same as in the first stage
    if ontology_container.version == '8':
        app_list = ["node", "arc", "interface"]
    else:
        app_set = {"node", "arc"}
    for component in app_set:
        definition_network = "root"  # rule root is root ...
        index = RecordIndex()
        index["label"] = component
        index["network"] = ontology_container.heirs_network_dictionary[definition_network]
        index_counter += 1  # indices.add(**index)
        indexID = ID_prefix["index"] + "%s" % index_counter
        indices[indexID] = index
        makeIndexAliases(indices[indexID],
                         indexID, component[0].capitalize())

    # typed tokens =======================================================================================
    for typed_token in typed_token_definition_nw:
        definition_network = typed_token_definition_nw[typed_token]
        index = RecordIndex()
        index["label"] = typed_token
        index["network"] = ontology_container.heirs_network_dictionary[definition_network]
        index["tokens"] = ontology_container.token_associated_with_typed_token[typed_token]
        index_counter += 1  # indices.add(**index)
        indexID = ID_prefix["index"] + "%s" % index_counter
        indices[indexID] = index

        makeIndexAliases(indices[indexID],
                         indexID, typed_token[0].capitalize())

    # conversion of typed tokens =========================================================================
    for typed_token in ontology_container.converting_tokens:
        definition_network = typed_token_definition_nw[typed_token]
        index = RecordIndex()
        label = TEMPLATES["conversion_label"] % typed_token  # [0].capitalize()
        index["label"] = label
        index["network"] = ontology_container.heirs_network_dictionary[definition_network]
        index["tokens"] = ontology_container.converting_tokens[typed_token]
        index_counter += 1
        indexID = ID_prefix["index"] + "%s" % index_counter
        indices[indexID] = index
        makeIndexAliases(indices[indexID], index_counter,
                         TEMPLATES["conversion_alias"] % typed_token[0].capitalize())

        # differential index =============================================================================
    for D in ["D"]:
        # differential index used in control
        index = RecordIndex()
        definition_network = "control"  # rule root is root ...
        index["label"] = D
        index["network"] = index["network"] = ontology_container.heirs_network_dictionary[definition_network]
        index_counter += 1
        indexID = ID_prefix["index"] + "%s" % index_counter
        indices[indexID] = index
        makeIndexAliases(indices[indexID],
                         indexID, index["label"])

        # inter-domain connections ==========================================================================
    if ontology_container.version == '8':
        for dimen in ["p", "q", "r", "t", "u", ]:
            # q :: input dimension
            # p :: output dimension
            # r :: internal state dimension
            index = RecordIndex()
            definition_network = "root"  # rule root is root ...
            index["label"] = dimen
            index["network"] = index["network"] = ontology_container.heirs_network_dictionary[definition_network]
            index_counter += 1
            indexID = ID_prefix["index"] + "%s" % index_counter
            indices[indexID] = index
            makeIndexAliases(indices[indexID],
                             indexID, index["label"])

    for i in indices:
        indices[i]["IRI"] = PROMO_IRI_PREFIX + indices[i]["label"]
        
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

        # get files locations:
        self.ontology_location = DIRECTORIES["ontology_location"] % ontology_name
        self.latex_image_location = DIRECTORIES["latex_location"] % ontology_name
        # get the named ontology

        self.ontology_name = ontology_name
        self.ontology_file = FILES["ontology_file"] % ontology_name
        self.ontology_container = getData(self.ontology_file)

        if "version" not in self.ontology_container:
            if "ontology_tree" not in self.ontology_container:
                dummy_ontology = self.ontology_container
                self.ontology_container = {}
                self.ontology_container["ontology_tree"] = dummy_ontology
            self.ontology_container["version"] = ONTOLOGY_VERSION

        # NOTE: here we can check for older versions

        self.ontology_tree = self.ontology_container["ontology_tree"]

        self.rules = self.ontology_container["rules"]  #

        for nw in self.ontology_tree:
            if nw not in self.rules["normed_network"]:
                self.rules["normed_network"][nw] = False

        #
        # FILES["converting_tokens_file"] % ontology_name
        file = FILES["typed_token_file"] % ontology_name
        # ................................... make available as part of the ontology
        self.converting_tokens = getData(file)

        # .................... constructs hierarchy network labels
        self.ontology_hierarchy = self.__makeOntologyHierarchy()
        self.networks = walkBreathFirstFnc(self.ontology_tree, "root")

        # ................................ list of all leave nodes
        self.list_leave_networks = self.__makeListOfLeaveNames()

        self.list_inter_branches, \
            self.list_inter_branches_pairs, \
            self.intra_domains = self.__makeListInterBranches(
                )  # ..............inter domains --> where tokens can be exchanged

        # RULE: constrain interconnections to in and out of centre domain
        self.interconnection_nws_list = []
        for nw in self.list_inter_branches_pairs:
            for c in CENTRE_NETWORKS:
                if c in nw:
                    if nw not in self.interconnection_nws_list:
                        self.interconnection_nws_list.append(nw)

        
        # Add unified interface domain to rules
        if "interface" not in self.rules["network_enable_adding_indices"]:  # note: this is a unified interface
            print(f"DEBUG: Adding unified 'interface' to rules dictionary")
            self.rules["network_enable_adding_indices"]["interface"] = False

        self.interconnection_network_dictionary, \
            self.intraconnection_network_dictionary = self.__makeConnectionNetworks(
                )  # ...... dict(connection network) of dict

        self.list_interconnection_networks = sorted(
                self.interconnection_network_dictionary.keys())
        self.list_intraconnection_networks = sorted(
                self.intraconnection_network_dictionary.keys())

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

        self.variable_types_on_networks = self.__makeVariableTypeListsNetworks()

        
        self.arc_options = self.__load_arc_options_to_file()

        self.interfaces = self.__setupInterfaces()

        self.variable_types_on_interfaces = VARIABLE_TYPE_INTERFACE# self.__makeVariableTypeListInterfaces()
        self.variable_types_on_intrafaces = self.__makeVariableTypeListIntraFaces()

        # ............................................  dict(network) of sets of networks that are below the hashtag network
        self.heirs_network_dictionary = self.__makeAllWhoInherit()
        self.interface_networks_accessible_to_networks_dictionary = \
            self.__makeInterfaceNetworksAccessibleToNetworksDictionary()
        # ..................... dict(network) of tokens on networks
        self.tokens_on_networks = self.__makeTokensOnNetworks()
        # ......................................................... global list of all
        self.tokens = self.__makeTokenList()
        #
        # .. tokens and typed tokens per network
        self.token_typedtoken_on_networks = self.__make_nw_token_typedtoken_dict()
        #
        # ........................... global list of node types (dynamics)
        self.node_type_list = self.__makeNodeTypesList()
                #
        #
        # ............. coded list of coded arc types token|mechanism|nature
        self.arc_type_list = self.__makeArcTypesList()
        self.arc_entity_types = self.__makeArcEntityTypes()

        self.object_key_list_networks, \
            self.object_key_list_intra, \
            self.object_key_list_inter = self.__makeObjectKeyLists()

        
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
            self.list_inter_node_objects_tokens, \
            self.node_entity_types = self.__makeNodeObjectList()

        
        self.token_definition_nw, \
            self.typed_token_definition_nw, \
            self.token_associated_with_typed_token = self.__makeDefinitionNetworkDictionaries()
        self.typed_token_refining_token = invertDict(
                self.token_associated_with_typed_token)

        self.variables, \
            self.indices, \
            self.version, \
            self.ProMoIRI = self.readVariables()

        self.node_arc_SubClasses = self.load_node_arc_assignments()
        
        if self.indices == {}:  # DOC: make indices if they do not yet exist
            self.indices = makeIndices(self)
            
        else:
            for i in self.indices:
                def_network = self.indices[i]["network"][0]
                self.indices[i]["network"] = self.heirs_network_dictionary[def_network]

        self.indexEquations()
        self.list_equation_png_files = self.__load_equation_png_files_for_ids(self.equation_dictionary.keys())
        self.list_variable_png_files = self.__load_variable_png_files()
        # Add PNG paths directly to variable records
        self.__add_png_paths_to_variables()

        # Load equation icons as QIcon objects for use in dialogs
        self.equation_icons = self.load_equation_icons()
        # Load variable icons as QIcon objects for use in dialogs
        self.variable_icons = self.load_variable_icons()
        self.equation_entity_dict = self.__makeEquationClassesDictionary()

        pass

    def __makeEquationClassesDictionary(self):

        equation_class_dict = {}
        for eq_id in self.equation_dictionary:
            eq_data = self.equation_dictionary[eq_id]

            eq = Equation(eq_id,
                          self.list_equation_png_files.get(eq_id, ""),
                          eq_data.get("type", ""),
                          eq_data.get("lhs", {}),
                          eq_data.get("rhs", {}),
                          eq_data.get("network", ""),
                          eq_data.get("doc", ""),
                          eq_data.get("created", "2024-01-01 00:00:00"),
                          eq_data.get("modified", "2024-01-01 00:00:00")
                          )
            equation_class_dict[eq_id] = eq

        return equation_class_dict

    def save_entities(self, entities_dict):
        """Save entities to file and update equation_entity_dict"""
        try:
            path = FILES["variable_assignment_to_entity_object"] % self.ontology_name

            # Clean up var_eq_forest data before saving to ensure proper format
            cleaned_entities = {}
            for entity_key, entity_data in entities_dict.items():
                cleaned_data = entity_data.copy()
                if 'var_eq_forest' in entity_data:
                    cleaned_forest = []
                    for tree in entity_data['var_eq_forest']:
                        cleaned_tree = {}
                        for key, values in tree.items():
                            # Ensure values are lists without duplicates
                            if isinstance(values, (list, set)):
                                # Convert to set to remove duplicates, then to list
                                cleaned_values = list(set(values))
                                cleaned_tree[key] = cleaned_values
                            else:
                                cleaned_tree[key] = values
                        cleaned_forest.append(cleaned_tree)
                    cleaned_data['var_eq_forest'] = cleaned_forest
                cleaned_entities[entity_key] = cleaned_data

            # Save entities to file
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(cleaned_entities, file, indent=4)

            print(f"Saved {len(cleaned_entities)} entities to {path}")

            # Update equation_entity_dict
            self.equation_entity_dict = self.__makeEquationClassesDictionary()
            print(f"Updated equation_entity_dict with {len(self.equation_entity_dict)} equations")

        except Exception as e:
            print(f"Error saving entities: {e}")

    def indexEquations(self):
        self.equation_dictionary = self.makeEquationDictionary()
        self.equation_variable_dictionary = self.__makeEquationVariableDictionary()
        # self.equations = self.__makeEquationAndIndexLists()
        
    def __setupInterfaces(self):
        # Interfaces are now standard ontology domains - no special handling needed
        # This method kept for backward compatibility but returns empty dict
        # Interface entities are created through standard domain processing
        
        return OrderedDict()

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
                        typed_tokens.extend(
                                self.ontology_tree[nw]["structure"]["token"][token])
                    tokens.extend(typed_tokens)
                    for token in tokens:
                        keys_networks.append((nw, "node", node_type, nature, token))
                    tokens = list(self.ontology_tree[nw]["structure"]["token"].keys())
                    for token in tokens:
                        keys_networks_tokens.append((nw, "node", node_type, nature, token))
                    if len(tokens) > 1:
                        keys_networks_tokens.append(
                                (nw, "node", node_type, nature, tokens))

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
            tokens = list(self.ontology_tree[left]["structure"]["token"].keys())
            for token in tokens:
                keys_intra.append((intra_nw, "intra",
                                   token))  # NOTE that's a fix as intra should be replaced by NAMES["intraface"]
                keys_intra.append((intra_nw, NAMES["intraface"], token))

        keys_inter = []
        # interconnection_network_dictionary:
        # for inter_nw in self.list_inter_branches_pairs:
        #     inter_token = self.interfaces[inter_nw]["token"]
        #     keys_inter.append((inter_nw, NAMES["interface"], inter_token))

        return keys_networks, keys_intra, keys_inter

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
            list_node_objects_on_networks_with_tokens[nw] = sorted(
                    nodeObjects_on_networks_with_token[nw])

        list_node_objects_on_intra_networks = {}
        list_node_objects_on_intra_networks_with_token = {}
        for nw in nodeObjects_on_intra_networks:
            list_node_objects_on_intra_networks[nw] = sorted(
                    nodeObjects_on_intra_networks[nw])
            list_node_objects_on_intra_networks_with_token[nw] = sorted(
                    nodeObjects_on_intra_networks_with_token[nw])

        list_node_objects_on_inter_networks = {}
        for nw in nodeObjects_on_inter_networks:
            list_node_objects_on_inter_networks[nw] = sorted(
                    nodeObjects_on_inter_networks[nw])

        list_arc_objects_on_networks = {}
        for nw in arcObjects_on_networks:
            list_arc_objects_on_networks[nw] = sorted(arcObjects_on_networks[nw])

        token_combinations = {}
        for nw in self.tokens_on_networks:
            tokens = self.tokens_on_networks[nw]

            # If it's a list of strings, use it directly
            if isinstance(tokens, list) and all(isinstance(t, str) for t in tokens):
                token_combinations[nw] = [list(comb) for r in range(1, len(tokens) + 1)
                                          for comb in itertools.combinations(tokens, r)]
            # If it's a single string, wrap it in a list
            elif isinstance(tokens, str):
                token_combinations[nw] = [[tokens]]  # Just the single token
        pass

        node_entity_types_in_internetworks = {}
        for nw in self.list_inter_branches:
            node_entity_types_in_internetworks[nw] = []
            for node_object in nodeObjects_on_networks[nw]:
                for token_combination in token_combinations[nw]:
                    node_entity_types_in_internetworks[nw].append("_".join(token_combination) + "|" + node_object)

        pass

        list_network_node_objects = sorted(set_node_objects_on_networks)
        list_network_node_objects_with_token = sorted(
                set_node_objects_on_networks_with_token)
        list_intra_node_objects = sorted(set_node_objects_on_intra_networks)
        list_intra_node_objects_with_token = sorted(
                set_node_objects_on_intra_networks_with_token)
        list_inter_node_objects = sorted(set_node_objects_on_inter_networks)
        list_arc_objects = sorted(set_arc_objects)

        list_reduced_network_node_objects = {}
        for nw in self.list_inter_branches:
            network_node_list = list_node_objects_on_networks[nw]
            list_reduced_network_node_objects[nw] = []
            for i in network_node_list:
                # RULE: reservoirs (time-scale constant) have no state
                if "constant" not in i:
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
                list_inter_node_objects_tokens, \
                node_entity_types_in_internetworks

    ########################

    def __make_nw_token_typedtoken_dict(self):
        dnary = {}
        for nw in list(self.ontology_tree.keys()):
            dnary[nw] = {}
            for token in self.ontology_tree[nw]["structure"]["token"]:
                dnary[nw][token] = []
                if self.ontology_tree[nw]["structure"]["token"][token]:
                    dnary[nw][token].append(
                            self.ontology_tree[nw]["structure"]["token"][token][0])

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
                if (l_type == "intra") & (r_type == "intra"):
                    type = "intra"
                if type == "inter":
                    cnw = TEMPLATE_INTRACONNECTION_NETWORK % (l, r)
                    interconnectionNetworks[cnw] = {
                            "left" : l,
                            "right": r,
                            "type" : type
                            }
                    # NOTE: left-right right-left both are enabled
                    cnw = TEMPLATE_INTRACONNECTION_NETWORK % (r, l)
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
                if i != j:  # Rule: interconnections are unidirectional thus we need both ways
                    pair = TEMPLATE_INTRACONNECTION_PAIRS % (
                            interbranches[i], interbranches[j])
                    interbranch_pairs.append(pair)
                    pair = TEMPLATE_INTRACONNECTION_PAIRS % (
                            interbranches[j], interbranches[i])
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
                variable_types_on_networks[nw].extend(
                        self.ontology_tree[nw]["behaviour"][component])
                # RULE : no state if there is no token
                if self.ontology_tree[nw]["structure"]["token"] != {}:
                    variable_types_on_networks_per_component[nw][component] = self.ontology_tree[nw]["behaviour"][
                        component]
                else:
                    if component == "node":
                        # RULE: state is required
                        try:
                            index = self.ontology_tree[nw]["behaviour"][component].index(
                                    "state")
                            variable_types_on_networks_per_component[nw][component] = \
                                self.ontology_tree[nw]["behaviour"][component][
                                    :index]
                        except:
                            pass
                    elif component == "graph":
                        variable_types_on_networks_per_component[nw][component] = self.ontology_tree[nw]["behaviour"][
                            component]
                    else:
                        # no variables if there is no tok
                        variable_types_on_networks_per_component[nw][component] = []

        return variable_types_on_networks

    def __makeVariableTypeListInterfaces(self):

        # variable_types_on_interfaces = {}
        # for nw in self.list_inter_branches_pairs:  # interfaces:  # ADDED:
        #     variable_types_on_interfaces[nw] = self.interfaces[nw][
        #         "internal_variable_classes"]  # RULE: interfaces have only one variable class

        return VARIABLE_TYPE_INTERFACE

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

    
    def __makeAllWhoInherit(self):
        heirs = {}
        for nw in self.networks:
            heirs[nw] = walkDepthFirstFnc(self.ontology_tree, nw)
        # print(heirs[nw])
        return heirs

    def __makeTokensOnNetworks(self):
        tokens_on_networks = {}
        for nw in self.networks:
            tokens_on_networks[nw] = list(
                    self.ontology_tree[nw]["structure"]["token"].keys())
        return tokens_on_networks

    def __makeTokenList(self):
        tokens = set()
        for nw in self.networks:
            for token in self.tokens_on_networks[nw]:
                tokens.add(token)
        return sorted(tokens)

    
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
        arcs = self.__makeArcTypesInLeaveNetworksDictCoded(self.list_leave_networks)
        leave_nws = self.list_leave_networks
        all_arcs = []
        for nw in leave_nws:
            all_arcs.extend(arcs[nw])
        # interconnection_network_dictionary:
        # for cnw in self.list_inter_branches_pairs:
        #     all_arcs.extend(arcs[cnw])
        return sorted(set(all_arcs))

    def __makeArcEntityTypes(self):
        arc_types = self.__makeArcTypesInLeaveNetworksDictCoded(self.list_inter_branches)
        # Note: this is a fix to maintain compatibility with the automaton edidor
        nws = self.list_inter_branches
        arc_entity_types = {}
        for nw in nws:
            try:
                arc_entity_types[nw] = arc_types[nw]
            except:
                pass
        pass
        return arc_entity_types

    
    def __makeArcTypesInLeaveNetworksDictCoded(self, networks):
        # RULE: this is a generation rule for graph objects arcs -- the term "transport" can be obtained from behaviour
        # Rule: continue -- arc self.ontology[nw]['behaviour']['arc'][0]  but may have to be more
        # RULE: continue -- current approach hard wired the term 'transport'

        arcs = {}
        for nw in networks:  # self.list_leave_networks:
            arcs_in_network = []
            for token in self.ontology_tree[nw]["structure"]["arc"]:
                for mechanism in self.ontology_tree[nw]["structure"]["arc"][token]:
                    if isinstance(self.ontology_tree[nw]["structure"]["arc"][token], list):
                        # RULE: requiring both mechanism and nature to be given
                        nature = M_None
                        arcs_in_network.append(TEMPLATE_ARC_APPLICATION %
                                               (token, mechanism, nature))
                    else:
                        for nature in self.ontology_tree[nw]["structure"]["arc"][token][mechanism]:
                            arcs_in_network.append(TEMPLATE_ARC_APPLICATION %
                                                   (token, mechanism, nature))
            arcs[nw] = sorted(set(arcs_in_network))

        # interconnection_network_dictionary:  # NOTE: the token is the same
        # for cnw in self.list_inter_branches_pairs:
        #     # for all interfaces
        #     arcs_in_network = []
        #     # RULE: fixed wired connection from and to interface
        #     inter_token = self.interfaces[cnw]["token"]
        #     mechanism = self.interfaces[cnw]["mechanism"]
        #     nature = self.interfaces[cnw]["nature"]
        #     arcs_in_network.append(TEMPLATE_ARC_APPLICATION %
        #                            (inter_token, mechanism, nature))
        #     arcs[cnw] = sorted(set(arcs_in_network))


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

    
    
    
    def __makeDefinitionNetworkDictionaries(self):
        token_definition_nw = {}  # hash is token
        typed_token_definition_nw = {}  # hash is typed token
        token_associated_with_typed_token = {}
        for token in self.tokens:
            for nw in self.networks:
                if token in self.token_typedtoken_on_networks[nw]:
                    if token not in token_definition_nw:
                        token_definition_nw[token] = nw
                    if self.token_typedtoken_on_networks[nw] != []:
                        for typed_token in self.token_typedtoken_on_networks[nw][token]:
                            if typed_token not in typed_token_definition_nw:
                                typed_token_definition_nw[typed_token] = nw
                            token_associated_with_typed_token[typed_token] = token
        return token_definition_nw, typed_token_definition_nw, token_associated_with_typed_token

    def makeEquationDictionary(self):
        equation_dictionary = {}
        # First pass: create basic dictionary without PNG files
        for var_ID in self.variables:
            for eq_ID in self.variables[var_ID]["equations"]:
                equation_dictionary[eq_ID] = self.variables[var_ID]["equations"][eq_ID]
                equation_dictionary[eq_ID]["lhs"] = self.variables[var_ID]["compiled_lhs"]

        # Second pass: add PNG files to the completed dictionary
        equation_png_files = self.__load_equation_png_files_for_ids(equation_dictionary.keys())
        for eq_id in equation_dictionary:
            png_path = equation_png_files.get(eq_id, None)
            # Only set if the path is valid and not empty
            if png_path and png_path != 'None' and str(png_path).strip():
                equation_dictionary[eq_id]["png_file"] = str(png_path)
            else:
                equation_dictionary[eq_id]["png_file"] = None
        return equation_dictionary

    def __makeEquationVariableDictionary(self):
        equation_variable_dictionary = {}
        for var_ID in self.variables:
            for eq_ID in self.variables[var_ID]["equations"]:
                equation_variable_dictionary[eq_ID] = (
                        var_ID, self.variables[var_ID]["equations"][eq_ID])
        return equation_variable_dictionary

    def __readVariableAssignmentToEntity(self):
        _, _, all_variables = load_var_idx_eq_from_file(self.ontology_name)
        return load_entities_from_file(self.ontology_name, all_variables)

    
    def addVariable(self, ID, **args):
        self.variables[ID] = {}
        for i in args:
            self.variables[ID][i] = args[i]

    def writeVariables(self, variables, indices, ProMoIRI):
        """
        The data are assumed to be a dictionary (ordered)
        Extraction is included as a method in the Variable class
        :param data: input data
        :return:
        """
        # RULE: The file name carries also the version at least for the time being
        f_name = FILES["variables_file"] % self.ontology_name

        data = VariableFile(variables, indices,
                            VARIABLE_EQUATIONS_VERSION, self.ProMoIRI)

        # NOTE: every saving generates a backup file -- enables scrolling back
        saveWithBackup(data, f_name)
        # putData(data, f_name)

        # Also write variables to text file in same directory
        try:
            # Extract directory from f_name and create text file path
            import os
            file_dir = os.path.dirname(f_name)
            if file_dir:
                variables_text_path = os.path.join(file_dir, "variables_definition_order.txt")
                equations_text_path = os.path.join(file_dir, "equations_sequence_order.txt")
            else:
                variables_text_path = "variables_definition_order.txt"
                equations_text_path = "equations_sequence_order.txt"

            self.writeVariablesToTextFile(variables, variables_text_path)

            # Also write equations to text file if equation dictionary is available
            if hasattr(self, 'equation_dictionary') and self.equation_dictionary:
                self.writeEquationsToTextFile(self.equation_dictionary, equations_text_path)

        except Exception as e:
            print(f"Warning: Failed to write variables/equations to text files: {e}")

    def readVariables(self):
        """
        main issue here is to handle the versions. For the time beigning it is to go from version 6 to version 7
        # version conversion: v6 to v7
        :return: variables
        """
        # print ("----------------------")

        variables_f_name = FILES["variables_file"] % self.ontology_name

        variable_record_dummy = makeCompleteVariableRecord(-1)

        if OS.path.exists(variables_f_name):
            data = getData(variables_f_name)

            for v_ID in data["variables"]:
                # RULE: we use a class units for their representation
                u = data["variables"][v_ID]["units"]
                data["variables"][v_ID]["units"] = Units(ALL=u)

                # selfhealing once the variable_record is modified
                # adds missing attribute
                # Note: it will not remove obsolete attributes
                key_list = list(data["variables"][v_ID].keys())
                for attrib in list(variable_record_dummy.keys()):
                    if attrib not in key_list:
                        data["variables"][v_ID][attrib] = variable_record_dummy[attrib]

            return data["variables"], data["indices"], data["version"], data["Ontology_global_IDs"]

        else:
            msg = "There is no variable file \n-- run foundation editor again and save information\n-- to generate an empty " \
                  "" \
                  "" \
                  "" \
                  "" \
                  "variable file"

            reply = QtWidgets.QMessageBox.warning(
                    QtWidgets.QWidget(), "ProMo", msg, QtWidgets.QMessageBox.Ok)
            if reply == OK:
                exit(-1)

    def writeVariablesToTextFile(self, variables, output_filename="variables_definition_order.txt"):
        """
        Write all variables to a text file in order of their definition (V_1, V_2, V_3, etc.)
        
        :param variables: Variables object (OrderedDict) or dictionary containing all variables
        :param output_filename: Name of the output file
        """
        try:
            # Handle both Variables object and plain dictionary
            if hasattr(variables, 'keys'):
                # Variables object (OrderedDict) - use .keys() directly
                var_ids = variables.keys()
            else:
                # Plain dictionary - use .keys()
                var_ids = variables.keys()

            # Get all variable IDs and sort them numerically
            variable_ids = []
            for var_id in var_ids:
                # Extract the numeric part from V_N format
                if var_id.startswith("V_"):
                    try:
                        num = int(var_id[2:])
                        variable_ids.append((num, var_id))
                    except ValueError:
                        # Handle cases where the suffix might not be a simple number
                        variable_ids.append((float('inf'), var_id))

            # Sort by the numeric part
            variable_ids.sort()

            # Write to file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write("List of Variables in Definition Order\n")
                f.write("=" * 50 + "\n\n")

                for num, var_id in variable_ids:
                    # Get variable object - handle both formats
                    if hasattr(variables, 'get'):
                        var = variables.get(var_id, {})
                    else:
                        var = variables.get(var_id, {})

                    f.write(f"Variable ID: {var_id}\n")
                    f.write(f"  Label: {var.get('label', 'N/A')}\n")
                    f.write(f"  Type: {var.get('type', 'N/A')}\n")
                    f.write(f"  Network: {var.get('network', 'N/A')}\n")
                    f.write(f"  Documentation: {var.get('doc', 'N/A')}\n")

                    # Write units if available
                    if var.get('units'):
                        f.write(f"  Units: {var['units']}\n")

                    # Write equations if available
                    equations = var.get('equations', {})
                    if equations:
                        f.write(f"  Equations: {list(equations.keys())}\n")

                    f.write("\n")

            print(f"Successfully wrote {len(variable_ids)} variables to {output_filename}")
            return True

        except Exception as e:
            print(f"Error writing variables to file: {e}")
            return False

    def writeEquationsToTextFile(self, equation_dictionary, output_filename="equations_sequence_order.txt"):
        """
        Write all equations to a text file in proper sequence order
        
        :param equation_dictionary: Dictionary containing all equations
        :param output_filename: Name of the output file
        """
        try:
            # Get all equation IDs and sort them numerically
            equation_ids = []
            for eq_id in equation_dictionary.keys():
                # Extract the numeric part from E_N format
                if eq_id.startswith("E_"):
                    try:
                        num = int(eq_id[2:])
                        equation_ids.append((num, eq_id))
                    except ValueError:
                        # Handle cases where the suffix might not be a simple number
                        equation_ids.append((float('inf'), eq_id))

            # Sort by the numeric part for proper sequence
            equation_ids.sort()

            # Write to file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write("List of Equations in Sequence Order\n")
                f.write("=" * 50 + "\n\n")

                for num, eq_id in equation_ids:
                    eq = equation_dictionary[eq_id]
                    f.write(f"Equation ID: {eq_id}\n")

                    # Write equation details
                    if isinstance(eq, dict):
                        f.write(f"  Type: {eq.get('type', 'N/A')}\n")
                        f.write(f"  Network: {eq.get('network', 'N/A')}\n")

                        # Write RHS if available
                        if 'rhs' in eq:
                            rhs = eq['rhs']
                            if isinstance(rhs, dict):
                                f.write(f"  RHS Global ID: {rhs.get('global_ID', 'N/A')}\n")
                                f.write(f"  RHS Internal: {rhs.get('internal', 'N/A')}\n")
                                f.write(f"  RHS LaTeX: {rhs.get('latex', 'N/A')}\n")
                            else:
                                f.write(f"  RHS: {rhs}\n")

                        # Write documentation if available
                        if 'doc' in eq:
                            f.write(f"  Documentation: {eq['doc']}\n")

                    f.write("\n")

            print(f"Successfully wrote {len(equation_ids)} equations to {output_filename}")
            return True

        except Exception as e:
            print(f"Error writing equations to file: {e}")
            return False

    
    
    def load_node_arc_assignments(self):
        
        assignment_file_name = FILES["variable_assignment_to_entity_object"] % self.ontology_name
        if OS.path.exists(assignment_file_name):
            data = self.__load_variable_assignment_file(assignment_file_name)
            return data
        else:
            return None

    def __load_variable_assignment_file(self, file_name):
        data = getData(file_name)

        # Clean up var_eq_forest data to handle JSON serialization issues
        if data:
            for entity_key, entity_data in data.items():
                if 'var_eq_forest' in entity_data:
                    cleaned_forest = []
                    for tree in entity_data['var_eq_forest']:
                        cleaned_tree = {}
                        for key, values in tree.items():
                            # Convert lists to sets to remove duplicates, then back to lists
                            if isinstance(values, list):
                                # Remove duplicates by converting to set and back
                                cleaned_values = list(set(values))
                                cleaned_tree[key] = cleaned_values
                            else:
                                cleaned_tree[key] = values
                        cleaned_forest.append(cleaned_tree)
                    entity_data['var_eq_forest'] = cleaned_forest

        return data

    def __load_arc_options_to_file(self):
        path = FILES["arc_options"] % self.ontology_name
        data = getData(path)
        return data

    def __load_equation_png_files_for_ids(self, equation_ids):
        """Load PNG files for a specific set of equation IDs"""
        dict_equation_png = {}
        latex_folder_path = Path(DIRECTORIES["latex_doc_location"] % self.ontology_name)
        for eq_id in equation_ids:
            equ_png_file_path = latex_folder_path / (eq_id + ".png")
            if OS.path.exists(equ_png_file_path):
                dict_equation_png[eq_id] = equ_png_file_path
            else:
                # Temporarily comment out to prevent GUI interference during loading
                # makeMessageBox("no such equation png file %s"%equ_png_file_path,"OK")
                print(f"Debug: No equation PNG file found: {equ_png_file_path}")
        return dict_equation_png

    def __load_variable_png_files(self):
        dict_variable_png = {}
        latex_folder_path = Path(DIRECTORIES["latex_doc_location"] % self.ontology_name)
        for var_id in self.variables:
            var_png_file_path = latex_folder_path / (var_id + ".png")
            if OS.path.exists(var_png_file_path):
                dict_variable_png[var_id] = var_png_file_path
            else:
                # Temporarily comment out to prevent GUI interference during loading
                # makeMessageBox("no such equation png file %s"%var_png_file_path,["OK"])
                print(f"Debug: No variable PNG file found: {var_png_file_path}")
        return dict_variable_png
        pass

    def load_equation_icons(self):
        """Load equation PNG files as QIcon objects for use in dialogs"""
        from PyQt5 import QtGui, QtCore
        equation_icons = {}

        
        # Direct pixel mapping from PNG to icon, then apply simple scaling
        scale_factor = 0.5  # Scale down to 50% of original size

        for eq_id, png_path in self.list_equation_png_files.items():
            try:
                # Load PNG as QIcon in the main GUI context
                pixmap = QtGui.QPixmap(str(png_path))
                if not pixmap.isNull():
                    # Get original dimensions
                    original_width = pixmap.width()
                    original_height = pixmap.height()

                    # Direct pixel mapping: use PNG dimensions as-is, then apply simple scaling
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)

                    # Create canvas exactly at the scaled dimensions
                    canvas_width = new_width
                    canvas_height = new_height

                    # Create canvas with light background for better contrast
                    canvas = QtGui.QPixmap(canvas_width, canvas_height)
                    canvas.fill(QtGui.QColor(248, 248, 248))  # Very light gray background

                    # Paint the scaled equation centered on the canvas
                    painter = QtGui.QPainter(canvas)
                    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
                    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
                    painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

                    # Paint the scaled equation filling the entire canvas (no centering needed)
                    scaled_pixmap = pixmap.scaled(
                            new_width, new_height,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                            )
                    painter.drawPixmap(0, 0, scaled_pixmap)
                    painter.end()

                    icon = QtGui.QIcon(canvas)
                    if not icon.isNull():
                        equation_icons[eq_id] = icon
                    else:
                        print(f"⚠ Equation icon is null for {eq_id}")
                else:
                    print(f"⚠ Equation pixmap is null for {eq_id}")

            except Exception as e:
                print(f"✗ Error loading equation icon for {eq_id}: {e}")

        return equation_icons

    def load_variable_icons(self):
        """Load variable PNG files as QIcon objects for use in dialogs"""
        from PyQt5 import QtGui, QtCore
        variable_icons = {}

        
        # Direct pixel mapping from PNG to icon, then apply simple scaling
        scale_factor = 1.0  # No scaling - use original size since we're making lines wider instead

        for var_id, png_path in self.list_variable_png_files.items():
            try:
                # Load PNG as QIcon in the main GUI context
                pixmap = QtGui.QPixmap(str(png_path))
                if not pixmap.isNull():
                    # Get original dimensions
                    original_width = pixmap.width()
                    original_height = pixmap.height()

                    # Direct pixel mapping: use PNG dimensions as-is, then apply simple scaling
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)

                    # Create canvas exactly at the scaled dimensions
                    canvas_width = new_width
                    canvas_height = new_height

                    # Create canvas with transparent background
                    canvas = QtGui.QPixmap(canvas_width, canvas_height)
                    canvas.fill(QtCore.Qt.transparent)

                    # Paint the scaled variable and center it in the canvas
                    scaled_pixmap = pixmap.scaled(
                            new_width, new_height,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                            )
                    painter = QtGui.QPainter(canvas)
                    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
                    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
                    painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

                    # Center the scaled pixmap in the canvas
                    x_offset = (canvas_width - scaled_pixmap.width()) // 2
                    y_offset = (canvas_height - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
                    painter.end()

                    icon = QtGui.QIcon(canvas)
                    if not icon.isNull():
                        variable_icons[var_id] = icon
                    else:
                        print(f"⚠ Variable icon is null for {var_id}")
                else:
                    print(f"⚠ Variable pixmap is null for {var_id}")

            except Exception as e:
                print(f"✗ Error loading variable icon for {var_id}: {e}")

        return variable_icons

    def filter_variables_by_type(
            self,
            variables: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]],
            allowed_types: List[str],
            exclude_types: Optional[List[str]] = None
            ) -> List[Union[Dict[str, Any], str]]:
        """
        Filter variables by allowed and excluded types.
        
        Args:
            variables: List of variable dictionaries or dict of variable dictionaries
            allowed_types: List of variable types to include
            exclude_types: List of variable types to exclude (optional)
            
        Returns:
            List of filtered variables (dicts if input was list, IDs if input was dict)
        """
        exclude_types = exclude_types or []

        if isinstance(variables, dict):
            # Return list of variable IDs
            filtered_ids = []
            for var_id, var_data in variables.items():
                var_type = var_data.get('type', 'unknown')
                if var_type in allowed_types and var_type not in exclude_types:
                    filtered_ids.append(var_id)
            return filtered_ids
        else:
            # Return list of variable dictionaries
            filtered = []
            for var in variables:
                var_type = var.get('type', 'unknown')
                if var_type in allowed_types and var_type not in exclude_types:
                    filtered.append(var)
            return filtered

    def filter_transport_variables(
            self,
            variables: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
            ) -> List[Union[Dict[str, Any], str]]:
        """Filter out transport variables."""
        return self.filter_variables_by_type(variables, [], ['transport'])

    def filter_only_transport(
            self,
            variables: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
            ) -> List[Union[Dict[str, Any], str]]:
        """Filter for only transport variables."""
        return self.filter_variables_by_type(variables, ['transport'])

    def filter_variables_by_network(
            self,
            variables: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]],
            networks: List[str]
            ) -> List[Union[Dict[str, Any], str]]:
        """
        Filter variables by network(s).
        
        Args:
            variables: List of variable dictionaries or dict of variable dictionaries
            networks: List of network names to include
            
        Returns:
            List of filtered variables
        """
        if isinstance(variables, dict):
            # Return list of variable IDs
            filtered_ids = []
            for var_id, var_data in variables.items():
                var_network = var_data.get('network', '')
                if var_network in networks:
                    filtered_ids.append(var_id)
            return filtered_ids
        else:
            # Return list of variable dictionaries
            filtered = []
            for var in variables:
                var_network = var.get('network', '')
                if var_network in networks:
                    filtered.append(var)
            return filtered

    def filter_variables_by_component(
            self,
            variables: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]],
            component: str
            ) -> List[Union[Dict[str, Any], str]]:
        """
        Filter variables by component type using ontology rules.
        
        Args:
            variables: List of variable dictionaries or dict of variable dictionaries
            component: Component type ('node', 'arc', 'graph')
            
        Returns:
            List of filtered variables
        """
        # Get variable types allowed for this component across all networks
        allowed_var_types = set()
        for network in self.variable_types_on_networks_per_component:
            if component in self.variable_types_on_networks_per_component[network]:
                allowed_var_types.update(self.variable_types_on_networks_per_component[network][component])

        if isinstance(variables, dict):
            # Return list of variable IDs
            filtered_ids = []
            for var_id, var_data in variables.items():
                var_type = var_data.get('type', '')
                if var_type in allowed_var_types:
                    filtered_ids.append(var_id)
            return filtered_ids
        else:
            # Return list of variable dictionaries
            filtered = []
            for var in variables:
                var_type = var.get('type', '')
                if var_type in allowed_var_types:
                    filtered.append(var)
            return filtered

    def get_variables_for_interface(
            self,
            interface_network: str
            ) -> List[str]:
        """
        Get variables applicable to a specific interface.
        
        Args:
            interface_network: Interface network name
            
        Returns:
            List of variable IDs for the interface
        """
        if interface_network in self.variable_types_on_interfaces:
            interface_var_types = self.variable_types_on_interfaces[interface_network]
            return self.filter_variables_by_type(self.variables, interface_var_types)
        return []

    def get_variables_for_intraface(
            self,
            intraface_network: str
            ) -> List[str]:
        """
        Get variables applicable to a specific intraface.
        
        Args:
            intraface_network: Intraface network name
            
        Returns:
            List of variable IDs for the intraface
        """
        if intraface_network in self.variable_types_on_intrafaces:
            intraface_var_types = self.variable_types_on_intrafaces[intraface_network]
            return self.filter_variables_by_type(self.variables, intraface_var_types)
        return []

    # Convenience methods for Entity class compatibility
    def get_output_variables_filtered(
            self,
            entity_variable_ids: List[str],
            exclude_transport: bool = True
            ) -> List[str]:
        """
        Entity-compatible method to get output variables with transport filtering.
        
        Args:
            entity_variable_ids: List of variable IDs in the entity
            exclude_transport: Whether to exclude transport variables
            
        Returns:
            List of filtered variable IDs
        """
        if not exclude_transport:
            return entity_variable_ids

        # Filter out transport variables using exchange board's variable data
        filtered_vars = []
        for var_id in entity_variable_ids:
            if var_id in self.variables:
                var_data = self.variables[var_id]
                if var_data.get('type') != 'transport':
                    filtered_vars.append(var_id)
            else:
                # Include variable if not found in exchange board (fallback)
                filtered_vars.append(var_id)

        return filtered_vars

    def get_equation_defined_variables_filtered(
            self,
            equation_defined_var_ids: List[str],
            exclude_transport: bool = True
            ) -> List[str]:
        """
        Entity-compatible method to filter equation-defined variables.
        
        Args:
            equation_defined_var_ids: List of equation-defined variable IDs
            exclude_transport: Whether to exclude transport variables
            
        Returns:
            List of filtered variable IDs
        """
        return self.get_output_variables_filtered(equation_defined_var_ids, exclude_transport)

    # Convenience methods for Behaviour Linker compatibility
    def filter_variables_for_behaviour_linker(
            self,
            entity_type_info: Dict[str, Any],
            variable_class_mode: str = 'state'
            ) -> List[Dict[str, Any]]:
        """
        Behaviour Linker compatible filtering method.
        
        Args:
            entity_type_info: Entity type information for classification rules
            variable_class_mode: Classification mode ('state', 'transport', 'intensity', 'all')
            
        Returns:
            List of filtered variable dictionaries
        """
        try:
            # Import here to avoid circular dependencies
            from OntologyBuilder.BehaviourLinker_v01.variable_classification_rules import \
                VariableClassificationRules

            # Convert variables to list of dictionaries for classification
            var_list = []
            for var_id, var_data in self.variables.items():
                try:
                    # Safely extract variable data
                    var_dict = {
                            'id'      : var_id,
                            'type'    : var_data.get('type', ''),
                            'label'   : var_data.get('label', ''),
                            'network' : var_data.get('network', ''),
                            'png_file': var_data.get('png_file'),
                            # Add other fields as needed
                            }
                    var_list.append(var_dict)
                except Exception as e:
                    print(f"Warning: Error processing variable {var_id} for filtering: {e}")
                    continue

            # Apply classification rules
            classification = VariableClassificationRules.classify_variables(var_list, entity_type_info)

            # Select appropriate classification based on mode
            if variable_class_mode == 'state':
                filtered_dicts = classification['allowed_root']
            elif variable_class_mode == 'transport':
                filtered_dicts = VariableClassificationRules.filter_variables_by_type(var_list, ['transport'])
            elif variable_class_mode == 'intensity':
                filtered_dicts = VariableClassificationRules.filter_variables_by_type(var_list,
                                                                                      ['effort', 'secondaryState'])
            elif variable_class_mode == 'all':
                # Combine all classifications, remove duplicates
                all_vars = (classification['allowed_root'] +
                            classification['inputs'] +
                            classification['outputs'])
                seen_ids = set()
                filtered_dicts = []
                for var in all_vars:
                    if var['id'] not in seen_ids:
                        seen_ids.add(var['id'])
                        filtered_dicts.append(var)
            else:
                # Default to state mode
                filtered_dicts = classification['allowed_root']

            return filtered_dicts

        except Exception as e:
            print(f"Error in filter_variables_for_behaviour_linker: {e}")
            # Return empty list as fallback
            return []

    def __add_png_paths_to_variables(self):
        """
        Add PNG file paths directly to variable records for easier access
        """
        for var_id in self.variables:
            if var_id in self.list_variable_png_files:
                png_path = str(self.list_variable_png_files[var_id])
                # Only set if the path is valid and not empty
                if png_path and png_path != 'None' and png_path.strip():
                    self.variables[var_id]["png_file"] = png_path
                else:
                    self.variables[var_id]["png_file"] = None
            else:
                self.variables[var_id]["png_file"] = None

    def writeEquationsFile(self, compiled_equations):
        """
        Write equations in input format equations file using FILES constant
        
        :compiled_equations in ProMo's input language
        """
        try:
            # Get the equation file name using FILES constant
            e_name = FILES["coded_equations"] % (self.ontology_location, "input_language")
            e_name = e_name.replace(".json", ".txt")

            equations = compiled_equations

            # Sort equation IDs numerically for proper sequence (E_1, E_2, E_3, etc.)
            equation_ids = []
            for equ_ID in equations.keys():
                if equ_ID.startswith("E_"):
                    try:
                        num = int(equ_ID[2:])
                        equation_ids.append((num, equ_ID))
                    except ValueError:
                        equation_ids.append((float('inf'), equ_ID))
                else:
                    equation_ids.append((float('inf'), equ_ID))

            # Sort numerically
            equation_ids.sort()

            # Write equations in proper numerical order
            with open(e_name, 'w') as f:
                for num, equ_ID in equation_ids:
                    if equ_ID in equations:
                        e = equations[equ_ID]
                        f.write("\n%s - %s - %s ::\n%s = %s\n" % (equ_ID, e["network"], e["type"], e["lhs"], e["rhs"]))

            print(f"Successfully wrote {len(equation_ids)} equations to {e_name}")
            return True

        except Exception as e:
            print(f"Error writing equations to file: {e}")
            return False
