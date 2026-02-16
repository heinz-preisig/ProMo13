"""Simple variable deletion method to replace the complex one."""

def delete_variable_with_dependencies(self, var_id):
    """Delete a variable and all its dependencies from the entity.
    
    This is a simplified method that:
    1. Removes variable from stored lists (init_vars, input_vars, output_vars)
    2. Removes variable from var_eq_forest directly
    3. Updates integrators if needed
    4. Calls update_var_eq_tree() to maintain consistency
    
    Args:
        var_id: The variable ID to delete
        
    Returns:
        tuple: (success, message, dependent_equations, orphaned_variables)
    """
    try:
        print(f"=== SIMPLIFIED VARIABLE DELETION: {var_id} ===")
        
        # === STEP 1: Remove from stored lists ===
        if hasattr(self, 'init_vars'):
            self.init_vars = [v for v in self.init_vars if v != var_id]
            print(f"Removed {var_id} from init_vars: {self.init_vars}")
            
        if hasattr(self, 'input_vars'):
            self.input_vars = [v for v in self.input_vars if v != var_id]
            print(f"Removed {var_id} from input_vars: {self.input_vars}")
                
        if hasattr(self, 'output_vars'):
            self.output_vars = [v for v in self.output_vars if v != var_id]
            print(f"Removed {var_id} from output_vars: {self.output_vars}")
        
        # === STEP 2: Remove from var_eq_forest ===
        if hasattr(self, 'var_eq_forest') and self.var_eq_forest:
            # Remove variable from all trees in forest
            for tree in self.var_eq_forest:
                if var_id in tree:
                    del tree[var_id]
                    print(f"Removed {var_id} from forest tree")
                
                # Remove variable from equation definitions (if it's used as LHS)
                for tree in self.var_eq_forest:
                    for key, values in tree.items():
                        if key.startswith('E_') and values and var_id in values:
                            tree[key] = [v for v in values if v != var_id]
                            print(f"Removed {var_id} from equation {key} definition: {tree[key]}")
            
            # === STEP 3: Update integrators ===
            if hasattr(self, 'integrators') and var_id in self.integrators:
                del self.integrators[var_id]
                print(f"Removed {var_id} from integrators: {self.integrators}")
            
        # === STEP 4: Update consistency ===
        self.update_var_eq_tree()
        
        return True, f"Variable {var_id} deleted successfully", set(), set()
        
    except Exception as e:
        print(f"Error in delete_variable_with_dependencies: {e}")
        return False, f"Error deleting variable: {str(e)}", set(), set()
