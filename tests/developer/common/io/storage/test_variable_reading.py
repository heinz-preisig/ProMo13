import pathlib

import pytest
import pytest_cases

from src.common import io
from src.common.io import storage

VARIABLE_DATA = [
    {
        "identifier": "V_1",
        "iri": "iri_V1",
        "label": "label_V1",
        "doc": "doc_V1",
        "indices": ["I_1", "I_2"],
    },
    {
        "identifier": "V_2",
        "iri": "iri_V2",
        "label": "label_V2",
        "doc": "doc_V2",
        "indices": [],
    },
    {
        "identifier": "V_3",
        "iri": "iri_V3",
        "label": "label_V3",
        "doc": "doc_V3",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_4",
        "iri": "iri_V4",
        "label": "label_V4",
        "doc": "doc_V4",
        "indices": ["I_3"],
    },
    {
        "identifier": "V_5",
        "iri": "iri_V5",
        "label": "label_V5",
        "doc": "doc_V5",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_6",
        "iri": "iri_V6",
        "label": "label_V6",
        "doc": "doc_V6",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_7",
        "iri": "iri_V7",
        "label": "label_V7",
        "doc": "doc_V7",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_8",
        "iri": "iri_V8",
        "label": "label_V8",
        "doc": "doc_V8",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_9",
        "iri": "iri_V9",
        "label": "label_V9",
        "doc": "doc_V9",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_10",
        "iri": "iri_V10",
        "label": "label_V10",
        "doc": "doc_V10",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_11",
        "iri": "iri_V11",
        "label": "label_V11",
        "doc": "doc_V11",
        "indices": ["I_1"],
    },
    {
        "identifier": "V_12",
        "iri": "iri_V12",
        "label": "label_V12",
        "doc": "doc_V12",
        "indices": ["I_1"],
    },
]


ACCESS_ERROR = "Can not access variable data"
CORRUPTED_ERROR = "Corrupted variable data"


@pytest_cases.case(id="")
@pytest_cases.parametrize(
    "name_id, error_msg",
    [("1", ACCESS_ERROR), ("2", CORRUPTED_ERROR), ("3", CORRUPTED_ERROR)],
    ids=("missing file", "invalid json", "invalid json schema"),
)
def case_variable_file_problem(
    ok_context: io.IOContext, name_id: str, error_msg: str
) -> tuple[io.IOContext, str]:
    ONTOLOGY_NAME = f"ontology{name_id}"
    ok_context.ontology_name = ONTOLOGY_NAME

    return ok_context, error_msg


class TestVariableReading:
    def test_variable_reading_ok(
        self, test_storage: storage.GenericStorage, ok_context: io.IOContext
    ) -> None:
        expected_data = VARIABLE_DATA

        output_data = test_storage.get_variable_data(ok_context)

        assert expected_data == output_data

    @pytest_cases.parametrize_with_cases("test_context, error_msg", cases=".")
    def test_exception_on_missing_variable_file(
        self,
        test_storage: storage.GenericStorage,
        test_context: io.IOContext,
        error_msg: str,
    ) -> None:
        with pytest.raises(io.DataIOError, match=error_msg):
            test_storage.get_variable_data(test_context)
