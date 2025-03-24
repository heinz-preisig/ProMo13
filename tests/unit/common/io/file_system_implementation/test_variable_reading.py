import shutil
from pathlib import Path

import pytest
from pytest_cases import parametrize, parametrize_with_cases

from src.common.corelib import Index, IndexMap, Variable, VariableMap
from src.common.io import DataIOError, IOContextMember, IOManager


@pytest.fixture
def test_files_path() -> Path:
    return (
        Path.cwd()
        / "tests"
        / "unit"
        / "common"
        / "io"
        / "file_system_implementation"
        / "test_files"
    )


@pytest.fixture
def tmp_test_files_path(tmp_path: Path, test_files_path: Path) -> Path:
    path = tmp_path / "test_files"
    shutil.copytree(test_files_path, path)
    return path


@pytest.fixture
def io_manager() -> IOManager:
    return IOManager()


INDEX_MAP = {
    "I_1": Index("I_1", "iri_I1", "label_I1"),
    "I_2": Index("I_2", "iri_I2", "label_I2"),
    "I_3": Index("I_3", "iri_I3", "label_I3"),
}
I_1 = INDEX_MAP["I_1"]
I_2 = INDEX_MAP["I_2"]
I_3 = INDEX_MAP["I_3"]


VARIABLE_MAP = {
    "V_1": Variable("V_1", "iri_V1", "label_V1", "doc_V1", [I_1, I_2]),
    "V_2": Variable("V_2", "iri_V2", "label_V2", "doc_V2", []),
    "V_3": Variable("V_3", "iri_V3", "label_V3", "doc_V3", [I_1]),
    "V_4": Variable("V_4", "iri_V4", "label_V4", "doc_V4", [I_3]),
    "V_5": Variable("V_5", "iri_V5", "label_V5", "doc_V5", [I_1]),
    "V_6": Variable("V_6", "iri_V6", "label_V6", "doc_V6", [I_1]),
    "V_7": Variable("V_7", "iri_V7", "label_V7", "doc_V7", [I_1]),
    "V_8": Variable("V_8", "iri_V8", "label_V8", "doc_V8", [I_1]),
    "V_9": Variable("V_9", "iri_V9", "label_V9", "doc_V9", [I_1]),
    "V_10": Variable("V_10", "iri_V10", "label_V10", "doc_V10", [I_1]),
    "V_11": Variable("V_11", "iri_V11", "label_V11", "doc_V11", [I_1]),
    "V_12": Variable("V_12", "iri_V12", "label_V12", "doc_V12", [I_1]),
}


class CasesVariableReading:
    def valid_data(
        self, io_manager: IOManager, tmp_test_files_path: Path
    ) -> tuple[IOManager, VariableMap]:
        REPOSITORY_LOCATION = str(tmp_test_files_path / "repositoryOK")
        ONTOLOGY_NAME = "ontologyOK"
        io_manager.set_repository_location(REPOSITORY_LOCATION)
        io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

        return io_manager, VARIABLE_MAP

    def invalid_missing_index_file(
        self, io_manager: IOManager, tmp_test_files_path: Path
    ) -> tuple[IOManager, str]:
        REPOSITORY_LOCATION = str(tmp_test_files_path / "repositoryOK")
        ONTOLOGY_NAME = "ontology1"
        io_manager.set_repository_location(REPOSITORY_LOCATION)
        io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

        error_msg = "Can not access variable data"

        return io_manager, error_msg

    # Indices, Variables and Equations are in the same file now, Indices
    # are read first and is the one failing.

    # @parametrize(folder_id=("2", "3"), ids=("invalid json", "invalid json schema"))
    # def invalid_json_problem(
    #     self,
    #     io_manager: IOManager,
    #     tmp_test_files_path: Path,
    #     folder_id: str,
    # ) -> tuple[IOManager, str]:
    #     REPOSITORY_LOCATION = str(tmp_test_files_path / "repositoryOK")
    #     ONTOLOGY_NAME = f"ontology{folder_id}"
    #     io_manager.set_repository_location(REPOSITORY_LOCATION)
    #     io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

    #     error_msg = "Corrupted variable data"

    #     return io_manager, error_msg


class TestIndexReading:
    @parametrize_with_cases(
        "manager, expected_variable_map", cases=CasesVariableReading, prefix="valid"
    )
    def test_index_reading_ok(
        self, manager: IOManager, expected_variable_map: VariableMap
    ) -> None:
        output_variable_map = manager.get_current_variable_map()

        assert expected_variable_map == output_variable_map

    # @parametrize_with_cases(
    #     "manager, error_msg", cases=CasesVariableReading, prefix="invalid"
    # )
    # def test_exception_on_missing_index_file(
    #     self, manager: IOManager, error_msg: str
    # ) -> None:
    #     with pytest.raises(DataIOError, match=error_msg):
    #         manager.get_current_variable_map()
