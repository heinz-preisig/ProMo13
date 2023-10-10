from typing import Dict, List, Union, Optional


class ModellerNode:
  # TODO: Add coordinates to be able to use pictures
  def __init__(
      self,
      id: str,
      name: str,
      network: str,
      named_network: str,
      modeller_class: str,
      type: str,
      variant: str,
      parent: str,
      instantiated_variables: Dict[str, Union[str, List[str]]],
      tokens: Optional[Dict[str, List[str]]] = None,
      injected_typed_tokens: Optional[Dict[str, str]] = None,
      children: Optional[List[str]] = None,
      conversions: Optional[Dict] = None,
  ):
    # Use **kwargs to capture all keyword arguments
    kwargs = locals()
    del kwargs['self']  # Remove 'self' from kwargs

    # Use setattr to set instance variables with their respective values
    for key, value in kwargs.items():
      setattr(self, key, value)
