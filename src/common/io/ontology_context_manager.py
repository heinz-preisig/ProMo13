import copy
import json
import logging
import stat
from pathlib import Path

import attrs

from .ontology_context import OntologyContext

logger = logging.getLogger(__name__)


@attrs.define
class OntologyContextManager:
    _ontology_context = attrs.field(init=False, factory=OntologyContext)

    def get_ontology_context(self) -> OntologyContext:
        context_copy = copy.deepcopy(self._ontology_context)
        return context_copy

    def set_repository_location(self, repo_location: str) -> None:
        self._ontology_context.repository_location = repo_location

    def set_ontology_name(self, name: str, available_ontologies: list[str]) -> None:
        self._verify_ontology_name(name, available_ontologies)
        self._ontology_context.ontology_name = name

    def _verify_ontology_name(self, name: str, available_ontologies: list[str]) -> None:
        if name not in available_ontologies:
            error_msg = f"The ontology {name} does not exist."
            raise FileNotFoundError(error_msg)

    def set_model_name(self, name: str, available_models: list[str]) -> None:
        self._verify_model_name(name, available_models)
        self._ontology_context.model_name = name

    def _verify_model_name(self, name: str, available_models: list[str]) -> None:
        if name not in available_models:
            error_msg = f"The model {name} does not exist."
            raise FileNotFoundError(error_msg)

    def set_instantiation_name(
        self, name: str, available_instantiations: list[str]
    ) -> None:
        self._verify_instantiation(name, available_instantiations)
        self._ontology_context.instantiation_name = name

    def _verify_instantiation(
        self, name: str, available_instantiations: list[str]
    ) -> None:
        if name not in available_instantiations:
            error_msg = f"The instantiation {name} does not exist."
            raise FileNotFoundError(error_msg)
