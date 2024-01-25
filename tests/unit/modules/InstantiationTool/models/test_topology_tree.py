"""
Module-level docstring

This module contains tests for the functionality in topology_tree.py.

Prerequisites:
- The testing framework and plugins are installed:
  * pytest
  * pytest_mock

Author: Alberto Rodriguez Fernandez
"""
import pytest
from typing import Dict, List

from PyQt5.QtCore import Qt

from packages.Common.classes.modeller_classes import TopologyObject
from packages.Utilities.InstantiationTool.models.topology_tree import TopologyTreeModel
from packages.shared_components import roles


CHECKED = Qt.CheckState.Checked
PARTIALLY_CHECKED = Qt.CheckState.PartiallyChecked
UNCHECKED = Qt.CheckState.Unchecked


@pytest.fixture
def tree_model(
    all_topology_objects: Dict[str, TopologyObject],
    request,
) -> TopologyTreeModel:
  is_preloaded = request.param

  model = TopologyTreeModel()

  if is_preloaded:
    model.load_data(all_topology_objects, list(all_topology_objects.keys()))

  return model


class TestLoadData:
  """Loading the data into the model"""
  PARAMS = [
      (False, [], [], [], "nothing"),
      (False, ["N_1"], ["N_1"], ["root"], "only the root"),
      (
          False,
          ["N_5"],
          ["N_1", "N_2", "N_4", "N_5"],
          ["root", "elem1", "elem1.1", "elem1.1.1"],
          "whole branch"
      ),
      (
          False,
          ["N_3", "N_5"],
          ["N_1", "N_2", "N_3", "N_4", "N_5"],
          ["root", "elem1", "elem2", "elem1.1", "elem1.1.1"],
          "two branches with common ancestor"
      ),
      (
          False,
          ["N_3", "A_1", "N_5"],
          ["N_1", "N_2", "N_3", "N_4", "A_1", "N_5"],
          ["root", "elem1", "elem2", "elem1.1", "elem1.2", "elem1.1.1"],
          "full tree"
      ),
      (
          True,
          ["N_5"],
          ["N_1", "N_2", "N_4", "N_5"],
          ["root", "elem1", "elem1.1", "elem1.1.1"],
          "branch after having a full tree"
      ),
  ]

  @pytest.mark.parametrize(
      (
          "tree_model",
          "filtered_list",
          "expected_obj_ids",
          "expected_output",
          "case_name",
      ),
      PARAMS,
      indirect=["tree_model"])
  def test_loading_data(
      self,
      tree_model: TopologyTreeModel,
      all_topology_objects: Dict[str, TopologyObject],
      filtered_list: List[str],
      expected_obj_ids: List[str],
      expected_output: List[str],
      case_name: str,
  ):
    """Loading data"""
    # SETUP
    assert_case = f"On loading \"{case_name}\":: "
    assert_str = assert_case +\
        "Expected \"{expected}\" text, \"{result}\" obtained."

    assert_msgs = [assert_str] * len(expected_obj_ids)

    # ACTION
    tree_model.load_data(all_topology_objects, filtered_list)
    # COLLECTION
    test_output = []
    for top_obj_id in expected_obj_ids:
      index = tree_model.get_index_from_id(top_obj_id)
      item = tree_model.itemFromIndex(index)
      test_output.append(item.data(roles.NAME_ROLE))
    # ASSERT
    for expected, result, msg in zip(expected_output, test_output, assert_msgs):
      assert expected == result, msg.format(expected=expected, result=result)


@pytest.fixture
def setup_checked_model(
    request,
    tree_model: TopologyTreeModel
) -> TopologyTreeModel:
  for top_obj_id, check_value in request.param:
    item_index = tree_model.get_index_from_id(top_obj_id)
    item = tree_model.itemFromIndex(item_index)
    item.setCheckState(check_value)

  return tree_model


class TestCheckPropagation:
  """Propagating the checking of items"""

  # Simplified way of representing the checked status of the tree.
  # + Means CHECKED
  # - Means UNCHECKED
  # * Means PARTIALLYCHECKED
  # () Indicates the change that is being tested.
  # The third element in params indicate the initial state and the
  # change that will be tested.
  # The last element in params indicate the expected state.
  PARAMS = [
      ([], True, "(+)-----", "N_1", CHECKED, "++++++"),
      ([], True, "-----(+)", "N_5", CHECKED, "**-+-+"),
      ([], True, "-(+)----", "N_2", CHECKED, "*+-+++"),
      ([("N_2", CHECKED)], True, "*+-+(-)+", "A_1", UNCHECKED, "**-+-+"),
      ([("N_2", CHECKED)], True, "*+(+)+++", "N_3", CHECKED, "++++++"),
  ]

  @pytest.mark.parametrize(
      (
          "setup_checked_model",
          "tree_model",
          "initial_config",
          "test_id",
          "test_check_status",
          "expected_output"
      ),
      PARAMS,
      indirect=["setup_checked_model", "tree_model"]
  )
  def test_propagating_from_different_items(
      self,
      setup_checked_model: TopologyTreeModel,
      initial_config: str,
      test_id: str,
      test_check_status,
      expected_output: str,
  ):
    """Propagating from different items"""
    # SETUP
    test_item_index = setup_checked_model.get_index_from_id(test_id)
    test_item = setup_checked_model.itemFromIndex(test_item_index)
    header_str = f"Initial config: {initial_config}.\n"
    assert_str = header_str + "For id {top_obj_id}: "\
        "Expected \"{expected}\" value, \""\
        "{result}\" obtained."
    assert_msg = [assert_str] * 6
    # ACTION
    test_item.setCheckState(test_check_status)
    # COLLECTION
    test_output = []
    ids = ["N_1", "N_2", "N_3", "N_4", "A_1", "N_5"]
    for top_obj_id in ids:
      collection_index = setup_checked_model.get_index_from_id(top_obj_id)
      collection_item = setup_checked_model.itemFromIndex(collection_index)
      collection_item_state = collection_item.checkState()
      if collection_item_state == CHECKED:
        test_output.append("+")
      elif collection_item_state == UNCHECKED:
        test_output.append("-")
      elif collection_item_state == PARTIALLY_CHECKED:
        test_output.append("*")
    # ASSERT
    zipped_data = zip(ids, expected_output, test_output, assert_msg)
    for top_obj_id, expected, result, msg in zipped_data:
      assert expected == result, \
          msg.format(top_obj_id=top_obj_id, expected=expected, result=result)
