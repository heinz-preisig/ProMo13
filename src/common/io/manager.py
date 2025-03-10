import copy
import json
import stat
import typing
from pathlib import Path

import attrs

from .context import IOContext, IOContextMember
from .context_manager import IOContextManager
from .file_io import FileIO


class DataIO(typing.Protocol):
    def validate_repository_location(self, location: str) -> None: ...
    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]: ...


@attrs.define
class IOManager:
    _data_io: DataIO = attrs.field(factory=FileIO)
    _ontology_context_manager: IOContextManager = attrs.field(
        init=False, factory=IOContextManager
    )

    def get_ontology_context(self) -> IOContext:
        return self._ontology_context_manager.get_ontology_context()

    def set_repository_location(self, location: str) -> None:
        self._data_io.validate_repository_location(location)
        self._ontology_context_manager.set_repository_location(location)

    def set_context_member_name(
        self, context_member: IOContextMember, name: str
    ) -> None:
        context = self._ontology_context_manager.get_ontology_context()
        context_member_options = self._data_io.get_context_member_options(
            context_member, context
        )
        self._ontology_context_manager.set_context_member_name(
            context_member, name, context_member_options
        )

    def get_available_ontologies(self) -> list[str]:
        context_member = IOContextMember.ONTOLOGY
        context = self._ontology_context_manager.get_ontology_context()
        available_ontologies = self._data_io.get_context_member_options(
            context_member, context
        )
        return available_ontologies

    def get_available_models(self) -> list[str]:
        context_member = IOContextMember.MODEL
        context = self._ontology_context_manager.get_ontology_context()
        available_models = self._data_io.get_context_member_options(
            context_member, context
        )
        return available_models

    def get_available_instantiations(self) -> list[str]:
        context_member = IOContextMember.INSTANTIATION
        context = self._ontology_context_manager.get_ontology_context()
        available_instantiations = self._data_io.get_context_member_options(
            context_member, context
        )
        return available_instantiations
