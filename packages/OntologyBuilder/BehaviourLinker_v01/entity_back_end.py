import os
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from Common.classes.entity_v1 import Entity
from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor
from OntologyBuilder.BehaviourLinker_v01.behaviour_association.equation_selector import select_equation_for_variable

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])

# Import the enhanced variable deletion function
from OntologyBuilder.BehaviourLinker_v01.variable_deletion import handle_variable_deletion_with_dependencies


# Error logging utility
def log_error(method_name: str, error: Exception, context: str = ""):
    """Log error with method name and context for debugging"""
    error_msg = f"ERROR in {method_name}"
    if context:
        error_msg += f" ({context})"
    error_msg += f": {str(error)}"
    print(error_msg)  # Keep console output for debugging


class EntityEditorBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self, ontology_container):
        super().__init__()
        self.ontology_container = ontology_container
        self.selected_entity_type = None

    def set_selected_entity_type_or_entity(self, entity_type_data):
        """Set the selected entity type from the main tree"""
        try:
            self.selected_entity_type = entity_type_data

            # Determine if we're in create or edit mode
            if self.selected_entity_type and self.selected_entity_type.get("name"):
                self.mode = "edit"
                # Notify frontend of mode change
                self.entity_frontend.set_mode("edit")
            else:
                self.mode = "create"
                # Notify frontend of mode change
                self.entity_frontend.set_mode("create")

        except Exception as e:
            log_error("set_selected_entity_type_or_entity", e, "setting selected entity type")

    def set_entity_frontend(self, entity_frontend):
        """Set the entity frontend reference for direct updates"""
        self.entity_frontend = entity_frontend

    def process_entity_front_message(self, message):
        """Process messages from the entity editor frontend"""
        event = message.get("event")

        if event == "add_state_variable":
            self.launch_behavior_association_editor(mode='state')
        elif event == "add_variable":
            self.launch_behavior_association_editor(mode='definable')
        elif event == "new_variable_added":
            # Handle new variable addition from frontend
            assignments = message.get("assignments")
            if assignments:
                self.handle_behavior_association(assignments)
        elif event == "def_variable":
            self.launch_equation_association_editor(message.get("var_id"))
        elif event == "delete_variable":
            self.handle_variable_deletion(message.get("var_id"))
        elif event == "save_entity":
            # Handle entity save from Accept button
            entity = message.get('entity')
            if entity:
                # Mark frontend as saved
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.markSaved()

                # Send the completed entity to main backend for final processing
                self.message.emit({
                        "event"        : "entity_data_ready",
                        "entity_object": entity  # Send only the Entity object
                        })

            else:
                self.message.emit({
                        "event": "error",
                        "error": "No entity to save"
                        })

    def launch_equation_association_editor(self, var_id):
        """Launch the equation association editor and handle its response"""
        try:

            # Get variable data from ontology container
            if var_id in self.ontology_container.variables:
                variable_data = self.ontology_container.variables[var_id]

                # Launch equation selector for this specific variable
                assignments = select_equation_for_variable(variable_data, self.ontology_container)

                if assignments:
                    # For direct equation selection, create a simple assignment structure
                    # that handle_behavior_association can understand
                    equation_id = assignments.get('equation_id')
                    use_initialization = assignments.get('use_initialization', False)

                    if use_initialization:
                        # For instantiation, don't include equation in tree/nodes
                        simple_assignments = {
                                'root_variable'     : var_id,
                                'root_equation'     : None,
                                'use_initialization': True,
                                'tree'              : {},  # Empty tree for instantiation
                                'nodes'             : {},  # Empty nodes for instantiation
                                'IDs'               : {}
                                }
                    else:
                        # For equation assignment, include equation in tree structure
                        simple_assignments = {
                                'root_variable'     : var_id,
                                'root_equation'     : equation_id,
                                'use_initialization': False,
                                'tree'              : {0: {'children': [1], 'parent': None}, 1: {'children': [], 'parent': 0}},
                                'nodes'             : {0: var_id, 1: equation_id},
                                'IDs'               : {var_id: 0, equation_id: 1}
                                }

                    # Process the assignments using the same logic as handle_behavior_association
                    self.handle_behavior_association(simple_assignments)

                    # Update frontend to show the changes
                    if hasattr(self, 'entity_frontend') and self.entity_frontend:
                        if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                            self.entity_frontend.update_entity_from_backend_entity(self.entity_frontend.current_entity)
                        else:
                            # Lists are managed by Entity class - no manual generation needed
                            pass
                else:
                    self.message.emit({
                            "event"  : "info",
                            "message": f"Equation association cancelled for {var_id}"
                            })
            else:
                log_error("process_entity_front_message", Exception(f"Variable {var_id} not found"), "def_variable event")
                self.message.emit({
                        "event": "error",
                        "error": f"Variable {var_id} not found"
                        })

        except Exception as e:
            log_error("process_entity_front_message", e, "launching equation association editor")
            self.message.emit({
                    "event": "error",
                    "error": f"Error launching equation association editor: {str(e)}"
                    })

    def launch_behavior_association_editor(self, mode='state'):
        """Launch the behavior association editor and handle its response
        
        Args:
            mode: 'state' for state variables only, 'definable' for variables definable from existing ones
        """
        try:
            # from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor

            entity_data = self.entity_frontend.current_entity_data
            # Get entity type information for rule-based filtering
            entity_type_info = {
                    'network'    : entity_data.get('network', 'unknown'),
                    'category'   : entity_data.get('category', 'unknown'),
                    'entity_type': entity_data.get('entity_type', 'unknown')
                    }

            # Launch the BehaviorAssociation editor with entity type info
            current_entity = None
            if hasattr(self, 'entity_frontend') and self.entity_frontend:
                if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                    current_entity = self.entity_frontend.current_entity

            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info, mode, current_entity)
            if assignments:
                # Process the assignments directly
                self.handle_behavior_association(assignments)
            else:
                # Don't mark as changed when user cancels
                self.message.emit({
                        "event"  : "info",
                        "message": "Behavior association cancelled"
                        })

        except Exception as e:
            log_error("launch_behavior_association_editor", e, f"launching editor in {mode} mode")
            self.message.emit({
                    "event": "error",
                    "error": f"Error launching BehaviorAssociation editor: {str(e)}"
                    })

    def handle_behavior_association(self, assignments):
        """Handle the behavior association assignments from the editor"""
        try:
            if assignments:
                # Extract key information
                root_variable = assignments.get('root_variable')
                root_equation = assignments.get('root_equation')
                use_initialization = assignments.get('use_initialization', False)

                # Check if we already have an entity object from previous operations
                existing_entity = None
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                        existing_entity = self.entity_frontend.current_entity
                        existing_entity.change_classification(root_variable,"none") # Note: here was the problem

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
                    entity = existing_entity

                    # Set up variable-equation relationships using the existing Entity
                    var_eq_assignments = self.extract_var_eq_assignments(assignments)

                    if var_eq_assignments:
                        # Set the root variable as output variable if not already set
                        root_variable = assignments.get('root_variable')

                        if use_initialization:
                            # Add to initialization variables using Entity method
                            entity.set_init_var(root_variable, True)

                            # Immediately refresh GUI to show the new instantiation variable
                            if hasattr(self, 'entity_frontend') and self.entity_frontend:
                                self.entity_frontend.populate_lists_from_entity(entity)
                        else:
                            # Add to output variables and create equation relationship using Entity method
                            entity.set_output_var(root_variable, True)

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
                            # Also remove from output_vars if it was there (to avoid conflicts)
                            entity.set_output_var(root_variable, False)

                            # Immediately refresh GUI to show the new instantiation variable
                            if hasattr(self, 'entity_frontend') and self.entity_frontend:
                                self.entity_frontend.populate_lists_from_entity(entity)
                        # Entity updated successfully

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
                    entity_data = self.entity_frontend.current_entity_data
                    entity_id = entity_data.get('entity_id')

                    # Get equations from ontology container - use equation_entity_dict directly
                    all_equations = getattr(self.ontology_container, 'equation_entity_dict', {})

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
                        entity.update_var_eq_tree()     # Note: update on creation

                        # Update entity_data with the Entity object - lists are managed internally
                        entity_data.update({
                                'entity_object': entity,  # Send the actual Entity object
                                })

                        # IMPORTANT: Store the Entity object in the frontend for future updates
                        self.entity_frontend.current_entity = entity

                # Update entity locally - don't send to main backend yet

                # Mark entity as changed but don't send to main backend yet
                self.entity_frontend.markChanged()

                # Update frontend for immediate display refresh
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if 'entity_object' in entity_data and entity_data['entity_object']:
                        self.entity_frontend.update_entity_from_backend_entity(entity)
                    else:
                        # No Entity object yet - lists will be generated when Entity is created
                        pass

            else:
                log_error("handle_behavior_association", Exception("No assignments"), "no behavior association assignments received")

        except Exception as e:
            log_error("handle_behavior_association", e, "processing behavior association assignments")
            self.message.emit({
                    "event": "error",
                    "error": str(e)
                    })

    def handle_entity_creation(self, entity_data):
        """Handle the final entity creation"""
        try:
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
            log_error("handle_entity_creation", e, "creating entity")
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

        # Extract var_eq_assignments from behavior assignments

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

    def handle_state_variable_selection_entity_based(self, assignments, entity_data):
        """Simplified state variable selection using Entity class only"""
        try:
            # Import Entity class
            from Common.classes.entity_v1 import Entity

            # Get all equations from ontology container
            all_equations = getattr(self.ontology_container, 'equation_entity_dict', {})

            # Extract the selected variable and equation
            root_variable = assignments.get('root_variable')
            root_equation = assignments.get('root_equation')

            if root_variable and root_equation:
                # Update the mode to edit
                self.mode = "edit"

                # Notify frontend of mode change
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.set_mode("edit")

                # Always work with Entity objects - no more entity_data complexity
                entity = None

                # Check if frontend already has an Entity object
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                        entity = self.entity_frontend.current_entity

                # Create new Entity if none exists
                if entity is None:
                    entity_name = entity_data.get('entity_id', 'new_entity').split('.')[-1]
                    entity = Entity(
                            entity_id=entity_name,
                            all_equations=all_equations
                            )

                    # Store Entity object in both places
                    entity_data['entity_object'] = entity
                    if hasattr(self, 'entity_frontend') and self.entity_frontend:
                        self.entity_frontend.current_entity = entity

                # Add variable and equation to Entity using its built-in method
                entity.add_variable_equation(root_variable, root_equation, assignments)

                # Send Entity object to frontend for display
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.update_entity_from_backend_entity(entity)

                # Mark entity as changed but don't send to main backend yet
                self.entity_frontend.markChanged()

        except Exception as e:
            log_error("handle_state_variable_selection", e, "handling state variable selection (Entity-based)")
            self.message.emit({
                    "event": "error",
                    "error": f"Error handling state variable selection: {str(e)}"
                    })

    def handle_state_variable_selection(self, assignments, entity_data):
        """Handle state variable selection in create mode"""
        try:
            # Extract the selected state variable
            root_variable = assignments.get('root_variable')
            if root_variable:
                # Update the mode to edit
                self.mode = "edit"

                # Notify frontend of mode change
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    self.entity_frontend.set_mode("edit")

                # Check if we already have an entity object from previous operations
                existing_entity = None
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                        existing_entity = self.entity_frontend.current_entity

                if existing_entity:
                    # Update existing entity
                    entity = existing_entity

                    # Add state variable to initialization list using Entity method
                    entity.set_init_var(root_variable, True)

                    # Immediately refresh GUI to show the new instantiation variable
                    if hasattr(self, 'entity_frontend') and self.entity_frontend:
                        self.entity_frontend.populate_lists_from_entity(entity)

                    # Update entity_data with the existing Entity object information
                    entity_data.update({
                            'entity_object': entity,
                            'var_eq_forest': entity.var_eq_forest,
                            'output_vars'  : entity.output_vars,
                            'input_vars'   : entity.input_vars,
                            'init_vars'    : entity.init_vars,
                            'integrators'  : entity.integrators
                            })

                    # State variable added successfully

                    # Note: Integrators are properly handled by Entity.update_var_eq_tree()
                    # based on equation objects' is_integrator() method

                    # Update entity_data with the latest entity information
                else:
                    # Create new entity only if no existing one
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
                        for eq_obj in self.ontology_container.equation_entity_dict:
                            all_equations[eq_obj.eq_id] = eq_obj
                    else:
                        all_equations = getattr(self.ontology_container, 'equation_dictionary', {})

                    # Create entity with the selected state variable and equation
                    # Build the var_eq_forest from the assignments
                    root_equation = assignments.get('root_equation')
                    var_eq_forest = [{}]  # Start with empty tree

                    if root_equation and not assignments.get('use_initialization', False):
                        # Add the equation to the forest
                        var_eq_forest[0][root_equation] = [root_variable]

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


                    entity_data.update({
                            'entity_object': entity,
                            # All list data is managed by the Entity object
                            })

                # Update entity locally - don't send to main backend yet

                # Mark entity as changed but don't send to main backend yet
                self.entity_frontend.markChanged()

                # Update frontend for immediate display refresh
                if hasattr(self, 'entity_frontend') and self.entity_frontend:
                    if 'entity_object' in entity_data and entity_data['entity_object']:
                        self.entity_frontend.update_entity_from_backend_entity(entity)
                    else:
                        # No Entity object yet - lists will be generated when Entity is created
                        log_error("handle_state_variable_selection", Exception("No entity object"), "no entity object")
                        pass

            else:
                log_error("handle_state_variable_selection", Exception("No valid state variable"), "no valid state variable in selection")

        except Exception as e:
            log_error("handle_state_variable_selection", e, "handling state variable selection")
            self.message.emit({
                    "event": "error",
                    "error": f"Error handling state variable selection: {str(e)}"
                    })

    def handle_new_variable_addition(self, assignments, entity_data):
        """Handle new variable addition in edit mode"""
        try:
            # Extract the new variable information
            root_variable = assignments.get('root_variable')
            if root_variable:
                # Check if we have an existing entity object
                if 'entity_object' in entity_data:
                    entity = entity_data['entity_object']

                    # Determine the type of variable based on assignments
                    definition_method = assignments.get('definition_method', 'initialization')

                    if definition_method == 'initialization':
                        # Add to initialization variables using Entity method
                        entity.set_init_var(root_variable, True)

                        # Immediately refresh GUI to show the new instantiation variable
                        if hasattr(self, 'entity_frontend') and self.entity_frontend:
                            self.entity_frontend.populate_lists_from_entity(entity)
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

                    # Mark entity as changed but don't send to main backend yet
                    self.entity_frontend.markChanged()

                    # Update frontend for immediate display refresh
                    if hasattr(self, 'entity_frontend') and self.entity_frontend:
                        self.entity_frontend.update_entity_from_backend_entity(entity)
                else:
                    log_error("handle_new_variable_addition", Exception("No entity object"), "no entity object found in entity_data")
            else:
                log_error("handle_new_variable_addition", Exception("No valid variable"), "no valid new variable in addition")

        except Exception as e:
            log_error("handle_new_variable_addition", e, "handling new variable addition")
            self.message.emit({
                    "event": "error",
                    "error": f"Error handling new variable addition: {str(e)}"
                    })

    def handle_variable_deletion(self, var_id):
        """Handle deletion of a variable from the entity using enhanced dependency analysis"""
        try:
            if not var_id:
                log_error("handle_variable_deletion", Exception("No variable ID"), "no variable ID provided for deletion")
                self.message.emit({
                        "event": "error",
                        "error": "No variable selected for deletion"
                        })
                return

            # Check if we have an entity object
            if hasattr(self, 'entity_frontend') and self.entity_frontend:
                if hasattr(self.entity_frontend, 'current_entity') and self.entity_frontend.current_entity:
                    entity = self.entity_frontend.current_entity

                    # Check if variable exists in entity
                    all_variables = entity.get_entity_variables()
                    if var_id not in all_variables:
                        log_error("handle_variable_deletion", Exception(f"Variable {var_id} not found"), f"variable {var_id} not found in entity")
                        self.message.emit({
                                "event": "error",
                                "error": f"Variable {var_id} not found in entity"
                                })
                        return

                    # Ensure forest structure exists before deletion
                    if not hasattr(entity, 'var_eq_forest') or not entity.var_eq_forest:
                        entity.generate_var_eq_forest({})

                    # Use the enhanced variable deletion with dependency analysis
                    success, message, dependent_equations, orphaned_variables = handle_variable_deletion_with_dependencies(entity, var_id)

                    if success:

                        # Mark entity as changed and update frontend
                        self.entity_frontend.markChanged()

                        # Force complete UI refresh
                        self.entity_frontend.populate_lists_from_entity(entity)

                        # Additional aggressive refresh - force model updates
                        self.entity_frontend.clear_all_lists()
                        self.entity_frontend.populate_lists_from_entity(entity)

                        # Force UI update
                        self.entity_frontend.ui.list_outputs.update()
                        self.entity_frontend.ui.list_inputs.update()
                        self.entity_frontend.ui.list_instantiate.update()
                        self.entity_frontend.ui.list_integrators.update()
                        self.entity_frontend.ui.list_included_variables.update()
                        self.entity_frontend.ui.list_not_defined_variables.update()

                        # Send detailed success message
                        full_message = f"Successfully deleted variable {var_id}"
                        if dependent_equations:
                            full_message += f"\nRemoved equations: {sorted(list(dependent_equations))}"
                        if orphaned_variables:
                            full_message += f"\nRemoved orphaned variables: {sorted(list(orphaned_variables))}"

                        # Show remaining counts
                        remaining_vars = entity.get_entity_variables()
                        remaining_eqs = list(entity.all_equations.keys())
                        full_message += f"\nRemaining variables: {len(remaining_vars)}"
                        full_message += f"\nRemaining equations: {len(remaining_eqs)}"

                        self.message.emit({
                                "event"  : "info",
                                "message": full_message
                                })

                else:
                    self.message.emit({
                            "event": "error",
                            "error": "No entity available for variable deletion"
                            })
            else:
                log_error("handle_variable_deletion", Exception("No entity frontend"), "no entity frontend available")
                self.message.emit({
                        "event": "error",
                        "error": "Entity editor not available"
                        })

        except Exception as e:
            log_error("handle_variable_deletion", e, f"deleting variable {var_id}")
            self.message.emit({
                    "event": "error",
                    "error": f"Error deleting variable: {str(e)}"
                    })
