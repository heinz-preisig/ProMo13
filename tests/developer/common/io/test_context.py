import dataclasses

import pytest
import pytest_cases

from src.common import io


@pytest.fixture
def io_manager() -> io.IOManager:
    return io.IOManager()


@pytest.fixture
def valid_io_manager(test_io_manager: io.IOManager) -> io.IOManager:
    REPO_LOCATION = "VALID_LOCATION"
    ONTOLOGY_NAME = "VALID_ONTOLOGY"
    MODEL_NAME = "VALID_MODEL"
    INSTANTIATION_NAME = "VALID_INSTANTIATION"

    test_io_manager.set_repository_location(REPO_LOCATION)
    test_io_manager.set_context_member_name(io.IOContextMember.ONTOLOGY, ONTOLOGY_NAME)
    test_io_manager.set_context_member_name(io.IOContextMember.MODEL, MODEL_NAME)
    test_io_manager.set_context_member_name(
        io.IOContextMember.INSTANTIATION, INSTANTIATION_NAME
    )

    return test_io_manager


class TestDefaultIOManagerConstructor:
    def test_empty_initial_context(self) -> None:
        io_manager = io.IOManager()

        ontology_context = io_manager.get_io_context()
        assert ontology_context == io.IOContext()


class TestGetOntologyContext:
    def test_returned_context_is_copy(self, io_manager: io.IOManager) -> None:
        ontology_context = io_manager.get_io_context()
        original_data = dataclasses.asdict(ontology_context)

        ontology_context.repository_location = "LocationModified"

        new_ontology_context = io_manager.get_io_context()
        data_after_modification = dataclasses.asdict(new_ontology_context)
        assert original_data == data_after_modification


class TestSetRepositoryLocation:
    def test_set_location_ok(self, test_io_manager: io.IOManager) -> None:
        manager = test_io_manager
        LOCATION = "VALID_LOCATION"

        manager.set_repository_location(LOCATION)

        new_ontology_context = manager.get_io_context()
        output = new_ontology_context.repository_location
        assert LOCATION == output

    def test_reset_depending_context(
        self,
        valid_io_manager: io.IOManager,
    ) -> None:
        manager = valid_io_manager
        new_repo_location = "NEW_REPO_LOCATION"
        expected_context = io.IOContext(new_repo_location)

        manager.set_repository_location(new_repo_location)

        output_context = manager.get_io_context()
        assert expected_context == output_context


@pytest_cases.parametrize(
    context_member=(
        io.IOContextMember.ONTOLOGY,
        io.IOContextMember.MODEL,
        io.IOContextMember.INSTANTIATION,
    ),
    ids=("ontology", "model", "instantiation"),
)
class CasesSetIOContextMemberName:
    @pytest_cases.case(id="")
    def invalid_name(
        self, context_member: io.IOContextMember
    ) -> tuple[io.IOContextMember, str]:
        INVALID_NAME = f"Invalid {context_member} name"

        return context_member, INVALID_NAME

    @pytest_cases.case(id="")
    def valid_name(
        self, context_member: io.IOContextMember
    ) -> tuple[io.IOContextMember, str]:
        VALID_NAME = f"{context_member}OK"

        return context_member, VALID_NAME

    @pytest_cases.case(id="")
    def cleared_members(
        self, context_member: io.IOContextMember
    ) -> tuple[io.IOContextMember, str, list[io.IOContextMember]]:
        VALID_NAME = f"{context_member}OK"

        match context_member:
            case io.IOContextMember.ONTOLOGY:
                cleared_members = [
                    io.IOContextMember.MODEL,
                    io.IOContextMember.INSTANTIATION,
                ]
            case io.IOContextMember.MODEL:
                cleared_members = [io.IOContextMember.INSTANTIATION]
            case io.IOContextMember.INSTANTIATION:
                cleared_members = []

        return context_member, VALID_NAME, cleared_members


class TestSetIOContextMemberName:
    @pytest_cases.parametrize_with_cases(
        "context_member, invalid_name",
        cases=CasesSetIOContextMemberName,
        prefix="invalid",
    )
    def test_exception_on_invalid_name(
        self,
        valid_io_manager: io.IOManager,
        context_member: io.IOContextMember,
        invalid_name: str,
    ) -> None:
        manager = valid_io_manager

        with pytest.raises(
            io.IOContextError,
            match=f"Invalid {context_member} name: {invalid_name}",
        ):
            manager.set_context_member_name(context_member, invalid_name)

    @pytest_cases.parametrize_with_cases(
        "context_member, valid_name",
        cases=CasesSetIOContextMemberName,
        prefix="valid",
    )
    def test_set_name_ok(
        self,
        valid_io_manager: io.IOManager,
        context_member: io.IOContextMember,
        valid_name: str,
    ) -> None:
        manager = valid_io_manager

        manager.set_context_member_name(context_member, valid_name)

        ontology_context = manager.get_io_context()
        output = ontology_context.get_context_member_name(context_member)
        assert valid_name == output

    @pytest_cases.parametrize_with_cases(
        "context_member, valid_name, cleared_members",
        cases=CasesSetIOContextMemberName,
        prefix="cleared",
    )
    def test_reset_depending_context(
        self,
        valid_io_manager: io.IOManager,
        context_member: io.IOContextMember,
        valid_name: str,
        cleared_members: list[io.IOContextMember],
    ) -> None:
        manager = valid_io_manager

        manager.set_context_member_name(context_member, valid_name)

        output = manager.get_io_context()
        for member in cleared_members:
            assert output.get_context_member_name(member) == ""

    @pytest_cases.parametrize_with_cases(
        "context_member, valid_name",
        cases=CasesSetIOContextMemberName,
        prefix="valid",
    )
    def test_set_name_on_incomplete_context(
        self,
        io_manager: io.IOManager,
        context_member: io.IOContextMember,
        valid_name: str,
    ) -> None:
        error_msg = "Insufficient IOContext to access data"

        with pytest.raises(io.IOStorageError, match=error_msg):
            io_manager.set_context_member_name(context_member, valid_name)
