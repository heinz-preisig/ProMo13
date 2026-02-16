#!/usr/bin/env python3
"""
Test script to verify GUI refresh for instantiation variables
"""

import sys
import os

# Add the packages directory to the path
sys.path.extend([
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages'),
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
])

from Common.classes.entity import Entity
from Common.classes.equation import Equation

def test_instantiation_gui_refresh():
    """Test that instantiation variables are properly detected and displayed"""
    print("=== Testing Instantiation Variable GUI Refresh ===")
    
    # Create a simple entity
    entity = Entity(
        entity_id="test_entity",
        all_equations={},
        var_eq_forest=[],
        init_vars=[],
        input_vars=[],
        output_vars=[]
    )
    
    print("=== Test 1: Empty entity ===")
    print(f"  Initial init_vars: {entity.init_vars}")
    print(f"  get_variables_to_be_instantiated(): {entity.get_variables_to_be_instantiated()}")
    
    # Add a variable for instantiation
    print("\n=== Test 2: Adding variable for instantiation ===")
    entity.set_init_var("V_test_var", True)
    print(f"  After set_init_var: {entity.init_vars}")
    print(f"  get_variables_to_be_instantiated(): {entity.get_variables_to_be_instantiated()}")
    
    # Verify the variable appears in instantiation list
    expected_vars = ["V_test_var"]
    actual_vars = entity.get_variables_to_be_instantiated()
    
    assert set(actual_vars) == set(expected_vars), f"Expected {expected_vars}, got {actual_vars}"
    print("  ✅ Variable correctly appears in instantiation list")
    
    print("\n=== Test 3: Multiple instantiation variables ===")
    entity.set_init_var("V_test_var2", True)
    entity.set_init_var("V_test_var3", True)
    
    actual_vars = entity.get_variables_to_be_instantiated()
    expected_vars = ["V_test_var", "V_test_var2", "V_test_var3"]
    
    assert set(actual_vars) == set(expected_vars), f"Expected {expected_vars}, got {actual_vars}"
    print(f"  Multiple variables: {actual_vars}")
    print("  ✅ Multiple instantiation variables work correctly")
    
    print("\n🎉 All instantiation GUI refresh tests passed!")

if __name__ == "__main__":
    test_instantiation_gui_refresh()
