#!/usr/bin/env python3
"""
Test loading interface variables from saved data
"""

import sys
import os

# Add the Common directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_interface_variable_loading():
    """Test that interface variables can be loaded without KeyError"""
    
    print("Testing Interface Variable Loading")
    print("=" * 40)
    
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
                self.variables = {}
                self.equation_dictionary = {}
        
        mock_ontology = MockOntologyContainer()
        
        # Create variables container
        variables = Variables(mock_ontology)
        
        # Mock interface variables that would be loaded from saved data
        class MockVariable:
            def __init__(self, var_id, label, var_type, network):
                self.ID = var_id
                self.label = label
                self.type = var_type
                self.network = network
                self.equations = {}
                self.aliases = {}
                self.index_structures = []
                self.units = "K"
                self.memory = None
        
        # Simulate loading interface variables from saved data
        interface_var1 = MockVariable("V_interface1", "physical_T", "state", "interface")
        interface_var2 = MockVariable("V_interface2", "macroscopic_F", "state", "interface")
        normal_var = MockVariable("V_normal1", "T", "state", "physical")
        
        variables[interface_var1.ID] = interface_var1
        variables[interface_var2.ID] = interface_var2
        variables[normal_var.ID] = normal_var
        
        print("✓ Created mock variables including interface variables")
        
        # This should trigger the fix - detect interface variables and set up domain
        variables.indexVariables()
        
        print("✓ Variables indexed successfully without KeyError")
        
        # Verify interface domain was created and indexed
        if hasattr(variables, 'interface_domain') and variables.interface_domain == "interface":
            print("✓ Interface domain automatically created during indexing")
        else:
            print("❌ Interface domain not created")
            return False
        
        # Check that interface variables are in the index
        if "interface" in variables.index_definition_networks_for_variable:
            interface_vars = variables.index_definition_networks_for_variable["interface"]
            if interface_var1.ID in interface_vars and interface_var2.ID in interface_vars:
                print("✓ Interface variables properly indexed")
            else:
                print("❌ Interface variables not found in index")
                return False
        else:
            print("❌ Interface domain not in index_definition_networks_for_variable")
            return False
        
        # Check component class index
        if "interface" in variables.index_definition_network_for_variable_component_class:
            component_index = variables.index_definition_network_for_variable_component_class["interface"]
            if "state" in component_index and interface_var1.ID in component_index["state"]:
                print("✓ Interface variables in component class index")
            else:
                print("❌ Interface variables not in component class index")
                return False
        else:
            print("❌ Interface domain not in component class index")
            return False
        
        print("\n✅ Interface Variable Loading Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during loading test: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_loading_fix():
    """Show what the loading fix addresses"""
    
    print("\nLoading Fix Context")
    print("=" * 20)
    
    print("❌ ORIGINAL LOADING ERROR:")
    print("KeyError: 'interface' during variable indexing")
    print("")
    print("CAUSE:")
    print("- Interface variables saved in 'interface' domain")
    print("- During loading, variables indexed before interface domain created")
    print("- indexVariables() tried to access index['interface'] that didn't exist")
    print("")
    print("✅ LOADING FIX APPLIED:")
    print("""
# Check if any loaded variables are in the interface domain
has_interface_variables = any(self[ID].network == "interface" for ID in self)

# Add interface domain if it exists or if we have interface variables
if (hasattr(self, 'interface_domain') and self.interface_domain) or has_interface_variables:
    if not hasattr(self, 'interface_domain') or not self.interface_domain:
        self.interface_domain = "interface"
    if self.interface_domain not in all_networks:
        all_networks.append(self.interface_domain)
""")
    print("")
    print("RESULT:")
    print("- Interface domain auto-created when interface variables detected")
    print("- No more KeyError during loading")
    print("- Interface variables properly indexed from saved data")

if __name__ == "__main__":
    success = test_interface_variable_loading()
    show_loading_fix()
    
    if success:
        print("\n🎯 Interface variable loading fix verified!")
        print("The loading KeyError should be resolved.")
    else:
        print("\n❌ Loading fix needs more work")
        sys.exit(1)
