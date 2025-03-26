from src.common import corelib
from src.common.io import builders, context, storage


class IOBuildManager:
    def __init__(self, data_controller: storage.DataIO):
        self._data_controller = data_controller
        self._indices: corelib.IndexMap = {}
        self._variables: corelib.VariableMap = {}
        self._equations: corelib.EquationMap = {}

    def reset(self) -> None:
        self._indices = {}
        self._variables = {}
        self._equations = {}

    def get_indices(self, io_context: context.IOContext) -> corelib.IndexMap:
        self._build_indices(io_context)

        return self._indices

    def _build_indices(self, io_context: context.IOContext) -> None:
        indices_cached = bool(self._indices)
        if indices_cached:
            return

        builder = builders.IndexMapBuilder()

        data = self._data_controller.get_index_data(io_context)
        self._indices = builder.build(data)

    def get_variables(self, io_context: context.IOContext) -> corelib.VariableMap:
        self._build_variables(io_context)

        return self._variables

    def _build_variables(self, io_context: context.IOContext) -> None:
        variables_cached = bool(self._variables)
        if variables_cached:
            return

        self._build_indices(io_context)
        builder = builders.VariableMapBuilder(self._indices)

        data = self._data_controller.get_variable_data(io_context)
        self._variables = builder.build(data)

    def get_equations(self, io_context: context.IOContext) -> corelib.EquationMap:
        self._build_equations(io_context)

        return self._equations

    def _build_equations(self, io_context: context.IOContext) -> None:
        equations_cached = bool(self._equations)
        if equations_cached:
            return

        self._build_variables(io_context)

        data = self._data_controller.get_equation_data(io_context)

        builder = builders.EquationMapBuilder(self._variables)
        self._equations = builder.build(data)
