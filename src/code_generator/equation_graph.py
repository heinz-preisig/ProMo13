from typing import List, Dict, Set

import networkx as nx


class EquationsGraph:
  """
  Represents a direct graph of equations.

  Attributes:
      _graph (DiGraph): A NetworkX DiGraph object to store the graph.
  """

  def __init__(self):
    self._graph = nx.DiGraph()

  def add_node(
      self,
      node: str,
  ) -> None:
    """Adds a node to the graph.

    Args:
        node (str): The node to be added, it corresponds to the
         identifier of an equation.
    """
    self._graph.add_node(node)

  def add_arc(
      self,
      source_node: str,
      sink_node: str,
  ) -> None:
    """Adds an arc to the graph.

    The arc is constructed from a source and a sink node. The equation
    referenced in the sink node defines one variable in the incidence
    list of the equation referenced in the source node.

    Args:
        source_node (str): Source node of the arc.
        sink_node (str): Sink node of the arc.
    """
    self._graph.add_edge(source_node, sink_node)

  def find_solving_order(self) -> List[Set[str]]:
    """Finds a solving order for the equations in the graph.

    The graph is constructed in a way that resembles a dependency
    resolution problem. An equation can only be computed if all
    necessary incident variables are already known. In the case of
    Strongly Connected Components (SCC), all equations in the SCC need
    to be computed together.

    The correct solving order is the reverse of the topological order
    calculated after the graph have been condensed to deal with the
    cycles.

    Returns:
        List[Set[str]]: One of the possible solving orders for the
         equations in the graph. Equations in the same set need to be
         computed together.
    """
    condensed_graph = nx.condensation(self._graph)
    topological_order = list(nx.topological_sort(condensed_graph))

    correct_order = [
        condensed_graph.nodes[node]["members"]
        for node in reversed(topological_order)
    ]

    return correct_order
