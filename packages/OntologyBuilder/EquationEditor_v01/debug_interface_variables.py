#!/usr/local/bin/python3
# encoding: utf-8

"""
Debug script to check what's actually in the interface domain
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def debug_interface_variables():
    """Debug what's in the interface domain"""
    try:
        from OntologyBuilder.EquationEditor_v01.variable_framework import Variables
        from Common.common_resources import VARIABLE_TYPE_INTERFACES
        
        # Create a minimal variables object
        variables = Variables()
        
        # Check if interface domain exists
        if hasattr(variables, 'interface_domain') and variables.interface_domain:
            print(f"Interface domain: {variables.interface_domain}")
            print(f"VARIABLE_TYPE_INTERFACES: {VARIABLE_TYPE_INTERFACES}")
            
            # Show ALL variables in interface domain
            print("\nAll variables in interface domain:")
            for var_ID in variables:
                var = variables[var_ID]
                if var.network == variables.interface_domain:
                    print(f"  ID: {var_ID}")
                    print(f"  Label: {var.label}")
                    print(f"  Type: {var.type}")
                    print(f"  Network: {var.network}")
                    print(f"  Doc: {var.doc}")
                    print(f"  Equations: {list(var.equations.keys())}")
                    print()
            
            # Show only interface type variables
            print("\nOnly 'get' type variables in interface domain:")
            for var_ID in variables:
                var = variables[var_ID]
                if var.network == variables.interface_domain and var.type == "get":
                    print(f"  ID: {var_ID}")
                    print(f"  Label: {var.label}")
                    print(f"  Type: {var.type}")
                    print(f"  Network: {var.network}")
                    print(f"  Doc: {var.doc}")
                    print(f"  Equations: {list(var.equations.keys())}")
                    print()
        else:
            print("No interface domain found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_interface_variables()
