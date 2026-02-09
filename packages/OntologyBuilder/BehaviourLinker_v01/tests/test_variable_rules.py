#!/usr/bin/env python3
"""
Test script for variable classification rules
"""

import sys
import os

# Add the packages directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Direct import since we're in the same directory
from variable_classification_rules import VariableClassificationRules

def test_physical_systems_rules():
    """Test rules for physical systems"""
    print("=== Testing Physical Systems Rules ===")
    
    # Test node entity type
    entity_type_info = {
        'network': 'macroscopic',
        'category': 'node',
        'entity type': 'energy_mass|dynamic|lumped'
    }
    
    rules = VariableClassificationRules.get_variable_rules(entity_type_info)
    print(f"Node rules: {rules}")
    
    # Test with sample variables
    sample_variables = [
        {'id': 'V_1', 'type': 'state', 'label': 'H'},
        {'id': 'V_2', 'type': 'effort', 'label': 'T'},
        {'id': 'V_3', 'type': 'transport', 'label': 'fq'},
        {'id': 'V_4', 'type': 'secondaryState', 'label': 'Cp'},
    ]
    
    classification = VariableClassificationRules.classify_variables(sample_variables, entity_type_info)
    print(f"Classification for node:")
    print(f"  Allowed root: {[v['label'] for v in classification['allowed_root']]}")
    print(f"  Inputs: {[v['label'] for v in classification['inputs']]}")
    print(f"  Outputs: {[v['label'] for v in classification['outputs']]}")
    
    # Test arc entity type
    entity_type_info_arc = {
        'network': 'macroscopic',
        'category': 'arc',
        'entity type': 'mass|convection|lumped'
    }
    
    rules_arc = VariableClassificationRules.get_variable_rules(entity_type_info_arc)
    print(f"\nArc rules: {rules_arc}")
    
    classification_arc = VariableClassificationRules.classify_variables(sample_variables, entity_type_info_arc)
    print(f"Classification for arc:")
    print(f"  Allowed root: {[v['label'] for v in classification_arc['allowed_root']]}")
    print(f"  Inputs: {[v['label'] for v in classification_arc['inputs']]}")
    print(f"  Outputs: {[v['label'] for v in classification_arc['outputs']]}")

def test_control_systems_rules():
    """Test rules for control systems"""
    print("\n=== Testing Control Systems Rules ===")
    
    entity_type_info = {
        'network': 'control',
        'category': 'signal',
        'entity type': 'signal|dynamic|ODE'
    }
    
    rules = VariableClassificationRules.get_variable_rules(entity_type_info)
    print(f"Control rules: {rules}")
    
    sample_variables = [
        {'id': 'V_1', 'type': 'signal', 'label': 'u'},
        {'id': 'V_2', 'type': 'signal', 'label': 'y'},
    ]
    
    classification = VariableClassificationRules.classify_variables(sample_variables, entity_type_info)
    print(f"Classification for control:")
    print(f"  Allowed root: {[v['label'] for v in classification['allowed_root']]}")
    print(f"  Inputs: {[v['label'] for v in classification['inputs']]}")
    print(f"  Outputs: {[v['label'] for v in classification['outputs']]}")

if __name__ == "__main__":
    test_physical_systems_rules()
    test_control_systems_rules()
    print("\n=== All Tests Completed ===")
