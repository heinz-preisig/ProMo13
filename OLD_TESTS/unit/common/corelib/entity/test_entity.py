from typing import List, Optional, Tuple
import pytest

from tests.conftest import parametrize

from src.common.corelib import Variable, Equation, VariableMap, EquationMap
from src.common.corelib import Entity
from src.common.corelib.entity import VariableState

VARIABLE_COUNT = 10
EQUATION_COUNT = 5
EQ_TO_VAR_MAP = {1: [1, 2, 3], 2: [1, 4, 5], 3: [2, 6, 7], 4: [1, 6, 8]}


@pytest.fixture(name="variables")
def fixture_variables() -> VariableMap:
  data: VariableMap = {}
  for i in range(1, VARIABLE_COUNT):
    var_id = f"V_{i}"
    data[var_id] = Variable(var_id)

  return data


@pytest.fixture(name="equations")
def fixture_equations(variables: VariableMap) -> EquationMap:
  data: EquationMap = {}
  for i in range(1, EQUATION_COUNT):
    eq_id = f"E_{i}"
    data[eq_id] = Equation(eq_id)

  for eq_int, var_list in EQ_TO_VAR_MAP.items():
    eq_id = f"E_{eq_int}"
    data[eq_id].variables = [variables[f"V_{i}"] for i in var_list]

  return data


def make_whole_var_state(
    var_id: str,
    text_state: str,
    eq_id: Optional[str],
    variables: VariableMap,
    equations: EquationMap,
) -> Tuple[Variable, VariableState, Optional[Equation]]:
  var = variables[var_id]
  var_state = VariableState[text_state]
  eq = None
  if eq_id is not None:
    eq = equations[eq_id]

  return (var, var_state, eq)


@pytest.fixture(name="new_entity")
def fixture_new_entity() -> Entity:
  return Entity("E")


@pytest.fixture(name="modified_entity")
def fixture_modified_entity(
    new_entity: Entity,
    variables: VariableMap,
    equations: EquationMap,
    request: pytest.FixtureRequest,
) -> Entity:
  params = request.param
  for var_id in params["add_list"]:
    new_entity.add_new_variable(variables[var_id])

  for data in params["update_list"]:
    var, var_state, eq = make_whole_var_state(*data, variables, equations)
    new_entity.update_variable(var, var_state, eq)

  return new_entity


@pytest.fixture(name="update_data")
def fixture_update_data(
    variables: VariableMap,
    equations: EquationMap,
    request: pytest.FixtureRequest,
) -> Tuple[Variable, VariableState, Optional[Equation]]:
  var, var_state, eq = make_whole_var_state(
      *request.param, variables, equations)

  return (var, var_state, eq)


@pytest.fixture(name="state_and_equation")
def fixture_state_and_equation(
    variables: VariableMap,
    equations: EquationMap,
    request: pytest.FixtureRequest,
) -> Tuple[VariableState, Optional[Equation]]:
  return make_whole_var_state(*request.param, variables, equations)


@pytest.fixture(name="variable_list")
def fixture_variable_list(
    variables: VariableMap,
    request: pytest.FixtureRequest,
) -> List[Variable]:
  return [
      variables[var_id]
      for var_id in request.param
  ]


# Build an entity


def test_entity_creation(new_entity: Entity):
  """# . Make a new entity with basic ontology info"""
  # GIVEN
  # WHEN
  # THEN
  assert True


def test_add_output_variable(new_entity: Entity, variables: VariableMap):
  """# . Add an output variable (default state)"""
  # GIVEN
  new_var = variables["V_1"]
  expected_output = VariableState.OUTPUT
  # WHEN
  new_entity.add_new_variable(new_var)
  test_output = new_entity.get_variable_state(new_var)
  # THEN
  assert test_output == expected_output, \
      f"\nExpected: \"{expected_output}\",\nObtained: \"{test_output}\""


PARAMS = {
    "From OUTPUT to INPUT": [
        {"add_list": ["V_1"], "update_list": []},
        ("V_1", "INPUT", None),
    ],
    "From OUTPUT to INSTANTIATION": [
        {"add_list": ["V_1"], "update_list": []},
        ("V_1", "INSTANTIATION", None),
    ],
    "Adding equation": [
        {"add_list": ["V_1"], "update_list": []},
        ("V_1", "OUTPUT", "E_1"),
    ],
    "Changing an equation": [
        {"add_list": ["V_1"], "update_list": [("V_1", "OUTPUT", "E_1")]},
        ("V_1", "OUTPUT", "E_2"),
    ],
    "Deleting an equation": [
        {"add_list": ["V_1"], "update_list": [("V_1", "OUTPUT", "E_1")]},
        ("V_1", "OUTPUT", None),
    ],
    "Changing state and equation": [
        {"add_list": ["V_1"], "update_list": [("V_1", "OUTPUT", "E_1")]},
        ("V_1", "INPUT", None),
    ],
    "Deleting equations with multiple dependencies": [
        {
            "add_list": ["V_1"],
            "update_list": [
                ("V_1", "OUTPUT", "E_1"),
                ("V_2", "DEPENDENT", "E_3")
            ]
        },
        ("V_1", "INPUT", None),
    ],
    "Changing an equations but keeping some dependencies": [
        {
            "add_list": ["V_1"],
            "update_list": [
                ("V_1", "OUTPUT", "E_1"),
                ("V_2", "DEPENDENT", "E_3")
            ]
        },
        ("V_1", "OUTPUT", "E_4"),
    ],

}

REMAINING_VARIABLES = [
    ("V_1",),
    ("V_1",),
    ("V_1", "V_2", "V_3"),
    ("V_1", "V_4", "V_5"),
    ("V_1",),
    ("V_1",),
    ("V_1",),
    ("V_1", "V_6", "V_8"),
]
PARAMS_EXTENDED = {
    key: PARAMS[key] + [vars]
    for key, vars in zip(PARAMS.keys(), REMAINING_VARIABLES)
}


@pytest.mark.it("# . Update a variable (changes to the updated variable)")
@parametrize(
    "modified_entity, update_data",
    PARAMS,
    indirect=True,
)
def test_update_variable(
    modified_entity: Entity,
    update_data: Tuple[Variable, VariableState, Optional[Equation]],
):
  # GIVEN
  var, var_state, eq = update_data
  expected_output = (var_state, eq)
  # WHEN
  modified_entity.update_variable(*update_data)
  # THEN
  test_output = (
      modified_entity.get_variable_state(var),
      modified_entity.get_equation_for_variable(var),
  )
  assert test_output == expected_output


@pytest.mark.it("# . Update a variable (changes to other variables)")
@parametrize(
    "modified_entity, update_data, variable_list",
    PARAMS_EXTENDED,
    indirect=True,
)
def test_update_variable2(
    modified_entity: Entity,
    update_data: Tuple[Variable, VariableState, Optional[Equation]],
    variable_list: List[Variable],
):
  # GIVEN
  expected_output = variable_list
  # WHEN
  modified_entity.update_variable(*update_data)
  # THEN
  test_output = modified_entity.get_variables()
  assert test_output == expected_output


PARAMS = {
    "Only one output variable": [
        {
            "add_list": ["V_1"],
            "update_list": [
                ("V_1", "OUTPUT", "E_1"),
                ("V_2", "DEPENDENT", "E_3")
            ]
        },
        "V_1",
        [],
    ],
    "Two independent output variables": [
        {
            "add_list": ["V_1", "V_9"],
            "update_list": [
                ("V_1", "OUTPUT", "E_1"),
                ("V_2", "DEPENDENT", "E_3")
            ]
        },
        "V_1",
        ["V_9"],
    ],
    "Two dependent output variables (ALLOWED)": [
        {
            "add_list": ["V_1", "V_2"],
            "update_list": [
                ("V_1", "OUTPUT", "E_1"),
                ("V_2", "OUTPUT", "E_3")
            ]
        },
        "V_1",
        ["V_2", "V_6", "V_7"],
    ],
    "Two dependent output variables (FORBIDDEN)": [
        {
            "add_list": ["V_1", "V_2"],
            "update_list": [
                ("V_1", "OUTPUT", "E_1"),
                ("V_2", "OUTPUT", "E_3")
            ]
        },
        "V_2",
        ["V_2", "V_6", "V_7"],
    ],

}


@pytest.mark.it("# . Remove an output variable")
@parametrize(
    "modified_entity, var_id, variable_list",
    PARAMS,
    indirect=["modified_entity", "variable_list"],
)
def test_delete_variable(
    modified_entity: Entity,
    var_id: str,
    variable_list: List[Variable],
    variables: VariableMap,
):
  # GIVEN
  var = variables[var_id]
  expected_output = variable_list
  # WHEN
  modified_entity.remove_variable(var)
  # THEN
  test_output = modified_entity.get_variables()
  assert test_output == expected_output

# . Remove an ouput variable
#
# Save an entity
# Load an entity

# Maybe for regression tests
# . Add a variable that already exist (error)
