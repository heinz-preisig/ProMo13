from dataclasses import dataclass, field
from enum import StrEnum


@dataclass
class IOContext:
    repository_location: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""


class IOContextMember(StrEnum):
    ONTOLOGY = "ontology"
    MODEL = "model"
    INSTANTIATION = "instantiation"
