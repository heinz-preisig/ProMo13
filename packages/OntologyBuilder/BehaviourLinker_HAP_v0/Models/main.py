import copy

from PyQt5 import QtCore

from Common.classes import entity
from Common.classes import equation
from Common.classes import io as old_io
from Common.classes import variable
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import entity_editor
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import entity_generator
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import image_list
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import tree
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_merger import EntityMergerModel


# from common import io  # 2026.01.09 HAP removed for the time being


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

    self._update_interfaces()
    self._update_tree_model()

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
      if no > 99: # up to 99 are reserved quantities TODO: globalise this value
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

  def load_entity(self, index: QtCore.QModelIndex) -> None:
    if not index.isValid():
      entity_data = [[]] * 6
      self._update_entity_models(entity_data)
      return

    entity_id = self.entity_tree_model.path_from_index(index)

    current_entity = self.all_entities.get(entity_id)
    if current_entity is None:
      # TODO: Maybe make an exception here
      return False

    entity_data = [
            [
                    self.all_equations[eq_id]
                    for eq_id in current_entity.get_integrators_eq()
                    ],
            [self.all_equations[eq_id] for eq_id in current_entity.get_equations()],
            [self.all_variables[var_id] for var_id in current_entity.get_input_vars()],
            [self.all_variables[var_id] for var_id in current_entity.get_output_vars()],
            [self.all_variables[var_id] for var_id in current_entity.get_init_vars()],
            [
                    self.all_variables[var_id]
                    for var_id in current_entity.get_pending_vars()
                    ],
            ]
    self._update_entity_models(entity_data)

  def _update_entity_models(
          self, entity_data: list[list[equation.Equation | variable.Variable]]
          ) -> None:
    for model, data in zip(self.entity_list_models, entity_data, strict=False):
      model.load_data(data)

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

  def generate_entity_types_for_network(self, network_type):
    """
    Generate entity types for a specific network type, organized by node and arc categories.

    Args:
        network_type: The type of network to generate entity types for

    Returns:
        dict: Dictionary with 'node' and 'arc' keys, each containing a list of entity types
    """
    if not hasattr(self, 'ontology') or not self.ontology:
      # Default types if no ontology is loaded
      if network_type == 'macroscopic':
        return {
                'node': [
                        'constant|infinity|charge',
                        'constant|infinity|energy',
                        'constant|infinity|mass',
                        'dynamic|lumped|charge',
                        'dynamic|lumped|energy',
                        'dynamic|lumped|mass',
                        'dynamic|ODE|signal',
                        'event|distributed|charge',
                        'event|distributed|energy',
                        'event|distributed|mass',
                        'event|lumped|charge',
                        'event|lumped|energy',
                        'event|lumped|mass'
                        ],
                'arc' : []  # Default empty arc types
                }
      return {'node': [], 'arc': []}

    try:
      network_info = self.ontology.tree.get(network_type, {})
      structure = network_info.get('structure', {})

      result = {'node': [], 'arc': []}

      # Process node types
      node_types = structure.get('node', {})
      token_types = structure.get('token', {})

      for node_type, mechanisms in node_types.items():
        if not mechanisms:
          result['node'].append(node_type)
          continue

        for mechanism in mechanisms:
          if not token_types:  # If no specific tokens
            result['node'].append(f"{node_type}|{mechanism}")
          else:
            for token in token_types:
              result['node'].append(f"{node_type}|{mechanism}|{token}")

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

  def _update_tree_model(self) -> None:
    # Debug: Print all loaded entities
    print("\n=== Loaded Entities ===")
    for entity_id, entity_obj in self.all_entities.items():
      print(f"Entity ID: {entity_id}, Type: {type(entity_obj)}")
      if hasattr(entity_obj, 'entity_name'):
        print(f"  - Name: {entity_obj.entity_name}")
      if hasattr(entity_obj, 'get_type'):
        print(f"  - Type: {entity_obj.get_type()}")
      if hasattr(entity_obj, 'get_tokens'):
        print(f"  - Tokens: {entity_obj.get_tokens()}")
      print("---")

    # Get network types from ontology
    network_types = self.get_network_types_from_ontology()
    print(f"\nNetwork types from ontology: {network_types}")

    # Generate entity types for each network, organized by node/arc
    network_base_types = {
            net_type: self.generate_entity_types_for_network(net_type)
            for net_type in network_types
            }

    # Default base types for unknown network types
    default_base_types = {
            'node': ['unknown|node|type'],
            'arc' : ['unknown|arc|type']
            }

    # Get all internetworks from existing entities and separate interfaces
    internetworks = {}
    interface_entities = {}

    for entity_id, entity_obj in self.all_entities.items():
      if '>>>' in entity_id:
        # This is an interface entity
        interface_parts = entity_id.split('>>>')
        source_network = interface_parts[0].split('.')[0].strip()
        interface_entities.setdefault(source_network, []).append(entity_id)
      else:
        # This is a regular entity
        # Format: macroscopic.node.mass|constant|infinity.massSource
        parts = entity_id.split('.')
        if len(parts) >= 3:  # Should have at least network, category, and entity parts
          net = parts[0]
          category = parts[1]  # 'node' or 'arc'
          base_type = '|'.join(parts[2].split('|')[:3])  # Get the first three parts of the type
          entity_name = parts[-1]  # The last part is the entity name

          # Determine network type
          net_type = network_types[0] if network_types else 'unknown'
          for ntype in network_types:
            if net.lower() == ntype.lower():
              net_type = ntype
              break

          if net not in internetworks:
            internetworks[net] = {'type': net_type, 'entities': {}}

          # Store entity data
          entity_data = {
                  'id'    : entity_id,
                  'name'  : entity_name,
                  'type'  : base_type,
                  'object': entity_obj
                  }
          internetworks[net]['entities'].setdefault(category, {}).setdefault(base_type, []).append(entity_data)

    # If no entities exist yet, add a default network
    if not internetworks and not interface_entities:
      default_net = network_types[0] if network_types else 'default'
      internetworks = {default_net: {'type': default_net, 'entities': {}}}

    # Create a list of all possible entity paths
    all_entity_paths = []

    # Add networks and their entities
    for net, net_data in internetworks.items():
      net_type = net_data['type']
      base_types = network_base_types.get(net_type, default_base_types)

      # Add the network itself
      all_entity_paths.append(net)

      # Process nodes and arcs separately
      for category in ['node', 'arc']:
        category_path = f"{net}.{category}"
        all_entity_paths.append(category_path)

        # Get the base types for this category
        category_base_types = base_types.get(category, [])

        # Add each base type under its category
        for base_type in category_base_types:
          type_path = f"{category_path}.{base_type}"
          all_entity_paths.append(type_path)

          # Add entities of this type
          for entity_data in net_data['entities'].get(category, {}).get(base_type, []):
            # For nodes, we need to ensure the path is in the correct format
            entity_id = entity_data['id']

            if category == 'node':
              # The entity_id should be in the format: net.node.base_type.entity_name
              parts = entity_id.split('.')
              if len(parts) >= 4:  # net.node.base_type.entity_name
                # Reconstruct the path to ensure it's in the correct format
                entity_path = f"{net}.node.{base_type}.{parts[-1]}"
                all_entity_paths.append(entity_path)

                # Add sub-entities if they exist
                if hasattr(entity_data['object'], 'sub_entities'):
                  for sub_entity in entity_data['object'].sub_entities:
                    sub_entity_name = sub_entity.split('.')[-1]
                    all_entity_paths.append(f"{entity_path}.{sub_entity_name}")
            else:
              # For arcs, use the entity ID as is
              all_entity_paths.append(entity_id)

              # Add sub-entities if they exist
              if hasattr(entity_data['object'], 'sub_entities'):
                for sub_entity in entity_data['object'].sub_entities:
                  sub_entity_name = sub_entity.split('.')[-1]
                  all_entity_paths.append(f"{entity_id}.{sub_entity_name}")

    # Add interface entities
    for source_net, interfaces in interface_entities.items():
      # Add the network if it's not already added
      if source_net not in internetworks:
        all_entity_paths.append(source_net)

      # Add interfaces node
      interfaces_path = f"{source_net}.interfaces"
      all_entity_paths.append(interfaces_path)

      # Add each interface entity
      for interface_id in interfaces:
        # Get the interface name (part after the last dot)
        interface_name = interface_id.split('.')[-1]
        all_entity_paths.append(f"{interfaces_path}.{interface_name}")

    # Debug: Print the paths that will be added to the tree
    print("\nAll entity paths to be added to the tree:")
    for path in all_entity_paths:
      print(f"- {path}")

    # Load the data into the tree model
    self.entity_tree_model.load_data(all_entity_paths)
    self.tree_changed.emit()

  def get_entity_editor_model(
          self, index: QtCore.QModelIndex
          ) -> entity_editor.EntityEditorModel:
    entity_id = self.entity_tree_model.path_from_index(index)
    return entity_editor.EntityEditorModel(
            copy.deepcopy(self.all_entities[entity_id]),
            self.all_variables,
            self.all_equations,
            )

  def add_entity(
          self, new_entity_id: str, bases: list[str]
          ) -> None | EntityMergerModel:
    new_entity = None
    number_of_bases = len(bases)

    if number_of_bases == 1:
      new_entity = copy.deepcopy(self.all_entities[bases[0]])   # if an alternative is generated
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

  def delete_entity(self, index: QtCore.QModelIndex) -> None:
    entity_id = self.entity_tree_model.path_from_index(index)
    del self.all_entities[entity_id]
    # self.entity_tree_model.remove_element(index)
    self._update_tree_model()
    self.load_entity(QtCore.QModelIndex())

  def is_a_leaf(self, index: QtCore.QModelIndex) -> None:
    return self.entity_tree_model.get_depth(index) == tree.LEAF_DEPTH

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
