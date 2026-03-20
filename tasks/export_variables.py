#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
Standalone script to export all variables to a text file in definition order
===============================================================================

This script loads the ontology data and exports all variables to a text file
ordered by their variable IDs (V_1, V_2, V_3, etc.).

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

# Get the correct path to the project root
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.extend([project_root, os.path.join(project_root, 'packages'), os.path.join(project_root, 'tasks')])

# Add the ProMo directory to path for constants module
sys.path.append(project_root)

from OntologyBuilder.EquationEditor_v01.ui_ontology_design_impl import UiOntologyDesign
from OntologyBuilder.EquationEditor_v01.ontology import Ontology

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
    Main function to load ontology data and export variables
    """
    try:
        # Initialize ontology container (similar to UiOntologyDesign)
        print("Loading ontology data...")
        
        # Use the demo database file
        ontology_location = "packages/OntologyBuilder/EquationEditor_v01/demo"
        
        # Create ontology container
        ontology_container = Ontology(ontology_location)
        
        # Create variables object
        from OntologyBuilder.EquationEditor_v01.variable_framework import Variables
        variables = Variables(ontology_container)
        
        # Import variables
        variables.importVariables(ontology_container.variables, ontology_container.indices)
        
        print(f"Loaded {len(variables)} variables from ontology")
        
        # Export variables to file
        output_file = "variables_definition_order.txt"
        success = write_variables_to_file(variables, output_file)
        
        if success:
            print(f"Variables successfully exported to {output_file}")
        else:
            print("Failed to export variables")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
