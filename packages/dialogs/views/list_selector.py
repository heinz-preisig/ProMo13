from typing import List

from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore

from packages.dialogs.views.compiled_uis import list_selector_ui

# TODO: Code the mode that can create a new item.


class ListSelectorView(QDialog):
  def __init__(
      self,
      list_items: List[str],
      parent=None,
      title: str = "List selector",
      instruction: str = "Select an Item:",
      has_new_button: bool = False,
  ):
    super().__init__(parent)

    self.ui = list_selector_ui.Ui_list_selector()
    self.ui.setupUi(self)

    self.setWindowTitle(title)
    self.ui.label_instruction.setText(instruction)

    self.ui.pbutton_create.setVisible(has_new_button)

    self.ui.pbutton_accept.setEnabled(False)
    self.ui.pbutton_cancel.setFocus()

    # Creating and loading the model
    self.model = QtCore.QStringListModel(list_items)
    self.ui.list.setModel(self.model)

    # Connectiong signals to slots
    self.ui.list.selectionModel().selectionChanged.connect(
        self.on_selection_changed
    )
    self.ui.list.doubleClicked.connect(self.accept)

    self.ui.pbutton_accept.clicked.connect(self.accept)
    self.ui.pbutton_cancel.clicked.connect(self.reject)

  def on_selection_changed(self, selected):
    self.ui.pbutton_accept.setEnabled(bool(selected))
