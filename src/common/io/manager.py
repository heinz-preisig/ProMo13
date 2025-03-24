import copy
import json
import stat
import typing
from pathlib import Path

import attrs
import cattrs

from src.common.corelib import IndexMap, VariableMap

from . import exceptions
from .builder import IOBuilder
from .context import IOContext, IOContextMember
from .context_handler import IOContextHandler
from .file_io import FileIO


class DataIO(typing.Protocol):
    def validate_repository_location(self, location: str) -> None: ...
    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]: ...
    def get_index_data(self, context: IOContext) -> typing.Any: ...
    def get_variable_data(self, context: IOContext) -> typing.Any: ...


@attrs.define
class IOManager:
    _data_io: DataIO = attrs.Factory(FileIO)
    _context_handler: IOContextHandler = attrs.field(
        init=False, factory=IOContextHandler
    )
    _builder: IOBuilder = attrs.field(init=False, factory=IOBuilder)

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
        self._build_index_map(context)

        return self._builder.indices

    def _build_index_map(self, context: IOContext) -> None:
        if self._builder.indices:
            return

        data = self._data_io.get_index_data(context)
        self._builder.build_index_map(data)

    def get_current_variable_map(self) -> VariableMap:
        context = self._context_handler.get_io_context()
        self._build_variable_map(context)

        return self._builder.variables

    def _build_variable_map(self, context: IOContext) -> None:
        self._build_index_map(context)

        if self._builder.variables:
            return

        data = self._data_io.get_variable_data(context)
        self._builder.build_variable_map(data)
