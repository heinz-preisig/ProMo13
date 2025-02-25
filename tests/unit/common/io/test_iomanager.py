import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

from src.common.io import DefaultIOManager, IOManager, OntologyContext


@pytest.fixture
def io_manager() -> IOManager:
    return DefaultIOManager()


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
def repo_location(tmp_path: Path, current_repository_path: Path) -> str:
    repo_path = tmp_path / "OntologyRepository"
    shutil.copytree(current_repository_path, repo_path)
    return str(repo_path)


@pytest.fixture
def new_repo_location(tmp_path: Path) -> str:
    repo_path = tmp_path / "NewOntologyRepository"
    repo_path.mkdir()
    return str(repo_path)


@pytest.mark.describe("Test DefaultIOManager creation:")
class TestDefaultIOManagerConstructor:
    @pytest.mark.it("Empty initial OntologyContext")
    def test_empty_context(self, io_manager: IOManager) -> None:
        ontology_context = io_manager.get_ontology_context()
        assert ontology_context.repository_location == ""
        assert ontology_context.ontology_name == ""
        assert ontology_context.model_name == ""
        assert ontology_context.instantiation_name == ""


@pytest.mark.describe("Test get_ontology_context")
class TestGetOntologyContext:
    @pytest.mark.it("OntologyContext returned is a copy")
    def test_context_copy(self, io_manager: IOManager) -> None:
        ontology_context = io_manager.get_ontology_context()
        ontology_context.repository_location = "PathModified"
        ontology_context = io_manager.get_ontology_context()
        assert ontology_context.repository_location == ""


@pytest.mark.describe("Test update_ontology_context:")
class TestUpdateOntologyContext:
    @pytest.mark.it("Exception on invalid repository path")
    def test_invalid_repository_path(
        self, io_manager: IOManager, nonexistent_dir_location: Path
    ) -> None:
        bad_ontology_context = OntologyContext(nonexistent_dir_location)
        with pytest.raises(
            FileNotFoundError,
            match=f"The directory {nonexistent_dir_location} does not exist.",
        ):
            io_manager.update_ontology_context(bad_ontology_context)

    @pytest.mark.it("Exception on read only repository dir")
    def test_read_only_dir(
        self, io_manager: IOManager, read_only_dir_location: str
    ) -> None:
        ontology_context = OntologyContext(read_only_dir_location)
        with pytest.raises(
            PermissionError,
            match=f"You have not write permissions on {read_only_dir_location}",
        ):
            io_manager.update_ontology_context(ontology_context)

    @pytest.mark.it("Exception on write only repository dir")
    def test_write_only_dir(
        self, io_manager: IOManager, write_only_dir_location: str
    ) -> None:
        ontology_context = OntologyContext(write_only_dir_location)
        with pytest.raises(
            PermissionError,
            match=f"You have not read permissions on {write_only_dir_location}",
        ):
            io_manager.update_ontology_context(ontology_context)

    @pytest.mark.it("Existing repository path updated correctly")
    def test_update_existing_repo_ok(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        existing_ontologies = ["Ontology1", "Ontology2", "TestOntology"]
        ontology_context = OntologyContext(repo_location)
        io_manager.update_ontology_context(ontology_context)
        new_ontology_context = io_manager.get_ontology_context()

        assert new_ontology_context.repository_location == repo_location
        assert sorted(new_ontology_context.ontologies) == sorted(existing_ontologies)

    @pytest.mark.it("New repository path updated correctly")
    def test_update_new_repo_ok(self, io_manager: IOManager, new_repo_location: str):
        ontology_context = OntologyContext(new_repo_location)

        io_manager.update_ontology_context(ontology_context)

        new_ontology_context = io_manager.get_ontology_context()

        assert new_ontology_context.repository_location == new_repo_location
        assert len(new_ontology_context.ontologies) == 0

    @pytest.mark.it("Exception on invalid ontology")
    def test_invalid_ontology(self, io_manager: IOManager, repo_location: str) -> None:
        ontology_name = "NonExistentOntology"
        ontology_context = OntologyContext(repo_location, ontology_name)
        with pytest.raises(
            FileNotFoundError,
            match=f"The ontology {ontology_name} does not exist in the repository at {repo_location}",
        ):
            io_manager.update_ontology_context(ontology_context)

    @pytest.mark.it("Ontology name updated correctly")
    def test_ontology_ok(self, io_manager: IOManager, repo_location: str):
        ontology_name = "TestOntology"
        ontology_context = OntologyContext(repo_location, ontology_name)
        existing_models = ["Model1", "Model2", "TestModel"]

        io_manager.update_ontology_context(ontology_context)

        new_ontology_context = io_manager.get_ontology_context()

        assert new_ontology_context.ontology_name == ontology_name
        assert sorted(new_ontology_context.models) == sorted(existing_models)

    @pytest.mark.it("Exception on invalid model")
    def test_invalid_model(self, io_manager: IOManager, repo_location: str) -> None:
        ontology_name = "TestOntology"
        model_name = "NonExistentModel"
        ontology_context = OntologyContext(repo_location, ontology_name, model_name)
        with pytest.raises(
            FileNotFoundError,
            match=f"The model {model_name} does not exist in the ontology {ontology_name}",
        ):
            io_manager.update_ontology_context(ontology_context)

    @pytest.mark.it("Model name updated correctly")
    def test_model_ok(self, io_manager: IOManager, repo_location: str):
        ontology_name = "TestOntology"
        model_name = "TestModel"
        ontology_context = OntologyContext(repo_location, ontology_name, model_name)
        existing_instantiations = [
            "Instantiation1",
            "Instantiation2",
            "TestInstantiation",
        ]

        io_manager.update_ontology_context(ontology_context)

        new_ontology_context = io_manager.get_ontology_context()

        assert new_ontology_context.model_name == model_name
        assert sorted(new_ontology_context.instantiations) == sorted(
            existing_instantiations
        )

    @pytest.mark.it("Exception on invalid instantiation")
    def test_invalid_instantiation(
        self, io_manager: IOManager, repo_location: str
    ) -> None:
        ontology_name = "TestOntology"
        model_name = "TestModel"
        instantiation_name = "NonExistentInstantiation"
        ontology_context = OntologyContext(
            repo_location, ontology_name, model_name, instantiation_name
        )
        with pytest.raises(
            FileNotFoundError,
            match=f"The instantiation {instantiation_name} does not exist in the model {model_name}",
        ):
            io_manager.update_ontology_context(ontology_context)

    @pytest.mark.it("Instantiation name updated correctly")
    def test_instantiation_ok(self, io_manager: IOManager, repo_location: str):
        ontology_name = "TestOntology"
        model_name = "TestModel"
        instantiation_name = "TestInstantiation"
        ontology_context = OntologyContext(
            repo_location, ontology_name, model_name, instantiation_name
        )

        io_manager.update_ontology_context(ontology_context)

        new_ontology_context = io_manager.get_ontology_context()

        assert new_ontology_context.instantiation_name == instantiation_name
