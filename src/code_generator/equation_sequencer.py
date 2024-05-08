"""Find sequence of equations

Functions:
    :func:`sequence_equations`: Finds a sequence of equations.
"""
import collections
from typing import Dict, List, Set, Tuple

import networkx as nx

from src.common import corelib
from src.common import topology

from pprint import pprint as pp

_EquationSequence = List[Set[str]]
_MapEquationTopology = Dict[str, Set[topology.EntityContainer]]
_VariableList = Set[str]


def sequence_equations(
    all_topology_objects: Dict[str, topology.TopologyObject],
) -> Tuple[_EquationSequence, _MapEquationTopology, _VariableList]:
  """Find a sequence of equations

  The sequence is one of the possible ordering that allow a computation
  of all variables in the model. 

  Args:
      all_topology_objects (Dict[str, topology.TopologyObject]): All
       the topology objects in the model

  Returns:
      Tuple[_EquationSequence, _MapEquationTopology, _VariableList]:
       the equation sequence and the byproducts of its generation:

       * All the equations used and what Topology objects contain them.
       * All the variables used in the model.
  """
  topology_graph = topology.build_topology_graph(
      all_topology_objects)

  equation_graph, equation_topology_map, variable_list = _build_equation_graph(
      topology_graph)
  equation_sequence = _find_solving_order(equation_graph)

  return (equation_sequence, equation_topology_map, variable_list)


def _build_equation_graph(
    topology_graph: nx.Graph,
) -> Tuple[nx.DiGraph, _MapEquationTopology, _VariableList]:
  """Build an equation digraph

  Each Node represents one equation in the model. Edges represent a
  dependency relationship, the source equation requires the value
  that the sink equation computes to perform its own computation.

  Args:
      topology_graph (nx.Graph): Graph of Topology objects representing
       the model.

  Returns:
      Tuple[nx.DiGraph, _MapEquationTopology, _VariableList]: The
       equation digraph and the byproducts of its generation:

       * All the equations used and what Topology objects contain them.
       * All the variables used in the model.
  """

  equations_graph = nx.DiGraph()
  processing_queue = collections.deque()
  variable_list = set()

  equation_topology_map = _get_integrators_info(topology_graph)
  for equation_id, topology_objects in equation_topology_map.items():
    equations_graph.add_node(equation_id)
    processing_queue.append((equation_id, topology_objects))

  while processing_queue:
    source_equation_id, topology_objects = processing_queue.popleft()

    for topology_obj in topology_objects:
      equations_info = _find_dependencies(
          source_equation_id,
          topology_obj,
          topology_graph
      )
      for equation_id, topology_objects in equations_info.items():
        if equation_id not in equations_graph:
          # TODO: Add variables to a set here coming from the
          # new eq in the graph.
          equations_graph.add_node(equation_id)

        equations_graph.add_edge(source_equation_id, equation_id)

        new_topology_objects = topology_objects - \
            equation_topology_map[equation_id]
        if new_topology_objects:
          processing_queue.append((equation_id, new_topology_objects))
          equation_topology_map[equation_id].update(new_topology_objects)

  return (equations_graph, equation_topology_map, variable_list)


def _get_integrators_info(topology_graph) -> _MapEquationTopology:
  """Return integrator equations and their location

  Args:
      topology_graph (nx.Graph): Graph of Topology objects representing
        the model.

  Returns:
      Dict[str, Set[str]]: maps the integrator equations to the
       topology objects where they are defined.
  """
  equation_topology_map = collections.defaultdict(set)
  for topology_obj in topology_graph:
    entity_instance = topology_obj.entity_instance
    for var_id in entity_instance.output_vars:
      equation_id = entity_instance.get_eq_for_var(var_id)
      if equation_id and equation_id is not None:
        equation_topology_map[equation_id[0]].add(topology_obj)

  return equation_topology_map


def _find_dependencies(
    equation_id: str,
    topology_obj: topology.EntityContainer,
    topology_graph: nx.Graph,
) -> _MapEquationTopology:
  """Find equation dependencies

  One equation is dependent on another if it provides a way to calculate
  one of its variables. 

  a = b + c (I)
  b = d - e (II)

  Equation `I` depends on equation `II` to get the value for `b`.

  Args:
      equation_id (str): Equation to find dependencies for.
      topology_obj (topology.EntityContainer): Contains the Entity where
       the equation is.
      topology_graph (nx.Graph): Graph of Topology objects representing
       the model.

  Returns:
      _MapEquationTopology: Dependencies and their locations.
  """
  entity_instance = topology_obj.entity_instance

  equation_topology_map = collections.defaultdict(set)

  for variable_id in entity_instance.get_variables_from_equation(equation_id):
    dependency_info = _find_equations_for_variable(
        variable_id, topology_obj, topology_graph)

    for dep_equation_id, dep_topology_objects in dependency_info.items():
      equation_topology_map[dep_equation_id].update(dep_topology_objects)

  return equation_topology_map


def _find_equations_for_variable(
    variable_id: str,
    topology_obj: topology.EntityContainer,
    topology_graph: nx.Graph,
) -> _MapEquationTopology:
  """Find equations to calculate a variable.

  The Topology object where the Entity containing the equation live is
  also returned.

  Several cases can arise:

  * The variable is instantiated: No equation is returned.
  * The variable is input: The neighbor topology objects are queried and
     all the appropiate equations and their locations are returned.
  * The variable have an equation: The equation and the location of the
     current Topology object is returned.

  Args:
      variable_id (str): The identifier of the variable.
      topology_obj (topology.EntityContainer): Main Topology object to
       look for the equation.
      topology_graph (nx.Graph): Graph of Topology objects to check for
       neighbors if necessary.
  Returns:
      _MapEquationTopology: Equations to calculate the variable and
       their locations.
  """

  entity_instance = topology_obj.entity_instance

  if not entity_instance.contains_var(variable_id):
      # TODO: Maybe raise an exception here.
    return {}

  if entity_instance.is_init(variable_id):
    return {}

  if entity_instance.is_input(variable_id):
    equation_topology_map = collections.defaultdict(set)
    for neighbor in topology_graph[topology_obj]:
      neighbor_entity: corelib.Entity = neighbor.entity_instance
      # Rules prevent further nesting, if a variable is input
      # the neighbors either dont have the variable, have an equation
      # for it or instantiate it.
      equations = neighbor_entity.get_eq_for_var(variable_id)

      if equations:
        equation_id = equations[0]
        equation_topology_map[equation_id].add(neighbor)

    return equation_topology_map

  equations = entity_instance.get_eq_for_var(variable_id)
  if equations:
    equation_id = equations[0]
    return {equation_id: {topology_obj}}

  return {}


def _find_solving_order(equations_graph: nx.DiGraph) -> List[Set[str]]:
  """Finds a solving order for the equations in the graph.

  The graph is constructed in a way that resembles a dependency
  resolution problem. An equation can only be computed if all
  necessary incident variables are already known. In the case of
  Strongly Connected Components (SCC), all equations in the SCC need
  to be computed together.

  The correct solving order is the reverse of the topological order
  calculated after the graph have been condensed to deal with the
  cycles.

  Args:
      equations_graph (nx.DiGraph): Graph to be processed.

  Returns:
      List[Set[str]]: One of the possible solving orders for the
       equations in the graph. Equations in the same set need to be
       computed together.
  """
  condensed_graph = nx.condensation(equations_graph)
  topological_order = list(nx.topological_sort(condensed_graph))

  correct_order = [
      condensed_graph.nodes[node]["members"]
      for node in reversed(topological_order)
  ]

  return correct_order
