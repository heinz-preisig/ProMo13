import pathlib
from collections.abc import Generator

import pytest
import pytest_cases

from src.common.io import storage

WRITE_ONLY_MODE = 0o222
READ_ONLY_MODE = 0o444


def case_missing_directory(tmp_path: pathlib.Path) -> str:
    return str(tmp_path / "MissingDirectory")


@pytest_cases.parametrize(
    mode=(WRITE_ONLY_MODE, READ_ONLY_MODE), ids=("write_only", "read_only")
)
def case_directory_permissions(tmp_path: pathlib.Path, mode: int) -> Generator[str]:
    dir_path = tmp_path / "Directory"
    dir_path.mkdir(mode=mode)

    yield str(dir_path)

    FULL_PERMISSION_MODE = 0o777
    dir_path.chmod(mode=FULL_PERMISSION_MODE)


class TestRepositoryValidation:
    @pytest_cases.parametrize_with_cases("location", cases=".")
    def test_exception_on_invalid_location(
        self, test_storage: storage.GenericStorage, location: str
    ) -> None:
        msg = f"Invalid repository location: {location}"

        with pytest.raises(storage.IOStorageError, match=msg):
            test_storage.validate_repository_location(location)
