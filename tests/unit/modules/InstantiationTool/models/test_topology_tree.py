import pytest
from pytest_mock import MockerFixture
from typing import Dict

from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt

from packages.Common.classes.modeller_classes import TopologyObject, NodeComposite, NodeSimple, Arc
from packages.Utilities.InstantiationTool.models.topology_tree import TopologyTreeModel, NAME_ROLE, CLASS_ROLE


@pytest.fixture
def tree_model() -> TopologyTreeModel:
  return TopologyTreeModel()


@pytest.fixture
def topology_objects(mocker: MockerFixture) -> Dict[str, TopologyObject]:
  data = {
      "N_1": {
          "name": "root",
          "parent": None,
          "modeller_class": NodeComposite,
      },
      "N_2": {
          "name": "elem1",
          "parent": "N_1",
          "modeller_class": NodeComposite,
      },
      "N_3": {
          "name": "elem2",
          "parent": "N_1",
          "modeller_class": NodeSimple,
          "instantiation_value": None,
      },
      "N_4": {
          "name": "elem1.1",
          "parent": "N_2",
          "modeller_class": "NodeComposite",
      },
      "A_1": {
          "name": "elem1.2",
          "parent": "N_2",
          "modeller_class": Arc,
          "instantiation_value": None,
      },
      "N_5": {
          "name": "elem1.1.1",
          "parent": "N_4",
          "modeller_class": NodeSimple,
          "instantiation_value": None,
      },
  }

  mock_topology_objects = {}
  for obj_id, obj_data in data.items():
    mock_obj = mocker.Mock(spec_set=obj_data["modeller_class"])
    mock_obj.get_name.return_value = obj_data["name"]
    mock_obj.get_parent_id.return_value = obj_data["parent"]
    if not isinstance(mock_obj, NodeComposite):
      mock_obj.get_instantiation_value.return_value = obj_data[
        "instantiation_value"]

    mock_topology_objects[obj_id] = mock_obj
  
  return mock_topology_objects


@pytest.fixture
def tree_model_with_data(
    tree_model: TopologyTreeModel,
    topology_objects: Dict[str, TopologyObject]
) -> TopologyTreeModel:
  tree_model.topology_objects = topology_objects
  return tree_model


class TestAddItem:
  """Adding items to the model"""

  def test_parenthood_add_root(
      self,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking parenthood when adding root item"""
    # Setup
    item_id = "N_1"

    # Action
    tree_model_with_data.add_item(item_id)

    # Test
    main_index = tree_model_with_data._id_to_index.get(item_id)

    assert main_index.parent() == QModelIndex(), "Item is not top level."

  def test_parenthood_add_non_root_item(
      self,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking parenthood when adding non root item"""
    # Setup
    tree_model_with_data.add_item("N_1")
    item_id = "N_2"

    # Action
    tree_model_with_data.add_item(item_id)

    # Test
    parent_index = tree_model_with_data._id_to_index.get("N_1")
    item_index = tree_model_with_data._id_to_index.get(item_id)

    assert item_index.parent() == parent_index, "Added with wrong parent"

  def test_data_add_composite_node(
      self,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking the data of an added composite node"""
    # Setup
    item_id = "N_1"

    # Action
    tree_model_with_data.add_item(item_id)

    # Test
    main_index = tree_model_with_data._id_to_index.get(item_id)
    instantiation_index = main_index.siblingAtColumn(1)

    errors = []
    if main_index.data(NAME_ROLE) != "root":
      errors.append("NAME_ROLE assigned incorrectly.")
    if main_index.data(CLASS_ROLE) != "NodeComposite":
      errors.append("CLASS_ROLE assigned incorrectly.")
    if instantiation_index.data() is not None:
      errors.append("Instantiation value inserted wrongly.")

    formatted_errors = "\n".join(errors)
    assert not errors, f"Errors occurred:\n{formatted_errors}"

  def test_data_add_non_composite_node(
      self,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking the data of an added non composite node"""
    # Setup
    tree_model_with_data.add_item("N_1")
    item_id = "N_3"

    # Action
    tree_model_with_data.add_item(item_id)

    # Test
    main_index = tree_model_with_data._id_to_index.get(item_id)
    instantiation_index = main_index.siblingAtColumn(1)

    errors = []
    if main_index.data(NAME_ROLE) != "elem2":
      errors.append("NAME_ROLE assigned incorrectly.")
    if main_index.data(CLASS_ROLE) != "NodeSimple":
      errors.append("CLASS_ROLE assigned incorrectly.")
    if instantiation_index.data() is None:
      errors.append("Instantiation value inserted wrongly.")

    formatted_errors = "\n".join(errors)
    assert not errors, f"Errors occurred:\n{formatted_errors}"


class TestAddAncestors:
  """Adding ancestors to the model"""

  def test_no_ancestor_added(
      self,
      mocker: MockerFixture,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking item with no ancestors (root)"""
    # Setup
    tree_model_with_data.add_item = mocker.Mock()
    item_id = "N_1"

    # Action
    tree_model_with_data.add_ancestors(item_id)

    # Test
    msg = "add_item method called"
    tree_model_with_data.add_item.assert_not_called(), msg

  def test_one_ancestor_added(
      self,
      mocker: MockerFixture,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking item with one ancestor"""
    # Setup
    tree_model_with_data.add_item = mocker.Mock()
    item_id = "N_2"

    # Action
    tree_model_with_data.add_ancestors(item_id)

    # Test
    msg = "More than one call to add_item method"
    tree_model_with_data.add_item.assert_called_once_with("N_1"), msg

  def test_multiple_ancestors_added(
      self,
      mocker: MockerFixture,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking item with multiple ancestors"""
    # Setup
    tree_model_with_data.add_item = mocker.Mock()
    item_id = "N_5"

    # Action
    tree_model_with_data.add_ancestors(item_id)

    # Test
    errors = []
    call_count = tree_model_with_data.add_item.call_count
    if call_count != 3:
      errors.append(
          f"add_item method called {call_count} times instead of 3")

    expected_args_list = [("N_1",), ("N_2",), ("N_4",)]
    calls_list = tree_model_with_data.add_item.call_args_list
    for i, (args, kwargs) in enumerate(calls_list):
      expected_args = expected_args_list[i]
      if args != expected_args:
        errors.append(f"On call #{i} of add_item method\n"
                      f"Unexpected args: {expected_args}\n"
                      f"Expected args: {args}")

    formatted_errors = "\n".join(errors)
    assert not errors, f"Errors occurred:\n{formatted_errors}"

  def test_ancestor_already_present(
      self,
      mocker: MockerFixture,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking item with ancestor already in the model"""
    # Setup
    tree_model_with_data.add_item("N_1")
    tree_model_with_data.add_item = mocker.Mock()
    item_id = "N_2"

    # Action
    tree_model_with_data.add_ancestors(item_id)

    # Test
    msg = "add_item method called"
    tree_model_with_data.add_item.assert_not_called(), msg

  def test_some_ancestors_already_present(
      self,
      mocker: MockerFixture,
      tree_model_with_data: TopologyTreeModel,
  ):
    """Checking item with some ancestors already in the model"""
    # Setup
    tree_model_with_data.add_item("N_1")
    tree_model_with_data.add_item = mocker.Mock()
    item_id = "N_4"

    # Action
    tree_model_with_data.add_ancestors(item_id)

    # Test
    errors = []
    call_count = tree_model_with_data.add_item.call_count
    expected_call_count = 1
    if call_count != expected_call_count:
      errors.append(
          f"add_item method called {call_count} times instead of"
          f"{expected_call_count}"
      )

    expected_args_list = [("N_2",)]
    calls_list = tree_model_with_data.add_item.call_args_list
    for i, (args, kwargs) in enumerate(calls_list):
      expected_args = expected_args_list[i]
      if args != expected_args:
        errors.append(f"On call #{i} of add_item method\n"
                      f"Unexpected args: {expected_args}\n"
                      f"Expected args: {args}")

    formatted_errors = "\n".join(errors)
    assert not errors, f"Errors occurred:\n{formatted_errors}"


class TestLoadData:
  """Loading the data into the model"""

  def test_load_only_root(
      self,
      mocker: MockerFixture,
      tree_model: TopologyTreeModel,
      components_data: Dict[str, Dict[str, str]],
  ):
    """Data contains only on item"""
    # Setup
    spy_add_item = mocker.spy(tree_model, "add_item")
    spy_add_parents = mocker.spy(tree_model, "add_parents")
    ids_list = ["N_1"]
    test_data = {
        item_id: components_data.get(item_id)
        for item_id in ids_list
    }

    # Action
    tree_model.load_data(test_data)

    # Test
    errors = []
    if tree_model.rowCount != 1:
      errors.append("")
    # Checking that only one element was added
    assert tree_model.rowCount() == 1
    # Checking that the add_parents function is called only once
    spy_add_parents.assert_called_once_with("root")
    # Checking that the add_items function is called only once
    spy_add_item.assert_called_once_with(None, "root")

  def test_load_one_branch(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """One branch"""
    spy_add_item = mocker.spy(tree_model, "add_item")
    spy_add_parents = mocker.spy(tree_model, "add_parents")

    tree_model.load_data(topology_objects, ["elem1.1.1"])

    # Checking the function calls
    spy_add_item.assert_any_call(None, "root")
    spy_add_item.assert_any_call("root", "elem1")
    spy_add_item.assert_any_call("elem1", "elem1.1")
    spy_add_item.assert_any_call("elem1.1", "elem1.1.1")
    assert spy_add_item.call_count == 4

    spy_add_parents.assert_any_call("elem1.1.1")
    spy_add_parents.assert_any_call("elem1.1")
    spy_add_parents.assert_any_call("elem1")
    spy_add_parents.assert_any_call("root")
    assert spy_add_parents.call_count == 4

    # Checking that all elements have the correct parents
    for child_id in ["elem1.1.1", "elem1.1", "elem1", "root"]:
      parent_id = topology_objects.get(child_id).get_parent_id()

      child_index = tree_model._id_to_index.get(child_id)
      if parent_id is None:
        parent_index = QModelIndex()
      else:
        parent_index = tree_model._id_to_index.get(parent_id)

      assert child_index.parent() == parent_index

  def test_load_second_branch(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Second branch after one is already in (common ancestor)"""
    spy_add_item = mocker.spy(tree_model, "add_item")
    spy_add_parents = mocker.spy(tree_model, "add_parents")

    tree_model.load_data(topology_objects, ["elem1.1.1", "elem2"])

    # Checking the function calls
    spy_add_item.assert_any_call(None, "root")
    spy_add_item.assert_any_call("root", "elem1")
    spy_add_item.assert_any_call("elem1", "elem1.1")
    spy_add_item.assert_any_call("elem1.1", "elem1.1.1")
    spy_add_item.assert_any_call("root", "elem2")
    assert spy_add_item.call_count == 5

    spy_add_parents.assert_any_call("elem1.1.1")
    spy_add_parents.assert_any_call("elem1.1")
    spy_add_parents.assert_any_call("elem1")
    spy_add_parents.assert_any_call("root")
    spy_add_parents.assert_any_call("elem2")
    assert spy_add_parents.call_count == 5

    # Checking that all elements have the correct parents
    for child_id in ["elem1.1.1", "elem1.1", "elem1", "root", "elem2"]:
      parent_id = topology_objects.get(child_id).get_parent_id()

      child_index = tree_model._id_to_index.get(child_id)
      if parent_id is None:
        parent_index = QModelIndex()
      else:
        parent_index = tree_model._id_to_index.get(parent_id)

      assert child_index.parent() == parent_index

  def test_load_whole_tree(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """The whole tree"""
    spy_add_item = mocker.spy(tree_model, "add_item")
    spy_add_parents = mocker.spy(tree_model, "add_parents")

    tree_model.load_data(topology_objects, ["elem1.1.1", "elem1.2", "elem2"])

    # Checking the function calls
    spy_add_item.assert_any_call(None, "root")
    spy_add_item.assert_any_call("root", "elem1")
    spy_add_item.assert_any_call("elem1", "elem1.1")
    spy_add_item.assert_any_call("elem1.1", "elem1.1.1")
    spy_add_item.assert_any_call("root", "elem2")
    spy_add_item.assert_any_call("elem1", "elem1.2")
    assert spy_add_item.call_count == 6

    spy_add_parents.assert_any_call("elem1.1.1")
    spy_add_parents.assert_any_call("elem1.1")
    spy_add_parents.assert_any_call("elem1")
    spy_add_parents.assert_any_call("root")
    spy_add_parents.assert_any_call("elem2")
    spy_add_parents.assert_any_call("elem1.2")
    assert spy_add_parents.call_count == 6

    # Checking that all elements have the correct parents
    for child_id in topology_objects:
      parent_id = topology_objects.get(child_id).get_parent_id()

      child_index = tree_model._id_to_index.get(child_id)
      if parent_id is None:
        parent_index = QModelIndex()
      else:
        parent_index = tree_model._id_to_index.get(parent_id)

      assert child_index.parent() == parent_index

  def test_load_data_on_a_populated_model(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Data after the model has been populated once"""
    tree_model.load_data(topology_objects, ["elem1.1.1", "elem1.2"])
    tree_model.load_data(topology_objects, ["elem1.1.1", "elem2"])

    # Checking that the dictionary have the right elements
    assert sorted(list(tree_model._id_to_index.keys())) == sorted(
        ["root", "elem1", "elem2", "elem1.1", "elem1.1.1"])

    # Checking that the model has the right number of elements at every level
    assert tree_model.rowCount() == 1
    assert tree_model.rowCount(tree_model._id_to_index.get("root")) == 2
    assert tree_model.rowCount(tree_model._id_to_index.get("elem1")) == 1
    assert tree_model.rowCount(tree_model._id_to_index.get("elem1.1")) == 1
    assert tree_model.rowCount(tree_model._id_to_index.get("elem1.1.1")) == 0
    assert tree_model.rowCount(tree_model._id_to_index.get("elem2")) == 0


CHECKED = Qt.CheckState.Checked
PARTIALLY_CHECKED = Qt.CheckState.PartiallyChecked
UNCHECKED = Qt.CheckState.Unchecked


class TestCheckPropagation:
  """Propagating the checking of items"""

  def test_propagating_down_on_bottom_item(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating down with bottom item changed"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    bottom_item_index = tree_model._id_to_index.get("elem1.1.1")
    bottom_item = tree_model.itemFromIndex(bottom_item_index)
    print(bottom_item)
    bottom_item.setCheckState(Qt.CheckState.Checked)
    # tree_model.propagate_check_state_down(bottom_item)

    assert bottom_item.checkState() == Qt.CheckState.Checked

  def test_propagating_down_on_middle_item(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating down with middle item changed"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("elem1")
    test_item = tree_model.itemFromIndex(test_item_index)
    test_item.setCheckState(Qt.CheckState.Checked)
    # tree_model.propagate_check_state_down(bottom_item)

    for item_id in ["elem1", "elem1.1", "elem1.2", "elem1.1.1"]:
      item_index = tree_model._id_to_index.get(item_id)
      item = tree_model.itemFromIndex(item_index)
      assert item.checkState() == Qt.CheckState.Checked

  def test_propagating_down_on_top_item(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating down with top item changed"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("root")
    test_item = tree_model.itemFromIndex(test_item_index)
    test_item.setCheckState(Qt.CheckState.Checked)
    # tree_model.propagate_check_state_down(bottom_item)

    for item_id in topology_objects.keys():
      item_index = tree_model._id_to_index.get(item_id)
      item = tree_model.itemFromIndex(item_index)
      assert item.checkState() == Qt.CheckState.Checked

  def test_propagating_up_on_top_item(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up with top item changed"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("root")
    test_item = tree_model.itemFromIndex(test_item_index)
    test_item.setCheckState(Qt.CheckState.Checked)

    spy_propagate_check_state_up = mocker.spy(
        tree_model, "propagate_check_state_up")

    assert test_item.checkState() == Qt.CheckState.Checked
    spy_propagate_check_state_up.assert_not_called()

  def test_propagating_up_children_checked_and_unchecked(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up when children are checked and unchecked"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("elem1")
    test_item = tree_model.itemFromIndex(test_item_index)
    test_item.setCheckState(Qt.CheckState.Checked)

    assert test_item.checkState() == Qt.CheckState.Checked
    assert test_item.parent().checkState() == Qt.CheckState.PartiallyChecked

  def test_propagating_up_children_checked(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up when children are checked"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("root")
    test_item = tree_model.itemFromIndex(test_item_index)

    for row in range(test_item.rowCount()):
      child_item = test_item.child(row)
      child_item.setCheckState(Qt.CheckState.Checked)

    assert test_item.checkState() == Qt.CheckState.Checked

  def test_propagating_up_children_unchecked(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up when children are unchecked"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("root")
    test_item = tree_model.itemFromIndex(test_item_index)

    for row in range(test_item.rowCount()):
      child_item = test_item.child(row)
      child_item.setCheckState(Qt.CheckState.Unchecked)

    assert test_item.checkState() == Qt.CheckState.Unchecked

  def test_propagating_up_children_partially_checked(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up when one children is partially checked"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("root")
    test_item = tree_model.itemFromIndex(test_item_index)

    child_item = test_item.child(0)
    child_item.setCheckState(Qt.CheckState.PartiallyChecked)

    assert test_item.checkState() == Qt.CheckState.PartiallyChecked

  def test_propagating_up_from_the_bottom(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up when the bottom children gets checked"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("elem1.1.1")
    test_item = tree_model.itemFromIndex(test_item_index)
    test_item.setCheckState(CHECKED)

    ids = ["root", "elem1", "elem1.1"]
    results = [PARTIALLY_CHECKED, PARTIALLY_CHECKED, CHECKED]
    for item_id, result in zip(ids, results):
      item_index = tree_model._id_to_index.get(item_id)
      item = tree_model.itemFromIndex(item_index)
      assert item.checkState() == result

  def test_propagating_up_children_partially_checked(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up when one children is partially checked"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("root")
    test_item = tree_model.itemFromIndex(test_item_index)

    child_item = test_item.child(0)
    child_item.setCheckState(Qt.CheckState.PartiallyChecked)

    assert test_item.checkState() == Qt.CheckState.PartiallyChecked

  def test_propagating_up_and_down_from_the_middle(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up and down from the middle"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    test_item_index = tree_model._id_to_index.get("elem1.1")
    test_item = tree_model.itemFromIndex(test_item_index)
    test_item.setCheckState(CHECKED)

    results_data = [
        ("root", PARTIALLY_CHECKED),
        ("elem1", PARTIALLY_CHECKED),
        ("elem1.1", CHECKED),
        ("elem1.1.1", CHECKED),
        ("elem1.2", UNCHECKED),
        ("elem2", UNCHECKED)
    ]
    for item_id, result in results_data:
      item_index = tree_model._id_to_index.get(item_id)
      item = tree_model.itemFromIndex(item_index)
      assert item.checkState() == result

  def test_propagating_up_and_down_from_the_middle_with_previous_checking(
      self,
      mocker,
      tree_model: TopologyTreeModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Propagating up and down from the middle with previous checking"""
    tree_model.load_data(topology_objects, topology_objects.keys())
    prev_item_index = tree_model._id_to_index.get("elem2")
    prev_item = tree_model.itemFromIndex(prev_item_index)
    prev_item.setCheckState(CHECKED)

    test_item_index = tree_model._id_to_index.get("elem1.1")
    test_item = tree_model.itemFromIndex(test_item_index)
    test_item.setCheckState(CHECKED)

    results_data = [
        ("root", PARTIALLY_CHECKED),
        ("elem1", PARTIALLY_CHECKED),
        ("elem1.1", CHECKED),
        ("elem1.1.1", CHECKED),
        ("elem1.2", UNCHECKED),
        ("elem2", CHECKED)
    ]
    for item_id, result in results_data:
      item_index = tree_model._id_to_index.get(item_id)
      item = tree_model.itemFromIndex(item_index)
      assert item.checkState() == result
