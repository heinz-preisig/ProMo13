import typing

import pytest
from pytest_cases import case, fixture, parametrize, parametrize_with_cases

from src.common.corelib import Index, IndexMap
from src.common.io import IOBuilderError, IOContext, IOContextMember, IOManager


class FakeDataIO:
    def validate_repository_location(self, location: str) -> None:
        pass

    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        return []

    def set_index_data(self, data: typing.Any) -> None:
        self._data = data

    def get_index_data(self, context: IOContext) -> typing.Any:
        return self._data


@pytest.fixture
def fake_data_io() -> FakeDataIO:
    return FakeDataIO()


@pytest.fixture
def fake_io_manager(fake_data_io: FakeDataIO) -> IOManager:
    return IOManager(fake_data_io)


GOOD_DATA = [
    {"identifier": "I_1", "label": "node"},
    {"identifier": "I_2"},
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
        data = GOOD_DATA
        fake_data_io.set_index_data(data)

        expected_index__map = {}
        for idx_data in data:
            identifier = idx_data["identifier"]
            new_index = Index(**idx_data)  # type: ignore
            expected_index__map[identifier] = new_index

        return fake_io_manager, expected_index__map

    @parametrize(
        data=(BAD_DATA_MISSING_REQUIRED, BAD_DATA_WRONG_TYPE),
        ids=("missing required attribute", "wrong attribute type"),
    )
    @case(id="")
    def invalid_data(
        self, fake_io_manager: IOManager, fake_data_io: FakeDataIO, data: typing.Any
    ) -> IOManager:
        fake_data_io.set_index_data(data)

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
