from typing import Dict, List, Union


class ModellerArc:
  # TODO: Add coordinates to be able to use pictures
  def __init__(
      self,
      id: str,
      name: str,
      source: str,
      sink: str,
      token: Dict[str, List[str]],
      typed_tokens: Dict[str, str],
      network: str,
      named_network: str,
      # modeller_class: str, # TODO Maybe there needs to be one to differentiate from inter/intrafaces
      mechanism: str,
      nature: str,
      variant: str,
      instantiated_variables: Dict[str, Union[str, List[str]]],
  ):
    # Use **kwargs to capture all keyword arguments
    kwargs = locals()
    del kwargs['self']  # Remove 'self' from kwargs

    # Use setattr to set instance variables with their respective values
    for key, value in kwargs.items():
      setattr(self, key, value)
