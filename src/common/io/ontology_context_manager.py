import copy

import attrs

from .io_exceptions import IOContextError
from .ontology_context import ContextMember, OntologyContext


@attrs.define
class OntologyContextManager:
    _ontology_context = attrs.field(init=False, factory=OntologyContext)

    def get_ontology_context(self) -> OntologyContext:
        context_copy = copy.deepcopy(self._ontology_context)
        return context_copy

    def set_repository_location(self, repo_location: str) -> None:
        self._ontology_context.repository_location = repo_location
        self._reset_context_after_repo_location()

    def set_context_member_name(
        self,
        context_member: ContextMember,
        name: str,
        options: list[str],
    ) -> None:
        self._verify_context_member_name(context_member, name, options)
        match context_member:
            case ContextMember.ONTOLOGY:
                self._ontology_context.ontology_name = name
                self._reset_context_after_ontology_name()
            case ContextMember.MODEL:
                self._ontology_context.model_name = name
                self._reset_context_after_model_name()
            case ContextMember.INSTANTIATION:
                self._ontology_context.instantiation_name = name

    def _verify_context_member_name(
        self,
        context_member: ContextMember,
        name: str,
        options: list[str],
    ) -> None:
        if name not in options:
            error_msg = f"Invalid {context_member} name: {name}"
            raise IOContextError(error_msg)

    def _reset_context_after_repo_location(self) -> None:
        self._ontology_context.ontology_name = ""
        self._reset_context_after_ontology_name()

    def _reset_context_after_ontology_name(self) -> None:
        self._ontology_context.model_name = ""
        self._reset_context_after_model_name()

    def _reset_context_after_model_name(self) -> None:
        self._ontology_context.instantiation_name = ""
