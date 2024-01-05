"""
This module defines the TopologyObject class and its subclasses.

The TopologyObject class is the base class for all topology objects used
in the modeller. These objects represent the fundamental building blocks
of the model's structure.

Subclasses of TopologyObject represent specific types of topology
objects, each with their own unique properties and methods. These
subclasses inherit from the TopologyObject base class and extend it with
functionality specific to each type of topology object.

Classes:
    TopologyObject: The base class for all Topology Objects.
    NodeComposite: Represents a Composite Node.
    EntityContainer: Represents a Topology Object linked to an Entity.
    NodeSimple: Represents a Simple Node.
    Arc: Represents an Arc.

Each class is documented in detail within its own docstring.
"""
from typing import List, Optional, Dict

from packages.Common.classes import entity

# Define type aliases
InstantiationDict = Dict[str, Dict[str, Optional[str]]]


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
    class_dict["name"] = self.name
    class_dict["parent_id"] = self.parent_id
    class_dict["modeller_class"] = self.__class__.__name__

    return class_dict


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
  """
  Represents a Topology Object linked to an Entity.

  Inheritance:
      Inherits from :class:`TopologyObject`.

  Attributes:
      entity_instance (:class:`Entity`): The entity instance associated
       with the EntityContainer.
      network (str): The network that the entity is part of.
      named_network (str): The named network associated with the entity.
      tokens (List[str]): The list of tokens associated with the entity.
      typed_tokens (Dict[str, List[str]]): The typed tokens associated
       with the entity.
      instantiated_variables (InstantiationDict, optional): The
       instantiated variables associated with the entity. Defaults to
       **None**.
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
      # TODO: Change this when the instantiated variableshave all the same type
      instantiated_variables: Optional[InstantiationDict] = None,
  ):
    """
    Initializes an EntityContainer instance.

    Args:
        entity_instance (Entity): The entity instance associated with
         the EntityContainer.
        network (str): The network that the entity is part of.
        named_network (str): The named network associated with the
         entity.
        tokens (List[str]): The list of tokens associated with the
         entity.
        typed_tokens (Dict[str, List[str]]): The typed tokens associated
         with the entity.
        instantiated_variables (InstantiationDict, optional): The
         instantiated variables associated with the entity. Defaults to
         **None**.
    """
    super().__init__(identifier, name, parent_id)

    self.entity_instance = entity_instance
    self.network = network
    self.named_network = named_network
    self.tokens = tokens
    self.typed_tokens = typed_tokens
    self.instantiated_variables: InstantiationDict = \
        instantiated_variables or {}

    # Adding the variables marked for initialization in the entity
    for var_id in self.entity_instance.get_init_vars():
      if var_id not in self.instantiated_variables:
        self.instantiated_variables[var_id] = {}
    #     # TODO: Connect this to the ontology instead
    #     if "I_3" in all_variables[var_id].index_structures:
    #       for tt in self.typed_tokens["mass"]:
    #         self.instantiated_variables[var_id][tt] = None
    #     else:
    #       self.instantiated_variables[var_id]["default"] = None

  def get_entity_name(self) -> str:
    return self.entity_instance.get_entity_name()

  def contains_init_var(self, var_id: str) -> bool:
    return self.entity_instance.is_init(var_id)

  def get_instantiation_value(
      self,
      var_id: str,
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
    assert var_id in self.instantiated_variables, \
        f"ERROR: In Topology Object \"{self.name}\": " \
        f"\"{var_id}\" not in instantiated variables."

    if typed_token is None:
      return self.instantiated_variables[var_id].get("default")
    else:
      # TODO: Replace with proper exception handling code
      assert typed_token in self.typed_tokens["mass"], \
          f"ERROR: In Topology Object \"{self.name}\": " \
          f"\"{typed_token}\" not in typed_tokens."
      return self.instantiated_variables[var_id].get(typed_token)

  def set_instantiation_value(
      self,
      var_id: str,
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
    assert var_id in self.instantiated_variables, \
        f"ERROR: {var_id} not in instantiated variables."

    if typed_tokens:
      for tt in typed_tokens:
        if tt in self.typed_tokens["mass"]:
          self.instantiated_variables[var_id][tt] = value
    else:
      self.instantiated_variables[var_id]["default"] = value

  def to_json(self):
    class_dict = super().to_json()
    class_dict["entity_name"] = self.entity_instance.get_entity_name()
    class_dict["network"] = self.network
    class_dict["named_network"] = self.named_network
    class_dict["tokens"] = self.tokens
    class_dict["typed_tokens"] = self.typed_tokens
    class_dict["instantiated_variables"] = self.instantiated_variables

    return class_dict


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
      tokens: List[str],
      typed_tokens: Dict[str, List[str]],
      network: str,
      named_network: str,
      source: str,
      sink: str,
      parent_id: Optional[str] = None,
      instantiated_variables: Optional[InstantiationDict] = None,
  ):
    super().__init__(identifier, name, entity_instance, network, named_network,
                     tokens, typed_tokens, parent_id, instantiated_variables)

    self.source = source
    self.sink = sink

  def to_json(self):
    class_dict = super().to_json()
    class_dict["source"] = self.source
    class_dict["sink"] = self.sink

    return class_dict


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
      tokens: List[str],
      typed_tokens: Dict[str, List[str]],
      network: str,
      named_network: str,
      conversions: str,
      parent_id: Optional[str] = None,
      instantiated_variables: Optional[InstantiationDict] = None,
      injected_typed_tokens: Optional[Dict[str, str]] = None,
  ):
    super().__init__(identifier, name, entity_instance, network, named_network,
                     tokens, typed_tokens, parent_id, instantiated_variables)
    self.conversions = conversions
    self.injected_typed_tokens = injected_typed_tokens

  def to_json(self):
    class_dict = super().to_json()
    class_dict["conversions"] = self.conversions
    class_dict["injected_typed_tokens"] = self.injected_typed_tokens

    return class_dict


modeller_class_mapping = {
    "NodeComposite": NodeComposite,
    "NodeSimple": NodeSimple,
    "Arc": Arc,
}
