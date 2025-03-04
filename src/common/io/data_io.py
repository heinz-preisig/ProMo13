import json
import logging
import stat
from pathlib import Path
from typing import Protocol

from . import path_resolver
from .ontology_context import ContextMember, OntologyContext

logger = logging.Logger(__name__)


class DataIOException(Exception):
    def __init__(
        self, message: str = "An error ocurred while performing IO operations"
    ):
        self.message = message
        super().__init__(self.message)


class DataIO(Protocol):
    def validate_repository_location(self, location: str) -> None: ...
    def get_context_member_options(
        self, context_member: ContextMember, context: OntologyContext
    ) -> list[str]: ...


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

    def get_context_member_options(
        self, context_member: ContextMember, context: OntologyContext
    ) -> list[str]:
        match context_member:
            case ContextMember.ONTOLOGY:
                template = path_resolver.Templates.ONTOLOGY_INDEX_FILE
            case ContextMember.MODEL:
                template = path_resolver.Templates.MODEL_INDEX_FILE
            case ContextMember.INSTANTIATION:
                template = path_resolver.Templates.INSTANTIATION_INDEX_FILE

        index_path = path_resolver.resolve(context, template)

        try:
            with index_path.open("r") as file:
                file_content = file.read()
        except (FileNotFoundError, PermissionError) as err:
            logger.error(err)
            new_error_msg = f"Can not access {context_member} index"
            raise DataIOException(new_error_msg)
        except Exception as err:
            logger.error(err)
            raise Exception(err)

        try:
            data = json.loads(file_content)
        except json.JSONDecodeError as err:
            logger.error(err)
            new_error_msg = f"Corrupted {context_member} index"
            raise DataIOException(new_error_msg)

        if not isinstance(data, list) or not all(
            isinstance(item, str) for item in data
        ):
            error_msg = f"Corrupted {context_member} index"
            raise DataIOException(error_msg)

        return data
