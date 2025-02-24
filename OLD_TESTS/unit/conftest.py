import pytest
from unittest.mock import mock_open, patch
from pathlib import Path
from packages.Common.classes import io
from packages.Common.classes import equation_parser

TEST_FILES_DIR = Path(__file__).parent / "test_files"


@pytest.fixture(scope="module")
def var_idx_eq():
  file_path = TEST_FILES_DIR / "var_idx_eq.json"
  with open(file_path, "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  ontology_name = "TEST"
  with patch("builtins.open", m_file):
    data = io.load_var_idx_eq_from_file(ontology_name)

  return data


@pytest.fixture(scope="module")
def entities(var_idx_eq):
  file_path = TEST_FILES_DIR / "entities.json"

  with open(file_path, "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  ontology_name = "TEST"
  _, _, all_equations = var_idx_eq
  with patch("builtins.open", m_file):
    data = io.load_entities_from_file(ontology_name, all_equations)
  return data


@pytest.fixture(scope="module")
def topology_objects(entities):
  ontology_name = "TEST"
  model_name = "TEST"
  file_path = TEST_FILES_DIR / "topology_objects.json"

  with open(file_path, "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  with patch("builtins.open", m_file):
    data = io.load_topology_objects(ontology_name, model_name, entities)

  return data


@pytest.fixture(scope="module")
def parser(var_idx_eq):
  file_path = TEST_FILES_DIR / "translation_template_matlab.json"
  with open(file_path, "r", encoding="utf-8") as file:
    m_file = mock_open(read_data=file.read())

  all_variables, all_indices, _ = var_idx_eq
  with patch("builtins.open", m_file):
    parser_obj = equation_parser.EquationParser(
        "matlab", all_variables, all_indices)

  return parser_obj
