import collections
import networkx as nx
from typing import Dict, List, Tuple, Set, Optional

import disjoint_set

from packages.Common.classes import entity
from packages.Common.classes import equation
from packages.Common.classes import variable

from pprint import pprint as pp

class VarEqDiGraph:
  def __init__(
    self,
    top_graph: nx.Graph,
    all_equations: Dict[str, equation.Equation],
    all_indices: Dict,
    all_variables: Dict[str, variable.Variable],
  ):
    self.top_graph = top_graph
    self.all_equations = all_equations
    self.all_indices = all_indices
    self.all_variables = all_variables

    self.digraph = nx.DiGraph()
    self.inst_variables = {}
    self.expressions = []
    self.integrators = []

    # Adding the integrators first.
    for top_node in self.top_graph:
      if "N" not in top_node or self.top_graph.nodes[top_node]["is_reservoir"]:
        continue

      associated_entity = self.top_graph.nodes[top_node]["entity"]
      for var_id, eq_id in associated_entity.integrators_info():
        vertex_id = (var_id, eq_id)
        if vertex_id in self.digraph:
          self.digraph.nodes[vertex_id]["topology_ids"].add(top_node)
          self.digraph.nodes[vertex_id]["index_sets"].add(
            associated_entity.index_set
          )
        else:
          self.digraph.add_node(
            vertex_id,
            topology_ids = {top_node},
            index_sets = {associated_entity.index_set},
          )

    for node in self.digraph:
      top_ids = self.digraph.nodes[node]["topology_ids"]
      index_sets = self.digraph.nodes[node]["index_sets"]
      self.integrators.append(node + (top_ids,) + (index_sets,))

    # pp(self.integrators)

    # Using BFS to build the rest of the digraph
    # Instantiations are handled in this step and stored so they do not
    # appear in the final digraph.

    queue = collections.deque()

    for vertex_id in self.digraph.nodes():
      queue.append((vertex_id, self.digraph.nodes[vertex_id]["topology_ids"]))

    # cont = 1
    while queue:
      # self.print_graph(file_name = f"step{cont}.png")
      # cont+=1

      parent_vertex_id, topology_ids = queue.popleft()
      children_vertexes = self.find_dependencies(
        parent_vertex_id,
        topology_ids,
      )

      for vertex_id, vertex_info in children_vertexes.items():
        if vertex_id in self.digraph:
          # In the case the combination of var-eq is already in the
          # graph we check if the combination is used in a topology
          # node that is not already in the digraph. If that is the
          # case we update the node and queue the new additions for
          # processing
          new_top_ids = vertex_info["topology_ids"].difference(
            self.digraph.nodes[vertex_id]["topology_ids"]
          )
          if new_top_ids:
            self.digraph.nodes[vertex_id]["topology_ids"].update(
              vertex_info["topology_ids"]
            )
            self.digraph.nodes[vertex_id]["index_sets"].update(
              vertex_info["index_sets"]
            )
            queue.append((vertex_id, new_top_ids))
        else:
          self.digraph.add_node(
            vertex_id,
            topology_ids = vertex_info["topology_ids"],
            index_sets = vertex_info["index_sets"],
          )
          queue.append((vertex_id, vertex_info["topology_ids"]))
        self.digraph.add_edge(parent_vertex_id, vertex_id)

    # self.print_graph(file_name = f"step{cont}.png")
    # pp(self.inst_variables)

    # Variables that are not instantiated are added to the instantiation
    # dictionary without instantiation values.
    for node in self.digraph:
      var_id, _ = node
      if var_id not in self.inst_variables:
        self.update_inst_vars(var_id, None)

    # for node in self.digraph:
    #   print(node[1] + ": " + str(self.digraph.nodes[node]["index_sets"]))
    # pp(self.inst_variables)

  def find_dependencies(
    self,
    parent_vertex_id: Tuple[str, str],
    topology_ids: Set[str],
  ) -> Dict[Tuple[str, str], Set[str]]:

    par_var_id, par_eq_id = parent_vertex_id
    par_eq = self.all_equations[par_eq_id]
    linked_vars = par_eq.get_incidence_list(par_var_id)

    dependencies = {}
    for var_id in linked_vars:
      for top_id in topology_ids:
        var_info = self.get_equations(parent_vertex_id, var_id, top_id)

        if var_info is None:
          continue

        for eq_id, new_top_id, new_index_set in var_info:
          vertex_id = (var_id, eq_id)
          if vertex_id in dependencies:
            dependencies[vertex_id]["topology_ids"].add(new_top_id)
            dependencies[vertex_id]["index_sets"].add(new_index_set)
          else:
            dependencies[vertex_id] = {
              "topology_ids": {new_top_id},
              "index_sets": {new_index_set},
            }

    return dependencies

  def get_equations(
    self,
    parent_vertex_id: Optional[Tuple[str, str]],
    var_id: str,
    top_id: str,
  ) -> Optional[List[Tuple[str, str]]]:

    # print("VAR: " + var_id)
    # print("TOP_ID: " + top_id)
    current_entity = self.top_graph.nodes[top_id]["entity"]
    inst_info = self.top_graph.nodes[top_id]["inst_info"]

    # No equation if the variable is calculated in the main integrators
    # (closing the loop).
    if var_id in current_entity.integrators:
      return None

    # No equation if the variable is being instantiated.
    # We add here the instantiation info.
    if var_id in inst_info:
      self.update_inst_vars(var_id, top_id)
      return None

    # If the variable is calculated somewere else we need to check there
    # to find the info.
    if current_entity.is_input(var_id):
      var_info = []
      # Loop through the neighbors. For more info see NetworkX docs.
      for top_node_id in self.top_graph[top_id]:
        # print("NID: " + top_node_id)
        neighbor_entity = self.top_graph.nodes[top_node_id]["entity"]
        if neighbor_entity.index_set is not None:
          self.digraph.nodes[parent_vertex_id]["index_sets"].add(
            neighbor_entity.index_set
          )
        if neighbor_entity.is_output(var_id):
          # A variable cant be input and output at the same time. When 
          # calling get_equations() on the neighbor parent_vertex_id can
          # be None because we call it only for output variables and
          # parent_vertex_id is only used if the variable is input.
          neighbor_var_info = self.get_equations(None, var_id, top_node_id)
          if neighbor_var_info is not None:
            var_info.extend(neighbor_var_info)

      return var_info

    eq_id = current_entity.get_eq_for_var(var_id)
    if eq_id is not None:
      # If we can find the info of the variable in the var_eq_forest.
      return [(eq_id, top_id, current_entity.index_set)]

    # If the variable can not be found in the topology object.
    return None

  def update_inst_vars(
    self,
    var_id: str,
    top_id: Optional[str],
  ) -> None:

    index_structures = self.all_variables[var_id].index_structures

    # Initializing variables that are not already in the dict.
    if var_id not in self.inst_variables:
      dimension = len(index_structures)
      self.inst_variables[var_id] = {
        "dimension": dimension,
        "vals": {},
      }
    else:
      dimension = self.inst_variables[var_id]["dimension"]

    # Variables that are not instantiated are also added to the dict
    # with vals: {} to help with the initialization. top_id = None is
    # the flag used to know we are dealing with these variables.
    if top_id is None:
      return

    # Storing values
    inst_info = self.top_graph.nodes[top_id]["inst_info"]

    if dimension == 0:
      self.inst_variables[var_id]["vals"] = inst_info[var_id]
    elif dimension == 1:
      # TODO Fix this, maybe a new node in the topology graph: "S"
      index = index_structures[0]
      index_label = self.all_indices[index]["aliases"]["internal_code"]
      if index_label == "S":
        for i, val in enumerate(inst_info[var_id], start=1):
          self.inst_variables[var_id]["vals"][str(i)] = [val]
      else:
        # print(var_id)
        # pp(inst_info[var_id])
        self.inst_variables[var_id]["vals"][top_id[1:]] = inst_info[var_id]
    elif dimension == 2:
      # TODO Find a better way of storing the matrices
      # So far only matrices from topology are instantiated
      # Change as needed to allow for instantiation of other things.
      self.inst_variables[var_id]["vals"]["rows"] = inst_info[var_id]["rows"]
      self.inst_variables[var_id]["vals"]["cols"] = inst_info[var_id]["cols"]
      self.inst_variables[var_id]["vals"]["vals"] = inst_info[var_id]["vals"]

  def find_solving_order(self) -> None:
    all_cycles = self.find_cycles()

    while self.digraph:
      self.process_dangling_nodes()
      self.process_dangling_cycles(all_cycles)

  def find_cycles(self) -> List[Set[Tuple[str, str]]]:
    # Usin DisjoinSet structure to find groups of cycles with no common
    # nodes.
    disj_set = disjoint_set.DisjointSet()
    nodes_in_cycles = set()
    for cycle in nx.simple_cycles(self.digraph):
      for element in cycle:
        disj_set.find(element)
        nodes_in_cycles.add(element)

    for u, v in self.digraph.edges:
      if u in nodes_in_cycles and v in nodes_in_cycles:
        disj_set.union(u, v)

    return list(disj_set.itersets())

  def current_dangling_nodes(self) -> List[Tuple[str, str]]:
    dangling_nodes = []
    for node in self.digraph.nodes:
      if self.digraph.out_degree(node) == 0:
        dangling_nodes.append(node)

    return dangling_nodes

  def process_dangling_nodes(self) -> None:
    while d_nodes := self.current_dangling_nodes():
      for node in d_nodes:
        if node in self.integrators:
          continue

        top_ids = self.digraph.nodes[node]["topology_ids"]
        index_sets = self.digraph.nodes[node]["index_sets"]
        self.expressions.append([node + (top_ids,) + (index_sets,)])

      self.digraph.remove_nodes_from(d_nodes)

  def current_dangling_cycles(
    self,
    all_cycles: List[Set[Tuple[str, str]]],
  ) -> List[Set[Tuple[str, str]]]:
    dangling_cycles = []
    for cycle in all_cycles:
      cycle_edges = set(self.digraph.subgraph(cycle).edges)
      out_edges = set(self.digraph.out_edges(cycle))

      if out_edges.issubset(cycle_edges):
        dangling_cycles.append(cycle)

    return dangling_cycles

  def process_dangling_cycles(
    self,
    all_cycles: List[Set[Tuple[str, str]]],
  ) -> None:

    while d_cycles := self.current_dangling_cycles(all_cycles):
      for cycle in d_cycles:
        cycle_info = []
        for node in cycle:
          top_ids = self.digraph.nodes[node]["topology_ids"]
          index_sets = self.digraph.nodes[node]["index_sets"]
          cycle_info.append(node + (top_ids,) + (index_sets,))

        self.expressions.append(cycle_info)
        all_cycles.remove(cycle)
        self.digraph.remove_nodes_from(cycle)

  def print_graph(
    self,
    graph: Optional[nx.Graph] = None, 
    file_name: Optional[str] = "output.png",
  ) -> None:

    if graph is None:
      graph = self.digraph

    out_graph = nx.drawing.nx_pydot.to_pydot(graph)
    out_graph.write_png(file_name)