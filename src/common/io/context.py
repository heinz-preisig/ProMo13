from dataclasses import dataclass
from enum import StrEnum


class IOContextMember(StrEnum):
    ONTOLOGY = "ontology"
    MODEL = "model"
    INSTANTIATION = "instantiation"


@dataclass
class IOContext:
    repository_location: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""

    def get_context_member_name(self, context_member: IOContextMember) -> str:
        match context_member:
            case IOContextMember.ONTOLOGY:
                return self.ontology_name
            case IOContextMember.MODEL:
                return self.model_name
            case IOContextMember.INSTANTIATION:
                return self.instantiation_name
