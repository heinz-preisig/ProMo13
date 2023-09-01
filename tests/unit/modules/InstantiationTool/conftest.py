import pytest

from PyQt5.QtWidgets import QApplication

from tasks.ProMo_inst import App
from packages.Utilities.InstantiationTool.models.main import MainModel


@pytest.fixture
def main_model(var_idx_eq, topology_objects, entities) -> MainModel:
  model = MainModel()
  model.all_variables, model.all_indices, _ = var_idx_eq
  model.topology_objects = topology_objects
  model.all_entities = entities

  return model


@pytest.fixture
def app() -> App:
  app = App([])
  yield app
  app.quit()
