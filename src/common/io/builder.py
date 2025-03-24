import logging
import typing

import cattrs

from src.common.corelib import Index, IndexMap, Variable, VariableMap

from . import exceptions

logger = logging.Logger(__name__)


def validate_type(val: typing.Any, type: typing.Any) -> typing.Any:
    if not isinstance(val, type):
        raise ValueError(f"{val} is not a {type}")

    return val


class IOBuilder:
    def __init__(self) -> None:
        self._strict_converter = self._generate_strict_converter()
        self.indices: IndexMap = {}
        self.variables: VariableMap = {}

    def _generate_strict_converter(self) -> cattrs.Converter:
        # Necessary to enforce type strictness in cattrs 24.1.2.
        # A better way is expected in future releases.
        c = cattrs.Converter()

        c.register_structure_hook(int, validate_type)
        c.register_structure_hook(float, validate_type)
        c.register_structure_hook(str, validate_type)
        c.register_structure_hook(bool, validate_type)

        return c

    def build_index_map(self, data: typing.Any) -> None:
        new_index_map = {}
        for idx_data in data:
            new_index = self._build_new_index(idx_data)
            new_index_map[new_index.identifier] = new_index

        self.indices = new_index_map

    def _build_new_index(self, idx_data: dict[str, typing.Any]) -> Index:
        try:
            return self._strict_converter.structure(idx_data, Index)
        except cattrs.BaseValidationError as err:
            logger.error(err)
            raise exceptions.IOBuilderError("Corrupted Index file") from err

    def build_variable_map(self, data: typing.Any) -> None:
        self._strict_converter.register_structure_hook(Index, validate_type)

        new_variable_map = {}
        for var_data in data:
            new_var_data = self._replace_identifier_with_instances(var_data)
            new_variable = self._build_new_variable(new_var_data)
            new_variable_map[new_variable.identifier] = new_variable

        self.variables = new_variable_map

        self._strict_converter.register_structure_hook(Index, cattrs.structure)

    def _replace_identifier_with_instances(
        self, var_data: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        INDICES_KEY = "indices"
        var_indices_ids = var_data[INDICES_KEY]
        var_indices = [self.indices[idx_id] for idx_id in var_indices_ids]

        return var_data | {INDICES_KEY: var_indices}

    def _build_new_variable(self, var_data: dict[str, typing.Any]) -> Variable:
        try:
            return self._strict_converter.structure(var_data, Variable)
        except cattrs.BaseValidationError as err:
            logger.error(err)
            raise exceptions.IOBuilderError("Corrupted Variable file") from err
