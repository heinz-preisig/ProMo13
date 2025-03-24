import typing

import pytest
from conftest import FakeDataIO
from pytest_cases import case, fixture, parametrize, parametrize_with_cases

from src.common.corelib import Index, IndexMap, Variable, VariableMap
from src.common.io import IOBuilderError, IOContext, IOContextMember, IOManager

INDEX_DATA_1 = [
    {"identifier": "I_1", "label": "node"},
    {"identifier": "I_2"},
    {"identifier": "I_3", "label": "interface", "iri": "promo:interface"},
]
INDEX_DATA_2 = [
    {"identifier": "I_4"},
    {"identifier": "I_5"},
    {"identifier": "I_6"},
]

GOOD_DATA: list[dict[str, typing.Any]] = [
    {"identifier": "V_1", "label": "t", "doc": "time", "indices": []},
    {"identifier": "V_2", "label": "x", "doc": "position", "indices": ["I_3"]},
    {"identifier": "V_3", "label": "n", "doc": "moles", "indices": ["I_1", "I_2"]},
]

BAD_DATA_MISSING_REQUIRED = [
    {"label": "t", "doc": "time", "indices": []},
    {"identifier": "V_2", "label": "x", "doc": "position", "indices": ["I_3"]},
    {"identifier": "V_3", "label": "n", "doc": "moles", "indices": ["I_1", "I_2"]},
]

BAD_DATA_WRONG_TYPE = [
    {"identifier": "V_1", "label": "t", "doc": "time", "indices": []},
    {"identifier": "V_2", "label": "x", "doc": "position", "indices": ["I_3"]},
    {"identifier": 3, "label": "n", "doc": "moles", "indices": ["I_1", "I_2"]},
]

IDENTIFIER_KEY = "identifier"
INDICES_KEY = "indices"


def build_index_map(map_data: typing.Any) -> IndexMap:
    indices = {}
    for idx_data in map_data:
        new_index = Index(**idx_data)

        identifier = idx_data[IDENTIFIER_KEY]
        indices[identifier] = new_index

    return indices


def build_variable_map(map_data: typing.Any, indices: IndexMap) -> VariableMap:
    variables = {}
    for var_data in map_data:
        instanced_indices = [indices[idx] for idx in var_data[INDICES_KEY]]
        instanced_var_data = var_data | {INDICES_KEY: instanced_indices}
        new_var = Variable(**instanced_var_data)

        identifier = var_data[IDENTIFIER_KEY]
        variables[identifier] = new_var

    return variables


class CasesVariableBuilding:
    def valid_data_ok(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO
    ) -> tuple[IOManager, VariableMap]:
        index_map_data = INDEX_DATA_1
        variable_map_data = GOOD_DATA

        fake_data_io.set_index_data(index_map_data)
        fake_data_io.set_variable_data(variable_map_data)

        indices = build_index_map(index_map_data)
        expected_variables = build_variable_map(variable_map_data, indices)

        return fake_io_manager, expected_variables

    @parametrize(
        data=(BAD_DATA_MISSING_REQUIRED, BAD_DATA_WRONG_TYPE),
        ids=("missing required attribute", "wrong attribute type"),
    )
    @case(id="")
    def invalid_data(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO, data: typing.Any
    ) -> IOManager:
        fake_data_io.set_index_data(INDEX_DATA_1)
        fake_data_io.set_variable_data(data)

        return fake_io_manager


class TestVariableBuilding:
    @parametrize_with_cases(
        "manager, expected_map", cases=CasesVariableBuilding, prefix="valid"
    )
    def test_build_variable_map_ok(
        self, manager: IOManager, expected_map: VariableMap
    ) -> None:
        output_variable_map = manager.get_current_variable_map()

        assert expected_map == output_variable_map

    @parametrize_with_cases("manager", cases=CasesVariableBuilding, prefix="invalid")
    def test_exception_on_invalid_data(self, manager: IOManager) -> None:
        error_msg = "Corrupted Variable file"

        with pytest.raises(IOBuilderError, match=error_msg):
            manager.get_current_variable_map()
