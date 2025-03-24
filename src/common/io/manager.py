import copy
import json
import stat
import typing
from pathlib import Path

import attrs
import cattrs

from src.common.corelib import IndexMap, VariableMap

from . import exceptions
from .build_manager import IOBuildManager
from .context import IOContext, IOContextMember
from .context_handler import IOContextHandler
from .file_io import FileIO
from .protocols import DataIO


class IOManager:
    def __init__(self, data_io: DataIO = FileIO()) -> None:
        self._data_io = data_io
        self._context_handler = IOContextHandler()
        self._builder = IOBuildManager(data_io)

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

        return self._builder.get_indices(context)

    def get_current_variable_map(self) -> VariableMap:
        context = self._context_handler.get_io_context()

        return self._builder.get_variables(context)
