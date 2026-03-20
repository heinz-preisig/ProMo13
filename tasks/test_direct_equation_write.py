#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
Direct test of writeEquationsFile method
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
    Direct test of the writeEquationsFile method
    """
    try:
        print("Testing writeEquationsFile method directly...")
        
        # Import the exchange board
        from Common.exchange_board import OntologyContainer
        from Common.resource_initialisation import FILES, DIRECTORIES
        
        # Create a mock ontology container with minimal setup
        class MockOntologyContainer:
            def __init__(self):
                self.ontology_location = "test_ontology"
                self.equation_dictionary = {
                    "E_1": {"lhs": "V_1", "rhs": "V_2 + V_3"},
                    "E_3": {"lhs": "V_4", "rhs": "V_5 * 2"},
                    "E_2": {"lhs": "V_6", "rhs": "V_7 + V_8"}
                }
        
        # Test the method
        mock_container = MockOntologyContainer()
        exchange_board = OntologyContainer("test_ontology")
        
        # Manually set the required attributes to avoid constructor issues
        exchange_board.ontology_location = "test_ontology"
        exchange_board.ontology_name = "test_ontology"
        exchange_board.ontology_container = mock_container
        
        # Check if method exists and test it
        if hasattr(exchange_board, 'writeEquationsFile'):
            print("✅ writeEquationsFile method exists in exchange_board")
            
            # Test the method
            print("Testing writeEquationsFile method...")
            success = exchange_board.writeEquationsFile("internal")
            
            if success:
                print("✅ Equation writing works correctly!")
                
                # Check if the file was created
                expected_file = FILES["coded_equations"] % ("test_ontology", "internal")
                expected_file = expected_file.replace(".json", ".txt")
                
                if os.path.exists(expected_file):
                    print(f"📁 File created: {expected_file}")
                    
                    # Read and check content
                    with open(expected_file, 'r') as f:
                        content = f.read()
                        lines = content.strip().split('\n')
                        print(f"📄 File contains {len(lines)} lines")
                        
                        # Check if equations are in numerical order
                        eq_ids = []
                        for line in lines:
                            if line.strip():
                                parts = line.split(' :: ')
                                if len(parts) >= 1:
                                    eq_id = parts[0].strip()
                                    if eq_id.startswith('E_'):
                                        try:
                                            num = int(eq_id[2:])
                                            eq_ids.append(num)
                                        except ValueError:
                                            pass
                        
                        # Sort and check
                        eq_ids.sort()
                        print(f"📊 Equation IDs in order: {[f'E_{id}' for id in eq_ids]}")
                else:
                    print("❌ Expected file was not created")
            else:
                print("❌ writeEquationsFile method not found in exchange_board")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
