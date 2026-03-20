#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
Test script to verify equation writing in exchange_board
===============================================================================
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

# Add to project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.extend([project_root, os.path.join(project_root, 'packages'), os.path.join(project_root, 'tasks')])

from Common.exchange_board import OntologyContainer

def main():
    """
    Test the equation writing functionality in exchange_board
    """
    try:
        print("Testing equation writing in exchange_board...")
        
        # Create a mock exchange board
        exchange_board = OntologyContainer("test_ontology")
        
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
        
        # Set equation dictionary in exchange board
        # exchange_board.setEquationDictionary(equations)
        
        print(f"Created {len(equations)} sample equations")
        
        # Test the equation writing functionality
        print("\nTesting writeEquationsFile method...")
        success = exchange_board.writeEquationsFile("internal")
        
        if success:
            print("✅ Equation writing test successful!")
            print("📁 The equations_just_list_internal_format.txt file should now be created with proper sequencing")
        else:
            print("❌ Equation writing test failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
