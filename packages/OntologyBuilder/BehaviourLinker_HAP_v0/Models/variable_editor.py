import os
from typing import Dict

from PyQt5 import QtCore

from Common.classes import io
from Common.classes import equation
from Common.classes import variable
from Common.classes import entity

from Common import resource_initialisation

from OntologyBuilder.BehaviourLinker_HAP_v0.Models import image_list


class VariableEditorModel(QtCore.QObject):
  initial_data_fetched = QtCore.pyqtSignal(
      bool, bool, bool, QtCore.QModelIndex)
  # Methods

  def __init__(
      self,
      editing_entity: entity.Entity,
      editing_variable: variable.Variable,
      all_variables: Dict[str, variable.Variable],
      all_equations: Dict[str, equation.Equation],
  ):
    super().__init__()
    self.editing_entity = editing_entity
    self.editing_variable = editing_variable
    self.all_variables = all_variables
    self.all_equations = all_equations
    self.initial_config = None

    self.equations_model = image_list.ImageListModel()
    self.load_equations_model()

  # def load_equations_model(self):
  #   var_equations = list(self.editing_variable.get_equations())
  #   # TODO: Remove this when the entity stores objects instead of strings
  #   var_equations = [self.all_equations[eq_id] for eq_id in var_equations]
  #   self.equations_model.load_data(var_equations)

  # def load_equations_model(self) -> None:
  #   """Load the equations model with equations that use the current variable."""
  #   try:
  #     print("\n=== load_equations_model called ===")
  #     print(f"Loading equations for variable: {self.variable_id}")
  #
  #     # Get the variable's equations
  #     var_equations = self.entity.get_eq_for_var(self.variable_id)
  #     print(f"Found {len(var_equations)} equations for variable")
  #
  #     # Filter out any equations that don't exist in all_equations
  #     valid_equations = []
  #     for eq_id in var_equations:
  #       if eq_id in self.all_equations:
  #         valid_equations.append(self.all_equations[eq_id])
  #       else:
  #         print(f"Warning: Equation '{eq_id}' not found in all_equations")
  #
  #     print(f"Loading {len(valid_equations)} valid equations into model")
  #     self.equations_model.load_data(valid_equations)
  #
  #   except Exception as e:
  #     print(f"Error in load_equations_model: {e}")
  #     import traceback
  #     traceback.print_exc()
  #     # Initialize with empty list if there's an error
  #     self.equations_model.load_data([])

  # def load_equations_model(self) -> None:
  #   """Load the equations model with equations that use the current variable."""
  #   try:
  #     print("\n=== load_equations_model called ===")
  #     var_id = self.editing_variable.get_id()
  #     print(f"Loading equations for variable: {var_id}")
  #
  #     # Get the variable's equations
  #     var_equations = self.editing_entity.get_eq_for_var(var_id)
  #     print(f"Found {len(var_equations)} equations for variable")
  #
  #     # Filter out any equations that don't exist in all_equations
  #     valid_equations = []
  #     for eq_id in var_equations:
  #       if eq_id in self.all_equations:
  #         valid_equations.append(self.all_equations[eq_id])
  #       else:
  #         print(f"Warning: Equation '{eq_id}' not found in all_equations")
  #
  #     print(f"Loading {len(valid_equations)} valid equations into model")
  #     self.equations_model.load_data(valid_equations)
  #
  #   except Exception as e:
  #     print(f"Error in load_equations_model: {e}")
  #     import traceback
  #     traceback.print_exc()
  #     # Initialize with empty list if there's an error
  #     self.equations_model.load_data([])

  def load_equations_model(self) -> None:
    """Load the equations model with equations that can be used with the current variable."""
    try:
      print("\n=== load_equations_model called ===")
      var_id = self.editing_variable.get_id()
      print(f"Loading equations for variable: {var_id}")

      # Get all equations that can be used with this variable
      explicit_equations = []
      for eq_id, eq in self.all_equations.items():
        # Check if the equation is explicit for this variable (variable is on LHS)
        if eq.is_explicit_for_var(var_id):
          explicit_equations.append(eq)

      print(f"Found {len(explicit_equations)} explicit equations in ontology")
      self.equations_model.load_data(explicit_equations)

    except Exception as e:
      print(f"Error in load_equations_model: {e}")
      import traceback
      traceback.print_exc()
      # Initialize with empty list if there's an error
      self.equations_model.load_data([])


  def get_last_index(self):
    last_row = self.equations_model.rowCount() - 1

    return self.equations_model.index(last_row, 0)

  def fetch_initial_data(self):
    var_id = self.editing_variable.get_id()
    # In the equations model, find the item corresponding to  the
    # equation assigned to the variable in the entity. If no equation
    # have been assigned the item corresponding to "no_eq" is used
    # instead.
    eq = self.editing_entity.get_eq_for_var(var_id)
    index = QtCore.QModelIndex()
    if eq is not None and eq:
      # print(eq)
      index = self.equations_model.findItems(eq[0])[0].index()

    self.initial_config = {
        "is_input": self.editing_entity.is_input(var_id),
        "is_output": self.editing_entity.is_output(var_id),
        "is_init": self.editing_entity.is_init(var_id),
        "selected_eq": index
    }

    self.initial_data_fetched.emit(
        self.initial_config["is_input"],
        self.initial_config["is_output"],
        self.initial_config["is_init"],
        self.initial_config["selected_eq"],
    )

  def compute_changes(self, final_config):
    var_id = self.editing_variable.get_id()
    self.editing_entity.set_input_var(var_id, final_config["is_input"])
    self.editing_entity.set_output_var(var_id, final_config["is_output"])
    self.editing_entity.set_init_var(var_id, final_config["is_init"])

    equations = []
    index = final_config["selected_eq"]
    if index.isValid():
        equations.append(index.data())

    changes = self.editing_entity.generate_var_eq_forest({var_id: equations})
    # TODO: Remove when the entity contain instances instead of str
    changes[0] = [self.all_variables[var_id] for var_id in changes[0]]
    changes[2] = [self.all_variables[var_id] for var_id in changes[2]]
    changes[1] = [self.all_equations[eq_id] for eq_id in changes[1]]
    changes[3] = [self.all_equations[eq_id] for eq_id in changes[3]]

    self.editing_entity.set_input_var(var_id, self.initial_config["is_input"])
    self.editing_entity.set_output_var(
        var_id, self.initial_config["is_output"])
    self.editing_entity.set_init_var(var_id, self.initial_config["is_init"])

    return changes

  def accept_changes(self, final_config):
    var_id = self.editing_variable.get_id()
    self.editing_entity.set_input_var(var_id, final_config["is_input"])
    self.editing_entity.set_output_var(var_id, final_config["is_output"])
    self.editing_entity.set_init_var(var_id, final_config["is_init"])

    self.editing_entity.update_var_eq_tree()
