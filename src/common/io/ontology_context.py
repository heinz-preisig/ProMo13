from dataclasses import dataclass, field
from enum import StrEnum


@dataclass
class OntologyContext:
    repository_location: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""
    ontologies: list[str] = field(init=False, default_factory=list)
    models: list[str] = field(init=False, default_factory=list)
    instantiations: list[str] = field(init=False, default_factory=list)


class ContextMember(StrEnum):
    ONTOLOGY = "ontology"
    MODEL = "model"
    INSTANTIATION = "instantiation"
