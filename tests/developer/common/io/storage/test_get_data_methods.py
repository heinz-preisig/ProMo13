import json
import pathlib
import string
import typing

import pytest
import pytest_cases

from src.common import io
from src.common.io import storage

ACCESS_ERROR = string.Template("Can not access $data_name data")
CORRUPTED_ERROR = string.Template("Corrupted $data_name data")


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
    ids=("missing file", "invalid json", "invalid json schema"),
)
def case_index_file_problem(
    ok_context: io.IOContext, name_id: str, error_msg_template: string.Template
) -> tuple[io.IOContext, string.Template]:
    ONTOLOGY_NAME = f"ontology{name_id}"
    ok_context.ontology_name = ONTOLOGY_NAME

    return ok_context, error_msg_template


class TestGetDataMethods:
    @pytest_cases.parametrize(data_name=("index", "variable", "equation"))
    def test_get_data_ok(
        self,
        test_storage: storage.GenericStorage,
        ok_context: io.IOContext,
        expected_data_dict: dict[str, typing.Any],
        data_name: str,
    ) -> None:
        expected_data = expected_data_dict[data_name]
        tested_method_name = f"get_{data_name}_data"
        tested_method = getattr(test_storage, tested_method_name)

        output_data = tested_method(ok_context)

        assert expected_data == output_data

    @pytest_cases.parametrize(data_name=("index", "variable", "equation"))
    @pytest_cases.parametrize_with_cases("test_context, error_msg_template", cases=".")
    def test_exception_on_problem_with_data(
        self,
        test_storage: storage.GenericStorage,
        test_context: io.IOContext,
        error_msg_template: string.Template,
        data_name: str,
    ) -> None:
        error_msg = error_msg_template.substitute(data_name=data_name)
        tested_method_name = f"get_{data_name}_data"
        tested_method = getattr(test_storage, tested_method_name)

        with pytest.raises(io.IOStorageError, match=error_msg):
            tested_method(test_context)

    @pytest_cases.parametrize(data_name=("index", "variable", "equation"))
    def test_insufficient_io_context(
        self,
        ok_context: io.IOContext,
        test_storage: storage.GenericStorage,
        data_name: str,
    ) -> None:
        error_msg = "Insufficient IOContext to access data"
        tested_method_name = f"get_{data_name}_data"
        tested_method = getattr(test_storage, tested_method_name)
        ok_context.ontology_name = ""

        with pytest.raises(io.IOStorageError, match=error_msg):
            tested_method(ok_context)
