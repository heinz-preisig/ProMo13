#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Debug PNG file paths only (no PyQt5)
===============================================================================

This script checks PNG file paths without requiring PyQt5.
"""

import os
import sys

# Add the path to the Common package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def debug_png_paths_only():
    """Debug PNG file paths without PyQt5"""
    
    print("PNG File Path Debug")
    print("=" * 50)
    
    try:
        # Try to get the ontology name and directories
        from Common.common_resources import getOntologyName, DIRECTORIES
        
        ontology_name = getOntologyName(task="task_entity_generation")
        if not ontology_name:
            print("No ontology found")
            return
        
        print(f"Ontology name: {ontology_name}")
        
        # Get the LaTeX directory
        latex_dir = DIRECTORIES["latex_doc_location"] % ontology_name
        print(f"LaTeX directory: {latex_dir}")
        
        if not os.path.exists(latex_dir):
            print(f"❌ LaTeX directory does not exist: {latex_dir}")
            return
        
        print(f"✅ LaTeX directory exists")
        
        # List PNG files in the directory
        png_files = []
        for file in os.listdir(latex_dir):
            if file.endswith('.png'):
                png_files.append(file)
        
        print(f"Found {len(png_files)} PNG files:")
        for png_file in png_files[:10]:  # Show first 10
            full_path = os.path.join(latex_dir, png_file)
            file_size = os.path.getsize(full_path)
            print(f"  {png_file} ({file_size} bytes)")
        
        if len(png_files) > 10:
            print(f"  ... and {len(png_files) - 10} more")
        
        # Check if any PNG files exist for common equation names
        common_eq_names = ['eq1', 'eq2', 'eq3', 'mass_balance', 'energy_balance']
        print(f"\nChecking common equation names:")
        for eq_name in common_eq_names:
            png_path = os.path.join(latex_dir, f"{eq_name}.png")
            if os.path.exists(png_path):
                size = os.path.getsize(png_path)
                print(f"  ✅ {eq_name}.png exists ({size} bytes)")
            else:
                print(f"  ❌ {eq_name}.png not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_png_paths_only()
