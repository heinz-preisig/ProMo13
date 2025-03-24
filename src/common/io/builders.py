import functools
import logging
import typing
from abc import ABC, abstractmethod

import cattrs

from src.common.corelib import Equation, Index, IndexMap, Variable, VariableMap

from . import exceptions

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")


def generate_strict_converter() -> cattrs.Converter:
    # Necessary to enforce type strictness in cattrs 24.1.2.
    # A better way is expected in future releases.
    c = cattrs.Converter()

    c.register_structure_hook(int, validate_type)
    c.register_structure_hook(float, validate_type)
    c.register_structure_hook(str, validate_type)
    c.register_structure_hook(bool, validate_type)

    return c


def validate_type(val: typing.Any, target_type: typing.Any) -> typing.Any:
    if not isinstance(val, target_type):
        raise ValueError(f"{val} is not a {target_type}")

    return val


class BaseMapBuilder(ABC, typing.Generic[T]):
    def __init__(self) -> None:
        self._corrupted_error_msg = "Corrupted file"
        self._item_type: type[T]
        self._converter = generate_strict_converter()

        self._register_extra_hooks()

    def _register_extra_hooks(self) -> None:
        pass

    def _clean_extra_hooks(self) -> None:
        pass

    @abstractmethod
    def _pre_process_data(self, data: typing.Any) -> typing.Any:
        pass

    def build(self, map_data: typing.Any) -> dict[str, T]:
        self._register_extra_hooks()
        new_map = self._build_map(map_data)
        self._clean_extra_hooks()

        return new_map

    def _build_map(self, map_data: typing.Any) -> dict[str, T]:
        ID_KEY = "identifier"
        new_map = {}
        for raw_item_data in map_data:
            item_data = self._pre_process_data(raw_item_data)
            new_item = self._build_new_map_item(item_data)
            identifier = item_data[ID_KEY]
            new_map[identifier] = new_item

        return new_map

    def _build_new_map_item(self, item_data: dict[str, typing.Any]) -> T:
        try:
            return self._converter.structure(item_data, self._item_type)
        except cattrs.BaseValidationError as err:
            logger.error(err)
            raise exceptions.IOBuilderError(self._corrupted_error_msg) from err


class IndexMapBuilder(BaseMapBuilder[Index]):
    def __init__(self) -> None:
        super().__init__()

        self._corrupted_error_msg = "Corrupted Index file"
        self._item_type = Index

    def _pre_process_data(self, data: typing.Any) -> typing.Any:
        return data


class VariableMapBuilder(BaseMapBuilder[Variable]):
    def __init__(self, indices: IndexMap):
        self._indices = indices

        super().__init__()

        self._corrupted_error_msg = "Corrupted Variable file"
        self._item_type = Variable

    def _register_extra_hooks(self) -> None:
        self._converter.register_structure_hook(Index, validate_type)

    def _clean_extra_hooks(self) -> None:
        self._converter.register_structure_hook(Index, cattrs.structure)

    def _pre_process_data(self, data: typing.Any) -> typing.Any:
        INDICES_KEY = "indices"
        instanced_indices = [self._indices[idx_id] for idx_id in data[INDICES_KEY]]
        return data | {INDICES_KEY: instanced_indices}


class EquationMapBuilder(BaseMapBuilder[Equation]):
    def __init__(self, variables: VariableMap):
        self._variables = variables

        super().__init__()

        self._corrupted_error_msg = "Corrupted Equation data"
        self._item_type = Equation

    def _register_extra_hooks(self) -> None:
        self._converter.register_structure_hook(Variable, validate_type)

    def _clean_extra_hooks(self) -> None:
        self._converter.register_structure_hook(Variable, cattrs.structure)

    def _pre_process_data(self, data: typing.Any) -> typing.Any:
        VARIABLES_KEY = "variables"

        instanced_variables = [
            self._variables[var_id] for var_id in data[VARIABLES_KEY]
        ]

        instanced_dict = {VARIABLES_KEY: instanced_variables}

        return data | instanced_dict
