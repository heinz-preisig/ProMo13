import copy
from typing import Optional

from PyQt5 import QtCore

from packages.Common.classes import entity
from packages.Common.classes import io
from packages.OntologyBuilder.BehaviourLinker.Models import entity_editor
from packages.OntologyBuilder.BehaviourLinker.Models import entity_generator
from packages.OntologyBuilder.BehaviourLinker.Models import image_list
from packages.OntologyBuilder.BehaviourLinker.Models import tree
from packages.OntologyBuilder.BehaviourLinker.Models.entity_merger import EntityMergerModel


class MainModel(QtCore.QObject):
  # Signals
  tree_changed = QtCore.pyqtSignal()

  # Methods
  def __init__(self):
    super().__init__()
    self.ontology_name = None
    self.ontology = None
    self.all_entities = None
    self.all_variables = None
    self.all_equations = None

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

  def load_ontology(self, ontology_name):
    self.ontology_name = ontology_name

    # TODO: Remove when this is done in the equation composer
    # io.generate_latex_images(ontology_name)

    # Loading data from files
    self.ontology = io.load_ontology_from_file(self.ontology_name)
    self.all_variables, _, self.all_equations = io.load_var_idx_eq_from_file(
        self.ontology_name
    )
    self.all_entities = io.load_entities_from_file(
        self.ontology_name,
        self.all_equations
    )

    self._update_interfaces()

    self._update_tree_model()

  def _update_interfaces(self):
    interface_entities = [
        ent
        for ent_name, ent in self.all_entities.items()
        if ent.is_interface_ent()
    ]
    interface_equations = {
        eq_id
        for eq_id, eq in self.all_equations.items()
        if eq.is_interface_eq()
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

    io.save_entities_to_file(self.ontology_name, self.all_entities)

  def create_entity_from_eq(
      self,
      eq_id: str,
      base_entity: Optional[entity.Entity] = None,
  ) -> entity.Entity:

    eq = self.all_equations[eq_id]

    output_var_id = eq.get_main_var_id()
    for v in eq.get_incidence_list(output_var_id):  # RULE: assumes only o
      no = int(v.split("V_")[1])
      input_var_id = v
      if no > 99:
        input_var_id = v
        break
    #input_var_id = v #eq.get_incidence_list(output_var_id)[0]  #TODO: select the one not being constant

    if base_entity is None:
      output_var_alias = self.all_variables[output_var_id].get_alias(
          "internal_code")
      input_var_alias = self.all_variables[input_var_id].get_alias(
          "internal_code")

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

  def load_entity(self, index: QtCore.QModelIndex):
    if not index.isValid():
      entity_data = [[]]*6
      self._update_entity_models(entity_data)
      return

    entity_id = self.entity_tree_model.path_from_index(index)

    current_entity = self.all_entities.get(entity_id)
    if current_entity is None:
      # TODO: Maybe make an exception here
      return False

    entity_data = [
        [self.all_equations[eq_id]
         for eq_id in current_entity.get_integrators_eq()],
        [self.all_equations[eq_id]
         for eq_id in current_entity.get_equations()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_input_vars()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_output_vars()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_init_vars()],
        [self.all_variables[var_id]
         for var_id in current_entity.get_pending_vars()],
    ]
    self._update_entity_models(entity_data)

  def _update_entity_models(self, entity_data):
    for model, data in zip(self.entity_list_models, entity_data):
      model.load_data(data)

  def _update_tree_model(self):
    self.entity_tree_model.load_data(self.all_entities.keys())
    self.tree_changed.emit()

  def get_entity_generator_model(self):
    return entity_generator.EntityGeneratorModel(
        self.ontology,
        list(self.all_entities.keys())
    )

  def get_entity_editor_model(self, index):
    entity_id = self.entity_tree_model.path_from_index(index)
    return entity_editor.EntityEditorModel(
        copy.deepcopy(self.all_entities[entity_id]),
        self.all_variables,
        self.all_equations,
    )

  def add_entity(self, new_entity_id, bases):
    new_entity = None
    number_of_bases = len(bases)

    if number_of_bases == 1:
      new_entity = copy.deepcopy(self.all_entities[bases[0]])
    else:
      new_entity = entity.Entity(new_entity_id, self.all_equations)

    self.all_entities[new_entity_id] = new_entity
    self._update_tree_model()

    if number_of_bases > 1:
      base_entities = [self.all_entities[b] for b in bases]
      merge_completed = new_entity.start_merging_process(base_entities)
      if not merge_completed:
        return EntityMergerModel(new_entity, self.all_variables, self.all_equations)

    return None

  def update_entity(self, index, updated_entity):
    entity_id = self.entity_tree_model.path_from_index(index)
    if updated_entity != self.all_entities[entity_id]:
      self.all_entities[entity_id] = updated_entity
      self.load_entity(index)

  def delete_entity(self, index):
    entity_id = self.entity_tree_model.path_from_index(index)
    del self.all_entities[entity_id]
    # self.entity_tree_model.remove_element(index)
    self._update_tree_model()
    self.load_entity(QtCore.QModelIndex())

  def is_a_leaf(self, index):
    return self.entity_tree_model.get_depth(index) == tree.LEAF_DEPTH

  def save(self):
    io.save_entities_to_file(self.ontology_name, self.all_entities)
    # TODO: Maybe merge all in this function
    self.save_arc_options()

  def save_arc_options(self):
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
          "sinks": [],
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
          "sinks": [],
      }
      interface_ent = self.all_entities[interface_ent_name]
      interface_networks = interface_ent.get_network()
      interface_input_var = interface_ent.get_input_vars()[0]
      interface_output_var = interface_ent.get_output_vars()[0]

      # if ("control" in interface_ent_name) and ("macroscopic" in interface_ent_name):
      #   print("debugging 1 -- found control", current_ent.entity_name)

      for ent_name in node_entities + arc_entities:
        current_ent = self.all_entities[ent_name]
        if (current_ent.get_network()[0] == interface_networks[0] and
                interface_input_var in current_ent.get_output_vars()):
          arc_options[interface_ent_name]["sources"].append(ent_name)
          print(">> added source")

        if (current_ent.get_network()[0] == interface_networks[1] and
                interface_output_var in current_ent.get_input_vars()):
          arc_options[interface_ent_name]["sinks"].append(ent_name)
          print(">>> added sink")

        if ("control >>> macroscopic" in interface_ent_name): # and ("macroscopic" in interface_ent_name):
          print("debugging -- found ", interface_ent_name, current_ent.entity_name)
          if "macroscopic" in ent_name : # == "macroscopic.node.mass|dynamic|lumped.dynamicReactiveLump":
            print("debugging 3",
                  "\n interface_input:", interface_input_var,
                  "\n interface_output_var", interface_output_var,
                  "\n current_ent.get_input_vars", current_ent.get_input_vars(),
                  "\n current_ent.get_output_vars", current_ent.get_output_vars(),
                  "\n arc_options[interface_ent_name][sources]", arc_options[interface_ent_name]["sources"],
                  "\n arc_options[interface_ent_name][sinks]", arc_options[interface_ent_name]["sinks"],
                  )

            pass

    io.save_arc_options_to_file(self.ontology_name, arc_options)
