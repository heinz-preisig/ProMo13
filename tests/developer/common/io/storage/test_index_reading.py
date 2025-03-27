import pathlib

import pytest
import pytest_cases

from src.common import io
from src.common.io import storage

INDEX_DATA = [
    {"identifier": "I_1", "iri": "iri_I1", "label": "label_I1"},
    {"identifier": "I_2", "iri": "iri_I2", "label": "label_I2"},
    {"identifier": "I_3", "iri": "iri_I3", "label": "label_I3"},
]


ACCESS_ERROR = "Can not access index data"
CORRUPTED_ERROR = "Corrupted index data"


@pytest_cases.case(id="")
@pytest_cases.parametrize(
    "name_id, error_msg",
    [("1", ACCESS_ERROR), ("2", CORRUPTED_ERROR), ("3", CORRUPTED_ERROR)],
    ids=("missing file", "invalid json", "invalid json schema"),
)
def case_index_file_problem(
    ok_context: io.IOContext, name_id: str, error_msg: str
) -> tuple[io.IOContext, str]:
    ONTOLOGY_NAME = f"ontology{name_id}"
    ok_context.ontology_name = ONTOLOGY_NAME

    return ok_context, error_msg


class TestIndexReading:
    def test_index_reading_ok(
        self, test_storage: storage.GenericStorage, ok_context: io.IOContext
    ) -> None:
        expected_data = INDEX_DATA

        output_data = test_storage.get_index_data(ok_context)

        assert expected_data == output_data

    @pytest_cases.parametrize_with_cases("test_context, error_msg", cases=".")
    def test_exception_on_problem_with_index_file(
        self,
        test_storage: storage.GenericStorage,
        test_context: io.IOContext,
        error_msg: str,
    ) -> None:
        with pytest.raises(io.DataIOError, match=error_msg):
            test_storage.get_index_data(test_context)
