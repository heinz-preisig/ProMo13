import pytest
from packages.Common.classes.equation_parser import EquationParser

@pytest.fixture
def parser(mocker):
  all_variables = {}
  all_indices = {}
  language = "TEST"

  translator_mock = mocker.patch(
    'packages.Common.classes.translator.Translator'
  )
  translator_mock.return_value.translate_variable.return_value = "a"
  return EquationParser(language, all_variables, all_indices)


def test_parse(parser):
  expected_output = "a"

  test_output = parser.parse("V_1")

  assert test_output == expected_output, f"Parse failed"