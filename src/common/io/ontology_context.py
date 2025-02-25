from dataclasses import dataclass


@dataclass
class OntologyContext:
    ontology_repository_path: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""
