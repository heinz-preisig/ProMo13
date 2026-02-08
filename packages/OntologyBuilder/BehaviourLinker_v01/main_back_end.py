import json
import os
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from Common.classes.entity import Entity
from Common.common_resources import getOntologyName
from Common.exchange_board import ProMoExchangeBoard
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from OntologyBuilder.BehaviourLinker_v01.entity_back_end import EntityEditorBackEnd
from OntologyBuilder.BehaviourLinker_v01.entity_front_end import EntityEditorFrontEnd
from OntologyBuilder.BehaviourLinker_v01.main_automaton import gui_automaton


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])



class BehaviourLinerBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def process_main_frontend_message(self, message):
        print(">>got message: ", message)
        event = message.get("event")

        # action
        if event == "failed":
            pass
        elif event == "selected_entity_type":
            self.entity_type = message.get("data", None)
            print(" got a selected entity type", self.entity_type)
            # Automatically launch entity editor for entity type selection (create mode)
            self.launch_entity_editor(mode="create")
        elif event == "selected_instance":
            self.entity_type = message.get("data", None)
            print(" got a selected entity instance", self.entity_type)
            # Automatically launch entity editor for instance selection (edit mode)
            self.launch_entity_editor(mode="edit")


        self.send_message_to_main_frontend(event)

    def send_message_to_main_frontend(self, event, data=None):
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
            self.send_message_to_main_frontend("entity_creation_complete")
        elif message.get("event") == "error":
            # Handle errors from entity editor
            error_msg = message.get("error", "Unknown error")
            print(f"Entity editor error: {error_msg}")
            self.send_message_to_main_frontend("error", {"error": error_msg})
    
    def process_entity_data(self, entity_data):
        """Process the entity data with equation selection and update frontend"""
        try:
            if not entity_data:
                print("No entity data provided")
                return
            
            root_variable = entity_data.get('root_variable')
            definition_method = entity_data.get('definition_method')
            
            print(f"Processing entity for variable: {root_variable}")
            print(f"Definition method: {definition_method}")
            
            if definition_method == 'initialization':
                print(f"Variable will be marked for initialization")
            else:
                equation_id = entity_data.get('equation_id')
                print(f"Variable will be defined by equation: {equation_id}")
            
            # Get the Entity object if available
            entity = entity_data.get('entity_object')
            if entity:
                print(f"Found Entity object: {entity.entity_name}")
                print(f"Entity var_eq_forest: {entity.var_eq_forest}")
                print(f"Entity output_vars: {entity.output_vars}")
                print(f"Entity input_vars: {entity.input_vars}")
                print(f"Entity init_vars: {entity.init_vars}")
                
                # Update the entity editor frontend with the Entity information
                self.update_entity_editor_frontend(entity)
            else:
                print("No Entity object found in entity_data")
            
            print("Entity data processed successfully")
            
        except Exception as e:
            print(f"Error processing entity data: {e}")
            self.send_message_to_main_frontend("error", {"error": str(e)})
    
    def update_entity_editor_frontend(self, entity):
        """Update the entity editor frontend with Entity object information"""
        try:
            # Get the entity editor frontend instance
            if hasattr(self, 'entity_editor_frontend') and self.entity_editor_frontend:
                # Update the frontend with the Entity object
                self.entity_editor_frontend.set_entity_object(entity)
                
                print(f"Updated entity editor frontend with Entity: {entity.entity_name}")
            else:
                print("Entity editor frontend not available")
                
        except Exception as e:
            print(f"Error updating entity editor frontend: {e}")
    
    def send_message_to_entity_frontend(self, event, data=None):
        """Send a message to the entity editor frontend"""
        message = {"event": event, "data": data}
        
        # Send through the main frontend message system
        if hasattr(self, 'entity_editor_frontend') and self.entity_editor_frontend:
            self.entity_editor_frontend.process_message(message)
        else:
            # Fallback: emit message if available
            if hasattr(self, 'message'):
                self.message.emit(message)

    def handle_behavior_association(self, assignments):
        """Handle the behavior association assignments from the editor"""
        try:
            if assignments:
                print(f"Received behavior association: {assignments}")

                # Here you can process the assignments as needed
                # For example, save them to the entity file or update the entity data

                # For now, just acknowledge receipt
                self.send_message_to_main_frontend({
                        "event"      : "behavior_association_processed",
                        "status"     : "success",
                        "assignments": assignments
                        })
            else:
                print("No behavior association assignments received")

        except Exception as e:
            print(f"Error handling behavior association: {e}")
            self.send_message_to_main_frontend({
                    "event" : "behavior_association_processed",
                    "status": "error",
                    "error" : str(e)
                    })

    def load_ontology(self):
        self.ontology_name = getOntologyName(task="task_entity_generation")
        if not self.ontology_name:
            exit(-1)
        self.send_message_to_main_frontend("start")
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

        self.send_message_to_main_frontend(event="make_tree", data={
            "node_entity_types": self.node_entity_types,
            "all_entities": self.all_entities
        })
        pass



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

    def launch_entity_editor(self, mode="create"):
        # Create entity components
        self.entity_back_end = EntityEditorBackEnd(self.ontology_container)
        self.entity_front_end = EntityEditorFrontEnd()

        # Pass the selected entity type information to the entity editor
        if hasattr(self, 'entity_type') and self.entity_type:
            self.entity_back_end.set_selected_entity_type(self.entity_type)
            self.entity_front_end.set_selected_entity_type(self.entity_type)
            print(f"Passing selected entity type to editor: {self.entity_type}")
            print(f"Editor mode: {mode}")

        # Pass ontology container to entity front end for behavior association
        self.entity_front_end.set_ontology_container(self.ontology_container)
        
        # Set up communication between backend and frontend
        self.entity_back_end.message.connect(self.handle_entity_editor_message)
        
        # Give the backend a reference to the frontend for updates
        self.entity_back_end.set_entity_frontend(self.entity_front_end)
        
        # Give the main backend a reference to the entity frontend
        self.entity_editor_frontend = self.entity_front_end

        # Set editor mode based on selection type
        if mode == "edit" and self.entity_type and self.entity_type.get('name'):
            # Edit mode - load existing entity data
            entity_name = self.entity_type.get('name')
            print(f"Loading existing entity for editing: {entity_name}")
            # TODO: Load existing entity data and populate editor
        else:
            # Create mode - prepare for new entity creation
            print("Preparing for new entity creation")
            # Generate entity structure from class definition
            self.generate_entity_from_class_definition()

        # Connect entity editor communication
        self.entity_front_end.message.connect(self.entity_back_end.process_entity_front_message)
        self.entity_back_end.message.connect(self.handle_entity_editor_message)

        # Show editor
        self.entity_front_end.show()
    
    def generate_entity_from_class_definition(self):
        """Generate entity structure from class definition"""
        try:
            if not hasattr(self, 'entity_type') or not self.entity_type:
                print("No entity type selected for generation")
                return
            
            # Extract entity type information
            network = self.entity_type.get('network')
            category = self.entity_type.get('category')
            entity_type = self.entity_type.get('entity type')
            
            print(f"Generating entity for: {network}.{category}.{entity_type}")
            
            # Get all variables that belong to this entity type
            entity_variables = self.get_variables_for_entity_type(network, category, entity_type)
            
            # Create initial entity data structure
            entity_data = {
                'entity_name': f"{network}.{category}.{entity_type}.new_entity",
                'network': network,
                'category': category,
                'entity_type': entity_type,
                'variables': entity_variables,
                'defined_variables': [],  # Will be populated as user defines them
                'not_defined_variables': [], #entity_variables.copy(),  # Initially all are undefined
                'equations': [],
                'inputs': [],
                'outputs': [],
                'integrators': []
            }
            
            # Send entity structure to frontend for display
            if hasattr(self, 'entity_front_end'):
                self.entity_front_end.populate_entity_structure(entity_data)
                
            # print(f"Generated entity structure with {len(entity_variables)} variables")
            
        except Exception as e:
            print(f"Error generating entity from class definition: {e}")
            self.send_message_to_main_frontend("error", {"error": str(e)})
    
    def get_variables_for_entity_type(self, network, category, entity_type):
        """Get all variables that belong to a specific entity type"""
        try:
            variables = []
            
            # Get all variables from ontology container
            all_variables = self.ontology_container.variables
            
            # Filter variables that belong to this entity type
            for var_id, var_data in all_variables.items():
                var_network = var_data.get('network')
                var_category = var_data.get('category', 'unknown')
                var_type = var_data.get('type', 'unknown')
                
                # Check if variable belongs to this entity type
                # This is a simplified approach - you may need to refine the logic
                if var_network == network:
                    # Add more sophisticated filtering based on your ontology structure
                    variables.append({
                        'id': var_id,
                        'label': var_data.get('label', var_id),
                        'network': var_network,
                        'category': var_category,
                        'type': var_type,
                        'equations': list(var_data.get('equations', {}).keys())
                    })
            
            print(f"Found {len(variables)} variables for entity type {network}.{category}.{entity_type}")
            return variables
            
        except Exception as e:
            print(f"Error getting variables for entity type: {e}")
            return []
