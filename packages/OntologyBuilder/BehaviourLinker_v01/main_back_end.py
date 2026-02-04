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
from Common.exchange_board import ProMoExchangeBoard
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from OntologyBuilder.BehaviourLinker_v01.entity_back_end import EntityEditorBackEnd
from OntologyBuilder.BehaviourLinker_v01.entity_front_end import EntityEditorFrontEnd
from OntologyBuilder.BehaviourLinker_v01.main_automaton import gui_automaton

TIMING = False
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])


# from OntologyBuilder.BehaviourLinker_v01.entity_back_end import


class BehaviourLinerBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def process_message(self, message):
        print(">>got message: ", message)
        event = message.get("event")

        # action
        if event == "failed":
            pass
        elif event == "selected_entity_type":
            self.entity_type = message.get("data", None)
            print(" got a selected entity type", self.entity_type)
        elif event == "new":
            self.launch_entity_editor(self.ontology_container)


        self.send_message(event)

    def send_message(self, event, data=None):
        message = {"event": event, "interface": gui_automaton[event], "data": data}
        self.message.emit(message)

    def handle_entity_editor_message(self, message):
        """Handle messages from the entity editor"""
        if message.get("event") == "entity_created":
            # Handle new entity from entity editor (legacy)
            self.add_entity(message.get("entity_data"))
        elif message.get("event") == "behavior_association_defined":
            # Handle behavior association from BehaviorAssociation editor (legacy)
            self.handle_behavior_association(message.get("assignments"))
        elif message.get("event") == "entity_data_ready":
            # Handle new entity data with equation selection
            self.process_entity_data(message.get("entity_data"))
        elif message.get("event") == "entity_created_successfully":
            # Handle successful entity creation
            print("Entity created successfully")
            self.send_message("entity_creation_complete")
        elif message.get("event") == "error":
            # Handle errors from entity editor
            error_msg = message.get("error", "Unknown error")
            print(f"Entity editor error: {error_msg}")
            self.send_message("error", {"error": error_msg})
    
    def process_entity_data(self, entity_data):
        """Process the entity data with equation selection"""
        try:
            if not entity_data:
                print("No entity data provided")
                return
            
            root_variable = entity_data.get('root_variable')
            definition_method = entity_data.get('definition_method')
            
            print(f"Processing entity for variable: {root_variable}")
            print(f"Definition method: {definition_method}")
            
            if definition_method == 'initialization':
                init_value = entity_data.get('initialization_value')
                print(f"Variable will be initialized with: {init_value}")
            else:
                equation_id = entity_data.get('equation_id')
                print(f"Variable will be defined by equation: {equation_id}")
            
            # Here you would typically:
            # 1. Create the Entity object with the selected definition
            # 2. Add it to the entity list
            # 3. Update the tree view
            # 4. Save to file
            
            # For now, just acknowledge and show a success message
            print("Entity data processed successfully")
            
        except Exception as e:
            print(f"Error processing entity data: {e}")
            self.send_message("error", {"error": str(e)})

    def handle_behavior_association(self, assignments):
        """Handle the behavior association assignments from the editor"""
        try:
            if assignments:
                print(f"Received behavior association: {assignments}")

                # Here you can process the assignments as needed
                # For example, save them to the entity file or update the entity data

                # For now, just acknowledge receipt
                self.send_message({
                        "event"      : "behavior_association_processed",
                        "status"     : "success",
                        "assignments": assignments
                        })
            else:
                print("No behavior association assignments received")

        except Exception as e:
            print(f"Error handling behavior association: {e}")
            self.send_message({
                    "event" : "behavior_association_processed",
                    "status": "error",
                    "error" : str(e)
                    })

    def load_ontology(self):
        self.ontology_name = getOntologyName(task="task_entity_generation")
        if not self.ontology_name:
            exit(-1)
        self.send_message("start")
        # get ontology
        self.ontology_location = DIRECTORIES["ontology_location"] % str(self.ontology_name)
        self.ontology_container = ProMoExchangeBoard(self.ontology_name)

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
        self.all_entities = self.load_entities_from_file(self.ontology_name)

        self.send_message(event="make_tree", data={
            "node_entity_types": self.node_entity_types,
            "all_entities": self.all_entities
        })
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

    def load_entities_from_file(self, ontology_name):
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

            all_equations = {}  # TODO: load all equations
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

    def launch_entity_editor(self, ontology_container):
        # Create entity components
        self.entity_back_end = EntityEditorBackEnd(self.ontology_container)
        self.entity_front_end = EntityEditorFrontEnd()

        # Connect entity editor communication
        self.entity_front_end.message.connect(self.entity_back_end.process_message)
        self.entity_back_end.message.connect(self.handle_entity_editor_message)

        # Pass ontology container to entity front end for behavior association
        self.entity_front_end.set_ontology_container(self.ontology_container)

        # Show editor
        self.entity_front_end.show()
