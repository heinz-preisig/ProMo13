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
