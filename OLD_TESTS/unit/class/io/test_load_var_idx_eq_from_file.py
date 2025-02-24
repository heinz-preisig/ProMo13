from datetime import datetime
import pytest

from tests.unit import test_utils


TEST_FILES = test_utils.get_test_files_path()


@pytest.mark.datafiles(TEST_FILES / 'var_idx_eq.json')
def test_load_var_idx_eq_from_file(datafiles, var_idx_eq):

  all_variables, all_indices, all_equations = var_idx_eq
  ######################################################################
  ########################### Variables tests ##########################
  ######################################################################
  # Test variable V_1
  var_test = all_variables.get("V_1")
  assert var_test.var_id == "V_1"
  assert var_test.IRI == "promo:value"
  assert var_test.aliases == {
      "global_ID": "V_1",
      "python": "value",
      "cpp": "value",
      "matlab": "value",
      "latex": "\\#",
      "internal_code": "value"
  }
  date_format = "%Y-%m-%d %H:%M:%S"
  assert var_test.created == datetime.strptime(
      "2023-09-06 09:59:12", date_format)

  assert var_test.doc == "numerical value"
  assert var_test.equations == []
  assert var_test.index_structures == []
  assert var_test.label == "value"
  assert var_test.network == "root"
  assert var_test.port_variable == True
  assert var_test.tokens == []
  assert var_test.type == "constant"
  assert var_test.units == [0, 0, 0, 0, 0, 0, 0, 0]

  # Test variable V_97
  var_test = all_variables.get("V_97")
  assert var_test.var_id == "V_97"
  assert var_test.IRI == "promo:d"
  assert var_test.aliases == {
      "global_ID": "V_97",
      "python": "d",
      "cpp": "d",
      "matlab": "d",
      "latex": "d",
      "internal_code": "d"
  }
  assert var_test.doc == "flow direction of convectional flow"
  assert var_test.equations == ["E_72"]
  assert var_test.index_structures == ["I_2"]
  assert var_test.label == "d"
  assert var_test.network == "macroscopic"
  assert var_test.port_variable == False
  assert var_test.tokens == []
  assert var_test.type == "transport"
  assert var_test.units == [0, 0, 0, 0, 0, 0, 0, 0]

  ######################################################################
  ########################### Equations tests ##########################
  ######################################################################
  eq_test = all_equations.get("E_72")
  assert eq_test.eq_id == "E_72"
  assert eq_test.rhs == {
      "global_ID": " F_16 D_0 V_8  O_5  I_1 O_5  V_17 D_1",
      "matlab": "sign(reduceproduct(F_N_A(N, A), \"N\", p(N)))",
      "latex": "\\text{sign} \\left( {F}{_{N, A}} \\stackrel{N}{\\,\\star\\,} {p}{_{N}} \\right)"
  }
  assert eq_test.type == "generic"
  assert eq_test.doc == "flow direction of convectional flow"
  assert eq_test.network == "macroscopic"
  assert eq_test.lhs == {
      "global_ID": "V_97",
      "matlab": "d(A)",
      "latex": "{d}{_{A}}"
  }

  ######################################################################
  ########################### Indices tests ############################
  ######################################################################

  idx_test = all_indices.get("I_1")
  assert idx_test.type == "index"
  assert idx_test.label == "node"
  assert idx_test.network == [
      "root",
      "physical",
      "reactions",
      "material",
      "macroscopic",
      "solid",
      "fluid",
      "liquid",
      "gas",
      "control"
  ]
  assert idx_test.aliases == {
      "global_ID": "I_1",
      "python": "N",
      "cpp": "N",
      "matlab": "N",
      "latex": "N",
      "internal_code": "N"
  }
  assert idx_test.iri == "promo:node"
  assert idx_test.indices == []

  idx_test = all_indices.get("I_5")
  assert idx_test.type == "block_index"
  assert idx_test.label == "node & species"
  assert idx_test.network == [
      "physical",
      "reactions",
      "material",
      "macroscopic",
      "solid",
      "fluid",
      "liquid",
      "gas"
  ]
  assert idx_test.aliases == {
      "global_ID": "I_5",
      "python": "N_x_S",
      "cpp": "N_x_S",
      "matlab": "N_x_S",
      "latex": "{N S}",
      "internal_code": "N & S"
  }
  assert idx_test.iri == "promo:node_&_species"
  assert idx_test.indices == ["I_1", "I_3"]
