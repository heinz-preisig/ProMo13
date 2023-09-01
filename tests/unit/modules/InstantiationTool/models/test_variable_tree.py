import pytest
from typing import Dict

from PyQt5.QtCore import QModelIndex

from packages.Common.classes.variable import Variable
from packages.Utilities.InstantiationTool.models.variable_tree import VariableTreeModel


@pytest.fixture
def tree_model() -> VariableTreeModel:
  return VariableTreeModel()


@pytest.fixture
def all_variables(mocker):
  return {
      "V_1": mocker.Mock(),
      "V_2": mocker.Mock(),
      "V_3": mocker.Mock(),
      "V_4": mocker.Mock(),
  }


class TestLoadData:
  """Loading the data into the model"""

  def test_load_nothing(
      self,
      mocker,
      tree_model: VariableTreeModel,
      all_variables: Dict[str, Variable],
  ):
    """Nothing"""
    tree_model.load_data()

    assert tree_model.rowCount() == 0

  def test_load_one_variable(
      self,
      mocker,
      tree_model: VariableTreeModel,
      all_variables: Dict[str, Variable],
  ):
    """One variable"""
    tree_model.load_data(all_variables, ["V_1"])

    # Checking that only one element was added
    assert tree_model.rowCount() == 1
    # Checking that the element was correclyt added to the tree
    assert "V_1" in tree_model._id_to_index
    assert tree_model._id_to_index.get("V_1") == tree_model.index(0, 0)

  def test_load_several_variables(
      self,
      mocker,
      tree_model: VariableTreeModel,
      all_variables: Dict[str, Variable],
  ):
    """Several variables"""
    tree_model.load_data(all_variables, all_variables.keys())

    # Checking that only one element was added
    assert tree_model.rowCount() == 4
    # Checking that the element was correclyt added to the tree
    assert "V_1" in tree_model._id_to_index
    assert tree_model._id_to_index.get("V_1") == tree_model.index(0, 0)
    assert "V_2" in tree_model._id_to_index
    assert tree_model._id_to_index.get("V_2") == tree_model.index(1, 0)
    assert "V_3" in tree_model._id_to_index
    assert tree_model._id_to_index.get("V_3") == tree_model.index(2, 0)
    assert "V_4" in tree_model._id_to_index
    assert tree_model._id_to_index.get("V_4") == tree_model.index(3, 0)

  def test_load_variables_after_model_is_populated(
      self,
      mocker,
      tree_model: VariableTreeModel,
      all_variables: Dict[str, Variable],
  ):
    """Several variables"""
    tree_model.load_data(all_variables, ["V_1", "V_2"])
    tree_model.load_data(all_variables, ["V_3", "V_4"])

    # Checking that only one element was added
    assert tree_model.rowCount() == 2
    # Checking that the element was correclyt added to the tree
    assert "V_1" not in tree_model._id_to_index
    assert "V_2" not in tree_model._id_to_index

    assert "V_3" in tree_model._id_to_index
    assert tree_model._id_to_index.get("V_3") == tree_model.index(0, 0)
    assert "V_4" in tree_model._id_to_index
    assert tree_model._id_to_index.get("V_4") == tree_model.index(1, 0)
