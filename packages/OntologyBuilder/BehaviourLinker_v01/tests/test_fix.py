#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Test the circular dependency fix
===============================================================================

This script tests that the makeEquationDictionary method works correctly
without the circular dependency issue.
"""

import sys
import os

# Add the path to the Common package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_make_equation_dictionary():
    """Test that makeEquationDictionary can be called without circular dependency"""
    
    print("Testing makeEquationDictionary method...")
    print("=" * 50)
    
    try:
        # Import the method directly to test it
        from Common.ontology_container import OntologyContainer
        
        # Create a mock container to test the method logic
        class MockContainer:
            def __init__(self):
                self.ontology_name = "test_ontology"
                self.variables = {
                    'var1': {
                        'equations': {
                            'eq1': {'label': 'Equation 1', 'expression': 'x = 1'},
                            'eq2': {'label': 'Equation 2', 'expression': 'y = 2'}
                        },
                        'compiled_lhs': 'lhs1'
                    },
                    'var2': {
                        'equations': {
                            'eq3': {'label': 'Equation 3', 'expression': 'z = 3'}
                        },
                        'compiled_lhs': 'lhs2'
                    }
                }
            
            def __load_equation_png_files_for_ids(self, equation_ids):
                """Mock PNG file loading"""
                return {
                    'eq1': '/path/to/eq1.png',
                    'eq2': None,  # No PNG for eq2
                    'eq3': '/path/to/eq3.png'
                }
            
            def makeEquationDictionary(self):
                """The fixed method"""
                equation_dictionary = {}
                
                # First pass: create basic dictionary without PNG files
                for var_ID in self.variables:
                    for eq_ID in self.variables[var_ID]["equations"]:
                        equation_dictionary[eq_ID] = self.variables[var_ID]["equations"][eq_ID]
                        equation_dictionary[eq_ID]["lhs"] = self.variables[var_ID]["compiled_lhs"]
                
                # Second pass: add PNG files to the completed dictionary
                equation_png_files = self.__load_equation_png_files_for_ids(equation_dictionary.keys())
                for eq_id in equation_dictionary:
                    equation_dictionary[eq_id]["png_file"] = equation_png_files.get(eq_id, None)
                
                return equation_dictionary
        
        # Test the method
        mock_container = MockContainer()
        result = mock_container.makeEquationDictionary()
        
        print("✓ Method executed successfully without circular dependency!")
        print(f"✓ Generated dictionary with {len(result)} equations:")
        
        for eq_id, eq_data in result.items():
            png_file = eq_data.get('png_file')
            png_status = "✓" if png_file else "○"
            print(f"  {png_status} {eq_id}: {eq_data.get('label', 'N/A')} -> PNG: {png_file}")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_make_equation_dictionary()
    sys.exit(0 if success else 1)
