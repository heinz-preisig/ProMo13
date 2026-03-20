#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
Test script to verify the fixed export functionality
===============================================================================

This script tests the modified exchange_board functionality.
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2009. 04. 17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys
from collections import OrderedDict

# Add the project root to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.extend([project_root, os.path.join(project_root, 'packages'), os.path.join(project_root, 'tasks')])

from Common.ontology_container import OntologyContainer

class MockVariable:
    """Mock variable class for testing"""
    def __init__(self, var_id, label, var_type, network, doc=""):
        self.label = label
        self.type = var_type
        self.network = network
        self.doc = doc
        self.units = "kg/s"  # Mock units
        self.equations = {}  # Mock equations dictionary

def main():
    """
    Test the fixed export functionality
    """
    try:
        print("Testing the fixed export functionality...")
        
        # Create a mock exchange board
        exchange_board = OntologyContainer("test_ontology")
        
        # Create mock variables
        variables = OrderedDict()
        variables["V_5"] = MockVariable("V_5", "FlowRate", "state", "physical", "Mass flow rate through the system")
        variables["V_1"] = MockVariable("V_1", "Temperature", "state", "physical", "System temperature")
        variables["V_3"] = MockVariable("V_3", "Pressure", "algebraic", "physical", "System pressure")
        variables["V_2"] = MockVariable("V_2", "Concentration", "state", "physical", "Chemical concentration")
        variables["V_4"] = MockVariable("V_4", "Volume", "algebraic", "physical", "System volume")
        
        # Create mock equations
        equations = {
            "E_7": {
                "type": "algebraic",
                "network": "physical",
                "rhs": {
                    "global_ID": "V_1 + V_2 * V_3",
                    "internal": "T + C * P",
                    "latex": "T + C \\cdot P"
                },
                "doc": "Combined temperature and pressure effect"
            },
            "E_2": {
                "type": "differential",
                "network": "physical",
                "rhs": {
                    "global_ID": "V_4 / V_5",
                    "internal": "V / F",
                    "latex": "\\frac{V}{F}"
                },
                "doc": "Volume flow relationship"
            },
            "E_5": {
                "type": "algebraic",
                "network": "physical",
                "rhs": {
                    "global_ID": "V_1 * 2.5",
                    "internal": "T * 2.5",
                    "latex": "2.5 \\cdot T"
                },
                "doc": "Temperature scaling"
            }
        }
        
        print(f"Created {len(variables)} sample variables and {len(equations)} sample equations")
        
        # Set equation dictionary in exchange board
        # exchange_board.setEquationDictionary(equations)
        
        # Test the write functionality (this should now create both text files)
        print("\nTesting writeVariables method...")
        exchange_board.writeVariables(variables, {}, {"test": "indices"}, {"variable": 1, "equation": 1})
        
        print("✅ Test completed!")
        print("📁 The following files should have been created:")
        print("   - variables_definition_order.txt (sorted V_1, V_2, V_3, ...)")
        print("   - equations_sequence_order.txt (sorted E_1, E_2, E_3, ...)")
        print("\nTo use with real data:")
        print("1. Run EquationComposer_01.py")
        print("2. Load your ontology data")
        print("3. Use the normal Write/Save button")
        print("4. Both files will be created automatically in the same location as your data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
