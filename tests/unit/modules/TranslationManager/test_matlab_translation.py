from pprint import pprint as pp
import pytest
from unittest.mock import mock_open, patch
from pathlib import Path
from datetime import datetime

from packages.Common.classes.io import load_var_idx_eq_from_file
from packages.Common.classes import equation_parser

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test_files'


@pytest.mark.datafiles(
    FIXTURE_DIR / 'variables.json',
    FIXTURE_DIR / 'translation_template_matlab.json')
def test_load_var_idx_eq_from_file(datafiles):
  ontology_name = "TEST"

  with open(datafiles / "variables.json", "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  with patch('builtins.open', m_file):
    all_variables, all_indices, all_equations = load_var_idx_eq_from_file(
        ontology_name)

  with open(datafiles / "translation_template_matlab.json", "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  with patch('builtins.open', m_file):
    parser = equation_parser.EquationParser(
        "matlab", all_variables, all_indices)

  # Product test
  translation = parser.parse(
      all_equations["E_129"].get_translation("global_ID")["rhs"])
  assert translation == "product(x(N, K) .^ (N_NK_KS(N, K)), \"K_x_S\")"
