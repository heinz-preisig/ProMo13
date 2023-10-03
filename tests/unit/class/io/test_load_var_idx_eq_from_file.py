from pprint import pprint as pp
import pytest
from unittest.mock import mock_open, patch
from pathlib import Path
from datetime import datetime

from packages.Common.classes.io import load_var_idx_eq_from_file

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test_files'


@pytest.mark.datafiles(FIXTURE_DIR / 'variables.json')
def test_load_var_idx_eq_from_file(datafiles):
  ontology_name = "TEST"

  with open(datafiles / "variables.json", "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  with patch('builtins.open', m_file):
    all_variables, all_indices, all_equations = load_var_idx_eq_from_file(
        ontology_name)

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
      "latex": "\\\\#",
      "internal_code": "value"
  }
  date_format = "%Y-%m-%d %H:%M:%S"
  assert var_test.created == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert var_test.modified == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
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
      "global_ID": " V_97",
      "python": "d",
      "cpp": "d",
      "matlab": "d",
      "latex": "d",
      "internal_code": "d"
  }
  assert var_test.created == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert var_test.modified == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert var_test.doc == "flow direction of convectional flow"
  assert var_test.equations == ["E_72"]
  assert var_test.index_structures == ["I_2"]
  assert var_test.label == "d"
  assert var_test.network == "macroscopic"
  assert var_test.port_variable == False
  assert var_test.tokens == ["mass"]
  assert var_test.type == "transport"
  assert var_test.units == [0, 0, 0, 0, 0, 0, 0, 0]

  # Test variable V_98
  var_test = all_variables.get("V_98")
  assert var_test.var_id == "V_98"
  assert var_test.IRI == "promo:c_AS"
  assert var_test.aliases == {
      "global_ID": " V_98",
      "python": "c_AS",
      "cpp": "c_AS",
      "matlab": "c_AS",
      "latex": "c",
      "internal_code": "c_AS"
  }
  assert var_test.created == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert var_test.modified == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert var_test.doc == "concentration in convectional flow"
  assert var_test.equations == ["E_73", "E_74"]
  assert var_test.index_structures == ["I_6"]
  assert var_test.label == "c_AS"
  assert var_test.network == "macroscopic"
  assert var_test.port_variable == False
  assert var_test.tokens == []
  assert var_test.type == "secondaryState"
  assert var_test.units == [0, -3, 1, 0, 0, 0, 0, 0]

  # Test variable V_99
  var_test = all_variables.get("V_99")
  assert var_test.var_id == "V_99"
  assert var_test.IRI == "qudt:MolarFlowRate"
  assert var_test.aliases == {
      "global_ID": " V_99",
      "python": "fnc_AS",
      "cpp": "fnc_AS",
      "matlab": "fnc_AS",
      "latex": "{\\\\hat{n}^c}",
      "internal_code": "fnc_AS"
  }
  assert var_test.created == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert var_test.modified == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert var_test.doc == "molar convectional mass flow in the given stream"
  assert var_test.equations == ["E_74"]
  assert var_test.index_structures == ["I_6"]
  assert var_test.label == "fnc_AS"
  assert var_test.network == "macroscopic"
  assert var_test.port_variable == False
  assert var_test.tokens == []
  assert var_test.type == "secondaryState"
  assert var_test.units == [-1, 0, 1, 0, 0, 0, 0, 0]

  ######################################################################
  ########################### Equations tests ##########################
  ######################################################################
  eq_test = all_equations.get("E_72")
  assert eq_test.eq_id == "E_72"
  assert eq_test.rhs == {
      "global_ID": " F_16 D_0 V_8  O_5  I_1 O_5  V_17 D_1",
      "matlab": "sign(reduceproduct(F_N_A(N, A), \"N\", p(N)))", "latex": "\\\\text{sign} \\\\left( {F}{_{N, A}} \\\\stackrel{N}{\\\\,\\\\star\\\\,} {p}{_{N}} \\\\right)"
  }
  assert eq_test.type == "generic"
  assert eq_test.doc == "flow direction of convectional flow"
  assert eq_test.network == "macroscopic"
  assert eq_test.lhs == {
      "global_ID": "V_97",
      "matlab": "d(A)",
      "latex": "{d}{_{A}}"
  }
  assert eq_test.created == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert eq_test.modified == datetime.strptime(
      "2023-09-14 10:16:31", date_format)

  eq_test = all_equations.get("E_73")
  assert eq_test.eq_id == "E_73"
  assert eq_test.rhs == {
      "global_ID": " D_0 V_4 O_4 D_0 V_70 O_1 V_97 O_3 F_10 D_0 V_70 D_1 D_1 D_1  O_5  I_5 O_5  V_66",
      "matlab": "reduceproduct((onehalf .* (F_NS_AS(N, A) - khatrirao(d(A), abs(F_NS_AS(N, A))))), \"N_x_S\", c(N))",
      "latex": "\\\\left({0.5}{_{}} \\\\, . \\\\, \\\\left({F}{_{{N S}, {A S}}}  - {d}{_{A}} \\\\, {\\\\odot} \\\\, |{F}{_{{N S}, {A S}}}|\\\\right)\\\\right) \\\\stackrel{{N S}}{\\\\,\\\\star\\\\,} {c}{_{{N S}}}"
  }
  assert eq_test.type == "generic"
  assert eq_test.doc == "concentration in convectional flow"
  assert eq_test.network == "macroscopic"
  assert eq_test.lhs == {
      "global_ID": "V_98",
      "matlab": "c_AS(A)",
      "latex": "{c}{_{{A S}}}"
  }
  assert eq_test.created == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert eq_test.modified == datetime.strptime(
      "2023-09-14 10:16:31", date_format)

  eq_test = all_equations.get("E_74")
  assert eq_test.eq_id == "E_74"
  assert eq_test.rhs == {
      "global_ID": " V_92 O_3 V_98",
      "matlab": "khatrirao(fV(A), c_AS(A))",
      "latex": "{\\\\hat{V}}{_{A}} \\\\, {\\\\odot} \\\\, {c}{_{{A S}}}"
  }
  assert eq_test.type == "generic"
  assert eq_test.doc == "molar convectional mass flow in the given stream"
  assert eq_test.network == "macroscopic"
  assert eq_test.lhs == {
      "global_ID": "V_99",
      "matlab": "fnc_AS(A)",
      "latex": "{{\\\\hat{n}^c}}{_{{A S}}}"
  }
  assert eq_test.created == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
  assert eq_test.modified == datetime.strptime(
      "2023-09-14 10:16:31", date_format)
