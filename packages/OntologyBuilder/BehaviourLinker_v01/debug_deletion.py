#!/usr/bin/env python3

"""
Debug script to test variable deletion process
"""

import sys
import os

# Add the project root to the path
root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages')])

def test_entity_creation_and_deletion():
    """Test the entity creation and variable deletion process"""
    try:
        print("=== TESTING ENTITY CREATION AND VARIABLE DELETION ===")
        
        # Import required modules
        from Common.classes.entity import Entity
        from Common.classes.equation import Equation
        from OntologyBuilder.BehaviourLinker_v01.variable_deletion import handle_variable_deletion_with_dependencies
        
        # Create a test entity
        entity = Entity("test_entity")
        print(f"Created entity: {entity.entity_id}")
        
        # Add some test variables
        test_vars = ["V_101", "V_102", "V_103"]
        for var in test_vars:
            entity.output_vars.append(var)
        
        print(f"Added variables: {entity.output_vars}")
        
        # Create test equations
        eq1 = Equation(
            eq_id="E_1",
            lhs={'global_ID': 'V_102'},
            rhs={'global_ID': 'V_101'},
            type='algebraic'
        )
        
        eq2 = Equation(
            eq_id="E_2", 
            lhs={'global_ID': 'V_103'},
            rhs={'global_ID': 'V_102'},
            type='algebraic'
        )
        
        entity.all_equations["E_1"] = eq1
        entity.all_equations["E_2"] = eq2
        
        print(f"Added equations: {list(entity.all_equations.keys())}")
        
        # Create a simple forest structure
        entity.var_eq_forest = [
            {
                "V_101": [],  # Input variable
                "V_102": ["E_1"],  # Defined by E_1
                "V_103": ["E_2"],  # Defined by E_2
                "E_1": ["V_101"],  # Uses V_101
                "E_2": ["V_102"]   # Uses V_102
            }
        ]
        
        print(f"Created forest: {entity.var_eq_forest}")
        
        # Test deletion of V_102 (should remove E_1, E_2 and V_103)
        print("\n=== TESTING DELETION OF V_102 ===")
        
        success, message, dependent_equations, orphaned_variables = handle_variable_deletion_with_dependencies(entity, "V_102")
        
        print(f"Deletion result: {success}")
        print(f"Message: {message}")
        print(f"Dependent equations: {dependent_equations}")
        print(f"Orphaned variables: {orphaned_variables}")
        print(f"Remaining variables: {entity.get_all_variables()}")
        print(f"Remaining equations: {list(entity.all_equations.keys())}")
        print(f"Remaining forest: {entity.var_eq_forest}")
        
        return success
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_entity_creation_and_deletion()
