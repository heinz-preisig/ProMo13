import json
import stat
from pathlib import Path
from typing import Protocol

from . import path_resolver
from .ontology_context import OntologyContext


class DataIO(Protocol):
    def validate_repository_location(self, location: str) -> None: ...
    def get_available_ontologies(self, context: OntologyContext) -> list[str]: ...
    def get_available_models(self, context: OntologyContext) -> list[str]: ...
    def get_available_instantiations(self, context: OntologyContext) -> list[str]: ...


class FileIO:
    def validate_repository_location(self, location: str) -> None:
        context = OntologyContext(location)
        template = path_resolver.Templates.ONTOLOGY_REPOSITORY_DIR
        repo_path = path_resolver.resolve(context, template)
        self._check_dir_exists(repo_path)

        mode = repo_path.stat().st_mode
        self._check_write_permissions(repo_path, mode)
        self._check_read_permissions(repo_path, mode)

    def _check_dir_exists(self, repo_path: Path) -> None:
        if not repo_path.is_dir():
            error_msg = f"The directory at {repo_path} does not exist."
            raise FileNotFoundError(error_msg)

    def _check_write_permissions(self, repo_path: Path, mode: int) -> None:
        is_writable = bool(mode & stat.S_IWUSR)
        if not is_writable:
            error_msg = f"You don't have write permissions at {repo_path}."
            raise PermissionError(error_msg)

    def _check_read_permissions(self, repo_path: Path, mode: int) -> None:
        is_readable = bool(mode & stat.S_IRUSR)
        if not is_readable:
            error_msg = f"You don't have read permissions at {repo_path}."
            raise PermissionError(error_msg)

    def get_available_ontologies(self, context: OntologyContext) -> list[str]:
        template = path_resolver.Templates.ONTOLOGY_INDEX_FILE
        index_path = path_resolver.resolve(context, template)

        with index_path.open("r") as file:
            data = json.load(file)

        if not isinstance(data, list) or not all(
            isinstance(item, str) for item in data
        ):
            error_msg = "Invalid data format in ontology index file."
            raise ValueError(error_msg)

        return data

    def get_available_models(self, context: OntologyContext) -> list[str]:
        template = path_resolver.Templates.MODEL_INDEX_FILE
        index_path = path_resolver.resolve(context, template)

        with index_path.open("r") as file:
            data = json.load(file)

        if not isinstance(data, list) or not all(
            isinstance(item, str) for item in data
        ):
            error_msg = "Invalid data format in model index file."
            raise ValueError(error_msg)

        return data

    def get_available_instantiations(self, context: OntologyContext) -> list[str]:
        template = path_resolver.Templates.INSTANTIATION_INDEX_FILE
        index_path = path_resolver.resolve(context, template)

        with index_path.open("r") as file:
            data = json.load(file)

        if not isinstance(data, list) or not all(
            isinstance(item, str) for item in data
        ):
            error_msg = "Invalid data format in instantiation index file."
            raise ValueError(error_msg)

        return data
