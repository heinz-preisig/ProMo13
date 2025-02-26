import copy
import json
import stat
from dataclasses import dataclass, field
from pathlib import Path

import attrs


@dataclass
class OntologyContext:
    repository_location: str = ""
    ontology_name: str = ""
    model_name: str = ""
    instantiation_name: str = ""
    ontologies: list[str] = field(init=False, default_factory=list)
    models: list[str] = field(init=False, default_factory=list)
    instantiations: list[str] = field(init=False, default_factory=list)


@attrs.define
class OntologyContextManager:
    _ontology_context = attrs.field(init=False, factory=OntologyContext)

    def get_ontology_context(self) -> OntologyContext:
        context_copy = copy.deepcopy(self._ontology_context)
        return context_copy

    def update_ontology_context(self, context: OntologyContext) -> None:
        if context.repository_location:
            self._update_repository_location(context.repository_location)
            self._update_ontologies()

        if context.ontology_name:
            self._update_ontology_name(context.ontology_name)
            self._update_models()

        if context.model_name:
            self._update_model_name(context.model_name)
            self._update_instantiations()

        if context.instantiation_name:
            self._update_instantiation_name(context.instantiation_name)

    def _update_repository_location(self, repo_location: str) -> None:
        self._verify_path(repo_location)

        self._ontology_context.repository_location = repo_location

    def _verify_path(self, repo_location: str) -> None:
        repo_path = Path(repo_location)

        self._check_dir_exists(repo_path)

        mode = repo_path.stat().st_mode
        self._check_write_permissions(repo_path, mode)
        self._check_read_permissions(repo_path, mode)

    def _check_dir_exists(self, repo_path: Path) -> None:
        if not repo_path.is_dir():
            raise FileNotFoundError(f"The directory {repo_path} does not exist.")

    def _check_write_permissions(self, repo_path: Path, mode: int) -> None:
        is_writable = bool(mode & stat.S_IWUSR)
        if not is_writable:
            raise PermissionError(f"You have not write permissions on {repo_path}")

    def _check_read_permissions(self, repo_path: Path, mode: int) -> None:
        is_readable = bool(mode & stat.S_IRUSR)
        if not is_readable:
            raise PermissionError(f"You have not read permissions on {repo_path}")

    def _update_ontologies(self) -> None:
        repo_path = Path(self._ontology_context.repository_location)
        ontologies_file_path = repo_path / ".ontologies.json"

        if not ontologies_file_path.is_file():
            NO_ONTOLOGIES = {"ontologies": []}
            with ontologies_file_path.open("w") as file:
                json.dump(NO_ONTOLOGIES, file)

        with ontologies_file_path.open("r") as file:
            data = json.load(file)

        self._ontology_context.ontologies = data["ontologies"]

    def _update_ontology_name(self, name: str) -> None:
        self._verify_ontology_name(name)

        self._ontology_context.ontology_name = name

    def _verify_ontology_name(self, name: str) -> None:
        repo_path = Path(self._ontology_context.repository_location)

        if name not in self._ontology_context.ontologies:
            raise FileNotFoundError(
                f"The ontology {name} does not exist in the repository at {repo_path}"
            )

    def _update_models(self) -> None:
        repo_path = Path(self._ontology_context.repository_location)
        ontology_name = self._ontology_context.ontology_name
        models_file_path = repo_path / ontology_name / "models" / ".models.json"
        with models_file_path.open("r") as file:
            data = json.load(file)

        self._ontology_context.models = data["models"]

    def _update_model_name(self, name: str) -> None:
        self._verify_model_name(name)

        self._ontology_context.model_name = name

    def _verify_model_name(self, name: str) -> None:
        ontology_name = self._ontology_context.ontology_name

        if name not in self._ontology_context.models:
            raise FileNotFoundError(
                f"The model {name} does not exist in the ontology {ontology_name}"
            )

    def _update_instantiations(self) -> None:
        repo_path = Path(self._ontology_context.repository_location)
        ontology_name = self._ontology_context.ontology_name
        model_name = self._ontology_context.model_name

        instantiations_file_path = (
            repo_path
            / ontology_name
            / "models"
            / model_name
            / "instantiations"
            / ".instantiations.json"
        )
        with instantiations_file_path.open("r") as file:
            data = json.load(file)

        self._ontology_context.instantiations = data["instantiations"]

    def _update_instantiation_name(self, name: str) -> None:
        model_name = self._ontology_context.model_name

        if name not in self._ontology_context.instantiations:
            raise FileNotFoundError(
                f"The instantiation {name} does not exist in the model {model_name}"
            )
        self._ontology_context.instantiation_name = name
