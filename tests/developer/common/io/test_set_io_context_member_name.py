import string

import pytest
import pytest_cases

from src.common import io
from tests.developer.common.io import helpers

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


@pytest_cases.parametrize(context_member=(list(io.IOContextMember)))
def test_set_name_correclty(
    valid_io_manager: io.IOManager,
    context_member: io.IOContextMember,
) -> None:
    # GIVEN an IOManager with valid IOContext, a context member and a valid name
    another_valid_name = ANOTHER_VALID_NAME_TEMPLATE.substitute(
        member_name=context_member
    )

    # WHEN setting the name
    valid_io_manager.set_context_member_name(context_member, another_valid_name)

    # THEN the name is correctly set
    io_context = valid_io_manager.get_io_context()
    output_name = io_context.get_context_member_name(context_member)
    assert another_valid_name == output_name


@pytest_cases.parametrize(context_member=(list(io.IOContextMember)))
@pytest_cases.case(id="")
def case_reset_depending_context(
    context_member: io.IOContextMember,
) -> tuple[io.IOContextMember, list[io.IOContextMember]]:
    match context_member:
        case io.IOContextMember.ONTOLOGY:
            dependent_members = [
                io.IOContextMember.MODEL,
                io.IOContextMember.INSTANTIATION,
            ]
        case io.IOContextMember.MODEL:
            dependent_members = [io.IOContextMember.INSTANTIATION]
        case io.IOContextMember.INSTANTIATION:
            dependent_members = []

    return context_member, dependent_members


@pytest_cases.parametrize_with_cases(
    "context_member, dependent_members", cases=case_reset_depending_context
)
@pytest.mark.it("reset depending IOContext attributes when name is changed")
def test_reset_depending_context(
    valid_io_manager: io.IOManager,
    context_member: io.IOContextMember,
    dependent_members: list[io.IOContextMember],
) -> None:
    # GIVEN an IOManager with valid IOContext, a context member, a list of dependent
    #  members and a valid name
    another_valid_name = ANOTHER_VALID_NAME_TEMPLATE.substitute(
        member_name=context_member
    )

    # WHEN setting the name
    valid_io_manager.set_context_member_name(context_member, another_valid_name)

    # THEN the IOContext attributes that depend on the context member get reset
    output_io_context = valid_io_manager.get_io_context()
    for member in dependent_members:
        assert output_io_context.get_context_member_name(member) == ""


@pytest_cases.parametrize(context_member=(list(io.IOContextMember)))
def test_exception_on_invalid_name(
    valid_io_manager: io.IOManager,
    context_member: io.IOContextMember,
) -> None:
    # GIVEN an IOManager with valid IOContext, a context member, an invalid name and an error message
    invalid_name = "invalid_name"
    error_msg = f"Invalid {context_member} name: {invalid_name}"

    # WHEN setting the name
    # THEN a IOContextError is raised
    with pytest.raises(io.IOContextError, match=error_msg):
        valid_io_manager.set_context_member_name(context_member, invalid_name)


@pytest.fixture
def io_manager() -> io.IOManager:
    return io.IOManager()


@pytest_cases.parametrize(context_member=(list(io.IOContextMember)))
def test_exception_on_insufficient_context(
    io_manager: io.IOManager, context_member: io.IOContextMember
) -> None:
    # GIVEN an IOManager with default IOContext, a context member, a name
    #  and an error message
    name = "name"
    error_msg = "Insufficient IOContext to access data"

    # WHEN setting the name
    # THEN a IOStorageError is raised
    with pytest.raises(io.IOStorageError, match=error_msg):
        io_manager.set_context_member_name(context_member, name)
