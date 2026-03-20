#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Debug PNG file paths for equations
===============================================================================

This script helps debug why PNG files are not showing up in the equation selector.
"""

import os
import sys
from pathlib import Path

# Add the path to the Common package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def debug_png_paths():
    """Debug PNG file paths and equation data"""
    
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
        
        # Try to create a mock ontology container to test equation dictionary
        try:
            from Common.exchange_board import OntologyContainer
            
            print(f"\nCreating OntologyContainer...")
            container = OntologyContainer(ontology_name)
            
            if hasattr(container, 'equation_dictionary'):
                eq_dict = container.equation_dictionary
                print(f"✅ Equation dictionary has {len(eq_dict)} equations")
                
                # Check first few equations for PNG files
                for i, (eq_id, eq_data) in enumerate(eq_dict.items()):
                    if i >= 5:  # Check first 5
                        break
                    
                    png_file = eq_data.get('png_file')
                    print(f"  {eq_id}: PNG = {png_file}")
                    
                    if png_file and os.path.exists(png_file):
                        print(f"    ✅ PNG file exists")
                    elif png_file:
                        print(f"    ❌ PNG file not found")
                    else:
                        print(f"    ⚪ No PNG file specified")
            else:
                print("❌ No equation dictionary found")
                
        except Exception as e:
            print(f"❌ Error creating OntologyContainer: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_icon_loading():
    """Test if PyQt5 can load PNG icons"""
    print("\nPyQt5 Icon Loading Test")
    print("=" * 30)
    
    try:
        from PyQt5 import QtGui, QtWidgets
        import sys
        
        # Create a minimal QApplication
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        
        # Test loading a simple PNG if available
        test_png = "/tmp/test.png"  # This likely doesn't exist, but we'll test the error handling
        
        icon = QtGui.QIcon(test_png)
        if icon.isNull():
            print(f"❌ Icon is null for {test_png} (expected)")
        else:
            print(f"✅ Icon loaded successfully for {test_png}")
        
        # Test with a simple generated image
        from PyQt5.QtGui import QPixmap
        
        pixmap = QPixmap(100, 50)
        pixmap.fill(QtGui.QColor("red"))
        icon = QtGui.QIcon(pixmap)
        
        if icon.isNull():
            print("❌ Generated icon is null")
        else:
            print("✅ Generated icon works")
        
        print("PyQt5 icon loading test completed")
        
    except Exception as e:
        print(f"❌ PyQt5 test failed: {e}")

if __name__ == "__main__":
    debug_png_paths()
    test_icon_loading()
