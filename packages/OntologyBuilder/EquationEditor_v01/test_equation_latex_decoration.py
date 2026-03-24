#!/usr/bin/env python3
"""
Test that interface equations show LaTeX decorator
"""

import sys
import os

# Add the Common directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_interface_equation_latex():
    """Test that interface equations have decorated LaTeX in RHS"""
    
    print("Testing Interface Equation LaTeX Decoration")
    print("=" * 50)
    
    try:
        from OntologyBuilder.EquationEditor_v01.variable_framework import Variables
        
        # Create a mock ontology container
        class MockOntologyContainer:
            def __init__(self):
                self.networks = ["physical", "macroscopic"]
                self.variable_types_on_networks = {
                    "physical": {"state", "algebraic"},
                    "macroscopic": {"state", "algebraic"},
                }
                self.ontology_tree = {
                    "physical": {"behaviour": {"node": ["state", "algebraic"]}},
                    "macroscopic": {"behaviour": {"node": ["state", "algebraic"]}}
                }
                self.heirs_network_dictionary = {
                    "root": ["physical", "macroscopic"],
                    "physical": ["physical"],
                    "macroscopic": ["macroscopic"]
                }
                self.list_inter_branches_pairs = []
                self.equation_dictionary = {}
        
        mock_ontology = MockOntologyContainer()
        
        # Create variables container
        variables = Variables(mock_ontology)
        
        # Mock a source variable with LaTeX alias
        class MockVariable:
            def __init__(self, var_id, label, var_type, network, latex_alias=None):
                self.ID = var_id
                self.label = label
                self.type = var_type
                self.network = network
                self.aliases = {"latex": latex_alias} if latex_alias else {}
                self.index_structures = []
                self.units = type('Units', (), {'prettyPrint': lambda: "K"})()
                self.memory = None
        
        # Create source variable with LaTeX
        source_var = MockVariable("V_source1", "T", "state", "physical", "T")
        variables[source_var.ID] = source_var
        
        print(f"✓ Created source variable: {source_var.label}")
        print(f"  LaTeX alias: {source_var.aliases.get('latex', 'None')}")
        
        # Create interface variable
        interface_var_ID = variables.createInterfaceVariable("V_source1")
        
        if interface_var_ID:
            interface_var = variables[interface_var_ID]
            print(f"✓ Created interface variable: {interface_var.label}")
            print(f"  LaTeX alias: {interface_var.aliases.get('latex', 'None')}")
            
            # Check interface equation
            if interface_var.equations:
                for equ_ID, equ_record in interface_var.equations.items():
                    print(f"✓ Interface equation {equ_ID}:")
                    print(f"  RHS global_ID: {equ_record['rhs']['global_ID']}")
                    print(f"  RHS latex: {equ_record['rhs']['latex']}")
                    
                    # Check if RHS LaTeX is decorated
                    rhs_latex = equ_record['rhs']['latex']
                    if '\\multimap' in rhs_latex:
                        print(f"✓ RHS LaTeX decorated: {rhs_latex}")
                        
                        # Should be: \multimap{T}
                        expected = f"\\\\multimap{{{source_var.aliases.get('latex', source_var.label)}}}"
                        if rhs_latex == expected:
                            print(f"✓ LaTeX decoration matches expected: {expected}")
                        else:
                            print(f"❌ LaTeX decoration mismatch:")
                            print(f"  Expected: {expected}")
                            print(f"  Got: {rhs_latex}")
                            return False
                    else:
                        print(f"❌ No LaTeX decoration in RHS: {rhs_latex}")
                        return False
            else:
                print("❌ Interface variable has no equations")
                return False
        else:
            print("❌ Failed to create interface variable")
            return False
        
        print("\n✅ Interface Equation LaTeX Decoration Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_equation_fix():
    """Show what the equation fix provides"""
    
    print("\nInterface Equation LaTeX Decoration Fix")
    print("=" * 45)
    
    print("✅ PROBLEM SOLVED:")
    print("- Interface equations now show decorated LaTeX in RHS")
    print("- Control equations display: physical_T = \\multimap{T}")
    print("- Clear visual indication of interface variable reference")
    print("- Consistent with interface variable LaTeX decoration")
    print()
    
    print("✅ IMPLEMENTATION:")
    print("1. Create decorated LaTeX for source variable")
    print("2. Use decorated LaTeX in equation RHS dictionary")
    print("3. Equation record contains: {'global_ID': V_source, 'latex': '\\\\multimap{T}'}")
    print("4. LaTeX compilation shows decorated interface variable")
    print()
    
    print("✅ VISUAL RESULT:")
    print("- Control equation: physical_T = \\\\multimap{T}")
    print("- Clear that RHS refers to decorated interface variable")
    print("- Consistent visual language throughout documentation")

if __name__ == "__main__":
    success = test_interface_equation_latex()
    show_equation_fix()
    
    if success:
        print("\n🎯 Interface equation LaTeX decoration ready!")
        print("Control equations will now show decorated interface variables.")
    else:
        print("\n❌ Equation LaTeX decoration needs more work")
        sys.exit(1)
