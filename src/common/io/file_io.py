import logging
import stat
import typing
from pathlib import Path

import attrs

from . import json_file_reader_manager, path_resolver
from .context import IOContext, IOContextMember
from .exceptions import DataIOError

logger = logging.Logger(__name__)


class FileReader(typing.Protocol):
    def get_repository_index_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]: ...
    def read_index_file(self, context: IOContext) -> typing.Any: ...


@attrs.define
class FileIO:
    _file_reader: FileReader = attrs.field(
        init=False, factory=json_file_reader_manager.JSONFileReader
    )

    def validate_repository_location(self, location: str) -> None:
        context = IOContext(location)
        template = path_resolver.PathTemplateStrings.ONTOLOGY_REPOSITORY_DIR
        repo_path = path_resolver.resolve(context, template)
        self._check_dir_exists(repo_path)

        mode = repo_path.stat().st_mode
        self._check_permissions(repo_path, mode)

    def _check_dir_exists(self, repo_path: Path) -> None:
        if not repo_path.is_dir():
            log_error_msg = f"The directory does not exist: {repo_path}"
            logger.error(log_error_msg)
            exception_msg = f"Invalid repository location: {repo_path}"
            raise DataIOError(exception_msg)

    def _check_permissions(self, repo_path: Path, mode: int) -> None:
        READ_MODE = stat.S_IRUSR
        WRITE_MODE = stat.S_IWUSR
        for mode_constant in [READ_MODE, WRITE_MODE]:
            has_mode_permissions = bool(mode & mode_constant)
            if not has_mode_permissions:
                log_error_msg = f"You don't have the necessary permissions ({mode_constant}): {repo_path}."
                logger.error(log_error_msg)
                exception_msg = f"Invalid repository location: {repo_path}"
                raise DataIOError(exception_msg)

    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        options = self._file_reader.get_repository_index_options(
            context_member, context
        )
        return options

    def get_index_data(self, context: IOContext) -> typing.Any:
        index_data = self._file_reader.read_index_file(context)
        return index_data

    def get_variable_data(self, context: IOContext) -> typing.Any:
        pass
