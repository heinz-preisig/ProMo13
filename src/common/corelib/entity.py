"""
Defines the `Entity` class and its associated classes

Classes:
    :class:`Entity`: Basic block to build models.
    :class:`EntityMathGrah`: Manages algebraic relationships in an
     entity.
    :class:`VariableState`: Enum for the variable states in an Entity.
"""
from collections import deque
from enum import IntFlag
from typing import Dict, List, Optional, Union

from attrs import define, Factory
import networkx as nx

from src.common.corelib import Variable, Equation


class VariableState(IntFlag):
  """Variable states in an Entity"""

  #: Default state
  DEFAULT = 1

  #: The variable will be obtained from another entity
  INPUT = 2

  #: The variable can be used by another entity
  OUTPUT = 4

  #: The variable will be instantiated
  INSTANTIATION = 8

  #: An equation is used to compute the variable
  DEPENDENT = 16

  #: The variable state is not NONE
  ANY = DEFAULT | INPUT | OUTPUT | INSTANTIATION | DEPENDENT

  #: The variable does not have way of being computed
  PENDING = ~(INPUT | INSTANTIATION | DEPENDENT)

  def has_state(self, state: "VariableState") -> bool:
    """Checks if a state is among the states

    Args:
        state (VariableState): The state to be checked

    Returns:
        bool: **True** if the state is set, **False** otherwise.
    """
    return bool(self & state)


class EntityMathGraph:
  """Manages algebraic relationships in an entity

  Contains variables and equations and their relationship inside an
  entity.

  The whole structure revolves around the output variables and all the
  other elements exist to make possible their computation.
  """

  def __init__(self):
    # The structure is represented as a directed graph:
    # - Each node is either a Variable or an Equation.
    # - An arc from a Variable to an equation implies that the Equation
    #   is used to compute the variable.
    # - An arc from an Equation to a Variable implies that the Equation
    #   uses the variable to perform the computation.
    self._graph = nx.DiGraph()

    # Output variables in the Entity. All variables and equations must
    # be connected to at least one of them or else they are not needed
    # and can be deleted.
    self._output_variables = set()

  @property
  def equations(self) -> List[Equation]:
    """All the equations in the graph"""
    return [
        node
        for node in self._graph.nodes()
        if isinstance(node, Equation)
    ]

  @property
  def variables(self) -> List[Variable]:
    """All the variables in the graph"""
    return [
        node
        for node in self._graph.nodes()
        if isinstance(node, Variable)
    ]

  @property
  def removable_variables(self) -> List[Variable]:
    """Variables that can be removed safely

    Safety in this case implies that no equation depends on them. The
    only variables that are not added or deleted with equations are the
    output variables. Even among them there is a chance that a
    dependency relationship exists so that needs to be checked.
    """
    return [
        var
        for var in self._output_variables
        if self._graph.in_degree(var) == 0
    ]

  def add_variable(self, var: Variable) -> None:
    """Add a variable to the graph

    Args:
        var (Variable): Variable to be added.
    """
    self._output_variables.add(var)
    self._graph.add_node(var)

  def add_equation(
      self,
      dependent_var: Variable,
      eq: Equation
  ) -> List[Variable]:
    """Add an equation to the graph

    Equations can only be added if there is a variable in the structure
    that can be computed from the equation. That is the reason why the
    dependent variable is also passed as argument.

    When an equation is added, its independent variables are also added
    to the structure.

    Args:
        dependent_var (Variable): Variable to be computed with the
         equation.
        eq (Equation): Equation to be added.

    Returns:
        List[Variable]: Variables added automatically when the equation
         is added. Includes variables that already existed in the
         structure but would be addedd otherwise.
    """
    self._graph.add_edge(dependent_var, eq)

    independent_variables = eq.independent_variables
    for independent_var in independent_variables:
      self._graph.add_edge(eq, independent_var)

    return independent_variables

  def update_output_variables(self, var: Variable, is_output: bool) -> None:
    """Update the output variables

    Changes if a variable is considered output.
    DOES NOT add or remove a variable from the structure.

    Args:
        var (Variable): Variable to look up.
        is_output (bool): Indicates if the variable belongs to the
         output of the Entity or not.
    """
    if is_output:
      self._output_variables.add(var)
    elif var in self._output_variables:
      self._output_variables.remove(var)

  def remove_variable(self, var: Variable) -> List[Variable]:
    """Remove a variable from the graph

    Can result in the removal of other variables and/or equations that
    are no longer needed.

    Args:
        var (Variable): Variable to be removed.

    Returns:
        List[Variable]: Variables removed as a result of the removal of
        the variable.
    """
    if var in self._output_variables:
      self._output_variables.remove(var)

    return self._remove_node(var)

  def remove_equation(self, eq: Equation) -> List[Variable]:
    """Remove an equation from the graph

    Can result in the removal of other variables and/or equations that
    are no longer needed.

    Args:
        eq (Equation): Equation to be removed.

    Returns:
        List[Variable]: Variables removed as a result of the removal of
         the equation.
    """
    incoming_edges = list(self._graph.in_edges(eq))
    self._graph.remove_edges_from(incoming_edges)

    return self._remove_node(eq)

  def _remove_node(
      self,
      node_to_remove: Union[Variable, Equation]
  ) -> List[Variable]:
    """Remove a node

    It also removes all other nodes that are no longer needed.

    Args:
        node_to_remove (Union[Variable, Equation]): The node to remove.

    Returns:
        List[Variable]: Removed variables.
    """

    removed_nodes = set()
    queue = deque([node_to_remove])

    while queue:
      node = queue.popleft()

      if self._is_node_disconnected(node):
        queue.extend(self._graph.successors(node))
        self._graph.remove_node(node)
        removed_nodes.add(node)

    return [
        node
        for node in removed_nodes
        if isinstance(node, Variable)
    ]

  def _is_node_disconnected(self, node: Union[Variable, Equation]) -> bool:
    """Check if a node is disconnected

    Disconnection implies that there is no path from any of the
    nodes containing output variables to the node.

    Args:
        node (Union[Variable, Equation]): Node to be checked.

    Returns:
        bool: **True** if the node is disconnected, **False** otherwise.
    """
    for var in self._output_variables:
      if nx.has_path(self._graph, var, node):
        return False

    return True

  def get_equation_for_variable(self, var: Variable) -> Optional[Equation]:
    """Return the equation for a variable

    Args:
        var (Variable): Variable used for the query.

    Returns:
        Equation: Equation that can be used to compute the variable or
         **None** if there is not one.
    """
    return next(self._graph.successors(var), None)


@define(eq=False)
class Entity():
  """Basic block to build models

  Contains the mathematical representation for a part of the model and
  hierarchical properties from the ontology to facilitate its use.

  Attributes:
      name (str): The name of the entity.
  """
  _identifier: str
  name: str = ""
  _topology_type: str = ""
  _network: str = ""
  _token: str = ""
  _mechanism: str = ""
  _nature: str = ""
  _variable_states: Dict[Variable, VariableState] = Factory(dict)
  _math_graph: EntityMathGraph = Factory(EntityMathGraph)

  @property
  def identifier(self) -> str:
    """Identifier of the entity"""
    return self._identifier

  @property
  def topology_type(self) -> str:
    """Topology type of the entity"""
    # TODO: This should be an enum in the topology module.
    return self._topology_type

  @property
  def removable_variables(self) -> List[Variable]:
    """Variables that can be removed safely"""
    return self._math_graph.removable_variables

  def get_variables(
      self, query_state: VariableState = VariableState.ANY
  ) -> List[Variable]:
    """Return variables with a certain state

    Returns all variables if no state is provided.

    Args:
        query_state (VariableState, optional): State that all returned
         variables must have. Defaults to VariableState.ANY.

    Returns:
        List[Variable]: Variables that match the query state.
    """
    return [
        var
        for var, var_state in self._variable_states.items()
        if var_state.has_state(query_state)
    ]

  def add_new_variable(
      self,
      var: Variable,
  ) -> None:
    """Add a new variable

    Variables added in this way always have the OUTPUT state which makes
    them imposible to delete as a consequence of other deletions.

    Args:
        var (Variable): Variable to be added.
    """
    self._variable_states[var] = VariableState.OUTPUT
    self._math_graph.add_variable(var)

  def update_variable(
      self,
      var: Variable,
      new_state: VariableState,
      new_equation: Optional[Equation] = None,
  ) -> None:
    """Update a variable

    Both the variable state and its equation might have changed so they
    both need to be checkd and updated if necesary. See:

    * :meth:`update_variable_state`: To handle the state change.
    * :meth:`update_variable_equation`: To handle the equation update.

    Args:
        var (Variable): Variable to be updated.
        new_state (VariableState): New state for the variable.
        new_equation (Optional[Equation]): Equation to compute the
        variable. Defaults to None.
    """
    self._check_variable(var)

    old_state = self._variable_states[var]
    if new_state != old_state:
      self._update_variable_state(var, new_state, old_state)

    old_equation = self._math_graph.get_equation_for_variable(var)
    if new_equation != old_equation:
      self._update_variable_equation(var, new_equation, old_equation)

  def _update_variable_state(
      self,
      var: Variable,
      new_state: VariableState,
      old_state: VariableState,
  ) -> None:
    """Updates the state of a variable

    In case there is a change in the OUTPUT state then the math graph
    needs to be updated as well.

    Args:
        var (Variable): Variable whose state is being updated.
        new_state (VariableState): New state of the variable.
        old_state (VariableState): Old state of the variable.
    """
    was_var_output = old_state.has_state(VariableState.OUTPUT)
    is_var_output = new_state.has_state(VariableState.OUTPUT)

    if was_var_output != is_var_output:
      self._math_graph.update_output_variables(var, is_var_output)

    self._variable_states[var] = new_state

  def _update_variable_equation(
      self,
      var: Variable,
      new_equation: Optional[Equation],
      old_equation: Optional[Equation],
  ) -> None:
    """Update the equation for a variable

    When the equation assigned to a variable changes, the math graph
    needs to be updated.

    The new equation is added before deleting the old one to avoid
    the removal of variables/equations that the new equation might use.

    Args:
        var (Variable): Variable whose equation is being updated
        new_equation (Equation): New equation for the variable
    """
    variables_to_add: List[Variable] = []
    variables_to_delete: List[Variable] = []

    if new_equation is not None:
      variables_from_equation = self._math_graph.add_equation(
          var, new_equation
      )
      variables_to_add = [
          var
          for var in variables_from_equation
          if var not in self._variable_states
      ]

    if old_equation is not None:
      variables_to_delete = self._math_graph.remove_equation(
          old_equation
      )

    self._update_state_dict(variables_to_add, variables_to_delete)

  def _update_state_dict(
      self,
      variables_to_add: List[Variable],
      variables_to_delete: List[Variable],
  ) -> None:
    """Update the state dictionary

    Add and remove variables from the variable_states dictionary. Added
    variables are always added with the DEFAULT state.

    Args:
        variables_to_add (List[Variable]): Variables to be added.
        variables_to_delete (List[Variable]): Varibales to be deleted.
    """
    for var in variables_to_add:
      self._variable_states[var] = VariableState.DEFAULT

    for var in variables_to_delete:
      del self._variable_states[var]

  def get_equation_for_variable(self, var: Variable) -> Optional[Equation]:
    """Return the equation for a variable

    Args:
        var (Variable): Variable whose equation is returned.

    Returns:
        Optional[Equation]: The equation that is used to compute the
         variable or **None** if there is not one.
    """
    self._check_variable(var)

    return self._math_graph.get_equation_for_variable(var)

  def get_variable_state(self, var: Variable) -> VariableState:
    """Return the state of a variable

    Args:
        var (Variable): variable whose state is returned.

    Returns:
        VariableState: The state of the variable.
    """
    self._check_variable(var)
    return self._variable_states[var]

  def _check_variable(self, var: Variable) -> None:
    """Checks if the variable is in the entity

    Args:
        var (Variable): Variable to be checked.

    Raises:
        ValueError: If the variable is not in the entity.
    """
    if var not in self._variable_states:
      msg = f"{var.label} not in entity {self.name}"
      raise ValueError(msg)

  def remove_variable(self, var: Variable) -> None:
    """Removes a variable from the entity

    Args:
        var (Variable): Variable to be removed

    Raises:
        ValueError: If the variable can not be removed.
    """
    if var not in self._math_graph.removable_variables:
      msg = (
          f"{var.label} can not be deleted from entity {self.name}."
          f"Remove other uses before trying to remove it."
      )
      raise ValueError(msg)

    removed_variables = self._math_graph.remove_variable(var)
    self._update_state_dict([], removed_variables)
