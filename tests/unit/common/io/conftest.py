import typing

import pytest

from src.common.io import IOContext, IOContextMember, IOManager


class FakeDataIO:
    def validate_repository_location(self, location: str) -> None:
        pass

    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        match context_member:
            case IOContextMember.ONTOLOGY:
                return ["VALID_ONTOLOGY", "ontologyOK"]
            case IOContextMember.MODEL:
                return ["VALID_MODEL", "modelOK"]
            case IOContextMember.INSTANTIATION:
                return ["VALID_INSTANTIATION", "instantiationOK"]

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
