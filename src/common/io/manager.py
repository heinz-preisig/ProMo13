import copy
import json
import stat
import typing
from pathlib import Path

import attrs
import cattrs

from src.common.corelib import Index, IndexMap

from . import exceptions
from .context import IOContext, IOContextMember
from .context_handler import IOContextHandler
from .file_io import FileIO


class DataIO(typing.Protocol):
    def validate_repository_location(self, location: str) -> None: ...
    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]: ...
    def get_index_data(self, context: IOContext) -> typing.Any: ...


@attrs.define
class IOManager:
    _data_io: DataIO = attrs.field(factory=FileIO)
    _context_handler: IOContextHandler = attrs.field(
        init=False, factory=IOContextHandler
    )

    def get_io_context(self) -> IOContext:
        return self._context_handler.get_io_context()

    def set_repository_location(self, location: str) -> None:
        self._data_io.validate_repository_location(location)
        self._context_handler.set_repository_location(location)

    def set_context_member_name(
        self, context_member: IOContextMember, name: str
    ) -> None:
        context = self._context_handler.get_io_context()
        context_member_options = self._data_io.get_context_member_options(
            context_member, context
        )
        self._context_handler.set_context_member_name(
            context_member, name, context_member_options
        )

    def get_context_member_valid_options(
        self, context_member: IOContextMember
    ) -> list[str]:
        context = self._context_handler.get_io_context()
        return self._data_io.get_context_member_options(context_member, context)

    def get_current_index_map(self) -> IndexMap:
        context = self._context_handler.get_io_context()
        data = self._data_io.get_index_data(context)
        new_index_map = {}

        c = cattrs.Converter()

        def validate_type(val, type):
            if not isinstance(val, type):
                raise ValueError(f"Not a {type}")
            return val

        c.register_structure_hook(int, validate_type)
        c.register_structure_hook(float, validate_type)
        c.register_structure_hook(str, validate_type)
        c.register_structure_hook(bool, validate_type)

        try:
            for idx_data in data:
                new_index = c.structure(idx_data, Index)
                new_index_map[new_index.identifier] = new_index
        except cattrs.BaseValidationError as err:
            raise exceptions.IOBuilderError("") from err

        return new_index_map
