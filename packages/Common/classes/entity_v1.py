"""Contains the entity class."""
import collections
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypedDict

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
            local_variable_classifications: Optional[Dict[str, Dict[str, Any]]] = None,
            ) -> None:
        self.entity_id = entity_id
        self.index_set = index_set
        self.integrators = integrators if integrators is not None else {}
        self.var_eq_forest = var_eq_forest if var_eq_forest is not None else [{}]
        self.init_vars = init_vars if init_vars is not None else []
        self.input_vars = set(input_vars) if input_vars is not None else set()
        self.output_vars = set(output_vars) if output_vars is not None else set()
        self.all_equations = all_equations
        self.is_reservoir = False

        # Initialize local variable classifications tracking
        self.local_variable_classifications = local_variable_classifications if local_variable_classifications is not None else {}
        self.classifications_initialized = bool(self.local_variable_classifications)  # True if we have classifications

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

    
    def has_integrators(self) -> bool:
        return bool(self.integrators)

    def integrators_info(self):
        """Get integrator variable-equation pairs from forest."""
        forest_data = self.forest_data  # _get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()

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
        if hasattr(self, 'forest_data') and self.var_eq_forest:
            forest_data = self.forest_data  #
        else:
            forest_data  = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
            self.forest_data = forest_data

        return sorted(list(forest_data['integrators']))

    def get_integrators_eq(self):
        """Get integrator equations from forest."""
        forest_data = self.forest_data()

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

        init_vars = self.get_init_vars()
        pending_vars = self._get_raw_pending_vars(all_variables, equation_defined_vars, init_vars)
        print("================ variable lists =================")
        print(f"all variables           :{all_variables}")
        print(f"all equations           :{all_equations}")
        print(f"equation defined vars   :{equation_defined_vars}")
        print(f"integrators             :{integrators}")
        print(f"pending variables       :{pending_vars}")
        print("================ variable lists =================")
        return {
                'all_variables'        : all_variables,
                'all_equations'        : all_equations,
                'equation_defined_vars': equation_defined_vars,
                'integrators'          : integrators,
                "pending_variables"    : pending_vars,
                }

    def get_entity_variables(self):
        """Get all variables included in the entity."""
        # Get variables from explicit lists first
        all_vars = set(self.input_vars) | set(self.output_vars) | set(self.init_vars) | set(self.get_equation_defined_vars())
        all_vars.update(self.integrators.keys())
        
        # Add equation-defined variables from forest (this catches variables like V_154 that have equations but aren't yet classified)
        equation_defined_from_forest = set(self.get_equation_defined_vars())
        all_vars.update(equation_defined_from_forest)

        return sorted(list(all_vars))

    def _apply_manual_classifications(self, base_list, target_classification):
        """Apply manual classifications to a base list.
        
        This method combines the raw base list with manual classification overrides
        to produce the final list that should be displayed in the GUI.
        
        Args:
            base_list: The raw list (input_vars, output_vars, init_vars, etc.)
            target_classification: The classification to apply ("input", "output", "instantiate", "pending")
            
        Returns:
            List with manual classifications applied
        """
        # print(">>>>>>>>>>>>> fixing list")
        if not hasattr(self, 'local_variable_classifications'):
            return base_list

        result = set(base_list)

        # Add variables that have manual classification matching target
        for var_id, classification_info in self.local_variable_classifications.items():
            classifications = classification_info['classification']
            # Handle both single string and list of classifications
            if isinstance(classifications, list):
                if target_classification in classifications:
                    result.add(var_id)
            else:
                # Legacy single classification
                if classifications == target_classification:
                    result.add(var_id)

        # Remove variables that have different manual classifications
        for var_id in base_list:
            if var_id in self.local_variable_classifications:
                classifications = self.local_variable_classifications[var_id]['classification']
                # Handle both single string and list of classifications
                if isinstance(classifications, list):
                    if target_classification not in classifications:
                        result.discard(var_id)
                else:
                    # Legacy single classification
                    if classifications != target_classification:
                        result.discard(var_id)

        return sorted(list(result))

    def change_classification(self, var_id, classifications):
        """Change the classification of a variable.
        
        This method updates the manual classification system without modifying raw lists.
        The raw lists remain unchanged and manual classifications are applied
        when the GUI requests variable lists.
        
        Args:
            var_id: The variable ID to change classification for
            classifications: List of new classifications (e.g., ["input", "output"])
        """
        # print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>move classification of variable {var_id} to {classifications}")

        # Update manual classification system
        if var_id not in self.local_variable_classifications:
            self.local_variable_classifications[var_id] = {
                    'classification': classifications,
                    'original_list' : f'list_{classifications[0]}' if classifications else 'list_none'
                    }
        else:
            old_classifications = self.local_variable_classifications[var_id]["classification"]
            self.local_variable_classifications[var_id]["classification"] = classifications
            # Update original_list to first classification if available
            if classifications:
                self.local_variable_classifications[var_id]["original_list"] = f'list_{classifications[0]}'
            # NOTE: We do NOT modify raw lists here
            # Raw lists are only modified when variables are actually added/removed
            # Manual classifications are applied when GUI requests lists

    def _move_variable_between_lists(self, var_id, old_classification, new_classification):
        """Move variable from one raw list to another when classification changes."""
        print(f"DEBUG: Moving {var_id} from {old_classification} to {new_classification}")
        print(f"DEBUG: Before - init_vars: {self.init_vars}, input_vars: {self.input_vars}")

        # Remove from old list
        if old_classification == "input":
            if var_id in self.input_vars:
                self.input_vars.remove(var_id)
                print(f"DEBUG: Removed {var_id} from input_vars")
        elif old_classification == "output":
            if var_id in self.output_vars:
                self.output_vars.remove(var_id)
                print(f"DEBUG: Removed {var_id} from output_vars")
        elif old_classification == "instantiate":
            if var_id in self.init_vars:
                self.init_vars.remove(var_id)
                print(f"DEBUG: Removed {var_id} from init_vars")
        elif old_classification == "pending":
            # Can't move from pending - it's computed
            pass

        # Add to new list
        if new_classification == "input":
            if var_id not in self.input_vars:
                self.input_vars.append(var_id)
                print(f"DEBUG: Added {var_id} to input_vars")
        elif new_classification == "output":
            if var_id not in self.output_vars:
                self.output_vars.append(var_id)
                print(f"DEBUG: Added {var_id} to output_vars")
        elif new_classification == "instantiate":
            if var_id not in self.init_vars:
                self.init_vars.append(var_id)
                print(f"DEBUG: Added {var_id} to init_vars")

        print(f"DEBUG: After - init_vars: {self.init_vars}, input_vars: {self.input_vars}")

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
                        'classification': ['output'],
                        'original_list' : 'list_outputs'
                        }

            for var_id in self.input_vars:
                self.local_variable_classifications[var_id] = {
                        'classification': ['input'],
                        'original_list' : 'list_inputs'
                        }

            for var_id in self.get_variables_to_be_instantiated():
                self.local_variable_classifications[var_id] = {
                        'classification': ['instantiate'],
                        'original_list' : 'list_instantiate'
                        }

            for var_id in self.get_pending_vars():
                self.local_variable_classifications[var_id] = {
                        'classification': ['pending'],
                        'original_list' : 'list_not_defined_variables'
                        }

            for var_id in self.get_integrator_vars():
                self.local_variable_classifications[var_id] = {
                        'classification': ['integrator'],
                        'original_list' : 'list_integrators'
                        }

            # Mark that classifications have been initialized
            self.classifications_initialized = True

            # print(
            #     f"Entity {self.entity_id}: Built local variable classifications: {len(self.local_variable_classifications)} variables tracked")

        except Exception as e:
            print(f"Error building local variable classifications for entity {self.entity_id}: {str(e)}")
            self.classifications_initialized = False

    def get_input_vars(self):
        """Get input variables (variables not defined by equations)."""
        # Use stored list directly - no tree calculation needed
        base_list = sorted(list(self.input_vars))
        return self._apply_manual_classifications(base_list, "input")

    def get_output_vars(self, all_variables=None):
        """
        Get output variables (variables defined by equations or explicitly marked as outputs).
        
        Args:
            all_variables: Optional Dict[str, Variable] to filter out transport variables.
                          If provided, variables with type 'transport' will be excluded.
        
        Returns:
            List of variable IDs that are output variables (excluding transport variables if all_variables provided)
        """
        # Use stored list directly - no tree calculation needed
        base_list = sorted(list(self.output_vars))
        result = self._apply_manual_classifications(base_list, "output")

        # Filter out transport variables if all_variables is provided
        if all_variables is not None:
            result = [var_id for var_id in result
                      if var_id in all_variables and all_variables[var_id].type != 'transport']

        return result

    def set_input_var(self, var_id, is_input):
        """Legacy method for backward compatibility. Consider using forest-based approach."""
        if not hasattr(self, 'input_vars'):
            self.input_vars = set()
        if is_input:
            self.input_vars.add(var_id)
        else:
            self.input_vars.discard(var_id)

    def get_pending_vars(self):
        """Get variables that are not yet defined (need instantiation)."""
        # Compute directly from current entity state to avoid recursion
        try:
            pending_vars = self.pending_vars
        except:
            # a = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
            pending_vars = self._get_raw_pending_vars(self.get_entity_variables(), self.get_equation_defined_vars(), self.get_init_vars())

        # Apply manual classifications for pending
        return self._apply_manual_classifications(sorted(list(pending_vars)), "pending")

    def _get_raw_pending_vars(self, all_included_vars,equation_defined_variables, init_vars) -> set[str]:
        # all_included_vars = self.get_entity_variables()
        # equation_defined_variables = self.get_equation_defined_vars()
        # init_vars = self.get_init_vars()

        # Variables that are not in any of the main lists (input, output, instantiate)
        # These are the truly "pending" variables
        main_list_vars = set(self.input_vars) | set(self.output_vars) | set(init_vars)
        pending_vars = set(all_included_vars) - set(equation_defined_variables) -  set(self.input_vars)
        return pending_vars

    def get_variables_to_be_instantiated(self):
        """Get variables that need to be instantiated."""
        # Compute directly from current entity state to avoid recursion
        instantiation_vars = set(self.init_vars)
        all_vars = self.get_entity_variables()

        for var_id in all_vars:
            defining_eqs = self.get_eq_for_var(var_id)
            if defining_eqs:
                for eq_id in defining_eqs:
                    if eq_id in self.all_equations:
                        equation = self.all_equations[eq_id]
                        is_instantiation = equation.is_instantiation_eq()
                        if is_instantiation:
                            instantiation_vars.add(var_id)

        # Exclude variables that are already in input or output lists (mutual exclusivity)
        main_list_vars = set(self.input_vars) | set(self.output_vars)
        instantiation_vars = instantiation_vars - main_list_vars

        # Apply manual classifications for instantiate
        return self._apply_manual_classifications(sorted(list(instantiation_vars)), "instantiate")

    
    def get_equation_defined_vars(self, all_variables=None):
        """Get variables that are defined by equations.
        
        This method extracts variables that have defining equations in var_eq_forest,
        providing a comprehensive view of equation-defined variables.
        
        Args:
            all_variables: Optional Dict[str, Variable] to filter out transport variables.
                          If provided, variables with type 'transport' will be excluded.
        
        Returns:
            List of variable IDs defined by equations (excluding transport variables if all_variables provided)
        """
        # Get equation-defined variables from forest (comprehensive approach)
        equation_defined_vars = set()
        
        if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
            for tree in self.var_eq_forest:
                for key, values in tree.items():
                    if key.startswith('V_') and values:  # Variable with equations
                        equation_defined_vars.add(key)
        
        # Filter out transport variables if all_variables is provided
        if all_variables is not None:
            non_transport_vars = set()
            for var_id in equation_defined_vars:
                if var_id in all_variables:
                    var_obj = all_variables[var_id]
                    if hasattr(var_obj, 'type') and var_obj.type != 'transport':
                        non_transport_vars.add(var_id)
                else:
                    # If variable not found in all_variables, include it (fallback behavior)
                    non_transport_vars.add(var_id)
            equation_defined_vars = non_transport_vars

        return sorted(list(equation_defined_vars))

    def set_output_var(self, var_id, is_output):
        """Legacy method for backward compatibility. Consider using forest-based approach."""
        if not hasattr(self, 'output_vars'):
            self.output_vars = set()
        if is_output:
            self.output_vars.add(var_id)
        else:
            self.output_vars.discard(var_id)

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
                self.change_classification(var_id,"instantiate")
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
        print(f"Added {var_id} to tree with empty dependencies in _add_variable_to_tree") # todo: check what's going on

    
    def get_not_defined_variables(self):
        """Get variables that are not yet defined (need instantiation)"""
        return self.get_pending_vars()

    def is_init(self, var_id):
        return var_id in self.init_vars

    
    
    def update_var_eq_tree(self) -> None:
        """Updates the variable-equation tree.

        The variable-equation tree is updated with the last tree generated
          by the method `generate_var_eq_tree`.
        """
        self.var_eq_forest = self.temp_var_eq_forest

        # Removing all variables that are not in the entity from the lists
        # input, output and init
        all_vars = set(self.get_entity_variables())
        self.input_vars = self.input_vars.intersection(all_vars)
        self.output_vars = self.output_vars.intersection(all_vars)
        self.init_vars = list(
                set(self.init_vars).intersection(all_vars)
                )
        # Update stored integrators using dynamic method for consistency
        # This maintains backward compatibility while avoiding duplicate logic

        self.forest_data = self._get_all_vars_equs_vars_in_eqs_and_integrators_from_forest()
        integrator_info = self.integrators_info()
        self.integrators = {var_id: eq_id for var_id, eq_id in integrator_info}
        self.pending_vars = self.forest_data['pending_variables']

        # Use the comprehensive list building method to ensure consistency
        # self.build_variable_lists_from_forest()

                #
    #         if rebuilt_tree:  # Only add non-empty trees
    #             rebuilt_forest.append(rebuilt_tree)
    #
    #     self.var_eq_forest = rebuilt_forest
    #     print(f"Rebuilt forest: {self.var_eq_forest}")
    #
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
            before = self.get_entity_variables()
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
                print(
                    f"  Iteration {iteration}: vars_to_delete={variables_to_delete}, equations_to_delete={equations_to_delete}")

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
                            print(
                                f"  Cleaned equation {key}: removed {len(values) - len(filtered_values)} deleted variables")

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
                        self.input_vars = set()
                    if hasattr(self, 'output_vars'):
                        self.output_vars = set()
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
            after = self.get_entity_variables()
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
        # FIXED: Preserve existing forest and add new relationships instead of rebuilding from scratch
        
        # Create a copy of the existing forest to work with
        import copy
        self.temp_var_eq_forest = copy.deepcopy(self.var_eq_forest)

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
        # FIXED: Check if tree already exists before creating new one
        for var_id in self.output_vars:
            # Find if this variable already has a tree in the preserved forest
            tree_exists = False
            for tree in self.temp_var_eq_forest:
                if var_id in tree:
                    tree_exists = True
                    break
            
            # Only create new tree if variable doesn't already have one
            if not tree_exists:
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

    
    def convert_to_dict(self) -> EntityDict:
        """Creates a dictionary with the information in the Entity.

        Returns:
            EntityDict: Dictionary containing the information of the
             Entity.
        """
        # Apply manual classifications to raw lists before saving
        self._sync_raw_lists_with_classifications()

        entity_dict = {}
        entity_dict["index_set"] = self.index_set
        entity_dict["integrators"] = self.integrators
        entity_dict["var_eq_forest"] = self.var_eq_forest
        entity_dict["init_vars"] = self.init_vars
        entity_dict["input_vars"] = list(self.input_vars)  # Convert set to list for JSON
        entity_dict["output_vars"] = list(self.output_vars)  # Convert set to list for JSON
        entity_dict["local_variable_classifications"] = self.local_variable_classifications  # Save classifications

        return entity_dict

    def _sync_raw_lists_with_classifications(self):
        """Sync raw lists with current manual classifications before saving."""
        # Rebuild raw lists based on classifications
        new_input_vars = []
        new_output_vars = []
        new_init_vars = []

        for var_id, info in self.local_variable_classifications.items():
            classification = info['classification']
            # Handle both single string and list of classifications
            if isinstance(classification, list):
                # Multiple classifications
                if 'input' in classification:
                    new_input_vars.append(var_id)
                if 'output' in classification:
                    new_output_vars.append(var_id)
                if 'instantiate' in classification:
                    new_init_vars.append(var_id)
            else:
                # Legacy single classification
                if classification == 'input':
                    new_input_vars.append(var_id)
                elif classification == 'output':
                    new_output_vars.append(var_id)
                elif classification == 'instantiate':
                    new_init_vars.append(var_id)

        # Update raw lists with manual classifications
        self.input_vars = set(new_input_vars)
        self.output_vars = set(new_output_vars)
        self.init_vars = new_init_vars

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
