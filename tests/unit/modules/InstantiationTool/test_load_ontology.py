import pytest

import conftest

from packages.Utilities.InstantiationTool.models.main import MainModel

TEST_FILES = conftest.get_test_files_path()


@pytest.fixture
def test_model(var_idx_eq, model_objects, entities) -> MainModel:
  model = MainModel()
  model.all_variables, model.all_indices, _ = var_idx_eq
  model.model_objects = model_objects
  model.all_entities = entities

  return model


@pytest.mark.datafiles(
    TEST_FILES / 'model.json',
    TEST_FILES / 'var_idx_eq.json',
    TEST_FILES / 'entities.json',
)
def test_get_required_variables(datafiles, test_model):
  print(test_model.all_entities.keys())
  assert test_model.all_entities.keys() == ["test"]
