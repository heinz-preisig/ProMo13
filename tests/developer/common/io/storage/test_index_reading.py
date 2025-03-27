import shutil
from pathlib import Path

import pytest
from pytest_cases import parametrize, parametrize_with_cases

from src.common.corelib import Index, IndexMap
from src.common.io import IOContextMember, IOManager
from src.common.io.storage.exceptions import DataIOError


class CasesIndexReading:
    def valid_data(
        self, io_manager: IOManager, base_path: Path
    ) -> tuple[IOManager, IndexMap]:
        REPOSITORY_LOCATION = str(base_path / "repositoryOK")
        ONTOLOGY_NAME = "ontologyOK"
        io_manager.set_repository_location(REPOSITORY_LOCATION)
        io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

        index_map = {
            "I_1": Index("I_1", "iri_I1", "label_I1"),
            "I_2": Index("I_2", "iri_I2", "label_I2"),
            "I_3": Index("I_3", "iri_I3", "label_I3"),
        }

        return io_manager, index_map

    def invalid_missing_index_file(
        self, io_manager: IOManager, base_path: Path
    ) -> tuple[IOManager, str]:
        REPOSITORY_LOCATION = str(base_path / "repositoryOK")
        ONTOLOGY_NAME = "ontology1"
        io_manager.set_repository_location(REPOSITORY_LOCATION)
        io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

        error_msg = "Can not access index data"

        return io_manager, error_msg

    @parametrize(folder_id=("2", "3"), ids=("invalid json", "invalid json schema"))
    def invalid_json_problem(
        self,
        io_manager: IOManager,
        base_path: Path,
        folder_id: str,
    ) -> tuple[IOManager, str]:
        REPOSITORY_LOCATION = str(base_path / "repositoryOK")
        ONTOLOGY_NAME = f"ontology{folder_id}"
        io_manager.set_repository_location(REPOSITORY_LOCATION)
        io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)

        error_msg = "Corrupted index data"

        return io_manager, error_msg


class TestIndexReading:
    @parametrize_with_cases(
        "manager, expected_index_map", cases=CasesIndexReading, prefix="valid"
    )
    def test_index_reading_ok(
        self, manager: IOManager, expected_index_map: IndexMap
    ) -> None:
        output_index_map = manager.get_current_index_map()

        assert expected_index_map == output_index_map

    @parametrize_with_cases(
        "manager, error_msg", cases=CasesIndexReading, prefix="invalid"
    )
    def test_exception_on_missing_index_file(
        self, manager: IOManager, error_msg: str
    ) -> None:
        with pytest.raises(DataIOError, match=error_msg):
            manager.get_current_index_map()
