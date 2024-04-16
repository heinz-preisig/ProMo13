"""
This module defines the TopologyObject class and its subclasses.

The TopologyObject class is the base class for all topology objects used
in ProMo. These objects represent the fundamental building blocks
of the model's structure.

Classes:
    :class:`TopologyObject`: The base class for all Topology Objects.
    :class:`NodeComposite`: Represents a Composite Node.
    :class:`EntityContainer`: Represents a Topology Object linked to an
     Entity.
    :class:`NodeSimple`: Represents a Simple Node.
    :class:`Arc`: Represents an Arc.

Functions:
    :func:`build_topology_graph`: Create a NetworkX Graph from a list of
     :class:`TopologyObjects`.


"""
import copy
from typing import List, Optional, Dict, Tuple
from typing_extensions import Self
import json

import networkx as nx

from packages.Common.classes import entity
from packages.Common.classes import variable

# Define type aliases
InstantiationDict = Dict[str, Dict[Tuple, Optional[str]]]


class TopologyObject:
  """
  Base class for Topology Objects in the modeller.

  Topology Objects are the primary components of the modeller,
  representing the fundamental building blocks of the model's
  structure.

  Attributes:
      identifier (str): A unique identifier for the Topology Object.
      name (str): The name of the Topology Object.
      parent_id (str, optional): The identifier of the parent Topology
       Object, if any. Defaults to **None**.
  """

  def __init__(
      self,
      identifier: str,
      name: str,
      parent_id: Optional[str] = None,
  ):
    """
    Initializes a new instance of the TopologyObject class.

    Args:
        identifier (str): A unique identifier for the Topology Object.
        name (str): The name of the Topology Object.
        parent_id (str, optional): The identifier of the parent Topology
         Object, if any. Defaults to **None**.
    """
    self.identifier = identifier
    self.name = name
    self.parent_id = parent_id

  # TODO: Make custom class for the return value
  def to_json(self):
    class_dict = {}
    class_dict["identifier"] = self.identifier
    class_dict["name"] = self.name
    class_dict["parent_id"] = self.parent_id
    class_dict["modeller_class"] = self.__class__.__name__

    return class_dict

  @classmethod
  def from_json(
      cls,
      data: Dict,
      all_entities: Dict[str, entity.Entity],
  ) -> Self:
    init_data = copy.deepcopy(data)

    # Only used to decide which class should be used
    del init_data["modeller_class"]

    return cls(**init_data)


class NodeComposite(TopologyObject):
  """
  Represents a Composite Node

  This type of node can contain other Topology Objects but is is not
  linked to an Entity.

  Inheritance:
      Inherits from :class:`TopologyObject`.

  Attributes:
      children_ids (List[str], optional): The ids of all the Topology
       Objects contained in the Composite Node.
  """

  def __init__(
      self,
      identifier: str,
      name: str,
      parent_id: Optional[str] = None,
      children_ids: Optional[List[str]] = None,
  ):
    super().__init__(identifier, name, parent_id)

    self.children_ids = children_ids or []

  def to_json(self):
    class_dict = super().to_json()
    class_dict["children_ids"] = self.children_ids

    return class_dict


class EntityContainer(TopologyObject):
  # """
  # Represents a Topology Object linked to an Entity.

  # Inheritance:
  #     Inherits from :class:`TopologyObject`.

  # Attributes:
  #     entity_instance (:class:`Entity`): The entity instance associated
  #      with the EntityContainer.
  #     network (str): The network that the entity is part of.
  #     named_network (str): The named network associated with the entity.
  #     tokens (List[str]): The list of tokens associated with the entity.
  #     typed_tokens (Dict[str, List[str]]): The typed tokens associated
  #      with the entity.
  #     instantiated_variables (InstantiationDict, optional): The
  #      instantiated variables associated with the entity. Defaults to
  #      **None**.
  # """

  def __init__(
      self,
      identifier: str,
      name: str,
      entity_instance: entity.Entity,
      network: str,
      named_network: str,
      tokens: List[str],
      typed_tokens: Dict[str, List[str]],
      parent_id: Optional[str] = None,
      instantiated_variables: Optional[InstantiationDict] = None,
      outgoing_connections: Optional[List[str]] = None,
  ):
    # """
    # Initializes an EntityContainer instance.

    # Args:
    #     entity_instance (Entity): The entity instance associated with
    #      the EntityContainer.
    #     network (str): The network that the entity is part of.
    #     named_network (str): The named network associated with the
    #      entity.
    #     tokens (List[str]): The list of tokens associated with the
    #      entity.
    #     typed_tokens (Dict[str, List[str]]): The typed tokens associated
    #      with the entity.
    #     instantiated_variables (InstantiationDict, optional): The
    #      instantiated variables associated with the entity. Defaults to
    #      **None**.
    # """
    super().__init__(identifier, name, parent_id)

    self.tokens = tokens
    self.typed_tokens = typed_tokens
    self.network = network
    self.named_network = named_network
    self.entity_instance = entity_instance
    self.instantiated_variables: InstantiationDict = \
        instantiated_variables or {}
    self.outgoing_connections = outgoing_connections or []

    # Adding the variables marked for initialization in the entity
    for var_id in self.entity_instance.get_init_vars():
      if var_id not in self.instantiated_variables:
        self.instantiated_variables[var_id] = {}

  def get_entity_name(self) -> str:
    return self.entity_instance.get_entity_name()

  def contains_init_var(self, var_id: str) -> bool:
    return self.entity_instance.is_init(var_id)

  def get_instantiation_value(
      self,
      var: variable.Variable,
      typed_token: Optional[str] = None,
  ) -> Optional[str]:
    """
    Retrieves the instantiation value of a variable

    Args:
        var_id (str): The identifier of the variable to retrieve.
        typed_token (str, optional): The typed token associated with the
         variable. Defaults to None.

    Returns:
        Optional[str]: The value of the variable. If the variable or
         typed_token does not exist, returns None.

    Raises:
        AssertionError: If var_id is not in instantiated_variables or if
         typed_token is not in typed_tokens["mass"].
    """
    # TODO: Replace with proper exception handling code
    assert var.var_id in self.instantiated_variables, \
        f"ERROR: In Topology Object \"{self.name}\": " \
        f"\"{var.var_id}\" not in instantiated variables."

    key_list = var.index_structures.copy()

    if isinstance(self, NodeSimple) and "I_1" in key_list:
      key_list[key_list.index("I_1")] = self.identifier

    if isinstance(self, Arc) and "I_2" in key_list:
      key_list[key_list.index("I_2")] = self.identifier

    if not key_list:
      key_list.append("1")

    if typed_token is not None:
      # TODO: Replace with proper exception handling code
      assert typed_token in self.typed_tokens["mass"], \
          f"ERROR: In Topology Object \"{self.name}\": " \
          f"\"{typed_token}\" not in typed_tokens."

      key_list[key_list.index("I_3")] = typed_token

    return self.instantiated_variables[var.var_id][tuple(key_list)]

  def set_instantiation_value(
      self,
      var: variable.Variable,
      typed_tokens: List[str],
      value: str,

  ) -> None:
    """
    Updates the instantiation value of a variable

    Args:
        var_id (str): The identifier of the variable to update.
        typed_token (str, optional): The typed token associated with the
         variable. Defaults to **None**.
        value (str, optional): The new value to set. Defaults to None.

    Raises:
        AssertionError: If var_id is not in instantiated_variables or if
         typed_token is not in typed_tokens["mass"].
    """
    # TODO: Replace with proper exception handling
    assert var.var_id in self.instantiated_variables, \
        f"ERROR: {var.var_id} not in instantiated variables."

    if typed_tokens:
      for tt in typed_tokens:
        assert tt in self.typed_tokens["mass"], \
            f"Error: {tt} not a token for variable {var.var_id}"

        self._set_instantiation_variable(var, value, tt)
    else:
      self._set_instantiation_variable(var, value)

  def _set_instantiation_variable(
      self,
      var: variable.Variable,
      value: str,
      tt: Optional[str] = None,
  ):
    key_list = var.index_structures.copy()

    if not key_list:
      key_list.append("1")

    if isinstance(self, NodeSimple) and "I_1" in key_list:
      key_list[key_list.index("I_1")] = self.identifier

    if isinstance(self, Arc) and "I_2" in key_list:
      key_list[key_list.index("I_2")] = self.identifier

    if tt is not None:
      key_list[key_list.index("I_3")] = tt

    self.instantiated_variables[var.var_id][tuple(key_list)] = value

  def add_outgoing_connection(self, connection_id: str) -> None:
    self.outgoing_connections.append(connection_id)

  def to_json(self):
    class_dict = super().to_json()
    class_dict["entity_name"] = self.entity_instance.get_entity_name()
    class_dict["network"] = self.network
    class_dict["named_network"] = self.named_network
    class_dict["tokens"] = self.tokens
    class_dict["typed_tokens"] = self.typed_tokens
    class_dict["instantiated_variables"] = {}

    for var_id, inst_info in self.instantiated_variables.items():
      class_dict["instantiated_variables"][var_id] = {
          str(key): value
          for key, value in inst_info.items()
      }
    class_dict["outgoing_connections"] = self.outgoing_connections

    return class_dict

  @classmethod
  def from_json(
      cls,
      data: Dict,
      all_entities: Dict[str, entity.Entity],
  ) -> Self:
    init_data = copy.deepcopy(data)

    # Only used to decide which class should be used
    del init_data["modeller_class"]

    # Switching to the entity object from its name
    init_data["entity_instance"] = all_entities[
        init_data.pop("entity_name")
    ]

    for var_id, inst_info in init_data["instantiated_variables"].items():
      init_data["instantiated_variables"][var_id] = {
          eval(key): value
          for key, value in inst_info.items()
      }

    return cls(**init_data)


class Arc(EntityContainer):
  """
  Represents an Arc, a specific type of EntityContainer.

  Inheritance:
      Inherits from :class:`EntityContainer`.

  Attributes:
      source (str): The source node of the arc.
      sink (str): The sink node of the arc.
  """

  def __init__(
      self,
      identifier: str,
      name: str,
      entity_instance: entity.Entity,
      network: str,
      named_network: str,
      tokens: List[str],
      typed_tokens: Dict[str, List[str]],
      parent_id: Optional[str] = None,
      instantiated_variables: Optional[InstantiationDict] = None,
      outgoing_connections: Optional[List[str]] = None,
      arc_type: Optional[str] = None,
  ):
    super().__init__(identifier, name, entity_instance, network, named_network,
                     tokens, typed_tokens, parent_id, instantiated_variables,
                     outgoing_connections)
    # TODO: Extend where interfaces are added
    if arc_type is None:
      arc_type = "Arc"


class NodeSimple(EntityContainer):
  """
  Represents a NodeSimple, a specific type of EntityContainer.

  Inheritance:
      Inherits from :class:`EntityContainer`.

  Attributes:
      conversions (str): The conversions associated with the node.
      injected_typed_tokens (Dict[str, str], optional): The injected
       typed tokens associated with the node.
  """

  def __init__(
      self,
      identifier: str,
      name: str,
      entity_instance: entity.Entity,
      network: str,
      named_network: str,
      tokens: List[str],
      typed_tokens: Dict[str, List[str]],
      conversions: str,
      parent_id: Optional[str] = None,
      instantiated_variables: Optional[InstantiationDict] = None,
      outgoing_connections: Optional[List[str]] = None,
      injected_typed_tokens: Optional[Dict[str, str]] = None,
  ):
    super().__init__(identifier, name, entity_instance, network, named_network,
                     tokens, typed_tokens, parent_id, instantiated_variables,
                     outgoing_connections)

    self.conversions = conversions
    self.injected_typed_tokens = injected_typed_tokens

  def to_json(self):
    class_dict = super().to_json()
    class_dict["outgoing_connections"] = self.outgoing_connections
    class_dict["conversions"] = self.conversions
    class_dict["injected_typed_tokens"] = self.injected_typed_tokens

    return class_dict


def build_topology_graph(
    topology_objects: List[TopologyObject],
) -> nx.Graph:
  """Build a graph from a list topology objects.

    This method iterates over all topology objects and adds them as
    nodes to the topology graph.

    Attr:
        topology_objects (List[TopologyObjects]): Topology objects to
         be added to the graph.
    """
  graph = nx.Graph()
  edges_info = []
  for topology_obj in topology_objects:
    if not isinstance(topology_obj, EntityContainer):
      continue

    for node_id in topology_obj.outgoing_connections:
      edges_info.append((topology_obj.identifier, node_id))

    graph.add_node(topology_obj)

  graph.add_edges_from(edges_info)

  return graph


modeller_class_mapping = {
    "NodeComposite": NodeComposite,
    "EntityContainer": EntityContainer,
    "NodeSimple": NodeSimple,
    "Arc": Arc,
}


class CustomJSONEncoder(json.JSONEncoder):
  """Custom encoder for Topology Objects."""

  def default(self, o):
    """Represents data from Topology Objects as a dictionary.

    Args:
        o (TopologyObject): Topology Object that will be encoded.

    Returns:
        dict: The dictionary representation of the TopologyObject. If
          the object is not an Topology Object instance then the default
          representation is returned.
    """
    if isinstance(o, TopologyObject):
      return o.to_json()

    return super().default(o)


def custom_decoder_factory(all_entities: Dict[str, entity.Entity]):
  class CustomJSONDecoder(json.JSONDecoder):
    """Custom decoder for Topology Objects."""

    def __init__(self):
      super().__init__(object_hook=self.custom_hook)
      self.all_entities = all_entities

    def custom_hook(self, dict_data: Dict):
      """Creates a Topology Object from json data.

      Args:
          dict_data (dict): The dictionary containing the JSON data.

      Raises:
          ValueError: If the 'modeller_class' key in the dictionary is not
           found in the 'modeller_class_mapping'.

      Returns:
          TopologyObject | Dict: An instance of the class object
          corresponding to the 'modeller_class' key in the dictionary, or
          the original dictionary if the 'modeller_class' key is
          not present.
      """
      if "modeller_class" in dict_data:
        if dict_data["modeller_class"] in modeller_class_mapping:
          class_object = modeller_class_mapping[dict_data["modeller_class"]]
          return class_object.from_json(dict_data, self.all_entities)
        else:
          raise ValueError(
              f"Invalid modeller_class: {dict_data['modeller_class']}")

      return dict_data

  return CustomJSONDecoder
