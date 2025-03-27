import shutil
from collections.abc import Generator
from pathlib import Path

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from src.common.io import IOContextError, IOContextMember, IOManager
from src.common.io.storage.exceptions import DataIOError


@pytest.fixture
def io_manager() -> IOManager:
    return IOManager()


@pytest.fixture
def test_files_path() -> Path:
    return (
        Path.cwd() / "tests" / "developer" / "common" / "io" / "storage" / "test_files"
    )


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


@pytest.fixture
def valid_io_manager(io_manager: IOManager, tmp_test_files_path: Path) -> IOManager:
    REPO_LOCATION = str(tmp_test_files_path / "repositoryOK")
    ONTOLOGY_NAME = "ontologyOK"
    MODEL_NAME = "modelOK"
    INSTANTIATION_NAME = "instantiationOK"

    io_manager.set_repository_location(REPO_LOCATION)
    io_manager.set_context_member_name(IOContextMember.ONTOLOGY, ONTOLOGY_NAME)
    io_manager.set_context_member_name(IOContextMember.MODEL, MODEL_NAME)
    io_manager.set_context_member_name(
        IOContextMember.INSTANTIATION, INSTANTIATION_NAME
    )

    return io_manager


def set_io_manager_context(
    manager: IOManager, member: IOContextMember, value: str, base_path: Path
) -> IOManager:
    match member:
        case IOContextMember.ONTOLOGY:
            location = str(base_path / value)
            manager.set_repository_location(location)
        case IOContextMember.MODEL:
            manager.set_context_member_name(IOContextMember.ONTOLOGY, value)
        case IOContextMember.INSTANTIATION:
            manager.set_context_member_name(IOContextMember.MODEL, value)

    return manager


@parametrize(
    "member, folder_prefix",
    [
        (IOContextMember.ONTOLOGY, "repository"),
        (IOContextMember.MODEL, "ontology"),
        (IOContextMember.INSTANTIATION, "model"),
    ],
    ids=("ontology", "model", "instantiation"),
)
class CasesIndexValidation:
    def invalid_missing_file(
        self,
        valid_io_manager: IOManager,
        tmp_test_files_path: Path,
        member: IOContextMember,
        folder_prefix: str,
    ) -> tuple[IOManager, IOContextMember, str]:
        folder_name = f"{folder_prefix}1"
        manager = set_io_manager_context(
            valid_io_manager, member, folder_name, tmp_test_files_path
        )
        error_msg = "Can not access {member} repository index"

        return manager, member, error_msg

    @parametrize(folder_id=("2", "3"), ids=("invalid json", "invalid json schema"))
    def invalid_json_problem(
        self,
        valid_io_manager: IOManager,
        tmp_test_files_path: Path,
        member: IOContextMember,
        folder_prefix: str,
        folder_id: str,
    ) -> tuple[IOManager, IOContextMember, str]:
        error_msg = "Corrupted {member} repository index"
        folder_name = f"{folder_prefix}{folder_id}"
        manager = set_io_manager_context(
            valid_io_manager, member, folder_name, tmp_test_files_path
        )

        return manager, member, error_msg

    @case(id="")
    def valid_index(
        self,
        valid_io_manager: IOManager,
        member: IOContextMember,
        folder_prefix: str,
    ) -> tuple[IOManager, IOContextMember]:
        return valid_io_manager, member

    @case(id="")
    def incomplete_context(
        self,
        io_manager: IOManager,
        member: IOContextMember,
        folder_prefix: str,
    ) -> tuple[IOManager, IOContextMember]:
        return io_manager, member


class TestIndexValidation:
    @parametrize_with_cases(
        "manager, member, error_msg", cases=CasesIndexValidation, prefix="invalid"
    )
    def test_exception_on_invalid_index(
        self,
        manager: IOManager,
        member: IOContextMember,
        error_msg: str,
    ) -> None:
        error_msg = error_msg.format(member=member)

        with pytest.raises(DataIOError, match=error_msg):
            manager.get_context_member_valid_options(member)

    @parametrize_with_cases(
        "manager, member", cases=CasesIndexValidation, prefix="valid"
    )
    def test_read_index_ok(self, manager: IOManager, member: IOContextMember) -> None:
        expected = [f"{member}{id}" for id in ["1", "2", "3", "OK"]]

        output = manager.get_context_member_valid_options(member)

        assert sorted(expected) == sorted(output)

    @parametrize_with_cases(
        "manager, member", cases=CasesIndexValidation, prefix="incomplete"
    )
    def test_exception_on_read_index_with_incomplete_context(
        self, manager: IOManager, member: IOContextMember
    ) -> None:
        error_msg = "Insufficient data in IOContext"

        with pytest.raises(IOContextError, match=error_msg):
            manager.get_context_member_valid_options(member)
