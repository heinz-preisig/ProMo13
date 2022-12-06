"""Contains the entity class."""
# TODO Extend with an explanation of what an entity is.
import collections
import copy
from typing import List, TypedDict, Optional, Dict, Tuple
from typing_extensions import Self

from packages.Common.classes import equation

class EntityDict(TypedDict):
  """Creates a new type for a dictionary that stores an entity."""
  root_variable: str
  root_equation: str
  tree: Dict[str, List[str]]
  blocked: List[str]
  to_be_initialized: List[str]

class NodeInfo(TypedDict):
  """Creates a new type for a dictionary that stores node information.

  To be used with `OldEntityDict`. Only for backwards compatibility.
  """
  ancestors: List[str]
  children: List[str]

class OldEntityDict(TypedDict):
  """Creates a new type for a dictionary that stores an entity.

  Used only for backwards compatibility.
  """
  root_variable: str
  root_equation: str
  tree: Dict[str, NodeInfo]
  nodes: Dict[str, str]
  IDs: Dict[str, str]  # pylint: disable=invalid-name Backwards compatibility
  blocked: List[str]
  to_be_initialized: List[str]
  buddies: List[str]


class Entity():
  """Models an entity."""
  # TODO Add an explanation of what is an entity.

  def __init__(
    self,
    entity_name: str,
    root_var_id: str,
    root_eq_id: str,
    unused_eq_ids: List[str],
    entity_equations: Dict[str, equation.Equation],
    var_eq_tree: Optional[EntityDict] = None,
    to_be_init: Optional[List[str]] = None,
  ) -> None:
    """Initializes the entity.

    Args:
        entity_name (str): Name of the entity.
        root_var_id (str): Id of the root variable.
        root_eq_id (str): Id of the root equation.
        unused_eq_ids (List[str]): Ids of equations not in use in the
          Entity.
        entity_equations (List[equation.Equation]): All equations that
          can be used in the Entity.
        var_eq_tree (Optional[EntityDict], optional): Tree that links
          variables and equations that are being used in the Entity.
          Defaults to None.
        to_be_init (Optional[List[str]], optional): Ids of the variables
          that require initialization. Defaults to None.
    """
    self.entity_name = entity_name
    self.root_variable_id = root_var_id
    self.root_equation_id = root_eq_id
    self.unused_equations_ids = unused_eq_ids
    self.entity_equations = entity_equations

    self.var_eq_tree = var_eq_tree
    self.to_be_init = to_be_init

    self.temp_var_eq_tree = None

  @classmethod
  def from_old_dict(
    cls,
    entity_name: str,
    entity_dict: OldEntityDict,
    all_equations: Dict[str, equation.Equation],
    ) -> Self:
    """Provides an alternative constructor.

    **Only for backwards compatibility.**
    Used when the data of an existing entity is stored in a dictionary.
      Variable/equation ids are converted to `V_#`/`E_#` where # is the
      old id.

    Args:
        entity_name (str): name of the entity.
        entity_dict (OldEntityDict): Information about the entity stored
          in a dictionary (See `OldEntityDict`)
        all_equations (Dict[str, equation.Equation]): All the equations
          in the Ontology. The keys are equation ids and the values are
          Equation objects.

    Returns:
        Self: An instance of the clase initialized with the information
          stored in the dictionary.
    """
    unused_equations_ids = ["E_" + eq_id for eq_id in entity_dict["blocked"]]

    # `entity_equations` includes the equations used in the tree plus
    # the unused equations.
    entity_equations = {}
    for var_eq_id in entity_dict["IDs"]:
      if "equation" in var_eq_id:
        eq_id = var_eq_id.replace("equation", "E")
        entity_equations[eq_id] = all_equations[eq_id]

    for eq_id in unused_equations_ids:
      entity_equations[eq_id] = all_equations[eq_id]

    # Creating a new instance of the class with the minimum information.
    instance = cls(
      entity_name,
      "V_" + entity_dict["root_variable"],
      "E_" + entity_dict["root_equation"],
      unused_equations_ids,
      entity_equations,
    )

    # Building `var_eq_info` from the tree.
    var_eq_info = {}
    for var_eq_id, node_id in entity_dict["IDs"].items():
      if "variable" in var_eq_id:
        var_id = var_eq_id.replace("variable", "V")
        var_eq_info[var_id] = []
        children = entity_dict["tree"][node_id]["children"]
        for child_node_id in children:
          eq_id = entity_dict["nodes"][child_node_id].replace("equation", "E")
          var_eq_info[var_id].append(eq_id)

    # Generating and updating `var_eq_tree`.
    instance.generate_var_eq_tree(var_eq_info)
    instance.update_var_eq_tree()

    return instance

  @classmethod
  def from_root(
    cls,
    entity_name: str,
    root_var_id: str,
    root_eq_id: str,
    all_equations: Dict[str, equation.Equation],
  ) -> Self:
    """Provides an alternative constructor.

    Used when a new entity is going to be created and only information
      about the root is defined.

    Args:
        entity_name (str): Name of the entity.
        root_var_id (str): Id of the root variable.
        root_eq_id (str): Id of the root equation.
        all_equations (List[equation.Equation]): All the equations in
          the Ontology.

    Returns:
        Self: An instance of the clase initialized with the information
          of the root.
    """
    # `entity_equations` are found by doing a BFS on a graph where
    # variables and equations are nodes and an arc exist between them
    # if the equation contains the variable.
    entity_equations = {}
    entity_equations[root_eq_id] = all_equations[root_eq_id]

    entity_variables = set()
    entity_variables.add(root_var_id)

    queue = collections.deque()
    queue.append(root_eq_id)

    while queue:
      item_id = queue.popleft()
      if "E_" in item_id:
        for var_id in all_equations[item_id].get_incidence_list():
          # TODO Find a way to not add constants.
          if var_id not in entity_variables:
            entity_variables.add(var_id)
            queue.append(var_id)

      if "V_" in item_id:
        for eq_id, eq in all_equations.items():
          if eq_id not in entity_equations and eq.contains_var(item_id):
            entity_equations[eq_id] = eq
            queue.append(eq_id)

    # All equations are unused except for the root equation.
    unused_eq_ids = list(entity_equations.keys()).remove(root_eq_id)

    # Creating a new instance of the class with the minimum information.
    instance =  cls(
      entity_name,
      root_var_id,
      root_eq_id,
      unused_eq_ids,
      entity_equations,
    )

    # `var_eq_info` only contains information about the root.
    var_eq_info = {}
    var_eq_info[root_var_id] = [root_eq_id]

     # Generating and updating `var_eq_tree`.
    instance.generate_var_eq_tree(var_eq_info)
    instance.update_var_eq_tree()

    return instance

  def update_var_eq_tree(self) -> None:
    """Updates the variable-equation tree.

    The variable-equation tree is updated with the last tree generated
      by the method `generate_var_eq_tree`.
    """
    self.var_eq_tree = self.temp_var_eq_tree
    unused_equations_ids = list(self.entity_equations.keys())

    for node_id in self.var_eq_tree:
      if "V" in node_id:
        continue
      unused_equations_ids.remove(node_id)

    self.unused_equations_ids = unused_equations_ids

  def generate_var_eq_tree(
    self,
    add_var_eq_info: Dict[str, List[str]]
  ) -> List[str]:
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
    # Creates a new tree
    tree = {}

    # The original `var_eq_info` is the nodes of the tree representing
    # variables. If the `var_eq_tree` has not been constructed then
    # `var_eq_info` is an empty dict.
    # TODO Copy only the variable nodes if there are problems with big
    # trees.
    if self.var_eq_tree:
      var_eq_info = copy.deepcopy(self.var_eq_tree)
    else:
      var_eq_info = {}

    # Updating `var_eq_info` with the data in `add_var_eq_info`.
    for var_id, equation_ids in add_var_eq_info.items():
      var_eq_info[var_id] = equation_ids

    # Adding the root_var as the root of the tree
    tree[self.root_variable_id] = []

    # Initially only the pair (root_var_id, rood_eq_id) are added to the
    # queue. This is the only pair that will ALWAYS be in the entity.
    queue = collections.deque()
    queue.append((self.root_variable_id, self.root_equation_id))

    while queue:
      var_id, eq_id = queue.popleft()

      # Adding the equation to the tree
      tree[eq_id] = []

      # Adding the equation to the list of children of the variable.
      tree[var_id].append(eq_id)

      # Adding only the appropiate variables as children.
      inc_list = self.entity_equations[eq_id].get_incidence_list(var_id)
      for child_var_id in inc_list:
        # Only for variables that are not already in the tree.
        if child_var_id not in tree:
          # Adding the variable to the tree
          tree[child_var_id] = []

          # Adding the variable as children of the equation.
          tree[eq_id].append(child_var_id)

          # If there are equations assigned to this variable then a new
          # entry is added to the stack.
          if child_var_id in var_eq_info:
            for child_eq_id in var_eq_info[child_var_id]:
              queue.append((child_var_id, child_eq_id))

    # Saving the tree as a temporary tree.
    self.temp_var_eq_tree = tree

    # Getting the ids that were in the original tree and are not in the
    # new tree.
    ids_used_in_original = set()
    if self.var_eq_tree is not None:
      ids_used_in_original = set(self.var_eq_tree.keys())
    ids_used_in_new = set(tree.keys())

    return list(ids_used_in_original.difference(ids_used_in_new))

  def _gen_to_be_init(self) -> None:
    """Generates the list of variables that need to be initialized.

    A variable need to be initialized if it falls into one of the
      following statements:

      - No equations are assigned to the variable.
      - The equation assigned to the variable is used to instantiate
        with an undetermined value.
    """
    to_be_init = []

    for node_id, children in self.var_eq_tree.items():
      if "V" not in node_id:
        continue

      # No equations are assigned to the variable.
      if not children:
        to_be_init.append(node_id)
        continue

      # The equation instantiates with an undetermined value.
      eq_id = children[0]
      if self.entity_equations[eq_id].is_instantiation_eq():
        to_be_init.append(node_id)

    self.to_be_init = to_be_init

  def convert_to_dict(self) -> EntityDict:
    """Creates a dictionary with the information in the Entity.

    Returns:
        EntityDict: Dictionary containing the information of the
         Entity.
    """
    self._gen_to_be_init()

    entity_dict = {}
    entity_dict["tree"] = self.var_eq_tree
    entity_dict["root_variable"] = self.root_variable_id
    entity_dict["root_equation"] = self.root_equation_id
    entity_dict["blocked"] = self.unused_equations_ids
    entity_dict["to_be_initialized"] = self.to_be_init

    return entity_dict

  def convert_to_old_dict(self) -> OldEntityDict:
    """Creates a dictionary with the information in the Entity.

    **Only for backwards compatibility.**
    Returns:
        OldEntityDict: Dictionary containing the information of the
         Entity.
    """
    self._gen_to_be_init()

    tree = {}
    ids = {}
    nodes = {}

    # Creates a tree where each node_id corresponds to the order that
    # the original node was inserted (dicts are ordered by default)
    for counter, item in enumerate(self.var_eq_tree.keys()):
      str_repr = item.replace("V", "variable")
      str_repr = str_repr.replace("E", "equation")
      nodes[str(counter)] = str_repr
      ids[str_repr] = str(counter)
      tree[str(counter)] = {
        "ancestors": [],
        "children": [],
      }
    # Filling up the `children` field for each node.
    for parent_id, children in self.var_eq_tree.items():
      parent_str = parent_id.replace("V", "variable")
      parent_str = parent_str.replace("E", "equation")
      children_str = []
      for children_id in children:
        str_repr = children_id.replace("V", "variable")
        str_repr = str_repr.replace("E", "equation")
        children_str.append(ids[str_repr])

      tree[ids[parent_str]]["children"] = children_str

    # Filling up the `ancestor` field for each node.
    for parent_id in nodes:
      for child_id in tree[parent_id]["children"]:
        tree[child_id]["ancestors"] = [parent_id]
        tree[child_id]["ancestors"].extend(tree[parent_id]["ancestors"])

    entity_dict = {}
    entity_dict["tree"] = tree
    entity_dict["nodes"] = nodes
    entity_dict["IDs"] = ids
    entity_dict["root_variable"] = self.root_variable_id.replace("V_", "")
    entity_dict["root_equation"] = self.root_equation_id.replace("E_", "")

    blocked = [item.replace("E_", "") for item in self.unused_equations_ids]
    entity_dict["blocked"] = blocked

    to_be_init = [item.replace("V_", "") for item in self.to_be_init]
    entity_dict["to_be_initialized"] = to_be_init
    entity_dict["buddies"] = []

    return entity_dict

  def get_used_variables(self) -> List[Tuple[str, bool]]:
    """Compiles a list of all variables that are used in the entity.

    Returns:
        List[Tuple[str, bool]]: Contains information about all variables
          used in the entity. The tuple contains:

          - str: Id of the variable.
          - bool: **True** if any equation has been assigned to the
            variable. **False** otherwise.
    """
    used_variables = []
    for node_id, children in self.var_eq_tree.items():
      if "V" not in node_id:
        continue
      if node_id == self.root_variable_id:
        continue

      used_variables.append((node_id, bool(children)))

    return used_variables

  def get_available_equations(
    self,
    var_id: str,
  ) -> Dict[str, List[Tuple[str, bool]]]:
    """Compiles a list of equations that can be assigned to a variable.

    This list also includes the equations that are already assigned to
    the variable.

    Args:
        var_id (str): Id of the variable.

    Returns:
        Dict[str, List[Tuple[str, bool]]]: The two keys in the dict are
          used to separate equations that have been written in explicit
          form for the variable and those whoe haven't. In both cases
          the information about the equations is stored in List where
          each element contains information about one equation in the
          form:

          - str: Id of the equation.
          - bool: **True** if the equation is already assigned to the
            variable. **False** otherwise.
    """
    available_equations = {
      "explicit": [],
      "implicit": [],
    }
    if var_id in self.var_eq_tree:
      for eq_id in self.var_eq_tree[var_id]:
        if self.entity_equations[eq_id].is_explicit_for_var(var_id):
          available_equations["explicit"].append((eq_id, True))
        else:
          available_equations["implicit"].append((eq_id, True))

    for eq_id in self.unused_equations_ids:
      if not self.entity_equations[eq_id].contains_var(var_id):
        continue

      if self.entity_equations[eq_id].is_explicit_for_var(var_id):
        available_equations["explicit"].append((eq_id, False))
      else:
        available_equations["implicit"].append((eq_id, False))

    return available_equations


