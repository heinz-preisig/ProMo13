import dataclasses
import enum


class IOContextMember(enum.StrEnum):
    ONTOLOGY = "ontology"
    MODEL = "model"
    INSTANTIATION = "instantiation"


@dataclasses.dataclass
class IOContext:
    repository_location: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""

    def get_context_member_name(self, context_member: IOContextMember) -> str:
        match context_member:
            case IOContextMember.ONTOLOGY:
                name = self.ontology_name
            case IOContextMember.MODEL:
                name = self.model_name
            case IOContextMember.INSTANTIATION:
                name = self.instantiation_name

        return name
