#!/usr/bin/env python3
"""
Simple test script to verify Entity list generation functionality
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

def test_entity_list_generation():
    """Test that Entity list generation works correctly"""
    print("=== Testing Entity List Generation ===")
    
    # Create test equations
    eq1 = Equation(
        eq_id="E_eq1",
        img_path="",
        type="algebraic",
        lhs={'global_ID': 'V_x'},
        rhs={'global_ID': 'V_y'},
        network="test_network",
        doc="Test equation 1",
        created="2024-01-01 00:00:00",
        modified="2024-01-01 00:00:00"
    )
    
    eq2 = Equation(
        eq_id="E_eq2", 
        img_path="",
        type="integrator",
        lhs={'global_ID': 'V_z'},
        rhs={'global_ID': 'Integral V_x'},  # Proper integrator format
        network="test_network",
        doc="Test integrator equation",
        created="2024-01-01 00:00:00",
        modified="2024-01-01 00:00:00"
    )
    
    all_equations = {
        "E_eq1": eq1,
        "E_eq2": eq2
    }
    
    # Manually set up operators dictionary to avoid import issues in test
    eq1.operators = {"Integral": "Integral"}
    eq2.operators = {"Integral": "Integral"}
    
    # Create a test var_eq_forest
    var_eq_forest = [
        {
            "V_x": ["E_eq1"],  # x is defined by eq1
            "V_y": [],         # y is input
            "V_z": ["E_eq2"]   # z is defined by integrator eq2
        },
        {
            "E_eq1": ["V_x", "V_y"],  # eq1 uses x and y
            "E_eq2": ["V_z", "V_x"]   # eq2 uses z and x
        }
    ]
    
    # Create Entity with the test data
    entity = Entity(
        entity_id="test_entity",
        all_equations=all_equations,
        var_eq_forest=var_eq_forest,
        init_vars=[],
        input_vars=[],
        output_vars=[]
    )
    
    print(f"Initial Entity state:")
    print(f"  output_vars: {entity.output_vars}")
    print(f"  input_vars: {entity.input_vars}")
    print(f"  init_vars: {entity.init_vars}")
    print(f"  integrators: {entity.integrators}")
    
    # Test the list generation method
    print("\n=== Calling build_variable_lists_from_forest() ===")
    entity.build_variable_lists_from_forest()
    
    print(f"\nAfter list generation:")
    print(f"  get_output_vars(): {entity.get_output_vars()}")
    print(f"  get_equation_defined_vars(): {entity.get_equation_defined_vars()}")
    print(f"  get_input_vars(): {entity.get_input_vars()}")
    print(f"  get_init_vars(): {entity.get_init_vars()}")
    print(f"  get_integrator_vars(): {entity.get_integrator_vars()}")
    print(f"  integrators_info(): {entity.integrators_info()}")
    print(f"  get_pending_vars(): {entity.get_pending_vars()}")
    print(f"  get_variables(): {entity.get_variables()}")
    
    # Verify expected results using getter methods
    expected_output = ["V_x", "V_z"]  # Both defined by equations
    expected_equation_defined = ["V_x", "V_z"]  # Same as output
    expected_input = ["V_y"]          # Not defined by equations
    expected_integrator_vars = ["V_z"]  # z is defined by integrator
    expected_integrators_info = [("V_z", "E_eq2")]  # z -> eq2 mapping
    expected_pending_vars = []  # All variables are either defined or input
    expected_all_variables = ["V_x", "V_y", "V_z"]  # All variables in forest
    
    success = True
    if set(entity.get_output_vars()) != set(expected_output):
        print(f"ERROR: get_output_vars() mismatch. Expected: {expected_output}, Got: {entity.get_output_vars()}")
        success = False
    
    if set(entity.get_equation_defined_vars()) != set(expected_equation_defined):
        print(f"ERROR: get_equation_defined_vars() mismatch. Expected: {expected_equation_defined}, Got: {entity.get_equation_defined_vars()}")
        success = False
    
    if set(entity.get_input_vars()) != set(expected_input):
        print(f"ERROR: get_input_vars() mismatch. Expected: {expected_input}, Got: {entity.get_input_vars()}")
        success = False
    
    if set(entity.get_integrator_vars()) != set(expected_integrator_vars):
        print(f"ERROR: get_integrator_vars() mismatch. Expected: {expected_integrator_vars}, Got: {entity.get_integrator_vars()}")
        success = False
    
    if entity.integrators_info() != expected_integrators_info:
        print(f"ERROR: integrators_info() mismatch. Expected: {expected_integrators_info}, Got: {entity.integrators_info()}")
        success = False
    
    if set(entity.get_pending_vars()) != set(expected_pending_vars):
        print(f"ERROR: get_pending_vars() mismatch. Expected: {expected_pending_vars}, Got: {entity.get_pending_vars()}")
        success = False
        
    if set(entity.get_variables()) != set(expected_all_variables):
        print(f"ERROR: get_variables() mismatch. Expected: {expected_all_variables}, Got: {entity.get_variables()}")
        success = False
    
    if success:
        print("\n✅ SUCCESS: Entity list generation works correctly!")
        return True
    else:
        print("\n❌ FAILURE: Entity list generation has issues!")
        return False

if __name__ == "__main__":
    test_entity_list_generation()
