"""
Rule-based system for classifying variables as inputs/outputs based on entity types and networks.
"""


class VariableClassificationRules:
    """Rule engine for determining variable input/output classification"""

    @staticmethod
    def get_variable_rules(entity_type_info):
        """
        Get variable classification rules based on entity type information
        
        Args:
            entity_type_info (dict): Dictionary containing network, category, entity_type
            
        Returns:
            dict: Rules for variable classification with keys:
                - 'allowed_root_types': List of variable types that can be root
                - 'input_types': List of variable types that should be inputs
                - 'output_types': List of variable types that should be outputs
        """
        network = entity_type_info.get('network', 'unknown')
        category = entity_type_info.get('category', 'unknown')
        entity_type = entity_type_info.get('entity_type', 'unknown')

        # Physical systems rules
        if network == 'physical' or network == 'macroscopic' or network == 'microscopic':
            return VariableClassificationRules._get_physical_systems_rules(category)

        # Control systems rules
        elif network == 'control':
            return VariableClassificationRules._get_control_systems_rules(category)

        # Info processing rules
        elif network == 'info_processing':
            return VariableClassificationRules._get_info_processing_rules(category)

        # Reactions rules
        elif network == 'reactions':
            return VariableClassificationRules._get_reactions_rules(category)

        # Default rules
        else:
            return VariableClassificationRules._get_default_rules()

    @staticmethod
    def _get_physical_systems_rules(category):
        """Rules for physical systems"""
        rules = {
                'allowed_root_types': ['state'],  # Only state variables can be root
                'input_types'       : ['transport'],  # Token flows are inputs
                'output_types'      : ['state', 'effort', 'secondaryState']  # State and secondary variables are outputs
                }

        # Node-specific rules
        if category == 'node':
            rules['output_types'].extend(['effort'])  # Nodes have effort variables as outputs

        # Arc-specific rules  
        elif category == 'arc':
            rules['input_types'] = ['effort']  # Arcs have effort variables as inputs
            rules['output_types'] = ['transport']  # Arcs have transport variables as outputs

        return rules

    @staticmethod
    def _get_control_systems_rules(category):
        """Rules for control systems"""
        return {
                'allowed_root_types': ['signal'],
                'input_types'       : ['signal'],
                'output_types'      : ['signal']
                }

    @staticmethod
    def _get_info_processing_rules(category):
        """Rules for info processing systems"""
        return {
                'allowed_root_types': ['signal'],
                'input_types'       : ['signal'],
                'output_types'      : ['signal']
                }

    @staticmethod
    def _get_reactions_rules(category):
        """Rules for reaction systems"""
        return {
                'allowed_root_types': ['state', 'conversion'],
                'input_types'       : ['conversion'],
                'output_types'      : ['state', 'conversion']
                }

    @staticmethod
    def _get_default_rules():
        """Default rules for unknown systems"""
        return {
                'allowed_root_types': ['state'],
                'input_types'       : ['transport'],
                'output_types'      : ['state', 'effort']
                }

    @staticmethod
    def filter_variables_by_type(variables, allowed_types):
        """
        Filter variables by their types
        
        Args:
            variables (list): List of variable dictionaries
            allowed_types (list): List of allowed variable types
            
        Returns:
            list: Filtered variables
        """
        filtered = []
        for var in variables:
            if var.get('type') in allowed_types:
                filtered.append(var)
        return filtered

    @staticmethod
    def classify_variables(variables, entity_type_info):
        """
        Classify variables as inputs/outputs based on rules
        
        Args:
            variables (list): List of variable dictionaries
            entity_type_info (dict): Entity type information
            
        Returns:
            dict: Classification with keys 'inputs', 'outputs', 'allowed_root'
        """
        rules = VariableClassificationRules.get_variable_rules(entity_type_info)

        classification = {
                'inputs'      : VariableClassificationRules.filter_variables_by_type(variables, rules['input_types']),
                'outputs'     : VariableClassificationRules.filter_variables_by_type(variables, rules['output_types']),
                'allowed_root': VariableClassificationRules.filter_variables_by_type(variables, rules['allowed_root_types'])
                }

        return classification
