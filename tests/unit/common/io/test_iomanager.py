import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

from src.common.io import DataIOException, DefaultIOManager, IOManager, OntologyContext


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


@pytest.fixture
def repo_with_invalid_json_index(new_repo_location: str) -> str:
    repo_path = Path(new_repo_location)
    repo_index = repo_path / ".repository_index.json"
    repo_index.write_text("invalid json")
    return str(repo_path)


@pytest.fixture
def repo_with_incorrect_structure_json_index(new_repo_location: str) -> str:
    repo_path = Path(new_repo_location)
    repo_index = repo_path / ".repository_index.json"
    repo_index.write_text('{"incorrect structure": ""}')
    return str(repo_path)


def preset_io_manager(io_manager: IOManager, context: OntologyContext) -> IOManager:
    if context.repository_location:
        io_manager.set_repository_location(context.repository_location)

    if context.ontology_name:
        io_manager.set_ontology_name(context.ontology_name)

    if context.model_name:
        io_manager.set_model_name(context.model_name)

    if context.instantiation_name:
        io_manager.set_instantiation_name(context.instantiation_name)

    return io_manager


class TestDefaultIOManagerConstructor:
    def test_empty_initial_context(self) -> None:
        io_manager = DefaultIOManager()

        ontology_context = io_manager.get_ontology_context()
        assert ontology_context == OntologyContext()


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

    def test_reset_depending_context(
        self,
        preset_io_manager_with_instantiation_name: IOManager,
        new_repo_location: str,
    ) -> None:
        manager = preset_io_manager_with_instantiation_name
        expected_context = OntologyContext(new_repo_location)

        manager.set_repository_location(new_repo_location)

        output_context = manager.get_ontology_context()
        assert expected_context == output_context


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

    def test_reset_depending_context(
        self, preset_io_manager_with_instantiation_name: IOManager, repo_location: str
    ) -> None:
        manager = preset_io_manager_with_instantiation_name
        ONTOLOGY_NAME = "Ontology1"
        expected_context = OntologyContext(repo_location, ONTOLOGY_NAME)

        manager.set_ontology_name(ONTOLOGY_NAME)

        output_context = manager.get_ontology_context()
        assert expected_context == output_context


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

    def test_reset_depending_context(
        self, preset_io_manager_with_instantiation_name: IOManager, repo_location: str
    ) -> None:
        manager = preset_io_manager_with_instantiation_name
        ONTOLOGY_NAME = "TestOntology"
        MODEL_NAME = "Model1"
        expected_context = OntologyContext(repo_location, ONTOLOGY_NAME, MODEL_NAME)

        manager.set_model_name(MODEL_NAME)

        output_context = manager.get_ontology_context()
        assert expected_context == output_context


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


class TestGetAvailableOntologies:
    def test_exception_on_index_access_problem(self, io_manager: IOManager) -> None:
        error_msg = "Can not access ontology index"

        with pytest.raises(DataIOException, match=error_msg):
            io_manager.get_available_ontologies()

    def test_exception_on_invalid_json_index(
        self, io_manager: IOManager, repo_with_invalid_json_index: str
    ) -> None:
        error_msg = "Corrupted ontology index"
        context = OntologyContext(repo_with_invalid_json_index)
        manager = preset_io_manager(io_manager, context)

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_ontologies()

    def test_exception_on_incorrect_structure_json_index(
        self, io_manager: IOManager, repo_with_incorrect_structure_json_index: str
    ) -> None:
        error_msg = "Corrupted ontology index"
        context = OntologyContext(repo_with_incorrect_structure_json_index)
        manager = preset_io_manager(io_manager, context)

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_ontologies()

    def test_get_available_ontologies_ok(
        self, preset_io_manager_with_repo_location: IOManager
    ) -> None:
        manager = preset_io_manager_with_repo_location
        expected_ontologies = ["Ontology1", "Ontology2", "Ontology3", "TestOntology"]

        output_ontologies = manager.get_available_ontologies()

        assert sorted(expected_ontologies) == sorted(output_ontologies)


class TestGetAvailableModels:
    def test_exception_on_missing_index(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        ONTOLOGY_NAME = "Ontology1"
        context = OntologyContext(repo_location, ONTOLOGY_NAME)
        manager = preset_io_manager(io_manager, context)
        error_msg = "Can not access model index"

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_models()

    def test_exception_on_invalid_json_index(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        ONTOLOGY_NAME = "Ontology2"
        context = OntologyContext(repo_location, ONTOLOGY_NAME)
        manager = preset_io_manager(io_manager, context)
        error_msg = "Corrupted model index"

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_models()

    def test_exception_on_incorrect_structure_json_index(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        ONTOLOGY_NAME = "Ontology3"
        context = OntologyContext(repo_location, ONTOLOGY_NAME)
        manager = preset_io_manager(io_manager, context)
        error_msg = "Corrupted model index"

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_models()

    def test_get_available_models_ok(
        self, preset_io_manager_with_ontology_name: IOManager
    ) -> None:
        manager = preset_io_manager_with_ontology_name
        expected_models = ["Model1", "Model2", "Model3", "TestModel"]

        output_models = manager.get_available_models()

        assert sorted(expected_models) == sorted(output_models)


class TestGetAvailableInstantiations:
    def test_exception_on_missing_index(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        ONTOLOGY_NAME = "TestOntology"
        MODEL_NAME = "Model1"
        context = OntologyContext(repo_location, ONTOLOGY_NAME, MODEL_NAME)
        manager = preset_io_manager(io_manager, context)
        error_msg = "Can not access instantiation index"

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_instantiations()

    def test_exception_on_invalid_json_index(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        ONTOLOGY_NAME = "TestOntology"
        MODEL_NAME = "Model2"
        context = OntologyContext(repo_location, ONTOLOGY_NAME, MODEL_NAME)
        manager = preset_io_manager(io_manager, context)
        error_msg = "Corrupted instantiation index"

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_instantiations()

    def test_exception_on_incorrect_structure_json_index(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        ONTOLOGY_NAME = "TestOntology"
        MODEL_NAME = "Model3"
        context = OntologyContext(repo_location, ONTOLOGY_NAME, MODEL_NAME)
        manager = preset_io_manager(io_manager, context)
        error_msg = "Corrupted instantiation index"

        with pytest.raises(DataIOException, match=error_msg):
            manager.get_available_instantiations()

    def test_get_available_instantiations_ok(
        self, preset_io_manager_with_model_name: IOManager
    ) -> None:
        manager = preset_io_manager_with_model_name
        expected_instantiations = [
            "Instantiation1",
            "Instantiation2",
            "TestInstantiation",
        ]

        output_instantiations = manager.get_available_instantiations()

        assert sorted(expected_instantiations) == sorted(output_instantiations)
