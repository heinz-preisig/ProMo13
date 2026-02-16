#!/usr/bin/env python3
"""
Test script to verify both included variables and instantiation variables lists work together
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

def test_both_lists():
    """Test that variables appear in both included and instantiation lists"""
    print("=== Testing Both Included Variables and Instantiation Lists ===")
    
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
    print(f"  get_variables(): {entity.get_variables()}")
    print(f"  get_variables_to_be_instantiated(): {entity.get_variables_to_be_instantiated()}")
    
    # Add a variable for instantiation
    print("\n=== Test 2: Add variable V_instant_1 for instantiation ===")
    entity.set_init_var("V_instant_1", True)
    
    print(f"  get_variables(): {entity.get_variables()}")
    print(f"  get_variables_to_be_instantiated(): {entity.get_variables_to_be_instantiated()}")
    
    # Verify it appears in both lists
    all_vars = entity.get_variables()
    instant_vars = entity.get_variables_to_be_instantiated()
    
    assert "V_instant_1" in all_vars, f"V_instant_1 should be in get_variables(): {all_vars}"
    assert "V_instant_1" in instant_vars, f"V_instant_1 should be in instantiation list: {instant_vars}"
    print("  ✅ V_instant_1 appears in both lists")
    
    # Add another variable for instantiation
    print("\n=== Test 3: Add variable V_instant_2 for instantiation ===")
    entity.set_init_var("V_instant_2", True)
    
    print(f"  get_variables(): {entity.get_variables()}")
    print(f"  get_variables_to_be_instantiated(): {entity.get_variables_to_be_instantiated()}")
    
    all_vars = entity.get_variables()
    instant_vars = entity.get_variables_to_be_instantiated()
    
    assert "V_instant_2" in all_vars, f"V_instant_2 should be in get_variables(): {all_vars}"
    assert "V_instant_2" in instant_vars, f"V_instant_2 should be in instantiation list: {instant_vars}"
    print("  ✅ V_instant_2 appears in both lists")
    
    # Add a variable defined by equation (should appear in included but not instantiation)
    print("\n=== Test 4: Add variable V_defined with equation ===")
    # Create a simple equation
    eq1 = Equation(
        eq_id="E_eq1",
        img_path="",
        type="algebraic",
        lhs={'global_ID': 'V_defined'},
        rhs={'global_ID': 'V_instant_1'},
        network="test_network",
        doc="Test equation",
        created="2024-01-01 00:00:00",
        modified="2024-01-01 00:00:00"
    )
    eq1.operators = {"Integral": "Integral"}
    
    entity.all_equations["E_eq1"] = eq1
    entity.var_eq_forest = [
        {
            "V_defined": ["E_eq1"],  # V_defined is defined by equation
            "V_instant_1": [],       # V_instant_1 is instantiation (no equation)
        },
        {
            "E_eq1": ["V_defined", "V_instant_1"]
        }
    ]
    
    print(f"  get_variables(): {entity.get_variables()}")
    print(f"  get_variables_to_be_instantiated(): {entity.get_variables_to_be_instantiated()}")
    
    all_vars = entity.get_variables()
    instant_vars = entity.get_variables_to_be_instantiated()
    
    # Check all variables are in included list
    assert "V_defined" in all_vars, f"V_defined should be in get_variables(): {all_vars}"
    assert "V_instant_1" in all_vars, f"V_instant_1 should be in get_variables(): {all_vars}"
    assert "V_instant_2" in all_vars, f"V_instant_2 should be in get_variables(): {all_vars}"
    
    # Check only instantiation variables are in instantiation list
    assert "V_instant_1" in instant_vars, f"V_instant_1 should be in instantiation list: {instant_vars}"
    assert "V_instant_2" in instant_vars, f"V_instant_2 should be in instantiation list: {instant_vars}"
    assert "V_defined" not in instant_vars, f"V_defined should NOT be in instantiation list: {instant_vars}"
    
    print("  ✅ All variables correctly categorized")
    
    print("\n🎉 All tests passed! Variables appear correctly in both lists.")
    print("\n=== Summary ===")
    print(f"Included variables (all): {all_vars}")
    print(f"Instantiation variables: {instant_vars}")

if __name__ == "__main__":
    test_both_lists()
