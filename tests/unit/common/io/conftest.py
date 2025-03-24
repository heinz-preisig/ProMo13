import typing

import pytest

from src.common.io import IOContext, IOContextMember, IOManager

DEFAULT_ONTOLOGY_NAME = "default"


class FakeDataIO:
    def __init__(self) -> None:
        self._index_data: dict[str, typing.Any] = {DEFAULT_ONTOLOGY_NAME: []}
        self._variable_data: dict[str, typing.Any] = {DEFAULT_ONTOLOGY_NAME: []}

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

    def set_index_data(
        self, data: typing.Any, ontology_name: str = DEFAULT_ONTOLOGY_NAME
    ) -> None:
        self._index_data[DEFAULT_ONTOLOGY_NAME] = data

    def get_index_data(self, context: IOContext) -> typing.Any:
        is_ontology_name_set = bool(context.ontology_name)
        if is_ontology_name_set:
            return self._index_data[context.ontology_name]

        return self._index_data[DEFAULT_ONTOLOGY_NAME]

    def set_variable_data(
        self, data: typing.Any, ontology_name: str = DEFAULT_ONTOLOGY_NAME
    ) -> None:
        self._variable_data[DEFAULT_ONTOLOGY_NAME] = data

    def get_variable_data(self, context: IOContext) -> typing.Any:
        is_ontology_name_set = bool(context.ontology_name)
        if is_ontology_name_set:
            return self._variable_data[context.ontology_name]

        return self._variable_data[DEFAULT_ONTOLOGY_NAME]


@pytest.fixture
def fake_data_io() -> FakeDataIO:
    return FakeDataIO()


@pytest.fixture
def fake_io_manager(fake_data_io: FakeDataIO) -> IOManager:
    return IOManager(fake_data_io)
