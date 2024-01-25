"""
Module-level docstring

This module contains tests for the functionality in variable_tree.py.

Prerequisites:
- The testing framework and plugins are installed:
  * pytest
  * pytest_mock

Author: Alberto Rodriguez Fernandez
"""
import pytest
from typing import Dict

from packages.Common.classes.variable import Variable
from packages.Utilities.InstantiationTool.models.variable_tree import VariableTreeModel


@pytest.fixture
def tree_model() -> VariableTreeModel:
  return VariableTreeModel()


@pytest.fixture
def variables(mocker) -> Dict[str, Variable]:
  return {
      "V_1": mocker.Mock(spec=Variable),
      "V_2": mocker.Mock(spec=Variable),
      "V_3": mocker.Mock(spec=Variable),
      "V_4": mocker.Mock(spec=Variable),
  }

class TestLoadData:
  """Loading the data into the model"""

  def test_load_nothing(
      self,
      tree_model: VariableTreeModel,
  ):
    """Nothing"""
    # SETUP
    expected_output = [0]
    assert_msg = ["Expected {expected} element inserted, {result} obtained."]
    # ACTION
    tree_model.load_data()
    # COLLECTION
    test_output = [tree_model.rowCount()]
    # ASSERT
    for expected, result, msg in zip(expected_output, test_output, assert_msg):
      assert expected == result, msg.format(expected=expected, result=result)

  def test_load_one_variable(
      self,
      mocker,
      tree_model: VariableTreeModel,
      variables: Dict[str, Variable],
  ):
    """One variable"""
    # SETUP
    key_list = ["V_1"]
    filtered_variables = {key: variables[key] for key in key_list}
    expected_output = [1, "V_1"]
    assert_msg = [
      "Expected {expected} element inserted, {result} obtained.",
      "Expected \"{expected}\" text, \"{result}\" obtained."
    ]
    # ACTION
    tree_model.load_data(filtered_variables)
    # COLLECTION
    test_output = [
      tree_model.rowCount(),
      tree_model.item(0).text()
    ]
    # ASSERT
    for expected, result, msg in zip(expected_output, test_output, assert_msg):
      assert expected == result, msg.format(expected=expected, result=result)

  def test_load_several_variables(
      self,
      tree_model: VariableTreeModel,
      variables: Dict[str, Variable]
  ):
    """Several variables"""
    # SETUP
    expected_output = [4, "V_1", "V_2", "V_3", "V_4"]
    assert_msg = [
      "Expected {expected} element inserted, {result} obtained.",
      "Expected \"{expected}\" text in position 0, \"{result}\" obtained.",
      "Expected \"{expected}\" text in position 1, \"{result}\" obtained.",
      "Expected \"{expected}\" text in position 2, \"{result}\" obtained.",
      "Expected \"{expected}\" text in position 3, \"{result}\" obtained.",
    ]
    # ACTION
    tree_model.load_data(variables)
    # COLLECTION
    test_output = [
      tree_model.rowCount(),
      tree_model.item(0).text(),
      tree_model.item(1).text(),
      tree_model.item(2).text(),
      tree_model.item(3).text(),
    ]
    # ASSERT
    for expected, result, msg in zip(expected_output, test_output, assert_msg):
      assert expected == result, msg.format(expected=expected, result=result)

  def test_load_variables_after_model_is_populated(
      self,
      mocker,
      tree_model: VariableTreeModel,
      variables: Dict[str, Variable],
  ):
    """Variables after the model is populated"""
    # SETUP
    key_list = ["V_1", "V_2"]
    filtered_variables = {key: variables[key] for key in key_list}
    tree_model.load_data(filtered_variables)
    key_list = ["V_3", "V_4"]
    filtered_variables = {key: variables[key] for key in key_list}

    expected_output = [2, "V_3", "V_4"]
    assert_msg = [
      "Expected {expected} element inserted, {result} obtained.",
      "Expected \"{expected}\" text in position 0, \"{result}\" obtained.",
      "Expected \"{expected}\" text in position 1, \"{result}\" obtained.",
    ]
    # ACTION
    tree_model.load_data(filtered_variables)
    # COLLECTION
    test_output = [
      tree_model.rowCount(),
      tree_model.item(0).text(),
      tree_model.item(1).text(),
    ]
    # ASSERT
    for expected, result, msg in zip(expected_output, test_output, assert_msg):
      assert expected == result, msg.format(expected=expected, result=result)

