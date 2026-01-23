from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import disjoint_set
import networkx as nx


def print_graph(
        graph: nx.Graph,
        file_name: Optional[str] = "graph.png",
        ) -> None:
    out_graph = nx.drawing.nx_pydot.to_pydot(graph)
    out_graph.write_png(file_name)


class EquationGraph:
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

    def _find_nodes_in_overlapping_cycle_groups(
            self,
            ) -> List[Set[Tuple[str, str]]]:
        """
        Partition the nodes of a graph's cycles into disjoint sets.

        This function finds all simple cycles in the graph and partitions
        the nodes of these cycles into disjoint sets. Each set represents a
        group of overlapping cycles.

        Returns:
            List[Set[Tuple[str, str]]]: Each set contains all the nodes in a
             group of overlapping cycles.
        """
        overlapping_cycles_nodes = disjoint_set.DisjointSet()
        for simple_cycle in nx.simple_cycles(self._graph):
            for node in simple_cycle:
                overlapping_cycles_nodes.find(node)

        for u, v in self._graph.edges:
            if u in overlapping_cycles_nodes and v in overlapping_cycles_nodes:
                overlapping_cycles_nodes.union(u, v)
                from pprint import pprint as pp
                pp(list(overlapping_cycles_nodes.itersets(with_canonical_elements=True)))
                print("================================================")

        return list(overlapping_cycles_nodes.itersets())  # type: ignore

        # def process_dangling_nodes(self) -> None:
    #   while d_nodes := self.current_dangling_nodes():
    #     for node in d_nodes:
    #       if node in self.integrators:
    #         continue

    #       top_ids = self.digraph.nodes[node]["topology_ids"]
    #       index_sets = self.digraph.nodes[node]["index_sets"]
    #       self.expressions.append([node + (top_ids,) + (index_sets,)])

    #     self.digraph.remove_nodes_from(d_nodes)

    # def current_dangling_nodes(self) -> List[Tuple[str, str]]:
    #   dangling_nodes = []
    #   for node in self.digraph.nodes:
    #     if self.digraph.out_degree(node) == 0:
    #       dangling_nodes.append(node)

    #   return dangling_nodes

    # def current_dangling_cycles(
    #     self,
    #     all_cycles: List[Set[Tuple[str, str]]],
    # ) -> List[Set[Tuple[str, str]]]:
    #   dangling_cycles = []
    #   for cycle in all_cycles:
    #     cycle_edges = set(self.digraph.subgraph(cycle).edges)
    #     out_edges = set(self.digraph.out_edges(cycle))

    #     if out_edges.issubset(cycle_edges):
    #       dangling_cycles.append(cycle)

    #   return dangling_cycles

    # def process_dangling_cycles(
    #     self,
    #     all_cycles: List[Set[Tuple[str, str]]],
    # ) -> None:

    #   while d_cycles := self.current_dangling_cycles(all_cycles):
    #     for cycle in d_cycles:
    #       cycle_info = []
    #       for node in cycle:
    #         top_ids = self.digraph.nodes[node]["topology_ids"]
    #         index_sets = self.digraph.nodes[node]["index_sets"]
    #         cycle_info.append(node + (top_ids,) + (index_sets,))

    #       self.expressions.append(cycle_info)
    #       all_cycles.remove(cycle)
    #       self.digraph.remove_nodes_from(cycle)
