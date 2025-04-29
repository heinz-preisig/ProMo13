import string

import pytest

from src.common import io
from src.common.io import storage
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


def test_set_location_correctly(test_io_manager: io.IOManager) -> None:
    # GIVEN an IOManager and a valid repository location
    expected_location = VALID_REPOSITORY_LOCATION

    # WHEN setting the repository location
    test_io_manager.set_repository_location(expected_location)

    # THEN the repository location is correctly set
    ontology_context = test_io_manager.get_io_context()
    output_location = ontology_context.repository_location
    assert expected_location == output_location


@pytest.mark.it("reset other IOContext attributes when repository location is changed")
def test_reset_depending_context(
    valid_io_manager: io.IOManager,
) -> None:
    # GIVEN an IOManager with valid IOContext
    new_repo_location = ANOTHER_VALID_REPOSITORY_LOCATION
    expected_context = io.IOContext(new_repo_location)

    # WHEN setting the repository location
    valid_io_manager.set_repository_location(new_repo_location)

    # THEN the IOContext attributes that depend on the repository location get reset
    output_context = valid_io_manager.get_io_context()
    assert expected_context == output_context
