#!/usr/bin/env python3
"""
Comprehensive test for the refactored dynamic variable list getters
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

def test_scenario_1():
    """Test basic scenario with mix of defined and undefined variables"""
    print("=== Test Scenario 1: Basic Mix ===")
    
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
    
    all_equations = {"E_eq1": eq1}
    eq1.operators = {"Integral": "Integral"}
    
    # Forest: x defined by eq1, y undefined, z undefined
    var_eq_forest = [
        {
            "V_x": ["E_eq1"],  # x is defined
            "V_y": [],         # y is undefined  
            "V_z": []          # z is undefined
        },
        {
            "E_eq1": ["V_x", "V_y"]  # eq1 uses x and y
        }
    ]
    
    entity = Entity(
        entity_id="test_entity_1",
        all_equations=all_equations,
        var_eq_forest=var_eq_forest,
        init_vars=[],
        input_vars=[],
        output_vars=[]
    )
    
    # Test dynamic getters
    print(f"  get_variables(): {entity.get_variables()}")
    print(f"  get_output_vars(): {entity.get_output_vars()}")
    print(f"  get_equation_defined_vars(): {entity.get_equation_defined_vars()}")
    print(f"  get_input_vars(): {entity.get_input_vars()}")
    print(f"  get_pending_vars(): {entity.get_pending_vars()}")
    
    # Verify expectations
    assert set(entity.get_variables()) == {"V_x", "V_y", "V_z"}
    assert set(entity.get_output_vars()) == {"V_x"}
    assert set(entity.get_equation_defined_vars()) == {"V_x"}  # Same as output_vars
    assert set(entity.get_input_vars()) == {"V_y", "V_z"}
    assert entity.get_pending_vars() == []
    
    print("  ✅ Scenario 1 passed\n")

def test_scenario_2():
    """Test with init variables"""
    print("=== Test Scenario 2: With Init Variables ===")
    
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
    
    all_equations = {"E_eq1": eq1}
    eq1.operators = {"Integral": "Integral"}
    
    var_eq_forest = [
        {
            "V_x": ["E_eq1"],  # x is defined
            "V_y": [],         # y is undefined
            "V_z": []          # z is undefined
        },
        {
            "E_eq1": ["V_x", "V_y"]
        }
    ]
    
    entity = Entity(
        entity_id="test_entity_2",
        all_equations=all_equations,
        var_eq_forest=var_eq_forest,
        init_vars=["V_z"],  # z is an init variable
        input_vars=[],
        output_vars=[]
    )
    
    print(f"  get_variables(): {entity.get_variables()}")
    print(f"  get_output_vars(): {entity.get_output_vars()}")
    print(f"  get_equation_defined_vars(): {entity.get_equation_defined_vars()}")
    print(f"  get_input_vars(): {entity.get_input_vars()}")
    print(f"  get_init_vars(): {entity.get_init_vars()}")
    print(f"  get_pending_vars(): {entity.get_pending_vars()}")
    
    # Verify expectations
    assert set(entity.get_variables()) == {"V_x", "V_y", "V_z"}
    assert set(entity.get_output_vars()) == {"V_x"}
    assert set(entity.get_equation_defined_vars()) == {"V_x"}  # Same as output_vars
    assert set(entity.get_input_vars()) == {"V_y"}  # y is input (undefined, not init)
    assert set(entity.get_init_vars()) == {"V_z"}
    assert entity.get_pending_vars() == []  # no pending vars
    
    print("  ✅ Scenario 2 passed\n")

def test_scenario_3():
    """Test with integrators"""
    print("=== Test Scenario 3: With Integrators ===")
    
    eq1 = Equation(
        eq_id="E_eq1",
        img_path="",
        type="integrator",
        lhs={'global_ID': 'V_x'},
        rhs={'global_ID': 'Integral V_y'},
        network="test_network",
        doc="Test integrator",
        created="2024-01-01 00:00:00",
        modified="2024-01-01 00:00:00"
    )
    
    all_equations = {"E_eq1": eq1}
    eq1.operators = {"Integral": "Integral"}
    
    var_eq_forest = [
        {
            "V_x": ["E_eq1"],  # x is defined by integrator
            "V_y": []          # y is undefined
        },
        {
            "E_eq1": ["V_x", "V_y"]
        }
    ]
    
    entity = Entity(
        entity_id="test_entity_3",
        all_equations=all_equations,
        var_eq_forest=var_eq_forest,
        init_vars=[],
        input_vars=[],
        output_vars=[]
    )
    
    print(f"  get_variables(): {entity.get_variables()}")
    print(f"  get_output_vars(): {entity.get_output_vars()}")
    print(f"  get_equation_defined_vars(): {entity.get_equation_defined_vars()}")
    print(f"  get_input_vars(): {entity.get_input_vars()}")
    print(f"  get_integrator_vars(): {entity.get_integrator_vars()}")
    print(f"  integrators_info(): {entity.integrators_info()}")
    
    # Verify expectations
    assert set(entity.get_variables()) == {"V_x", "V_y"}
    assert set(entity.get_output_vars()) == {"V_x"}  # x defined by integrator
    assert set(entity.get_equation_defined_vars()) == {"V_x"}  # Same as output_vars
    assert set(entity.get_input_vars()) == {"V_y"}   # y is input
    assert set(entity.get_integrator_vars()) == {"V_x"}
    assert entity.integrators_info() == [("V_x", "E_eq1")]
    
    print("  ✅ Scenario 3 passed\n")

def test_consistency():
    """Test that all methods return consistent results"""
    print("=== Test Consistency ===")
    
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
    
    all_equations = {"E_eq1": eq1}
    eq1.operators = {"Integral": "Integral"}
    
    var_eq_forest = [
        {"V_x": ["E_eq1"], "V_y": [], "V_z": []},
        {"E_eq1": ["V_x", "V_y"]}
    ]
    
    entity = Entity(
        entity_id="test_consistency",
        all_equations=all_equations,
        var_eq_forest=var_eq_forest,
        init_vars=[],
        input_vars=[],
        output_vars=[]
    )
    
    # Call multiple times to ensure consistency
    for i in range(3):
        vars1 = entity.get_variables()
        vars2 = entity.get_variables()
        assert vars1 == vars2, f"Inconsistent results on iteration {i}"
    
    # Test that all variables are accounted for
    all_vars = set(entity.get_variables())
    output_vars = set(entity.get_output_vars())
    equation_defined_vars = set(entity.get_equation_defined_vars())
    input_vars = set(entity.get_input_vars())
    init_vars = set(entity.get_init_vars())
    
    # Verify output_vars and equation_defined_vars are the same
    assert output_vars == equation_defined_vars, f"Output vars and equation-defined vars should match: {output_vars} vs {equation_defined_vars}"
    
    # All variables should be the union of output, input, and init vars
    expected_all = output_vars | input_vars | init_vars
    assert all_vars == expected_all, f"Variable sets don't match: {all_vars} vs {expected_all}"
    
    print("  ✅ Consistency test passed\n")

if __name__ == "__main__":
    try:
        test_scenario_1()
        test_scenario_2() 
        test_scenario_3()
        test_consistency()
        print("🎉 All tests passed! Dynamic variable list getters work correctly.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
