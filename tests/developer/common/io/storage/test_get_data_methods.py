import string
import typing

import pytest
import pytest_cases

from src.common import io
from src.common.io import storage

ACCESS_ERROR = string.Template("Can not access $data_name data")
CORRUPTED_ERROR = string.Template("Corrupted $data_name data")

INDEX_DATA = [
    {"identifier": "I_1", "iri": "iri_I1", "label": "label_I1"},
    {"identifier": "I_2", "iri": "iri_I2", "label": "label_I2"},
    {"identifier": "I_3", "iri": "iri_I3", "label": "label_I3"},
]


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


EQUATION_DATA = [
    {"identifier": "E_1", "variables": ["V_1", "V_2", "V_3"]},
    {"identifier": "E_6", "variables": ["V_1", "V_2", "V_5", "V_6"]},
    {"identifier": "E_2", "variables": ["V_4", "V_5", "V_6"]},
    {"identifier": "E_3", "variables": ["V_5", "V_1", "V_7"]},
    {"identifier": "E_4", "variables": ["V_8", "V_9", "V_10"]},
    {"identifier": "E_5", "variables": ["V_9", "V_4", "V_11", "V_12"]},
]


@pytest.fixture
def expected_data_dict() -> dict[str, typing.Any]:
    return {"index": INDEX_DATA, "variable": VARIABLE_DATA, "equation": EQUATION_DATA}


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

        with pytest.raises(io.DataIOError, match=error_msg):
            tested_method(test_context)
