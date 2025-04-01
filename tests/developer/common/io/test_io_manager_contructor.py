import pytest

from src.common import io


@pytest.fixture
def io_manager() -> io.IOManager:
    return io.IOManager()


def test_empty_default_context(io_manager: io.IOManager) -> None:
    # GIVEN a new IOManager

    # WHEN retrieving the IOContext
    ontology_context = io_manager.get_io_context()

    # THEN the default IOContext is empty
    assert ontology_context == io.IOContext()
