import os
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from Common.classes.entity import Entity
from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor
from OntologyBuilder.BehaviourLinker_v01.behaviour_association.equation_selector import select_equation_for_variable

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])


class EntityEditorBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self, ontology_container):
        super().__init__()
        self.ontology_container = ontology_container
        self.selected_entity_type = None

    def set_selected_entity_type_or_entity(self, entity_type_data):
        """Set the selected entity type from the main tree"""
        self.selected_entity_type = entity_type_data
        print(f"EntityEditorBackEnd received selected entity type: {self.selected_entity_type}")

        # Determine if we're in create or edit mode
        if self.selected_entity_type and self.selected_entity_type.get("name"):
            self.mode = "edit"
            entity_name = self.selected_entity_type.get("name")
            print(f"EntityEditorBackEnd in EDIT mode for entity: {entity_name}")
            # Notify frontend of mode change
            self.entity_frontend.set_mode("edit")
        else:
            self.mode = "create"
            # Notify frontend of mode change
            self.entity_frontend.set_mode("create")

    def set_entity_frontend(self, entity_frontend):
        """Set the entity frontend reference for direct updates"""
        self.entity_frontend = entity_frontend
        # print("EntityEditorBackEnd: Entity frontend reference set")

    def process_entity_front_message(self, message):
        """Process messages from the entity editor frontend"""
        event = message.get("event")
        # entity_data = self.entity_frontend.current_entity_data

        if event == "add_state_variable":
            self.launch_behavior_association_editor()
        elif event == "add_variable":
            self.launch_behavior_association_editor()
        elif event == "def_variable":
            self.launch_equation_association_editor(message.get("var_id"))
        elif event == "save_entity":
            # Handle entity save from Accept button
            entity = message.get('entity')
            if entity:
                print(f"Saving entity: {entity.entity_id}")
                
                # Mark frontend as saved
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.markSaved()
                
                # Send the completed entity to main backend for final processing
                print(f"Sending completed entity to main backend: {entity.entity_id}")
                self.message.emit({
                    "event": "entity_data_ready",
                    "entity_object": entity  # Send only the Entity object
                })
                
                # # Send success message back to frontend
                # self.message.emit({
                #     "event": "entity_saved",
                #     "entity_name": entity.entity_id,
                #     "message": f"Entity '{entity.entity_id}' saved successfully"
                # })
            else:
                print("No entity provided for saving")
                self.message.emit({
                    "event": "error",
                    "error": "No entity to save"
                })

    def launch_equation_association_editor(self, var_id):
        """Launch the equation association editor and handle its response"""
        try:
            entity_data = self.entity_frontend.current_entity_data
            entity_type_info = {
                    'network'    : entity_data.get('network', 'unknown'),
                    'category'   : entity_data.get('category', 'unknown'),
                    'entity_type': entity_data.get('entity_type', 'unknown')
                    }
            
            # Get variable data from ontology container
            if var_id in self.ontology_container.variables:
                variable_data = self.ontology_container.variables[var_id]
                
                # Launch equation selector for this specific variable
                assignments = select_equation_for_variable(variable_data, self.ontology_container)
                
                if assignments:
                    print(f"Received equation association for {var_id}: {assignments}")
                    
                    # For direct equation selection, create a simple assignment structure
                    # that handle_behavior_association can understand
                    equation_id = assignments.get('equation_id')
                    use_initialization = assignments.get('use_initialization', False)
                    
                    if use_initialization:
                        # For instantiation, don't include equation in tree/nodes
                        simple_assignments = {
                            'root_variable': var_id,
                            'root_equation': None,
                            'use_initialization': True,
                            'tree': {},  # Empty tree for instantiation
                            'nodes': {},  # Empty nodes for instantiation
                            'IDs': {}
                        }
                    else:
                        # For equation assignment, include equation in tree structure
                        simple_assignments = {
                            'root_variable': var_id,
                            'root_equation': equation_id,
                            'use_initialization': False,
                            'tree': {0: {'children': [1], 'parent': None}, 1: {'children': [], 'parent': 0}},
                            'nodes': {0: var_id, 1: equation_id},
                            'IDs': {var_id: 0, equation_id: 1}
                        }
                    
                    # Process the assignments using the same logic as handle_behavior_association
                    self.handle_behavior_association(simple_assignments)
                    
                    # Update frontend to show the changes
                    if hasattr(self, 'entity_frontend') and self.entity_frontend:
                        if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                            print(f"Found current_entity: {self.entity_frontend.current_entity}")
                            self.entity_frontend.update_entity_from_backend_entity(self.entity_frontend.current_entity)
                        else:
                            print("No current_entity found - using entity_data approach")
                            # No Entity object yet - refresh from entity data
                            self.generate_lists_from_entity_data(self.entity_frontend.current_entity_data)
                else:
                    print(f"No equation association defined for {var_id}")
                    self.message.emit({
                            "event"  : "info",
                            "message": f"Equation association cancelled for {var_id}"
                            })
            else:
                print(f"Variable {var_id} not found in ontology container")
                self.message.emit({
                        "event": "error",
                        "error": f"Variable {var_id} not found"
                        })
                
        except Exception as e:
            print(f"Error launching equation association editor: {e}")
            self.message.emit({
                    "event": "error",
                    "error": f"Error launching equation association editor: {str(e)}"
                    })


    def launch_behavior_association_editor(self):
        """Launch the behavior association editor and handle its response"""
        try:
            # from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor

            entity_data = self.entity_frontend.current_entity_data
            # Get entity type information for rule-based filtering
            entity_type_info = {
                    'network'    : entity_data.get('network', 'unknown'),
                    'category'   : entity_data.get('category', 'unknown'),
                    'entity_type': entity_data.get('entity_type', 'unknown')
                    }

            print(f"Debug: Launching behavior association editor with entity type: {entity_type_info}")

            # Launch the BehaviorAssociation editor with entity type info
            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info)

            if assignments:
                # Process the assignments directly
                self.handle_behavior_association(assignments)
            else:
                print("No behavior association defined")
                self.message.emit({
                        "event"  : "info",
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

                # Check if we already have an entity object from previous operations #TODO: check if this is necessary
                existing_entity = None
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                        existing_entity = self.entity_frontend.current_entity
                        print(f"Found existing entity: {existing_entity.entity_id}")

                # Create entity data structure
                entity_data = {
                        'root_variable'    : root_variable,
                        'definition_method': 'initialization' if use_initialization else 'equation',
                        'equation_id'      : root_equation if not use_initialization else None,
                        'tree_structure'   : assignments.get('tree', {}),
                        'nodes'            : assignments.get('nodes', {}),
                        'assignments'      : assignments
                        }

                if existing_entity:
                    # Update existing entity instead of creating new one
                    print(f"Updating existing entity: {existing_entity.entity_id}")
                    entity = existing_entity

                    # Set up variable-equation relationships using the existing Entity
                    var_eq_assignments = self.extract_var_eq_assignments(assignments)

                    if var_eq_assignments:
                        # Set the root variable as output variable if not already set
                        root_variable = assignments.get('root_variable')
                        use_initialization = assignments.get('use_initialization', False)
                        
                        if use_initialization:
                            # Add to initialization variables using Entity method
                            entity.set_init_var(root_variable, True)
                            print(f"Added {root_variable} to init_vars for instantiation")
                        else:
                            # Add to output variables and create equation relationship using Entity method
                            entity.set_output_var(root_variable, True)
                            print(f"Added {root_variable} to output_vars with equation")

                        # Generate the variable-equation forest using Entity's method
                        entity.generate_var_eq_forest(var_eq_assignments)
                        entity.update_var_eq_tree()
                    else:
                        # Handle instantiation case with no equation assignments
                        root_variable = assignments.get('root_variable')
                        use_initialization = assignments.get('use_initialization', False)
                        
                        if use_initialization and root_variable:
                            # Add to initialization variables using Entity method
                            entity.set_init_var(root_variable, True)
                            print(f"Added {root_variable} to init_vars for instantiation (no assignments)")
                            # Also remove from output_vars if it was there (to avoid conflicts)
                            entity.set_output_var(root_variable, False)
                            print(f"Removed {root_variable} from output_vars (now instantiation)")
                        print(f"Entity init_vars after adding: {entity.init_vars}")

                        print(f"=== AFTER FOREST GENERATION ===")
                        print(f"Entity var_eq_forest: {entity.var_eq_forest}")
                        print(f"Entity integrators: {entity.integrators}")
                        print(f"Entity output_vars: {entity.output_vars}")
                        print(f"Entity input_vars: {entity.input_vars}")
                        print(f"Entity init_vars: {entity.init_vars}")

                        # Check if E_93 is in the forest and if it should be an integrator
                        has_e93 = False
                        for tree in entity.var_eq_forest:
                            for key, values in tree.items():
                                if key == 'E_93':
                                    has_e93 = True
                                    print(f"Found E_93 in forest with values: {values}")
                                elif values and 'E_93' in values:
                                    has_e93 = True
                                    print(f"Found E_93 in values: {values}")

                        print(f"E_93 found in forest: {has_e93}")

                        # Note: Integrators are properly handled by Entity.update_var_eq_tree()
                        # based on equation objects' is_integrator() method

                    # Update entity_data with the existing Entity object information
                    entity_data.update({
                            'entity_object': entity,
                            'var_eq_forest': entity.var_eq_forest,
                            'output_vars'  : entity.output_vars,
                            'input_vars'   : entity.input_vars,
                            'init_vars'    : entity.init_vars,
                            'integrators'  : entity.integrators
                            })

                else:
                    # Create new entity only if no existing one
                    print("Creating new entity")
                    entity_data = self.entity_frontend.current_entity_data
                    entity_id = entity_data.get('entity_id')
                    entity_name = entity_id.split(".")[
                        -1]  # f"{self.selected_entity_type.get('network', 'unknown')}.{self.selected_entity_type.get('category', 'unknown')}.{self.selected_entity_type.get('entity type', 'unknown')}.new_entity"

                    # Get equations from ontology container - use list_equation_classes for actual Equation objects
                    all_equations = {}
                    if hasattr(self.ontology_container, 'list_equation_classes'):
                        print(
                            f"Using list_equation_classes with {len(self.ontology_container.list_equation_classes)} equations")
                        for eq_obj in self.ontology_container.list_equation_classes:
                            all_equations[eq_obj.eq_id] = eq_obj
                            # Debug: Check if E_93 has is_integrator method
                            # if eq_obj.eq_id == 'E_93':
                            #     print(
                            #         f"E_93 object: type={type(eq_obj)}, has_is_integrator={hasattr(eq_obj, 'is_integrator')}")
                            #     if hasattr(eq_obj, 'is_integrator'):
                            #         print(f"E_93.is_integrator(): {eq_obj.is_integrator()}")
                    else:
                        print("list_equation_classes not found, falling back to equation_dictionary")
                        all_equations = getattr(self.ontology_container, 'equation_dictionary', {})

                    # Create entity with empty forest (like in the old implementation)
                    entity = Entity(
                            entity_id=entity_id,
                            all_equations=all_equations,
                            var_eq_forest=[{}],  # Initialize with empty forest
                            init_vars=[],
                            input_vars=[],
                            output_vars=[],
                            )

                    # Set up variable-equation relationships using the Entity's built-in method
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
                                'output_vars'  : entity.output_vars,
                                'input_vars'   : entity.input_vars,
                                'init_vars'    : entity.init_vars,
                                'integrators'  : entity.integrators
                                })
                        
                        # IMPORTANT: Store the Entity object in the frontend for future updates
                        self.entity_frontend.current_entity = entity

                # Update entity locally - don't send to main backend yet
                print(f"Entity data updated locally: {entity_data}")
                if 'entity_object' in entity_data:
                    entity_data['entity_object'].printMe()
                
                # Mark entity as changed but don't send to main backend yet
                self.entity_frontend.markChanged()

                # Update frontend for immediate display refresh
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if 'entity_object' in entity_data and entity_data['entity_object']:
                        self.entity_frontend.update_entity_from_backend_entity(entity)
                    else:
                        # No Entity object yet - generate lists from entity_data
                        self.generate_lists_from_entity_data(entity_data)

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
                    "event"      : "entity_created_successfully",
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

        print(f"=== EXTRACTING VAR_EQ_ASSIGNMENTS ===")
        print(f"Nodes: {nodes}")
        print(f"Tree: {tree}")

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

        print(f"Extracted var_eq_assignments: {var_eq_assignments}")
        return var_eq_assignments

    def handle_state_variable_selection_entity_based(self, assignments, entity_data):
        """Simplified state variable selection using Entity class only"""
        try:
            print(f"Backend handling state variable selection (Entity-based): {assignments}")
            
            # Import Entity class
            from Common.classes.entity import Entity
            
            # Get all equations from ontology container
            all_equations = {}
            if hasattr(self.ontology_container, 'list_equation_classes'):
                for eq_obj in self.ontology_container.list_equation_classes:
                    all_equations[eq_obj.eq_id] = eq_obj
            else:
                all_equations = getattr(self.ontology_container, 'equation_dictionary', {})
            
            # Extract the selected variable and equation
            root_variable = assignments.get('root_variable')
            root_equation = assignments.get('root_equation')
            
            if root_variable and root_equation:
                # Update the mode to edit
                self.mode = "edit"
                print(f"Mode changed to: {self.mode}")
                
                # Notify frontend of mode change
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.set_mode("edit")
                
                # Always work with Entity objects - no more entity_data complexity
                entity = None
                
                # Check if frontend already has an Entity object
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                        entity = self.entity_frontend.current_entity
                        print(f"Using existing Entity object: {entity.entity_id}")
                
                # Create new Entity if none exists
                if entity is None:
                    entity_name = entity_data.get('entity_id', 'new_entity').split('.')[-1]
                    entity = Entity(
                        entity_id=entity_name,
                        all_equations=all_equations
                    )
                    print(f"Created new Entity object: {entity_name}")
                    
                    # Store Entity object in both places
                    entity_data['entity_object'] = entity
                    if hasattr(self, 'entity_frontend') and self.entity_frontend:
                        self.entity_frontend.current_entity = entity
                
                # Add variable and equation to Entity using its built-in method
                entity.add_variable_equation(root_variable, root_equation, assignments)
                
                print(f"Entity object updated with variable {root_variable}")
                entity.printMe()
                
                # Send Entity object to frontend for display
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.update_entity_from_backend_entity(entity)
                
                # Mark entity as changed but don't send to main backend yet
                self.entity_frontend.markChanged()
            
        except Exception as e:
            print(f"Error handling state variable selection (Entity-based): {e}")
            self.message.emit({
                    "event": "error",
                    "error": f"Error handling state variable selection: {str(e)}"
                    })

    def handle_state_variable_selection(self, assignments, entity_data):
        """Handle state variable selection in create mode"""
        try:
            print(f"Backend handling state variable selection: {assignments}")

            # Extract the selected state variable
            root_variable = assignments.get('root_variable')
            if root_variable:
                # Update the mode to edit
                self.mode = "edit"
                print(f"Mode changed to: {self.mode}")

                # Notify frontend of mode change
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.set_mode("edit")

                # Check if we already have an entity object from previous operations
                existing_entity = None
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                        existing_entity = self.entity_frontend.current_entity
                        print(f"Found existing entity for state selection: {existing_entity.entity_id}")

                if existing_entity:
                    # Update existing entity
                    print(f"Updating existing entity with state variable: {root_variable}")
                    entity = existing_entity

                    # Add state variable to initialization list using Entity method
                    entity.set_init_var(root_variable, True)

                    # Update entity_data with the existing Entity object information
                    entity_data.update({
                            'entity_object': entity,
                            'var_eq_forest': entity.var_eq_forest,
                            'output_vars'  : entity.output_vars,
                            'input_vars'   : entity.input_vars,
                            'init_vars'    : entity.init_vars,
                            'integrators'  : entity.integrators
                            })

                    print(f"=== AFTER STATE VARIABLE ADDITION ===")
                    print(f"Entity var_eq_forest: {entity.var_eq_forest}")
                    print(f"Entity integrators: {entity.integrators}")
                    print(f"Entity output_vars: {entity.output_vars}")
                    print(f"Entity input_vars: {entity.input_vars}")
                    print(f"Entity init_vars: {entity.init_vars}")

                    # Note: Integrators are properly handled by Entity.update_var_eq_tree()
                    # based on equation objects' is_integrator() method
                    
                    # Update entity_data with the latest entity information
                    entity_data.update({
                            'entity_object': entity,
                            'var_eq_forest': entity.var_eq_forest,
                            'output_vars'  : entity.output_vars,
                            'input_vars'   : entity.input_vars,
                            'init_vars'    : entity.init_vars,
                            'integrators'  : entity.integrators
                            })
                else:
                    # Create new entity only if no existing one
                    print("Creating new entity for state variable selection")
                    # Process the state variable selection similar to behavior association
                    entity_data.update({
                            'root_variable'    : root_variable,
                            'definition_method': 'initialization',  # State variables are typically initialized
                            'equation_id'      : None,
                            'assignments'      : assignments
                            })

                    # Create entity with proper parameters
                    entity_name = f"{self.selected_entity_type.get('network', 'unknown')}.{self.selected_entity_type.get('category', 'unknown')}.{self.selected_entity_type.get('entity type', 'unknown')}.new_entity"

                    # Get equations from ontology container - use list_equation_classes for actual Equation objects
                    all_equations = {}
                    if hasattr(self.ontology_container, 'list_equation_classes'):
                        print(
                            f"Using list_equation_classes with {len(self.ontology_container.list_equation_classes)} equations")
                        for eq_obj in self.ontology_container.list_equation_classes:
                            all_equations[eq_obj.eq_id] = eq_obj
                            # Debug: Check if E_93 has is_integrator method
                            if eq_obj.eq_id == 'E_93':
                                print(
                                    f"E_93 object: type={type(eq_obj)}, has_is_integrator={hasattr(eq_obj, 'is_integrator')}")
                                if hasattr(eq_obj, 'is_integrator'):
                                    print(f"E_93.is_integrator(): {eq_obj.is_integrator()}")
                    else:
                        print("list_equation_classes not found, falling back to equation_dictionary")
                        all_equations = getattr(self.ontology_container, 'equation_dictionary', {})

                    # Create entity with the selected state variable and equation
                    # Build the var_eq_forest from the assignments
                    root_equation = assignments.get('root_equation')
                    var_eq_forest = [{}]  # Start with empty tree

                    if root_equation and not assignments.get('use_initialization', False):
                        # Add the equation to the forest
                        var_eq_forest[0][root_equation] = [root_variable]
                        print(f"Added equation {root_equation} with variable {root_variable} to var_eq_forest")

                    # Prepare add_var_eq_info for sophisticated Entity class
                    add_var_eq_info = {}
                    if root_equation and not assignments.get('use_initialization', False):
                        add_var_eq_info[root_variable] = [root_equation]

                    entity = Entity(
                            entity_id=entity_name,
                            all_equations=all_equations,
                            var_eq_forest=var_eq_forest,  # Use the populated forest
                            init_vars=[root_variable],  # Add state variable to initialization list
                            input_vars=[],
                            output_vars=[root_variable]  # Set as output since defined by equation
                            )

                    # Note: Integrators are properly handled by Entity.update_var_eq_tree()
                    # based on equation objects' is_integrator() method

                    print(f"Created entity with var_eq_forest: {entity.var_eq_forest}")
                    print(f"Created entity with output_vars: {entity.output_vars}")
                    print(f"Created entity with init_vars: {entity.init_vars}")
                    print(f"Created entity with integrators: {entity.integrators}")

                    # Original Entity class doesn't have sophisticated analysis methods
                    # Use the Entity as-is with manually populated lists
                    print("Using original Entity class with manual list population")

                    # Update entity_data with the actual Entity object information
                    # Get variable information for defined variables list
                    var_info = None
                    if hasattr(self.ontology_container,
                               'variables') and root_variable in self.ontology_container.variables:
                        var_data = self.ontology_container.variables[root_variable]
                        var_info = {
                                'id'     : root_variable,
                                'label'  : var_data.get('label', root_variable),
                                'network': var_data.get('network', 'unknown')
                                }

                    # For original Entity class, use manually populated lists
                    entity_equations = [root_equation] if root_equation else []

                    print(f"DEBUG: Using manual equation list: {entity_equations}")

                    entity_data.update({
                            'entity_object'    : entity,
                            'var_eq_forest'    : entity.var_eq_forest,
                            'output_vars'      : entity.output_vars,
                            'input_vars'       : entity.input_vars,
                            'init_vars'        : entity.init_vars,
                            'integrators'      : entity.integrators,
                            'defined_variables': [var_info] if var_info else [],
                            # Add selected variable to defined list
                            'equations'        : entity_equations  # Add equations from manual list
                            })

                # Update entity locally - don't send to main backend yet
                print(f"State variable selection processed, entity data: {entity_data}")
                if 'entity_object' in entity_data:
                    entity_data['entity_object'].printMe()
                
                # Mark entity as changed but don't send to main backend yet
                self.entity_frontend.markChanged()

                # Update frontend for immediate display refresh
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if 'entity_object' in entity_data and entity_data['entity_object']:
                        self.entity_frontend.update_entity_from_backend_entity(entity)
                    else:
                        # No Entity object yet - generate lists from entity_data
                        self.generate_lists_from_entity_data(entity_data)

            else:
                print("No valid state variable in selection")

        except Exception as e:
            print(f"Error handling state variable selection: {e}")
            self.message.emit({
                    "event": "error",
                    "error": f"Error handling state variable selection: {str(e)}"
                    })

    def handle_new_variable_addition(self, assignments, entity_data):
        """Handle new variable addition in edit mode"""
        try:
            print(f"Backend handling new variable addition: {assignments}")

            # Extract the new variable information
            root_variable = assignments.get('root_variable')
            if root_variable:
                # Check if we have an existing entity object
                if 'entity_object' in entity_data:
                    entity = entity_data['entity_object']
                    print(f"Updating existing entity with new variable: {root_variable}")

                    # Determine the type of variable based on assignments
                    definition_method = assignments.get('definition_method', 'initialization')
                    equation_id = assignments.get('root_equation')

                    if definition_method == 'initialization':
                        # Add to initialization variables using Entity method
                        entity.set_init_var(root_variable, True)
                    else:
                        # Add to output variables and create equation relationship using Entity method
                        entity.set_output_var(root_variable, True)

                        # Create variable-equation assignments for forest generation
                        var_eq_assignments = self.extract_var_eq_assignments(assignments)
                        if var_eq_assignments:
                            entity.generate_var_eq_forest(var_eq_assignments)
                            entity.update_var_eq_tree()

                    # Update entity_data with the latest entity information
                    entity_data.update({
                            'var_eq_forest': entity.var_eq_forest,
                            'output_vars'  : entity.output_vars,
                            'input_vars'   : entity.input_vars,
                            'init_vars'    : entity.init_vars,
                            'integrators'  : entity.integrators
                            })

                    # Update entity locally - don't send to main backend yet
                    print(f"New variable addition processed, entity data: {entity_data}")
                    entity.printMe()
                    
                    # Mark entity as changed but don't send to main backend yet
                    self.entity_frontend.markChanged()

                    # Update frontend for immediate display refresh
                    if hasattr(self, 'entity_frontend') and self.entity_frontend:
                        self.entity_frontend.update_entity_from_backend_entity(entity)
                else:
                    print("No entity object found in entity_data - cannot add variable")
            else:
                print("No valid new variable in addition")

        except Exception as e:
            print(f"Error handling new variable addition: {e}")
            self.message.emit({
                    "event": "error",
                    "error": f"Error handling new variable addition: {str(e)}"
                    })
