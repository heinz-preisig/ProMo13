#!/usr/bin/env python3
"""
Test that interface domain is properly indexed for LaTeX generation
"""

import sys
import os

# Add the Common directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from OntologyBuilder.EquationEditor_v01.variable_framework import Variables

def test_interface_domain_indexing():
    """Test that interface domain is included in index_definition_network_for_variable_component_class"""
    
    print("Testing Interface Domain Indexing")
    print("=" * 40)
    
    try:
        # Create a mock ontology container
        class MockOntologyContainer:
            def __init__(self):
                self.networks = ["physical", "macroscopic"]
                self.variable_types_on_networks = {
                    "physical": {"state", "algebraic"},
                    "macroscopic": {"state", "algebraic"},
                    "interface": {"state", "algebraic"}
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
        
        mock_ontology = MockOntologyContainer()
        
        # Create a variables container
        variables = Variables(mock_ontology)
        
        # Mock some interface variables
        class MockVariable:
            def __init__(self, var_id, label, var_type, network):
                self.ID = var_id
                self.label = label
                self.type = var_type
                self.network = network
        
        # Add interface variables
        interface_var = MockVariable("V_interface1", "physical_T", "state", "interface")
        variables[interface_var.ID] = interface_var
        
        # Mock the interface domain
        variables.interface_domain = "interface"
        
        # Mock the required attributes
        variables.networks = ["physical", "macroscopic"]
        variables.interconnection_networks = []
        variables.intraconnection_networks = []
        
        variables.ontology_container = mock_ontology
        
        # Test the indexing
        variables.indexVariables()
        
        print("✓ Variables indexed successfully")
        
        # Check if interface domain is in the index
        if "interface" in variables.index_definition_network_for_variable_component_class:
            print("✓ Interface domain found in index_definition_network_for_variable_component_class")
            
            interface_index = variables.index_definition_network_for_variable_component_class["interface"]
            print(f"  Interface index contents: {interface_index}")
            
            # Check if our interface variable is indexed
            if "state" in interface_index and interface_var.ID in interface_index["state"]:
                print("✓ Interface variable properly indexed")
            else:
                print("❌ Interface variable not found in index")
                return False
        else:
            print("❌ Interface domain NOT found in index")
            print(f"  Available domains: {list(variables.index_definition_network_for_variable_component_class.keys())}")
            return False
        
        print("\n✅ Interface Domain Indexing Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_fix_context():
    """Show what the fix addresses"""
    
    print("\nFix Context")
    print("=" * 15)
    
    print("❌ ORIGINAL ERROR:")
    print("KeyError: 'interface' in LaTeX generation")
    print("")
    print("CAUSE:")
    print("- Interface variables created in 'interface' domain")
    print("- LaTeX generation uses index_definition_network_for_variable_component_class")
    print("- Interface domain was not included in this index")
    print("- KeyError when trying to access index_dictionary['interface']")
    print("")
    print("✅ FIX APPLIED:")
    print("""
# Added interface domain handling in indexVariables()
if hasattr(self, 'interface_domain') and self.interface_domain:
  self.index_definition_network_for_variable_component_class[self.interface_domain] = {}
  for ID in self:
    if self[ID].network == self.interface_domain:
      t = self[ID].type
      if t not in self.index_definition_network_for_variable_component_class[self.interface_domain]:
        self.index_definition_network_for_variable_component_class[self.interface_domain][t] = set()
      self.index_definition_network_for_variable_component_class[self.interface_domain][t].add(ID)
""")
    print("")
    print("RESULT:")
    print("- Interface domain now properly indexed")
    print("- LaTeX generation can find interface variables")
    print("- No more KeyError during save/compile")

if __name__ == "__main__":
    success = test_interface_domain_indexing()
    show_fix_context()
    
    if success:
        print("\n🎯 Interface domain indexing fix verified!")
        print("The LaTeX KeyError should be resolved.")
    else:
        print("\n❌ Fix needs more work")
        sys.exit(1)
