from typing import List

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QStringListModel, QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView, QListView

from Common.classes import ontology
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import entity_generator_ui
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.progress_bar import CircleProgressBar


class EntityGeneratorView(QtWidgets.QDialog):
  def __init__(self, model, parent=None):
    super().__init__(parent)

    # Set up the user interface
    self.ui = entity_generator_ui.Ui_entity_generator()
    self.ui.setupUi(self)

    self._model = model

    self.p_bar = CircleProgressBar(6, self)
    self.p_bar.resize(self.p_bar.minimumSizeHint())
    self.ui.pbar_layout.addWidget(self.p_bar)

    self.ui.pbutton_next.setFocus()

    self.ui.stackedWidget.setCurrentIndex(0)

    self.setup_page()

  def setup_page(self):
    page = self.ui.stackedWidget.currentIndex()

    self.setup_buttons(page)
    self.setup_selection_mode(page)

  def setup_buttons(self, page):
    # print("page:" + str(page))
    self.ui.pbutton_previous.setEnabled(True)
    self.ui.pbutton_finish.setEnabled(True)
    self.ui.pbutton_next.setEnabled(False)

    if page == 0:
      self.ui.pbutton_previous.setEnabled(False)
      self.ui.pbutton_next.setEnabled(True)

    if page != 5:
      self.ui.pbutton_finish.setEnabled(False)

  def setup_selection_mode(self, page):
    # Setting the selection mode for pages 2 and 5
    if page == 2 or page == 6:
      # When the type of the entity is "Node" multiple tokens and
      # bases can be selected.
      # TODO: Check about multiple bases for the "Arcs"
      if self.ui.rbutton_node.isChecked():
        # Multiple selection mode
        self.ui.list_token.setSelectionMode(2)
      else:
        # Single selection mode
        self.ui.list_token.setSelectionMode(1)

  def next_page(self):
    self.p_bar.next()

    current_page = self.ui.stackedWidget.currentIndex()
    self.ui.stackedWidget.setCurrentIndex(current_page + 1)

    self.setup_page()

  def previous_page(self):
    self.p_bar.previous()

    current_page = self.ui.stackedWidget.currentIndex()
    self.ui.stackedWidget.setCurrentIndex(current_page - 1)

    self.setup_page()

  def on_tree_changed(self):
    self.ui.tree_bases.expandAll()
    # self.ui.tree_entities.clearSelection()
    self.ui.tree_bases.setCurrentIndex(QtCore.QModelIndex())
