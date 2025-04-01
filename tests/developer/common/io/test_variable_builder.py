import typing

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from src.common.corelib import VariableMap
from src.common.io import IOBuilderError, IOContextMember, IOManager
from tests.developer.common.io.helpers import (
    FakeStorage,
    build_index_map,
    build_variable_map,
)

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
        self, test_io_manager: IOManager, fake_storage: FakeStorage
    ) -> tuple[IOManager, VariableMap]:
        index_map_data = INDEX_DATA
        variable_map_data = GOOD_DATA1
        ontology_name = "ontologyOK"

        self._setup_fake_data(
            fake_storage, index_map_data, variable_map_data, ontology_name
        )

        test_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

        indices = build_index_map(index_map_data)
        expected_variables = build_variable_map(variable_map_data, indices)

        return test_io_manager, expected_variables

    def valid_context_change(
        self, test_io_manager: IOManager, fake_storage: FakeStorage
    ) -> tuple[IOManager, VariableMap]:
        index_map_data = INDEX_DATA
        initial_variable_map_data = GOOD_DATA1
        final_variable_map_data = GOOD_DATA2
        ontology_name1 = "ontologyOK"
        ontology_name2 = "VALID_ONTOLOGY"

        self._setup_fake_data(
            fake_storage, index_map_data, initial_variable_map_data, ontology_name1
        )
        self._setup_fake_data(
            fake_storage, index_map_data, final_variable_map_data, ontology_name2
        )

        indices = build_index_map(index_map_data)
        expected_variables = build_variable_map(final_variable_map_data, indices)

        test_io_manager.set_context_member_name(
            IOContextMember.ONTOLOGY, ontology_name1
        )
        test_io_manager.get_current_variable_map()
        test_io_manager.set_context_member_name(
            IOContextMember.ONTOLOGY, ontology_name2
        )

        return test_io_manager, expected_variables

    @parametrize(
        data=(BAD_DATA_MISSING_REQUIRED, BAD_DATA_WRONG_TYPE),
        ids=("missing required attribute", "wrong attribute type"),
    )
    @case(id="")
    def invalid_data(
        self, test_io_manager: IOManager, fake_storage: FakeStorage, data: typing.Any
    ) -> IOManager:
        index_map_data = INDEX_DATA
        variable_map_data = data
        ontology_name = "ontologyOK"

        self._setup_fake_data(
            fake_storage, index_map_data, variable_map_data, ontology_name
        )

        test_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

        return test_io_manager

    def _setup_fake_data(
        self,
        fake: FakeStorage,
        index_map_data: typing.Any,
        variable_map_data: typing.Any,
        ontology_name: str,
    ) -> None:
        fake.set_index_data(index_map_data, ontology_name)
        fake.set_variable_data(variable_map_data, ontology_name)


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
