import pytest
from typing import Dict

from tests.unit import test_utils

from packages.Common.classes import modeller_classes

TEST_FILES = test_utils.get_test_files_path()


@pytest.mark.datafiles(
    TEST_FILES / "model.json",
    TEST_FILES / "entities.json",
    TEST_FILES / "var_idx_eq.json",
)
def test_load_model_from_file(
    datafiles,
    topology_objects: Dict[str, modeller_classes.TopologyObject]
):
  test_object = topology_objects.get("N_0")
  assert isinstance(test_object, modeller_classes.NodeComposite)

  test_object = topology_objects.get("N_1")
  assert isinstance(test_object, modeller_classes.NodeSimple)
  assert test_object.entity_instance.get_entity_name(
  ) == "macroscopic.node.mass|constant|infinity.Source"

  test_object = topology_objects.get("A_1")
  assert isinstance(test_object, modeller_classes.Arc)
  assert test_object.entity_instance.get_entity_name(
  ) == "macroscopic.arc.mass|diffusion|lumped.ConnectionDiffusion"
