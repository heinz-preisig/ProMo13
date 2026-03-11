#!/usr/local/bin/python3
# encoding: utf-8

"""
Generate arc-node compatibility file using the dynamic arc options generator
Creates a comprehensive mapping of which arcs can connect which nodes
"""

import json
import os
from pathlib import Path
from dynamic_arc_options_generator import DynamicArcOptionsGenerator, DynamicPhysicalDomainMapper


def create_sample_ontology_data():
    """Create sample ontology data structure for demonstration"""
    return {
        "ontology_tree": {
            "macroscopic": {
                "structure": {
                    "arc": {
                        "mass": {
                            "convection": {},
                            "diffusion": {}
                        },
                        "energy": {
                            "conduction": {},
                            "convection": {}
                        },
                        "charge": {
                            "conduction": {}
                        }
                    }
                }
            }
        }
    }


def create_sample_entities_data():
    """Create sample entities data with arc and node entities"""
    return {
        "macroscopic.arc.mass|convection|lumped.convectiveMassFlow": {
            "entity_type": "arc",
            "variables": {
                "pressure": {"type": "effort", "classification": "effort"},
                "mass_flow_rate": {"type": "flow", "classification": "flow"}
            }
        },
        "macroscopic.arc.mass|diffusion|lumped.diffusionalMassTransfer": {
            "entity_type": "arc", 
            "variables": {
                "chemical_potential": {"type": "effort", "classification": "effort"},
                "mass_flow_rate": {"type": "flow", "classification": "flow"}
            }
        },
        "macroscopic.arc.energy|conduction|lumped.heatConduction": {
            "entity_type": "arc",
            "variables": {
                "temperature": {"type": "effort", "classification": "effort"},
                "heat_flow_rate": {"type": "flow", "classification": "flow"}
            }
        },
        "macroscopic.arc.charge|conduction|lumped.electricalConduction": {
            "entity_type": "arc",
            "variables": {
                "voltage": {"type": "effort", "classification": "effort"},
                "current": {"type": "flow", "classification": "flow"}
            }
        },
        "macroscopic.node.mass|constant|infinity.massSource": {
            "entity_type": "node",
            "variables": {
                "pressure": {"type": "effort", "classification": "effort"}
            }
        },
        "macroscopic.node.mass|dynamic|lumped.dynamicMass": {
            "entity_type": "node",
            "variables": {
                "pressure": {"type": "effort", "classification": "effort"},
                "mass": {"type": "state", "classification": "state"}
            }
        },
        "macroscopic.node.energy|constant|infinity.energySource": {
            "entity_type": "node",
            "variables": {
                "temperature": {"type": "effort", "classification": "effort"}
            }
        },
        "macroscopic.node.energy|dynamic|lumped.thermalMass": {
            "entity_type": "node",
            "variables": {
                "temperature": {"type": "effort", "classification": "effort"},
                "energy": {"type": "state", "classification": "state"}
            }
        },
        "macroscopic.node.charge|constant|infinity.chargeSource": {
            "entity_type": "node",
            "variables": {
                "voltage": {"type": "effort", "classification": "effort"}
            }
        },
        "macroscopic.node.charge|dynamic|lumped.electricalCapacitance": {
            "entity_type": "node",
            "variables": {
                "voltage": {"type": "effort", "classification": "effort"},
                "charge": {"type": "state", "classification": "state"}
            }
        }
    }


def generate_arc_node_compatibility_file(ontology_data=None, entities_data=None, output_file=None):
    """
    Generate comprehensive arc-node compatibility file
    
    Args:
        ontology_data: Ontology structure (will use sample if None)
        entities_data: Entity definitions (will use sample if None)
        output_file: Output file path (will use default if None)
    """
    
    # Use sample data if not provided
    if ontology_data is None:
        ontology_data = create_sample_ontology_data()
        print("Using sample ontology data")
    
    if entities_data is None:
        entities_data = create_sample_entities_data()
        print("Using sample entities data")
    
    # Set default output file
    if output_file is None:
        output_file = Path(__file__).parent / "generated_arc_node_compatibility.json"
    
    # Initialize the dynamic generator
    generator = DynamicArcOptionsGenerator(ontology_data, entities_data)
    
    # Generate enhanced arc options
    enhanced_options = generator.generate_enhanced_arc_options()
    
    # Create comprehensive compatibility mapping
    compatibility_mapping = {
        "metadata": {
            "generated_by": "DynamicArcOptionsGenerator",
            "description": "Comprehensive arc-node compatibility mapping with physical domain information",
            "total_arcs": len(enhanced_options),
            "generation_timestamp": str(Path(__file__).stat().st_mtime)
        },
        "arc_options": enhanced_options,
        "compatibility_summary": create_compatibility_summary(enhanced_options),
        "physical_domains": create_physical_domain_summary(enhanced_options)
    }
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compatibility_mapping, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Arc-node compatibility file generated: {output_file}")
    print(f"📊 Generated {len(enhanced_options)} arc configurations")
    
    return compatibility_mapping


def create_compatibility_summary(enhanced_options):
    """Create summary of arc-node compatibility"""
    summary = {
        "total_arcs": len(enhanced_options),
        "arcs_by_token": {},
        "node_compatibility": {},
        "connection_statistics": {
            "max_sources_per_arc": 0,
            "max_sinks_per_arc": 0,
            "total_possible_connections": 0
        }
    }
    
    # Analyze each arc
    for arc_name, arc_data in enhanced_options.items():
        sources = arc_data.get("sources", [])
        sinks = arc_data.get("sinks", [])
        physical_domain = arc_data.get("physical_domain")
        
        # Update statistics
        summary["connection_statistics"]["max_sources_per_arc"] = max(
            summary["connection_statistics"]["max_sources_per_arc"], len(sources)
        )
        summary["connection_statistics"]["max_sinks_per_arc"] = max(
            summary["connection_statistics"]["max_sinks_per_arc"], len(sinks)
        )
        summary["connection_statistics"]["total_possible_connections"] += len(sources) * len(sinks)
        
        # Group by token
        if physical_domain:
            token = physical_domain.get("token", "unknown")
            if token not in summary["arcs_by_token"]:
                summary["arcs_by_token"][token] = []
            summary["arcs_by_token"][token].append(arc_name)
        
        # Track node compatibility
        for source in sources:
            if source not in summary["node_compatibility"]:
                summary["node_compatibility"][source] = {"can_be_source": [], "can_be_sink": []}
            summary["node_compatibility"][source]["can_be_source"].append(arc_name)
        
        for sink in sinks:
            if sink not in summary["node_compatibility"]:
                summary["node_compatibility"][sink] = {"can_be_source": [], "can_be_sink": []}
            summary["node_compatibility"][sink]["can_be_sink"].append(arc_name)
    
    return summary


def create_physical_domain_summary(enhanced_options):
    """Create summary of physical domains"""
    domains = {}
    
    for arc_name, arc_data in enhanced_options.items():
        physical_domain = arc_data.get("physical_domain")
        if physical_domain:
            token = physical_domain.get("token", "unknown")
            mechanism = physical_domain.get("transport_equation", "unknown")
            effort_var = physical_domain.get("effort_variable", "unknown")
            flow_var = physical_domain.get("flow_variable", "unknown")
            
            domain_key = f"{token}|{mechanism}"
            if domain_key not in domains:
                domains[domain_key] = {
                    "token": token,
                    "transport_mechanism": mechanism,
                    "effort_variable": effort_var,
                    "flow_variable": flow_var,
                    "arcs": []
                }
            domains[domain_key]["arcs"].append(arc_name)
    
    return domains


def load_real_data_if_available():
    """Try to load real ontology and entities data from the project"""
    # Look for real data files in common locations
    potential_paths = [
        "../../tests/developer/common/io/storage/test_files/repositoryOK/ontologyOK",
        "../../../tests/developer/common/io/storage/test_files/repositoryOK/ontologyOK",
        "/home/heinz/1_Gits/CAM12/tests/developer/common/io/storage/test_files/repositoryOK/ontologyOK"
    ]
    
    for base_path in potential_paths:
        try:
            entities_file = Path(base_path) / "entities.json"
            if entities_file.exists():
                with open(entities_file, 'r') as f:
                    entities_data = json.load(f)
                print(f"✅ Loaded real entities data from {entities_file}")
                return entities_data
        except Exception as e:
            print(f"⚠️  Could not load from {base_path}: {e}")
    
    return None


if __name__ == "__main__":
    print("🔄 Generating arc-node compatibility file...")
    
    # Try to load real data, fall back to sample
    real_entities = load_real_data_if_available()
    
    # Generate compatibility file
    compatibility_data = generate_arc_node_compatibility_file(
        entities_data=real_entities
    )
    
    # Print summary
    print("\n📋 Generation Summary:")
    print(f"   Total arcs: {compatibility_data['metadata']['total_arcs']}")
    print(f"   Physical domains: {len(compatibility_data['physical_domains'])}")
    
    stats = compatibility_data['compatibility_summary']['connection_statistics']
    print(f"   Total possible connections: {stats['total_possible_connections']}")
    
    print("\n🎯 Arc-node compatibility file ready for use!")
