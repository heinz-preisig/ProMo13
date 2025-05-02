import typing

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

        builder = self._get_core_map_builder(map_variant, io_context)
        data = self._data_controller.get_core_map_data(map_variant, io_context)

        self._core_maps[map_variant] = builder.build(data)

    def _get_core_map_builder(
        self, map_variant: corelib.CoreMapVariant, io_context: context.IOContext
    ) -> builders.CoreMapBuilder[typing.Any]:
        dependencies = self._build_core_map_dependencies(map_variant, io_context)

        return self._select_core_map_builder(map_variant, dependencies)

    def _build_core_map_dependencies(
        self, map_variant: corelib.CoreMapVariant, io_context: context.IOContext
    ) -> list[corelib.CoreMap]:
        dependencies = []
        for dependency_variant in CORE_MAPS_BUILD_DEPENDENCIES[map_variant]:
            self._build_core_map(io_context, dependency_variant)
            dependencies.append(self._core_maps[dependency_variant])

        return dependencies

    def _select_core_map_builder(
        self,
        map_variant: corelib.CoreMapVariant,
        dependencies: list[corelib.CoreMap],
    ) -> builders.CoreMapBuilder[typing.Any]:
        match map_variant:
            case corelib.CoreMapVariant.INDEX:
                return builders.IndexMapBuilder()
            case corelib.CoreMapVariant.VARIABLE:
                index_map = typing.cast(corelib.IndexMap, dependencies[0])
                return builders.VariableMapBuilder(index_map)
            case corelib.CoreMapVariant.EQUATION:
                variable_map = typing.cast(corelib.VariableMap, dependencies[0])
                return builders.EquationMapBuilder(variable_map)
