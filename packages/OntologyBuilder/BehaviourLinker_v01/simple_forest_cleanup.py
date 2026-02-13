def simple_forest_cleanup(forest_structure, var_to_remove):
    """
    Simple forest-based cleanup that works with the existing forest structure.
    
    Args:
        forest_structure: list of tree dictionaries
        var_to_remove: variable to remove
        
    Returns:
        dict: {
            'cleaned_forest': list,
            'removed_equations': set,
            'removed_variables': set
        }
    """
    print(f"Simple forest cleanup for variable: {var_to_remove}")
    print(f"Original forest: {forest_structure}")
    
    removed_equations = set()
    removed_variables = set()
    
    # Work with a copy
    cleaned_forest = []
    for tree in forest_structure:
        cleaned_tree = tree.copy()
        cleaned_forest.append(cleaned_tree)
    
    # Step 1: Remove the target variable from all trees
    for tree in cleaned_forest:
        if var_to_remove in tree:
            del tree[var_to_remove]
            print(f"Removed {var_to_remove} from tree")
    
    # Step 2: Find equations that defined this variable
    equations_defining_var = set()
    for tree in forest_structure:
        if var_to_remove in tree and tree[var_to_remove]:
            equations_defining_var.update(tree[var_to_remove])
    
    print(f"Equations that defined {var_to_remove}: {equations_defining_var}")
    
    # Step 3: For each equation, check if it should be removed
    for eq_id in equations_defining_var:
        print(f"Checking equation {eq_id}")
        
        # Find all variables defined by this equation
        vars_defined_by_eq = set()
        for tree in forest_structure:
            if eq_id in tree:
                vars_defined_by_eq.update(tree[eq_id])
                break
        
        print(f"Variables defined by {eq_id}: {vars_defined_by_eq}")
        
        # Remove the target variable
        vars_defined_by_eq.discard(var_to_remove)
        
        if not vars_defined_by_eq:
            print(f"Removing equation {eq_id} (no remaining variables)")
            removed_equations.add(eq_id)
            
            # Remove equation from all trees
            for tree in cleaned_forest:
                if eq_id in tree:
                    del tree[eq_id]
        else:
            # Check if remaining variables are defined by other equations
            shared_vars = set()
            unique_vars = set()
            
            for var in vars_defined_by_eq:
                is_shared = False
                for tree in forest_structure:
                    if var in tree and tree[var]:
                        for other_eq in tree[var]:
                            if other_eq != eq_id:
                                is_shared = True
                                shared_vars.add(var)
                                break
                    if is_shared:
                        break
                
                if not is_shared:
                    unique_vars.add(var)
            
            print(f"Shared variables: {shared_vars}")
            print(f"Unique variables: {unique_vars}")
            
            if not unique_vars:
                print(f"Keeping equation {eq_id} (all variables shared)")
            else:
                print(f"Equation {eq_id} has unique variables, keeping for now")
    
    # Step 4: Remove variables that are only defined by removed equations
    for tree in cleaned_forest:
        vars_to_remove = set()
        for var, eqs in list(tree.items()):
            if var.startswith('V_') and eqs:
                # Check if all defining equations were removed
                all_removed = all(eq in removed_equations for eq in eqs)
                if all_removed:
                    vars_to_remove.add(var)
        
        for var in vars_to_remove:
            del tree[var]
            removed_variables.add(var)
            print(f"Removed variable {var} (all defining equations removed)")
    
    # Add target variable to removed set
    removed_variables.add(var_to_remove)
    
    # Clean up empty trees
    cleaned_forest = [tree for tree in cleaned_forest if tree]
    
    print(f"Simple cleanup completed:")
    print(f"  Removed equations: {removed_equations}")
    print(f"  Removed variables: {removed_variables}")
    print(f"  Cleaned forest: {cleaned_forest}")
    
    return {
        'cleaned_forest': cleaned_forest,
        'removed_equations': removed_equations,
        'removed_variables': removed_variables
    }
