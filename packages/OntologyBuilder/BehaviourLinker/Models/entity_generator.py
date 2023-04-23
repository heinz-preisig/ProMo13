from typing import List, Optional

import itertools

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QStringListModel
from packages.Common.classes import ontology
from packages.OntologyBuilder.BehaviourLinker.Models import tree_bases


class EntityGeneratorModel(QtCore.QObject):
  # Signals
  tree_changed = QtCore.pyqtSignal()

  def __init__(self, ontology: ontology.Ontology, entity_ids: List[str]):
    super().__init__()

    self.ontology = ontology
    self.entity_ids = entity_ids
    self.new_entity_name = None

    # Qt Models
    # One Model for the list on each page of the Stacked Widget.
    # Except page 0 that have RadioButtons instead.
    self.stacked_models: List[QStringListModel] = [None]*6
    for i in range(1, 5):
      self.stacked_models[i] = QStringListModel()

    self.tree_bases_model = tree_bases.TreeBasesModel()

    # Model to store the selections for each page as they get made.
    # This model will feed the Summary widget.
    self.summary = QStringListModel([""]*6)

  def update_summary(self, pos: int, new_value):
    """Updates the summary model.

    Args:
        pos (int): position in the list of the value to be updated.
        new_value (str): the value used for the update.
    """
    if pos != 0:
      new_value = self._selection_to_string(pos, new_value)

    old_value = self.summary.index(pos).data()

    # If a new selection is made then the selection for all the items
    # after the current page is reset.
    if new_value != old_value:
      for i in range(pos + 1, 6):
        index = self.summary.index(i)
        self.summary.setData(index, "")

      # Update summary in the given position.
      index = self.summary.index(pos)
      self.summary.setData(index, new_value)

  def _selection_to_string(self, pos, selection):
    if pos == 2:
      return "_".join(
          sorted([
              index.data()
              for index in selection
          ]))
    elif pos == 5:
      return "*".join(
          sorted([
              self.tree_bases_model.path_from_index(index)
              for index in selection
          ]))
    else:
      return selection[0].data()

  def update_stacked_models(self, page: int):
    """Update a stacked model.

    Updates the model indicated by page using the information stored in
    the ontology and the entity_ids.

    Args:
        page (int): indicates which model should be updated.
    """
    # If there is already a selection stored in summary no update is
    # required.
    if self.summary.index(page).data() != "":
      return

    # No model exist for page0. It only contains the RadioButtons
    if page == 0:
      return

    # For pages 1-4 the update information comes from the ontology.
    # For page 5 the possible bases are filtered from the entity_ids.
    if page != 5:
      print(self.summary.stringList())
      new_list = self.ontology.get_ontology_tree_info(
          page,
          self.summary.stringList(),
      )
      self.stacked_models[page].setStringList(new_list)
    else:
      bases = self._get_possible_bases()
      self.tree_bases_model.load_data(bases)
      self.tree_changed.emit()

  def _get_possible_bases(self):
    """Returns valid entity bases from existing entities.

    An existing entity can serve as a base for a new entity if it meets
    the following criteria:
      - It shares the same type, network, mechanism/timescale, and
        nature.
      - All its tokens are contained within the tokens of the new
        entity.

        Example:
          Consider a new entity with tokens [mass, energy]. It can use
          the following entities as a base:
            - [mass]
            - [energy]
            - [mass, energy]

          However, it cannot use the following entities as a base:
            - [charge]              (Missing charge token in the new entity)
            - [charge, mass]        (Missing charge token in the new entity)
    """
    ent_type, network, tokens, mechanism, nature, _ = self.summary.stringList()

    # Finding all token combinations with at least one token.
    # The token order is maintained.
    tokens = tokens.split("_")
    token_combinations = []
    for l in range(1, len(tokens) + 1):
      for combo in itertools.combinations(tokens, l):
        token_combinations.append(list(combo))

    token_combinations = [
        "_".join(token)
        for token in token_combinations
    ]

    # print(token_combinations)
    # For each of the token combinations the names of the valid entities
    # are stored to be returned.
    possible_bases = []
    for token in token_combinations:
      partial_id = self._generate_entity_id(
          ent_type,
          network,
          token,
          mechanism,
          nature,
          None,
      )
      # print(partial_id)
      possible_bases.extend([
          full_id
          for full_id in self.entity_ids
          if partial_id in full_id
      ])
      # print(possible_bases)

    return sorted(possible_bases)

  def _generate_entity_id(
      self,
      ent_type: str,
      network: str,
      tokens: str,
      mechanism: str,
      nature: str,
      name: Optional[str]
  ) -> str:
    """Generates the entity ID based on provided arguments.

    Args:
        ent_type (str): Entity type.
        network (str): Entity network.
        tokens (str): Entity tokens.
        mechanism (str): Entity mechanism/timescale.
        nature (str): Entity nature.
        name (Optional[str]): Entity name.

    Returns:
        str: A partial ID if name is None. Otherwise a full ID of an
          entity.
    """
    str1 = "|".join([tokens, mechanism, nature])
    str2 = ".".join([network, ent_type, str1])

    if name is not None:
      return ".".join([str2, name])

    return str2

  def get_used_names(self):
    entity_info = self.summary.stringList()[:5]
    partial_id = self._generate_entity_id(*entity_info, "")

    return [
        full_id.split(".")[-1]
        for full_id in self.entity_ids
        if partial_id in full_id
    ]

  def add_entity_name(self, name: str):
    entity_info = self.summary.stringList()[:5]
    self.new_entity_id = self._generate_entity_id(*entity_info, name)
