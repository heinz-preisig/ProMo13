import pytest
from pytest_mock import MockerFixture

from typing import Dict

from tests.unit import test_utils

from packages.Common.classes.entity import Entity
from packages.Common.classes.variable import Variable
from packages.Common.classes.modeller_classes import TopologyObject

from packages.Utilities.InstantiationTool.models.main import (
    MainModel, InvalidEntityError
)

TEST_FILES = test_utils.get_test_files_path()


@pytest.fixture
def main_model(mocker: MockerFixture) -> MainModel:
  model = MainModel()

  model.variable_tree_model = mocker.Mock()
  model.topology_tree_model = mocker.Mock()

  return MainModel()


@pytest.fixture
def mock_io_functions(
    mocker: MockerFixture,
    all_variables: Dict[str, Variable],
    all_entities: Dict[str, Entity],
    topology_objects: Dict[str, TopologyObject],
):
  mock_func1 = mocker.patch(
      "io.load_var_idx_eq_from_file",
      return_value=(all_variables, {}, {})
  )
  mock_func2 = mocker.patch(
      "io.load_entities_from_file",
      return_value=all_entities
  )
  mock_func3 = mocker.patch(
      "io.load_model_from_file",
      return_value=topology_objects
  )

  yield mock_func1, mock_func2, mock_func3


params = [
    (),

]


class TestLoadOntologyInfo:
  """Loading the Ontology Information"""

  @pytest.mark.parametrize("all_topology_objects", [(["N_1"])], indirect=True)
  def test_finding_required_variables(
      self,
      mocker: MockerFixture,
      main_model: MainModel,
      all_variables: Dict[str, Variable],
      mock_io_functions,
  ):
    """Model with only one root composite node"""
    # SETUP
    main_model.variable_tree_model.load_data = mocker.Mock()
    main_model.topology_tree_model.load_data = mocker.Mock()
    assert_str = "For id {top_obj_id}: "\
        "Expected \"{expected}\" value, \""\
        "{result}\" obtained."
    assert_msg = [assert_str]
    var_list = []
    expected_variables = {var_id: all_variables[var_id] for var_id in var_list}
    expected_output = [expected_variables]
    # ACTION
    main_model.load_ontology_info("ontology_name", "model_name")
    # COLLECTION
    test_output = [
        main_model.variable_tree_model.load_data.call_args[0][0],
    ]
    # ASSERT
    zipped_data = zip(ids, expected_output, test_output, assert_msg)
    for top_obj_id, expected, result, msg in zipped_data:
      assert expected == result, \
          msg.format(top_obj_id=top_obj_id, expected=expected, result=result)


class TestDiscoverRequiredVariables:
  """Discovering required variables"""

  def test_only_composite_node(
      self,
      main_model: MainModel,
      all_entities: Dict[str, Entity],
      topology_objects: Dict[str, TopologyObject],
  ):
    """Only composite node"""
    main_model._all_entities = all_entities
    main_model._all_topology_objects = {
        key: topology_objects.get(key)
        for key in ["C_root"]
    }

    main_model._discover_required_variables()

    assert main_model.required_variables == []

  def test_several_objects(
      self,
      main_model: MainModel,
      all_entities: Dict[str, Entity],
      topology_objects: Dict[str, TopologyObject],
  ):
    """Several objects"""
    main_model.all_entities = all_entities
    main_model.topology_objects = {
        key: topology_objects.get(key)
        for key in ["C_root", "N_1", "A_1", "C_1"]
    }

    main_model._discover_required_variables()

    assert main_model.required_variables == sorted(
        ["V_1", "V_2", "V_3", "V_4"])

  def test_object_with_bad_entity(
      self,
      main_model: MainModel,
      all_entities: Dict[str, Entity],
      topology_objects: Dict[str, TopologyObject],
  ):
    """Raising exception for object with unknown entity"""
    main_model.all_entities = all_entities
    main_model.topology_objects = {
        key: topology_objects.get(key)
        for key in ["C_root", "N_1", "A_1", "C_1", "N_2"]
    }

    with pytest.raises(InvalidEntityError):
      main_model._discover_required_variables()


class TestFilterTopologyObjects:
  """Filtering topology objects"""

  def test_variable_not_in_objects(
      self,
      mocker,
      main_model: MainModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Variable not in any object"""
    main_model.all_entities = all_entities
    main_model.topology_objects = {
        key: topology_objects.get(key)
        for key in ["C_root", "N_1", "A_1", "C_1"]
    }
    assert main_model._filter_topology_objects(["V_6"]) == []

  def test_variable_in_one_objects(
      self,
      mocker,
      main_model: MainModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Variable in one object"""
    main_model.all_entities = all_entities
    main_model.topology_objects = {
        key: topology_objects.get(key)
        for key in ["C_root", "N_1", "A_1", "C_1"]
    }
    assert main_model._filter_topology_objects(["V_1"]) == ["N_1"]

  def test_variable_in_multiple_objects(
      self,
      mocker,
      main_model: MainModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Variable in multiple object"""
    main_model.all_entities = all_entities
    main_model.topology_objects = {
        key: topology_objects.get(key)
        for key in ["C_root", "N_1", "A_1", "C_1"]
    }
    assert main_model._filter_topology_objects(["V_2"]) == ["A_1", "N_1"]

  def test_multiple_variables_in_multiple_objects(
      self,
      mocker,
      main_model: MainModel,
      topology_objects: Dict[str, TopologyObject],
  ):
    """Multiple variable in multiple object"""
    main_model.all_entities = all_entities
    main_model.topology_objects = {
        key: topology_objects.get(key)
        for key in ["C_root", "N_1", "A_1", "C_1"]
    }
    assert main_model._filter_topology_objects(["V_1", "V_4"]) == [
        "A_1", "N_1"]

    # TODO: This are more like integration tests. MOVE to appropiate location
    # @pytest.mark.datafiles(
    #     TEST_FILES / 'model.json',
    #     TEST_FILES / 'var_idx_eq.json',
    #     TEST_FILES / 'entities.json',
    # )
    # def test_discover_required_variables(datafiles, main_model: MainModel):
    #   main_model._discover_required_variables()

    #   assert main_model.required_variables == [
    #       'V_100', 'V_110', 'V_15', 'V_164', 'V_182', 'V_6', 'V_66', 'V_7']

    # @pytest.mark.datafiles(
    #     TEST_FILES / 'model.json',
    #     TEST_FILES / 'var_idx_eq.json',
    #     TEST_FILES / 'entities.json',
    # )
    # def test_filter_topology_objects(datafiles, main_model: MainModel):
    #   filtered_topology_objects = main_model._filter_topology_objects(
    #       {"var_id": "V_100"}
    #   )

    #   assert filtered_topology_objects == [
    #       "N_10", "N_11", "N_14", "N_15", "N_3", "N_6", "N_7", "N_8"
    #   ]
