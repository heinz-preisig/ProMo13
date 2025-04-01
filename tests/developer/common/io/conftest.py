import pytest

from src.common.io import IOManager
from tests.developer.common.io.helpers import FakeStorage


@pytest.fixture
def fake_storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def fake_io_manager(fake_storage: FakeStorage) -> IOManager:
    return IOManager(fake_storage)
