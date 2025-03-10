import logging
import stat
import typing
from pathlib import Path

import attrs

from . import json_file_reader, path_resolver
from .context import IOContext, IOContextMember
from .exceptions import DataIOError

logger = logging.Logger(__name__)


class FileReader(typing.Protocol):
    def get_index_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]: ...


@attrs.define
class FileIO:
    _file_reader: FileReader = attrs.field(
        init=False, factory=json_file_reader.JSONFileReader
    )

    def validate_repository_location(self, location: str) -> None:
        context = IOContext(location)
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
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        options = self._file_reader.get_index_options(context_member, context)
        return options
