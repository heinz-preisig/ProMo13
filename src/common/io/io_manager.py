import copy
import json
import stat
from pathlib import Path
from typing import Protocol

import attrs

from .data_io import DataIO, FileIO
from .ontology_context import OntologyContext
from .ontology_context_manager import OntologyContextManager


class IOManager(Protocol):
    def get_ontology_context(self) -> OntologyContext: ...
    def set_repository_location(self, location: str) -> None: ...
    def set_ontology_name(self, name: str) -> None: ...
    def set_model_name(self, name: str) -> None: ...
    def set_instantiation_name(self, name: str) -> None: ...


@attrs.define
class DefaultIOManager:
    _ontology_context_manager: OntologyContextManager = attrs.field(
        init=False, factory=OntologyContextManager
    )
    _data_io: DataIO = attrs.field(init=False, factory=FileIO)

    def get_ontology_context(self) -> OntologyContext:
        return self._ontology_context_manager.get_ontology_context()

    def set_repository_location(self, location: str) -> None:
        self._data_io.validate_repository_location(location)
        self._ontology_context_manager.set_repository_location(location)

    def set_ontology_name(self, name: str) -> None:
        context = self._ontology_context_manager.get_ontology_context()
        available_ontologies = self._data_io.get_available_ontologies(context)
        self._ontology_context_manager.set_ontology_name(name, available_ontologies)

    def set_model_name(self, name: str) -> None:
        context = self._ontology_context_manager.get_ontology_context()
        available_models = self._data_io.get_available_models(context)
        self._ontology_context_manager.set_model_name(name, available_models)

    def set_instantiation_name(self, name: str) -> None:
        context = self._ontology_context_manager.get_ontology_context()
        available_instantiations = self._data_io.get_available_instantiations(context)
        self._ontology_context_manager.set_instantiation_name(
            name, available_instantiations
        )
