#!/usr/local/bin/python3
# encoding: utf-8

"""
Enhanced arc connection logic for the modeller
Uses physical domain information including effort variables and tokens
"""

from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict


class EnhancedArcConnectionValidator:
    """
    Enhanced validator for arc connections using physical domain information
    """
    
    def __init__(self, enhanced_arc_options: Dict[str, Dict[str, any]]):
        """
        Initialize with enhanced arc options
        
        Args:
            enhanced_arc_options: Arc options with physical domain information
        """
        self.arc_options = enhanced_arc_options
        self.token_to_arcs = self._build_token_index()
        self.effort_to_arcs = self._build_effort_index()
    
    def _build_token_index(self) -> Dict[str, List[str]]:
        """Build index of arcs by token type"""
        token_index = defaultdict(list)
        for arc_name, arc_data in self.arc_options.items():
            physical_domain = arc_data.get("physical_domain")
            if physical_domain:
                token = physical_domain.get("token")
                if token:
                    token_index[token].append(arc_name)
        return dict(token_index)
    
    def _build_effort_index(self) -> Dict[str, List[str]]:
        """Build index of arcs by effort variable"""
        effort_index = defaultdict(list)
        for arc_name, arc_data in self.arc_options.items():
            physical_domain = arc_data.get("physical_domain")
            if physical_domain:
                effort = physical_domain.get("effort_variable")
                if effort:
                    effort_index[effort].append(arc_name)
        return dict(effort_index)
    
    def get_compatible_arcs_for_nodes(self, source_node_id: str, sink_node_id: str, 
                                    model_container: Dict[str, any]) -> List[str]:
        """
        Get list of compatible arcs for connecting two nodes
        
        Args:
            source_node_id: ID of source node
            sink_node_id: ID of sink node
            model_container: Model data container
            
        Returns:
            List of compatible arc names
        """
        source_node = model_container["nodes"][source_node_id]
        sink_node = model_container["nodes"][sink_node_id]
        
        source_entity_id = source_node["entity_id"]
        sink_entity_id = sink_node["entity_id"]
        
        compatible_arcs = []
        
        for arc_name, arc_data in self.arc_options.items():
            # Check basic compatibility
            if (source_entity_id in arc_data.get("sources", []) and 
                sink_entity_id in arc_data.get("sinks", [])):
                
                # Add physical domain compatibility check
                if self._check_physical_domain_compatibility(arc_name, source_node, sink_node):
                    compatible_arcs.append(arc_name)
        
        return compatible_arcs
    
    def _check_physical_domain_compatibility(self, arc_name: str, source_node: Dict, 
                                            sink_node: Dict) -> bool:
        """
        Check physical domain compatibility between nodes and arc
        
        Args:
            arc_name: Name of the arc
            source_node: Source node data
            sink_node: Sink node data
            
        Returns:
            True if compatible, False otherwise
        """
        physical_domain = self.arc_options[arc_name].get("physical_domain")
        
        if not physical_domain:
            return True  # Non-physical arcs are always compatible
        
        # Check token compatibility
        token = physical_domain.get("token")
        if token:
            # Nodes should have the token in their entity IDs
            if (token not in source_node["entity_id"] or 
                token not in sink_node["entity_id"]):
                return False
        
        return True
    
    def get_arc_physical_info(self, arc_name: str) -> Optional[Dict[str, str]]:
        """
        Get physical domain information for an arc
        
        Args:
            arc_name: Name of the arc
            
        Returns:
            Physical domain information or None if not available
        """
        return self.arc_options.get(arc_name, {}).get("physical_domain")
    
    def validate_connection_with_effort_variables(self, source_node_id: str, sink_node_id: str,
                                               arc_name: str, model_container: Dict[str, any]) -> List[str]:
        """
        Validate connection using effort variable information
        
        Args:
            source_node_id: ID of source node
            sink_node_id: ID of sink node  
            arc_name: Name of the arc
            model_container: Model data container
            
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        physical_info = self.get_arc_physical_info(arc_name)
        if not physical_info:
            return warnings  # No physical domain to validate
        
        # Check if source node has the required effort variable as output
        effort_variable = physical_info.get("effort_variable")
        if effort_variable:
            source_node = model_container["nodes"][source_node_id]
            # This would need to be implemented based on how variables are stored in nodes
            # For now, we'll assume the check passes if the node is in the physical domain
            if "physical" not in source_node.get("network", ""):
                warnings.append(f"Source node may not provide effort variable '{effort_variable}'")
        
        return warnings
    
    def get_arcs_by_token(self, token: str) -> List[str]:
        """Get all arcs that transport a specific token"""
        return self.token_to_arcs.get(token, [])
    
    def get_arcs_by_effort_variable(self, effort_variable: str) -> List[str]:
        """Get all arcs driven by a specific effort variable"""
        return self.effort_to_arcs.get(effort_variable, [])
    
    def suggest_connections_for_token(self, token: str, model_container: Dict[str, any]) -> List[Tuple[str, str, str]]:
        """
        Suggest possible connections for a specific token
        
        Args:
            token: Token type (mass, energy, charge, etc.)
            model_container: Model data container
            
        Returns:
            List of tuples (source_node_id, sink_node_id, arc_name)
        """
        suggestions = []
        token_arcs = self.get_arcs_by_token(token)
        
        for arc_name in token_arcs:
            arc_data = self.arc_options[arc_name]
            sources = arc_data.get("sources", [])
            sinks = arc_data.get("sinks", [])
            
            # Find matching nodes in the model
            for node_id, node_data in model_container["nodes"].items():
                entity_id = node_data["entity_id"]
                
                if entity_id in sources:
                    # Find compatible sinks
                    for sink_id, sink_data in model_container["nodes"].items():
                        if sink_data["entity_id"] in sinks:
                            suggestions.append((node_id, sink_id, arc_name))
        
        return suggestions


class EnhancedArcConnectionRules:
    """
    Enhanced rules for arc connections in the modeller
    """
    
    def __init__(self, connection_validator: EnhancedArcConnectionValidator):
        self.validator = connection_validator
    
    def apply_enhanced_connection_rules(self, source_node_id: str, model_container: Dict[str, any]) -> Dict[str, any]:
        """
        Apply enhanced connection rules when starting an arc from a node
        
        Args:
            source_node_id: ID of the source node
            model_container: Model data container
            
        Returns:
            Dictionary with connection rules and feasible targets
        """
        source_node = model_container["nodes"][source_node_id]
        source_entity_id = source_node["entity_id"]
        
        # Find all arcs that can start from this node
        feasible_arcs = []
        for arc_name, arc_data in self.validator.arc_options.items():
            if source_entity_id in arc_data.get("sources", []):
                feasible_arcs.append(arc_name)
        
        # Group arcs by physical domain information
        arcs_by_token = defaultdict(list)
        arcs_by_effort = defaultdict(list)
        
        for arc_name in feasible_arcs:
            physical_info = self.validator.get_arc_physical_info(arc_name)
            if physical_info:
                token = physical_info.get("token")
                effort = physical_info.get("effort_variable")
                if token:
                    arcs_by_token[token].append(arc_name)
                if effort:
                    arcs_by_effort[effort].append(arc_name)
        
        # Determine feasible sink nodes
        feasible_sink_variants = set()
        for arc_name in feasible_arcs:
            feasible_sink_variants.update(self.validator.arc_options[arc_name].get("sinks", []))
        
        return {
            "feasible_arcs": feasible_arcs,
            "feasible_sink_variants": list(feasible_sink_variants),
            "arcs_by_token": dict(arcs_by_token),
            "arcs_by_effort": dict(arcs_by_effort),
            "physical_domains": {
                arc_name: self.validator.get_arc_physical_info(arc_name) 
                for arc_name in feasible_arcs
            }
        }
    
    def validate_proposed_connection(self, source_node_id: str, sink_node_id: str, 
                                   arc_name: str, model_container: Dict[str, any]) -> Dict[str, any]:
        """
        Validate a proposed connection with enhanced rules
        
        Args:
            source_node_id: ID of source node
            sink_node_id: ID of sink node
            arc_name: Name of the arc
            model_container: Model data container
            
        Returns:
            Validation result with warnings/errors
        """
        result = {
            "valid": False,
            "warnings": [],
            "errors": [],
            "physical_info": None
        }
        
        # Basic compatibility check
        compatible_arcs = self.validator.get_compatible_arcs_for_nodes(
            source_node_id, sink_node_id, model_container
        )
        
        if arc_name not in compatible_arcs:
            result["errors"].append(f"Arc '{arc_name}' is not compatible between these nodes")
            return result
        
        result["valid"] = True
        result["physical_info"] = self.validator.get_arc_physical_info(arc_name)
        
        # Enhanced validation with effort variables
        effort_warnings = self.validator.validate_connection_with_effort_variables(
            source_node_id, sink_node_id, arc_name, model_container
        )
        result["warnings"].extend(effort_warnings)
        
        return result


if __name__ == "__main__":
    # Example usage
    enhanced_options = {
        "macroscopic.arc.mass|convection|lumped.convectiveMassFlow": {
            "sources": ["macroscopic.node.mass|dynamic|lumped.dynamicMass"],
            "sinks": ["macroscopic.node.mass|constant|infinity.massSource"],
            "physical_domain": {
                "effort_variable": "pressure",
                "token": "mass",
                "transport_equation": "convection",
                "flow_variable": "mass_flow_rate"
            }
        }
    }
    
    validator = EnhancedArcConnectionValidator(enhanced_options)
    rules = EnhancedArcConnectionRules(validator)
    
    print("Enhanced arc connection system initialized")
    print(f"Available arcs by token: {validator.token_to_arcs}")
    print(f"Available arcs by effort: {validator.effort_to_arcs}")
