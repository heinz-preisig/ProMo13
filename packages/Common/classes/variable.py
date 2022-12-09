"""Contains the variable class."""
from typing import Dict, List
from typing_extensions import TypedDict, Self


class OldEquationsinVariableDict(TypedDict):
  rhs: str
  type: str
  doc: str
  network: str
  incidence_list: List[str]


class OldVariableDict(TypedDict):
  """Creates a new type for a dictionary that stores info about a var"""
  aliases: Dict[str, str]
  doc: str
  equations: Dict[int, OldEquationsinVariableDict]
  index_structures: List[int]
  label: str
  network: str
  port_variable: bool
  tokens: List[str]
  type: str
  units: List[int]


class Variable():
  """Models a variable."""
  def __init__(self, var_id:str, label: str):
    """Initializes the variable

    Args:
        var_id (str): Id of the variable.
        label (str): Variable label.
    """
    self.var_id = var_id
    self.label = label

  @classmethod
  def from_old_dict(cls, var_id: str, var_dict: OldVariableDict) -> Self:
    """Provides an alternative constructor.

    Uses the variable id and a dictionary containing the information
    about the variable.
    **Only used for backwards compatibility.**

    Args:
        var_id (str): Id of the variable.
        var_dict (OldVariableDict): Contains information about the
          variable.

    Returns:
        Variable: An instance of the Variable class initialized with the
          values provided.
    """
    return cls(var_id, var_dict["label"])
