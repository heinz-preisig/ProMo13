import dataclasses

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from src.common.io import (
    IOContext,
    IOContextError,
    IOContextMember,
    IOManager,
)


@pytest.fixture
def io_manager() -> IOManager:
    return IOManager()


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


@pytest.fixture
def fake_io_manager() -> IOManager:
    fake_data_io = FakeDataIO()
    return IOManager(data_io=fake_data_io)


@pytest.fixture
def valid_io_manager(fake_io_manager: IOManager) -> IOManager:
    REPO_LOCATION = "VALID_LOCATION"
    ONTOLOGY_NAME = "VALID_ONTOLOGY"
    MODEL_NAME = "VALID_MODEL"
    INSTANTIATION_NAME = "VALID_INSTANTIATION"

    fake_io_manager.set_repository_location(REPO_LOCATION)
    fake_io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)
    fake_io_manager.set_context_member_name(IOContextMember.MODEL, MODEL_NAME)
    fake_io_manager.set_context_member_name(
        IOContextMember.INSTANTIATION, INSTANTIATION_NAME
    )

    return fake_io_manager


class TestDefaultIOManagerConstructor:
    def test_empty_initial_context(self) -> None:
        io_manager = IOManager()

        ontology_context = io_manager.get_io_context()
        assert ontology_context == IOContext()


class TestGetOntologyContext:
    def test_returned_context_is_copy(self, io_manager: IOManager) -> None:
        ontology_context = io_manager.get_io_context()
        ontology_context.repository_location = "PathModified"

        ontology_context = io_manager.get_io_context()

        assert ontology_context.repository_location == ""


class TestSetRepositoryLocation:
    def test_set_location_ok(self, fake_io_manager: IOManager) -> None:
        manager = fake_io_manager
        LOCATION = "VALID_LOCATION"

        manager.set_repository_location(LOCATION)

        new_ontology_context = manager.get_io_context()
        output = new_ontology_context.repository_location
        assert LOCATION == output

    def test_reset_depending_context(
        self,
        valid_io_manager: IOManager,
    ) -> None:
        manager = valid_io_manager
        new_repo_location = "NEW_REPO_LOCATION"
        expected_context = IOContext(new_repo_location)

        manager.set_repository_location(new_repo_location)

        output_context = manager.get_io_context()
        assert expected_context == output_context


@parametrize(
    context_member=(
        IOContextMember.ONTOLOGY,
        IOContextMember.MODEL,
        IOContextMember.INSTANTIATION,
    ),
    ids=("ontology", "model", "instantiation"),
)
class CasesSetIOContextMemberName:
    @case(id="")
    def invalid_name(
        self, context_member: IOContextMember
    ) -> tuple[IOContextMember, str]:
        INVALID_NAME = f"Invalid {context_member} name"

        return context_member, INVALID_NAME

    @case(id="")
    def valid_name(
        self, context_member: IOContextMember
    ) -> tuple[IOContextMember, str]:
        VALID_NAME = f"{context_member}OK"

        return context_member, VALID_NAME

    @case(id="")
    def cleared_members(
        self, context_member: IOContextMember
    ) -> tuple[IOContextMember, str, list[IOContextMember]]:
        VALID_NAME = f"{context_member}OK"

        match context_member:
            case IOContextMember.ONTOLOGY:
                cleared_members = [IOContextMember.MODEL, IOContextMember.INSTANTIATION]
            case IOContextMember.MODEL:
                cleared_members = [IOContextMember.INSTANTIATION]
            case IOContextMember.INSTANTIATION:
                cleared_members = []

        return context_member, VALID_NAME, cleared_members


class TestSetIOContextMemberName:
    @parametrize_with_cases(
        "context_member, invalid_name",
        cases=CasesSetIOContextMemberName,
        prefix="invalid",
    )
    def test_exception_on_invalid_name(
        self,
        valid_io_manager: IOManager,
        context_member: IOContextMember,
        invalid_name: str,
    ) -> None:
        manager = valid_io_manager

        with pytest.raises(
            IOContextError,
            match=f"Invalid {context_member} name: {invalid_name}",
        ):
            manager.set_context_member_name(context_member, invalid_name)

    @parametrize_with_cases(
        "context_member, valid_name",
        cases=CasesSetIOContextMemberName,
        prefix="valid",
    )
    def test_set_name_ok(
        self,
        valid_io_manager: IOManager,
        context_member: IOContextMember,
        valid_name: str,
    ) -> None:
        manager = valid_io_manager

        manager.set_context_member_name(context_member, valid_name)

        ontology_context = manager.get_io_context()
        output = ontology_context.get_context_member_name(context_member)
        assert valid_name == output

    @parametrize_with_cases(
        "context_member, valid_name, cleared_members",
        cases=CasesSetIOContextMemberName,
        prefix="cleared",
    )
    def test_reset_depending_context(
        self,
        valid_io_manager: IOManager,
        context_member: IOContextMember,
        valid_name: str,
        cleared_members: list[IOContextMember],
    ) -> None:
        manager = valid_io_manager

        manager.set_context_member_name(context_member, valid_name)

        output = manager.get_io_context()
        for member in cleared_members:
            assert output.get_context_member_name(member) == ""

    @parametrize_with_cases(
        "context_member, valid_name",
        cases=CasesSetIOContextMemberName,
        prefix="valid",
    )
    def test_set_name_on_incomplete_context(
        self,
        io_manager: IOManager,
        context_member: IOContextMember,
        valid_name: str,
    ) -> None:
        context = io_manager.get_io_context()
        error_msg = "Insufficient data in IOContext"

        with pytest.raises(IOContextError, match=error_msg):
            io_manager.set_context_member_name(context_member, valid_name)
