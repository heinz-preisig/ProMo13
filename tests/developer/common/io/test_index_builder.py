import typing

import pytest
from pytest_cases import case, fixture, parametrize, parametrize_with_cases

from src.common.corelib import Index, IndexMap
from src.common.io import IOBuilderError, IOContext, IOContextMember, IOManager
from tests.developer.common.io.helpers import FakeDataIO, build_index_map

GOOD_DATA1 = [
    {"identifier": "I_1", "label": "node"},
    {"identifier": "I_2"},
    {"identifier": "I_3", "label": "interface", "iri": "promo:interface"},
]

GOOD_DATA2 = [
    {"identifier": "I_1", "label": "node"},
    {"identifier": "I_2", "label": "random_label"},
    {"identifier": "I_3", "label": "interface", "iri": "promo:interface"},
]

BAD_DATA_MISSING_REQUIRED = [
    {"label": "node"},
    {"identifier": "I_2"},
    {"identifier": "I_3", "label": "interface", "iri": "promo:interface"},
]

BAD_DATA_WRONG_TYPE = [
    {"identifier": "I_1", "label": "node"},
    {"identifier": "I_2"},
    {"identifier": "I_3", "label": 131, "iri": "promo:interface"},
]


class CasesIndexBuilding:
    def valid_data_ok(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO
    ) -> tuple[IOManager, IndexMap]:
        map_data = GOOD_DATA1
        ontology_name = "ontologyOK"

        fake_data_io.set_index_data(map_data, ontology_name)

        expected_index_map = build_index_map(map_data)

        fake_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

        return fake_io_manager, expected_index_map

    def valid_context_change(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO
    ) -> tuple[IOManager, IndexMap]:
        initial_index_data = GOOD_DATA1
        final_index_data = GOOD_DATA2
        ontology_name1 = "VALID_ONTOLOGY"
        ontology_name2 = "ontologyOK"

        fake_data_io.set_index_data(initial_index_data, ontology_name1)
        fake_data_io.set_index_data(final_index_data, ontology_name2)

        expected_index_map = build_index_map(final_index_data)

        fake_io_manager.set_context_member_name(
            IOContextMember.ONTOLOGY, ontology_name1
        )
        fake_io_manager.get_current_index_map()
        fake_io_manager.set_context_member_name(
            IOContextMember.ONTOLOGY, ontology_name2
        )

        return fake_io_manager, expected_index_map

    @parametrize(
        data=(BAD_DATA_MISSING_REQUIRED, BAD_DATA_WRONG_TYPE),
        ids=("missing required attribute", "wrong attribute type"),
    )
    @case(id="")
    def invalid_data(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO, data: typing.Any
    ) -> IOManager:
        ontology_name = "ontologyOK"

        fake_data_io.set_index_data(data, ontology_name)

        fake_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

        return fake_io_manager


class TestIndexBuilding:
    @parametrize_with_cases(
        "manager, expected_map", cases=CasesIndexBuilding, prefix="valid"
    )
    def test_build_index_map_ok(
        self, manager: IOManager, expected_map: IndexMap
    ) -> None:
        output_index_map = manager.get_current_index_map()

        assert expected_map == output_index_map

    @parametrize_with_cases("manager", cases=CasesIndexBuilding, prefix="invalid")
    def test_exception_on_invalid_data(self, manager: IOManager) -> None:
        error_msg = "Corrupted Index file"

        with pytest.raises(IOBuilderError, match=error_msg):
            manager.get_current_index_map()
