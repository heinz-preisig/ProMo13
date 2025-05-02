import json
import pathlib
import string
import typing

import pytest
import pytest_cases

from src.common import corelib, io
from src.common.io import storage

ACCESS_ERROR = string.Template("Can not access $map_variant data")
CORRUPTED_ERROR = string.Template("Corrupted $map_variant data")


@pytest.fixture(scope="module")
def data_dir_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "test_data"


@pytest.fixture(scope="module")
def expected_data_dict(data_dir_path: pathlib.Path) -> dict[str, typing.Any]:
    data_file_path = data_dir_path / "data.json"
    with data_file_path.open() as f:
        data: dict[str, typing.Any] = json.load(f)

    return data


@pytest_cases.case(id="")
@pytest_cases.parametrize(
    "name_id, error_msg_template",
    [("1", ACCESS_ERROR), ("2", CORRUPTED_ERROR), ("3", CORRUPTED_ERROR)],
    ids=[
        f"|error: {error_type}|"
        for error_type in ["missing file", "invalid json", "invalid json schema"]
    ],
)
def case_index_file_problem(
    ok_context: io.IOContext, name_id: str, error_msg_template: string.Template
) -> tuple[io.IOContext, string.Template]:
    ONTOLOGY_NAME = f"ontology{name_id}"
    ok_context.ontology_name = ONTOLOGY_NAME

    return ok_context, error_msg_template


@pytest_cases.parametrize(
    map_variant=list(corelib.CoreMapVariant),
    ids=[f"|map_variant: {map_variant}|" for map_variant in corelib.CoreMapVariant],
)
def test_get_core_map_data_correctly(
    test_storage: storage.GenericStorage,
    ok_context: io.IOContext,
    map_variant: corelib.CoreMapVariant,
    expected_data_dict: dict[str, typing.Any],
) -> None:
    # GIVEN a storage instance,
    # an IOContext pointing to valid data,
    # a map_variant
    # and the expected map data,
    expected_data = expected_data_dict[map_variant]

    # WHEN retrieving the map data
    output_data = test_storage.get_core_map_data(map_variant, ok_context)

    # THEN the output data should match the expected data
    assert expected_data == output_data


@pytest_cases.parametrize_with_cases(
    "test_context, error_msg_template", cases=case_index_file_problem
)
@pytest_cases.parametrize(
    map_variant=list(corelib.CoreMapVariant),
    ids=[f"|map_variant: {map_variant}|" for map_variant in corelib.CoreMapVariant],
)
def test_exception_on_problem_with_data(
    test_storage: storage.GenericStorage,
    test_context: io.IOContext,
    map_variant: corelib.CoreMapVariant,
    error_msg_template: string.Template,
) -> None:
    # GIVEN a storage instance,
    # an IOContext pointing to a file with a problem,
    # a map_variant,
    # and an error message
    error_message = error_msg_template.substitute(map_variant=map_variant)

    # WHEN retrieving the map data
    # THEN the expected error message should be raised
    with pytest.raises(io.IOStorageError, match=error_message):
        test_storage.get_core_map_data(map_variant, test_context)


@pytest.fixture
def context_with_no_ontology_name() -> io.IOContext:
    context = io.IOContext()
    context.ontology_name = ""
    return context


@pytest_cases.parametrize(map_variant=list(corelib.CoreMapVariant))
def test_exception_on_insufficient_io_context(
    test_storage: storage.GenericStorage,
    context_with_no_ontology_name: io.IOContext,
    map_variant: corelib.CoreMapVariant,
) -> None:
    # GIVEN a storage instance,
    # an IOContext without an ontology name,
    # a map_variant
    # and an error message
    error_message = "Insufficient IOContext to access data"

    # WHEN retrieving the map data
    # THEN the expected error message should be raised
    with pytest.raises(io.IOStorageError, match=error_message):
        test_storage.get_core_map_data(map_variant, context_with_no_ontology_name)
