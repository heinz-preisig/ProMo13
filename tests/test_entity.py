# pylint: skip-file
import sys
import os
import json

sys.path.insert(0, os.path.abspath("../../../"))
from packages.Common.classes import io
from packages.Common.classes import entity
from packages.Common.classes import equation

def test_dummy():
  """Test with dummy equations and entities."""
  equation_data = [
    ("E_2", "V_1", "V_3 V_4 V_5", "random"),
    ("E_6", "V_3", "V_12 V_5 V_13 V_14", "random"),
    ("E_7", "V_3", "V_12 V_15", "random"),
    ("E_8", "V_3", "V_13 V_16", "random"),
    ("E_9", "V_4", "V_13 V_17 V_5", "random"),
    ("E_10", "V_4", "V_18 V_19", "random"),
    ("E_11", "V_5", "V_17 V_20", "random"),
    ("E_22", "V_13", "V_14 V_21", "random"),
  ]

  all_eq = {}
  for equ_id, lhs, rhs, network in equation_data:
    all_eq[equ_id] = equation.Equation(equ_id, lhs, rhs, network)

  # For the initial tree
  test_entity = entity.Entity.from_root(
    "test_entity",
    "V_1",
    "E_2",
    ["E_6", "E_7", "E_8", "E_9", "E_10", "E_11", "E_22"],
    all_eq,
  )
  test_entity.generate_var_eq_tree({"V_3": ["E_6"]})
  test_entity.update_var_eq_tree()

  test_entity.generate_var_eq_tree({"V_4": ["E_9"]})
  test_entity.update_var_eq_tree()

  test_entity.generate_var_eq_tree({"V_5": ["E_11"]})
  test_entity.update_var_eq_tree()

  test_entity.generate_var_eq_tree({"V_13": ["E_22"]})
  test_entity.update_var_eq_tree()

  # v3: eq6 -> eq7
  test_entity.generate_var_eq_tree({"V_3": ["E_7"]})
  test_entity.update_var_eq_tree()
  # v5: eq11 -> eq6
  test_entity.generate_var_eq_tree({"V_5": ["E_6"]})
  test_entity.update_var_eq_tree()

  print(json.dumps(test_entity, cls=io.EntityJSONEncoder, indent=2))

def test_real_system():
  """Test with current system."""
  path_repository = os.path.abspath("../../../../Ontology_Repository")
  path_ontology = "/".join([path_repository, "ProMo_sandbox6-main"])
  path_equations = "/".join([path_ontology, "equations_global_ID.json"])
  path_entities = "/".join([
    path_ontology,
    "variable_assignment_to_entity_object.json"
  ])
  all_eq = io.load_equations_from_file(path_equations)
  ent_name = "macroscopic.node.event|lumped|mass.test"
  test_entity = io.load_entities_from_old_file(
    path_entities,
    all_eq,
    [ent_name],
  )

  print(json.dumps(test_entity, cls=io.EntityJSONEncoder, indent=2))

test_dummy()
