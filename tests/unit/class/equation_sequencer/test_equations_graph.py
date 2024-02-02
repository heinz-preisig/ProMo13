"""
This module contain tests for the EquationsGraph class.

Author: Alberto Rodriguez Fernandez
"""

import pytest
from typing import List, Tuple

from packages.Common.classes.equations_sequencer import EquationsGraph

PARAMS = [
    (0, [], [], "Nothing"),
    (
        12,
        [],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "Only nodes"),
    (
        12,
        [
            (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (4, 7), (4, 8),
            (5, 9), (6, 3), (6, 9), (7, 11), (8, 7), (9, 10), (9, 11), (11, 12),
        ],
        [1, 2, 4, 5, 6, 8, 3, 9, 7, 10, 11, 12],
        "No cycles",
    ),
    (
        12,
        [
            (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (4, 7), (4, 8),
            (5, 9), (6, 3), (6, 9), (7, 11), (8, 7), (9, 10), (9, 11), (11, 12),
            (12, 8),
        ],
        [1, 2, 4, 5, 6, 3, 9, 10, {7, 8, 11, 12}],
        "One simple cycle",
    ),
    (
        12,
        [
            (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (4, 7), (4, 8),
            (5, 9), (6, 3), (6, 9), (7, 11), (8, 7), (9, 2), (9, 10), (9, 11),
            (11, 12),
        ],
        [1, {2, 5, 6, 9}, 4, 3, 10, 8, 7, 11, 12],
        "Two overlaping cycles",
    ),
    (
        12,
        [
            (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (4, 7), (4, 8),
            (5, 9), (6, 3), (6, 9), (7, 11), (8, 7), (9, 2), (9, 10), (9, 11),
            (11, 12), (12, 8),
        ],
        [1, {2, 5, 6, 9}, 4, 3, 10, {7, 8, 11, 12}],
        "Three cycles, two overlapping"
    ),
]


def make_graph(
    number_of_nodes: int,
    arcs: List[Tuple[int, int]],
) -> EquationsGraph:

  test_graph = EquationsGraph()

  for i in range(1, number_of_nodes+1):
    node = str(i)
    test_graph.add_node(node)

  for i_source, i_sink in arcs:
    source = str(i_source)
    sink = str(i_sink)

    test_graph.add_arc(source, sink)

  return test_graph


class TestFindSolvingOrder:
  """Checking the topology sorting"""
  @pytest.mark.parametrize(
      (
          "number_of_nodes",
          "arcs",
          "expected_data",
          "case_name",
      ),
      PARAMS
  )
  def test_find_solving_order(
      self,
      number_of_nodes: int,
      arcs: List[Tuple[int, int]],
      expected_data: List[int],
      case_name: str,
  ):
    """Using different graphs"""
    # SETUP
    graph = make_graph(number_of_nodes, arcs)
    assert_case = f"Test case: Graph contains \"{case_name}\":: "
    assert_msg = assert_case +\
        "\nExpected: \"{expected}\",\nObtained: \"{result}\""

    expected_output = []
    for element in reversed(expected_data):
      group = set()
      if isinstance(element, set):
        for sub_element in element:
          group.add(str(sub_element))
      else:
        group.add(str(element))

      expected_output.append(group)

    # ACTION
    test_data = graph.find_solving_order()
    # COLLECTION
    test_output = test_data
    # ASSERT
    assert expected_output == test_output, \
        assert_msg.format(expected=expected_output, result=test_output)
