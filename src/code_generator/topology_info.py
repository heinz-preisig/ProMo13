"""
Contains the TopologyInfo class.

See :class:`TopologyInfo`
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional
import typing

import networkx as nx

from packages.Common.classes import modeller_classes
from packages.Common.classes import entity
from packages.Common.classes import equation


class TopologyInfo:
  """
  A class to store topology information.

  Attributes:
      _all_topology_objects (dict): All the topology objects used to
       build the topology graph.
      topology_graph (nx.Graph): The graph of the TopologyObjects.
      names_info (defaultdict(list)): Stores the names for nodes,
       arcs, species, etc.
      index_sets (defaultdict(list)): Stores what objects belong to
       each index set.
      map_id_to_counter (dict): Maps identifiers corresponding to the
       original indices to values from 1..Ni where Ni is the number of
       objects related to the index.
  """

  def __init__(
      self,
      all_topology_objects: Dict[str, modeller_classes.TopologyObject],
  ):
    self._all_topology_objects = all_topology_objects
    self.graph = nx.Graph()
    self.names_info = defaultdict(list)
    self.index_sets = defaultdict(list)
    self.map_id_to_counter = {}
    self._variables_info = {}
    self._equations_info = defaultdict(set)
    self._build_graph()

  def _build_graph(self) -> None:
    """Builds a graph from the topology objects.

    This method iterates over all topology objects and adds them as
    nodes to the topology graph. An extra node is added to store
    information about the topology through :meth:`_add_topology_node`.

    Edges are added to the graph after all nodes have been added.

    During this process, extracts information from the topology objects
    and stores it in :attr:`names_info`, :attr:`index_sets` and
    :attr:`map_id_to_counter`. See
    :meth:`update_dicts_from_topology_object` for more info.
    """
    species_names = set()

    counters = defaultdict(int)
    edges_info = []
    for top_obj_id, top_obj in self._all_topology_objects.items():
      if not isinstance(top_obj, modeller_classes.EntityContainer):
        continue

      # Used to map N_x, A_x and I_x to integer indices.
      ent_type = top_obj.entity_instance.entity_type

      self._update_dicts_from_topology_object(counters[ent_type], top_obj)
      counters[ent_type] += 1

      # TODO: Extend for other typed tokens
      species_names.update(top_obj.typed_tokens["mass"])

      # We can't add the edges yet because the nodes might not be in the
      # graph yet.
      for node_id in top_obj.outgoing_connections:
        edges_info.append((top_obj_id, node_id))

      self.graph.add_node(top_obj_id, top_obj=top_obj)

    # Fixing the information about species after they have been collected
    self.names_info["species"] = sorted(list(species_names))
    for i, name in enumerate(self.names_info["species"]):
      self.map_id_to_counter[name] = i

    self.graph.add_edges_from(edges_info)
    self._add_topology_node(edges_info)

  def _update_dicts_from_topology_object(
      self,
      counter: int,
      top_obj: modeller_classes.EntityContainer,
  ) -> None:
    """Updates the auxiliary dictionaries.

    The auxiliary dictionaries are :attr:`names_info`,
    :attr:`index_sets` and :attr:`map_id_to_counter`.

    Args:
        counter (int): Current counter for the corresponding top_obj.
        top_obj (modeller_classes.EntityContainer): Stores the
         information used to update the dictionaries.
    """
    self.map_id_to_counter[top_obj.identifier] = counter

    entity_index_set = top_obj.entity_instance.index_set
    self.index_sets[entity_index_set].append(counter)

    entity_type = top_obj.entity_instance.entity_type
    self.names_info[entity_type].append(top_obj.name)

  def _add_topology_node(self, edges_info: List[Tuple[str, str]]) -> None:
    """Adds a topology node to the graph.

    This method first creates a new entity that stores the topology
    information by invoking :meth:`_create_topology_entity`. It then
    instantiates an EntityContainer with this newly created entity.
    After that, it adds a node to the graph using this TopologyObject
    (the EntityContainer instance). Finally, it adds edges to this node
    from all other nodes in the graph.

    Args:
        edges_info (List[Tuple[str, str]]): Each tuple represents a pair
         of nodes that have an edge between them in the graph.
    """
    topology_entity, inst_vars = self._create_topology_entity(edges_info)

    topology_obj = modeller_classes.EntityContainer(
        "T", "Topology", topology_entity, "", "", [], {},
        instantiated_variables=inst_vars,
    )

    self.graph.add_node("T", top_obj=topology_obj)

    for node_id in self.graph:
      if node_id != "T":
        self.graph.add_edge("T", node_id)

  def _create_topology_entity(
      self,
      edges_info: List[Tuple[str, str]]
  ) -> Tuple[entity.Entity, modeller_classes.InstantiationDict]:
    """Creates an entity with the topology information.

    Stores the relevant topology information as instantiation values
    in the corresponding incidence matrices. Then creates an entity
    marking the incidence matrices as output variables.

    Args:
        edges_info (List[Tuple[str, str]]): Each tuple represents a pair
         of nodes that have an edge between them in the graph.

    Returns:
        Tuple[entity.Entity, modeller_classes.InstantiationDict]: The
         created entity and the instantiation information for the
         incidence matrices.
    """
    # TODO: Fix this when a fixed constant list is provided.
    instantiated_variables = {
        "V_10": {},    # F
        "V_64": {},    # D
    }
    # TODO: Extend for interfaces
    for node1, node2 in edges_info:
      top_obj1 = self._all_topology_objects[node1]
      if isinstance(top_obj1, modeller_classes.NodeSimple):
        instantiated_variables["V_10"][(node1, node2)] = -1
        instantiated_variables["V_64"][(node1, node2)] = -1
      elif isinstance(top_obj1, modeller_classes.Arc):
        instantiated_variables["V_10"][(node2, node1)] = 1
        instantiated_variables["V_64"][(node2, node1)] = 1

    topology_entity = entity.Entity(
        "Topology", {}, None, {}, [], list(instantiated_variables), [],
        list(instantiated_variables)
    )
    return (topology_entity, instantiated_variables)

  def get_integrators_info(self) -> Dict[str, Set[str]]:
    """
    Collects information about the integrators in the model.

    Returns:
        Dict[str, Set[str]]: maps the integrator equations to the
         topology objects where they are defined.
    """
    equation_topology_map = defaultdict(set)
    for top_obj_id in self.graph.nodes():
      top_obj = typing.cast(
          modeller_classes.EntityContainer,
          self._all_topology_objects[top_obj_id],
      )
      entity_instance = top_obj.entity_instance
      for variable_id, equation_id in entity_instance.integrators_info():
        equation_topology_map[equation_id].add(top_obj_id)
        self._variables_info[variable_id] = {}
        self._equations_info[equation_id].add(entity_instance.index_set)

    return equation_topology_map

  def find_dependencies(
      self,
      equation_id: str,
      top_obj_id: str,
  ) -> Dict[str, Set[str]]:
    top_obj = typing.cast(
        modeller_classes.EntityContainer,
        self._all_topology_objects[top_obj_id],
    )
    entity_instance = top_obj.entity_instance

    equation_topology_map = defaultdict(set)
    for variable_id in entity_instance.get_variables_from_equation(equation_id):
      dependency_info = self._find_equations_for_variable(variable_id, top_obj)
      for dep_equation_id, dep_top_obj_id, dep_index_set in dependency_info:
        equation_topology_map[dep_equation_id].add(dep_top_obj_id)

        self._equations_info[dep_equation_id].add(dep_index_set)
        self._equations_info[equation_id].add(dep_index_set)

    return equation_topology_map

  def _find_equations_for_variable(
      self,
      variable_id: str,
      top_obj: modeller_classes.EntityContainer,
  ) -> List[Tuple[str, str, str]]:

    entity_instance = top_obj.entity_instance

    if not entity_instance.contains_var(variable_id):
      # TODO: Maybe raise an exception here.
      return []

    if entity_instance.is_init(variable_id):
      instantiation_info = self._transform_instantiation_from_ids_to_numeric(
          top_obj, variable_id
      )
      self._variables_info[variable_id].update(instantiation_info)

      return []

    if entity_instance.is_input(variable_id):
      equations_for_variable = []
      for neighbor_id in self.graph[top_obj.identifier]:
        neighbor_top_obj = typing.cast(
            modeller_classes.EntityContainer,
            self._all_topology_objects[neighbor_id],
        )
        neighbor_ent = neighbor_top_obj.entity_instance
        if neighbor_ent.is_output(variable_id):
          neighbor_equation_info = self._find_equations_for_variable(
              variable_id, neighbor_top_obj
          )
          equations_for_variable.extend(neighbor_equation_info)

      return equations_for_variable

    # TODO: Change when the function return only one equation
    equation_id = entity_instance.get_eq_for_var(variable_id)[0]
    return [(equation_id, top_obj.identifier, entity_instance.index_set)]

  def _transform_instantiation_from_ids_to_numeric(
      self,
      top_obj: modeller_classes.EntityContainer,
      variable_id: str,
  ) -> Dict[Tuple, str]:
    original_instantiation_info = top_obj.instantiated_variables[variable_id]
    new_instantiation_info = {}

    for key, value in original_instantiation_info.items():
      new_key = tuple([
          self.map_id_to_counter[element]
          for element in key
      ])
      new_instantiation_info[new_key] = value

    return new_instantiation_info
