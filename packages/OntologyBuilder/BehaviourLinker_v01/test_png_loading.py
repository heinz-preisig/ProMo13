#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Test PNG loading with actual files
===============================================================================

This script tests loading actual PNG files from the LaTeX directory.
"""

import os
import sys

def test_png_loading():
    """Test loading actual PNG files"""
    
    print("PNG Loading Test")
    print("=" * 30)
    
    # Path to the LaTeX directory
    latex_dir = "/home/heinz/1_Gits/CAM12/Ontology_Repository/processes_distributed_001/LaTeX"
    
    if not os.path.exists(latex_dir):
        print(f"❌ LaTeX directory not found: {latex_dir}")
        return
    
    print(f"✅ LaTeX directory found: {latex_dir}")
    
    # Find some PNG files
    png_files = []
    for file in os.listdir(latex_dir):
        if file.endswith('.png') and file.startswith('E_'):
            png_files.append(file)
            if len(png_files) >= 5:  # Test first 5 equation PNGs
                break
    
    if not png_files:
        print("❌ No equation PNG files found")
        return
    
    print(f"✅ Found {len(png_files)} equation PNG files to test:")
    
    try:
        from PyQt5 import QtGui, QtWidgets
        from PyQt5.QtCore import QSize
        
        # Create minimal QApplication
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        
        for png_file in png_files:
            png_path = os.path.join(latex_dir, png_file)
            file_size = os.path.getsize(png_path)
            
            print(f"\nTesting: {png_file} ({file_size} bytes)")
            
            # Test loading as QPixmap
            pixmap = QtGui.QPixmap(png_path)
            if pixmap.isNull():
                print(f"  ❌ Pixmap is null")
            else:
                print(f"  ✅ Pixmap loaded: {pixmap.width()}x{pixmap.height()}")
            
            # Test loading as QIcon
            icon = QtGui.QIcon(png_path)
            if icon.isNull():
                print(f"  ❌ Icon is null")
            else:
                print(f"  ✅ Icon loaded successfully")
                
                # Test getting pixmap at different sizes
                for size in [50, 100, 200, 300]:
                    test_pixmap = icon.pixmap(QSize(size, size))
                    if test_pixmap.isNull():
                        print(f"    ❌ Failed at {size}x{size}")
                    else:
                        print(f"    ✅ {size}x{size}: {test_pixmap.width()}x{test_pixmap.height()}")
        
        print(f"\n✅ PNG loading test completed successfully!")
        
    except Exception as e:
        print(f"❌ PyQt5 test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_png_loading()
