import pathlib
import shutil

import pytest

from src.common import io
from src.common.io import storage


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
def test_storage() -> storage.GenericStorage:
    return storage.FileStorage()


@pytest.fixture
def base_path(tmp_path: pathlib.Path, test_files_path: pathlib.Path) -> pathlib.Path:
    path = tmp_path / "test_files"
    shutil.copytree(test_files_path, path)
    return path


@pytest.fixture
def ok_context(base_path: pathlib.Path) -> io.IOContext:
    ok_location = str(base_path / "repositoryOK")
    ok_ontology = "ontologyOK"
    ok_model = "modelOK"
    ok_instantiation = "instantiationOK"
    return io.IOContext(ok_location, ok_ontology, ok_model, ok_instantiation)


@pytest.fixture
def io_manager() -> io.IOManager:
    return io.IOManager()
