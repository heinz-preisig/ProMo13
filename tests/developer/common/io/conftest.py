import pytest

from src.common.io import IOManager
from tests.developer.common.io.helpers import FakeDataIO


@pytest.fixture
def fake_data_io() -> FakeDataIO:
    return FakeDataIO()


@pytest.fixture
def fake_io_manager(fake_data_io: FakeDataIO) -> IOManager:
    return IOManager(fake_data_io)
