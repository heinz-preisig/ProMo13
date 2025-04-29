import dataclasses

import pytest

from src.common import io


@pytest.fixture
def io_manager() -> io.IOManager:
    return io.IOManager()


class TestGetOntologyContext:
    def test_returned_context_is_copy(self, io_manager: io.IOManager) -> None:
        # GIVEN an IOManager with default IOContext
        ontology_context = io_manager.get_io_context()
        original_data = dataclasses.asdict(ontology_context)

        # WHEN modifying the IOContext
        ontology_context.repository_location = "LocationModified"

        # THEN the original IOContext is not modified
        new_ontology_context = io_manager.get_io_context()
        data_after_modification = dataclasses.asdict(new_ontology_context)
        assert original_data == data_after_modification
