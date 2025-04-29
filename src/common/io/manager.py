import typing

from src.common import corelib
from src.common.io import build_manager, context, context_handler, storage


class IOManager:
    def __init__(self, data_controller: storage.GenericStorage | None = None) -> None:
        self._data_controller = data_controller or storage.FileStorage()
        self._context_handler = context_handler.IOContextHandler()
        self._builder = build_manager.IOBuildManager(self._data_controller)

    def get_io_context(self) -> context.IOContext:
        return self._context_handler.get_io_context()

    def set_repository_location(self, location: str) -> None:
        self._data_controller.validate_repository_location(location)
        self._context_handler.set_repository_location(location)
        self._builder.reset()

    def set_context_member_name(
        self, context_member: context.IOContextMember, name: str
    ) -> None:
        io_context = self._context_handler.get_io_context()
        context_member_options = self._data_controller.get_context_member_options(
            context_member, io_context
        )
        self._context_handler.set_context_member_name(
            context_member, name, context_member_options
        )
        self._builder.reset()

    def get_context_member_valid_options(
        self, context_member: context.IOContextMember
    ) -> list[str]:
        io_context = self._context_handler.get_io_context()
        return self._data_controller.get_context_member_options(
            context_member, io_context
        )

    def get_current_index_map(self) -> corelib.IndexMap:
        io_context = self._context_handler.get_io_context()

        index_map = typing.cast(
            corelib.IndexMap,
            self._builder.get_core_map(io_context, corelib.CoreMapVariant.INDEX),
        )
        return index_map

    def get_current_variable_map(self) -> corelib.VariableMap:
        io_context = self._context_handler.get_io_context()

        variable_map = typing.cast(
            corelib.VariableMap,
            self._builder.get_core_map(io_context, corelib.CoreMapVariant.VARIABLE),
        )
        return variable_map

    def get_current_equation_map(self) -> corelib.EquationMap:
        io_context = self._context_handler.get_io_context()

        equation_map = typing.cast(
            corelib.EquationMap,
            self._builder.get_core_map(io_context, corelib.CoreMapVariant.EQUATION),
        )
        return equation_map
