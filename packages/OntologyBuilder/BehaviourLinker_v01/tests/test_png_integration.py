#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Test PNG file integration in equation dictionary
===============================================================================

This script tests that PNG file paths are correctly added to the equation dictionary.
"""

import sys
import os

# Add the path to the Common package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_equation_dictionary_png_integration():
    """Test that equation dictionary includes PNG file paths"""
    
    print("Testing PNG File Integration in Equation Dictionary")
    print("==================================================")
    
    try:
        # Try to import and create an ontology container
        from Common.exchange_board import OntologyContainer
        from Common.common_resources import getOntologyName
        
        # Get ontology name
        ontology_name = getOntologyName(task="task_entity_generation")
        if not ontology_name:
            print("No ontology available for testing")
            return
        
        print(f"Testing with ontology: {ontology_name}")
        
        # Create ontology container
        container = OntologyContainer(ontology_name)
        
        # Check if equation dictionary exists
        if hasattr(container, 'equation_dictionary'):
            equation_dict = container.equation_dictionary
            print(f"Equation dictionary found with {len(equation_dict)} equations")
            
            # Check a few equations for PNG file paths
            png_count = 0
            sample_size = min(5, len(equation_dict))  # Check up to 5 equations
            
            for i, (eq_id, eq_data) in enumerate(equation_dict.items()):
                if i >= sample_size:
                    break
                
                png_file = eq_data.get('png_file')
                print(f"  Equation {eq_id}:")
                print(f"    Label: {eq_data.get('label', 'N/A')}")
                print(f"    PNG file: {png_file}")
                
                if png_file and os.path.exists(png_file):
                    png_count += 1
                    print(f"    ✓ PNG file exists")
                elif png_file:
                    print(f"    ⚠ PNG file specified but not found")
                else:
                    print(f"    - No PNG file specified")
                print()
            
            print(f"Summary: {png_count}/{sample_size} equations have existing PNG files")
            
        else:
            print("No equation dictionary found in ontology container")
        
        # Also check the separate PNG file dictionary
        if hasattr(container, 'list_equation_png_files'):
            png_dict = container.list_equation_png_files
            print(f"Separate PNG dictionary found with {len(png_dict)} entries")
            
            # Show a few examples
            for i, (eq_id, png_file) in enumerate(png_dict.items()):
                if i >= 3:
                    break
                print(f"  {eq_id}: {png_file}")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_equation_dictionary_png_integration()
