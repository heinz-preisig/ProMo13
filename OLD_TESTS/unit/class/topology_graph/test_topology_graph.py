import pytest
from typing import Dict, Set

from code_generator.topology_graph import TopologyInfo


@pytest.fixture(scope="module")
def topology_info(topology_objects) -> TopologyInfo:
  return TopologyInfo(topology_objects)


class TestInitialization:
  """TopologyInfo initialization"""

  def test_names_info(self, topology_info: TopologyInfo):
    """names_info"""
    # SETUP
    expected_output = {
        "node": ["default"]*7,
        "arc": ["default"]*6,
        "species": ["A"],
    }
    # ASSERT
    test_output = topology_info.names_info
    assert test_output == expected_output

  def test_index_sets(self, topology_info: TopologyInfo):
    """index_sets"""
    # SETUP
    expected_output = {
        "N_cons": [0, 4],
        "N_dyna": [1, 2, 3, 5, 6],
        "A_diff": [0, 1, 2, 3, 4, 5],
    }
    # ASSERT
    test_output = topology_info.index_sets
    assert test_output == expected_output

  def test_map_id_to_counter(self, topology_info: TopologyInfo):
    """map_id_to_counter"""
    # SETUP
    expected_output = {
        "N_1": 0,
        "N_2": 1,
        "N_7": 2,
        "N_6": 3,
        "N_8": 4,
        "N_10": 5,
        "N_12": 6,
        "A_3": 0,
        "A_4": 1,
        "A_5": 2,
        "A_9": 3,
        "A_11": 4,
        "A_13": 5,
        "A": 0,
    }
    # ASSERT
    test_output = topology_info.map_id_to_counter
    assert test_output == expected_output

  def test_graph_nodes(self, topology_info: TopologyInfo):
    """graph nodes"""
    # SETUP
    expected_output = set([
        "N_1", "N_2", "N_7", "N_6", "N_8", "N_10", "N_12",
        "A_3", "A_4", "A_5", "A_9", "A_11", "A_13",
        "T",
    ])
    # ASSERT
    test_output = set(topology_info.graph.nodes())
    assert test_output == expected_output

  def test_graph_edges(self, topology_info: TopologyInfo):
    """graph edges"""
    # SETUP
    expected_output = set(
        frozenset(edge)
        for edge in [
            ("N_1", "A_3"), ("N_1", "A_4"),
            ("N_2", "A_9"),
            ("N_7", "A_5"), ("N_7", "A_11"),
            ("A_3", "N_2"),
            ("A_4", "N_7"),
            ("A_5", "N_6"),
            ("A_9", "N_8"),
            ("N_10", "A_13"),
            ("A_11", "N_10"),
            ("A_13", "N_12"),
            ("T", "N_1"), ("T", "N_2"), ("T", "N_7"), ("T", "N_6"),
            ("T", "N_8"), ("T", "N_10"), ("T", "N_12"), ("T", "A_3"),
            ("T", "A_4"), ("T", "A_5"), ("T", "A_9"), ("T", "A_11"),
            ("T", "A_13"),
        ])
    # ASSERT
    test_output = set(frozenset(edge) for edge in topology_info.graph.edges())
    assert test_output == expected_output

  def test_topology_node(self, topology_info: TopologyInfo):
    """topology node"""
    # SETUP
    incidence_list = {
        ("N_1", "A_3"): -1,
        ("N_1", "A_4"): -1,
        ("N_2", "A_9"): -1,
        ("N_7", "A_5"): -1,
        ("N_7", "A_11"): -1,
        ("N_2", "A_3"): 1,
        ("N_7", "A_4"): 1,
        ("N_6", "A_5"): 1,
        ("N_8", "A_9"): 1,
        ("N_10", "A_13"): -1,
        ("N_10", "A_11"): 1,
        ("N_12", "A_13"): 1,
    }

    expected_output = {
        "V_10": incidence_list,
        "V_64": incidence_list,
    }
    # ASSERT
    top_obj = topology_info.graph.nodes["T"]["top_obj"]
    test_output = top_obj.instantiated_variables
    assert test_output == expected_output


class TestFindDependencies:
  """Find Dependencies Method"""
  PARAMETERS = [
      ("V_85", "N_1", {}, "Init variable in self object"),
  ]

  @pytest.mark.parametrize(
      (
          "variable_id",
          "top_obj_id",
          "expected_data",
          "case_name"
      ),
      PARAMETERS,
  )
  def test_find_dependencies_return_value(
      self,
      topology_info: TopologyInfo,
      equation_id: str,
      top_obj_id: str,
      expected_data: Dict[str, Set[str]],
      case_name: str,
  ):
    """Return value"""
    # SETUP
    assert_case = f"Test case: \"{case_name}\":: "
    assert_msg = assert_case +\
        "\nExpected: \"{expected}\",\nObtained: \"{result}\""

    expected_output = expected_data
    # ACTION
    test_output = topology_info.find_dependencies(equation_id, top_obj_id)
    # ASSERT
    assert expected_output == test_output, \
        assert_msg.format(expected=expected_output, result=test_output)
