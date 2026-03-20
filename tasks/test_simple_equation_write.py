#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
Simple test for equation writing functionality
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

# Add to project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.extend([project_root, os.path.join(project_root, 'packages'), os.path.join(project_root, 'tasks')])

def main():
    """
    Simple test to verify equation writing method exists and works
    """
    try:
        print("Testing equation writing method...")
        
        # Import the exchange board
        from Common.exchange_board import OntologyContainer
        
        # Create a minimal mock ontology container
        class MockOntologyContainer:
            def __init__(self):
                self.ontology_location = "test_ontology"
                self.ontology_container = {"version": "3.0"}  # Add version to avoid error
                self.equation_dictionary = {
                    "E_1": {"lhs": "V_1", "rhs": "V_2 + V_3"},
                    "E_3": {"lhs": "V_4", "rhs": "V_5 * 2"},
                    "E_2": {"lhs": "V_6", "rhs": "V_7 + V_8"}
                }
        
        # Test the method exists
        mock_container = MockOntologyContainer()
        exchange_board = OntologyContainer("test_ontology")
        
        # Check if method exists
        if hasattr(exchange_board, 'writeEquationsFile'):
            print("✅ writeEquationsFile method exists in exchange_board")
            
            # Test the method
            print("Testing writeEquationsFile method...")
            success = exchange_board.writeEquationsFile("internal")
            
            if success:
                print("✅ Equation writing works correctly!")
                print("📁 Method is available for use in UI")
            else:
                print("❌ Equation writing test failed")
        else:
            print("❌ writeEquationsFile method not found in exchange_board")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
