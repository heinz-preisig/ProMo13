import json
import os
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from Common.classes.entity import Entity
# from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
# from BricksAndTreeSemantics import PRIMITIVES
# from OntologyBuilder.BehaviourLinker_v01.BricksAndTreeSemantics import RULES
# from DataModelNoBrickNumbers import DataModel
# from OntologyBuilder.BehaviourLinker_v01.main_automaton import UI_state
# from Utilities import TreePlot
# from Utilities import camelCase
# from Utilities import debugging
from Common.common_resources import getOntologyName
from Common.ontology_container import OntologyContainer
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES

TIMING = False
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])


class BehaviourLinerBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def process_message(self, message):
        print(">>got message: ", message)

        if message.get("event") == "start":
            print("Backend received start event")

    def send_message(self, message):
        self.message.emit(message)

    def load_ontology(self):
        self.ontology_name = getOntologyName(task="task_entity_generation")
        if not self.ontology_name:
            exit(-1)
        self.send_message({"event": "ontology_loaded", "ontology_name": self.ontology_name})
        # get ontology
        self.ontology_location = DIRECTORIES["ontology_location"] % str(self.ontology_name)
        self.ontology_container = OntologyContainer(self.ontology_name)

        # self.variable_types_on_networks = self.ontology_container.variable_types_on_networks
        # self.converting_tokens = self.ontology_container.converting_tokens
        #
        # self.rules = self.ontology_container.rules
        self.ontology_tree = self.ontology_container.ontology_tree
        self.ontology_hierarchy = self.ontology_container.ontology_hierarchy
        self.networks = self.ontology_container.networks
        self.interconnection_nws = self.ontology_container.interconnection_network_dictionary
        self.intraconnection_nws = self.ontology_container.intraconnection_network_dictionary
        self.intraconnection_nws_list = list(self.intraconnection_nws.keys())
        self.interconnection_nws_list = self.ontology_container.interconnection_nws_list

        self.indices = self.ontology_container.indices
        self.variables = self.ontology_container.variables  # Variables(self.ontology_container)
        # link the indices for compilation
        # self.variables.importVariables(
        #         self.ontology_container.variables, self.indices)

        self.initial_variable_list = sorted(self.variables.keys())
        self.initial_equation_list = sorted(self.ontology_container.equation_dictionary.keys())
        # all possible entity types
        self.node_entity_types = self.ontology_container.node_entity_types
        self.arc_entity_types = self.ontology_container.list_arc_objects

        # load all instances
        self.all_entities = self.load_intities_from_file(self.ontology_name)
        pass

        # def load_entities_from_file(  #TODO: do we need the interface entityies?
        #         ontology_name: str,
        #         all_equations: dict[str, equation.Equation],
        #         entity_names: list[str] | None = None,
        #         ) -> dict[str, entity.Entity]:
    #     def generate_entity_types_for_network(self, network_type):
    #         """
    #         Generate entity types for a specific network type, organized by node and arc categories.
    #
    #         Args:
    #             network_type: The type of network to generate entity types for
    #
    #         Returns:
    #             dict: Dictionary with 'node' and 'arc' keys, each containing a list of entity types
    #         """
    #         # Default empty result
    #         result = {'node': [], 'arc': []}
    #
    #         # If no ontology is loaded, return empty result
    #         if not hasattr(self, 'ontology') or not self.ontology:
    #             return result
    #
    #         try:
    #             # Get the network info from the ontology
    #             network_info = self.ontology.tree.get(network_type, {})
    #             structure = network_info.get('structure', {})
    #
    #             # Process node types
    #             node_types = structure.get('node', {})
    #             dynamics = list(node_types.keys())
    #             natures = list(node_types.values())
    #             token_types = structure.get('token', {})
    #
    #             all_tokens = list(token_types.keys())
    #
    #             # Generate all token combinations
    #             token_combinations = self.generate_token_combinations(all_tokens)
    #
    #             # Process node types with all token combinations
    #             for token_combo in token_combinations:
    #                 # result['node'].append(token_combo)
    #
    #                 for dynamics, natures in node_types.items():
    #                     for nature in natures:
    #                         result['node'].append(f"{token_combo}|{dynamics}|{nature}")
    #                     # if not natures:
    #                     #   result['node'].append(f"{dynamics}|{nature}")
    #                     #   continue
    #                     #
    #                     # for nature in natures:
    #                     #   if not token_combinations:  # If no token combinations
    #                     #     result['node'].append(f"{dynamics}|{nature}")
    #                     #   else:
    #                     #     # Add all token combinations to the node type
    #                     #     for token_combo in token_combinations:
    #                     #       result['node'].append(f"{dynamics}|{nature}|{token_combo}")
    #
    #             # Process arc types
    #             arc_types = structure.get('arc', {})
    #             for arc_type, arc_mechs in arc_types.items():
    #                 for mech, sub_mechs in arc_mechs.items():
    #                     if not sub_mechs:  # If no sub-mechanisms
    #                         result['arc'].append(f"{arc_type}|{mech}")
    #                     else:
    #                         for sub_mech in sub_mechs:
    #                             result['arc'].append(f"{arc_type}|{mech}|{sub_mech}")
    #
    #             # Remove duplicates and sort
    #             result['node'] = sorted(list(set(result['node'])))
    #             result['arc'] = sorted(list(set(result['arc'])))
    #
    #             return result
    #
    #         except Exception as e:
    #             print(f"Error generating entity types for {network_type}: {e}")
    #             return {'node': [], 'arc': []}
    #
    #
    #
    # def generate_entity_types_for_network(self, network_type):
    #     """
    #     Generate entity types for a specific network type, organized by node and arc categories.
    #
    #     Args:
    #         network_type: The type of network to generate entity types for
    #
    #     Returns:
    #         dict: Dictionary with 'node' and 'arc' keys, each containing a list of entity types
    #     """
    #     # Default empty result
    #     result = {'node': [], 'arc': []}
    #
    #     # # If no ontology is loaded, return empty result
    #     # if not hasattr(self, 'ontology') or not self.ontology:
    #     #     return result
    #
    #     onto_tree = self.ontology_container.ontology_tree
    #     tokens_nw = self.ontology_container.tokens_on_networks
    #     inter_branches = self.ontology_container.list_inter_branches
    #     node_types_red = self.ontology_container.list_network_node_objects
    #     arc_types = self.ontology_container.list_network_arc_objects
    #     # for nw in inter_branches:
    #     #     token_combinations = "_".joint tokens_nw[nw]
    #     #     for node_arc in ["node", "arc"]:
    #
    #         # try:
    #         #     # Get the network info from the ontology
    #         #     network_info = self.ontology.tree.get(network_type, {})
    #         #     structure = network_info.get('structure', {})
    #         #
    #         #     # Process node types
    #         #     node_types = structure.get('node', {})
    #         #     dynamics = list(node_types.keys())
    #         #     natures = list(node_types.values())
    #         #     token_types = structure.get('token', {})
    #         #
    #         #     all_tokens = list(token_types.keys())
    #         #
    #         #     # Generate all token combinations
    #         #     token_combinations = self.generate_token_combinations(all_tokens)
    #         #
    #         #     # Process node types with all token combinations
    #         #     for token_combo in token_combinations:
    #         #         # result['node'].append(token_combo)
    #         #
    #         #         for dynamics, natures in node_types.items():
    #         #             for nature in natures:
    #         #                 result['node'].append(f"{token_combo}|{dynamics}|{nature}")
    #         #             # if not natures:
    #         #             #   result['node'].append(f"{dynamics}|{nature}")
    #         #             #   continue
    #         #             #
    #         #             # for nature in natures:
    #         #             #   if not token_combinations:  # If no token combinations
    #         #             #     result['node'].append(f"{dynamics}|{nature}")
    #         #             #   else:
    #         #             #     # Add all token combinations to the node type
    #         #             #     for token_combo in token_combinations:
    #         #             #       result['node'].append(f"{dynamics}|{nature}|{token_combo}")
    #         #
    #         #     # Process arc types
    #         #     arc_types = structure.get('arc', {})
    #         #     for arc_type, arc_mechs in arc_types.items():
    #         #         for mech, sub_mechs in arc_mechs.items():
    #         #             if not sub_mechs:  # If no sub-mechanisms
    #         #                 result['arc'].append(f"{arc_type}|{mech}")
    #         #             else:
    #         #                 for sub_mech in sub_mechs:
    #         #                     result['arc'].append(f"{arc_type}|{mech}|{sub_mech}")
    #         #
    #         #     # Remove duplicates and sort
    #         #     result['node'] = sorted(list(set(result['node'])))
    #         #     result['arc'] = sorted(list(set(result['arc'])))
    #
    #     return result
    #
    #     # except Exception as e:
    #     # print(f"Error generating entity types for {network_type}: {e}")
    #     # return {'node': [], 'arc': []}


    def load_intities_from_file(self, ontology_name):
    # """Loads data from file to create Entity objects.

    # Args:
    #     path (str): Path to the entity file.
    #     all_equations (Dict[str, equation.Equation]): All the equations
    #         in the Ontology. The keys are equation ids and the values are
    #         Equation objects.
    #     entity_names (list[str]): Names of the entities that will be
    #     loaded. If **None** all entities are loaded. Defaults to **None**.

    # Returns:
    #     list[Entity]: Contains instances of Entity with data loaded from
    #       the specified file.

    # Args:
    #     ontology_name (str): Name of the ontology.
    #     all_equations (Dict[str, equation.Equation]): Data of all
    #       equations. The keys are the equation ids and the corresponding
    #       values are Equation objects.
    #     entity_names (Optional[List[str]], optional): Names of the
    #       entities that will be loaded. If **None** all entities are
    #       loaded. Defaults to **None**.

    # Returns:
    #     Dict[str, entity.Entity]: Data of the entities. The keys are
    #       the names of the entities and the corresponding values are
    #       Entity objects.
    # """
        path = (
                FILES["variable_assignment_to_entity_object"]
                % ontology_name
        )

    # TODO: This file needs to be created empty when the ontology is
    # created. In here should be only an exception in case the file is not found.

    # # If the file doesnt exists it creates a new one
    # if not os.path.isfile(path):
    #   with open(path, "w", encoding="utf-8",) as file:
    #     json.dump({}, file, indent=4)
    #   return {}

        with open(
                path,
                encoding="utf-8",
                ) as file:
            data = json.load(file)
    # from pprint import pprint as pp
    # pp(data)
    # TODO Change behaviour in case of no data.
        if not data:
            return {}

        # if entity_names is None:
        #   entity_names = data.keys()
        entity_names = data.keys()

        entities = {}
        for ent_name in entity_names:
            if ent_name not in data:
                print(ent_name + " not found.")
                continue

            all_equations = {}   # TODO: load all equations
            new_entity = Entity(
                    ent_name,
                    all_equations,
                    data[ent_name]["index_set"],
                    data[ent_name]["integrators"],
                    data[ent_name]["var_eq_forest"],
                    data[ent_name]["init_vars"],
                    data[ent_name]["input_vars"],
                    data[ent_name]["output_vars"],
                    )
            # TODO Check why it cant be stored as base#
            if "base_" in ent_name:
                ent_name = ent_name.replace("base_", "base#")

            entities[ent_name] = new_entity

        return entities
#   self.memory = {
#           "brick"            : None,
#           "item"             : None,
#           "tree schema"      : None,
#           "tree instantiated": None,
#           "new tree"         : False
#           }
#
#   self.state = "start"
#   self.previousEvent = "start"
#
#   self.UI_state = UI_state
#
#   self.frontEnd = frontEnd
#   self.rules = RULES
#   # self.frontEnd.setRules(RULES, PRIMITIVES)
#   self.primitive_counter = 0
#
#   self.project_name = None
#   self.dataModel = None
#
# def processEvent(self, message):
#   if TIMING: start = time.time()
#   # debugging(">>>> message ", message)
#   event = message["event"]
#   # self.fail = False
#   for a in self.UI_state[event]["action"]:
#     if a == "addItem":
#       self.addItem(message)
#     elif a == "addLink":
#       self.addLink(message)
#     elif a == "copyTree":
#       self.copyTree(message)
#     elif a == "deleteTree":
#       self.deleteTree(message)
#     elif a == "extractInstance":
#       self.extractInstance(message)
#     elif a == "showTree":
#       self.showTree(message)
#     elif a == "instantiatePrimitive":
#       self.instantiatePrimitive(message)
#     elif a == "loadOntology":  #
#       self.loadOntology(message)
#     elif a == "markChanged":
#       self.markChanged(message)
#     elif a == "newTree":
#       self.newTree(message)
#     elif a == "putBricksListForTree":
#       self.putBricksListForTree(message)
#     elif a == "putTreeList":
#       self.putTreeList(message)
#     elif a == "removeItem":
#       self.removeItem(message)
#     # elif a == "renameItem":
#     #   self.renameItem(message)
#     elif a == "saveTreeWithNewName":
#       self.saveTreeWithNewName(message)
#     elif a == "renameTree":
#       self.renameTree(message)
#     elif a == "saveTrees":
#       self.saveTrees(message)
#     elif a == "visualise":
#       self.visualise(message)
#     elif a == "visualise_ontology_only":
#       self.visualise(message)
#     else:
#       print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> oops no such command", a)
#
#   if len(self.UI_state[event]["show"]) > 0:
#     if self.UI_state[event]["show"][0] == "do_nothing":
#       return
#   ui_state = self.UI_state[event]
#   # self.frontEnd.setInterface(ui_state["show"])
#   self.previousEvent = event
#
#   self.memory.update(message)
#   if TIMING: print("processing time", time.time() - start)
#
# def loadOntology(self, message):
#   name = message["project_name"]
#   self.ontology_name = getOntologyName(task="task_ontology_equations")
#   if not self.ontology_name:
#     exit(-1)
#   self.project_name = name
#   self.dataModel = DataModel(name)
#   self.dataModel.loadFromFile()
#   pass
#
# def markChanged(self, message):
#   self.frontEnd.markChanged()
#
# def saveTreeWithNewName(self, message):
#   project_name = message["project_name"]
#   self.dataModel.saveBricksTreesAndInstances(project_name)
#   self.project_name = project_name
#
# def copyTree(self, message):
#   """
#   copy a tree with a new name
#   """
#   tree_to_be_copied_name = self.memory["tree_name"]
#   tree_name = message["tree_name"]
#   self.dataModel.copyTree(tree_to_be_copied_name, tree_name)
#   self.memory["tree_name"] = tree_name
#   pass
#
# def addItem(self, message):
#   tree_item_name = self.memory["tree_item_name"]
#   item_name = camelCase(message["item_name"])
#   item_name_with_number = self.__getNameWithBrickNumber(item_name, tree_item_name)
#   tree_name = self.memory["tree_name"]
#   self.dataModel.addItemToTree(tree_name,
#                                tree_item_name,
#                                item_name_with_number)
#   pass
#
# def __getNameWithBrickNumber(self, item_name, tree_item_name):
#   if "_" in tree_item_name:
#     no, _ = tree_item_name.split("_")
#     item_name_ = "%s_" % no + item_name
#   else:
#     item_name_ = item_name
#   return item_name_
#
# def removeItem(self, message):
#   # tree_item_name = self.memory["tree_item_name"]
#   item_name = message["item_name"]
#   parent_name = message["parent_name"]
#   tree_name = self.memory["tree_name"]
#   self.dataModel.removeItem("trees", tree_name, parent_name, item_name)
#   pass
#
# def instantiatePrimitive(self, message):
#   pass
#   tree_name = self.memory["tree_name"]
#   primitive_type = message["type"]
#   value = message["value"]
#   self.dataModel.modifyPrimitiveValue(tree_name, primitive_type, value)
#
#   pass
#
# def addLink(self, message):
#   # check for no name in the brick is already in the path
#
#   link_position = self.memory["tree_item_name"]
#   path = message["path"]
#   brick_name = message["brick_name"]
#   brick_names = self.dataModel.getAllNamesInABrickOrATree(brick_name, "brick")
#   for name in brick_names:
#     if name in path:
#       makeMessageBox("the name %s is defined in the brick and the path -- link is not allowed" % name)
#       return
#   if link_position:
#     if not brick_name:
#       return
#
#     tree_name = self.memory["tree_name"]
#     self.dataModel.linkBrickToItem(tree_name,
#                                    link_position,
#                                    brick_name)
#
# def saveTrees(self, message):
#   self.dataModel.saveBricksTreesAndInstances(self.project_name)
#   self.frontEnd.markSaved()
#
# def extractInstance(self, message):
#   tree_name = self.memory["tree_name"]
#   self.dataModel.reduceGraph(tree_name)
#
# def putTreeList(self, message):
#   tree_list = self.dataModel.getTreeList()
#   self.frontEnd.putTreeList(tree_list)
#
# # def rememberTreeSelection(self, message):
# #   self.memory["tree_name"] = message["tree_name"]
#
# def showTree(self, message):
#   if TIMING: start = time.time()
#   try:
#     tree_name = message["tree_name"]
#   except:
#     tree_name = self.memory["tree_name"]
#   if TIMING: print("getting tuples", time.time() - start)
#   instances = self.dataModel.instances
#
#   paths, properties, leaves = self.dataModel.getTreePaths(tree_name)
#
#   # graph, root = self.dataModel.getGraph(tree_name, "tree_name")
#   # self.frontEnd.showNewTreeTree(graph, root, instances)
#   props = self.dataModel.getTreeItemProperties(tree_name)
#   self.frontEnd.showNewNewTreeTree(tree_name, paths, props, leaves, instances)
#   pass
#
#   # ======================== trees
#
# def newTree(self, message):
#   brick_name = message["brick_name"]
#   tree_name = message["tree_name"]
#   self.dataModel.newTree(tree_name, brick_name)
#
# def renameTree(self, message):
#   old_name = self.memory["tree_name"]
#   new_name = message["tree_name"]
#   self.dataModel.renameTree(old_name, new_name)
#   pass
#
# def deleteTree(self, message):
#   tree_name = self.memory["tree_name"]
#   self.dataModel.deleteTree(tree_name)
#
# def putBricksListForTree(self, message):
#   brick_list = self.dataModel.getBrickList()
#   self.frontEnd.putBricksListForTree(brick_list)
#
# def visualise(self, message):
#   tree = self.memory["tree_name"]
#   with_no_instances = message["with_no_instances"]
#   # print("with instances:", with_no_instances)
#   dataBrickTuples = self.dataModel.makeDataTuplesForGraph(tree,
#                                                           "tree_name")
#   class_names = [tree]  # sorted(self.dataModel.BRICK_GRAPHS.keys())
#   graph = TreePlot(graph_name=tree, graph_triples=dataBrickTuples, class_names=class_names, no_instances=with_no_instances)
#   graph.makeMe(tree)
#   file_name_bricks = os.path.join(ONTOLOGY_REPOSITORY, self.project_name) + "+%s_tree" % tree
#
#   graph.dot.render(file_name_bricks, format="pdf")
#   os.remove(file_name_bricks)
#
#   path = file_name_bricks + ".pdf"
#   if os.path.exists("/.dockerenv"):
#     subprocess.Popen(['evince', str(path)])
#     # subprocess.Popen(['okular', str(path)])
#     # subprocess.Popen(['qpdfview --unique', str(path)])
#     # makeMessageBox("cannot display pdf-file, open it locally", buttons=["OK"])
#   elif sys.platform.startswith('linux'):
#     subprocess.Popen(['xdg-open', str(path)])
#   elif sys.platform.startswith('win32'):
#     subprocess.Popen(['start', str(path)], shell=True)
#   pass
