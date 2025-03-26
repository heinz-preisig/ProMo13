import logging
import pathlib
import stat
import typing

import attrs

from src.common.io import context
from src.common.io.data_io import (
    exceptions,
    json_file_reader_manager,
    path_resolver,
    protocols,
)

logger = logging.Logger(__name__)


@attrs.define
class FileIO:
    _file_reader: protocols.FileReader = attrs.field(
        init=False, factory=json_file_reader_manager.JSONFileReader
    )

    def validate_repository_location(self, location: str) -> None:
        new_context = context.IOContext(location)
        template = path_resolver.PathTemplateStrings.ONTOLOGY_REPOSITORY_DIR
        repo_path = path_resolver.resolve(new_context, template)
        self._check_dir_exists(repo_path)

        mode = repo_path.stat().st_mode
        self._check_permissions(repo_path, mode)

    def _check_dir_exists(self, repo_path: pathlib.Path) -> None:
        if not repo_path.is_dir():
            log_error_msg = f"The directory does not exist: {repo_path}"
            logger.error(log_error_msg)
            exception_msg = f"Invalid repository location: {repo_path}"
            raise exceptions.DataIOError(exception_msg)

    def _check_permissions(self, repo_path: pathlib.Path, mode: int) -> None:
        READ_MODE = stat.S_IRUSR
        WRITE_MODE = stat.S_IWUSR
        for mode_constant in [READ_MODE, WRITE_MODE]:
            has_mode_permissions = bool(mode & mode_constant)
            if not has_mode_permissions:
                log_error_msg = f"You don't have the necessary permissions ({mode_constant}): {repo_path}."
                logger.error(log_error_msg)
                exception_msg = f"Invalid repository location: {repo_path}"
                raise exceptions.DataIOError(exception_msg)

    def get_context_member_options(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> list[str]:
        options = self._file_reader.get_repository_index_options(
            context_member, io_context
        )
        return options

    def get_index_data(self, io_context: context.IOContext) -> typing.Any:
        index_data = self._file_reader.read_index_file(io_context)
        return index_data

    def get_variable_data(self, io_context: context.IOContext) -> typing.Any:
        variable_data = self._file_reader.read_variable_file(io_context)
        return variable_data

    def get_equation_data(self, io_context: context.IOContext) -> typing.Any:
        equation_data = self._file_reader.read_equation_file(io_context)
        return equation_data
