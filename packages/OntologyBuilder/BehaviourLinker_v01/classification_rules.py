"""
Classification Rules Module
Handles all classification logic independently from the UI
"""

from PyQt5.QtWidgets import QMessageBox


class ClassificationRules:
    """
    Centralized classification rules that can be edited independently
    without affecting the main dialog code
    """
    
    def __init__(self):
        """Initialize classification rules"""
        self.rules = self._define_rules()
    
    def _define_rules(self):
        """
        Define all classification rules for different domain branches
        Edit this section to modify behavior without touching other code
        """
        return {
            # PHYSICAL BRANCH RULES
            'physical': {
                'list_inputs': {
                    'visible_buttons': ['none'],  # Only allow removing input
                    'allowed_combinations': [['none']],
                    'forbidden_combinations': [['input'], ['output'], ['instantiate']],
                    'description': 'Input variables - can only be removed'
                },
                'list_outputs': {
                    'visible_buttons': ['none'],  # Only allow removing from output
                    'allowed_combinations': [['none']],
                    'forbidden_combinations': [['input'], ['output'], ['instantiate']],
                    'description': 'Output variables - can only be removed'
                },
                'list_instantiate': {
                    'visible_buttons': ['instantiate', 'input', 'none'],
                    'allowed_combinations': [
                        ['instantiate'],  # Keep as instantiate only
                        ['instantiate', 'input'],  # Add input to instantiate
                        ['none']  # Remove all classifications
                    ],
                    'forbidden_combinations': [['output']],
                    'description': 'Instantiate variables - can add input or remove all'
                },
                'list_not_defined_variables': {
                    'visible_buttons': ['input', 'instantiate', 'none'],
                    'allowed_combinations': [
                        ['input'],        # Move to inputs
                        ['instantiate'],   # Move to instantiate
                        ['none']           # Keep as pending
                    ],
                    'forbidden_combinations': [['output']],
                    'description': 'Pending variables - can move to input or instantiate'
                },
                'list_equations': {
                    'visible_buttons': ['none'],
                    'allowed_combinations': [['none']],
                    'forbidden_combinations': [['input'], ['output'], ['instantiate']],
                    'description': 'Equation variables - cannot be classified elsewhere'
                }
            },
            
            # CONTROL BRANCH RULES
            'control': {
                'list_inputs': {
                    'visible_buttons': ['input', 'none'],
                    'allowed_combinations': [['input'], ['none']],
                    'forbidden_combinations': [['output'], ['instantiate']],
                    'description': 'Control inputs - signals flowing into system'
                },
                'list_outputs': {
                    'visible_buttons': ['output', 'none'],
                    'allowed_combinations': [['output'], ['none']],
                    'forbidden_combinations': [['input'], ['instantiate']],
                    'description': 'Control outputs - signals flowing out of system'
                },
                'list_instantiate': {
                    'visible_buttons': ['instantiate', 'none'],
                    'allowed_combinations': [['instantiate'], ['none']],
                    'forbidden_combinations': [['input'], ['output']],
                    'description': 'Control instantiate - parameters and initial states'
                },
                'list_not_defined_variables': {
                    'visible_buttons': ['input', 'output', 'instantiate', 'none'],
                    'allowed_combinations': [
                        ['input'], ['output'], ['instantiate'], ['none']
                    ],
                    'forbidden_combinations': [
                        ['input', 'output'], ['input', 'instantiate'],
                        ['output', 'instantiate'], ['input', 'output', 'instantiate']
                    ],
                    'description': 'Control pending - can classify as input, output, or instantiate'
                },
                'list_equations': {
                    'visible_buttons': ['none'],
                    'allowed_combinations': [['none']],
                    'forbidden_combinations': [['input'], ['output'], ['instantiate']],
                    'description': 'Control equations - cannot be classified elsewhere'
                }
            },
            
            # INFO_PROCESSING BRANCH RULES
            'info_processing': {
                'list_inputs': {
                    'visible_buttons': ['input', 'none'],
                    'allowed_combinations': [['input'], ['none']],
                    'forbidden_combinations': [['output'], ['instantiate']],
                    'description': 'Info processing inputs - data flowing into system'
                },
                'list_outputs': {
                    'visible_buttons': ['output', 'none'],
                    'allowed_combinations': [['output'], ['none']],
                    'forbidden_combinations': [['input'], ['instantiate']],
                    'description': 'Info processing outputs - data flowing out of system'
                },
                'list_instantiate': {
                    'visible_buttons': ['instantiate', 'none'],
                    'allowed_combinations': [['instantiate'], ['none']],
                    'forbidden_combinations': [['input'], ['output']],
                    'description': 'Info processing instantiate - parameters and constants'
                },
                'list_not_defined_variables': {
                    'visible_buttons': ['input', 'output', 'instantiate', 'none'],
                    'allowed_combinations': [
                        ['input'], ['output'], ['instantiate'], ['none']
                    ],
                    'forbidden_combinations': [
                        ['input', 'output'], ['input', 'instantiate'],
                        ['output', 'instantiate'], ['input', 'output', 'instantiate']
                    ],
                    'description': 'Info processing pending - can classify as input, output, or instantiate'
                },
                'list_equations': {
                    'visible_buttons': ['none'],
                    'allowed_combinations': [['none']],
                    'forbidden_combinations': [['input'], ['output'], ['instantiate']],
                    'description': 'Info processing equations - cannot be classified elsewhere'
                }
            },
            
            # REACTION BRANCH RULES
            'reaction': {
                'list_inputs': {
                    'visible_buttons': ['input', 'none'],
                    'allowed_combinations': [['input'], ['none']],
                    'forbidden_combinations': [['output'], ['instantiate']],
                    'description': 'Reaction inputs - reactants and conditions'
                },
                'list_outputs': {
                    'visible_buttons': ['output', 'none'],
                    'allowed_combinations': [['output'], ['none']],
                    'forbidden_combinations': [['input'], ['instantiate']],
                    'description': 'Reaction outputs - products and results'
                },
                'list_instantiate': {
                    'visible_buttons': ['instantiate', 'none'],
                    'allowed_combinations': [['instantiate'], ['none']],
                    'forbidden_combinations': [['input'], ['output']],
                    'description': 'Reaction instantiate - reaction parameters and rates'
                },
                'list_not_defined_variables': {
                    'visible_buttons': ['input', 'output', 'instantiate', 'none'],
                    'allowed_combinations': [
                        ['input'], ['output'], ['instantiate'], ['none']
                    ],
                    'forbidden_combinations': [
                        ['input', 'output'], ['input', 'instantiate'],
                        ['output', 'instantiate'], ['input', 'output', 'instantiate']
                    ],
                    'description': 'Reaction pending - can classify as input, output, or instantiate'
                },
                'list_equations': {
                    'visible_buttons': ['none'],
                    'allowed_combinations': [['none']],
                    'forbidden_combinations': [['input'], ['output'], ['instantiate']],
                    'description': 'Reaction equations - cannot be classified elsewhere'
                }
            }
        }
    
    def get_visible_buttons(self, list_name, var_info=None, domain='physical'):
        """
        Get which radio buttons should be visible for a given list and domain
        
        Args:
            list_name (str): Name of the list (e.g., 'list_inputs')
            var_info (dict): Variable information (for future enhancements)
            domain (str): Domain branch (physical, control, info_processing, reaction)
        
        Returns:
            list: List of button names that should be visible
        """
        domain_rules = self.rules.get(domain, self.rules['physical'])
        list_rules = domain_rules.get(list_name, domain_rules['list_inputs'])
        return list_rules['visible_buttons']
    
    def validate_selection(self, list_name, selections, parent_widget=None, domain='physical'):
        """
        Validate a selection according to the domain-specific rules
        
        Args:
            list_name (str): Name of the list
            selections (list): List of selected button names
            parent_widget: Parent widget for showing messages
            domain (str): Domain branch (physical, control, info_processing, reaction)
        
        Returns:
            tuple: (is_valid, validated_selections, error_message)
        """
        domain_rules = self.rules.get(domain, self.rules['physical'])
        list_rules = domain_rules.get(list_name, domain_rules['list_inputs'])
        
        # Rule: "none" clears everything
        if not selections or 'none' in selections:
            return True, ['none'], None
        
        # Check forbidden combinations
        for forbidden in list_rules['forbidden_combinations']:
            if all(item in selections for item in forbidden):
                error_msg = f"Invalid combination: {', '.join(forbidden)}. {list_rules['description']}"
                if parent_widget:
                    QMessageBox.warning(parent_widget, "Invalid Classification", error_msg)
                return False, None, error_msg
        
        # Check if combination is allowed
        for allowed in list_rules['allowed_combinations']:
            if all(item in selections for item in allowed) and len(selections) == len(allowed):
                return True, selections, None
        
        # Check if it's a partial allowed combination (for multi-select)
        if domain == 'physical' and list_name in ['list_instantiate']:
            # Allow partial selections for physical instantiate list
            valid_items = []
            for item in selections:
                if item in ['instantiate', 'input']:
                    valid_items.append(item)
                else:
                    error_msg = f"Invalid selection '{item}' for {list_name}. {list_rules['description']}"
                    if parent_widget:
                        QMessageBox.warning(parent_widget, "Invalid Classification", error_msg)
                    return False, None, error_msg
            
            if valid_items:
                return True, valid_items, None
        
        # Default: not allowed
        error_msg = f"Selection not allowed: {', '.join(selections)}. {list_rules['description']}"
        if parent_widget:
            QMessageBox.warning(parent_widget, "Invalid Classification", error_msg)
        return False, None, error_msg
    
    def get_button_visibility_config(self, list_name, var_info=None, domain='physical'):
        """
        Get complete visibility configuration for the dialog
        
        Args:
            list_name (str): Name of the list
            var_info (dict): Variable information
            domain (str): Domain branch (physical, control, info_processing, reaction)
        
        Returns:
            dict: Configuration for button visibility
        """
        visible_buttons = self.get_visible_buttons(list_name, var_info, domain)
        
        return {
            'select_input': 'input' in visible_buttons,
            'select_output': 'output' in visible_buttons,
            'radioButton': 'instantiate' in visible_buttons,  # instantiate button
            'select_none': 'none' in visible_buttons,
            'description': self.rules.get(domain, {}).get(list_name, {}).get('description', ''),
            'allow_multiple': domain == 'physical' and list_name in ['list_instantiate']
        }
    
    def apply_classification_to_entity(self, entity, var_id, validated_selections):
        """
        Apply validated classifications to the entity
        
        Args:
            entity: The entity object
            var_id (str): Variable ID
            validated_selections (list): Validated classification selections
        """
        if hasattr(entity, 'change_classification'):
            entity.change_classification(var_id, validated_selections)
        else:
            # Fallback for older entity versions
            manual_classifications = getattr(entity, 'local_variable_classifications', {})
            if var_id not in manual_classifications:
                manual_classifications[var_id] = {}
            manual_classifications[var_id]['classification'] = validated_selections


# === CONVENIENCE FUNCTIONS ===

def get_classification_rules():
    """Get a fresh instance of classification rules"""
    return ClassificationRules()

def setup_dialog_with_rules(ui, list_name, var_info=None, current_classifications=None, domain='physical'):
    """
    Setup dialog UI according to classification rules
    
    Args:
        ui: Dialog UI object
        list_name (str): Name of the current list
        var_info (dict): Variable information
        current_classifications (list): Current classifications
        domain (str): Domain branch (physical, control, info_processing, reaction)
    """
    rules = get_classification_rules()
    config = rules.get_button_visibility_config(list_name, var_info, domain)
    
    # Show/hide buttons based on rules
    ui.select_input.setVisible(config['select_input'])
    ui.select_output.setVisible(config['select_output'])
    ui.radioButton.setVisible(config['radioButton'])
    ui.select_none.setVisible(config['select_none'])
    
    # Set button group exclusivity based on whether multiple selections are allowed
    ui.buttonGroup.setExclusive(not config['allow_multiple'])
    
    # Set current selection
    if current_classifications:
        if 'input' in current_classifications and config['select_input']:
            ui.select_input.setChecked(True)
        if 'output' in current_classifications and config['select_output']:
            ui.select_output.setChecked(True)
        if 'instantiate' in current_classifications and config['radioButton']:
            ui.radioButton.setChecked(True)
        if 'none' in current_classifications and config['select_none']:
            ui.select_none.setChecked(True)
    else:
        # If no current classifications and button group is exclusive, set a default
        if not config['allow_multiple'] and config['select_none']:
            ui.select_none.setChecked(True)
    
    return config

def validate_and_apply_classification(ui, list_name, var_id, entity, parent_widget=None, domain='physical'):
    """
    Validate and apply classification using rules
    
    Args:
        ui: Dialog UI object
        list_name (str): Name of the current list
        var_id (str): Variable ID
        entity: The entity object
        parent_widget: Parent widget for messages
        domain (str): Domain branch (physical, control, info_processing, reaction)
    
    Returns:
        bool: True if classification was applied successfully
    """
    rules = get_classification_rules()
    
    # Collect selections
    selections = []
    if ui.select_input.isChecked() and ui.select_input.isVisible():
        selections.append('input')
    if ui.select_output.isChecked() and ui.select_output.isVisible():
        selections.append('output')
    if ui.radioButton.isChecked() and ui.radioButton.isVisible():
        selections.append('instantiate')
    if ui.select_none.isChecked() and ui.select_none.isVisible():
        selections.append('none')
    
    # Validate selections
    is_valid, validated_selections, error_msg = rules.validate_selection(
        list_name, selections, parent_widget, domain
    )
    
    if is_valid and validated_selections:
        # Apply to entity
        rules.apply_classification_to_entity(entity, var_id, validated_selections)
        return True
    
    return False
