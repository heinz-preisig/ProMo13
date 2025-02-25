import copy
import json
import stat
from pathlib import Path
from typing import Protocol

import attrs

from .ontology_context import OntologyContext


class IOManager(Protocol):
    def get_ontology_context(self) -> OntologyContext: ...
    def update_ontology_context(self, context: OntologyContext) -> None: ...


@attrs.define
class DefaultIOManager:
    _ontology_context: OntologyContext = attrs.field(
        init=False, factory=OntologyContext
    )

    def get_ontology_context(self) -> OntologyContext:
        context_copy = copy.deepcopy(self._ontology_context)
        return context_copy

    def update_ontology_context(self, context: OntologyContext) -> None:
        repo_path = Path(context.repository_location)

        if not repo_path.is_dir():
            raise FileNotFoundError(f"The directory {repo_path} does not exist.")

        mode = repo_path.stat().st_mode
        is_writable = bool(mode & stat.S_IWUSR)
        if not is_writable:
            raise PermissionError(f"You have not write permissions on {repo_path}")

        is_readable = bool(mode & stat.S_IRUSR)
        if not is_readable:
            raise PermissionError(f"You have not read permissions on {repo_path}")

        self._ontology_context.repository_location = context.repository_location
        ontologies_file_path = repo_path / ".ontologies.json"

        if not ontologies_file_path.is_file():
            NO_ONTOLOGIES = {"ontologies": []}
            with ontologies_file_path.open("w") as file:
                json.dump(NO_ONTOLOGIES, file)

        with ontologies_file_path.open("r") as file:
            data = json.load(file)

        self._ontology_context.ontologies = data["ontologies"]

        if not context.ontology_name == "":
            if context.ontology_name not in self._ontology_context.ontologies:
                raise FileNotFoundError(
                    f"The ontology {context.ontology_name} does not exist in the repository at {repo_path}"
                )
            self._ontology_context.ontology_name = context.ontology_name

            models_file_path = (
                repo_path / context.ontology_name / "models" / ".models.json"
            )
            with models_file_path.open("r") as file:
                data = json.load(file)

            self._ontology_context.models = data["models"]

        if not context.model_name == "":
            if context.model_name not in self._ontology_context.models:
                raise FileNotFoundError(
                    f"The model {context.model_name} does not exist in the ontology {context.ontology_name}"
                )
            self._ontology_context.model_name = context.model_name

            instantiations_file_path = (
                repo_path
                / context.ontology_name
                / "models"
                / context.model_name
                / "instantiations"
                / ".instantiations.json"
            )
            with instantiations_file_path.open("r") as file:
                data = json.load(file)

            self._ontology_context.instantiations = data["instantiations"]

        if not context.instantiation_name == "":
            if context.instantiation_name not in self._ontology_context.instantiations:
                raise FileNotFoundError(
                    f"The instantiation {context.instantiation_name} does not exist in the model {context.model_name}"
                )
            self._ontology_context.instantiation_name = context.instantiation_name
