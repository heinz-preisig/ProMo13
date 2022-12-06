"""Contains the equation class."""
from typing import TypedDict, List, Optional
from typing_extensions import Self

class EquationDict(TypedDict):
  """Creates a new type for a dictionary that stores an equation."""
  # TODO Update the way equations are stored.
  variable_ID: str # pylint: disable=invalid-name Backwards compatibility
  lhs: str
  rhs: str
  network: str


class Equation():
  """Models an equation."""
  # TODO Add atributes.
  # TODO Explain the different possibilites for the terms in the equations

  def __init__(self, eq_id: str, lhs: str, rhs: str, network: str) -> None:
    """Initializes the equation.

    An additional array `variables` is constructed to store the id of
    all the variable in the equation. The first position is always the
    id of the variable in the lhs.

    Args:
        eq_id (str): Id of the equation.
        lhs (str): Only contains one term representing a variable.
        rhs (str): Contains several terms describing the rhs of the
          equation.
        network (str): Network where the equation was defined.
    """
    self.eq_id = eq_id
    self.lhs = lhs
    self.rhs = rhs
    self.network = network

    self.terms = self.lhs.split()
    self.terms.extend(self.rhs.split())

  @classmethod
  def from_dict(cls, eq_id: str, eq_dict: EquationDict) -> Self:
    """Provides an alternative constructor.

    Uses the equation id and a dictionary containing the information
    about the equation.

    Args:
        eq_id (str): Id of the equation.
        eq_dict (str): Contains information about the equation in the
          following fields:

          - lhs (str): Only contains one term representing a variable.
          - rhs (str): Contains several terms describing the rhs of the
              equation.
          - network (str): Network where the equation was defined.

    Returns:
        Equation: An instance of the Equation class initialized with the
          values provided.
    """
    return cls(eq_id, eq_dict["lhs"], eq_dict["rhs"], eq_dict["network"])

  def is_explicit_for_var(self, var_id: str) -> bool:
    """Checks if a variable is in the lhs of the equation.

    Args:
        var_id (str): Id of the variable.

    Returns:
        bool: **True** if the variable is on the lhs of the equation.
          **False** otherwise.
    """
    if self.terms[0] == var_id:
      return True

    return False

  def contains_var(self, var_id: str) -> bool:
    """Checks if a variable appears in the equation.

    Args:
        var_id (str): Id of the variable.

    Returns:
        Bool: **True** if the variable appears on the equation.
          **False** otherwise.
    """
    if var_id in self.terms:
      return True

    return False

  def convert_to_dict(self) -> EquationDict:
    """Converts the equation into a dictionary.

    Returns:
        Dict: Dictionary containing the information of the equation with
          the following fields:

          - variable_ID (str): Id of the variable in the lhs.
          - lhs (str): Only contains one term representing a variable.
          - rhs (str): Contains several terms describing the rhs of the
              equation.
          - network (str): Network where the equation was defined.
    """
    eq_dict = {}
    eq_dict["variable_ID"] = self.terms[0]
    eq_dict["lhs"] = self.lhs
    eq_dict["rhs"] = self.rhs
    eq_dict["network"] = self.network

    return eq_dict

  def get_incidence_list(self, var_id: Optional[str] = None) -> List[str]:
    """Returns the incidence list for the equation.

    Args:
        var_id (Optional[str], optional): Id of the variable or **None**
          if all variables in the equation are desired. Defaults to
          **None**.

    Returns:
        List[str]: Contains the ids of the variables needed to calculate
          the variable passed as argument using this equation.

    """
    inc_list = list(filter(lambda term: "V" in term, self.terms))
    if var_id is None:
      return inc_list

    if self.contains_var(var_id):
      inc_list.remove(var_id)
      return inc_list

    print(f"Variable {var_id} not in equation {self.eq_id}")
    return []

  def is_instantiation_eq(self) -> bool:
    """Checks if this equation is used for instantiation with `Value`.

    Specifically it checks when the `Initialize` operator (O_11) and the
    `Value` variable (V_1) are in the rhs of the equation.

    Returns:
        Bool: **True** is the equation is used to instantiate a variable
          with an undetermined value. **False** otherwise.
    """
    # TODO Find a way that is independent from hard coded identifiers.
    if "O_11" in self.rhs and "V_1" in self.rhs:
      return True
    return False

