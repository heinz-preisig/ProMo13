"""Contains the entity class."""
# TODO Extend with an explanation of what an entity is.
# TODO Update the docstrings.
import collections
import copy
from typing import List, TypedDict, Optional, Dict, Tuple, Callable
from typing_extensions import Self
from pprint import pprint as pp

from packages.Common.classes import equation


class EntityDict(TypedDict):
  """Creates a new type for a dictionary that stores an entity."""
  index_set: str
  integrators: Dict[str, str]
  var_eq_forest: List[Dict[str, List[str]]]
  init_vars: List[str]
  input_vars: List[str]
  output_vars: List[str]


class Entity():
  """Models an entity."""
  # TODO Add an explanation of what is an entity.

  def __init__(
      self,
      entity_name: str,
      all_equations: Dict[str, equation.Equation],
      index_set: Optional[str] = None,
      integrators: Optional[Dict[str, str]] = {},
      var_eq_forest: Optional[List[Dict[str, List[str]]]] = [],
      init_vars: Optional[List[str]] = [],
      input_vars: Optional[List[str]] = [],
      output_vars: Optional[List[str]] = [],
  ) -> None:
    # """Initializes the entity.

    # Args:
    #     entity_name (str): Name of the entity.
    #     var_eq_tree (Optional[EntityDict], optional): List of trees that
    #       link variables and equations used in the Entity.
    #       Defaults to None.
    #     init_vars (Optional[List[str]], optional): Ids of the variables
    #       that require initialization. Defaults to None.
    # """
    self.entity_name = entity_name
    self.index_set = index_set
    self.integrators = integrators
    self.var_eq_forest = var_eq_forest
    self.init_vars = init_vars
    self.input_vars = input_vars
    self.output_vars = output_vars
    self.all_equations = all_equations

    if entity_name != "Topology":
      network, ent_type, str1, name = entity_name.split(".")
      token, mechanism, nature = str1.split("|")

      self.index_set = ent_type[0].capitalize() + "_" + mechanism[:4]

    self.temp_var_eq_forest = None
    self.merge_conflicts = {}
    self.merged_vars = {}
    self.undo_merging = {}

    # pp(self.all_equations)

  def integrators_info(self):
    return list(self.integrators.items())

  def get_integrators_eq(self):
    return sorted(list(self.integrators.values()))

  def get_equations(self):
    # TODO: Check if something breaks after returning all equations
    # including the integrators.
    equations = []
    for tree in self.var_eq_forest:
      equations.extend([
          key
          for key in tree
          if "E_" in key
      ])

    return sorted(equations)

  def get_variables(self):
    variables = list(self.integrators.keys())

    for tree in self.var_eq_forest:
      variables.extend([
          key
          for key in tree
          if "V_" in key
      ])

    return sorted(variables)

  def get_input_vars(self):
    return sorted(self.input_vars)

  def set_input_var(self, var_id, is_input):
    if is_input:
      if var_id not in self.input_vars:
        self.input_vars.append(var_id)
    else:
      if var_id in self.input_vars:
        self.input_vars.remove(var_id)

  def get_output_vars(self):
    return sorted(self.output_vars)

  def set_output_var(self, var_id, is_output):
    if is_output:
      if var_id not in self.output_vars:
        self.output_vars.append(var_id)
    else:
      if var_id in self.output_vars:
        self.output_vars.remove(var_id)

  def get_init_vars(self):
    return sorted(self.init_vars)

  def set_init_var(self, var_id, is_init):
    if is_init:
      if var_id not in self.init_vars:
        self.init_vars.append(var_id)
    else:
      if var_id in self.init_vars:
        self.init_vars.remove(var_id)

  def get_pending_vars(self):
    no_eq_vars = set()
    for tree in self.var_eq_forest:
      for key, value in tree.items():
        if "V_" in key and not value:
          no_eq_vars.add(key)

    pending_vars = no_eq_vars - \
        (set(self.input_vars) | set(self.init_vars))

    return sorted(list(pending_vars))

  def get_var_status(self, var_id):
    return [
        self.get_eq_for_var(var_id),
        self.is_input(var_id),
        self.is_output(var_id),
        self.is_init(var_id)
    ]

  def is_init(self, var_id):
    return var_id in self.init_vars

  def is_var_top_level(self, var_id):
    if var_id not in self.output_vars:
      return False

    self.output_vars.remove(var_id)
    deleted_vars = self.generate_var_eq_forest({})[2]
    self.output_vars.append(var_id)

    if var_id in deleted_vars:
      return True
    else:
      return False

  # @classmethod
  # def from_root(
  #   cls,
  #   entity_name: str,
  #   root_var_id: str,
  #   root_eq_id: str,
  #   all_equations: Dict[str, equation.Equation],
  # ) -> Self:
  #   """Provides an alternative constructor.

  #   Used when a new entity is going to be created and only information
  #     about the root is defined.

  #   Args:
  #       entity_name (str): Name of the entity.
  #       root_var_id (str): Id of the root variable.
  #       root_eq_id (str): Id of the root equation.
  #       all_equations (List[equation.Equation]): All the equations in
  #         the Ontology.

  #   Returns:
  #       Self: An instance of the clase initialized with the information
  #         of the root.
  #   """
  #   # `entity_equations` are found by doing a BFS on a graph where
  #   # variables and equations are nodes and an arc exist between them
  #   # if the equation contains the variable.
  #   entity_equations = {}
  #   entity_equations[root_eq_id] = all_equations[root_eq_id]

  #   entity_variables = set()
  #   entity_variables.add(root_var_id)

  #   queue = collections.deque()
  #   queue.append(root_eq_id)

  #   while queue:
  #     item_id = queue.popleft()
  #     if "E_" in item_id:
  #       for var_id in all_equations[item_id].get_incidence_list():
  #         # TODO Find a way to not add constants.
  #         if var_id not in entity_variables:
  #           entity_variables.add(var_id)
  #           queue.append(var_id)

  #     if "V_" in item_id:
  #       for eq_id, eq in all_equations.items():
  #         if eq_id not in entity_equations and eq.contains_var(item_id):
  #           entity_equations[eq_id] = eq
  #           queue.append(eq_id)

  #   # All equations are unused except for the root equation.
  #   unused_eq_ids = list(entity_equations.keys()).remove(root_eq_id)

  #   # Creating a new instance of the class with the minimum information.
  #   instance =  cls(
  #     entity_name,
  #     root_var_id,
  #     root_eq_id,
  #     unused_eq_ids,
  #     entity_equations,
  #   )

  #   # `var_eq_info` only contains information about the root.
  #   var_eq_info = {}
  #   var_eq_info[root_var_id] = [root_eq_id]

  #    # Generating and updating `var_eq_tree`.
  #   instance.generate_var_eq_tree(var_eq_info)
  #   instance.update_var_eq_tree()

  #   return instance

  def update_var_eq_tree(self) -> None:
    """Updates the variable-equation tree.

    The variable-equation tree is updated with the last tree generated
      by the method `generate_var_eq_tree`.
    """
    self.var_eq_forest = self.temp_var_eq_forest

    # Removing all variables that are not in the entity from the lists
    # input, output and init
    all_vars = set(self.get_variables())
    self.input_vars = list(
        set(self.input_vars).intersection(all_vars)
    )
    # TODO: Verify if this is needed. In principle all output vars should
    # remain.
    self.output_vars = list(
        set(self.output_vars).intersection(all_vars)
    )
    self.init_vars = list(
        set(self.init_vars).intersection(all_vars)
    )
    self.integrators = {}
    for tree in self.var_eq_forest:
      new_integrators = {}
      for key, values in tree.items():
        if "V_" in key and values and self.all_equations[values[0]].is_integrator():
          new_integrators[key] = values[0]
      for key in new_integrators:
        del tree[key]

      self.integrators.update(new_integrators)

  def generate_var_eq_forest(
      self,
      add_var_eq_info: Dict[str, List[str]]
  ) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Generates a new variable-equation tree.

    Also compiles the difference between the original tree and the newly
      generated tree.
    Args:
        add_var_eq_info (Dict[str, List[str]]): Additional information
          about the equations assigned to variables. The keys are ids
          of variables and the values are the ids of the equations
          assigned to those variables.

    Returns:
        List[str]: Ids of all variables and equations that wouldn't be
          needed in the newly generated tree compared with the original
          tree.
    """
    # Creates a new forest
    self.temp_var_eq_forest = []

    # The original `var_eq_info` is the nodes of the tree representing
    # variables. If the `var_eq_forest` has not been constructed then
    # `var_eq_info` is an empty dict.
    # TODO Copy only the variable nodes if there are problems with big
    # trees.
    var_eq_info = {}
    for var_id, eq_id in self.integrators.items():
      var_eq_info[var_id] = [eq_id]

    for tree in self.var_eq_forest:
      var_eq_info.update(tree)

    # Updating `var_eq_info` with the data in `add_var_eq_info`.
    # TODO: Change to var_eq_info.update(add_var_eq_info)
    for var_id, equation_ids in add_var_eq_info.items():
      var_eq_info[var_id] = equation_ids

    # Adding the roots for all trees. The roots are always the
    # output variables.
    for var_id in self.output_vars:
      self.temp_var_eq_forest.append({
          var_id: []
      })

    # Initially only the root variables that have assigned equations
    # are added to the queue.
    queue = collections.deque()
    for var_id in self.output_vars:
      # TODO: Change this is multiple equations are not allowed
      # for a single variable.
      if var_id not in var_eq_info:
        continue

      for eq_id in var_eq_info[var_id]:
        queue.append((var_id, eq_id))

    while queue:
      # pp(queue)
      var_id, eq_id = queue.popleft()

      # Finding the correct tree
      curr_tree = None
      for tree in self.temp_var_eq_forest:
        if var_id in tree:
          curr_tree = tree
          break

      # Adding the equation to the tree
      curr_tree[eq_id] = []

      # Adding the equation to the list of children of the variable.
      curr_tree[var_id].append(eq_id)

      # pp(self.all_equations)
      # Adding only the appropiate variables as children.
      incidence_list = self.all_equations[eq_id].get_incidence_list(var_id)
      for child_var_id in incidence_list:
        # Only for variables that are not already in the forest.
        not_in_forest = True
        for tree in self.temp_var_eq_forest:
          if child_var_id in tree:
            not_in_forest = False
            break

        if not_in_forest:
          # Adding the variable to the tree
          curr_tree[child_var_id] = []

          # Adding the variable as children of the equation.
          curr_tree[eq_id].append(child_var_id)

          # If there are equations assigned to this variable then a new
          # entry is added to the queue.
          if child_var_id in var_eq_info:
            for child_eq_id in var_eq_info[child_var_id]:
              queue.append((child_var_id, child_eq_id))

    # Finding what vars and eqs have been added and which ones have
    # been deleted.
    ids_used_in_original = set()

    ids_used_in_original.update(list(self.integrators.keys()))
    for tree in self.var_eq_forest:
      ids_used_in_original.update(list(tree.keys()))

    ids_used_in_new = set()
    for tree in self.temp_var_eq_forest:
      ids_used_in_new.update(list(tree.keys()))

    added_ids = ids_used_in_new.difference(ids_used_in_original)
    deleted_ids = ids_used_in_original.difference(ids_used_in_new)

    added_vars = [
        element_id
        for element_id in added_ids
        if "V_" in element_id
    ]

    added_eqs = [
        element_id
        for element_id in added_ids
        if "E_" in element_id
    ]

    deleted_vars = [
        element_id
        for element_id in deleted_ids
        if "V_" in element_id
    ]

    deleted_eqs = [
        element_id
        for element_id in deleted_ids
        if "E_" in element_id
    ]

    return [added_vars, added_eqs, deleted_vars, deleted_eqs]

  # def _gen_init_vars(self) -> None:
  #   """Generates the list of variables that need to be initialized.

  #   A variable need to be initialized if it falls into one of the
  #     following statements:

  #     - No equations are assigned to the variable.
  #     - The equation assigned to the variable is used to instantiate
  #       with an undetermined value.
  #   """
  #   init_vars = []

  #   for node_id, children in self.var_eq_tree.items():
  #     if "V" not in node_id:
  #       continue

  #     # No equations are assigned to the variable.
  #     if not children:
  #       init_vars.append(node_id)
  #       continue

  #     # The equation instantiates with an undetermined value.
  #     eq_id = children[0]
  #     if self.entity_equations[eq_id].is_instantiation_eq():
  #       init_vars.append(node_id)

  #   self.init_vars = init_vars

  def convert_to_dict(self) -> EntityDict:
    """Creates a dictionary with the information in the Entity.

    Returns:
        EntityDict: Dictionary containing the information of the
         Entity.
    """
    # self._gen_init_vars()

    entity_dict = {}
    entity_dict["index_set"] = self.index_set
    entity_dict["integrators"] = self.integrators
    entity_dict["var_eq_forest"] = self.var_eq_forest
    entity_dict["init_vars"] = self.init_vars
    entity_dict["input_vars"] = self.input_vars
    entity_dict["output_vars"] = self.output_vars

    return entity_dict

  # def convert_to_old_dict(self) -> OldEntityDict:
  #   """Creates a dictionary with the information in the Entity.

  #   **Only for backwards compatibility.**
  #   Returns:
  #       OldEntityDict: Dictionary containing the information of the
  #        Entity.
  #   """
  #   self._gen_init_vars()

  #   tree = {}
  #   ids = {}
  #   nodes = {}

  #   # Creates a tree where each node_id corresponds to the order that
  #   # the original node was inserted (dicts are ordered by default)
  #   for counter, item in enumerate(self.var_eq_tree.keys()):
  #     str_repr = item.replace("V", "variable")
  #     str_repr = str_repr.replace("E", "equation")
  #     nodes[str(counter)] = str_repr
  #     ids[str_repr] = str(counter)
  #     tree[str(counter)] = {
  #       "ancestors": [],
  #       "children": [],
  #     }
  #   # Filling up the `children` field for each node.
  #   for parent_id, children in self.var_eq_tree.items():
  #     parent_str = parent_id.replace("V", "variable")
  #     parent_str = parent_str.replace("E", "equation")
  #     children_str = []
  #     for children_id in children:
  #       str_repr = children_id.replace("V", "variable")
  #       str_repr = str_repr.replace("E", "equation")
  #       children_str.append(ids[str_repr])

  #     tree[ids[parent_str]]["children"] = children_str

  #   # Filling up the `ancestor` field for each node.
  #   for parent_id in nodes:
  #     for child_id in tree[parent_id]["children"]:
  #       tree[child_id]["ancestors"] = [parent_id]
  #       tree[child_id]["ancestors"].extend(tree[parent_id]["ancestors"])

  #   entity_dict = {}
  #   entity_dict["tree"] = tree
  #   entity_dict["nodes"] = nodes
  #   entity_dict["IDs"] = ids
  #   entity_dict["root_variable"] = self.root_variable_id.replace("V_", "")
  #   entity_dict["root_equation"] = self.root_equation_id.replace("E_", "")

  #   blocked = [item.replace("E_", "") for item in self.unused_equations_ids]
  #   entity_dict["blocked"] = blocked

  #   init_vars = [item.replace("V_", "") for item in self.init_vars]
  #   entity_dict["init_varsialized"] = init_vars
  #   entity_dict["buddies"] = []

  #   return entity_dict

  # def get_used_variables(self) -> List[Tuple[str, bool]]:
  #   """Compiles a list of all variables that are used in the entity.

  #   Returns:
  #       List[Tuple[str, bool]]: Contains information about all variables
  #         used in the entity. The tuple contains:

  #         - str: Id of the variable.
  #         - bool: **True** if any equation has been assigned to the
  #           variable. **False** otherwise.
  #   """
  #   used_variables = []
  #   for node_id, children in self.var_eq_tree.items():
  #     if "V" not in node_id:
  #       continue
  #     if node_id == self.root_variable_id:
  #       continue

  #     used_variables.append((node_id, bool(children)))

  #   return used_variables

  # def get_available_equations(
  #   self,
  #   var_id: str,
  # ) -> Dict[str, List[Tuple[str, bool]]]:
  #   """Compiles a list of equations that can be assigned to a variable.

  #   This list also includes the equations that are already assigned to
  #   the variable.

  #   Args:
  #       var_id (str): Id of the variable.

  #   Returns:
  #       Dict[str, List[Tuple[str, bool]]]: The two keys in the dict are
  #         used to separate equations that have been written in explicit
  #         form for the variable and those whoe haven't. In both cases
  #         the information about the equations is stored in List where
  #         each element contains information about one equation in the
  #         form:

  #         - str: Id of the equation.
  #         - bool: **True** if the equation is already assigned to the
  #           variable. **False** otherwise.
  #   """
  #   available_equations = {
  #     "explicit": [],
  #     "implicit": [],
  #   }
  #   if var_id in self.var_eq_tree:
  #     for eq_id in self.var_eq_tree[var_id]:
  #       if self.entity_equations[eq_id].is_explicit_for_var(var_id):
  #         available_equations["explicit"].append((eq_id, True))
  #       else:
  #         available_equations["implicit"].append((eq_id, True))

  #   for eq_id in self.unused_equations_ids:
  #     if not self.entity_equations[eq_id].contains_var(var_id):
  #       continue

  #     if self.entity_equations[eq_id].is_explicit_for_var(var_id):
  #       available_equations["explicit"].append((eq_id, False))
  #     else:
  #       available_equations["implicit"].append((eq_id, False))

  #   return available_equations

  # def get_variables_to_instantiate(self) -> Tuple[List[str], List[str]]:
  #   """Return all variables in use in the entity.

  #   Returns:
  #       Tuple[List[str], List[str]]: The first list contains the ids of
  #         the variables that need to be initialized. The ids of the rest
  #         of the variables are in the second list.
  #   """
  #   # TODO Find a way to merge with `get_used_variables`.
  #   self._gen_init_vars()
  #   all_variables = set()
  #   for node_id in self.var_eq_tree:
  #     if "V_" in node_id:
  #       all_variables.add(node_id)

  #   all_variables.remove(self.root_variable_id)

  #   return (self.init_vars, list(all_variables - set(self.init_vars)))

  def is_input(self, var_id: str) -> bool:
    if var_id in self.input_vars:
      return True

    return False

  def is_output(self, var_id: str) -> bool:
    if var_id in self.output_vars:
      return True

    return False

  def get_eq_for_var(self, var_id: str) -> Optional[List[str]]:
    # TODO: Check that the change from returning a str -> List[str] is
    # not affecting anything else.
    if var_id in self.integrators:
      return [self.integrators[var_id]]

    for tree in self.var_eq_forest:
      if var_id in tree:
        return tree[var_id]

    return None

  def start_merging_process(self, parents: List[Self]):
    """Starts the merging process.

    Args:
      parents (List[Self]): Entities to me merged.

    Returns:
      bool: **True** if the merge is complete. **False** otherwise.
    """
    self.output_vars = self._merging_variables(parents, "get_output_vars")
    self.input_vars = self._merging_variables(parents, "get_input_vars")
    self.init_vars = self._merging_variables(parents, "get_init_vars")

    all_vars = self._merging_variables(parents, "get_variables")
    self.merged_vars = {}
    self.merge_conflicts = {}
    self.undo_merging = {}
    for var_id in all_vars:
      assigned_eqs = self._find_all_equations(var_id, parents)
      number_of_equations = len(assigned_eqs)
      if number_of_equations <= 1:
        self.merged_vars[var_id] = assigned_eqs
      else:
        self.merge_conflicts[var_id] = assigned_eqs

    self.generate_var_eq_forest(self.merged_vars)
    temp_input = self.input_vars
    temp_init = self.init_vars
    self.update_var_eq_tree()
    self.init_vars = temp_init
    self.input_vars = temp_input

    if not self.merge_conflicts:
      self._finish_merge()
      return True

    return False

  def get_conflict(self):
    for var_id, assigned_equations in self.merge_conflicts.items():
      if self.get_eq_for_var(var_id) is not None:
        return (var_id, assigned_equations)

    self._finish_merge()
    return None

  def solve_conflict(self, var_id, eq_id):
    self.undo_merging[var_id] = self.merge_conflicts.pop(var_id)
    self.merged_vars.update({var_id: [eq_id]})

    self.generate_var_eq_forest(self.merged_vars)
    temp_input = self.input_vars
    temp_init = self.init_vars
    self.update_var_eq_tree()
    self.init_vars = temp_init
    self.input_vars = temp_input

  def undo_merging_step(self):
    if not self.undo_merging:
      return None

    last_var_id = self.undo_merging.keys()[-1]
    self.merge_conflicts[last_var_id] = self.undo_merging.pop(last_var_id)
    del self.merged_vars[last_var_id]

    self.generate_var_eq_forest(self.merged_vars)
    temp_input = self.input_vars
    temp_init = self.init_vars
    self.update_var_eq_tree()
    self.init_vars = temp_init
    self.input_vars = temp_input

    return (last_var_id, self.merge_conflicts[last_var_id])

  def is_undo_merge_possible(self):
    return bool(self.undo_merging)

  def _finish_merge(self):
    self.merged_vars = {}
    self.merge_conflicts = {}
    self.undo_merging = {}

    self.input_vars = [
        var_id
        for var_id in self.input_vars
        if self.get_eq_for_var(var_id) is not None
    ]

    self.init_vars = [
        var_id
        for var_id in self.init_vars
        if self.get_eq_for_var(var_id) is not None
    ]

  def _merging_variables(
      self,
      parents: List[List[str]],
      method: Callable[[], List[str]]
  ) -> List[str]:

    merge_set = {
        var_id
        for ent in parents
        for var_id in getattr(ent, method)()
    }
    return list(merge_set)

  def _find_all_equations(self, var_id: str, parents: List[Self]) -> List[str]:
    equation_lists = [ent.get_eq_for_var(var_id) for ent in parents]
    all_equations = set()
    for eq_list in equation_lists:
      if eq_list is not None:
        all_equations.update(eq_list)

    return list(all_equations)
