#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Simple debug without any imports that might trigger PyQt5
===============================================================================

This script checks basic file system paths without importing any project modules.
"""

import os

def simple_debug():
    """Simple debug without project imports"""
    
    print("Simple Path Debug")
    print("=" * 30)
    
    # Check common locations where PNG files might be stored
    possible_paths = [
        "/home/heinz/1_Gits/CAM12/latex",
        "/home/heinz/1_Gits/CAM12/latex_docs", 
        "/home/heinz/1_Gits/CAM12/ProMo12/latex",
        "/home/heinz/1_Gits/CAM12/ProMo12/latex_docs",
        "/home/heinz/1_Gits/CAM12",
        "/home/heinz/1_Gits/CAM12/ProMo12"
    ]
    
    for base_path in possible_paths:
        if os.path.exists(base_path):
            print(f"✅ Found: {base_path}")
            
            # Look for PNG files
            png_files = []
            try:
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.endswith('.png'):
                            png_files.append(os.path.join(root, file))
            except:
                pass
            
            if png_files:
                print(f"  Found {len(png_files)} PNG files:")
                for png_file in png_files[:5]:  # Show first 5
                    rel_path = os.path.relpath(png_file, base_path)
                    size = os.path.getsize(png_file)
                    print(f"    {rel_path} ({size} bytes)")
                
                if len(png_files) > 5:
                    print(f"    ... and {len(png_files) - 5} more")
            else:
                print(f"  No PNG files found")
        else:
            print(f"❌ Not found: {base_path}")
    
    # Also check for any ontology-related files
    print(f"\nChecking for ontology files:")
    ontology_files = []
    search_paths = ["/home/heinz/1_Gits/CAM12", "/home/heinz/1_Gits/CAM12/ProMo12"]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if 'ontology' in file.lower() and file.endswith('.json'):
                            rel_path = os.path.relpath(os.path.join(root, file), search_path)
                            ontology_files.append(rel_path)
                            if len(ontology_files) <= 5:  # Show first 5
                                print(f"  {rel_path}")
            except:
                pass
    
    if not ontology_files:
        print("  No ontology JSON files found")

if __name__ == "__main__":
    simple_debug()
