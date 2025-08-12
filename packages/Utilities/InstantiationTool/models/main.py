from typing import cast

from PyQt5 import QtCore

from packages.Common.classes import entity, io
from packages.Utilities.InstantiationTool.models import topology_tree
from src.common import old_io, old_topology, roles
from src.common.components import image_list
from src.common.constants import FixedVariables

# TODO: The information about the selection needs to be stored in the main_model,
# there is no way to retrieve it afterwards without talking to the view


class InvalidEntityError(Exception):
    """The entity doesn't exist"""

    pass


class MainModel(QtCore.QObject):
    # Signals
    variable_tree_changed = QtCore.pyqtSignal()
    topology_tree_changed = QtCore.pyqtSignal()
    selection_changed = QtCore.pyqtSignal(bool)
    # Add this new signal
    update_instantiate_field = QtCore.pyqtSignal(str)  # Signal to update the line edit


    # Methods
    def __init__(self) -> None:
        super().__init__()

        self._io_handler = old_io.IOHandler()

        self._ontology_name = ""
        self._model_name = ""
        self._all_entities = {}
        self._all_variables = {}
        self._all_equations = {}  # TODO: Check if I really need to store this
        self._all_indices = {}
        self._all_topology_objects = {}
        self._instantiation = {}

        self._required_variables = []
        self._optional_variables = []

        # Possible typed tokens for each variable in the model.
        self._typed_tokens_per_variable = {}

        # self.variable_tree_model = variable_tree.VariableTreeModel()
        self.variable_list = image_list.ImageListModel()
        self.topology_tree_model = topology_tree.TopologyTreeModel()

        # The selection state is store in these variables.
        self._is_variable_selected = False
        self._is_topology_object_selected = False

        self._variable_filter_string = None
        self._variable_show_uninstantiated_only = False

    def get_available_ontologies(self) -> list[str]:
        return io.get_available_ontologies()

    def get_available_models(self, ontology_name: str) -> list[str]:
        return io.get_available_models(ontology_name)

    def load_ontology_info(self, ontology_name: str, model_name: str) -> None:
        self._ontology_name = ontology_name
        self._model_name = model_name

        params = {"ontology_name": ontology_name, "model_name": model_name}
        self._io_handler.add_path_parameters(params)

        var_idx_eq = io.load_var_idx_eq_from_file(self._ontology_name)
        self._all_variables, self._all_indices, self._all_equations = var_idx_eq

        self._all_entities = io.load_entities_from_file(
            self._ontology_name, self._all_equations
        )
        self._all_topology_objects = io.load_topology_objects(
            self._ontology_name,
            self._model_name,
            self._all_entities,
        )

        self._instantiation = self._io_handler.get_instantiation_data()
        self._generate_topology_instantiation()

        self._discover_required_variables()
        self._update_variable_tree_model()

        # if self._required_variables:
        #   self._update_topology_tree_model(self._required_variables[0])

    def _generate_topology_instantiation(self) -> None:
        connections: list[tuple[str, str]] = []
        for top_obj in self._all_topology_objects.values():
            if isinstance(top_obj, old_topology.NodeComposite):
                continue

            top_obj = cast(old_topology.EntityContainer, top_obj)

            for connect_obj_id in top_obj.outgoing_connections:
                connections.append((top_obj.identifier, connect_obj_id))

        self._instantiation[FixedVariables.INCIDENCE_MATRIX] = {}
        self._instantiation[FixedVariables.INCIDENCE_MATRIX_NA_SOURCE] = {}
        self._instantiation[FixedVariables.INCIDENCE_MATRIX_NA_SINK] = {}
        self._instantiation[FixedVariables.INCIDENCE_MATRIX_NI_SOURCE] = {}
        self._instantiation[FixedVariables.INCIDENCE_MATRIX_NI_SINK] = {}
        self._instantiation[FixedVariables.INCIDENCE_MATRIX_AI_SOURCE] = {}
        self._instantiation[FixedVariables.INCIDENCE_MATRIX_AI_SINK] = {}

        for source, sink in connections:
            if source.startswith("N"):
                if sink.startswith("A"):
                    tuple_key = (source, sink)

                    update_dict = self._instantiation[FixedVariables.INCIDENCE_MATRIX]
                    update_dict[tuple_key] = "-1"

                    update_dict = self._instantiation[
                        FixedVariables.INCIDENCE_MATRIX_NA_SOURCE
                    ]
                    update_dict[tuple_key] = "1"
                elif sink.startswith("I"):
                    tuple_key = (source, sink)
                    update_dict = self._instantiation[
                        FixedVariables.INCIDENCE_MATRIX_NI_SOURCE
                    ]
                    update_dict[tuple_key] = "1"
            elif source.startswith("A"):
                if sink.startswith("N"):
                    tuple_key = (sink, source)

                    update_dict = self._instantiation[FixedVariables.INCIDENCE_MATRIX]
                    update_dict[tuple_key] = "1"

                    update_dict = self._instantiation[
                        FixedVariables.INCIDENCE_MATRIX_NA_SINK
                    ]
                    update_dict[tuple_key] = "1"
                else:
                    tuple_key = (source, sink)
                    update_dict = self._instantiation[
                        FixedVariables.INCIDENCE_MATRIX_AI_SOURCE
                    ]
                    update_dict[tuple_key] = "1"
            else:
                if sink.startswith("N"):
                    tuple_key = (sink, source)
                    update_dict = self._instantiation[
                        FixedVariables.INCIDENCE_MATRIX_NI_SINK
                    ]
                    update_dict[tuple_key] = "1"
                else:
                    tuple_key = (sink, source)
                    update_dict = self._instantiation[
                        FixedVariables.INCIDENCE_MATRIX_AI_SINK
                    ]
                    update_dict[tuple_key] = "1"

    def _discover_required_variables(self) -> None:
        used_entities: dict[str, entity.Entity] = {}
        for top_obj in self._all_topology_objects.values():
            # Composite nodes dont have an associated entity
            if isinstance(top_obj, old_topology.NodeComposite):
                continue

            top_obj = cast(old_topology.EntityContainer, top_obj)

            ent_name = top_obj.get_entity_name()
            # TODO: Move this and the test case to io.load_model
            if ent_name not in self._all_entities:
                raise InvalidEntityError

            self._find_typed_tokens_per_variable(top_obj, self._all_entities[ent_name])

            used_entities.setdefault(ent_name, self._all_entities[ent_name])

        required_variables = set()
        for ent in used_entities.values():
            required_variables.update(ent.get_init_vars())

        self._required_variables = sorted(required_variables)

    def _find_typed_tokens_per_variable(
        self, top_obj: old_topology.EntityContainer, ent: entity.Entity
    ) -> None:
        for var_id in ent.get_variables():
            # TODO: Extend to the other typed tokens
            if var_id not in self._typed_tokens_per_variable:
                self._typed_tokens_per_variable[var_id] = set()

            if (
                "I_4" in self._all_variables[var_id].index_structures
            ):  # TODO: there should be a dictionary label --> ID
                self._typed_tokens_per_variable[var_id].update(
                    set(top_obj.typed_tokens["mass"])
                )

    def _update_variable_tree_model(self) -> None:
        """Loads the necessary data into the model

        The list of variables is filtered and the result is loaded into the
        model. At the end a signal is emited to notify that the data in the
        model changed.
        """
        # filtered_variables = {
        #     var_id: self._all_variables[var_id]
        #     for var_id in self._filter_variables()
        # }

        # self.variable_tree_model.load_data(
        #     filtered_variables,
        #     self._typed_tokens_per_variable
        # )
        # self.variable_tree_changed.emit()
        ids = [self._all_variables[var].var_id for var in self._required_variables]
        paths = self._io_handler.get_imgs_paths(ids)
        self.variable_list.load_data(ids, paths)

    def _filter_variables(self) -> list[str]:
        # TODO: Implement this
        filtered_list = self._required_variables
        return filtered_list

    def on_variables_selected(self, index: QtCore.QModelIndex) -> None:
        """Updates the checked status of the variable_tree_model.

        It also triggers an update on the topology_tree_model.
         See :meth:`_update_topology_tree_model`.

        Args:
            index (QtCore.QModelIndex): Index that triggers the update.
        """
        # self.variable_tree_model.handle_check_state_change(index)

        # selected_variables = self.variable_tree_model.get_checked_items()
        # self._update_topology_tree_model(selected_variables)

        selected_variable = index.data(roles.ID_ROLE)
        self._update_topology_tree_model({selected_variable: []})

        self._check_selection_status()

    def on_topology_tree_model_check_box_changed(self) -> None:
        self._check_selection_status()

    # def _check_selection_status(self) -> None:
    #     # bool(self.variable_tree_model.get_checked_items())
    #     is_variable_selected = True
    #     is_topology_object_selected = bool(self.topology_tree_model.get_checked_items())
    #
    #     is_selection_complete = is_variable_selected and is_topology_object_selected
    #
    #     self.selection_changed.emit(is_selection_complete)    #todo: is it here that the values must be entered into the line editor?
    def _check_selection_status(self) -> None:
      is_variable_selected = True
      selected_topology_objects = self.topology_tree_model.get_checked_items()
      is_topology_object_selected = bool(selected_topology_objects)
      is_selection_complete = is_variable_selected and is_topology_object_selected

      # If we have a complete selection, try to find an existing value
      if is_selection_complete and hasattr(self, '_view'):
        # Get the current variable index from the view
        current_index = self._view.ui.tree_required_variables.currentIndex()
        if current_index.isValid():
          var_item = self.variable_list.itemFromIndex(current_index)
          if var_item:  # Make sure we got a valid item
            var_id = var_item.data(roles.ID_ROLE)

            # For simplicity, let's just use the first selected topology object
            if selected_topology_objects and var_id in self._instantiation:
              top_obj_id = selected_topology_objects[0]

              # Try to find a matching key in the instantiation
              for key, value in self._instantiation[var_id].items():
                # Check if this key matches our topology object
                if str(top_obj_id) in key or (len(key) == 1 and key[0] == "1"):
                  self.update_instantiate_field.emit(str(value))
                  break
              else:
                # No matching value found, clear the line edit
                self.update_instantiate_field.emit("")
            else:
              # No instantiation for this variable, clear the field
              self.update_instantiate_field.emit("")
          else:
            # No valid variable item, clear the field
            self.update_instantiate_field.emit("")
        else:
          # No valid variable selected, clear the field
          self.update_instantiate_field.emit("")
      else:
        # Selection not complete, clear the field
        self.update_instantiate_field.emit("")

      self.selection_changed.emit(is_selection_complete)

    def instantiate(self, instantiation_value: str, var_index: QtCore.QModelIndex) -> None:
      # ... existing code ...

      # After updating the instantiation, emit the signal to update the UI
      self.update_instantiate_field.emit(instantiation_value)

    def _update_topology_tree_model(
        self,
        variables_selected: dict[str, list[str]],
    ) -> None:
        """Updates the topology tree model.

        The model is updated and only topology objects that contain at least
        one of the variables in the variable list passed as argument are
        added. If the variable have any typed tokens selected, the topology
        objects also need to have at least one of the typed tokens to be
        included.

        The filtering is done in :meth:`_filter_topology_objects`.

        Args:
            var_list (Dict[str,List[str]]): Variables used for filtering.
        """
        filtered_ids = self._filter_topology_objects(variables_selected)

        self.topology_tree_model.load_data(self._all_topology_objects, filtered_ids)
        self.topology_tree_changed.emit()

    def _filter_topology_objects(
        self,
        variables_selected: dict[str, list[str]],
    ) -> list[str]:
        """Filters all_topology_objects

        The filtering is done at several levels. The main one uses a dict of
        variables and typed tokens to get only the topology objects that
        contain at least one of the variables with at least one of its typed
        tokens.

        Args:
            var_list (Dict[str, List[str]]): The keys are the variable ids.
             The valus are the corresponding typed tokens.

        Returns:
            List[str]: Ids of the Topology Objects that pass the filter.
        """
        # TODO: Add filtering for checkbox and searchbar
        filtered_topology_objects = set()
        for var_id, typed_tokens in variables_selected.items():
            for top_obj_id, top_obj in self._all_topology_objects.items():
                if isinstance(top_obj, old_topology.NodeComposite):
                    continue

                top_obj = cast(old_topology.EntityContainer, top_obj)

                # If there are types tokens the topology object needs to contain
                # at least one of them
                if typed_tokens:
                    typed_token_condition = bool(
                        set(typed_tokens) & set(top_obj.typed_tokens["mass"])
                    )
                else:
                    typed_token_condition = True

                # Main filter: contains variable + typed token
                if top_obj.contains_init_var(var_id) and typed_token_condition:
                    filtered_topology_objects.add(top_obj_id)

        return sorted(filtered_topology_objects)

    def instantiate(
        self, instantiation_value: str, var_index: QtCore.QModelIndex
    ) -> None:
        instantiated_top_obj = self.topology_tree_model.get_checked_items()
        var_item = self.variable_list.itemFromIndex(var_index)
        var_id = var_item.data(roles.ID_ROLE)

        if var_id not in self._instantiation:
            self._instantiation[var_id] = {}

        for top_obj_id in instantiated_top_obj:
            typed_tokens = []
            key_list = []
            index_structures = self._all_variables[var_id].index_structures
            if "I_1" in index_structures or "I_2" in index_structures:
                key_list.append(top_obj_id)

            typed_tokens = []
            if "I_4" in index_structures:
                typed_tokens = self._all_topology_objects[top_obj_id].typed_tokens[
                    "mass"
                ]

            if not typed_tokens and not key_list:
                id_key = ("1",)
                self._instantiation[var_id][id_key] = instantiation_value
                continue

            if typed_tokens:
                for tt in typed_tokens:
                    id_list = []
                    id_list.extend(key_list)
                    id_list.append(tt)
                    id_key = tuple(id_list)
                    self._instantiation[var_id][id_key] = instantiation_value
            else:
                id_key = (top_obj_id,)
                self._instantiation[var_id][id_key] = instantiation_value

    def save_instantiation(self) -> None:
        self._io_handler.set_instantiation_data(self._instantiation)
