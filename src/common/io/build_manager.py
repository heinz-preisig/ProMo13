from src.common import corelib
from src.common.io import builders, context, storage

CORE_MAPS_BUILD_DEPENDENCIES = {
    corelib.CoreMapVariant.INDEX: [],
    corelib.CoreMapVariant.VARIABLE: [corelib.CoreMapVariant.INDEX],
    corelib.CoreMapVariant.EQUATION: [corelib.CoreMapVariant.VARIABLE],
}


class IOBuildManager:
    def __init__(self, data_controller: storage.GenericStorage):
        self._data_controller = data_controller

        self._core_maps: dict[corelib.CoreMapVariant, corelib.CoreMap] = {
            corelib.CoreMapVariant.INDEX: {},
            corelib.CoreMapVariant.VARIABLE: {},
            corelib.CoreMapVariant.EQUATION: {},
        }

    def reset(self) -> None:
        for core_map_variant in self._core_maps:
            self._core_maps[core_map_variant] = {}

    def get_core_map(
        self, io_context: context.IOContext, map_variant: corelib.CoreMapVariant
    ) -> corelib.CoreMap:
        self._build_core_map(io_context, map_variant)

        return self._core_maps[map_variant]

    def _build_core_map(
        self, io_context: context.IOContext, map_variant: corelib.CoreMapVariant
    ) -> None:
        core_map_cached = bool(self._core_maps[map_variant])
        if core_map_cached:
            return

        for dependency_variant in CORE_MAPS_BUILD_DEPENDENCIES[map_variant]:
            self._build_core_map(io_context, dependency_variant)

        dependencies = [
            self._core_maps[dependency_variant]
            for dependency_variant in CORE_MAPS_BUILD_DEPENDENCIES[map_variant]
        ]

        match map_variant:
            case corelib.CoreMapVariant.INDEX:
                builder = builders.IndexMapBuilder(*dependencies)
                data = self._data_controller.get_index_data(io_context)
            case corelib.CoreMapVariant.VARIABLE:
                builder = builders.VariableMapBuilder(*dependencies)
                data = self._data_controller.get_variable_data(io_context)
            case corelib.CoreMapVariant.EQUATION:
                builder = builders.EquationMapBuilder(*dependencies)
                data = self._data_controller.get_equation_data(io_context)

        self._core_maps[map_variant] = builder.build(data)
