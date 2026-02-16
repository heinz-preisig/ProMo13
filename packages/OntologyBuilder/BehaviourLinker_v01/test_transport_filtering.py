#!/usr/bin/env python3
"""
Test script to verify transport variable filtering in output variables
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
from Common.classes.variable import Variable

def create_test_variable(var_id, var_type="state"):
    """Create a test variable with specified type"""
    return Variable(
        var_id=var_id,
        img_path="",
        IRI="",
        aliases={},
        compiled_lhs={},
        doc=f"Test variable {var_id}",
        equations=[],
        index_structures=["I_1"],
        label=var_id,
        network="test_network",
        port_variable=False,
        tokens=[],
        memory="",
        imported=False,
        type=var_type,
        units=[],
        created="2024-01-01 00:00:00",
        modified="2024-01-01 00:00:00"
    )

def test_transport_filtering():
    """Test that transport variables are filtered out from output variables"""
    print("=== Testing Transport Variable Filtering ===")
    
    # Create test equations
    eq1 = Equation(
        eq_id="E_eq1",
        img_path="",
        type="algebraic",
        lhs={'global_ID': 'V_state_var'},
        rhs={'global_ID': 'V_transport_var'},
        network="test_network",
        doc="Test equation 1",
        created="2024-01-01 00:00:00",
        modified="2024-01-01 00:00:00"
    )
    
    eq2 = Equation(
        eq_id="E_eq2",
        img_path="",
        type="algebraic",
        lhs={'global_ID': 'V_transport_var'},
        rhs={'global_ID': 'V_input_var'},
        network="test_network",
        doc="Test equation 2 (defines transport variable)",
        created="2024-01-01 00:00:00",
        modified="2024-01-01 00:00:00"
    )
    
    all_equations = {
        "E_eq1": eq1,
        "E_eq2": eq2
    }
    
    # Set up operators
    eq1.operators = {"Integral": "Integral"}
    eq2.operators = {"Integral": "Integral"}
    
    # Create a test var_eq_forest
    var_eq_forest = [
        {
            "V_state_var": ["E_eq1"],      # state variable defined by eq1
            "V_transport_var": ["E_eq2"],   # transport variable defined by eq2
            "V_input_var": [],              # input variable (no defining equation)
        },
        {
            "E_eq1": ["V_state_var", "V_transport_var"],
            "E_eq2": ["V_transport_var", "V_input_var"]
        }
    ]
    
    # Create test variables
    all_variables = {
        "V_state_var": create_test_variable("V_state_var", "state"),
        "V_transport_var": create_test_variable("V_transport_var", "transport"),
        "V_input_var": create_test_variable("V_input_var", "input")
    }
    
    # Create Entity with the test data
    entity = Entity(
        entity_id="test_entity",
        all_equations=all_equations,
        var_eq_forest=var_eq_forest,
        init_vars=[],
        input_vars=[],
        output_vars=[]
    )
    
    print("=== Test 1: Without variable filtering ===")
    equation_defined_vars = entity.get_equation_defined_vars()
    print(f"  All equation-defined variables: {equation_defined_vars}")
    print(f"  Expected: ['V_state_var', 'V_transport_var'] (both defined by equations)")
    
    assert set(equation_defined_vars) == {"V_state_var", "V_transport_var"}
    print("  ✅ Test 1 passed")
    
    print("\n=== Test 2: With transport variable filtering ===")
    filtered_vars = entity.get_equation_defined_vars(all_variables=all_variables)
    print(f"  Filtered equation-defined variables: {filtered_vars}")
    print(f"  Expected: ['V_state_var'] (transport variable filtered out)")
    
    assert set(filtered_vars) == {"V_state_var"}
    print("  ✅ Test 2 passed")
    
    print("\n=== Test 3: Backward compatibility (get_output_vars) ===")
    # get_output_vars() should still work without parameters
    output_vars = entity.get_output_vars()
    print(f"  get_output_vars(): {output_vars}")
    print(f"  Expected: ['V_state_var', 'V_transport_var'] (no filtering)")
    
    assert set(output_vars) == {"V_state_var", "V_transport_var"}
    print("  ✅ Test 3 passed")
    
    print("\n=== Test 4: get_output_vars with filtering ===")
    # get_output_vars() with all_variables parameter should filter
    filtered_output_vars = entity.get_output_vars(all_variables=all_variables)
    print(f"  get_output_vars(all_variables): {filtered_output_vars}")
    print(f"  Expected: ['V_state_var'] (transport variable filtered out)")
    
    assert set(filtered_output_vars) == {"V_state_var"}
    print("  ✅ Test 4 passed")
    
    print("\n=== Test 5: get_transport_vars method ===")
    transport_vars = entity.get_transport_vars(all_variables)
    print(f"  get_transport_vars(): {transport_vars}")
    print(f"  Expected: ['V_transport_var'] (only transport variable)")
    
    assert set(transport_vars) == {"V_transport_var"}
    print("  ✅ Test 5 passed")
    
    print("\n=== Test 6: Verify variable types ===")
    for var_id, var_obj in all_variables.items():
        print(f"  {var_id}: type = {var_obj.type}")
    
    print("\n🎉 All transport filtering tests passed!")

if __name__ == "__main__":
    test_transport_filtering()
