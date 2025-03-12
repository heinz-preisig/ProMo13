import shutil
from collections.abc import Generator
from pathlib import Path

import pytest
from pytest_cases import parametrize, parametrize_with_cases

from src.common.io import DataIOError, IOContextMember, IOManager


@pytest.fixture
def io_manager() -> IOManager:
    return IOManager()


@pytest.fixture
def test_files_path() -> Path:
    return Path.cwd() / "tests" / "unit" / "common" / "io" / "test_files"


@pytest.fixture
def tmp_test_files_path(tmp_path: Path, test_files_path: Path) -> Path:
    path = tmp_path / "test_files"
    shutil.copytree(test_files_path, path)
    return path


class CasesRepositoryValidation:
    WRITE_ONLY_MODE = 0o222
    READ_ONLY_MODE = 0o444

    def case_nonexistent_directory(self, tmp_path: Path) -> str:
        return str(tmp_path / "Directory")

    @parametrize(
        mode=(WRITE_ONLY_MODE, READ_ONLY_MODE), ids=("write_only", "read_only")
    )
    def case_directory_permissions(self, tmp_path: Path, mode: int) -> Generator[str]:
        dir_path = tmp_path / "Directory"
        dir_path.mkdir(mode=mode)

        yield str(dir_path)

        FULL_PERMISSION_MODE = 0o777
        dir_path.chmod(mode=FULL_PERMISSION_MODE)


class TestRepositoryValidation:
    @parametrize_with_cases("location", cases=CasesRepositoryValidation)
    def test_exception_on_invalid_location(
        self, io_manager: IOManager, location: str
    ) -> None:
        msg = f"Invalid repository location: {location}"

        with pytest.raises(
            DataIOError,
            match=msg,
        ):
            io_manager.set_repository_location(location)


def setup_io_manager_to_repository(
    base_path: Path, repo_type: str, manager: IOManager, folder_id: str
) -> IOManager:
    if repo_type == "ontology":
        repository_name = f"repository{folder_id}"
        set_repo_location(manager, base_path, repository_name)
        return manager

    set_repo_location(manager, base_path)

    if repo_type == "model":
        ontology_name = f"ontology{folder_id}"
        manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)
        return manager

    ontology_name = "ontologyOK"
    manager.set_context_member_name(IOContextMember.ONTOLOGY, ontology_name)

    model_name = f"model{folder_id}"
    manager.set_context_member_name(IOContextMember.MODEL, model_name)

    return manager


def set_repo_location(
    manager: IOManager, base_path: Path, repo_name: str = "repositoryOK"
) -> None:
    repository_path = base_path / repo_name
    repository_location = str(repository_path)
    manager.set_repository_location(repository_location)


@parametrize(
    member=(
        IOContextMember.ONTOLOGY,
        IOContextMember.MODEL,
        IOContextMember.INSTANTIATION,
    ),
    ids=("ontology", "model", "instantiation"),
)
class CasesIndexValidation:
    def case_missing_file(
        self,
        member: IOContextMember,
    ) -> tuple[str, str, IOContextMember]:
        folder_id = "1"
        error_msg = "Can not access {type} index"

        return folder_id, error_msg, member

    @parametrize(folder_id=("2", "3"), ids=("invalid json", "invalid json schema"))
    def case_json_problem(
        self,
        folder_id: str,
        member: IOContextMember,
    ) -> tuple[str, str, IOContextMember]:
        error_msg = "Corrupted {type} index"
        return folder_id, error_msg, member


class TestIndexValidation:
    @parametrize_with_cases("folder_id, error_msg, member", cases=CasesIndexValidation)
    def test_exception_on_invalid_index(
        self,
        io_manager: IOManager,
        tmp_test_files_path: Path,
        folder_id: str,
        error_msg: str,
        member: IOContextMember,
    ) -> None:
        manager = setup_io_manager_to_repository(
            tmp_test_files_path, member, io_manager, folder_id
        )
        error_msg = error_msg.format(type=member)

        with pytest.raises(DataIOError, match=error_msg):
            manager.get_context_member_valid_options(member)

    @parametrize(
        member=(
            IOContextMember.ONTOLOGY,
            IOContextMember.MODEL,
            IOContextMember.INSTANTIATION,
        ),
        ids=("ontology", "model", "instantiation"),
    )
    def test_read_index_ok(
        self, io_manager: IOManager, tmp_test_files_path: Path, member: IOContextMember
    ) -> None:
        FOLDER_ID = "OK"
        manager = setup_io_manager_to_repository(
            tmp_test_files_path, member, io_manager, FOLDER_ID
        )
        expected = [f"{member}{id}" for id in ["1", "2", "3", "OK"]]

        output = manager.get_context_member_valid_options(member)

        assert sorted(expected) == sorted(output)
