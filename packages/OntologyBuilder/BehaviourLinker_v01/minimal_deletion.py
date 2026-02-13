def minimal_variable_deletion(entity, var_id):
    """
    Minimal variable deletion - just remove the variable and update lists.
    No complex dependency analysis, just basic cleanup.
    """
    print(f"=== MINIMAL VARIABLE DELETION: {var_id} ===")
    
    # Step 1: Remove variable from all explicit lists
    entity.set_output_var(var_id, False)
    entity.set_input_var(var_id, False)
    entity.set_init_var(var_id, False)
    
    # Remove from integrators if present
    if hasattr(entity, 'integrators') and var_id in entity.integrators:
        del entity.integrators[var_id]
        print(f"Removed {var_id} from integrators")
    
    # Step 2: Remove from forest structure
    if hasattr(entity, 'var_eq_forest') and entity.var_eq_forest:
        for tree in entity.var_eq_forest:
            if var_id in tree:
                del tree[var_id]
                print(f"Removed {var_id} from forest")
        
        # Also remove from any equation definitions
        for tree in entity.var_eq_forest:
            for key, values in tree.items():
                if key.startswith('E_') and values and var_id in values:
                    values.remove(var_id)
                    print(f"Removed {var_id} from equation {key} definition")
    
    # Step 3: Regenerate variable lists from remaining forest
    all_variables = set()
    if hasattr(entity, 'var_eq_forest') and entity.var_eq_forest:
        for tree in entity.var_eq_forest:
            for key, values in tree.items():
                if key.startswith('V_'):
                    all_variables.add(key)
    
    # Update explicit lists to only include remaining variables
    saved_output_vars = entity.output_vars.copy()
    saved_input_vars = entity.input_vars.copy() 
    saved_init_vars = entity.init_vars.copy()
    
    entity.output_vars = [var for var in saved_output_vars if var in all_variables]
    entity.input_vars = [var for var in saved_input_vars if var in all_variables]
    entity.init_vars = [var for var in saved_init_vars if var in all_variables]
    
    print(f"Remaining variables: {all_variables}")
    print(f"Updated lists: output={entity.output_vars}, input={entity.input_vars}, init={entity.init_vars}")
    
    return {
        'success': True,
        'message': f"Variable {var_id} deleted (minimal approach)",
        'removed_variables': {var_id}
    }
