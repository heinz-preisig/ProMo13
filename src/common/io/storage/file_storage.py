import typing

import attrs

from src.common import corelib
from src.common.io import context
from src.common.io.storage import (
    file_reader,
    protocols,
    repository_validation,
)


@attrs.define
class FileStorage:
    _file_reader: protocols.FileReader = attrs.field(
        init=False, factory=file_reader.FileReader
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

    def get_core_map_data(
        self, map_variant: corelib.CoreMapVariant, io_context: context.IOContext
    ) -> typing.Any:
        return self._file_reader.read_core_map_file(map_variant, io_context)
