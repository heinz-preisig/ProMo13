"""Contains the equation class."""
from typing import TypedDict, List, Optional, Dict, Tuple
from typing_extensions import Self
from datetime import datetime


class EquationDict(TypedDict):
  """Creates a new type for a dictionary that stores an equation."""
  # TODO Update the way equations are stored.
  variable_ID: str  # pylint: disable=invalid-name Backwards compatibility
  lhs: str
  rhs: str
  network: str


class Equation():
  """Models an equation."""
  # TODO Add atributes.
  # TODO Explain the different possibilites for the terms in the equations

  def __init__(
      self,
      eq_id: str,
      img_path: str,
      type: str,
      lhs: Dict[str, str],
      rhs: Dict[str, str],
      network: str,
      doc: str,
      created: str,
      modified: str,
  ) -> None:

    self.eq_id = eq_id
    self.img_path = img_path
    self.type = type
    self.lhs = lhs
    self.rhs = rhs
    self.network = network
    self.doc = doc

    date_format = "%Y-%m-%d %H:%M:%S"
    self.created = datetime.strptime(created, date_format)
    self.modified = datetime.strptime(modified, date_format)

    # TODO: Probably throw an exception if "global_ID" is not found
    self.terms = self.lhs.get("global_ID").split()
    self.terms.extend(self.rhs.get("global_ID").split())

  def get_main_var_id(self):
    return self.terms[0]

  def get_id(self):
    return self.eq_id

  def get_img_path(self):
    return self.img_path

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

  def get_dependencies_list(self):
    var_id = self.get_main_var_id()
    return self.get_incidence_list(var_id)

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
    inc_list = list(set(filter(lambda term: "V" in term, self.terms)))
    if var_id is None:
      return inc_list

    if self.contains_var(var_id):
      inc_list.remove(var_id)
      # return inc_list

    # In some cases var_id wont be explicitly in the equation but
    # one of the variables with be a function of var_id.
    return inc_list
    # print(f"Variable {var_id} not in equation {self.eq_id}")
    # return []

  def is_instantiation_eq(self) -> bool:
    """Checks if this equation is used for instantiation with `Value`.

    Specifically it checks when the `Initialize` operator (O_11) and the
    `Value` variable (V_1) are in the rhs of the equation.

    Returns:
        Bool: **True** is the equation is used to instantiate a variable
          with an undetermined value. **False** otherwise.
    """
    # TODO Find a way that is independent from hard coded identifiers.
    # Probably from variable classes or tags
    if "O_11" in self.rhs and "V_1" in self.rhs:
      return True
    return False

  def parse_integrator(self):
    # NOTE: fixed HAP 2006-02-10

    from OntologyBuilder.OntologyEquationEditor.resources import CODE
    operator_integrator = CODE["global_ID"]["operator"]["Integral"].replace(" ","")
    components = self.rhs.get("global_ID").split()
    if components[0] != operator_integrator:
      return None

    return {
        "var_id": self.terms[0],
        "int_interval_ini": components[7],
        "int_interval_fin": components[9],
        "integrand": components[2],
        "int_var": components[4],
        "init_value": components[13],
    }

  def is_integrator(self):
    # TODO: Check for a better way to check this
    from OntologyBuilder.OntologyEquationEditor.resources import CODE
    operator_integrator = CODE["global_ID"]["operator"]["Integral"].replace(" ","")
    components = self.rhs.get("global_ID").split()
    if components[0] == operator_integrator:
      return True

    return False

  # def get_translation(self, language: str) -> Dict[str, str]:
  #   lhs_global_repr = self.lhs["global_ID"]
  #   rhs_global_repr = self.rhs["global_ID"]
  #   translation = {
  #       "lhs": equation_parser.,
  #       "rhs": self.rhs.get(language)
  #   }

  #  return translation

  def get_mod_date(self):
    return self.modified

  def is_interface_eq(self) -> bool:
    return ">>>" in self.network

  def is_root(self) -> bool:
    return "F_17" in str(self.rhs.get("global_ID"))
