from collections.abc import Generator
from pathlib import Path

import pytest
from pytest_cases import parametrize, parametrize_with_cases

from src.common.io import DataIOError, IOManager


class CasesRepositoryValidation:
    WRITE_ONLY_MODE = 0o222
    READ_ONLY_MODE = 0o444

    def case_missing_directory(self, base_path: Path) -> str:
        return str(base_path / "MissingDirectory")

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
