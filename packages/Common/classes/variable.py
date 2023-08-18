"""Contains the variable class."""
from typing import Dict, List
from typing_extensions import Self


class Variable():
  """Models a variable."""

  def __init__(
      self,
      var_id: str,
      img_path: str,
      aliases: Dict[str, str],
      doc: str,
      equations: List[str],
      index_structures: List[int],
      label: str,
      network: str,
      port_variable: bool,
      tokens: List[str],
      var_type: str,
      units: List[int],
  ):
    # """Initializes the variable

    # Args:
    #     var_id (str): Id of the variable.
    #     label (str): Variable label.
    # """
    self.var_id = var_id
    self.img_path = img_path
    self.aliases = aliases
    self.doc = doc
    self.equations = equations
    self.index_structures = [str(i) for i in index_structures]
    self.label = label
    self.network = network
    self.port_variable = port_variable
    self.tokens = tokens
    self.var_type = var_type
    self.units = units

  @classmethod
  def from_dict(
      cls,
      var_id: str,
      img_path: str,
      var_data: Dict,
  ) -> Self:
    """Provides an alternative constructor.

    Used when a new variable is going to be created from a Dict.

    Args:
      var_id (str): Id of the variable.
      var_data (Dict): Information about the variable stored in a Dict.

    Returns:
        Self: An instance of the clase initialized with the information
          stored in the Dict.
    """

    # Creating a new instance of the class
    return cls(
        var_id,
        img_path,
        var_data["aliases"],
        var_data["doc"],
        var_data["equations"],
        var_data["index_structures"],
        var_data["label"],
        var_data["network"],
        var_data["port_variable"],
        var_data["tokens"],
        var_data["type"],
        var_data["units"],
    )

  def get_id(self):
    return self.var_id

  def get_img_path(self):
    return self.img_path

  def get_equations(self):
    return tuple(self.equations)

  def convert_to_dict(self) -> Dict:
    output_dict = {}
    output_dict["aliases"] = self.aliases
    output_dict["doc"] = self.doc
    output_dict["equations"] = self.equations
    output_dict["index_structures"] = self.index_structures
    output_dict["label"] = self.label
    output_dict["network"] = self.network
    output_dict["port_variable"] = self.port_variable
    output_dict["tokens"] = self.tokens
    output_dict["type"] = self.var_type
    output_dict["units"] = self.units

    return output_dict

  def is_eligible(self, network, ent_type, tokens):
    # TODO: The variables need to be contructed so we can match with the
    # entities and see if they are eligible.
    # if network != self.network:
    #     return False
    if len(self.index_structures) != 1:
      return False

    own_type = ""
    index = self.index_structures[0]
    if index == "1" or index == "5" or index == "7":
      own_type = "node"

    if index == "2" or index == "6":
      own_type = "arc"

    # print(str(index) + own_type + " ## " + ent_type)
    if ent_type == own_type:
      return True

    return False

  def is_constant(self):
    if self.var_type == "constant":
      return True

    return False

  def is_topology(self):
    if self.var_type == "topology":
      return True

    return False

  def get_alias(self, language):
    return self.aliases[language]

  def get_indices(self):
    return self.index_structures
