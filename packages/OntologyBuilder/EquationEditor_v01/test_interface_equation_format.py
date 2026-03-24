#!/usr/bin/env python3
"""
Test script to verify interface equations are created in proper format
"""

import sys
import os

# Add the Common directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from OntologyBuilder.EquationEditor_v01.variable_framework import Variables
from Common.ontology_container import OntologyContainer

def test_interface_equation_format():
    """Test that interface equations use proper record structure"""
    
    print("Testing Interface Equation Format")
    print("=" * 50)
    
    # Create a minimal test setup
    variables = Variables()
    variables.ontology_container = OntologyContainer("test_ontology")
    
    # Setup basic structure
    variables.ontology_container.networks = ["physical", "macroscopic"]
    variables.ontology_container.heirs_network_dictionary = {
        "physical": ["physical"],
        "macroscopic": ["macroscopic"]
    }
    variables.ontology_container.variable_types_on_networks = {
        "physical": ["state"],
        "macroscopic": ["state"]
    }
    variables.ontology_container.indices = {}
    
    # Mock the required methods
    def newProMoVariableIRI():
        return "V_test"
    
    def newProMoEquationIRI():
        return "E_test"
    
    variables.newProMoVariableIRI = newProMoVariableIRI
    variables.newProMoEquationIRI = newProMoEquationIRI
    
    # Create a mock source variable
    class MockVariable:
        def __init__(self):
            self.label = "T"
            self.type = "state"
            self.network = "physical"
            self.index_structures = []
            self.units = "K"
            self.aliases = {"latex": "T", "global_ID": "V_test"}
            self.memory = None
    
    # Add mock source variable
    source_var = MockVariable()
    source_var_ID = "V_source"
    variables[source_var_ID] = source_var
    
    # Test interface variable creation
    try:
        interface_var_ID = variables.createInterfaceVariable("physical", source_var_ID, "macroscopic")
        
        print(f"✓ Interface variable created: {interface_var_ID}")
        
        # Check the interface variable
        interface_var = variables[interface_var_ID]
        print(f"✓ Interface variable label: {interface_var.label}")
        print(f"✓ Interface variable network: {interface_var.network}")
        
        # Check the interface equation
        if interface_var.equations:
            equ_ID, equation = list(interface_var.equations.items())[0]
            print(f"✓ Interface equation ID: {equ_ID}")
            
            # Verify proper equation record structure
            required_fields = ["rhs", "type", "doc", "network", "incidence_list", "created", "modified"]
            missing_fields = [field for field in required_fields if field not in equation]
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False
            else:
                print("✓ All required fields present")
            
            # Check RHS format
            rhs = equation["rhs"]
            if "global_ID" in rhs and "latex" in rhs:
                print("✓ RHS has proper format: {'global_ID': ..., 'latex': ...}")
                print(f"   global_ID: {rhs['global_ID']}")
                print(f"   latex: {rhs['latex']}")
            else:
                print("❌ RHS format incorrect")
                return False
            
            # Check incidence list
            if isinstance(equation["incidence_list"], list):
                print(f"✓ Incidence list present: {equation['incidence_list']}")
            else:
                print("❌ Incidence list missing or not a list")
                return False
            
            # Check equation type
            if equation["type"] == "generic":
                print("✓ Equation type is 'generic' (standard)")
            else:
                print(f"❌ Unexpected equation type: {equation['type']}")
                return False
                
        else:
            print("❌ No equation found in interface variable")
            return False
        
        # Check ontology container equation dictionary
        if equ_ID in variables.ontology_container.equation_dictionary:
            ont_equation = variables.ontology_container.equation_dictionary[equ_ID]
            if ont_equation == equation:
                print("✓ Equation properly stored in ontology container")
            else:
                print("❌ Equation mismatch in ontology container")
                return False
        else:
            print("❌ Equation not found in ontology container")
            return False
        
        print("\n✅ Interface Equation Format Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during interface variable creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_interface_equation_format()
    if success:
        print("\n🎯 Interface equations are now properly formatted!")
    else:
        print("\n❌ Interface equation format needs more work")
        sys.exit(1)
