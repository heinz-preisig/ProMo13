#!/usr/bin/env python3
"""
Test LaTeX decoration in interface variable definition
"""

import sys
import os

# Add the Common directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_interface_variable_latex_definition():
    """Test that interface variables have LaTeX decoration in their definition"""
    
    print("Testing Interface Variable LaTeX Definition")
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
            print(f"  Network: {interface_var.network}")
            print(f"  LaTeX alias: {interface_var.aliases.get('latex', 'None')}")
            
            # Check if LaTeX is decorated
            latex = interface_var.aliases.get('latex', '')
            if '\\multimapdot' in latex:
                print(f"✓ LaTeX decoration applied: {latex}")
                
                # Should be: \multimapdot{T}
                expected = f"\\multimapdot{{{source_var.aliases.get('latex', source_var.label)}}}"
                if latex == expected:
                    print(f"✓ LaTeX decoration matches expected: {expected}")
                else:
                    print(f"❌ LaTeX decoration mismatch:")
                    print(f"  Expected: {expected}")
                    print(f"  Got: {latex}")
                    return False
            else:
                print(f"❌ No LaTeX decoration found: {latex}")
                return False
        else:
            print("❌ Failed to create interface variable")
            return False
        
        print("\n✅ Interface Variable LaTeX Definition Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_improved_approach():
    """Show the improved approach benefits"""
    
    print("\nImproved LaTeX Decoration Approach")
    print("=" * 40)
    
    print("✅ BETTER IMPLEMENTATION:")
    print("1. LaTeX decoration added to variable aliases during creation")
    print("2. Template uses compiled_lhs['latex'] directly")
    print("3. No template logic needed for decoration")
    print("4. LaTeX is part of variable definition, not presentation")
    print()
    
    print("✅ BENEFITS:")
    print("- LaTeX decoration is intrinsic to variable definition")
    print("- Consistent across all uses of the variable")
    print("- Template stays simple and clean")
    print("- No conditional logic in template")
    print("- Easier to maintain and debug")
    print()
    
    print("✅ RESULT:")
    print("- Interface variable LaTeX: aliases['latex'] = '\\multimapdot{T}'")
    print("- Template renders: $\\multimapdot{T}$")
    print("- Clear visual distinction built into variable definition")

if __name__ == "__main__":
    success = test_interface_variable_latex_definition()
    show_improved_approach()
    
    if success:
        print("\n🎯 Interface variable LaTeX definition improved!")
        print("LaTeX decoration is now part of variable definition itself.")
    else:
        print("\n❌ LaTeX definition needs more work")
        sys.exit(1)
