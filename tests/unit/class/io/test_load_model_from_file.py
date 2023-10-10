import pytest
import conftest


TEST_FILES = conftest.get_test_files_path()


@pytest.mark.datafiles(TEST_FILES / "model.json")
def test_load_model_from_file(datafiles, model_objects):
  test_node = model_objects["N_0"]
  assert test_node.name == "TopLevel"
  assert test_node.parent == None
  assert test_node.children == ["N_1", "N_2", "N_3", "N_4"]

  test_node = model_objects["N_7"]
  assert test_node.parent == "N_2"
  assert test_node.children == []
  assert test_node.name == "Pore1.1"
  assert test_node.variant == "Pore"
  assert test_node.network == "liquid"
  assert test_node.named_network == "A-liquid"
  assert test_node.modeller_class == "node_simple"
  assert test_node.type == "dynamic|lumped"

  test_arc = model_objects["A_2"]
  assert test_arc.name == "1 | 4"
  assert test_arc.source == "N_1"
  assert test_arc.sink == "N_15"
  assert test_arc.token == "mass"
  assert test_arc.network == "liquid"
  assert test_arc.named_network == "A-liquid"
  assert test_arc.mechanism == "diffusion"
  assert test_arc.nature == "lumped"
  assert test_arc.variant == "New_Connection"
