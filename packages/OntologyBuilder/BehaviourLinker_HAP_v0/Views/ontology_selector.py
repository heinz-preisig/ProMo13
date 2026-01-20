from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore

from packages.OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import ontology_selector_ui

# TODO: Code the mode that can create a new ontology.


class OntologySelectorView(QDialog):
  def __init__(self, ontology_names: str, parent=None, is_new_allowed: bool = False):
    super().__init__(parent)

    self.ui = ontology_selector_ui.Ui_ontology_selector()
    self.ui.setupUi(self)

    self.ui.pbutton_cancel.setFocus()

    # Two modes for this dlg. In one we can create a new ontology and
    # select it. In the other we can only select between existing
    # ontologies.
    if is_new_allowed:
      self.ui.label_instruction.setText(
          "Select an Ontology or create a new one.")
      self.ui.pbutton_create.setVisible(True)
    else:
      self.ui.label_instruction.setText("Select an Ontology.")
      self.ui.pbutton_create.setVisible(False)

    self.ui.pbutton_accept.setEnabled(False)

    # Creating and loading the model
    self.model = QtCore.QStringListModel(ontology_names)
    self.ui.list_ontologies.setModel(self.model)

    # Connectiong signals to slots
    self.ui.list_ontologies.selectionModel().selectionChanged.connect(
        self.on_selection_changed
    )
    self.ui.list_ontologies.doubleClicked.connect(self.accept)

    self.ui.pbutton_accept.clicked.connect(self.accept)
    self.ui.pbutton_cancel.clicked.connect(self.reject)

  def on_selection_changed(self, selected):
    if selected:
      self.ui.pbutton_accept.setEnabled(True)
    else:
      self.ui.pbutton_accept.setEnabled(False)
