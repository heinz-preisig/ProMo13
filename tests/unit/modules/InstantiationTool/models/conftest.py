import pytest
from pytest_mock import MockerFixture
from typing import Dict


from packages.Common.classes.variable import Variable
from packages.Common.classes.entity import Entity
from packages.Common.classes.modeller_classes import (
    TopologyObject, NodeComposite, NodeSimple, Arc
)


class MockNodeComposite(NodeComposite):
  name = None
  parent_id = None


class MockArc(Arc):
  name = None
  parent_id = None

  def get_instantiation_value(self):
    return None


class MockNodeSimple(NodeSimple):
  name = None
  parent_id = None

  def get_instantiation_value(self):
    return None


DATA_VARIABLES = {
    "V_1": {
        "png_path": "Path1",
    },
    "V_2": {
        "png_path": "Path2",
    },
    "V_3": {
        "png_path": "Path3",
    },
    "V_4": {
        "png_path": "Path4",
    },
    "V_5": {
        "png_path": "Path5",
    },
}

DATA_ENTITIES = {
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

DATA_TOPOLOGY_OBJECTS = {
    "N_1": {
        "name": "root",
        "parent": None,
        "modeller_class": MockNodeComposite,
    },
    "N_2": {
        "name": "elem1",
        "parent": "N_1",
        "modeller_class": MockNodeComposite,
    },
    "N_3": {
        "name": "elem2",
        "parent": "N_1",
        "modeller_class": MockNodeSimple,
        "entity_name": "E_1",
        "instantiation_value": None,
    },
    "N_4": {
        "name": "elem1.1",
        "parent": "N_2",
        "modeller_class": MockNodeComposite,
    },
    "A_1": {
        "name": "elem1.2",
        "parent": "N_2",
        "modeller_class": MockArc,
        "entity_name": "E_2",
        "instantiation_value": None,
    },
    "N_5": {
        "name": "elem1.1.1",
        "parent": "N_4",
        "modeller_class": MockNodeSimple,
        "entity_name": "E_3",
        "instantiation_value": None,
    },
}


@pytest.fixture
def all_variables(mocker):
  mock_all_variables = {}
  for var_id, var_data in DATA_VARIABLES.items():
    mock_var = mocker.Mock(spec=Variable)
    mock_var.get_img_path.return_value = var_data.get("png_path")

    mock_all_variables[var_id] = mock_var

  return mock_all_variables


@pytest.fixture
def all_entities(mocker):
  mock_all_entities = {}
  for ent_id, ent_data in DATA_ENTITIES.items():
    mock_ent = mocker.Mock(spec=Entity)
    mock_ent.get_entity_name.return_value = ent_id
    mock_ent.get_init_vars.return_value = ent_data["init_vars"]

    mock_all_entities[ent_id] = mock_ent

  return mock_all_entities


@pytest.fixture
def all_topology_objects(
    mocker: MockerFixture,
    all_entities: Dict[str, Entity],
) -> Dict[str, TopologyObject]:

  mock_topology_objects = {}
  for top_obj_id, obj_data in DATA_TOPOLOGY_OBJECTS.items():
    mock_obj = mocker.Mock(spec_set=obj_data["modeller_class"])
    mock_obj.name = obj_data["name"]
    mock_obj.parent_id = obj_data["parent"]
    if not isinstance(mock_obj, NodeComposite):
      ent_name = obj_data["entity_name"]
      mock_obj.get_instantiation_value.return_value = obj_data[
          "instantiation_value"]
      mock_obj.get_entity_name.return_value = ent_name

      def side_effect_contains_init_var(arg, ent_name=ent_name):
        return arg in all_entities[ent_name].get_init_vars()
      mock_obj.contains_init_var.side_effect = side_effect_contains_init_var

    mock_topology_objects[top_obj_id] = mock_obj

  return mock_topology_objects
