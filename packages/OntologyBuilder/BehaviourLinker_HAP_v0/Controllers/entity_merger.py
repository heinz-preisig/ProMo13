from typing import List

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QStringListModel, QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView, QListView

from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_merger import EntityMergerModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_merger import EntityMergerView
from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates import image_list


# TODO List
# 1. Filter the list of available variables to add.
# 2. Automatically mark as input or instantiation some variables.


class EntityMergerController(QtCore.QObject):
  selectionStatusChanged = QtCore.pyqtSignal(bool)

  def __init__(self, model: EntityMergerModel, view: EntityMergerView):
    super().__init__()

    self._model = model
    self._view = view

    self._view.ui.list_equations.setModel(self._model.equations_model)
    delegate = image_list.ImageItemDelegate(self._view.ui.list_equations)
    self._view.ui.list_equations.setItemDelegate(delegate)

    # Connecting signals to slots
    # View signals
    self._view.ui.pbutton_next.clicked.connect(self.next)
    self._view.ui.pbutton_previous.clicked.connect(self.previous)
    self._view.ui.pbutton_cancel.clicked.connect(self._view.reject)

    self._view.ui.list_equations.doubleClicked.connect(self.next)
    # Model signals
    self._model.variableChanged.connect(self._view.load_label_img)
    self._model.newDataLoaded.connect(self._view.set_pbutton_previous_state)

    self.next()

  def next(self):
    index = self._view.ui.list_equations.currentIndex()
    if index.isValid():
      self._model.solve_conflict(index)

    data = self._model.get_next_conflict()
    if data is None:
      self._view.accept()

  def previous(self):
    self._model.undo()
