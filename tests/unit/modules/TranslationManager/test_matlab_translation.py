import pytest
from tests.unit import test_utils

TEST_FILES = test_utils.get_test_files_path()


@pytest.mark.datafiles(
    TEST_FILES / 'var_idx_eq.json',
    TEST_FILES / 'translation_template_matlab.json')
def test_matlab_translation(datafiles, var_idx_eq, parser):
  ontology_name = "TEST"
  _, _, all_equations = var_idx_eq

  # # Product
  # translation = parser.parse(
  #     all_equations["E_129"].get_translation("global_ID")["rhs"])
  # assert translation == "product(x(N, K) .^ (N_NK_KS(N, K)), \"K_x_S\")"

  # # Partial diff
  # translation = parser.parse(
  #     all_equations["E_6"].get_translation("global_ID")["rhs"])
  # assert translation == "-1 .* pardiff(U(N), V(N))"

  # # Total diff
  # translation = parser.parse(
  #     all_equations["E_89"].get_translation("global_ID")["rhs"])
  # assert translation == "totaldiff(charge(N), t)"

  # # Integral
  # translation = parser.parse(
  #     all_equations["E_87"].get_translation("global_ID")["rhs"])
  # assert translation == "integral(dHdt(N), t, to, te)"

  # # Instantiate
  # translation = parser.parse(
  #     all_equations["E_79"].get_translation("global_ID")["rhs"])
  # assert translation == "instantiate(fHc_A(A), value)"

  # # Root
  # translation = parser.parse(
  #     all_equations["E_97"].get_translation("global_ID")["rhs"])
  # assert translation == "root(Ue(N))"

  # E_152
  translation = parser.parse(
      " V_71 O_3 F_11 D_0 V_184 D_1 O_4 V_91  O_5 I_5 O_5 V_66"
  )
  assert translation == "who knows"
