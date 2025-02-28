from dataclasses import dataclass, field
from enum import StrEnum


@dataclass
class OntologyContext:
    repository_location: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""


class ContextMember(StrEnum):
    ONTOLOGY = "ontology"
    MODEL = "model"
    INSTANTIATION = "instantiation"
