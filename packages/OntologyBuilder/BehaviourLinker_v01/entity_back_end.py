import json
import os
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from Common.classes.entity import Entity
from OntologyBuilder.BehaviourLinker_v01.entity_automaton import gui_automaton

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



#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])




class EntityEditorBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self, ontology_container):
        super().__init__()
        self.ontology_container = ontology_container
        self.selected_entity_type = None

    def set_selected_entity_type(self, entity_type_data):
        """Set the selected entity type from the main tree"""
        self.selected_entity_type = entity_type_data
        print(f"EntityEditorBackEnd received selected entity type: {self.selected_entity_type}")
        
        # Determine if we're in create or edit mode
        if self.selected_entity_type and self.selected_entity_type.get("name"):
            self.mode = "edit"
            entity_name = self.selected_entity_type.get("name")
            print(f"EntityEditorBackEnd in EDIT mode for entity: {entity_name}")
            # TODO: Load existing entity data for editing
        else:
            self.mode = "create"
            print(f"EntityEditorBackEnd in CREATE mode for entity type: {self.selected_entity_type.get('entity type') if self.selected_entity_type else 'Unknown'}")

    def set_entity_frontend(self, entity_frontend):
        """Set the entity frontend reference for direct updates"""
        self.entity_frontend = entity_frontend
        print("EntityEditorBackEnd: Entity frontend reference set")

    def process_entity_front_message(self, message):
        """Process messages from the entity editor frontend"""
        event = message.get("event")
        
        if event == "launch_behavior_association_editor":
            # Launch the behavior association editor
            ontology_container = message.get("ontology_container")
            self.launch_behavior_association_editor(ontology_container)
        elif event == "behavior_association_defined":
            # Handle the behavior association with equation selection
            assignments = message.get("assignments")
            self.handle_behavior_association(assignments)
        elif event == "entity_created":
            # Handle new entity creation
            entity_data = message.get("entity_data")
            self.handle_entity_creation(entity_data)
        else:
            print(f"Unknown event: {event}")

    # def send_message_to_entity_frontend(self, event, data=None):
    #     """Send a message to the entity editor frontend"""
    #     message = {"event": event, "interface": gui_automaton[event], "data": data}
    #     self.message.emit(message)
    
    def launch_behavior_association_editor(self, ontology_container):
        """Launch the behavior association editor and handle its response"""
        try:
            from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor
            
            # Get entity type information for rule-based filtering
            entity_type_info = {
                'network': self.selected_entity_type.get('network', 'unknown'),
                'category': self.selected_entity_type.get('category', 'unknown'),
                'entity type': self.selected_entity_type.get('entity type', 'unknown')
            }
            
            print(f"Debug: Launching behavior association editor with entity type: {entity_type_info}")
            
            # Launch the BehaviorAssociation editor with entity type info
            assignments = launch_behavior_association_editor(ontology_container, entity_type_info)
            
            if assignments:
                # Process the assignments directly
                self.handle_behavior_association(assignments)
            else:
                print("No behavior association defined")
                self.message.emit({
                    "event": "info",
                    "message": "Behavior association cancelled"
                })
                
        except Exception as e:
            print(f"Error launching BehaviorAssociation editor: {e}")
            self.message.emit({
                "event": "error",
                "error": f"Error launching BehaviorAssociation editor: {str(e)}"
            })
    
    def handle_behavior_association(self, assignments):
        """Handle the behavior association assignments from the editor"""
        try:
            if assignments:
                print(f"Received behavior association: {assignments}")
                
                # Extract key information
                root_variable = assignments.get('root_variable')
                root_equation = assignments.get('root_equation')
                use_initialization = assignments.get('use_initialization', False)
                
                # Create entity data structure
                entity_data = {
                    'root_variable': root_variable,
                    'definition_method': 'initialization' if use_initialization else 'equation',
                    'equation_id': root_equation if not use_initialization else None,
                    'tree_structure': assignments.get('tree', {}),
                    'nodes': assignments.get('nodes', {}),
                    'assignments': assignments
                }

                # Create entity with proper parameters TODO: ask for a name
                entity_name = f"{self.selected_entity_type.get('network', 'unknown')}.{self.selected_entity_type.get('category', 'unknown')}.{self.selected_entity_type.get('entity type', 'unknown')}.new_entity"
                
                # Get equations from ontology container
                all_equations = getattr(self.ontology_container, 'equation_dictionary', {})
                
                # Create entity with empty forest (like in the old implementation)
                entity = Entity(
                    entity_name=entity_name,
                    all_equations=all_equations,
                    var_eq_forest=[{}],  # Initialize with empty forest
                    init_vars=[],
                    input_vars=[],
                    output_vars=[]
                )
                
                # Set up variable-equation relationships using the Entity's built-in method
                # Extract variable-equation assignments from the behavior association data
                var_eq_assignments = self.extract_var_eq_assignments(assignments)
                
                if var_eq_assignments:
                    # Set the root variable as output variable (required for var_eq_forest generation)
                    root_variable = assignments.get('root_variable')
                    if root_variable:
                        entity.set_output_var(root_variable, True)
                    
                    # Generate the variable-equation forest using Entity's method
                    entity.generate_var_eq_forest(var_eq_assignments)
                    entity.update_var_eq_tree()
                    
                    # Update entity_data with the actual Entity object information
                    entity_data.update({
                        'entity_object': entity,  # Send the actual Entity object
                        'var_eq_forest': entity.var_eq_forest,
                        'output_vars': entity.output_vars,
                        'input_vars': entity.input_vars,
                        'init_vars': entity.init_vars,
                        'integrators': entity.integrators
                    })
                    
                # Send back to main backend for processing
                print(f"Entity data ready: {entity_data}")
                entity.printMe()
                self.message.emit({
                    "event": "entity_data_ready",
                    "entity_data": entity_data
                })
                
            else:
                print("No behavior association assignments received")
                
        except Exception as e:
            print(f"Error handling behavior association: {e}")
            self.message.emit({
                "event": "error",
                "error": str(e)
            })
    
    def handle_entity_creation(self, entity_data):
        """Handle the final entity creation"""
        try:
            print(f"Creating entity with data: {entity_data}")
            
            # Here you would typically:
            # 1. Validate the entity data
            # 2. Create the Entity object
            # 3. Save it to the ontology
            
            # For now, just acknowledge receipt
            self.message.emit({
                "event": "entity_created_successfully",
                "entity_data": entity_data
            })
            
        except Exception as e:
            print(f"Error creating entity: {e}")
            self.message.emit({
                "event": "error",
                "error": str(e)
            })
    
    def extract_var_eq_assignments(self, assignments):
        """Extract variable-equation assignments from behavior association data"""
        var_eq_assignments = {}
        
        # Get nodes and tree from assignments
        nodes = assignments.get('nodes', {})
        tree = assignments.get('tree', {})
        
        # Extract variable -> equation relationships
        # nodes: {node_id: var_id/equation_id}, tree: {tree_node_id: tree_data}
        for node_id, node_value in nodes.items():
            if node_value.startswith('V_'):  # It's a variable
                # Find if this variable has an equation in the tree
                equation_id = None
                # Look for this variable node in the tree
                if node_id in tree:
                    # Get the children of this variable node
                    children = tree[node_id].get('children', [])
                    # Find the equation in the children
                    for child_node_id in children:
                        if child_node_id in nodes:
                            child_value = nodes[child_node_id]
                            if child_value.startswith('E_'):
                                equation_id = child_value
                                break
                
                if equation_id:
                    var_eq_assignments[node_value] = [equation_id]
                else:
                    var_eq_assignments[node_value] = []  # Variable with no equation
        
        return var_eq_assignments