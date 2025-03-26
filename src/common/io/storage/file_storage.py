import typing

import attrs

from src.common.io import context
from src.common.io.storage import (
    json_file_reader_manager,
    protocols,
    repository_validation,
)


@attrs.define
class FileStorage:
    _file_reader: protocols.FileReader = attrs.field(
        init=False, factory=json_file_reader_manager.JSONFileReader
    )

    def validate_repository_location(self, location: str) -> None:
        repo_validator = repository_validation.FolderRepositoryValidator(location)
        repo_validator.validate_repository_location()

    def get_context_member_options(
        self, context_member: context.IOContextMember, io_context: context.IOContext
    ) -> list[str]:
        return self._file_reader.get_repository_index_options(
            context_member, io_context
        )

    def get_index_data(self, io_context: context.IOContext) -> typing.Any:
        return self._file_reader.read_index_file(io_context)

    def get_variable_data(self, io_context: context.IOContext) -> typing.Any:
        return self._file_reader.read_variable_file(io_context)

    def get_equation_data(self, io_context: context.IOContext) -> typing.Any:
        return self._file_reader.read_equation_file(io_context)
