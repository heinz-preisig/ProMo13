import shutil
from collections.abc import Generator
from pathlib import Path

import pytest

from src.common.io import ContextMember, DefaultIOManager, IOManager, OntologyContext


class FakeDataIO:
    def validate_repository_location(self, location: str) -> None:
        pass

    def get_context_member_options(
        self, context_member: ContextMember, context: OntologyContext
    ) -> list[str]:
        match context_member:
            case ContextMember.ONTOLOGY:
                return ["VALID_ONTOLOGY", "OntologyOK"]
            case ContextMember.MODEL:
                return ["VALID_MODEL", "ModelOK"]
            case ContextMember.INSTANTIATION:
                return ["VALID_INSTANTIATION", "InstantiationOK"]


@pytest.fixture
def io_manager() -> IOManager:
    fake_data_io = FakeDataIO()
    return DefaultIOManager(data_io=fake_data_io)


@pytest.fixture
def valid_io_manager(io_manager: IOManager) -> IOManager:
    REPO_LOCATION = "VALID_LOCATION"
    ONTOLOGY_NAME = "VALID_ONTOLOGY"
    MODEL_NAME = "VALID_MODEL"
    INSTANTIATION_NAME = "VALID_INSTANTIATION"

    io_manager.set_repository_location(REPO_LOCATION)
    io_manager.set_ontology_name(ONTOLOGY_NAME)
    io_manager.set_model_name(MODEL_NAME)
    io_manager.set_instantiation_name(INSTANTIATION_NAME)

    return io_manager


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
    def test_set_location_ok(self, io_manager: IOManager) -> None:
        LOCATION = "VALID_LOCATION"
        io_manager.set_repository_location(LOCATION)

        new_ontology_context = io_manager.get_ontology_context()
        output = new_ontology_context.repository_location

        assert LOCATION == output

    def test_reset_depending_context(
        self,
        valid_io_manager: IOManager,
    ) -> None:
        manager = valid_io_manager
        new_repo_location = "NEW_REPO_LOCATION"
        expected_context = OntologyContext(new_repo_location)

        manager.set_repository_location(new_repo_location)

        output_context = manager.get_ontology_context()
        assert expected_context == output_context


class TestSetOntologyName:
    def test_exception_on_invalid_ontology_name(
        self, valid_io_manager: IOManager
    ) -> None:
        ONTOLOGY_NAME = "InvalidOntologyName"
        manager = valid_io_manager

        with pytest.raises(
            FileNotFoundError,
            match=f"The ontology {ONTOLOGY_NAME} does not exist.",
        ):
            manager.set_ontology_name(ONTOLOGY_NAME)

    def test_set_ontology_name_ok(self, valid_io_manager: IOManager) -> None:
        ONTOLOGY_NAME = "OntologyOK"
        manager = valid_io_manager

        manager.set_ontology_name(ONTOLOGY_NAME)

        ontology_context = manager.get_ontology_context()
        output = ontology_context.ontology_name
        assert ONTOLOGY_NAME == output

    def test_reset_depending_context(self, valid_io_manager: IOManager) -> None:
        ONTOLOGY_NAME = "OntologyOK"
        manager = valid_io_manager
        expected_model_name = ""
        expected_instantiation_name = ""

        manager.set_ontology_name(ONTOLOGY_NAME)

        output_context = manager.get_ontology_context()
        output_model_name = output_context.model_name
        output_instantiation_name = output_context.instantiation_name
        assert expected_model_name == output_model_name
        assert expected_instantiation_name == output_instantiation_name


class TestSetModelName:
    def test_exception_on_invalid_model_name(self, valid_io_manager: IOManager) -> None:
        MODEL_NAME = "InvalidModelName"
        manager = valid_io_manager

        with pytest.raises(
            FileNotFoundError,
            match=f"The model {MODEL_NAME} does not exist.",
        ):
            manager.set_model_name(MODEL_NAME)

    def test_set_model_name_ok(self, valid_io_manager: IOManager) -> None:
        MODEL_NAME = "ModelOK"
        manager = valid_io_manager

        manager.set_model_name(MODEL_NAME)

        ontology_context = manager.get_ontology_context()
        output = ontology_context.model_name
        assert MODEL_NAME == output

    def test_reset_depending_context(self, valid_io_manager: IOManager) -> None:
        MODEL_NAME = "ModelOK"
        manager = valid_io_manager
        expected_instantiation_name = ""

        manager.set_model_name(MODEL_NAME)

        output_context = manager.get_ontology_context()
        output_instantiation_name = output_context.instantiation_name
        assert expected_instantiation_name == output_instantiation_name


class TestSetInstantiationName:
    def test_exception_on_invalid_instantiation_name(
        self, valid_io_manager: IOManager
    ) -> None:
        INSTANTIATION_NAME = "InvalidInstantiationName"
        manager = valid_io_manager

        with pytest.raises(
            FileNotFoundError,
            match=f"The instantiation {INSTANTIATION_NAME} does not exist.",
        ):
            manager.set_instantiation_name(INSTANTIATION_NAME)

    def test_set_instantiation_name_ok(self, valid_io_manager: IOManager) -> None:
        INSTANTIATION_NAME = "InstantiationOK"
        manager = valid_io_manager

        manager.set_instantiation_name(INSTANTIATION_NAME)

        ontology_context = manager.get_ontology_context()
        output = ontology_context.instantiation_name
        assert INSTANTIATION_NAME == output
