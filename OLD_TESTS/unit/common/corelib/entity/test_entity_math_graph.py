import pytest

from src.common.corelib import Variable, Equation
from src.common.corelib import EntityMathGraph
from src.common.corelib import EquationMap, VariableMap

variable_ids = ["V_1", "V_2", "V_3", "V_4"]
equation_ids = ["E_1", "E_2", "E_3"]
equation_variables = {
    "E_1": ["V_1", "V_2", "V_3"]
}


@pytest.fixture
def math_graph() -> EntityMathGraph:
  return EntityMathGraph()


@pytest.fixture
def variables() -> VariableMap:
  data: VariableMap = {}

  for var_id in variable_ids:
    data[var_id] = Variable(var_id)

  return data


@pytest.fixture
def equations(variables: VariableMap) -> EquationMap:
  data: EquationMap = {}

  for eq_id in equation_ids:
    data[eq_id] = Equation(eq_id)

  data["E_1"].variables = [
      variables[var_id]
      for var_id in equation_variables["E_1"]
  ]

  return data


def test_add_variable(math_graph: EntityMathGraph, variables: VariableMap):
  # SETUP
  expected_output = [variables["V_1"]]
  # ACTION
  math_graph.add_variable(variables["V_1"])

  # COLLECTION
  test_output = math_graph.removable_variables

  # ASSERT
  assert expected_output == test_output, \
      f"\nExpected: \"{expected_output}\",\nObtained: \"{test_output}\""
