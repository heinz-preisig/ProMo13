#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Test script for equation selection workflow
===============================================================================

This script tests the equation selection functionality independently.
"""

import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal

# Add the path to the behavior association module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from behavior_association.equation_selector import EquationSelectorDialog


class MockOntologyContainer:
    """Mock ontology container for testing"""
    def __init__(self):
        self.ontology_name = "test_ontology"
        # Mock equation dictionary with PNG file paths
        self.equation_dictionary = {
            'eq_1': {
                'label': 'Mass Balance',
                'expression': 'd/dt(V) = F_in - F_out',
                'description': 'Mass balance for the reactor volume',
                'png_file': '/tmp/test_eq_1.png'  # Mock PNG path
            },
            'eq_2': {
                'label': 'Energy Balance', 
                'expression': 'd/dt(T) = (F_in*T_in - F_out*T)/V + Q/(V*rho*Cp)',
                'description': 'Energy balance for reactor temperature',
                'png_file': None  # No PNG available
            }
        }


def test_equation_selector():
    """Test the equation selector dialog"""
    
    # Create sample variable data with equations (minimal - PNG files come from ontology container)
    variable_data = {
        'id': 'test_var_1',
        'label': 'Test Variable',
        'type': 'state',
        'network': 'test_network',
        'equations': {
            'eq_1': {},  # Minimal data - full data comes from ontology container
            'eq_2': {}
        }
    }
    
    # Create mock ontology container
    ontology_container = MockOntologyContainer()
    
    # Create QApplication
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    # Create and show the dialog
    dialog = EquationSelectorDialog(variable_data, ontology_container)
    
    print("Testing Equation Selector Dialog")
    print("================================")
    print("1. Dialog should show with variable info")
    print("2. Two definition methods: Equation and Initialization")
    print("3. Equation list should show 2 equations")
    print("4. Equation data (including PNG files) comes from ontology container")
    print("5. Select equation or initialization method")
    print("6. Click OK to see results")
    
    # Show dialog and get result
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        result = dialog.get_selection()
        print("\nSelection Result:")
        print(f"  Equation ID: {result['equation_id']}")
        print(f"  Use Initialization: {result['use_initialization']}")
        print(f"  Initialization Value: {result['initialization_value']}")
    else:
        print("\nDialog cancelled")
    
    print("\nTest completed!")


def test_variable_without_equations():
    """Test equation selector with variable that has no equations"""
    
    variable_data = {
        'id': 'test_var_2',
        'label': 'Input Variable',
        'type': 'input',
        'network': 'test_network',
        'equations': {}  # No equations available
    }
    
    ontology_container = MockOntologyContainer()
    
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    dialog = EquationSelectorDialog(variable_data, ontology_container)
    
    print("\n\nTesting Variable Without Equations")
    print("==================================")
    print("1. Dialog should show with variable info")
    print("2. Equation option should be disabled")
    print("3. Initialization should be automatically selected")
    print("4. User must enter an initialization value")
    
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        result = dialog.get_selection()
        print("\nSelection Result:")
        print(f"  Equation ID: {result['equation_id']}")
        print(f"  Use Initialization: {result['use_initialization']}")
        print(f"  Initialization Value: {result['initialization_value']}")
    else:
        print("\nDialog cancelled")


if __name__ == "__main__":
    print("Equation Selection Test Suite")
    print("=============================")
    
    try:
        # Test with variable that has equations
        test_equation_selector()
        
        # Test with variable that has no equations
        test_variable_without_equations()
        
        print("\n\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    sys.exit(0)
