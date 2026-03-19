#!/usr/bin/env python3
"""
Simple Variable Access Rules - Clean and Maintainable

Just a nested dictionary mapping domains to accessible variable classes from other domains.
"""

from typing import Dict, List, Set
from Common.common_resources import CONNECTION_NETWORK_SEPARATOR


class SimpleVariableAccessRules:
    """
    Simple variable access rules using a clean nested dictionary approach.
    """
    
    def __init__(self, ontology_container):
        self.ontology_container = ontology_container
        self.networks = ontology_container.networks
        self.ontology_tree = ontology_container.ontology_tree
        
        # Simple nested dictionary: {domain: {source_domain: [variable_classes]}}
        self.access_rules = self._build_access_rules()
    
    def _build_access_rules(self) -> Dict[str, Dict[str, List[str]]]:
        """Build simple access rules dictionary"""
        rules = {}
        
        # Initialize all domains
        for domain in self.networks:
            rules[domain] = {}
        
        # Add cross-domain access based on interconnections
        interconnections = getattr(self.ontology_container, 'interconnection_nws_list', [])
        
        for inter_nw in interconnections:
            if CONNECTION_NETWORK_SEPARATOR in inter_nw:
                left_domain, right_domain = inter_nw.split(CONNECTION_NETWORK_SEPARATOR)
                
                # Get variable classes for each domain
                left_vars = self._get_domain_variable_classes(left_domain)
                right_vars = self._get_domain_variable_classes(right_domain)
                
                # Add cross-access rules
                self._add_cross_access(rules, left_domain, right_domain, left_vars, right_vars)
        
        # Add root network access for all
        if 'root' in self.networks:
            root_vars = self._get_domain_variable_classes('root')
            common_root_vars = [v for v in root_vars if v in ['constant', 'frame', 'network']]
            
            for domain in self.networks:
                if domain != 'root':
                    rules[domain]['root'] = common_root_vars
        
        return rules
    
    def _get_domain_variable_classes(self, domain: str) -> List[str]:
        """Get all variable classes for a domain"""
        try:
            # Get all variable classes from all components
            all_vars = set()
            for component in self.ontology_tree[domain]["behaviour"]:
                all_vars.update(self.ontology_tree[domain]["behaviour"][component])
            
            # Apply token restrictions
            if self.ontology_tree[domain]["structure"]["token"] == {}:
                # No tokens - remove state from nodes
                if 'node' in self.ontology_tree[domain]["behaviour"]:
                    if 'state' in all_vars:
                        all_vars.remove('state')
            
            return list(all_vars)
        except:
            return []
    
    def _add_cross_access(self, rules: Dict, left_domain: str, right_domain: str, 
                         left_vars: List[str], right_vars: List[str]):
        """Add cross-access rules between two domains"""
        # Define what each domain can access from the other
        access_matrix = {
            'physical': {
                'macroscopic': ['state', 'observation', 'algebraic'],
                'control': ['observation', 'secondaryState', 'algebraic']
            },
            'macroscopic': {
                'physical': ['effort', 'state'],
                'control': ['observation', 'secondaryState', 'algebraic']
            },
            'control': {
                'physical': ['effort', 'state'],
                'macroscopic': ['state', 'observation', 'algebraic']
            }
        }
        
        # Add access from left to right
        if left_domain in access_matrix and right_domain in access_matrix[left_domain]:
            allowed_vars = access_matrix[left_domain][right_domain]
            accessible = [v for v in right_vars if v in allowed_vars]
            if accessible:
                rules[left_domain][right_domain] = accessible
        
        # Add access from right to left
        if right_domain in access_matrix and left_domain in access_matrix[right_domain]:
            allowed_vars = access_matrix[right_domain][left_domain]
            accessible = [v for v in left_vars if v in allowed_vars]
            if accessible:
                rules[right_domain][left_domain] = accessible
    
    def get_accessible_variable_types(self, domain: str) -> Set[str]:
        """Get all accessible variable types for a domain"""
        accessible = set()
        
        # Add domain's own variables
        own_vars = self._get_domain_variable_classes(domain)
        accessible.update(own_vars)
        
        # Add cross-domain variables
        if domain in self.access_rules:
            for source_domain, var_types in self.access_rules[domain].items():
                accessible.update(var_types)
        
        return accessible
    
    def get_access_rules(self) -> Dict[str, Dict[str, List[str]]]:
        """Get the access rules dictionary"""
        return self.access_rules
    
    def print_rules(self):
        """Print the access rules in a readable format"""
        print("=== Variable Access Rules ===")
        for domain, sources in self.access_rules.items():
            if sources:
                print(f"\n{domain} can access from:")
                for source_domain, var_types in sources.items():
                    print(f"  {source_domain}: {var_types}")


# Simple integration function
def create_simple_variable_access_system(ontology_container):
    """Create simple variable access system"""
    rules = SimpleVariableAccessRules(ontology_container)
    
    # Create backward-compatible format
    variable_types_on_networks = {}
    for domain in rules.networks:
        variable_types_on_networks[domain] = list(rules.get_accessible_variable_types(domain))
    
    return variable_types_on_networks, rules
