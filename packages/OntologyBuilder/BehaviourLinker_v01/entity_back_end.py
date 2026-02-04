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



TIMING = False
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

    def process_message(self, message):
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
    
    def launch_behavior_association_editor(self, ontology_container):
        """Launch the behavior association editor and handle its response"""
        try:
            from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor
            
            # Launch the BehaviorAssociation editor
            assignments = launch_behavior_association_editor(ontology_container)
            
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
                initialization_value = assignments.get('initialization_value')
                
                # Create entity data structure
                entity_data = {
                    'root_variable': root_variable,
                    'definition_method': 'initialization' if use_initialization else 'equation',
                    'equation_id': root_equation if not use_initialization else None,
                    'initialization_value': initialization_value if use_initialization else None,
                    'tree_structure': assignments.get('tree', {}),
                    'nodes': assignments.get('nodes', {}),
                    'assignments': assignments
                }
                
                # Send back to main backend for processing
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