"""Contains the variable class."""
from typing import Dict, List
from typing_extensions import Self
import json
from datetime import datetime


class Variable():
  """Models a variable."""

  def __init__(
      self,
      var_id: str,
      img_path: str,
      IRI: str,
      aliases: Dict[str, str],
      compiled_lhs: Dict[str, str],
      doc: str,
      equations: List[str],
      index_structures: List[str],
      label: str,
      network: str,
      port_variable: bool,
      tokens: List[str],
      type: str,
      units: List[int],
      created: str,
      modified: str,
  ):
    self.var_id = var_id
    self.img_path = img_path
    self.IRI = IRI
    self.aliases = aliases
    self.compiled_lhs = compiled_lhs
    self.doc = doc
    self.equations = equations
    self.index_structures = index_structures
    self.label = label
    self.network = network
    self.port_variable = port_variable
    self.tokens = tokens
    self.type = type
    self.units = units

    date_format = "%Y-%m-%d %H:%M:%S"
    self.created = datetime.strptime(created, date_format)
    self.modified = datetime.strptime(modified, date_format)

  def get_id(self):
    return self.var_id

  def get_img_path(self):
    return self.img_path

  def get_equations(self):
    return tuple(self.equations)

# TODO: At some point fix this so it can handle a complex case like the variable
# one.
  # def convert_to_dict(self) -> Dict:
  #   output_dict = {}
  #   output_dict["aliases"] = self.aliases
  #   output_dict["doc"] = self.doc
  #   output_dict["equations"] = self.equations
  #   output_dict["index_structures"] = self.index_structures
  #   output_dict["label"] = self.label
  #   output_dict["network"] = self.network
  #   output_dict["port_variable"] = self.port_variable
  #   output_dict["tokens"] = self.tokens
  #   output_dict["type"] = self.var_type
  #   output_dict["units"] = self.units

  #   return output_dict

  # TODO: Make a better name for this function
  def is_eligible(self, network, ent_type, tokens):
    # TODO: The variables need to be contructed so we can match with the
    # entities and see if they are eligible.
    # if network != self.network:
    #     return False

    # TODO: Check if a variable with no indices can be output
    if not self.index_structures:
      return False

    own_type = ""
    index = self.index_structures[0]
    if index == "I_1":
      own_type = "node"

    if index == "I_2":
      own_type = "arc"

    # print(str(index) + own_type + " ## " + ent_type)
    if ent_type == own_type:
      return True

    return False

  def is_constant(self):
    if self.type == "constant":
      return True

    return False

  def is_topology(self):
    if self.type == "topology":
      return True

    return False

  def get_alias(self, language):
    return self.aliases.get(language)

  def get_translation(self, language):
    return self.compiled_lhs.get(language)

  def get_indices(self):
    return self.index_structures

  def __str__(self):
    return json.dumps(self.__dict__)

  def get_mod_date(self):
    return self.modified
