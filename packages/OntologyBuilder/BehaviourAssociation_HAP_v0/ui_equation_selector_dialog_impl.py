"""Implementation of GUI logic for the Equation Selector dialog."""
from typing import Optional, List

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from packages.OntologyBuilder.BehaviourAssociation import ctrl_equation_selector_dialog
from packages.OntologyBuilder.BehaviourAssociation import ui_equation_selector_dialog


_Controller = ctrl_equation_selector_dialog.ControllerEquationSelectorDlg


class EquationSelectorDlg(QtWidgets.QDialog):
  """Implementation of the logic for the equation selector dialog.

  Attributes:
    ui (object): Contains the GUI widgets, obtained from QtDesigner.
  """

  def __init__(
    self,
    controller: _Controller,
    parent: Optional[QtWidgets.QWidget] = None,
  ):
    """Initializes the EquationSelectorDlg.

    Args:
      parent (QWidget): Parent widget of the dialog. Defaults to **None**.
    """
    super().__init__(parent)
    self.ui = ui_equation_selector_dialog.Ui_Dialog()
    self.ui.setupUi(self)

    self.controller = controller

    self._refresh_variable_list()

    # Connections
    self.ui.check_box_show_all_vars.toggled.connect(self._show_all_vars)
    self.ui.list_variables.itemClicked.connect(
      lambda item: self._variable_selected(self.ui.list_variables.row(item)))
    self.ui.list_explicit.itemClicked.connect(self._equation_selected)
    self.ui.list_implicit.itemClicked.connect(self._equation_selected)

    self.ui.pbutton_save.clicked.connect(self._save_eq_selection)
    self.ui.pbutton_discard.clicked.connect(self._refresh_variable_list)
    self.ui.pbutton_accept.clicked.connect(super().accept)
    self.ui.pbutton_cancel.clicked.connect(super().reject)

  def _save_eq_selection(self) -> None:
    """Saves the changes done in the equation lists."""

    var_pos = self.ui.list_variables.currentRow()
    eq_info = {
      "explicit": [],
      "implicit": [],
    }
    for pos in range(self.ui.list_explicit.count()):
      item = self.ui.list_explicit.item(pos)
      widget = self.ui.list_explicit.itemWidget(item)
      eq_info["explicit"].append(widget.is_checked())

    for pos in range(self.ui.list_implicit.count()):
      item = self.ui.list_implicit.item(pos)
      widget = self.ui.list_implicit.itemWidget(item)
      eq_info["implicit"].append(widget.is_checked())

    self.controller.add_new_var_info(var_pos, eq_info)
    self._refresh_variable_list()

  def _show_all_vars(self, toggled: bool) -> None:
    """Changes what variables swill be shown.

    Args:
        toggled (bool): If **True** all variables will be shown. If
          **False** only variables without equations assigned will be
          shown.
    """
    self.controller.set_show_all(toggled)

    self._refresh_variable_list()

  def _refresh_variable_list(self) -> None:
    """Reloads the variable list."""
    self.ui.list_variables.clear()
    var_info = self.controller.get_display_variables()

    # If there are no variables to display then it should display all
    # variables.
    if not var_info:
      self.ui.check_box_show_all_vars.setChecked(True)
      var_info = self.controller.get_display_variables()

    finished = []

    for count, (var_png_path, status) in enumerate(var_info):
      if status:
        finished.append(count)

      pixmap = QtGui.QPixmap(var_png_path)

      var_display = QtWidgets.QLabel()
      var_display.setPixmap(pixmap)
      var_display.setFixedHeight(48)
      var_display.setMinimumWidth(48)
      var_display.setAlignment(QtCore.Qt.AlignCenter)

      list_item = QtWidgets.QListWidgetItem()
      list_item.setSizeHint(var_display.sizeHint())

      self.ui.list_variables.addItem(list_item)
      self.ui.list_variables.setItemWidget(list_item, var_display)

    self._set_variable_list_style(
      [],
      range(self.ui.list_variables.count()),
      finished,
    )

    self._refresh_equation_list(None)

  def _refresh_equation_list(self, var_pos: Optional[int] = None) -> None:
    """Reloads the equation list.

    The equations depend on the selected variable. If no variable is
    selected the tab widget won't be visible.

    Args:
        var_pos (Optional[int], optional): Position of the selected
          variable in the variable list. Defaults to **None**.
    """
    if var_pos is None:
      self.ui.tab_equations.setVisible(False)
      self.ui.pbutton_save.setVisible(False)
      self.ui.pbutton_discard.setVisible(False)
      return

    self.ui.list_explicit.clear()
    self.ui.list_implicit.clear()

    equation_data = self.controller.get_display_equations(var_pos)

    for path, checked in equation_data["explicit"]:
      eq_display = EquationDisplay(path, checked)

      list_item = QtWidgets.QListWidgetItem()
      list_item.setSizeHint(eq_display.sizeHint())

      self.ui.list_explicit.addItem(list_item)
      self.ui.list_explicit.setItemWidget(list_item, eq_display)

    for path, checked in equation_data["implicit"]:
      eq_display = EquationDisplay(path, checked)

      list_item = QtWidgets.QListWidgetItem()
      list_item.setSizeHint(eq_display.sizeHint())

      self.ui.list_implicit.addItem(list_item)
      self.ui.list_implicit.setItemWidget(list_item, eq_display)

    title = "Explicit Equations (" + str(self.ui.list_explicit.count())  + ")"
    self.ui.tab_equations.setTabText(0, title)

    title = "Implicit Equations (" + str(self.ui.list_implicit.count())  + ")"
    self.ui.tab_equations.setTabText(1, title)

    self.ui.tab_equations.setVisible(True)
    self.ui.pbutton_save.setVisible(True)
    self.ui.pbutton_discard.setVisible(True)
    self.ui.tab_equations.setCurrentIndex(0)

  def _variable_selected(self, row: int) -> None:
    selected = [row]
    var_info = self.controller.get_display_variables()
    finished = []
    for count, (_, status) in enumerate(var_info):
      if status:
        finished.append(count)

    unselected = list(range(self.ui.list_variables.count()))
    unselected.remove(row)

    self._set_variable_list_style(selected, unselected, finished)

    self._refresh_equation_list(row)

  def _equation_selected(self, item: QtWidgets.QListWidgetItem) -> None:
    """Updates the checkbox status in the `EquationDisplay`.

    Args:
        item (QtWidgets.QListWidgetItem): Item that has been selected.
    """
    parent_list = item.listWidget()
    widget = parent_list.itemWidget(item)
    widget.toggle()

  def _set_variable_list_style(
    self,
    selected: List[int],
    unselected: List[int],
    finished: List[int],
  ) -> None:
    """Changes the style of the variables in the variable list.

    The selected variable will have a blue border.
    Variables that already have equations assigned are considered
    fisnished and will have a green border.
    The rest of the variables (unselected) will have the normal black
    border.

    Args:
        selected (List[int]): Position of the selected variable.
        unselected (List[int]): Position of variables that are not
          selected or finished.
        finished (List[int]): Position of variables considered finished.
    """
    for row_id in unselected:
      list_item = self.ui.list_variables.item(row_id)
      widget = self.ui.list_variables.itemWidget(list_item)
      widget.setStyleSheet("border: 1px solid black;")

    for row_id in finished:
      list_item = self.ui.list_variables.item(row_id)
      widget = self.ui.list_variables.itemWidget(list_item)
      widget.setStyleSheet("border: 2px solid green;")

    for row_id in selected:
      list_item = self.ui.list_variables.item(row_id)
      widget = self.ui.list_variables.itemWidget(list_item)
      widget.setStyleSheet("border: 2px solid blue;")


class EquationDisplay(QtWidgets.QWidget):
  """Custom widget to display the equations."""
  def __init__(
    self,
    png_path: str,
    checked: bool,
    parent: QtWidgets.QWidget = None,
    ) -> None:
    super().__init__(parent)

    pixmap = QtGui.QPixmap()
    pixmap.load(png_path)

    label = QtWidgets.QLabel()
    label.setPixmap(pixmap)

    self.chkbox = QtWidgets.QCheckBox()
    self.chkbox.setChecked(checked)
    self.chkbox.setFixedWidth(15)

    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(self.chkbox)
    layout.addWidget(label)

    # TODO Check if this is needed
    spacer = QtWidgets.QSpacerItem(
      20,
      20,
      QtWidgets.QSizePolicy.Minimum,
      QtWidgets.QSizePolicy.Expanding,
    )
    layout.addItem(spacer)

    self.setLayout(layout)

  def toggle(self) -> None:
    """Changes the value of the `checked` property of the checkbox."""
    value = self.chkbox.isChecked()
    self.chkbox.setChecked(not value)

  def is_checked(self) -> bool:
    """Gets the value of the `checked` property of the checkbox."""
    return self.chkbox.isChecked()
