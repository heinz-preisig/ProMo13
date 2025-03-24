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

        try:
            for idx_data in data:
                new_index = self._strict_converter.structure(idx_data, Index)
                new_index_map[new_index.identifier] = new_index
        except cattrs.BaseValidationError as err:
            logger.error(err)
            raise exceptions.IOBuilderError("Corrupted Index file") from err

        self.indices = new_index_map

    def build_variable_map(self, data: typing.Any) -> None:
        new_variable_map = {}

        self._strict_converter.register_structure_hook(Index, validate_type)

        try:
            for var_data in data:
                var_indices_ids = var_data["indices"]
                var_indices = [self.indices[idx_id] for idx_id in var_indices_ids]
                new_var_data = var_data | {"indices": var_indices}
                new_variable = self._strict_converter.structure(new_var_data, Variable)
                new_variable_map[new_variable.identifier] = new_variable
        except cattrs.BaseValidationError as err:
            logger.error(err)
            raise exceptions.IOBuilderError("Corrupted Variable file") from err

        self._strict_converter.register_structure_hook(Index, cattrs.structure)

        self.variables = new_variable_map
