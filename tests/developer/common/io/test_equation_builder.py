import typing

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from src.common.corelib import EquationMap
from src.common.io import IOBuilderError, IOContextMember, IOManager
from tests.developer.common.io.helpers import (
    FakeStorage,
    build_equation_map,
    build_index_map,
    build_variable_map,
)

INDEX_DATA = [
    {"identifier": "I_1", "label": "node"},
    {"identifier": "I_2"},
    {"identifier": "I_3", "label": "interface", "iri": "promo:interface"},
]

VARIABLE_DATA = [
    {"identifier": "V_1", "label": "t", "doc": "time", "indices": []},
    {"identifier": "V_2", "label": "x", "doc": "position", "indices": ["I_3"]},
    {"identifier": "V_3", "label": "n", "doc": "moles", "indices": ["I_1", "I_2"]},
]

EQUATION_DATA = [
    {"identifier": "E_1", "variables": ["V_1", "V_2"]},
    {"identifier": "E_2", "variables": ["V_2", "V_1", "V_3"]},
    {"identifier": "E_3", "variables": ["V_3", "V_1", "V_2"]},
]

EQUATION_DATA2 = [
    {"identifier": "E_1", "variables": ["V_1", "V_2"]},
    {"identifier": "E_2", "variables": ["V_2", "V_1", "V_3"]},
    {"identifier": "E_3", "variables": ["V_3", "V_1", "V_2"]},
]

BAD_DATA_MISSING_REQUIRED = [
    {"variables": ["V_1", "V_2"]},
    {"identifier": "E_2", "variables": ["V_2", "V_1", "V_3"]},
    {"identifier": "E_3", "variables": ["V_3", "V_1", "V_2"]},
]

BAD_DATA_WRONG_TYPE = [
    {"identifier": 1, "variables": ["V_1", "V_2"]},
    {"identifier": "E_2", "variables": ["V_2", "V_1", "V_3"]},
    {"identifier": "E_3", "variables": ["V_3", "V_1", "V_2"]},
]


class CasesEquationBuilding:
    def valid_data_ok(
        self, fake_io_manager: IOManager, fake_storage: FakeStorage
    ) -> tuple[IOManager, EquationMap]:
        ontology_name = "ontologyOK"

        self._setup_fake_data(
            fake_storage, INDEX_DATA, VARIABLE_DATA, EQUATION_DATA, ontology_name
        )

        fake_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

        indices = build_index_map(INDEX_DATA)
        variables = build_variable_map(VARIABLE_DATA, indices)
        expected_equations = build_equation_map(EQUATION_DATA, variables)

        return fake_io_manager, expected_equations

    def valid_context_change(
        self, fake_io_manager: IOManager, fake_storage: FakeStorage
    ) -> tuple[IOManager, EquationMap]:
        ontology_name1 = "ontologyOK"
        ontology_name2 = "VALID_ONTOLOGY"

        self._setup_fake_data(
            fake_storage, INDEX_DATA, VARIABLE_DATA, EQUATION_DATA, ontology_name1
        )

        self._setup_fake_data(
            fake_storage, INDEX_DATA, VARIABLE_DATA, EQUATION_DATA2, ontology_name2
        )

        indices = build_index_map(INDEX_DATA)
        variables = build_variable_map(VARIABLE_DATA, indices)
        expected_equations = build_equation_map(EQUATION_DATA2, variables)

        fake_io_manager.set_context_member_name(
            IOContextMember.ONTOLOGY, ontology_name1
        )
        fake_io_manager.get_current_equation_map()
        fake_io_manager.set_context_member_name(
            IOContextMember.ONTOLOGY, ontology_name2
        )

        return fake_io_manager, expected_equations

    @parametrize(
        data=(BAD_DATA_MISSING_REQUIRED, BAD_DATA_WRONG_TYPE),
        ids=("missing required attribute", "wrong attribute type"),
    )
    @case(id="")
    def invalid_data(
        self, fake_io_manager: IOManager, fake_storage: FakeStorage, data: typing.Any
    ) -> IOManager:
        ontology_name = "ontologyOK"

        self._setup_fake_data(
            fake_storage, INDEX_DATA, VARIABLE_DATA, data, ontology_name
        )

        fake_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

        return fake_io_manager

    def _setup_fake_data(
        self,
        fake: FakeStorage,
        index_map_data: typing.Any,
        variable_map_data: typing.Any,
        equation_map_data: typing.Any,
        ontology_name: str,
    ) -> None:
        fake.set_index_data(index_map_data, ontology_name)
        fake.set_variable_data(variable_map_data, ontology_name)
        fake.set_equation_data(equation_map_data, ontology_name)


class TestEquationBuilding:
    @parametrize_with_cases(
        "manager, expected_map", cases=CasesEquationBuilding, prefix="valid"
    )
    def test_build_variable_map_ok(
        self, manager: IOManager, expected_map: EquationMap
    ) -> None:
        output_equation_map = manager.get_current_equation_map()

        assert expected_map.keys() == output_equation_map.keys()
        for key in expected_map:
            expected_equation = expected_map[key]
            output_equation = output_equation_map[key]
            assert expected_equation == output_equation

    @parametrize_with_cases("manager", cases=CasesEquationBuilding, prefix="invalid")
    def test_exception_on_invalid_data(self, manager: IOManager) -> None:
        error_msg = "Corrupted Equation data"

        with pytest.raises(IOBuilderError, match=error_msg):
            manager.get_current_equation_map()
