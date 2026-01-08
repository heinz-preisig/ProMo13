"""Controller for the EquationSelectorDialog"""
import os

from typing import List, Tuple, Dict

from packages.Common.classes import entity
from packages.Common import resource_initialisation
# from packages.Common.ontology_container import OntologyContainer
# from packages.Common import resource_initialisation

class ControllerEquationSelectorDlg():
  """Controls the behavior of the dialog."""
  def __init__(self, entity_to_edit: entity.Entity, ontology_name: str):
    self.entity = entity_to_edit
    self.show_all = False

    self.variable_list = []
    self.equations_list = []

    self.path_ontology = resource_initialisation.DIRECTORIES[
      "ontology_location"
    ] % ontology_name

  def get_display_variables(self) -> List[Tuple[str, bool]]:
    """Decides what variables will be shown.

    The decision depends on the value of the `show_all` attribute. When
    it is **True**, all variables used in the entity will be shown. If
    the value is  **False** only variables without equations assigned
    will be shown.

    Returns:
        List[Tuple]: Contains tuples indicating the variables that will
          be shown. The tuple contains:

          - str: Path to the png file depicting the variable.
          - bool: **True** if any equation has been assigned to the
            variable. **False** otherwise.
    """
    display_variables = []
    self.variable_list.clear()

    for var_id, has_equation_assigned in self.entity.get_used_variables():
      # TODO Remove this when is no longer necessary.
      old_var_id = var_id.replace("V_", "")
      png_path = os.path.join(
          self.path_ontology,
          "LaTeX",
          f"variable_{old_var_id}.png",
        )
      if has_equation_assigned and self.show_all:
        self.variable_list.append(var_id)
        display_variables.append((png_path, has_equation_assigned))
      elif not has_equation_assigned:
        self.variable_list.append(var_id)
        display_variables.append((png_path, has_equation_assigned))

    return display_variables

  def get_display_equations(
    self,
    var_pos: int,
  ) -> Dict[str, List[Tuple[str, bool]]]:
    """Returns the equations that will be displayed for a variable.

    Args:
        var_pos (int): Position of the variable in the variable list.

    Returns:
        Dict[str, List[Tuple[str, bool]]]: The two keys in the dict are
          used to separate equations that have been written in explicit
          form for the variable and those whoe haven't. In both cases
          the information about the equations is stored in List where
          each element contains information about one equation in the
          form:

          - str: Path to the png file depicting the equation.
          - bool: **True** if the equation is already assigned to the
            variable. **False** otherwise.
    """
    self.equations_list.clear()
    display_equations = {}

    var_id = self.variable_list[var_pos]

    self.equations_list = self.entity.get_available_equations(var_id)
    for key, eq_list in self.equations_list.items():
      display_equations[key] = []
      for eq_id, is_already_assigned in eq_list:
        # TODO Remove this when is no longer necessary.
        old_eq_id = eq_id.replace("E_", "")
        png_path = os.path.join(
          self.path_ontology,
          "LaTeX",
          f"equation_{old_eq_id}.png",
        )
        display_equations[key].append((png_path, is_already_assigned))

    return display_equations

  def set_show_all(self, toggled: bool) -> None:
    # TODO Make this a public variable instead.
    self.show_all = toggled

  def add_new_var_info(
    self,
    var_pos: int,
    eq_info: Dict[str, List[bool]]
  ) -> None:
    """Adds the changes for a variable to the entity.

    Args:
        var_pos (int): Position of the variable in the variable list.
        eq_info (Dict[str, List[bool]]): The two keys in the dict are
          used to separate equations that have been written in explicit
          form for the variable and those who haven't. In both cases
          the information about the equations is stored in List where
          each element is **True** if the equation is assigned to the
            variable. **False** otherwise.
    """
    var_id = self.variable_list[var_pos]
    var_eq_info = {var_id: []}

    for key, eq_list in self.equations_list.items():
      for counter, (eq_id, _) in enumerate(eq_list):
        if eq_info[key][counter]:
          var_eq_info[var_id].append(eq_id)

    self.entity.generate_var_eq_tree(var_eq_info)
    # TODO Show a list of changes and ask for permission to continue.
    self.entity.update_var_eq_tree()
