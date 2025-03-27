import pathlib

import pytest
import pytest_cases

from src.common import io
from src.common.io import storage

EQUATION_DATA = [
    {"identifier": "E_1", "variables": ["V_1", "V_2", "V_3"]},
    {"identifier": "E_6", "variables": ["V_1", "V_2", "V_5", "V_6"]},
    {"identifier": "E_2", "variables": ["V_4", "V_5", "V_6"]},
    {"identifier": "E_3", "variables": ["V_5", "V_1", "V_7"]},
    {"identifier": "E_4", "variables": ["V_8", "V_9", "V_10"]},
    {"identifier": "E_5", "variables": ["V_9", "V_4", "V_11", "V_12"]},
]


ACCESS_ERROR = "Can not access equation data"
CORRUPTED_ERROR = "Corrupted equation data"


@pytest_cases.case(id="")
@pytest_cases.parametrize(
    "name_id, error_msg",
    [("1", ACCESS_ERROR), ("2", CORRUPTED_ERROR), ("3", CORRUPTED_ERROR)],
    ids=("missing file", "invalid json", "invalid json schema"),
)
def case_equation_file_problem(
    ok_context: io.IOContext, name_id: str, error_msg: str
) -> tuple[io.IOContext, str]:
    ONTOLOGY_NAME = f"ontology{name_id}"
    ok_context.ontology_name = ONTOLOGY_NAME

    return ok_context, error_msg


class TestVariableReading:
    def test_equation_reading_ok(
        self, test_storage: storage.GenericStorage, ok_context: io.IOContext
    ) -> None:
        expected_data = EQUATION_DATA

        output_data = test_storage.get_equation_data(ok_context)

        assert expected_data == output_data

    @pytest_cases.parametrize_with_cases("test_context, error_msg", cases=".")
    def test_exception_on_missing_equation_file(
        self,
        test_storage: storage.GenericStorage,
        test_context: io.IOContext,
        error_msg: str,
    ) -> None:
        with pytest.raises(io.DataIOError, match=error_msg):
            test_storage.get_equation_data(test_context)
