import shutil
from pathlib import Path

import pytest
from pytest_cases import parametrize_with_cases

from src.common.corelib import Index, IndexMap
from src.common.io import IOContextMember, IOManager


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


class CasesIndexReading:
    def case_reading_ok(
        self, io_manager: IOManager, tmp_test_files_path: Path
    ) -> tuple[IOManager, IndexMap]:
        REPOSITORY_LOCATION = str(tmp_test_files_path / "repositoryOK")
        ONTOLOGY_NAME = "ontologyOK"
        io_manager.set_repository_location(REPOSITORY_LOCATION)
        io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

        index_map = {
            "I_1": Index("I_1", "iri_I1", "label_I1"),
            "I_2": Index("I_2", "iri_I2", "label_I2"),
            "I_3": Index("I_3", "iri_I3", "label_I3"),
        }

        return io_manager, index_map


class TestIndexReading:
    @parametrize_with_cases("manager, expected_index_map", cases=CasesIndexReading)
    def test_index_reading_ok(
        self, manager: IOManager, expected_index_map: IndexMap
    ) -> None:
        output_index_map = manager.get_current_index_map()

        assert expected_index_map == output_index_map
