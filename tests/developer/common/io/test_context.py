import dataclasses
import string

import pytest
import pytest_cases

from src.common import io
from tests.developer.common.io import helpers


@pytest.fixture
def io_manager() -> io.IOManager:
    return io.IOManager()


VALID_NAME_TEMPLATE = string.Template("valid_${member_name}_name")
ANOTHER_VALID_NAME_TEMPLATE = string.Template("another_valid_${member_name}_name")
VALID_REPOSITORY_LOCATION = "valid_repository_location"
ANOTHER_VALID_REPOSITORY_LOCATION = "another_valid_repository_location"


@pytest.fixture
def test_storage(fake_storage: helpers.FakeStorage) -> helpers.FakeStorage:
    for context_member in io.IOContextMember:
        valid_name = VALID_NAME_TEMPLATE.substitute(member_name=context_member)
        another_valid_name = ANOTHER_VALID_NAME_TEMPLATE.substitute(
            member_name=context_member
        )

        fake_storage.set_context_member_options(
            context_member, [valid_name, another_valid_name]
        )

    return fake_storage


@pytest.fixture
def test_io_manager(test_storage: helpers.FakeStorage) -> io.IOManager:
    return io.IOManager(test_storage)


@pytest.fixture
def valid_io_manager(test_io_manager: io.IOManager) -> io.IOManager:
    test_io_manager.set_repository_location(VALID_REPOSITORY_LOCATION)

    for context_member in io.IOContextMember:
        valid_name = VALID_NAME_TEMPLATE.substitute(member_name=context_member)
        test_io_manager.set_context_member_name(context_member, valid_name)

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
        expected_location = VALID_REPOSITORY_LOCATION

        test_io_manager.set_repository_location(expected_location)

        ontology_context = test_io_manager.get_io_context()
        output_location = ontology_context.repository_location
        assert expected_location == output_location

    @pytest.mark.it(
        "reset other IOContext attributes when repository location is changed"
    )
    def test_reset_depending_context(
        self,
        valid_io_manager: io.IOManager,
    ) -> None:
        new_repo_location = ANOTHER_VALID_REPOSITORY_LOCATION
        expected_context = io.IOContext(new_repo_location)

        valid_io_manager.set_repository_location(new_repo_location)

        output_context = valid_io_manager.get_io_context()
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
    ) -> tuple[io.IOContextMember, str, str]:
        invalid_context_member_name = f"Invalid{context_member}name"
        error_msg = f"Invalid {context_member} name: {invalid_context_member_name}"

        return context_member, invalid_context_member_name, error_msg

    @pytest_cases.case(id="")
    def valid_name(
        self, context_member: io.IOContextMember
    ) -> tuple[io.IOContextMember, str]:
        another_valid_name = ANOTHER_VALID_NAME_TEMPLATE.substitute(
            member_name=context_member
        )

        return context_member, another_valid_name

    @pytest_cases.case(id="")
    def cleared_members(
        self, context_member: io.IOContextMember
    ) -> tuple[
        io.IOContextMember, str, dict[io.IOContextMember, list[io.IOContextMember]]
    ]:
        another_valid_name = ANOTHER_VALID_NAME_TEMPLATE.substitute(
            member_name=context_member
        )

        resetted_members = {
            io.IOContextMember.ONTOLOGY: [
                io.IOContextMember.MODEL,
                io.IOContextMember.INSTANTIATION,
            ],
            io.IOContextMember.MODEL: [io.IOContextMember.INSTANTIATION],
            io.IOContextMember.INSTANTIATION: [],
        }

        return context_member, another_valid_name, resetted_members


class TestSetIOContextMemberName:
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
        "context_member, invalid_name, error_msg",
        cases=CasesSetIOContextMemberName,
        prefix="invalid",
    )
    def test_exception_on_invalid_name(
        self,
        valid_io_manager: io.IOManager,
        context_member: io.IOContextMember,
        invalid_name: str,
        error_msg: str,
    ) -> None:
        manager = valid_io_manager

        with pytest.raises(io.IOContextError, match=error_msg):
            manager.set_context_member_name(context_member, invalid_name)

    @pytest_cases.parametrize_with_cases(
        "context_member, valid_name, resetted_members",
        cases=CasesSetIOContextMemberName,
        prefix="cleared",
    )
    @pytest.mark.it("reset depending IOContext attributes when name is changed")
    def test_reset_depending_context(
        self,
        valid_io_manager: io.IOManager,
        context_member: io.IOContextMember,
        valid_name: str,
        resetted_members: dict[io.IOContextMember, list[io.IOContextMember]],
    ) -> None:
        valid_io_manager.set_context_member_name(context_member, valid_name)

        output_io_context = valid_io_manager.get_io_context()
        for member in resetted_members[context_member]:
            assert output_io_context.get_context_member_name(member) == ""

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
