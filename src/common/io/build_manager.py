from src.common.corelib import EquationMap, IndexMap, VariableMap

from .builders import EquationMapBuilder, IndexMapBuilder, VariableMapBuilder
from .context import IOContext
from .protocols import DataIO


class IOBuildManager:
    def __init__(self, data_io: DataIO):
        self._data_io = data_io
        self._indices: IndexMap = {}
        self._variables: VariableMap = {}
        self._equations: EquationMap = {}

    def reset(self) -> None:
        self._indices = {}
        self._variables = {}
        self._equations = {}

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

    def get_equations(self, context: IOContext) -> EquationMap:
        self._build_equations(context)

        return self._equations

    def _build_equations(self, context: IOContext) -> None:
        equations_cached = bool(self._equations)
        if equations_cached:
            return

        self._build_variables(context)

        data = self._data_io.get_equation_data(context)

        builder = EquationMapBuilder(self._variables)
        self._equations = builder.build(data)
