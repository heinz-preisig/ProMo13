import collections
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict

import networkx as nx

from packages.Common.classes import entity
from packages.Common.classes import equation
from packages.Common.classes import variable
from packages.Common.classes import index
from packages.Common.classes import modeller_classes
from code_generator import topology_graph

from pprint import pprint as pp


def print_graph(
    graph: nx.Graph,
    file_name: Optional[str] = "graph.png",
) -> None:
  out_graph = nx.drawing.nx_pydot.to_pydot(graph)
  out_graph.write_png(file_name)


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


class EquationSequencer:
  def __init__(
      self,
      all_equations: Dict[str, equation.Equation],
      all_indices: Dict[str, index.Index],
      all_variables: Dict[str, variable.Variable],
      all_topology_objects: Dict[str, modeller_classes.TopologyObject],
  ):
    self._all_equations = all_equations
    self._all_indices = all_indices
    self._all_variables = all_variables
    self._all_topology_objects = all_topology_objects

    self._topology_info = topology_graph.TopologyInfo(all_topology_objects)
    self._equations_graph = EquationsGraph()

    self.inst_variables = {}
    self.expressions = []
    self.integrators = []

    self._build_equations_graph()

  def _build_equations_graph(self):
    equation_topology_map: Dict[str, Set[str]] = {}

    processing_queue = collections.deque()

    # TODO: Transform into the integrators output format
    integrators_info = self._topology_info.get_integrators_info()
    equation_topology_map.update(integrators_info)
    for equation_id, topology_ids in integrators_info.items():
      self._equations_graph.add_node(equation_id)
      processing_queue.append((equation_id, topology_ids))

    while processing_queue:
      source_equation_id, topology_ids = processing_queue.popleft()

      for top_obj_id in topology_ids:
        equations_info = self._topology_info.find_dependencies(
            source_equation_id,
            top_obj_id,
        )
        for equation_id, topology_ids in equations_info.items():
          self._equations_graph.add_node(equation_id)
          self._equations_graph.add_arc(source_equation_id, equation_id)
          new_topology_ids = topology_ids.difference(
              equation_topology_map[equation_id]
          )
          if new_topology_ids:
            processing_queue.append((equation_id, new_topology_ids))
            equation_topology_map[equation_id].update(new_topology_ids)

  #   # Adding the integrators first.
  #   for top_node in self.top_graph:
  #     if "N" not in top_node or self.top_graph.nodes[top_node]["is_reservoir"]:
  #       continue

  #     associated_entity = self.top_graph.nodes[top_node]["entity"]
  #     for var_id, eq_id in associated_entity.integrators_info():
  #       vertex_id = (var_id, eq_id)
  #       if vertex_id in self.digraph:
  #         self.digraph.nodes[vertex_id]["topology_ids"].add(top_node)
  #         self.digraph.nodes[vertex_id]["index_sets"].add(
  #             associated_entity.index_set
  #         )
  #       else:
  #         self.digraph.add_node(
  #             vertex_id,
  #             topology_ids={top_node},
  #             index_sets={associated_entity.index_set},
  #         )

  #   for node in self.digraph:
  #     top_ids = self.digraph.nodes[node]["topology_ids"]
  #     index_sets = self.digraph.nodes[node]["index_sets"]
  #     self.integrators.append(node + (top_ids,) + (index_sets,))

  #   # pp(self.integrators)

  #   # Using BFS to build the rest of the digraph
  #   # Instantiations are handled in this step and stored so they do not
  #   # appear in the final digraph.

  #   queue = collections.deque()

  #   for vertex_id in self.digraph.nodes():
  #     queue.append((vertex_id, self.digraph.nodes[vertex_id]["topology_ids"]))

  #   # cont = 1
  #   while queue:
  #     # self.print_graph(file_name = f"step{cont}.png")
  #     # cont+=1

  #     parent_vertex_id, topology_ids = queue.popleft()
  #     children_vertexes = self.find_dependencies(
  #         parent_vertex_id,
  #         topology_ids,
  #     )

  #     for vertex_id, vertex_info in children_vertexes.items():
  #       if vertex_id in self.digraph:
  #         # In the case the combination of var-eq is already in the
  #         # graph we check if the combination is used in a topology
  #         # node that is not already in the digraph. If that is the
  #         # case we update the node and queue the new additions for
  #         # processing
  #         new_top_ids = vertex_info["topology_ids"].difference(
  #             self.digraph.nodes[vertex_id]["topology_ids"]
  #         )
  #         if new_top_ids:
  #           self.digraph.nodes[vertex_id]["topology_ids"].update(
  #               vertex_info["topology_ids"]
  #           )
  #           self.digraph.nodes[vertex_id]["index_sets"].update(
  #               vertex_info["index_sets"]
  #           )
  #           queue.append((vertex_id, new_top_ids))
  #       else:
  #         self.digraph.add_node(
  #             vertex_id,
  #             topology_ids=vertex_info["topology_ids"],
  #             index_sets=vertex_info["index_sets"],
  #         )
  #         queue.append((vertex_id, vertex_info["topology_ids"]))
  #       self.digraph.add_edge(parent_vertex_id, vertex_id)

  #   # self.print_graph(file_name = f"step{cont}.png")
  #   # pp(self.inst_variables)

  #   # Variables that are not instantiated are added to the instantiation
  #   # dictionary without instantiation values.
  #   for node in self.digraph:
  #     var_id, _ = node
  #     if var_id not in self.inst_variables:
  #       self.update_inst_vars(var_id, None)

  #   # for node in self.digraph:
  #   #   print(node[1] + ": " + str(self.digraph.nodes[node]["index_sets"]))
  #   # pp(self.inst_variables)

  # def find_dependencies(
  #     self,
  #     parent_vertex_id: Tuple[str, str],
  #     topology_ids: Set[str],
  # ) -> Dict[Tuple[str, str], Set[str]]:

  #   par_var_id, par_eq_id = parent_vertex_id
  #   par_eq = self.all_equations[par_eq_id]
  #   linked_vars = par_eq.get_incidence_list(par_var_id)

  #   dependencies = {}
  #   for var_id in linked_vars:
  #     # TODO: Find out what to do with time in the integrators
  #     if var_id == "V_4":
  #       continue
  #     for top_id in topology_ids:
  #       var_info = self.get_equations(parent_vertex_id, var_id, top_id)
  #       # pp(var_info)

  #       if var_info is None:
  #         continue

  #       for eq_id, new_top_id, new_index_set in var_info:
  #         vertex_id = (var_id, eq_id)
  #         if vertex_id in dependencies:
  #           dependencies[vertex_id]["topology_ids"].add(new_top_id)
  #           dependencies[vertex_id]["index_sets"].add(new_index_set)
  #         else:
  #           dependencies[vertex_id] = {
  #               "topology_ids": {new_top_id},
  #               "index_sets": {new_index_set},
  #           }

  #   return dependencies

  # def get_equations(
  #     self,
  #     parent_vertex_id: Optional[Tuple[str, str]],
  #     var_id: str,
  #     top_id: str,
  # ) -> Optional[List[Tuple[str, str]]]:

  #   # print("VAR: " + var_id)
  #   # print("TOP_ID: " + top_id)
  #   current_entity = self.top_graph.nodes[top_id]["entity"]
  #   inst_info = self.top_graph.nodes[top_id]["inst_info"]
  #   # pp(current_entity.entity_name)
  #   # pp(inst_info)

  #   # No equation if the variable is calculated in the main integrators
  #   # (closing the loop).
  #   if var_id in current_entity.integrators:
  #     return None

  #   # No equation if the variable is being instantiated.
  #   # We add here the instantiation info.
  #   if var_id in inst_info:
  #     self.update_inst_vars(var_id, top_id)
  #     return None

  #   # If the variable is calculated somewere else we need to check there
  #   # to find the info.
  #   if current_entity.is_input(var_id):
  #     var_info = []
  #     # Loop through the neighbors. For more info see NetworkX docs.
  #     for top_node_id in self.top_graph[top_id]:
  #       # print(top_node_id)
  #       # print("NID: " + top_node_id)
  #       neighbor_entity = self.top_graph.nodes[top_node_id]["entity"]
  #       # print("NEIGHBOR:" + str(neighbor_entity.index_set))
  #       if neighbor_entity.is_output(var_id):
  #         # A variable cant be input and output at the same time. When
  #         # calling get_equations() on the neighbor parent_vertex_id can
  #         # be None because we call it only for output variables and
  #         # parent_vertex_id is only used if the variable is input.
  #         neighbor_var_info = self.get_equations(None, var_id, top_node_id)
  #         if neighbor_var_info is not None:
  #           var_info.extend(neighbor_var_info)

  #         # The index set of the neighbor is only added if the variable
  #         # that we are looking for is an output there.
  #         if neighbor_entity.index_set is not None:
  #           self.digraph.nodes[parent_vertex_id]["index_sets"].add(
  #               neighbor_entity.index_set
  #           )

  #     return var_info

  #   eq_id = current_entity.get_eq_for_var(var_id)
  #   if eq_id is not None:
  #     # If we can find the info of the variable in the var_eq_forest.
  #     return [(eq_id[0], top_id, current_entity.index_set)]

  #   # If the variable can not be found in the topology object.
  #   return None

  # def update_inst_vars(
  #     self,
  #     var_id: str,
  #     top_id: Optional[str],
  # ) -> None:
  #   # Initializing variables that are not already in the dict.
  #   if var_id not in self.inst_variables:
  #     self.inst_variables[var_id] = {}

  #   # Variables that are not instantiated are also added to the dict
  #   # with vals: {} to help with the initialization. top_id = None is
  #   # the flag used to know we are dealing with these variables.
  #   if top_id is None:
  #     return

  #   # Storing values
  #   node_inst_info = self.top_graph.nodes[top_id]["inst_info"]
  #   self.inst_variables[var_id].update(node_inst_info[var_id])
