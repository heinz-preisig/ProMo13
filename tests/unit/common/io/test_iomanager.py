import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

from src.common.io import DefaultIOManager, IOManager, OntologyContext


@pytest.fixture
def io_manager() -> IOManager:
    return DefaultIOManager()


@pytest.fixture
def repo_location(tmp_path: Path, current_repository_path: Path) -> str:
    repo_path = tmp_path / "OntologyRepository"
    shutil.copytree(current_repository_path, repo_path)
    return str(repo_path)


@pytest.fixture
def preset_io_manager_with_repo_location(
    io_manager: IOManager, repo_location: str
) -> IOManager:
    io_manager.set_repository_location(repo_location)
    return io_manager


@pytest.fixture
def preset_io_manager_with_ontology_name(
    preset_io_manager_with_repo_location: IOManager,
) -> IOManager:
    ONTOLOGY_NAME = "TestOntology"
    manager = preset_io_manager_with_repo_location
    manager.set_ontology_name(ONTOLOGY_NAME)
    return manager


@pytest.fixture
def preset_io_manager_with_model_name(
    preset_io_manager_with_ontology_name: IOManager,
) -> IOManager:
    MODEL_NAME = "TestModel"
    manager = preset_io_manager_with_ontology_name
    manager.set_model_name(MODEL_NAME)
    return manager


@pytest.fixture
def preset_io_manager_with_instantiation_name(
    preset_io_manager_with_model_name: IOManager,
) -> IOManager:
    INSTANTIATION_NAME = "TestInstantiation"
    manager = preset_io_manager_with_model_name
    manager.set_instantiation_name(INSTANTIATION_NAME)
    return manager


@pytest.fixture
def nonexistent_dir_location(tmp_path: Path) -> str:
    return str(tmp_path / "NonexistentDir")


@pytest.fixture
def read_only_dir_location(tmp_path: Path) -> str:
    dir_path = tmp_path / "ReadOnlyDir"
    READ_ONLY = 0o444
    dir_path.mkdir(mode=READ_ONLY)
    return str(dir_path)


@pytest.fixture
def write_only_dir_location(tmp_path: Path) -> Generator[str]:
    dir_path = tmp_path / "WriteOnlyDir"
    WRITE_ONLY = 0o222
    dir_path.mkdir(mode=WRITE_ONLY)
    yield str(dir_path)
    FULL_PERMISSIONS = 0o777
    dir_path.chmod(mode=FULL_PERMISSIONS)


@pytest.fixture
def current_repository_path() -> Path:
    return Path.cwd() / "tests" / "unit" / "common" / "io" / "OntologyRepository"


@pytest.fixture
def new_repo_location(tmp_path: Path) -> str:
    repo_path = tmp_path / "NewOntologyRepository"
    repo_path.mkdir()
    return str(repo_path)


class TestDefaultIOManagerConstructor:
    def test_empty_initial_context(self) -> None:
        io_manager = DefaultIOManager()

        ontology_context = io_manager.get_ontology_context()
        assert ontology_context.repository_location == ""
        assert ontology_context.ontology_name == ""
        assert ontology_context.model_name == ""
        assert ontology_context.instantiation_name == ""


class TestGetOntologyContext:
    def test_returned_context_is_copy(self, io_manager: IOManager) -> None:
        ontology_context = io_manager.get_ontology_context()
        ontology_context.repository_location = "PathModified"
        ontology_context = io_manager.get_ontology_context()
        assert ontology_context.repository_location == ""


class TestSetRepositoryLocation:
    def test_exception_on_invalid_location(
        self, io_manager: IOManager, nonexistent_dir_location: str
    ) -> None:
        with pytest.raises(
            FileNotFoundError,
            match=f"The directory at {nonexistent_dir_location} does not exist.",
        ):
            io_manager.set_repository_location(nonexistent_dir_location)

    def test_exception_on_read_only_location(
        self, io_manager: IOManager, read_only_dir_location: str
    ) -> None:
        with pytest.raises(
            PermissionError,
            match=f"You don't have write permissions at {read_only_dir_location}.",
        ):
            io_manager.set_repository_location(read_only_dir_location)

    def test_exception_on_write_only_location(
        self, io_manager: IOManager, write_only_dir_location: str
    ) -> None:
        with pytest.raises(
            PermissionError,
            match=f"You don't have read permissions at {write_only_dir_location}.",
        ):
            io_manager.set_repository_location(write_only_dir_location)

    def test_set_location_ok(self, io_manager: IOManager, repo_location: str) -> None:
        io_manager.set_repository_location(repo_location)

        new_ontology_context = io_manager.get_ontology_context()
        assert new_ontology_context.repository_location == repo_location


class TestSetOntologyName:
    def test_exception_on_invalid_ontology(
        self, preset_io_manager_with_repo_location: IOManager
    ) -> None:
        ONTOLOGY_NAME = "NonExistentOntology"
        manager = preset_io_manager_with_repo_location

        with pytest.raises(
            FileNotFoundError,
            match=f"The ontology {ONTOLOGY_NAME} does not exist.",
        ):
            manager.set_ontology_name(ONTOLOGY_NAME)

    def test_set_ontology_ok(
        self, preset_io_manager_with_repo_location: IOManager
    ) -> None:
        ONTOLOGY_NAME = "TestOntology"
        manager = preset_io_manager_with_repo_location

        manager.set_ontology_name(ONTOLOGY_NAME)

        ontology_context = manager.get_ontology_context()
        assert ontology_context.ontology_name == ONTOLOGY_NAME


class TestSetModelName:
    def test_exception_on_invalid_model(
        self, preset_io_manager_with_ontology_name: IOManager
    ) -> None:
        MODEL_NAME = "NonExistentModel"
        manager = preset_io_manager_with_ontology_name

        with pytest.raises(
            FileNotFoundError,
            match=f"The model {MODEL_NAME} does not exist.",
        ):
            manager.set_model_name(MODEL_NAME)

    def test_set_model_ok(
        self, preset_io_manager_with_ontology_name: IOManager
    ) -> None:
        MODEL_NAME = "TestModel"
        manager = preset_io_manager_with_ontology_name

        manager.set_model_name(MODEL_NAME)

        ontology_context = manager.get_ontology_context()
        assert ontology_context.model_name == MODEL_NAME


class TestSetInstantiationName:
    def test_exception_on_invalid_instantiation(
        self, preset_io_manager_with_model_name: IOManager
    ) -> None:
        INSTANTIATION_NAME = "NonExistentInstantiation"
        manager = preset_io_manager_with_model_name

        with pytest.raises(
            FileNotFoundError,
            match=f"The instantiation {INSTANTIATION_NAME} does not exist.",
        ):
            manager.set_instantiation_name(INSTANTIATION_NAME)

    def test_set_instantiation_ok(
        self, preset_io_manager_with_model_name: IOManager
    ) -> None:
        INSTANTIATION_NAME = "TestInstantiation"
        manager = preset_io_manager_with_model_name

        manager.set_instantiation_name(INSTANTIATION_NAME)

        ontology_context = manager.get_ontology_context()
        assert ontology_context.instantiation_name == INSTANTIATION_NAME
