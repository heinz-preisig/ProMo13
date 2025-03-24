from src.common.corelib import IndexMap, VariableMap

from .builders import IndexMapBuilder, VariableMapBuilder
from .context import IOContext
from .protocols import DataIO


class IOBuildManager:
    def __init__(self, data_io: DataIO):
        self._data_io = data_io
        self._indices: IndexMap = {}
        self._variables: VariableMap = {}

    def get_indices(self, context: IOContext) -> IndexMap:
        self._build_indices(context)

        return self._indices

    def _build_indices(self, context: IOContext) -> None:
        indices_cached = bool(self._indices)
        if indices_cached:
            return

        builder = IndexMapBuilder()

        data = self._data_io.get_index_data(context)
        self._indices = builder.build(data)

    def get_variables(self, context: IOContext) -> VariableMap:
        self._build_variables(context)

        return self._variables

    def _build_variables(self, context: IOContext) -> None:
        variables_cached = bool(self._variables)
        if variables_cached:
            return

        self._build_indices(context)
        builder = VariableMapBuilder(self._indices)

        data = self._data_io.get_variable_data(context)
        self._variables = builder.build(data)
