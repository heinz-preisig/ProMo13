import pytest
from pytest_mock import mocker

from typing import Dict

from tests.unit import test_utils

from packages.Common.classes.entity import Entity
from packages.Common.classes.modeller_classes import NodeComposite, NodeSimple, Arc, TopologyObject

from packages.Utilities.InstantiationTool.models.main import MainModel, InvalidEntityError

TEST_FILES = test_utils.get_test_files_path()


@pytest.fixture
def all_entities(mocker):
  info = {
      "E_1": {
          "init_vars": ["V_1", "V_2", "V_3"],
      },
      "E_2": {
          "init_vars": ["V_2", "V_4"]
      },
      "E_3": {
          "init_vars": ["V_5"]
      },
      "E_4": {
          "init_vars": ["V_1", "V_5"]
      }
  }
  mock_all_entities = {}
  for ent_id, ent_data in info.items():
    mock_ent = mocker.Mock(spec=Entity)
    mock_ent.get_entity_name.return_value = ent_id
    mock_ent.get_init_vars.return_value = ent_data.get("init_vars")

    mock_all_entities[ent_id] = mock_ent

  return mock_all_entities


@pytest.fixture
def topology_objects(mocker: mocker, all_entities: Dict[str, Entity]):
  info = {
      "C_root": {
          "modeller_class": NodeComposite,
      },
      "N_1": {
          "modeller_class": NodeSimple,
          "entity_name": "E_1",
      },
      "A_1": {
          "modeller_class": Arc,
          "entity_name": "E_2",
      },
      "C_1": {
          "modeller_class": NodeComposite,
      },
      "N_2": {
          "modeller_class": NodeSimple,
          "entity_name": "E_6",
      }
  }
  mock_topology_objects = {}
  for top_obj_id, data in info.items():
    top_obj_class = data.get("modeller_class")
    mock_obj = mocker.Mock(spec=top_obj_class)

    if not isinstance(mock_obj, NodeComposite):
      ent_name = data.get("entity_name")
      mock_obj.get_entity_name.return_value = ent_name
      if top_obj_id != "N_2":
        # Closure function to store the ent_name value
        def side_effect_contains_init_var(arg, ent_name=ent_name):
          return arg in all_entities.get(ent_name).get_init_vars()
        mock_obj.contains_init_var.side_effect = side_effect_contains_init_var

    mock_topology_objects[top_obj_id] = mock_obj

  return mock_topology_objects


@pytest.fixture
def main_model():
  return MainModel()


class TestDiscoverRequiredVariables:
  """Discovering required variables"""

  def test_only_composite_node(
      self,
      main_model: MainModel,
      all_entities: Dict[str, Entity],
      topology_objects: Dict[str, TopologyObject],
  ):
    """Only composite node"""
    main_model.all_entities = all_entities
    main_model.topology_objects = {
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
