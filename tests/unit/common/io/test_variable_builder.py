import typing

import pytest
from conftest import FakeDataIO, build_index_map, build_variable_map
from pytest_cases import case, parametrize, parametrize_with_cases

from src.common.corelib import VariableMap
from src.common.io import IOBuilderError, IOContextMember, IOManager

INDEX_DATA = [
    {"identifier": "I_1", "label": "node"},
    {"identifier": "I_2"},
    {"identifier": "I_3", "label": "interface", "iri": "promo:interface"},
]

GOOD_DATA1 = [
    {"identifier": "V_1", "label": "t", "doc": "time", "indices": []},
    {"identifier": "V_2", "label": "x", "doc": "position", "indices": ["I_3"]},
    {"identifier": "V_3", "label": "n", "doc": "moles", "indices": ["I_1", "I_2"]},
]

GOOD_DATA2 = [
    {"identifier": "V_1", "label": "t", "doc": "time", "indices": []},
    {"identifier": "V_2", "label": "not x", "doc": "position", "indices": ["I_3"]},
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


class CasesVariableBuilding:
    def valid_data_ok(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO
    ) -> tuple[IOManager, VariableMap]:
        index_map_data = INDEX_DATA
        variable_map_data = GOOD_DATA1

        fake_data_io.set_index_data(index_map_data)
        fake_data_io.set_variable_data(variable_map_data)

        indices = build_index_map(index_map_data)
        expected_variables = build_variable_map(variable_map_data, indices)

        return fake_io_manager, expected_variables

    def valid_context_change(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO
    ) -> tuple[IOManager, VariableMap]:
        index_map_data = INDEX_DATA
        initial_variable_map_data = GOOD_DATA1
        final_variable_map_data = GOOD_DATA2
        ontology_name = "ontologyOK"

        fake_data_io.set_index_data(index_map_data)
        fake_data_io.set_index_data(index_map_data, ontology_name)
        fake_data_io.set_variable_data(initial_variable_map_data)
        fake_data_io.set_variable_data(final_variable_map_data, ontology_name)

        indices = build_index_map(index_map_data)
        expected_variables = build_variable_map(final_variable_map_data, indices)

        fake_io_manager.get_current_variable_map()
        fake_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

        return fake_io_manager, expected_variables

    @parametrize(
        data=(BAD_DATA_MISSING_REQUIRED, BAD_DATA_WRONG_TYPE),
        ids=("missing required attribute", "wrong attribute type"),
    )
    @case(id="")
    def invalid_data(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO, data: typing.Any
    ) -> IOManager:
        fake_data_io.set_index_data(INDEX_DATA)
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
