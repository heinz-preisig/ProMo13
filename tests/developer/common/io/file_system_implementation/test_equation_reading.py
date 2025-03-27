import shutil
from pathlib import Path

import pytest
from pytest_cases import parametrize, parametrize_with_cases

from src.common.corelib import (
    Equation,
    EquationMap,
    Index,
    IndexMap,
    Variable,
    VariableMap,
)
from src.common.io import IOContextMember, IOManager
from src.common.io.storage.exceptions import DataIOError


@pytest.fixture
def test_files_path() -> Path:
    return (
        Path.cwd()
        / "tests"
        / "developer"
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

V_1 = VARIABLE_MAP["V_1"]
V_2 = VARIABLE_MAP["V_2"]
V_3 = VARIABLE_MAP["V_3"]
V_4 = VARIABLE_MAP["V_4"]
V_5 = VARIABLE_MAP["V_5"]
V_6 = VARIABLE_MAP["V_6"]
V_7 = VARIABLE_MAP["V_7"]
V_8 = VARIABLE_MAP["V_8"]
V_9 = VARIABLE_MAP["V_9"]
V_10 = VARIABLE_MAP["V_10"]
V_11 = VARIABLE_MAP["V_11"]
V_12 = VARIABLE_MAP["V_12"]

EQUATION_MAP = {
    "E_1": Equation("E_1", [V_1, V_2, V_3]),
    "E_2": Equation("E_2", [V_4, V_5, V_6]),
    "E_3": Equation("E_3", [V_5, V_1, V_7]),
    "E_4": Equation("E_4", [V_8, V_9, V_10]),
    "E_5": Equation("E_5", [V_9, V_4, V_11, V_12]),
    "E_6": Equation("E_6", [V_1, V_2, V_5, V_6]),
}


class CasesEquationReading:
    def valid_data(
        self, io_manager: IOManager, tmp_test_files_path: Path
    ) -> tuple[IOManager, EquationMap]:
        REPOSITORY_LOCATION = str(tmp_test_files_path / "repositoryOK")
        ONTOLOGY_NAME = "ontologyOK"
        io_manager.set_repository_location(REPOSITORY_LOCATION)
        io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

        return io_manager, EQUATION_MAP


class TestEquationReading:
    @parametrize_with_cases(
        "manager, expected_equation_map", cases=CasesEquationReading, prefix="valid"
    )
    def test_equation_reading_ok(
        self, manager: IOManager, expected_equation_map: EquationMap
    ) -> None:
        output_equation_map = manager.get_current_equation_map()

        assert expected_equation_map == output_equation_map
