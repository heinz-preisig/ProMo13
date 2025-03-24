import dataclasses

from src.common.io import context, exceptions

REPOSITORY_LOCATION_KEY = "repository_location"
IO_CONTEXT_MEMBER_KEY = "{context_member}_name"


@dataclasses.dataclass
class IOContextNode:
    parent: str
    child: str
    value: str = ""


class IOContextHandler:
    def __init__(self) -> None:
        key_ontology_name = self._get_context_member_key(
            context.IOContextMember.ONTOLOGY
        )
        key_model_name = self._get_context_member_key(context.IOContextMember.MODEL)
        key_instantiation_name = self._get_context_member_key(
            context.IOContextMember.INSTANTIATION
        )

        self._nodes: dict[str, IOContextNode] = {
            REPOSITORY_LOCATION_KEY: IOContextNode("", "ontology_name"),
            key_ontology_name: IOContextNode("repository_location", "model_name"),
            key_model_name: IOContextNode("ontology_name", "instantiation_name"),
            key_instantiation_name: IOContextNode("model_name", ""),
        }

    def _get_context_member_key(self, context_member: context.IOContextMember) -> str:
        return IO_CONTEXT_MEMBER_KEY.format(context_member=context_member)

    def get_repository_location(self) -> str:
        return self._nodes[REPOSITORY_LOCATION_KEY].value

    def get_context_member_name(self, context_member: context.IOContextMember) -> str:
        key_name = self._get_context_member_key(context_member)
        return self._nodes[key_name].value

    def set_repository_location(self, repository_location: str) -> None:
        self._nodes[REPOSITORY_LOCATION_KEY].value = repository_location
        self._reset_dependent_context(REPOSITORY_LOCATION_KEY)

    def set_context_member_name(
        self,
        context_member: context.IOContextMember,
        name: str,
        options: list[str],
    ) -> None:
        self._verify_context_member_name(context_member, name, options)

        key_name = self._get_context_member_key(context_member)
        self._nodes[key_name].value = name

        self._reset_dependent_context(key_name)

    def _verify_context_member_name(
        self,
        context_member: context.IOContextMember,
        name: str,
        options: list[str],
    ) -> None:
        if name not in options:
            error_msg = f"Invalid {context_member} name: {name}"
            io_context = self.get_io_context()
            raise exceptions.IOContextError(error_msg, io_context)

    def _reset_dependent_context(self, key_name: str) -> None:
        child_key = self._nodes[key_name].child
        if not child_key:
            return

        self._nodes[child_key].value = ""
        self._reset_dependent_context(child_key)

    def get_io_context(self) -> context.IOContext:
        return context.IOContext(
            repository_location=self.get_repository_location(),
            ontology_name=self.get_context_member_name(
                context.IOContextMember.ONTOLOGY
            ),
            model_name=self.get_context_member_name(context.IOContextMember.MODEL),
            instantiation_name=self.get_context_member_name(
                context.IOContextMember.INSTANTIATION
            ),
        )
