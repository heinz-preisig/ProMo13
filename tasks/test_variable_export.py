#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
Test script to demonstrate variable export functionality
===============================================================================

This script creates sample variables and exports them to a text file
to demonstrate the variable ordering functionality.
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

class MockVariable:
    """Mock variable class for testing"""
    def __init__(self, var_id, label, var_type, network, doc=""):
        self.label = label
        self.type = var_type
        self.network = network
        self.doc = doc
        self.units = "kg/s"  # Mock units
        self.equations = {}  # Mock equations dictionary

def write_variables_to_file(variables, output_filename="variables_list.txt"):
    """
    Write all variables to a text file in order of their definition (V_1, V_2, V_3, etc.)
    
    :param variables: Variables object (OrderedDict) containing all variables
    :param output_filename: Name of the output file
    """
    try:
        # Get all variable IDs and sort them numerically
        variable_ids = []
        for var_id in variables.keys():
            # Extract the numeric part from V_N format
            if var_id.startswith("V_"):
                try:
                    num = int(var_id[2:])
                    variable_ids.append((num, var_id))
                except ValueError:
                    # Handle cases where the suffix might not be a simple number
                    variable_ids.append((float('inf'), var_id))
        
        # Sort by the numeric part
        variable_ids.sort()
        
        # Write to file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("List of Variables in Definition Order\n")
            f.write("=" * 50 + "\n\n")
            
            for num, var_id in variable_ids:
                var = variables[var_id]
                f.write(f"Variable ID: {var_id}\n")
                f.write(f"  Label: {var.label}\n")
                f.write(f"  Type: {var.type}\n")
                f.write(f"  Network: {var.network}\n")
                f.write(f"  Documentation: {var.doc}\n")
                
                # Write units if available
                if hasattr(var, 'units') and var.units:
                    f.write(f"  Units: {var.units}\n")
                
                # Write equations if available
                if hasattr(var, 'equations') and var.equations:
                    f.write(f"  Equations: {list(var.equations.keys())}\n")
                
                f.write("\n")
        
        print(f"Successfully wrote {len(variable_ids)} variables to {output_filename}")
        return True
        
    except Exception as e:
        print(f"Error writing variables to file: {e}")
        return False

def main():
    """
    Create sample variables and test the export functionality
    """
    try:
        print("Creating sample variables for testing...")
        
        # Create a mock Variables OrderedDict
        variables = OrderedDict()
        
        # Add sample variables in random order to test sorting
        variables["V_5"] = MockVariable("V_5", "FlowRate", "state", "physical", "Mass flow rate through the system")
        variables["V_1"] = MockVariable("V_1", "Temperature", "state", "physical", "System temperature")
        variables["V_3"] = MockVariable("V_3", "Pressure", "algebraic", "physical", "System pressure")
        variables["V_2"] = MockVariable("V_2", "Concentration", "state", "physical", "Chemical concentration")
        variables["V_4"] = MockVariable("V_4", "Volume", "algebraic", "physical", "System volume")
        
        print(f"Created {len(variables)} sample variables")
        
        # Export variables to file
        output_file = "sample_variables_definition_order.txt"
        success = write_variables_to_file(variables, output_file)
        
        if success:
            print(f"Sample variables successfully exported to {output_file}")
            print("\nTo use with real data:")
            print("1. Load your actual ontology data using the EquationComposer GUI")
            print("2. Use the 'Export Variables to Text File' menu option")
            print("3. Or run the export script with proper dependencies installed")
        else:
            print("Failed to export variables")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
