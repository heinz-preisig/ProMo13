from typing import List, Optional, Dict, Union

from packages.Common.classes import entity


class TopologyObject:
  def __init__(
      self,
      id: str,
      name: str,
      modeller_class: str,
      parent: Optional[str],
      children: List[str] = [],
  ):
    self.id = id
    self.name = name
    self.parent = parent
    self.children = children

  def get_parent_id(self) -> Optional[str]:
    return self.parent

  def get_name(self) -> str:
    return self.name

  def get_modeller_class(self):
    return self.__class__


class NodeComposite(TopologyObject):
  def __init__(
      self,
      id: str,
      name: str,
      parent: Optional[str],
      children: List[str] = [],
  ):
    super().__init__(id, name, parent, children)


class EntityContainer(TopologyObject):
  def __init__(
      self,
      id: str,
      name: str,
      parent: Optional[str],
      children: List[str],
      entity_instance: entity.Entity,
      network: str,
      named_network: str,
      tokens: Dict[str, List[str]],
      instantiated_variables: Dict[str, Union[str, List[str]]] = {},
  ):
    super().__init__(id, name, parent, children)
    self.entity_instance = entity_instance
    self.tokens = tokens
    self.network = network
    self.named_network = named_network
    self.instantiated_variables = instantiated_variables

    # Adding the variables marked for initialization in the entity
    for var_id in self.entity_instance.get_init_vars():
      if var_id not in self.instantiated_variables:
        self.instantiated_variables[var_id] = None

  def get_entity_name(self) -> str:
    return self.entity_instance.get_entity_name()

  def contains_init_var(self, var_id: str) -> bool:
    return self.entity_instance.is_init(var_id)

  def get_instantiation_value(
      self,
      var_id: str,
      typed_token: Optional[str]
  ) -> Optional[str]:
    # TODO: Implement the part with the typed token.
    return self.instantiated_variables.get(var_id)

  def update_instantiation_value(self, var_id: str, value: str) -> None:
    self.instantiated_variables[var_id] = value


class Arc(EntityContainer):
  def __init__(
      self,
      id: str,
      name: str,
      parent: Optional[str],
      children: List[str],
      entity_instance: entity.Entity,
      instantiated_variables: Dict[str, Union[str, List[str]]],
      tokens: Dict[str, List[str]],
      network: str,
      named_network: str,
      source: str,
      sink: str,
  ):
    super().__init__(id, name, parent, children, entity_instance,
                     network, named_network, tokens, instantiated_variables)

    self.source = source
    self.sink = sink


class NodeSimple(EntityContainer):
  def __init__(
      self,
      id: str,
      name: str,
      parent: Optional[str],
      children: List[str],
      entity_instance: entity.Entity,
      instantiated_variables: Dict[str, Union[str, List[str]]],
      tokens: Dict[str, List[str]],
      network: str,
      named_network: str,
      conversions: str,
      injected_typed_tokens: Optional[Dict[str, str]]
  ):
    super().__init__(id, name, parent, children, entity_instance,
                     network, named_network, tokens, instantiated_variables)


modeller_class_mapping = {
    "NodeComposite": NodeComposite,
    "NodeSimple": NodeSimple,
    "Arc": Arc,
}
