from pathlib import Path
import pytest
from unittest.mock import mock_open, patch
from packages.Common.classes import io
from packages.Common.classes import equation_parser


def get_test_files_path() -> Path:
  """Return the test_files directory."""
  return Path(__file__).resolve().parent / 'test_files'


@pytest.fixture
def var_idx_eq(datafiles):
  ontology_name = "TEST"
  with open(datafiles / "var_idx_eq.json", "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  with patch('builtins.open', m_file):
    data = io.load_var_idx_eq_from_file(ontology_name)

  return data


@pytest.fixture
def model_objects(datafiles):
  ontology_name = "TEST"
  model_name = "TEST"

  with open(datafiles / "model.json", "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  with patch('builtins.open', m_file):
    data = io.load_model_from_file(ontology_name, model_name)

  return data


@pytest.fixture
def parser(datafiles, var_idx_eq):
  with open(
      datafiles / "translation_template_matlab.json",
      "r",
      encoding="utf-8"
  ) as file:
    m_file = mock_open(read_data=file.read())

  all_variables, all_indices, _ = var_idx_eq
  with patch('builtins.open', m_file):
    parser_obj = equation_parser.EquationParser(
        "matlab", all_variables, all_indices)

  return parser_obj


@pytest.fixture
def entities(datafiles, var_idx_eq):
  ontology_name = "TEST"
  _, _, all_equations = var_idx_eq

  with open(datafiles / "entities.json", "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  with patch('builtins.open', m_file):
    data = io.load_entities_from_file(ontology_name, all_equations)
  return data
