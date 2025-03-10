import json
import logging
import stat
import typing
from pathlib import Path

import jsonschema

from . import json_schemas, path_resolver
from .io_exceptions import DataIOError
from .ontology_context import ContextMember, OntologyContext

logger = logging.Logger(__name__)


class DataIO(typing.Protocol):
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
            log_error_msg = f"The directory does not exist: {repo_path}"
            logger.error(log_error_msg)
            exception_msg = f"Invalid repository location: {repo_path}"
            raise DataIOError(exception_msg)

    def _check_write_permissions(self, repo_path: Path, mode: int) -> None:
        WRITE_MODE = stat.S_IWUSR
        is_writable = bool(mode & WRITE_MODE)
        if not is_writable:
            log_error_msg = f"You don't have write permissions: {repo_path}."
            logger.error(log_error_msg)
            exception_msg = f"Invalid repository location: {repo_path}"
            raise DataIOError(exception_msg)

    def _check_read_permissions(self, repo_path: Path, mode: int) -> None:
        READ_MODE = stat.S_IRUSR
        is_readable = bool(mode & READ_MODE)
        if not is_readable:
            log_error_msg = f"You don't have read permissions: {repo_path}."
            logger.error(log_error_msg)
            exception_msg = f"Invalid repository location: {repo_path}"
            raise DataIOError(exception_msg)

    def get_context_member_options(
        self, context_member: ContextMember, context: OntologyContext
    ) -> list[str]:
        content = self._get_index_file_content(context_member, context)
        options = self._process_index_file_content(context_member, content)

        return options

    def _get_index_file_content(
        self, context_member: ContextMember, context: OntologyContext
    ) -> str:
        index_path = self._get_path_to_index_file(context_member, context)

        access_error_msg = f"Can not access {context_member} index"
        file_content = self._get_file_content(index_path, access_error_msg)

        return file_content

    def _get_path_to_index_file(
        self, context_member: ContextMember, context: OntologyContext
    ) -> Path:
        match context_member:
            case ContextMember.ONTOLOGY:
                template = path_resolver.Templates.ONTOLOGY_INDEX_FILE
            case ContextMember.MODEL:
                template = path_resolver.Templates.MODEL_INDEX_FILE
            case ContextMember.INSTANTIATION:
                template = path_resolver.Templates.INSTANTIATION_INDEX_FILE

        index_path = path_resolver.resolve(context, template)
        return index_path

    def _get_file_content(self, index_path: Path, error_msg: str) -> str:
        try:
            with index_path.open("r") as file:
                file_content = file.read()
        except (FileNotFoundError, PermissionError) as err:
            logger.error(err)
            raise DataIOError(error_msg) from err

        return file_content

    def _process_index_file_content(
        self, context_member: ContextMember, content: str
    ) -> list[str]:
        corrupted_error_msg = f"Corrupted {context_member} index"
        data: list[str] = self._load_json(content, corrupted_error_msg)

        schema = json_schemas.INDEX_FILE
        self._validate_json(data, schema, corrupted_error_msg)

        return data

    def _load_json(self, file_content: str, error_msg: str) -> typing.Any:
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError as err:
            logger.error(err)
            raise DataIOError(error_msg) from err

        return data

    def _validate_json(
        self, data: typing.Any, schema: typing.Any, error_msg: str
    ) -> None:
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as err:
            logger.error(err)
            raise DataIOError(error_msg) from err
