"""Contains the entity class."""
import collections
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypedDict

from typing import Self

from Common.classes import equation


class EntityDict(TypedDict):
    """Creates a new type for a dictionary that stores an entity."""
    index_set: str
    integrators: Dict[str, str]
    var_eq_forest: List[Dict[str, List[str]]]
    init_vars: List[str]
    input_vars: List[str]
    output_vars: List[str]


class Entity():
    """Models an entity."""

    def __init__(
            self,
            entity_id: str,
            all_equations: Dict[str, equation.Equation],
            index_set: Optional[str] = None,
            integrators: Optional[Dict[str, str]] = None,
            var_eq_forest: Optional[List[Dict[str, List[str]]]] = None,
            init_vars: Optional[List[str]] = None,
            input_vars: Optional[List[str]] = None,
            output_vars: Optional[List[str]] = None,
            ) -> None:
        self.entity_id = entity_id
        self.index_set = index_set
        self.integrators = integrators if integrators is not None else {}
        self.var_eq_forest = var_eq_forest if var_eq_forest is not None else [{}]
        self.init_vars = init_vars if init_vars is not None else []
        self.input_vars = input_vars if input_vars is not None else []
        self.output_vars = output_vars if output_vars is not None else []
        self.all_equations = all_equations
        self.is_reservoir = False

        # Initialize local variable classifications tracking
        self.local_variable_classifications = {}  # {var_id: {'classification': 'input'/'output'/'none', 'original_list': 'list_name'}}
        self.classifications_initialized = False

        self.all_included_variables = []
        if entity_id == "Topology" or ">>>" in entity_id:
            self.entity_type = "interface"
            return

        try:
            # Simple split into exactly 4 parts
            self.network, self.category, self.entity_type, self.name = entity_id.split('.', 3)

            # Set index set based on category
            self.index_set = f"{self.category.capitalize()}_{self.entity_type[:4].lower()}"

            # Check if this is a reservoir (special case with | in entity_type)
            if '|' in self.entity_type:
                type_parts = self.entity_type.split('|')
                if len(type_parts) >= 3:
                    mechanism, nature = type_parts[1], type_parts[2]
                    self.is_reservoir = f"{mechanism}|{nature}" == "constant|infinity"

        except ValueError:
            # If split fails, set defaults
            self.entity_type = "unknown"
            self.index_set = "Unknown"

        self.temp_var_eq_forest = None
        self.merge_conflicts = {}
        self.merged_vars = {}
        self.undo_merging = {}


    def create_variant(self, new_name):
        """Create a variant of this entity with the given name.

        Args:
            new_name: Name for the new variant

        Returns:
            Entity: A new entity that is a variant of this one
        """
        import copy
        variant = copy.deepcopy(self)
        variant.entity_id = new_name

        # Add variant relationship metadata
        if not hasattr(variant, 'variant_of'):
            variant.variant_of = self.entity_id

        return variant

    # def create_new_instance(self, entity_id, entity_type=None):
    #     """Create a completely new instance with default values.
    #
    #     Args:
    #         entity_id: Full ID for the new instance
    #         entity_type: Optional type for the new instance
    #
    #     Returns:
    #         Entity: A new entity instance
    #     """
    #     new_entity = Entity(
    #             entity_id=entity_id,
    #             all_equations={},  # Will be populated by the caller
    #             index_set=self.index_set if hasattr(self, 'index_set') else "",
    #             )
    #
    #     # Set default properties
    #     if not hasattr(new_entity, 'is_reservoir'):
    #         new_entity.is_reservoir = False
    #     if entity_type:
    #         new_entity.entity_type = entity_type
    #
    #     return new_entity

    def has_integrators(self) -> bool:
        return bool(self.integrators)

    def integrators_info(self):
        """Get integrator variable-equation pairs from forest."""
        forest_data = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
        
        # Build mapping of variable -> equation for integrators
        integrator_pairs = []
        for equation in forest_data['all_equations']:
            if (hasattr(self, 'all_equations') and 
                equation in self.all_equations and 
                self.all_equations[equation].is_integrator()):
                var_id = self.all_equations[equation].lhs["global_ID"]
                integrator_pairs.append((var_id, equation))
        
        return integrator_pairs
    
    def get_integrator_vars(self):
        """Get integrator variables from forest."""
        forest_data = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
        return sorted(list(forest_data['integrators']))

    def get_integrators_eq(self):
        """Get integrator equations from forest."""
        forest_data = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
        
        # Build mapping of variable -> equation for integrators
        integrator_eqs = {}
        for equation in forest_data['all_equations']:
            if (hasattr(self, 'all_equations') and 
                equation in self.all_equations and 
                self.all_equations[equation].is_integrator()):
                var_id = self.all_equations[equation].lhs["global_ID"]
                integrator_eqs[var_id] = equation
        
        return sorted(list(integrator_eqs.values()))

    def get_equations(self):
        equations = []
        for tree in self.var_eq_forest:
            equations.extend([
                    key
                    for key in tree
                    if "E_" in key
                    ])

        return sorted(equations)

    def _get_all_vars_equs_vars_in_eqs_and_integrators_from_forest(self):
        """Helper method to get all variables and their categorization from forest."""
        all_variables = set()
        all_equations = set()
        equation_defined_vars = set()
        integrators = set()
        
        if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
            for tree in self.var_eq_forest:
                for key, values in tree.items():
                    if key.startswith('V_'):
                        all_variables.add(key)
                        # Variables with values are defined by equations
                        if values:
                            equation_defined_vars.add(key)
                    
                    if key.startswith('E_'):
                        all_equations.add(key)
                        # Find integrator equations
                        if (hasattr(self, 'all_equations') and 
                            key in self.all_equations and 
                            self.all_equations[key].is_integrator()):
                            var_id = self.all_equations[key].lhs["global_ID"]
                            integrators.add(var_id)
        
        return {
            'all_variables': all_variables,
            'all_equations': all_equations,
            'equation_defined_vars': equation_defined_vars,
            'integrators': integrators
        }
    
    def get_entity_variables(self):
        """Get all variables included in the entity."""
        forest_data = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
        
        # Combine variables from forest, integrators, and init variables
        all_vars = set(forest_data['all_variables'])
        all_vars.update(forest_data['integrators'])
        # Include init variables that might not be in forest (for instantiation)
        all_vars.update(set(getattr(self, 'init_vars', [])))
        
        return sorted(list(all_vars))

    def change_classification(self, var_id, classification):
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>move classification of variable {var_id} to {classification}")
        self.local_variable_classifications[var_id]["classification"] = classification

        pass

    def build_local_variable_classifications(self, variables=None):
        """Build local dictionary tracking variable classifications on first-time calculation"""
        try:
            # Clear existing classifications
            self.local_variable_classifications.clear()
            
            # Use provided variables dict or get from ontology if available
            if variables is None and hasattr(self, 'all_equations'):
                # Try to get variables from equations or other source
                variables = {}
            
            # Classify variables based on their current entity membership
            for var_id in self.output_vars:
                self.local_variable_classifications[var_id] = {
                    'classification': 'output',
                    'original_list': 'list_outputs'
                }
            
            for var_id in self.input_vars:
                self.local_variable_classifications[var_id] = {
                    'classification': 'input', 
                    'original_list': 'list_inputs'
                }
            
            for var_id in self.get_variables_to_be_instantiated():
                self.local_variable_classifications[var_id] = {
                    'classification': 'instantiate',
                    'original_list': 'list_instantiate'
                }
            
            for var_id in self.get_pending_vars():
                self.local_variable_classifications[var_id] = {
                    'classification': 'pending',
                    'original_list': 'list_not_defined_variables'
                }
            
            for var_id in self.get_integrator_vars():
                self.local_variable_classifications[var_id] = {
                    'classification': 'integrator',
                    'original_list': 'list_integrators'
                }
            
            # Mark that classifications have been initialized
            self.classifications_initialized = True
            
            print(f"Entity {self.entity_id}: Built local variable classifications: {len(self.local_variable_classifications)} variables tracked")
            
        except Exception as e:
            print(f"Error building local variable classifications for entity {self.entity_id}: {str(e)}")
            self.classifications_initialized = False

    def get_input_vars(self):
        """Get input variables (variables not defined by equations)."""
        return sorted(list(self.input_vars))

    def set_input_var(self, var_id, is_input):
        """Legacy method for backward compatibility. Consider using forest-based approach."""
        if not hasattr(self, 'input_vars'):
            self.input_vars = []
        if is_input:
            if var_id not in self.input_vars:
                self.input_vars.append(var_id)
        else:
            if var_id in self.input_vars:
                self.input_vars.remove(var_id)

    def get_output_vars(self, all_variables=None):
        """Get output variables (variables defined by equations).
        
        Args:
            all_variables: Optional Dict[str, Variable] to filter out transport variables.
                          If provided, variables with type 'transport' will be excluded.
        
        Returns:
            List of variable IDs that are output variables (excluding transport variables if all_variables provided)
        """
        return self.get_equation_defined_vars(all_variables)

    # def get_transport_vars(self, all_variables):
    #     """Get all transport variables in the entity.
    #
    #     Args:
    #         all_variables: Dict[str, Variable] containing variable information
    #
    #     Returns:
    #         List of variable IDs that have type 'transport'
    #     """
    #     transport_vars = set()
    #
    #     # Get all variables in the entity
    #     entity_var_ids = set(self.get_variables())
    #
    #     # Filter for transport variables
    #     for var_id in entity_var_ids:
    #         if var_id in all_variables:
    #             var_obj = all_variables[var_id]
    #             if hasattr(var_obj, 'type') and var_obj.type == 'transport':
    #                 transport_vars.add(var_id)
    #
    #     return sorted(list(transport_vars))

    def get_equation_defined_vars(self, all_variables=None):
        """Get variables that are defined by equations.
        
        This is the explicit method for accessing equation-defined variables.
        Returns variables that have defining equations in the var_eq_forest.
        
        Args:
            all_variables: Optional Dict[str, Variable] to filter out transport variables.
                          If provided, variables with type 'transport' will be excluded.
        
        Returns:
            List of variable IDs defined by equations (excluding transport variables if all_variables provided)
        """
        forest_data = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
        equation_defined_vars = set(forest_data['equation_defined_vars'])
        
        # # Filter out transport variables if all_variables is provided
        # #NOTE: Not used because the node is not alllowed to have transport variagles
        # if all_variables is not None:
        #     non_transport_vars = set()
        #     for var_id in equation_defined_vars:
        #         if var_id in all_variables:
        #             var_obj = all_variables[var_id]
        #             if hasattr(var_obj, 'type') and var_obj.type != 'transport':
        #                 non_transport_vars.add(var_id)
        #         else:
        #             # If variable not found in all_variables, include it (fallback behavior)
        #             non_transport_vars.add(var_id)
        #     equation_defined_vars = non_transport_vars

        return sorted(list(equation_defined_vars))

    def set_output_var(self, var_id, is_output):
        """Legacy method for backward compatibility. Consider using forest-based approach."""
        if not hasattr(self, 'output_vars'):
            self.output_vars = []
        if is_output:
            if var_id not in self.output_vars:
                self.output_vars.append(var_id)
        else:
            if var_id in self.output_vars:
                self.output_vars.remove(var_id)

    def get_init_vars(self):
        """Get initialization variables."""
        # Init vars are still stored as an attribute since they're user-defined
        return sorted(getattr(self, 'init_vars', []))

    def set_init_var(self, var_id, is_init):
        """Set a variable as initialization variable."""
        if not hasattr(self, 'init_vars'):
            self.init_vars = []
        if is_init:
            if var_id not in self.init_vars:
                self.init_vars.append(var_id)
                # Also add to tree structure
                self._add_variable_to_tree(var_id)
        else:
            if var_id in self.init_vars:
                self.init_vars.remove(var_id)
                # Also remove from tree structure
                self._remove_variable_from_tree(var_id)

    def _remove_variable_from_tree(self, var_id):
        """Remove a variable from the tree structure."""
        if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
            for tree in self.var_eq_forest:
                if var_id in tree:
                    del tree[var_id]
                    print(f"Removed {var_id} from tree")
                    break

    def _add_variable_to_tree(self, var_id):
        """Add a variable to the tree structure."""
        if not hasattr(self, 'var_eq_forest'):
            self.var_eq_forest = []
        
        # Handle empty forest case
        if not self.var_eq_forest:
            self.var_eq_forest = [{}]
        
        # Find first non-empty tree or use first tree
        target_tree = None
        for tree in self.var_eq_forest:
            if tree:  # Non-empty tree
                target_tree = tree
                break
        if target_tree is None:
            # All trees are empty, use first one
            target_tree = self.var_eq_forest[0]
        
        # Add variable to tree
        target_tree[var_id] = []
        print(f"Added {var_id} to tree with empty dependencies")

    def get_pending_vars(self):
        """Get variables that are not yet defined (need instantiation)."""
        forest_data = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
        
        # Variables without defining equations
        all_included_vars = self.get_entity_variables()
        equation_defined_variables = self.get_equation_defined_vars()
        init_vars = self.get_init_vars()
        pending_vars = set(all_included_vars) - set(equation_defined_variables) - set(init_vars)
        
        return sorted(list(pending_vars))

    def get_variables_to_be_instantiated(self):
        """Get variables that need to be instantiated.
        
        These are variables that either:
        1. Have been marked to be instantiated in the equation interface (init_vars)
        2. Have an RHS that contains the instantiate operator
        """
        # Start with explicitly marked initialization variables
        instantiation_vars = set(self.init_vars)
        
        # Check for variables with equations that have instantiate operator
        # Get all variables in the entity
        all_vars = self.get_entity_variables()
        
        for var_id in all_vars:
            # Find the defining equation for this variable
            defining_eqs = self.get_eq_for_var(var_id)
            
            if defining_eqs:
                for eq_id in defining_eqs:
                    if eq_id in self.all_equations:
                        equation = self.all_equations[eq_id]
                        is_instantiation = equation.is_instantiation_eq()
                        if is_instantiation:
                            instantiation_vars.add(var_id)
        
        return sorted(list(instantiation_vars))

    def get_not_defined_variables(self):
        """Get variables that are not yet defined (need instantiation)"""
        return self.get_pending_vars()

    def is_init(self, var_id):
        return var_id in self.init_vars

    # def is_var_top_level(self, var_id):
    #     if var_id not in self.output_vars:
    #         return False
    #
    #     self.output_vars.remove(var_id)
    #     deleted_vars = self.generate_var_eq_forest({})[2]
    #     self.output_vars.append(var_id)
    #
    #     if var_id in deleted_vars:
    #         return True
    #     else:
    #         return False

    # @classmethod
    # def from_root(
    #   cls,
    #   entity_name: str,
    #   root_var_id: str,
    #   root_eq_id: str,
    #   all_equations: Dict[str, equation.Equation],
    # ) -> Self:
    #   """Provides an alternative constructor.

    #   Used when a new entity is going to be created and only information
    #     about the root is defined.

    #   Args:
    #       entity_name (str): Name of the entity.
    #       root_var_id (str): Id of the root variable.
    #       root_eq_id (str): Id of the root equation.
    #       all_equations (List[equation.Equation]): All the equations in
    #         the Ontology.

    #   Returns:
    #       Self: An instance of the clase initialized with the information
    #         of the root.
    #   """
    #   # `entity_equations` are found by doing a BFS on a graph where
    #   # variables and equations are nodes and an arc exist between them
    #   # if the equation contains the variable.
    #   entity_equations = {}
    #   entity_equations[root_eq_id] = all_equations[root_eq_id]

    #   entity_variables = set()
    #   entity_variables.add(root_var_id)

    #   queue = collections.deque()
    #   queue.append(root_eq_id)

    #   while queue:
    #     item_id = queue.popleft()
    #     if "E_" in item_id:
    #       for var_id in all_equations[item_id].get_incidence_list():
    #         # TODO Find a way to not add constants.
    #         if var_id not in entity_variables:
    #           entity_variables.add(var_id)
    #           queue.append(var_id)

    #     if "V_" in item_id:
    #       for eq_id, eq in all_equations.items():
    #         if eq_id not in entity_equations and eq.contains_var(item_id):
    #           entity_equations[eq_id] = eq
    #           queue.append(eq_id)

    #   # All equations are unused except for the root equation.
    #   unused_eq_ids = list(entity_equations.keys()).remove(root_eq_id)

    #   # Creating a new instance of the class with the minimum information.
    #   instance =  cls(
    #     entity_name,
    #     root_var_id,
    #     root_eq_id,
    #     unused_eq_ids,
    #     entity_equations,
    #   )

    #   # `var_eq_info` only contains information about the root.
    #   var_eq_info = {}
    #   var_eq_info[root_var_id] = [root_eq_id]

    #    # Generating and updating `var_eq_tree`.
    #   instance.generate_var_eq_tree(var_eq_info)
    #   instance.update_var_eq_tree()

    #   return instance

    def update_var_eq_tree(self) -> None:
        """Updates the variable-equation tree.

        The variable-equation tree is updated with the last tree generated
          by the method `generate_var_eq_tree`.
        """
        self.var_eq_forest = self.temp_var_eq_forest

        # Removing all variables that are not in the entity from the lists
        # input, output and init
        all_vars = set(self.get_entity_variables())
        self.input_vars = list(
                set(self.input_vars).intersection(all_vars)
                )
        self.output_vars = list(
                set(self.output_vars).intersection(all_vars)
                )
        self.init_vars = list(
                set(self.init_vars).intersection(all_vars)
                )
        # Update stored integrators using dynamic method for consistency
        # This maintains backward compatibility while avoiding duplicate logic
        integrator_info = self.integrators_info()
        self.integrators = {var_id: eq_id for var_id, eq_id in integrator_info}
        
        # Use the comprehensive list building method to ensure consistency
        self.build_variable_lists_from_forest()

    # def rebuild_from_components(self, deleted_var_id, dependent_equations, orphaned_variables, cleaned_forest):
    #     """Rebuild entity from scratch after variable deletion.
    #
    #     This method creates a clean entity structure from the remaining components,
    #     avoiding all the patching and workarounds needed for incremental updates.
    #
    #     Args:
    #         deleted_var_id: The variable ID that was deleted
    #         dependent_equations: Set of equation IDs that were deleted
    #         orphaned_variables: Set of variable IDs that were orphaned/deleted
    #         cleaned_forest: The cleaned var_eq_forest structure
    #     """
    #     print(f"=== REBUILDING ENTITY FROM SCRATCH ===")
    #     print(f"Deleted variable: {deleted_var_id}")
    #     print(f"Deleted equations: {dependent_equations}")
    #     print(f"Deleted variables: {orphaned_variables}")
    #     print(f"Cleaned forest: {cleaned_forest}")
    #
    #     # Save original state for type determination
    #     original_output_vars = set(self.output_vars)
    #     original_input_vars = set(self.input_vars)
    #     original_init_vars = set(self.init_vars)
    #     original_all_equations = getattr(self, 'all_equations', {}).copy()
    #
    #     # Clear everything completely
    #     self.output_vars = []
    #     self.input_vars = []
    #     self.init_vars = []
    #     self.integrators = {}
    #     self.all_equations = {}
    #     self.var_eq_forest = cleaned_forest
    #
    #     # Rebuild from clean forest
    #     remaining_variables = set()
    #     remaining_equations = set()
    #
    #     print(f"Processing cleaned forest: {cleaned_forest}")
    #     print(f"Original all_equations keys: {list(original_all_equations.keys())}")
    #
    #     # First pass: collect all variables mentioned in equations
    #     variables_mentioned_in_equations = set()
    #     for tree in cleaned_forest:
    #         for key, values in tree.items():
    #             if key.startswith('E_') and values:
    #                 for var_id in values:
    #                     if var_id.startswith('V_'):
    #                         variables_mentioned_in_equations.add(var_id)
    #
    #     print(f"Variables mentioned in equations: {variables_mentioned_in_equations}")
    #
    #     # Second pass: process forest items and rebuild complete structure
    #     rebuilt_forest = []
    #     for tree in cleaned_forest:
    #         rebuilt_tree = {}
    #         for key, values in tree.items():
    #             print(f"Processing forest item: {key} -> {values}")
    #             if key.startswith('V_'):
    #                 remaining_variables.add(key)
    #                 # Determine variable type from original classification
    #                 if key in original_output_vars:
    #                     self.output_vars.append(key)
    #                     print(f"    Added to output_vars: {key}")
    #                 elif key in original_input_vars:
    #                     self.input_vars.append(key)
    #                     print(f"    Added to input_vars: {key}")
    #                 elif key in original_init_vars:
    #                     self.init_vars.append(key)
    #                     print(f"    Added to init_vars: {key}")
    #
    #                 # Add variable to rebuilt tree
    #                 rebuilt_tree[key] = values
    #
    #             elif key.startswith('E_'):
    #                 remaining_equations.add(key)
    #                 print(f"    Found equation: {key}")
    #                 # Restore original equation object if available
    #                 if key in original_all_equations:
    #                     self.all_equations[key] = original_all_equations[key]
    #                     print(f"    Restored equation {key}: {original_all_equations[key]}")
    #                 else:
    #                     print(f"    WARNING: Equation {key} not found in original_all_equations!")
    #                     print(f"    Available equations: {list(original_all_equations.keys())}")
    #
    #                 # Add equation to rebuilt tree
    #                 rebuilt_tree[key] = values
    #
    #         # Add missing variables that are mentioned in equations but not as keys
    #         for var_id in variables_mentioned_in_equations:
    #             if var_id not in rebuilt_tree:
    #                 print(f"Adding missing variable to forest: {var_id}")
    #                 rebuilt_tree[var_id] = []
    #                 remaining_variables.add(var_id)
    #
    #                 # Determine variable type from original classification
    #                 if var_id in original_output_vars:
    #                     self.output_vars.append(var_id)
    #                     print(f"    Added to output_vars: {var_id}")
    #                 elif var_id in original_input_vars:
    #                     self.input_vars.append(var_id)
    #                     print(f"    Added to input_vars: {var_id}")
    #                 elif var_id in original_init_vars:
    #                     self.init_vars.append(var_id)
    #                     print(f"    Added to init_vars: {var_id}")
    #
    #         if rebuilt_tree:  # Only add non-empty trees
    #             rebuilt_forest.append(rebuilt_tree)
    #
    #     # Update the forest with the rebuilt structure
    #     self.var_eq_forest = rebuilt_forest
    #     print(f"Rebuilt forest: {self.var_eq_forest}")
    #
    #     # Rebuild integrators from remaining components
    #     print(f"Rebuilding integrators from rebuilt forest...")
    #     print(f"Rebuilt forest: {self.var_eq_forest}")
    #     print(f"Available equations: {list(self.all_equations.keys())}")
    #
    #     for tree in self.var_eq_forest:
    #         for key, values in tree.items():
    #             if key.startswith('E_') and values and key in self.all_equations:
    #                 equation = self.all_equations[key]
    #                 print(f"Checking equation {key}: {equation}")
    #
    #                 # Check if this is an integrator equation
    #                 is_integrator = equation.is_integrator()
    #                 print(f"  Equation.is_integrator(): {is_integrator}")
    #
    #                 print(f"  Is integrator: {is_integrator}")
    #
    #                 # If it's an integrator, find the variable it defines
    #                 if is_integrator:
    #                     print(f"  Equation {key} is an integrator, looking for variables...")
    #                     for var in values:
    #                         print(f"    Checking variable {var}: starts with V_? {var.startswith('V_')}, in remaining_variables? {var in remaining_variables}")
    #                         if var.startswith('V_') and var in remaining_variables:
    #                             self.integrators[var] = key
    #                             print(f"  Rebuilt integrator: {var} -> {key}")
    #                             break
    #                     else:
    #                         print(f"  No suitable variable found in values: {values}")
    #
    #     print(f"Entity rebuilt successfully:")
    #     print(f"  output_vars: {self.output_vars}")
    #     print(f"  input_vars: {self.input_vars}")
    #     print(f"  init_vars: {self.init_vars}")
    #     print(f"  integrators: {self.integrators}")
    #     print(f"  all_equations count: {len(self.all_equations)}")
    #     print(f"  var_eq_forest: {self.var_eq_forest}")
    #     print(f"=== END ENTITY REBUILD ===")
    #
    #     # Ensure lists are consistent with the rebuilt forest
    #     self.build_variable_lists_from_forest()

    def build_variable_lists_from_forest(self):
        """Legacy method - now uses dynamic computation from forest.
        
        All variable lists are now computed dynamically using the getter methods.
        This method is kept for backward compatibility but no longer stores cached lists.
        """
        print(f"=== BUILDING VARIABLE LISTS FROM FOREST (LEGACY) ===")
        print(f"All variable lists are now computed dynamically.")
        print(f"Use get_variables(), get_input_vars(), get_output_vars(), etc. directly.")
        
        # Initialize init_vars if not present (only user-defined variables need storage)
        if not hasattr(self, 'init_vars') or not self.init_vars:
            self.init_vars = []
        
        # Show current dynamic values for verification
        print(f"Current dynamic values:")
        print(f"  all_variables: {self.get_entity_variables()}")
        print(f"  output_vars: {self.get_output_vars()}")
        print(f"  input_vars: {self.get_input_vars()}")
        print(f"  init_vars: {self.get_init_vars()}")
        print(f"  integrators: {self.get_integrator_vars()}")
        print(f"=== END BUILDING VARIABLE LISTS ===")

    def delete_variable_with_dependencies(self, var_id):
        """Delete a variable and all its dependencies from the entity.
        
        This method performs recursive dependency analysis in both directions:
        1. Find equations that depend on the deleted variable
        2. Find all variables that appear in those equations (LHS and RHS)
        3. Recursively find equations that depend on those variables
        4. Continue until no more dependencies are found
        5. Remove all discovered variables and equations
        
        Args:
            var_id: The variable ID to delete
            
        Returns:
            tuple: (success, message, dependent_equations, orphaned_variables)
        """
        try:
            print(f"=== RECURSIVE VARIABLE DELETION: {var_id} ===")
            
            # Print tree BEFORE deletion
            print(f"=== TREE BEFORE DELETION ===")
            before = self.all_included_variables
            print(f"Before deletion: {before}")

            if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
                for i, tree in enumerate(self.var_eq_forest):
                    print(f"Tree {i}:")
                    for key, values in tree.items():
                        print(f"  {key} -> {values}")
            else:
                print("No var_eq_forest found")
            print(f"=== END TREE BEFORE ===")
            
            dependent_equations = set()
            orphaned_variables = set()
            variables_to_delete = {var_id}  # Start with the original variable
            equations_to_delete = set()
            
            # === RECURSIVE DEPENDENCY ANALYSIS ===
            # First, find which tree contains the variable to delete
            target_tree_idx = None
            if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
                for tree_idx, tree in enumerate(self.var_eq_forest):
                    if var_id in tree:
                        target_tree_idx = tree_idx
                        print(f"    Found {var_id} in tree {tree_idx}")
                        break
            
            if target_tree_idx is None:
                print(f"    Variable {var_id} not found in any tree")
                return False, f"Variable {var_id} not found in any tree", set(), set()
            
            changed = True
            iteration = 0
            
            while changed and iteration < 10:  # Prevent infinite loops
                changed = False
                iteration += 1
                print(f"  Iteration {iteration}: vars_to_delete={variables_to_delete}, equations_to_delete={equations_to_delete}")
                
                # Only search within the target tree, not across all trees
                current_equations = set()
                if hasattr(self, 'var_eq_forest') and self.var_eq_forest and target_tree_idx is not None:
                    tree = self.var_eq_forest[target_tree_idx]
                    print(f"    Analyzing tree {target_tree_idx} for equations containing {variables_to_delete}...")
                    
                    # Find equations that depend on current variables to delete
                    for var_key, var_values in tree.items():
                        if var_key.startswith('V_') and var_key in variables_to_delete:
                            # This variable depends on these equations
                            for eq in var_values:
                                if eq.startswith('E_'):
                                    current_equations.add(eq)
                                    print(f"        Found {var_key} depends on {eq}: {var_values}")
                    
                    # Also find equations that contain variables to delete
                    for eq_key, eq_values in tree.items():
                        if eq_key.startswith('E_'):
                            # Check if any variable to delete appears in this equation
                            vars_in_eq = [var for var in eq_values if var in variables_to_delete]
                            if vars_in_eq:
                                current_equations.add(eq_key)
                                print(f"        Found {eq_key} contains {vars_in_eq}: {eq_values}")
                
                if current_equations - equations_to_delete:
                    new_eqs = current_equations - equations_to_delete
                    equations_to_delete.update(new_eqs)
                    changed = True
                    print(f"    Found new equations to delete: {new_eqs}")
                
                # Find all variables that appear in equations to delete (within target tree only)
                current_variables = set()
                if hasattr(self, 'var_eq_forest') and self.var_eq_forest and target_tree_idx is not None:
                    tree = self.var_eq_forest[target_tree_idx]
                    print(f"    Analyzing tree {target_tree_idx} for variables in equations {equations_to_delete}...")
                    
                    # Find variables that appear in equations to delete
                    for eq_key, eq_values in tree.items():
                        if eq_key in equations_to_delete:
                            # Add all variables from this equation (both LHS and RHS)
                            vars_in_eq = [var for var in eq_values if var.startswith('V_')]
                            for var in vars_in_eq:
                                current_variables.add(var)
                            print(f"        Found variables in {eq_key}: {vars_in_eq}")
                    
                    # Find variables that depend on equations to delete (reverse dependency)
                    for var_key, var_values in tree.items():
                        if var_key.startswith('V_'):
                            # Check if this variable depends on any equation to delete
                            eq_dependencies = [eq for eq in var_values if eq in equations_to_delete]
                            if eq_dependencies:
                                current_variables.add(var_key)
                                print(f"        Found {var_key} depends on {eq_dependencies}: {var_values}")
                
                if current_variables - variables_to_delete:
                    new_vars = current_variables - variables_to_delete
                    variables_to_delete.update(new_vars)
                    changed = True
                    print(f"    Found new variables to delete: {new_vars}")
            
            print(f"Final sets after {iteration} iterations:")
            print(f"  Variables to delete: {variables_to_delete}")
            print(f"  Equations to delete: {equations_to_delete}")
            
            # Ensure we always have at least the original variable
            if var_id not in variables_to_delete:
                variables_to_delete.add(var_id)
                print(f"  Added original variable {var_id} to deletion set")
            
            # === STEP 1: Remove all variables to delete (only from target tree) ===
            print(f"Removing {len(variables_to_delete)} variables from tree {target_tree_idx}...")
            if hasattr(self, 'var_eq_forest') and self.var_eq_forest and target_tree_idx is not None:
                tree = self.var_eq_forest[target_tree_idx]
                # Remove variables from target tree only
                variables_to_remove = [var for var in tree.keys() if var in variables_to_delete]
                for var in variables_to_remove:
                    del tree[var]
                    print(f"  Removed variable {var} from tree {target_tree_idx}")
            
            # === STEP 2: Remove all equations to delete (only from target tree) ===
            print(f"Removing {len(equations_to_delete)} equations from tree {target_tree_idx}...")
            if hasattr(self, 'var_eq_forest') and self.var_eq_forest and target_tree_idx is not None:
                tree = self.var_eq_forest[target_tree_idx]
                equations_to_remove = [eq for eq in tree.keys() if eq in equations_to_delete]
                for eq in equations_to_remove:
                    del tree[eq]
                    print(f"  Removed equation {eq} from tree {target_tree_idx}")
            
            # === STEP 3: Clean up any remaining references (only in target tree) ===
            # Remove deleted variables from any remaining equation definitions in target tree
            if hasattr(self, 'var_eq_forest') and self.var_eq_forest and target_tree_idx is not None:
                tree = self.var_eq_forest[target_tree_idx]
                for key, values in tree.items():
                    if key.startswith('E_') and values:
                        # Filter out any deleted variables
                        filtered_values = [v for v in values if v not in variables_to_delete]
                        if len(filtered_values) != len(values):
                            tree[key] = filtered_values
                            print(f"  Cleaned equation {key}: removed {len(values) - len(filtered_values)} deleted variables")
            
            # === STEP 4: Update integrators ===
            if hasattr(self, 'integrators'):
                integrators_to_remove = variables_to_delete.intersection(self.integrators.keys())
                for var in integrators_to_remove:
                    del self.integrators[var]
                    print(f"  Removed {var} from integrators")
            
            # === STEP 4.5: Remove deleted variables from all lists ===
            # Always remove deleted variables from lists, not just when tree is empty
            if hasattr(self, 'init_vars'):
                init_vars_to_remove = variables_to_delete.intersection(self.init_vars)
                for var in init_vars_to_remove:
                    self.init_vars.remove(var)
                    print(f"  Removed {var} from init_vars")
            if hasattr(self, 'input_vars'):
                input_vars_to_remove = variables_to_delete.intersection(self.input_vars)
                for var in input_vars_to_remove:
                    self.input_vars.remove(var)
                    print(f"  Removed {var} from input_vars")
            if hasattr(self, 'output_vars'):
                output_vars_to_remove = variables_to_delete.intersection(self.output_vars)
                for var in output_vars_to_remove:
                    self.output_vars.remove(var)
                    print(f"  Removed {var} from output_vars")
            
            # === STEP 5: Update consistency ===
            self.update_var_eq_tree()
            
            # === STEP 5.5: Clear variable lists if tree is empty ===
            if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
                tree_is_empty = all(len(tree) == 0 for tree in self.var_eq_forest)
                if tree_is_empty:
                    print("  Tree is empty - clearing all variable lists")
                    if hasattr(self, 'init_vars'):
                        self.init_vars = []
                    if hasattr(self, 'input_vars'):
                        self.input_vars = []
                    if hasattr(self, 'output_vars'):
                        self.output_vars = []
                    if hasattr(self, 'integrators'):
                        self.integrators = {}
            
            # === STEP 6: Force regeneration of all lists from tree ===
            print("Regenerating lists from tree...")
            # The lists will be regenerated by the existing dynamic methods when get_all_variables() is called
            
            # Print tree AFTER deletion
            print(f"=== TREE AFTER DELETION ===")
            if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
                for i, tree in enumerate(self.var_eq_forest):
                    print(f"Tree {i}:")
                    for key, values in tree.items():
                        print(f"  {key} -> {values}")
            else:
                print("No var_eq_forest found after deletion")
            print(f"=== END TREE AFTER ===")
            after = self.all_included_variables
            print(f"After deletion: {after}")
            
            # === STEP 6: Build summary message ===
            orphaned_variables = variables_to_delete - {var_id}  # All other variables are "orphaned"
            dependent_equations = equations_to_delete
            
            message = f"Deleted variable {var_id}"
            if dependent_equations:
                message += f" and {len(dependent_equations)} dependent equation(s)"
            if orphaned_variables:
                message += f" and {len(orphaned_variables)} additional variable(s)"
            
            print(f"Recursive deletion complete: {message}")
            print(f"  - Original variable: {var_id}")
            print(f"  - Additional variables: {orphaned_variables}")
            print(f"  - Dependent equations: {dependent_equations}")
            print(f"  - Total iterations: {iteration}")
            
            return True, message, dependent_equations, orphaned_variables
            
        except Exception as e:
            print(f"Error in delete_variable_with_dependencies: {e}")
            return False, f"Error deleting variable: {str(e)}", set(), set()

    # def list_all_variables_for_selection(self):
    #     """List all variables in the entity organized by category for selection.
    #
    #     This method displays all variables grouped into:
    #     - All variables
    #     - Input variables
    #     - Output variables
    #     - Initialization variables
    #     - Integrator variables
    #
    #     Returns:
    #         dict: Dictionary with variable categories as keys and lists of variable IDs as values
    #     """
    #     all_vars = self.get_entity_variables()
    #     input_vars = self.get_input_vars()
    #     output_vars = self.get_output_vars()
    #     init_vars = self.get_init_vars()
    #     integrator_vars = self.get_integrator_vars()
    #
    #     print("=== AVAILABLE VARIABLES FOR SELECTION ===")
    #     print(f"ALL VARIABLES ({len(all_vars)}):")
    #     for i, var in enumerate(all_vars, 1):
    #         print(f"  {i:2d}. {var}")
    #
    #     print(f"\nINPUT VARIABLES ({len(input_vars)}):")
    #     for i, var in enumerate(input_vars, 1):
    #         print(f"  {i:2d}. {var}")
    #
    #     print(f"\nOUTPUT VARIABLES ({len(output_vars)}):")
    #     for i, var in enumerate(output_vars, 1):
    #         print(f"  {i:2d}. {var}")
    #
    #     print(f"\nINITIALIZATION VARIABLES ({len(init_vars)}):")
    #     for i, var in enumerate(init_vars, 1):
    #         print(f"  {i:2d}. {var}")
    #
    #     print(f"\nINTEGRATOR VARIABLES ({len(integrator_vars)}):")
    #     for i, var in enumerate(integrator_vars, 1):
    #         print(f"  {i:2d}. {var}")
    #
    #     print("=== END VARIABLE LIST ===")
    #
    #     return {
    #         'all_variables': all_vars,
    #         'input_variables': input_vars,
    #         'output_variables': output_vars,
    #         'init_variables': init_vars,
    #         'integrator_variables': integrator_vars
    #     }

    # def select_and_delete_variable(self):
    #     """Interactive method to select a variable from available lists and delete it.
    #
    #     This method:
    #     1. Lists all available variables by category
    #     2. Prompts for variable selection
    #     3. Deletes the selected variable with all dependencies
    #
    #     Returns:
    #         tuple: (success, message, dependent_equations, orphaned_variables)
    #     """
    #     # First, list all available variables
    #     variables = self.list_all_variables_for_selection()
    #
    #     # Get all unique variables for selection
    #     all_unique_vars = sorted(set(variables['all_variables']))
    #
    #     if not all_unique_vars:
    #         return False, "No variables available for deletion", set(), set()
    #
    #     print(f"\nSelect a variable to delete (1-{len(all_unique_vars)}):")
    #     try:
    #         selection = input("Enter the number of the variable to delete: ").strip()
    #         if not selection.isdigit():
    #             return False, "Invalid selection: please enter a number", set(), set()
    #
    #         index = int(selection) - 1
    #         if index < 0 or index >= len(all_unique_vars):
    #             return False, f"Invalid selection: please enter a number between 1 and {len(all_unique_vars)}", set(), set()
    #
    #         selected_var = all_unique_vars[index]
    #         print(f"\nSelected variable: {selected_var}")
    #
    #         # Confirm deletion
    #         confirm = input(f"Are you sure you want to delete '{selected_var}'? (y/N): ").strip().lower()
    #         if confirm != 'y':
    #             return False, "Deletion cancelled by user", set(), set()
    #
    #         # Delete the variable
    #         return self.delete_variable_with_dependencies(selected_var)
    #
    #     except KeyboardInterrupt:
    #         return False, "Deletion cancelled by user", set(), set()
    #     except Exception as e:
    #         return False, f"Error during selection: {str(e)}", set(), set()

    def generate_var_eq_forest(
            self,
            add_var_eq_info: Dict[str, List[str]]
            ) -> Tuple[List[str], List[str], List[str], List[str]]:
        # """Generates a new variable-equation tree.
        #
        # Also compiles the difference between the original tree and the newly
        #   generated tree.
        # Args:
        #     add_var_eq_info (Dict[str, List[str]]): Additional information
        #       about the equations assigned to variables. The keys are ids
        #       of variables and the values are the ids of the equations
        #       assigned to those variables.
        #
        # Returns:
        #     List[str]: Ids of all variables and equations that wouldn't be
        #       needed in the newly generated tree compared with the original
        #       tree.
        # """
        # TODO: Check if there is a simpler way to add only one equation.
        # Creates a new forest
        self.temp_var_eq_forest = []

        # The original `var_eq_info` is the nodes of the tree representing
        # variables. If the `var_eq_forest` has not been constructed then
        # `var_eq_info` is an empty dict.
        var_eq_info = {}
        for var_id, eq_id in self.integrators.items():
            var_eq_info[var_id] = [eq_id]

        for tree in self.var_eq_forest:
            var_eq_info.update(tree)

        # Updating `var_eq_info` with the data in `add_var_eq_info`.
        for var_id, equation_ids in add_var_eq_info.items():
            var_eq_info[var_id] = equation_ids

        # Adding the roots for all trees. The roots are always the
        # output variables.
        for var_id in self.output_vars:
            self.temp_var_eq_forest.append({
                    var_id: []
                    })

        # Initially only the root variables that have assigned equations
        # are added to the queue.
        queue = collections.deque()
        for var_id in self.output_vars:
            # TODO: Change this is multiple equations are not allowed
            # for a single variable.
            if var_id not in var_eq_info:
                continue

            for eq_id in var_eq_info[var_id]:
                queue.append((var_id, eq_id))

        while queue:
            # pp(queue)
            var_id, eq_id = queue.popleft()

            # Finding the correct tree
            curr_tree = None
            for tree in self.temp_var_eq_forest:
                if var_id in tree:
                    curr_tree = tree
                    break

            # Adding the equation to the list of children of the variable.
            curr_tree[var_id].append(eq_id)

            # pp(self.all_equations)

            # Get incidence list from Equation object
            equation = self.all_equations[eq_id]
            incidence_list = equation.get_incidence_list(var_id)

            # Adding the equation to the tree
            curr_tree[eq_id] = [
                    child_var_id
                    for child_var_id in incidence_list
                    if child_var_id not in self.integrators
                    ]
            # Adding only new variables to the forest
            for child_var_id in incidence_list:
                # Only for variables that are not already in the forest.
                not_in_forest = True
                for tree in self.temp_var_eq_forest:
                    if child_var_id in tree:
                        not_in_forest = False
                        break

                if not_in_forest:
                    # Adding the variable to the tree
                    curr_tree[child_var_id] = []
                    
                    # Check if this dependent variable has an instantiation equation
                    # If so, add it to init_vars so it will be included in variables to be instantiated
                    for eq_id, equation in self.all_equations.items():
                        if child_var_id in str(equation.lhs):
                            if equation.is_instantiation_eq():
                                # Use a temporary set to track instantiation variables
                                if not hasattr(self, '_temp_instantiation_vars'):
                                    self._temp_instantiation_vars = set()
                                self._temp_instantiation_vars.add(child_var_id)
                                break

                    # If there are equations assigned to this variable then a new
                    # entry is added to the queue.
                    if child_var_id in var_eq_info:
                        for child_eq_id in var_eq_info[child_var_id]:
                            queue.append((child_var_id, child_eq_id))

        # Finding what vars and eqs have been added and which ones have
        # been deleted.
        ids_used_in_original = set()

        ids_used_in_original.update(list(self.integrators.keys()))
        for tree in self.var_eq_forest:
            ids_used_in_original.update(list(tree.keys()))

        ids_used_in_new = set()
        for tree in self.temp_var_eq_forest:
            ids_used_in_new.update(list(tree.keys()))

        added_ids = ids_used_in_new.difference(ids_used_in_original)
        deleted_ids = ids_used_in_original.difference(ids_used_in_new)

        added_vars = [
                element_id
                for element_id in added_ids
                if "V_" in element_id
                ]

        added_eqs = [
                element_id
                for element_id in added_ids
                if "E_" in element_id
                ]

        deleted_vars = [
                element_id
                for element_id in deleted_ids
                if "V_" in element_id
                ]

        deleted_eqs = [
                element_id
                for element_id in deleted_ids
                if "E_" in element_id
                ]

        # Convert temporary instantiation variables to final init_vars list
        if hasattr(self, '_temp_instantiation_vars'):
            # Ensure init_vars exists as a list
            if not hasattr(self, 'init_vars'):
                self.init_vars = []
            
            # Add new instantiation variables to init_vars
            current_init_vars = set(self.init_vars)
            current_init_vars.update(self._temp_instantiation_vars)
            self.init_vars = sorted(list(current_init_vars))
            
            # Clean up temporary set
            delattr(self, '_temp_instantiation_vars')

        return [added_vars, added_eqs, deleted_vars, deleted_eqs]

    # def _gen_init_vars(self) -> None:
    #   """Generates the list of variables that need to be initialized.

    #   A variable need to be initialized if it falls into one of the
    #     following statements:

    #     - No equations are assigned to the variable.
    #     - The equation assigned to the variable is used to instantiate
    #       with an undetermined value.
    #   """
    #   init_vars = []

    #   for node_id, children in self.var_eq_tree.items():
    #     if "V" not in node_id:
    #       continue

    #     # No equations are assigned to the variable.
    #     if not children:
    #       init_vars.append(node_id)
    #       continue

    #     # The equation instantiates with an undetermined value.
    #     eq_id = children[0]
    #     if self.entity_equations[eq_id].is_instantiation_eq():
    #       init_vars.append(node_id)

    #   self.init_vars = init_vars

    def convert_to_dict(self) -> EntityDict:
        """Creates a dictionary with the information in the Entity.

        Returns:
            EntityDict: Dictionary containing the information of the
             Entity.
        """
        # self._gen_init_vars()

        entity_dict = {}
        entity_dict["index_set"] = self.index_set
        entity_dict["integrators"] = self.integrators
        entity_dict["var_eq_forest"] = self.var_eq_forest
        entity_dict["init_vars"] = self.init_vars
        entity_dict["input_vars"] = self.input_vars
        entity_dict["output_vars"] = self.output_vars

        return entity_dict

    def is_input(self, var_id: str) -> bool:
        if var_id in self.input_vars:
            return True

        return False

    def is_output(self, var_id: str) -> bool:
        if var_id in self.output_vars:
            return True

        return False

    def get_eq_for_var(self, var_id: str) -> Optional[List[str]]:
        if var_id in self.integrators:
            return [self.integrators[var_id]]

        for tree in self.var_eq_forest:
            if var_id in tree:
                return tree[var_id]

        return None

    def get_variables_from_equation(self, equation_id: str) -> List[str]:
        for tree in self.var_eq_forest:
            if equation_id in tree:
                return tree[equation_id]

        return None

    # def start_merging_process(self, parents: List[Self]):
    #     """Starts the merging process.
    #
    #     Args:
    #       parents (List[Self]): Entities to me merged.
    #
    #     Returns:
    #       bool: **True** if the merge is complete. **False** otherwise.
    #     """
    #     self.output_vars = self._merging_variables(parents, "get_output_vars")
    #     self.input_vars = self._merging_variables(parents, "get_input_vars")
    #     self.init_vars = self._merging_variables(parents, "get_init_vars")
    #
    #     all_vars = self._merging_variables(parents, "get_variables")
    #     self.merged_vars = {}
    #     self.merge_conflicts = {}
    #     self.undo_merging = {}
    #     for var_id in all_vars:
    #         assigned_eqs = self._find_all_equations(var_id, parents)
    #         number_of_equations = len(assigned_eqs)
    #         if number_of_equations <= 1:
    #             self.merged_vars[var_id] = assigned_eqs
    #         else:
    #             self.merge_conflicts[var_id] = assigned_eqs
    #
    #     self.generate_var_eq_forest(self.merged_vars)
    #     temp_input = self.input_vars
    #     temp_init = self.init_vars
    #     self.update_var_eq_tree()
    #     self.init_vars = temp_init
    #     self.input_vars = temp_input
    #
    #     if not self.merge_conflicts:
    #         self._finish_merge()
    #         return True
    #
    #     return False

    # def get_conflict(self):
    #     for var_id, assigned_equations in self.merge_conflicts.items():
    #         if self.get_eq_for_var(var_id) is not None:
    #             return (var_id, assigned_equations)
    #
    #     self._finish_merge()
    #     return None

    # def solve_conflict(self, var_id, eq_id):
    #     self.undo_merging[var_id] = self.merge_conflicts.pop(var_id)
    #     self.merged_vars.update({var_id: [eq_id]})
    #
    #     self.generate_var_eq_forest(self.merged_vars)
    #     temp_input = self.input_vars
    #     temp_init = self.init_vars
    #     self.update_var_eq_tree()
    #     self.init_vars = temp_init
    #     self.input_vars = temp_input

    # def undo_merging_step(self):
    #     if not self.undo_merging:
    #         return None
    #
    #     last_var_id = self.undo_merging.keys()[-1]
    #     self.merge_conflicts[last_var_id] = self.undo_merging.pop(last_var_id)
    #     del self.merged_vars[last_var_id]
    #
    #     self.generate_var_eq_forest(self.merged_vars)
    #     temp_input = self.input_vars
    #     temp_init = self.init_vars
    #     self.update_var_eq_tree()
    #     self.init_vars = temp_init
    #     self.input_vars = temp_input
    #
    #     return (last_var_id, self.merge_conflicts[last_var_id])

    # def is_undo_merge_possible(self):
    #     return bool(self.undo_merging)
    #
    # def _finish_merge(self):
    #     self.merged_vars = {}
    #     self.merge_conflicts = {}
    #     self.undo_merging = {}
    #
    #     self.input_vars = [
    #             var_id
    #             for var_id in self.input_vars
    #             if self.get_eq_for_var(var_id) is not None
    #             ]
    #
    #     self.init_vars = [
    #             var_id
    #             for var_id in self.init_vars
    #             if self.get_eq_for_var(var_id) is not None
    #             ]
    #
    # def _merging_variables(
    #         self,
    #         parents: List[List[str]],
    #         method: Callable[[], List[str]]
    #         ) -> List[str]:
    #
    #     merge_set = {
    #             var_id
    #             for ent in parents
    #             for var_id in getattr(ent, method)()
    #             }
    #     return list(merge_set)

    # TODO: Check for possible duplication
    # def _find_all_equations(self, var_id: str, parents: List[Self]) -> List[str]:
    #     equation_lists = [ent.get_eq_for_var(var_id) for ent in parents]
    #     all_equations = set()
    #     for eq_list in equation_lists:
    #         if eq_list is not None:
    #             all_equations.update(eq_list)
    #
    #     return list(all_equations)

    def get_entity_name(self):
        return self.entity_id

    def contains_var(self, var_id: str) -> bool:
        return var_id in self.get_entity_variables()

    def is_interface_ent(self) -> bool:
        return ">>>" in self.entity_id

    def get_type(self) -> Optional[str]:
        if self.entity_id == "Topology":
            return None

        if self.is_interface_ent():
            return "interface"

        _, ent_type, _, _ = self.entity_id.split(".")
        return ent_type

    def get_network(self) -> Optional[List[str]]:
        if self.entity_id == "Topology":
            return None

        if ">>>" in self.entity_id:
            return [self.entity_id.split(" ")[0], self.entity_id.split(" ")[2]]

        return [self.entity_id.split(".")[0]]

    def get_tokens(self) -> Optional[List[str]]:
        if self.entity_id == "Topology":
            return None

        if ">>>" in self.entity_id:
            return None

        str1 = self.entity_id.split(".")[2]
        token_str = str1.split("|")[0]
        tokens = token_str.split("_")
        return tokens

    def printMe(self):
        dictionary = self.convert_to_dict()
        print("\n===================")
        print("\nEntity name: ", self.entity_id)
        for key, value in dictionary.items():
            print(key, value)
        print("\n===================")
