import json
import os
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from Common.classes.entity_v1 import Entity
from Common.common_resources import getOntologyName
from Common.exchange_board import OntologyContainer
from Common.pop_up_message_box import makeMessageBox
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.ui_get_string_impl import UI_GetString
from OntologyBuilder.BehaviourLinker_v01.entity_back_end import EntityEditorBackEnd
from OntologyBuilder.BehaviourLinker_v01.entity_front_end import EntityEditorFrontEnd  # Back to original - refactored version is incompatible
from OntologyBuilder.BehaviourLinker_v01.main_automaton import gui_automaton


from OntologyBuilder.BehaviourLinker_v01.error_logger import log_error


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("..", ".."))  # Go up two levels to project root
sys.path.extend([root, os.path.join(root, "packages")])  # Add packages directory to path


class BehaviourLinerBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def process_main_frontend_message(self, message):
        event = message.get("event")

        # action
        if event == "failed":
            pass
        elif event == "selected_entity_type":
            self.entity_type = message.get("data", None)
            # Automatically launch entity editor for entity type selection (create mode)
            self.launch_entity_editor(mode="create")
        elif event == "selected_instance":
            self.entity_type = message.get("data", None)
            # Automatically launch entity editor for instance selection (edit mode)
            self.launch_entity_editor(mode="edit")
        elif event == "edit":
            # Entity instance selected - just update GUI to show edit/delete buttons
            self.entity_type = message.get("data", None)
            # Don't launch editor, just update GUI state
        elif event == "delete_instance":
            entity_data = message.get("data", None)
            if entity_data:
                self.delete_entity_instance(entity_data)
        elif event == "save":
            # Handle save event - mark as saved
            self.send_message_to_main_frontend("saved", {})
        elif event == "entity_saved":
            # Handle entity saved confirmation
            entity_name = message.get('entity_name')
            save_message = message.get('message')
            # Entity saved confirmation

            # Forward to main frontend
            self.send_message_to_main_frontend("entity_saved", {
                    'entity_name': entity_name,
                    'message'    : save_message
                    })

        self.send_message_to_main_frontend(event)

    def _convert_and_save_entities(self):
        """Convert all entities to dictionary format and save to ontology container"""
        entities_data = {}
        for entity_id, entity_obj in self.all_entities.items():
            # Use the entity's actual ID, not the dictionary key
            actual_entity_id = getattr(entity_obj, 'entity_id', entity_id)
            entities_data[actual_entity_id] = entity_obj.convert_to_dict()
            print(f"=== BACKEND DEBUG: Saving entity {actual_entity_id} (key was {entity_id}) ===")
        
        # Save using Exchange Board method (updates equation_entity_dict automatically)
        self.ontology_container.save_entities(entities_data)
        return entities_data

    def delete_entity_instance(self, entity_data):
        """Delete an entity instance from all_entities and update tree"""
        try:
            network = entity_data.get("network")
            category = entity_data.get("category")
            entity_type = entity_data.get("entity type")
            name = entity_data.get("name")

            entity_id = f"{network}.{category}.{entity_type}.{name}"

            # Remove from all_entities if it exists
            if entity_id in self.all_entities:
                del self.all_entities[entity_id]
                # Entity deleted

                # Convert entities to dictionary format and save using helper method
                self._convert_and_save_entities()

                # Update the main frontend tree to reflect the deletion
                self.update_main_frontend_tree()

                # Mark as changed and show save button
                self.mark_changed()

                # Send confirmation message
                self.send_message_to_main_frontend("entity_deleted", {
                        'entity_id'  : entity_id,
                        'entity_name': name
                        })
            else:
                # Entity not found
                makeMessageBox(f"Entity '{name}' not found", buttons=["OK"])

        except Exception as e:
            log_error("delete_entity_instance", e, f"deleting entity '{name}'")
            makeMessageBox(f"Error deleting entity: {str(e)}", buttons=["OK"])

    def mark_changed(self):
        """Mark the frontend as changed (red LED, show save button)"""
        try:
            # Send message to frontend to mark as changed
            self.send_message_to_main_frontend("mark_changed", {})
        except Exception as e:
            log_error("mark_changed", e, "marking interface as changed")

    def update_main_frontend_tree(self):
        """Update the main frontend tree with current entities"""
        try:
            # for eid in self.all_entities:
            #     print(f"=== TREE DEBUG: Entity in all_entities: {eid} ===")
            
            # Prepare data for tree update
            node_entity_types = {}
            arc_entity_types = {}

            # Extract entity types from ontology
            if hasattr(self.ontology_container, 'node_entity_types'):
                node_entity_types = self.ontology_container.node_entity_types
                # print(f"=== TREE DEBUG: Found {len(node_entity_types)} node entity types ===")

            # Extract arc entity types from ontology
            if hasattr(self.ontology_container, 'arc_entity_types'):
                arc_entity_types = self.ontology_container.arc_entity_types
                # print(f"=== TREE DEBUG: Found {len(arc_entity_types)} arc entity types ===")

            data = {
                    "node_entity_types": node_entity_types,
                    "arc_entity_types" : arc_entity_types,
                    "all_entities"     : self.all_entities
                    }

            # print(f"=== TREE DEBUG: Sending make_tree message to frontend ===")
            # Send tree update to frontend
            self.send_message_to_main_frontend("make_tree", data)
            # print(f"=== TREE DEBUG: Tree update message sent ===")

        except Exception as e:
            log_error("update_main_frontend_tree", e, "updating frontend tree")

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
            # Handle new entity with Entity object or edited entity in edit mode
            entity = message.get("entity_object")
            is_edit_mode = message.get("is_edit_mode", False)
            original_entity_id = message.get("original_entity_id")

            if entity:
                if is_edit_mode and original_entity_id:
                    # Edit mode - replace the original entity with the edited copy
                    self.replace_entity_in_all_entities(original_entity_id, entity)
                else:
                    # Create mode - add the new entity
                    self.process_entity_object(entity)
            else:
                # No Entity object found
                pass
        elif message.get("event") == "populate_entity_lists":
            # Handle populate_entity_lists from backend
            self.send_message_to_entity_frontend("populate_entity_lists", message.get("lists_data"))
        elif message.get("event") == "entity_created_successfully":
            # Handle successful entity creation
            # Entity created successfully
            self.send_message_to_main_frontend("entity_creation_complete")
        elif message.get("event") == "save_entity":
            # Handle entity save - mark main interface as changed
            entity = message.get("entity")
            if entity:
                # Entity saved
                # Add/update entity in all_entities
                self.add_entity_to_all_entities(entity)
                # Mark main interface as changed
                self.mark_changed()
            else:
                # No entity provided
                pass
        elif message.get("event") == "error":
            # Handle errors from entity editor
            error_msg = message.get("error", "Unknown error")
            log_error("handle_entity_editor_message", Exception(error_msg), "processing entity editor error")
            self.send_message_to_main_frontend("error", {"error": error_msg})

    def process_entity_object(self, entity):
        """Process Entity object directly - no data duplication needed"""
        try:
            if not entity:
                # No Entity object provided
                return

            # Use the Entity object directly - no more data extraction needed
            entity_id = getattr(entity, 'entity_id', 'Unknown Entity')
            # Processing Entity object

            # Add the entity to all_entities
            self.add_entity_to_all_entities(entity)

            # Mark main interface as changed when entity is processed
            self.mark_changed()

            # Update the entity editor frontend with the Entity information
            self.update_entity_editor_frontend(entity)

        except Exception as e:
            self.send_message_to_main_frontend("error", {"error": str(e)})

    def process_entity_data(self, entity_data):
        """Process the entity data with equation selection and update frontend"""
        try:
            if not entity_data:
                # No entity data provided
                return

            root_variable = entity_data.get('root_variable')
            definition_method = entity_data.get('definition_method')

            # Get the Entity object if available
            entity = entity_data.get('entity_object')
            if entity:
                entity_name = getattr(entity, 'entity_id', 'Unknown Entity')
                # Found Entity object

                # Add the entity to all_entities and save it
                self.add_entity_to_all_entities(entity)

                # Update the entity editor frontend with the Entity information
                self.update_entity_editor_frontend(entity)

                # Update the main frontend tree to show the new entity
                # self.update_main_frontend_tree()
            else:
                # No Entity object found
                pass

            # Entity data processed successfully

        except Exception as e:
            self.send_message_to_main_frontend("error", {"error": str(e)})

    def update_entity_editor_frontend(self, entity):
        """Update the entity editor frontend with Entity object information"""
        try:
            # Check if entity is None
            if entity is None:
                # Cannot update - Entity object is None
                return

            # Get the entity editor frontend instance
            if hasattr(self, 'entity_editor_frontend') and self.entity_editor_frontend:
                # Update the frontend with the Entity object
                self.entity_editor_frontend.set_entity_object(entity)

                entity_name = getattr(entity, 'entity_id', 'Unknown Entity')
                # Updated entity editor frontend
            else:
                # Entity editor frontend not available
                pass

        except Exception as e:
            log_error("update_entity_editor_frontend", e,
                      f"updating frontend for {getattr(entity, 'entity_id', 'unknown entity')}")

    def replace_entity_in_all_entities(self, original_entity_id, edited_entity):
        """Replace the original entity with the edited copy in all_entities"""
        try:
            if original_entity_id in self.all_entities:
                # Replace the original entity with the edited copy
                self.all_entities[original_entity_id] = edited_entity

                # Convert entities to dictionary format and save using helper method
                self._convert_and_save_entities()

                # Update the main frontend tree to reflect the changes
                self.update_main_frontend_tree()

                # Mark as changed and show save button
                self.mark_changed()

                # Entity replaced successfully
            else:
                # Original entity not found
                makeMessageBox(f"Original entity '{original_entity_id}' not found for replacement", buttons=["OK"])

        except Exception as e:
            log_error("replace_entity_in_all_entities", e, f"replacing entity '{original_entity_id}'")
            makeMessageBox(f"Error replacing entity: {str(e)}", buttons=["OK"])

    def add_entity_to_all_entities(self, entity):
        """Add or update an entity in all_entities and save to file"""
        try:
            # Check if entity is None or doesn't have entity_name
            if entity is None:
                # Cannot add - Entity object is None
                return

            if not hasattr(entity, 'entity_id'):
                # Cannot add - missing entity_id
                return

            # Check if entity already exists
            entity_id = entity.entity_id
            if entity_id in self.all_entities:
                # Updating existing entity
                pass
            else:
                # Adding new entity
                pass

            # Add/update the entity in the all_entities dictionary
            entity_id = getattr(entity, 'entity_id', entity_id)  # Use entity's actual ID
            self.all_entities[entity_id] = entity
            print(f"=== BACKEND DEBUG: Added entity {entity_id} to all_entities ===")
            print(f"=== BACKEND DEBUG: Entity object type: {type(entity)} ===")
            print(f"=== BACKEND DEBUG: Entity attribute check - hasattr(entity_id): {hasattr(entity, 'entity_id')} ===")
            if hasattr(entity, 'entity_id'):
                print(f"=== BACKEND DEBUG: Entity.entity_id: {getattr(entity, 'entity_id')} ===")
            print(f"=== BACKEND DEBUG: Total entities in all_entities: {len(self.all_entities)} ===")

            # Convert entities to dictionary format and save using helper method
            self._convert_and_save_entities()

            # Update the main frontend tree to show the new entity
            self.update_main_frontend_tree()

        except Exception as e:
            print(f">>>>>>>>>>>>>>> Error adding entity to all_entities: {e}")

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

                # Here you can process the assignments as needed
                # For example, save them to the entity file or update the entity data

                # For now, just acknowledge receipt
                self.send_message_to_main_frontend({
                        "event"      : "behavior_association_processed",
                        "status"     : "success",
                        "assignments": assignments
                        })
            else:
                log_error("handle_behavior_association", Exception("No assignments"),
                          "no behavior association assignments received")

        except Exception as e:
            log_error("handle_behavior_association", e, "processing behavior association assignments")
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
        self.arc_entity_types = self.ontology_container.arc_entity_types

        # load all instances
        self.all_entities = self.load_entities_from_file(self.ontology_name)

        self.send_message_to_main_frontend(event="make_tree", data={
                "node_entity_types": self.node_entity_types,
                "arc_entity_types" : self.arc_entity_types,
                "all_entities"     : self.all_entities
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

        # Create empty file if it doesn't exist
        if not os.path.isfile(path):
            with open(path, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)
            return {}

        with open(
                path,
                encoding="utf-8",
                ) as file:
            data = json.load(file)
        if not data:
            return {}

        # if entity_names is None:
        #   entity_names = data.keys()
        entity_names = data.keys()

        entities = {}
        for ent_name in entity_names:
            if ent_name not in data:
                log_error("load_entity", Exception(f"Entity '{ent_name}' not found"), "loading entity from file")
                continue

            # Use equation_entity_dict from exchange board
            all_equations = {}
            if hasattr(self, 'ontology_container') and self.ontology_container:
                if hasattr(self.ontology_container, 'equation_entity_dict'):
                    all_equations = self.ontology_container.equation_entity_dict
                else:
                    log_error("load_entity", Exception("equation_entity_dict not found"),
                              "loading entity - no equations available")
                    # Return empty entity if no equations available
                    continue

            new_entity = Entity(
                    ent_name,
                    all_equations,  # Now with real global equations!
                    data[ent_name]["index_set"],
                    data[ent_name]["integrators"],
                    data[ent_name]["var_eq_forest"],
                    data[ent_name]["init_vars"],
                    data[ent_name]["input_vars"],
                    data[ent_name]["output_vars"],
                    )
            
            # Generate local variable classifications from the loaded data
            new_entity.build_local_variable_classifications()
            # Convert base_ prefix to base# for internal consistency
            if "base_" in ent_name:
                ent_name = ent_name.replace("base_", "base#")

            entities[ent_name] = new_entity

        return entities

    def launch_entity_editor(self, mode="create"):
        # Create entity components
        self.entity_back_end = EntityEditorBackEnd(self.ontology_container)
        self.entity_front_end = EntityEditorFrontEnd()  # Back to original - refactored version is incompatible

        # IMPORTANT: Clear state manager to prevent cross-contamination between sessions
        self.entity_back_end.state_manager.clear_state()
        self.entity_back_end.state_manager.set_frontend(self.entity_front_end)
        self.entity_back_end.state_manager.set_backend(self.entity_back_end)

        # Add IconHelper to original for better icon management
        if hasattr(self.entity_front_end, 'ui') and hasattr(self.entity_front_end.ui, 'pushAddVariable'):
            from .icon_helper import IconHelper
            IconHelper.setup_round_button(self.entity_front_end.ui.pushAddVariable, "new", tooltip="new variable")
            IconHelper.setup_round_button(self.entity_front_end.ui.pushAddStateVariable, "dependent_variable", tooltip="add state variable")
            IconHelper.setup_round_button(self.entity_front_end.ui.pushAddTransport, "token_flow", tooltip="add transport variable")
            IconHelper.setup_round_button(self.entity_front_end.ui.pushEditVariable, "edit", tooltip="edit variable")
            IconHelper.setup_round_button(self.entity_front_end.ui.pushDeleteVariable, "delete", tooltip="delete variable")
            IconHelper.setup_round_button(self.entity_front_end.ui.pushAccept, "accept", tooltip="accept")
            IconHelper.setup_round_button(self.entity_front_end.ui.pushCancle, "cancel", tooltip="cancel")
            IconHelper.setup_round_button(self.entity_front_end.ui.pushAddIntensitity, "infinity", tooltip="secondary states -- intensities")
            
            # Keep the LED button setup exactly like the original
            self.signalButton = IconHelper.setup_round_button(self.entity_front_end.ui.LED, "LED_green", tooltip="status", mysize=20)

        # Pass ontology container to entity front end for behavior association
        self.entity_front_end.set_ontology_container(self.ontology_container)

        # Set up communication between backend and frontend
        self.entity_back_end.message.connect(self.handle_entity_editor_message)

        # Give the backend a reference to the frontend for updates
        self.entity_back_end.set_entity_frontend(self.entity_front_end)

        # IMPORTANT: Set the selected entity type in the backend so it knows the mode
        if hasattr(self, 'entity_type') and self.entity_type:
            self.entity_back_end.set_selected_entity_type_or_entity(self.entity_type)

        # Give the main backend a reference to the entity frontend
        self.entity_editor_frontend = self.entity_front_end

        # Set editor mode based on selection type
        if mode == "edit" and self.entity_type and self.entity_type.get('name'):
            # Edit mode - load existing entity data as a COPY to preserve original
            import copy

            entity_network = self.entity_type.get("network")
            entity_category = self.entity_type.get("category")
            entity_type = self.entity_type.get("entity type")
            entity_name = self.entity_type.get('name')
            entity_id = f"{entity_network}.{entity_category}.{entity_type}.{entity_name}"

            # Create a deep copy of the original entity for editing
            original_entity = self.all_entities[entity_id]
            entity_copy = copy.deepcopy(original_entity)

            # Store reference to original entity for save operations
            self.entity_front_end.original_entity_id = entity_id
            self.entity_front_end.original_entity = original_entity
            self.entity_front_end.is_edit_mode = True

            # Load the COPY into the editor, not the original
            self.entity_front_end.set_entity_object(entity_copy)
            self.entity_front_end.set_mode("edit")
            
            # IMPORTANT: Update the state manager with the entity copy
            self.entity_back_end.state_manager.update_entity_state(entity_copy)

            # Also populate current_entity_data for behavior association editor
            entity_data = {
                    'network'      : entity_network,
                    'category'     : entity_category,
                    'entity_type'  : entity_type,
                    'entity_name'  : entity_name,
                    'entity_id'    : entity_id,
                    'entity_object': entity_copy  # Use the copy
                    }
            self.entity_front_end.current_entity_data = entity_data
        else:
            # Create mode - prepare for new entity creation
            # Generate entity structure from class definition
            success = self.generate_entity_from_class_definition()
            # Only show editor if entity creation was successful
            if not success:
                return  # Don't show editor if creation failed/cancelled

        # Connect entity editor communication
        self.entity_front_end.message.connect(self.entity_back_end.process_entity_front_message)
        self.entity_back_end.message.connect(self.handle_entity_editor_message)

        # Show editor
        self.entity_front_end.show()

    def generate_entity_from_class_definition(self):
        """Generate entity structure from class definition"""
        try:
            if not hasattr(self, 'entity_type') or not self.entity_type:
                log_error("generate_entity_from_class_definition", Exception("No entity type selected"),
                          "generating entity from class definition")
                return False

            # Extract entity type information
            network = self.entity_type.get('network')
            category = self.entity_type.get('category')
            entity_type = self.entity_type.get('entity type')

            # Get existing entity names for this entity type to use as limiting list
            existing_names = self.get_existing_entity_names_for_type(network, category, entity_type)

            # Create name dialog with limiting list to prevent duplicates
            task = UI_GetString("provide a name for the entity", limiting_list=existing_names)
            result = task.exec_()

            # Check if dialog was accepted (not rejected or closed)
            if not task.text:
                # User cancelled the name dialog - close the entity editor and return failure
                if hasattr(self, 'entity_front_end'):
                    self.entity_front_end.close()
                return False

            entity_name = task.text
            if not entity_name:
                # User accepted but provided empty name - close the entity editor and return failure
                if hasattr(self, 'entity_front_end'):
                    self.entity_front_end.close()
                return False

            # For create mode, start with empty variables - user will add them
            # Don't populate with all available variables from ontology
            entity_variables = []  # Empty list for create mode

            # Create initial entity data structure
            entity_data = {
                    'entity_id'            : f"{network}.{category}.{entity_type}.{entity_name}",
                    'network'              : network,
                    'category'             : category,
                    'entity_type'          : entity_type,
                    'variables'            : entity_variables,  # Empty for create mode
                    'defined_variables'    : [],  # Will be populated as user defines them
                    'not_defined_variables': [],  # Empty for create mode
                    'equations'            : [],
                    'inputs'               : [],
                    'outputs'              : [],
                    'integrators'          : []
                    }

            # Send entity structure to frontend for display
            if hasattr(self, 'entity_front_end'):
                self.entity_front_end.populate_entity_structure(entity_data)

            # Return success
            return True

        except Exception as e:
            log_error("generate_entity_from_class_definition", e, "generating entity structure")
            self.send_message_to_main_frontend("error", {"error": str(e)})
            return False

    def get_existing_entity_names_for_type(self, network, category, entity_type):
        """Get all existing entity names for a specific entity type"""
        try:
            existing_names = []

            # Iterate through all entities to find matching ones
            for entity_id, entity_obj in self.all_entities.items():
                # Parse entity_id to extract components
                if ">" not in entity_id:  # Skip arc entities which contain ">"
                    parts = entity_id.split('.')
                    if len(parts) == 4:
                        entity_net, entity_cat, entity_type_name, entity_name = parts

                        # Check if this entity matches the requested type
                        if (entity_net == network and
                                entity_cat == category and
                                entity_type_name == entity_type):
                            existing_names.append(entity_name)

            return existing_names

        except Exception as e:
            log_error("get_existing_entity_names_for_type", e,
                      f"getting existing names for {network}.{category}.{entity_type}")
            return []

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
                            'id'       : var_id,
                            'label'    : var_data.get('label', var_id),
                            'network'  : var_network,
                            'category' : var_category,
                            'type'     : var_type,
                            'equations': list(var_data.get('equations', {}).keys())
                            })

            return variables

        except Exception as e:
            log_error("get_variables_for_entity_type", e, f"getting variables for {network}.{category}.{entity_type}")
            return []
