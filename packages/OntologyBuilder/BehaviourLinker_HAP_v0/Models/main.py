import copy
import re

from PyQt5 import QtCore
from PyQt5 import QtGui
from uaclient.api.u.unattended_upgrades.status.v1 import UnattendedUpgradesStatusResult

from Common.classes import entity
from Common.classes import equation
from Common.classes import io as old_io
from Common.classes import variable
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import entity_editor
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import image_list
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import tree
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_merger import EntityMergerModel


# from common import io  # 2026.01.09 HAP removed for the time being


class SimpleVar:
  # Class variable to store the model reference
  _model = None

  def __init__(self, var_id, model=None):
    self._id = var_id
    self._equation = None
    self._variable = None
    self._model = model or SimpleVar._model

  def get_id(self):
    return self._id

  def get_img_path(self):
    """Get the image path for this variable/equation.
    
    Returns:
        str: Path to the image file or a default icon if not found
    """
    # First try to get the model from instance, then from class
    model = self._model or SimpleVar._model

    if model:
      # Check if this is an equation
      if self._id in getattr(model, 'all_equations', {}):
        self._equation = model.all_equations.get(self._id)
        if hasattr(self._equation, 'get_img_path') and callable(self._equation.get_img_path):
          return self._equation.get_img_path()

      # Check if this is a variable
      if self._id in getattr(model, 'all_variables', {}):
        self._variable = model.all_variables.get(self._id)
        if hasattr(self._variable, 'get_img_path') and callable(self._variable.get_img_path):
          return self._variable.get_img_path()

    # Default fallback
    if self._id and 'eq_' in self._id:
      return ":/icons/equation.png"
    return ":/icons/variable.png"

  def get_display_text(self):
    """Return a more detailed display text for the variable/equation."""
    # Try to get the equation or variable details if they exist in the model
    model = self._model or SimpleVar._model

    if model:
      if not self._equation and self._id in getattr(model, 'all_equations', {}):
        self._equation = model.all_equations.get(self._id)
      if not self._variable and self._id in getattr(model, 'all_variables', {}):
        self._variable = model.all_variables.get(self._id)

    if self._equation:
      return f"{self._id}: {self._equation.equation if hasattr(self._equation, 'equation') else 'No equation'}"
    elif self._variable:
      return f"{self._id}: {self._variable.value if hasattr(self._variable, 'value') else 'No value'}"
    return self._id

  def __repr__(self):
    return f"SimpleVar({self._id})"

  @classmethod
  def set_model(cls, model):
    """Set the model reference for all SimpleVar instances."""
    cls._model = model
    cls._model = model


class MainModel(QtCore.QObject):
  # Signals
  tree_changed = QtCore.pyqtSignal()

  # Methods
  def __init__(self) -> None:
    super().__init__()
    # self._io_manager = io.IOManager()                                     # 2026.01.09 HAP removed for the time being
    # # Remove when the user have the option to change the repository       # 2026.01.09 HAP removed for the time being
    # self._io_manager.set_repository_location("../../Ontology_Repository") # 2026.01.09 HAP removed for the time being

    self.ontology_name = ""
    self.ontology = None
    self.all_entities: dict[str, entity.Entity] = {}
    self.all_variables: dict[str, variable.Variable] = {}
    self.all_equations: dict[str, equation.Equation] = {}

    # PyQt models
    self.entity_tree_model = tree.TreeModel()
    self.entity_list_models = [
            image_list.ImageListModel(self),  # Integrators
            image_list.ImageListModel(self),  # Equations
            image_list.ImageListModel(self),  # Input_vars
            image_list.ImageListModel(self),  # Output_vars
            image_list.ImageListModel(self),  # Init_vars
            image_list.ImageListModel(self),  # Pending_vars
            ]

    # Set the model reference for SimpleVar instances
    SimpleVar.set_model(self)

  # def get_available_ontologies(self) -> list[str]:                    # 2026.01.09 HAP removed for the time being
  #   return self._io_manager.get_context_member_valid_options(         # 2026.01.09 HAP removed for the time being
  #           io.IOContextMember.ONTOLOGY                               # 2026.01.09 HAP removed for the time being
  #           )                                                         # 2026.01.09 HAP removed for the time being

  def get_available_ontologies(self) -> list[str]:
    return old_io.get_available_ontologies()

  def load_ontology(self, ontology_name: str) -> None:
    self.ontology_name = ontology_name

    # TODO: Remove when this is done in the equation composer
    # io.generate_latex_images(ontology_name)

    # Loading data from files
    self.ontology = old_io.load_ontology_from_file(self.ontology_name)
    self.all_variables, _, self.all_equations = old_io.load_var_idx_eq_from_file(self.ontology_name)
    self.all_entities = old_io.load_entities_from_file(self.ontology_name, self.all_equations)
    self.all_entity_types = {}

    pass
    self._make_all_entity_types()

    self._update_interfaces()
    self._update_tree_model()

    # r = self.generate_entity_types_for_network(newtwork)

  def _update_interfaces(self) -> None:

    interface_entities = [
            ent for ent_name, ent in self.all_entities.items() if ent.is_interface_ent()
            ]
    interface_equations = {
            eq_id for eq_id, eq in self.all_equations.items() if eq.is_interface_eq()
            }

    for ent in interface_entities:
      main_eq_id = ent.get_equations()[0]

      # Delete the entity if there is not an interface equation
      if main_eq_id not in interface_equations:
        del self.all_entities[ent.entity_name]
        continue

      # TODO: Check for modification dates to see if the entity needs to be updated.
      update_needed = True
      if update_needed:
        new_ent = self.create_entity_from_eq(main_eq_id, ent)
        self.all_entities[ent.entity_name] = new_ent

      interface_equations.remove(main_eq_id)

    for eq_id in interface_equations:
      new_ent = self.create_entity_from_eq(eq_id)
      self.all_entities[new_ent.entity_name] = new_ent

  def _make_all_entity_types(self):
    inter_networks = [nw for nw in self.ontology.tree if self.ontology.tree[nw]["type"] == "inter"]
    for nw in inter_networks:
      self.all_entity_types[nw] = self.generate_entity_types_for_network(nw)

  # TODO -- not very handy if it crasches an incomplete file is generated
  # old_io.save_entities_to_file(self.ontology_name, self.all_entities)

  def create_entity_from_eq(
          self,
          eq_id: str,
          base_entity: entity.Entity | None = None,
          ) -> entity.Entity:
    eq = self.all_equations[eq_id]

    output_var_id = eq.get_main_var_id()
    for v in eq.get_incidence_list(output_var_id):  # RULE: assumes only o
      no = int(v.split("V_")[1])
      input_var_id = v
      if no > 99:  # up to 99 are reserved quantities TODO: globalise this value
        input_var_id = v
        break
    # input_var_id = v #eq.get_incidence_list(output_var_id)[0]  #TODO: select the one not being constant

    if base_entity is None:
      output_var_alias = self.all_variables[output_var_id].get_alias(
              "internal_code"
              )
      input_var_alias = self.all_variables[input_var_id].get_alias(
              "internal_code"
              )

      new_ent = entity.Entity(
              f"{eq.network} ({input_var_alias} -> {output_var_alias})",
              self.all_equations,
              )
    # elif ">>>" in base_entity.entity_name:                      # TODO: this blocks redoes the interfaces every time
    #   output_var_alias = self.all_variables[output_var_id].get_alias(
    #       "internal_code")
    #   input_var_alias = self.all_variables[input_var_id].get_alias(
    #       "internal_code")
    #   del self.all_entities[base_entity.entity_name]
    #   base_entity.entity_name  = f"{eq.network} ({input_var_alias} -> {output_var_alias})"
    #   new_ent = entity.Entity(
    #           f"{eq.network} ({input_var_alias} -> {output_var_alias})",
    #           self.all_equations,
    #   )

    else:
      new_ent = entity.Entity(
              base_entity.entity_name,
              self.all_equations,
              base_entity.index_set,
              )

    new_ent.set_input_var(input_var_id, True)
    new_ent.set_output_var(output_var_id, True)
    new_ent.generate_var_eq_forest({output_var_id: [eq_id]})
    new_ent.update_var_eq_tree()

    return new_ent

  def _load_entity_data(self, entity_obj):
    """Helper method to load data for an entity object."""
    try:
      print(f"Loading data for entity: {entity_obj.entity_name}")

      # Get all the data we want to display
      integrators = self.safe_get(entity_obj, 'get_integrators_eq', [])
      equations = self.safe_get(entity_obj, 'get_equations', [])
      input_vars = self.safe_get(entity_obj, 'get_input_vars', [])
      output_vars = self.safe_get(entity_obj, 'get_output_vars', [])
      init_vars = self.safe_get(entity_obj, 'get_init_vars', [])
      pending_vars = self.safe_get(entity_obj, 'get_pending_vars', [])

      print(f"Found data - Integrators: {len(integrators)}, Equations: {len(equations)}")
      print(f"Input vars: {len(input_vars)}, Output vars: {len(output_vars)}")
      print(f"Init vars: {len(init_vars)}, Pending vars: {len(pending_vars)}")

      # Update the UI with the entity's data
      self._update_entity_models([
              integrators,
              equations,
              input_vars,
              output_vars,
              init_vars,
              pending_vars
              ])

    except Exception as e:
      print(f"Error loading entity data: {e}")
      import traceback
      traceback.print_exc()
      self._update_entity_models([[], [], [], [], [], []])


  def load_entity(self, index: QtCore.QModelIndex) -> None:
    """Load an entity based on the selected index in the tree view."""
    print("\n" + "=" * 50)
    print("=== load_entity called ===")
    print(f"Index valid: {index.isValid()}")

    try:
      if not index.isValid():
        print("Invalid index in load_entity")
        self._update_entity_models([[], [], [], [], [], []])
        return

      # Get the display text of the selected item
      item = self.entity_tree_model.itemFromIndex(index)
      if item is None:
        print("Error: Could not get item from index")
        self._update_entity_models([[], [], [], [], []])
        return

      display_text = item.text()
      print(f"Display text: {display_text}")

      # Get entity ID from item data
      entity_id = item.data(QtCore.Qt.UserRole + 1)
      print(f"Entity ID from item data: {entity_id}")

      # Store the current entity ID
      self.current_entity_id = entity_id
      print(f"Set current_entity_id to: {entity_id}")

      # Verify the entity exists
      if entity_id in self.all_entities:
        print(f"Entity found in all_entities")
        entity_obj = self.all_entities[entity_id]
        self._load_entity_data(entity_obj)
      else:
        print(f"Entity ID {entity_id} not found in all_entities")
        print(f"Available entity IDs (first 5): {list(self.all_entities.keys())[:5]}")
        self._update_entity_models([[], [], [], [], [], []])

    except Exception as e:
      print(f"Error in load_entity: {e}")
      import traceback
      traceback.print_exc()
      self._update_entity_models([[], [], [], [], [], []])

  def safe_get(self, obj, method_name, default=None):
    """Safely get a value from an object's method."""
    if hasattr(obj, method_name):
      method = getattr(obj, method_name)
      if callable(method):
        try:
          result = method()
          return result if result is not None else default
        except Exception as e:
          print(f"Error in {method_name}: {e}")
          return default
    return default

  class SimpleVar:
    def __init__(self, var_id, model=None):
      self._id = var_id
      self._model = model
      self._equation = None
      self._variable = None

    def get_id(self):
      return self._id

    def get_img_path(self):
      # Return a default image path or implement your logic here
      return ":/icons/variable.png"

    def get_display_text(self):
      """Return a more detailed display text for the variable/equation."""
      # Try to get the equation or variable details if they exist in the model
      if self._model:
        if self._id in self._model.all_equations:
          self._equation = self._model.all_equations.get(self._id)
        if self._id in self._model.all_variables:
          self._variable = self._model.all_variables.get(self._id)

      if self._equation:
        return f"{self._id}: {self._equation.equation if hasattr(self._equation, 'equation') else 'No equation'}"
      elif self._variable:
        return f"{self._id}: {self._variable.value if hasattr(self._variable, 'value') else 'No value'}"
      return self._id

    print("=====================\n")

  def save(self) -> None:
    """
    Save the current state of the model.
    This is a placeholder that should be implemented according to your application's needs.
    """
    print("Save method called - implement saving logic here")
    # TODO: Implement actual saving logic
    # This could involve:
    # 1. Saving the current ontology state
    # 2. Persisting entity data
    # 3. Updating any necessary files
    pass

  def get_network_types_from_ontology(self):
    """
    Extract all network types from the ontology that are labeled as "inter".

    Returns:
        list: List of network type names that are marked as "inter"
    """
    if not hasattr(self, 'ontology') or not self.ontology:
      return ['macroscopic']  # Default fallback

    try:
      ontology_tree = self.ontology.tree
      return [
              net_name for net_name, net_data in ontology_tree.items()
              if isinstance(net_data, dict) and net_data.get('type') == 'inter'
              ]
    except Exception as e:
      print(f"Error getting network types: {e}")
      return ['macroscopic']  # Default fallback on error


  def generate_token_combinations(self, tokens):
    """Generate all possible non-empty combinations of tokens separated by underscores.
    
    Args:
        tokens: List of token strings to combine
        
    Returns:
        List of all possible combinations as strings
    """
    if not tokens:
      return []
    
    from itertools import combinations
    all_combinations = []
    # Generate combinations of all lengths from 1 to number of tokens
    for r in range(1, len(tokens) + 1):
      # Get all combinations of length r
      for combo in combinations(tokens, r):
        # Join tokens with underscore
        all_combinations.append('_'.join(combo))
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(all_combinations))

  def generate_entity_types_for_network(self, network_type):
    """
    Generate entity types for a specific network type, organized by node and arc categories.

    Args:
        network_type: The type of network to generate entity types for

    Returns:
        dict: Dictionary with 'node' and 'arc' keys, each containing a list of entity types
    """
    # Default empty result
    result = {'node': [], 'arc': []}

    # If no ontology is loaded, return empty result
    if not hasattr(self, 'ontology') or not self.ontology:
      return result

    try:
      # Get the network info from the ontology
      network_info = self.ontology.tree.get(network_type, {})
      structure = network_info.get('structure', {})

      # Process node types
      node_types = structure.get('node', {})
      dynamics = list(node_types.keys())
      natures = list(node_types.values())
      token_types = structure.get('token', {})

      all_tokens = list(token_types.keys())
      
      # Generate all token combinations
      token_combinations = self.generate_token_combinations(all_tokens)

      # Process node types with all token combinations
      for token_combo in token_combinations:
        # result['node'].append(token_combo)

        for dynamics, natures in node_types.items():
          for nature in natures:
            result['node'].append(f"{token_combo}|{dynamics}|{nature}")
          # if not natures:
          #   result['node'].append(f"{dynamics}|{nature}")
          #   continue
          #
          # for nature in natures:
          #   if not token_combinations:  # If no token combinations
          #     result['node'].append(f"{dynamics}|{nature}")
          #   else:
          #     # Add all token combinations to the node type
          #     for token_combo in token_combinations:
          #       result['node'].append(f"{dynamics}|{nature}|{token_combo}")

      # Process arc types
      arc_types = structure.get('arc', {})
      for arc_type, arc_mechs in arc_types.items():
        for mech, sub_mechs in arc_mechs.items():
          if not sub_mechs:  # If no sub-mechanisms
            result['arc'].append(f"{arc_type}|{mech}")
          else:
            for sub_mech in sub_mechs:
              result['arc'].append(f"{arc_type}|{mech}|{sub_mech}")

      # Remove duplicates and sort
      result['node'] = sorted(list(set(result['node'])))
      result['arc'] = sorted(list(set(result['arc'])))

      return result

    except Exception as e:
      print(f"Error generating entity types for {network_type}: {e}")
      return {'node': [], 'arc': []}
  def _update_entity_models(self, entity_data):
    """Update the entity list models with new data.

    Args:
        entity_data: A list of lists containing the data for each model.
                    The order should be:
                    [integrators, equations, input_vars, output_vars, init_vars, pending_vars]
    """
    model_names = ["Integrators", "Equations", "Input Vars", "Output Vars", "Init Vars", "Pending Vars"]

    # Validate inputs
    if not hasattr(self, 'entity_list_models') or len(self.entity_list_models) != len(model_names):
      return

    if not isinstance(entity_data, (list, tuple)) or len(entity_data) != len(model_names):
      return

    for model, data, name in zip(self.entity_list_models, entity_data, model_names):
      try:
        # Skip if model is missing required methods
        required_methods = ['load_data', 'clear']
        if not all(hasattr(model, m) for m in required_methods):
          continue

        # Skip if no data or invalid data type
        if data is None or not isinstance(data, (list, tuple)):
          model.clear()
          continue

        # Process items
        valid_data = []
        for item in data:
          if item is None:
            continue

          # Extract item ID
          item_id = None
          if hasattr(item, 'get_id') and callable(item.get_id):
            item_id = item.get_id()
          elif hasattr(item, 'id') and not callable(item.id):
            item_id = item.id
          elif hasattr(item, 'name') and not callable(item.name):
            item_id = item.name
          elif isinstance(item, str):
            item_id = item

          if item_id is not None:
            valid_data.append(SimpleVar(item_id, self))

        # Update the model
        model.clear()
        if valid_data:
          model.load_data(valid_data)

      except Exception as e:
        # Silently handle errors to prevent UI disruption
        model.clear()
        continue

  def _update_tree_model(self) -> None:
    """Update the tree model with the current state of entities."""
    self.entity_tree_model.clear()
    networks = set()

    # Add networks from both entities and generated types
    for entity_id in self.all_entities:
        parts = entity_id.split('.')
        if len(parts) >= 2:
            networks.add(parts[0])
    networks.update(self.all_entity_types.keys())

    for net in sorted(networks):
        net_item = QtGui.QStandardItem(net)
        self.entity_tree_model.appendRow(net_item)

        for category in ['node', 'arc']:
            cat_item = QtGui.QStandardItem(category)
            net_item.appendRow(cat_item)

            # Get all generated types for this network and category
            generated_types = set()
            if (net in self.all_entity_types and 
                category in self.all_entity_types[net]):
                generated_types = set(self.all_entity_types[net][category])

            # Create a dictionary to store type items
            type_items = {}

            # First, create items for all generated types
            for entity_type in sorted(generated_types):
                type_item = QtGui.QStandardItem(entity_type)
                type_item.setData(('entity_type', net, category, entity_type), QtCore.Qt.UserRole + 1)
                type_item.setData(entity_type, QtCore.Qt.UserRole + 2)
                cat_item.appendRow(type_item)
                type_items[entity_type] = type_item

            # Then add all entities under their types
            for entity_id, entity_obj in self.all_entities.items():
                if not entity_id.startswith(f"{net}.{category}."):
                    continue

                try:
                    parts = entity_id.split('.')
                    if len(parts) < 3:
                        continue

                    type_parts = parts[2].split('|')
                    if len(type_parts) < 3:
                        continue

                    # Reconstruct the entity type (token|dynamics|nature)
                    entity_type = '|'.join(type_parts[:3])
                    entity_name = parts[-1]
                    base_type = type_parts[0]

                    # Create display name
                    display_name = f"tokens:{base_type} name:{entity_name}"

                    # Create the item
                    item = QtGui.QStandardItem(display_name)
                    item.setData(entity_id, QtCore.Qt.UserRole + 1)
                    item.setData(entity_id, QtCore.Qt.UserRole + 2)
                    item.setData(entity_obj, QtCore.Qt.UserRole + 3)

                    # Ensure the type item exists
                    if entity_type not in type_items:
                        type_item = QtGui.QStandardItem(entity_type)
                        type_item.setData(('entity_type', net, category, entity_type), QtCore.Qt.UserRole + 1)
                        type_item.setData(entity_type, QtCore.Qt.UserRole + 2)
                        cat_item.appendRow(type_item)
                        type_items[entity_type] = type_item

                    # Add the entity to its type
                    type_items[entity_type].appendRow(item)

                except Exception as e:
                    print(f"Error processing entity {entity_id}: {e}")

    self.tree_changed.emit()


  def get_entity_editor_model(self, index: QtCore.QModelIndex = None) -> entity_editor.EntityEditorModel:
    """Get the entity editor model for the selected item."""
    print("\n" + "=" * 50)
    print("=== get_entity_editor_model called ===")

    try:
      # Get the current entity ID
      entity_id = getattr(self, 'current_entity_id', None)
      print(f"Current entity ID: {entity_id}")

      if not entity_id:
        print("Error: No current_entity_id set")
        raise ValueError("No entity is currently selected")

      # Verify the entity exists
      if entity_id not in self.all_entities:
        print(f"Error: Entity '{entity_id}' not found in all_entities")
        print(f"Available entities (first 5): {list(self.all_entities.keys())[:5]}")
        raise ValueError(f"Entity not found: {entity_id}")

      print(f"Creating editor model for entity: {entity_id}")
      entity_obj = self.all_entities[entity_id]
      print(f"Entity type: {type(entity_obj).__name__}")
      print(f"Entity attributes: {[attr for attr in dir(entity_obj) if not attr.startswith('__')]}")

      # Create and return the editor model
      editor_model = entity_editor.EntityEditorModel(
              copy.deepcopy(entity_obj),
              self.all_variables,
              self.all_equations,  # self.all_entities,
              )
      print("Successfully created editor model")
      return editor_model

    except Exception as e:
      print(f"Error in get_entity_editor_model: {e}")
      import traceback
      traceback.print_exc()
      raise


  def update_entity(self, index: QtCore.QModelIndex, updated_entity: entity.Entity) -> None:
    """Update an existing entity in the model."""
    print("\n" + "=" * 50)
    print("=== update_entity called ===")

    try:
      entity_id = getattr(self, 'current_entity_id', None)
      if not entity_id:
        print("Error: No current_entity_id set")
        raise ValueError("No entity is currently selected")

      print(f"Updating entity: {entity_id}")

      if entity_id not in self.all_entities:
        print(f"Error: Entity {entity_id} not found in model")
        print(f"Available entities (first 5): {list(self.all_entities.keys())[:5]}")
        raise ValueError(f"Entity {entity_id} not found in model")

      # Update the entity
      self.all_entities[entity_id] = updated_entity
      print(f"Successfully updated entity: {entity_id}")

      # Update the tree view
      print("Updating tree model...")
      self._update_tree_model()
      print("Tree model updated")

    except Exception as e:
      print(f"Error in update_entity: {e}")
      import traceback
      traceback.print_exc()
      raise

  def add_entity(
          self, new_entity_id: str, bases: list[str]
          ) -> None | EntityMergerModel:
    new_entity = None
    number_of_bases = len(bases)

    if number_of_bases == 1:
      new_entity = copy.deepcopy(self.all_entities[bases[0]])  # if an alternative is generated
    else:
      new_entity = entity.Entity(new_entity_id, self.all_equations)

    self.all_entities[new_entity_id] = new_entity
    self._update_tree_model()

    if number_of_bases > 1:
      base_entities = [self.all_entities[b] for b in bases]
      merge_completed = new_entity.start_merging_process(base_entities)
      if not merge_completed:
        return EntityMergerModel(
                new_entity, self.all_variables, self.all_equations
                )

    return None

  def update_entity(
          self, index: QtCore.QModelIndex, updated_entity: entity.Entity
          ) -> None:
    entity_id = self.entity_tree_model.path_from_index(index)
    if updated_entity != self.all_entities[entity_id]:
      self.all_entities[entity_id] = updated_entity
      self.load_entity(index)

  def is_a_leaf(self, index: QtCore.QModelIndex) -> None:
    return self.entity_tree_model.get_depth(index) == tree.LEAF_DEPTH
      
  def delete_entity(self, index: QtCore.QModelIndex) -> None:
    """Delete an entity from the model.
    
    Args:
        index: The model index of the entity to delete
    """
    print("\n" + "=" * 50)
    print("=== delete_entity called ===")
    
    try:
      # Get the entity ID from the current selection
      entity_id = getattr(self, 'current_entity_id', None)
      if not entity_id:
        print("Error: No entity is currently selected")
        return

      print(f"Deleting entity: {entity_id}")

      # Check if entity exists
      if entity_id not in self.all_entities:
        print(f"Error: Entity {entity_id} not found in model")
        return

      # Delete the entity
      del self.all_entities[entity_id]
      print(f"Successfully deleted entity: {entity_id}")

      # Clear current entity ID
      self.current_entity_id = None

      # Update the tree view
      print("Updating tree model...")
      self._update_tree_model()
      print("Tree model updated")

      # Clear the entity views
      self._update_entity_models([[], [], [], [], [], []])

    except Exception as e:
      print(f"Error in delete_entity: {e}")
      import traceback
      traceback.print_exc()

  def save(self) -> None:
    old_io.save_entities_to_file(self.ontology_name, self.all_entities)
    # TODO: Maybe merge all in this function
    self.save_arc_options()

  def save_arc_options(self) -> None:
    arc_entities = []
    node_entities = []
    interface_entities = []
    for ent_name, ent in self.all_entities.items():
      ent_type = ent.get_type()
      if ent_type == "interface":
        interface_entities.append(ent_name)
      elif ent_type == "arc":
        arc_entities.append(ent_name)
      elif ent_type == "node":
        node_entities.append(ent_name)
      else:
        # TODO: Replace for proper logs.
        print("ERROR: Unknown entity type.")

    arc_options = {}
    for arc_ent_name in arc_entities:
      arc_options[arc_ent_name] = {
              "sources": [],
              "sinks"  : [],
              }
      arc_network = self.all_entities[arc_ent_name].get_network()[0]
      # Only one token per arc
      arc_token = self.all_entities[arc_ent_name].get_tokens()[0]
      for node_ent_name in node_entities:
        if self.all_entities[node_ent_name].get_network()[0] != arc_network:
          continue
        if arc_token not in self.all_entities[node_ent_name].get_tokens():
          continue

        # TODO: Add conditions for variables

        arc_options[arc_ent_name]["sources"].append(node_ent_name)
        arc_options[arc_ent_name]["sinks"].append(node_ent_name)

    for interface_ent_name in interface_entities:
      arc_options[interface_ent_name] = {
              "sources": [],
              "sinks"  : [],
              }
      interface_ent = self.all_entities[interface_ent_name]
      interface_networks = interface_ent.get_network()
      interface_input_var = interface_ent.get_input_vars()[0]
      interface_output_var = interface_ent.get_output_vars()[0]

      # if ("control" in interface_ent_name) and ("macroscopic" in interface_ent_name):
      #   print("debugging 1 -- found control", current_ent.entity_name)

      for ent_name in node_entities + arc_entities:
        current_ent = self.all_entities[ent_name]
        if (
                current_ent.get_network()[0] == interface_networks[0]
                and interface_input_var in current_ent.get_output_vars()
        ):
          arc_options[interface_ent_name]["sources"].append(ent_name)
          print(">> added source")

        if (
                current_ent.get_network()[0] == interface_networks[1]
                and interface_output_var in current_ent.get_input_vars()
        ):
          arc_options[interface_ent_name]["sinks"].append(ent_name)
          print(">>> added sink")

        if (
                "control >>> macroscopic" in interface_ent_name
        ):  # and ("macroscopic" in interface_ent_name):
          print(
                  "debugging -- found ",
                  interface_ent_name,
                  current_ent.entity_name,
                  )
          if (
                  "macroscopic" in ent_name
          ):  # == "macroscopic.node.mass|dynamic|lumped.dynamicReactiveLump":
            print(
                    "debugging 3",
                    "\n interface_input:",
                    interface_input_var,
                    "\n interface_output_var",
                    interface_output_var,
                    "\n current_ent.get_input_vars",
                    current_ent.get_input_vars(),
                    "\n current_ent.get_output_vars",
                    current_ent.get_output_vars(),
                    "\n arc_options[interface_ent_name][sources]",
                    arc_options[interface_ent_name]["sources"],
                    "\n arc_options[interface_ent_name][sinks]",
                    arc_options[interface_ent_name]["sinks"],
                    )

            pass

    old_io.save_arc_options_to_file(self.ontology_name, arc_options)
