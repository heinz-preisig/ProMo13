from dataclasses import dataclass, field


@dataclass
class OntologyContext:
    repository_location: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""
    ontologies: list[str] = field(init=False, default_factory=list)
    models: list[str] = field(init=False, default_factory=list)
    instantiations: list[str] = field(init=False, default_factory=list)
