"""
Simple variable domain validation system.
Ensures only one variable with a given name exists in a given domain.
"""

class VariableDomainValidator:
    """Validates variable uniqueness within domains"""
    
    @staticmethod
    def is_variable_name_unique_in_domain(variable_name, domain, ontology_container, exclude_var_id=None):
        """
        Check if a variable name is unique within a domain.
        
        Args:
            variable_name (str): The variable name to check
            domain (str): The domain (network) to check in
            ontology_container: The ontology container with variables
            exclude_var_id (str, optional): Variable ID to exclude from check (for edits)
            
        Returns:
            bool: True if name is unique, False if duplicate exists
            str: ID of the duplicate variable if found, None otherwise
        """
        if not hasattr(ontology_container, 'variables'):
            return True, None
            
        variables = ontology_container.variables
        
        for var_id, var_data in variables.items():
            # Skip the variable we're excluding (for edit operations)
            if exclude_var_id and var_id == exclude_var_id:
                continue
                
            # Check if variable is in the same domain and has the same name
            if (var_data.get('network') == domain and 
                var_data.get('label') == variable_name):
                return False, var_id
                
        return True, None
    
    @staticmethod
    def validate_variable_name(variable_name, domain, ontology_container, exclude_var_id=None):
        """
        Validate a variable name and return appropriate error message if invalid.
        
        Args:
            variable_name (str): The variable name to validate
            domain (str): The domain (network) 
            ontology_container: The ontology container with variables
            exclude_var_id (str, optional): Variable ID to exclude from check
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not variable_name or not variable_name.strip():
            return False, "Variable name cannot be empty"
            
        variable_name = variable_name.strip()
        
        # Check uniqueness within domain
        is_unique, duplicate_id = VariableDomainValidator.is_variable_name_unique_in_domain(
            variable_name, domain, ontology_container, exclude_var_id
        )
        
        if not is_unique:
            return False, f"Variable name '{variable_name}' already exists in domain '{domain}' (Variable ID: {duplicate_id})"
            
        return True, None
