import pathlib
import shutil

import pytest

from src.common import io


@pytest.fixture
def test_files_path() -> pathlib.Path:
    return (
        pathlib.Path.cwd()
        / "tests"
        / "developer"
        / "common"
        / "io"
        / "storage"
        / "test_files"
    )


@pytest.fixture
def base_path(tmp_path: pathlib.Path, test_files_path: pathlib.Path) -> pathlib.Path:
    path = tmp_path / "test_files"
    shutil.copytree(test_files_path, path)
    return path


@pytest.fixture
def io_manager() -> io.IOManager:
    return io.IOManager()
