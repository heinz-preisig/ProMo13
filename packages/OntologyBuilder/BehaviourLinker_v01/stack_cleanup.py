def recursive_cleanup_incidence_matrix(incidence_matrix, var_to_remove):
    """
    Recursively clean up incidence matrix using stack-based approach.
    
    Args:
        incidence_matrix: dict of equation -> [variables]
        var_to_remove: variable to remove
        
    Returns:
        dict: {
            'cleaned_matrix': dict,
            'removed_equations': set,
            'removed_variables': set
        }
    """
    print(f"Starting recursive cleanup for variable: {var_to_remove}")
    
    removed_equations = set()
    removed_variables = set()
    current_matrix = {eq: vars[:] for eq, vars in incidence_matrix.items()}
    
    # Stack-based recursive cleanup
    # Stack holds variables that need to be processed
    var_stack = [var_to_remove]
    
    while var_stack:
        current_var = var_stack.pop()
        print(f"Processing variable from stack: {current_var}")
        print(f"Current stack: {var_stack}")
        print(f"Current matrix: {current_matrix}")
        
        if current_var in removed_variables:
            print(f"Variable {current_var} already processed")
            continue
            
        # Find equations that contain this variable
        equations_with_var = []
        for eq_id, variables in current_matrix.items():
            if current_var in variables:
                equations_with_var.append(eq_id)
        
        print(f"Equations containing {current_var}: {equations_with_var}")
        
        # For each equation containing this variable, check if it should be removed
        for eq_id in equations_with_var:
            if eq_id in removed_equations:
                continue
                
            # Remove the variable from this equation
            if current_var in current_matrix[eq_id]:
                current_matrix[eq_id].remove(current_var)
                print(f"Removed {current_var} from equation {eq_id}")
            
            # Check if equation is now empty or only has shared variables
            remaining_vars = current_matrix[eq_id]
            print(f"Remaining variables in {eq_id}: {remaining_vars}")
            
            if not remaining_vars:
                # Equation is empty - remove it
                print(f"Removing equation {eq_id} (empty)")
                removed_equations.add(eq_id)
                del current_matrix[eq_id]
            else:
                # Check if all remaining variables are shared with other equations
                all_shared = True
                for var in remaining_vars:
                    is_shared = False
                    for other_eq_id, other_vars in current_matrix.items():
                        if other_eq_id != eq_id and var in other_vars:
                            is_shared = True
                            break
                    
                    if not is_shared:
                        # Found a variable that's not shared
                        all_shared = False
                        break
                
                if all_shared:
                    print(f"Equation {eq_id} only has shared variables - keeping it")
                else:
                    # Equation has unique variables - check if it should be removed
                    # For now, we'll keep equations with any unique variables
                    print(f"Equation {eq_id} has unique variables - keeping it")
        
        # Mark current variable as removed
        removed_variables.add(current_var)
        print(f"Marked variable {current_var} as removed")
        
        # Check if any equations should now be removed due to having only removable variables
        equations_to_remove = []
        for eq_id, variables in current_matrix.items():
            if eq_id in removed_equations:
                continue
                
            # Check if all variables in this equation are either:
            # 1. Already removed, or
            # 2. Shared with other equations
            all_removable_or_shared = True
            for var in variables:
                if var not in removed_variables:
                    # Check if shared
                    is_shared = False
                    for other_eq_id, other_vars in current_matrix.items():
                        if other_eq_id != eq_id and var in other_vars:
                            is_shared = True
                            break
                    
                    if not is_shared:
                        # Variable is not removed and not shared
                        all_removable_or_shared = False
                        break
            
            if all_removable_or_shared and variables:
                print(f"Equation {eq_id} can be removed (all variables removable/shared)")
                equations_to_remove.append(eq_id)
        
        # Remove identified equations and add their variables to stack
        for eq_id in equations_to_remove:
            removed_equations.add(eq_id)
            vars_to_add = current_matrix[eq_id]
            print(f"Removing equation {eq_id} and adding variables to stack: {vars_to_add}")
            
            for var in vars_to_add:
                if var not in removed_variables:
                    var_stack.append(var)
            
            del current_matrix[eq_id]
    
    print(f"Recursive cleanup completed:")
    print(f"  Removed equations: {removed_equations}")
    print(f"  Removed variables: {removed_variables}")
    print(f"  Cleaned matrix: {current_matrix}")
    
    return {
        'cleaned_matrix': current_matrix,
        'removed_equations': removed_equations,
        'removed_variables': removed_variables
    }
