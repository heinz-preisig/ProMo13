"""
variable instantiation dialog
"""


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from packages.ModelBuilder.ModelComposer.instantiation_dialog_HAP import Ui_Dialog
from packages.Common.classes import entity
from packages.Common.classes import variable
from Common.resources_icons import roundButton

class InstantiationDialog(QtWidgets.QDialog):

  def __init__(self, variable_to_instantiate, variable_instantiated, variables):

    super().__init__()
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)

    self.variable_to_instantiate = variable_to_instantiate
    self.variable_instantiated = variable_instantiated
    self.variables = variables

    self.newly_instantiated = {}

    self.variable_index = {}
    self.value_index = {}

    self.selected_variable_ID = None


    roundButton(self.ui.pushInstantiate, "accept", tooltip="instantiate variables with numbers")
    roundButton(self.ui.pushAccept, "accept", tooltip="save instantiations")
    roundButton(self.ui.pushCancel, "reject", tooltip="cancel")

    self.ui.pushInstantiate.setAutoDefault(False)
    self.ui.pushAccept.setAutoDefault(False)
    self.ui.pushCancel.setAutoDefault(False)

    self.ui.pushInstantiate.hide()


    reg_ex = QtCore.QRegExp("[-+]?[0-9]*[.]?[0-9]+([eE][-+]?[0-9]+)?")         #"[0-9]+.?[0-9]{,2}")
    input_validator = QtGui.QRegExpValidator(reg_ex, self.ui.lineEdit)
    self.ui.lineEdit.setValidator(input_validator)

    self.ui.lineEdit.hide()
    self.ui.listValues.hide()

    self.populateListVariable()

  def populateListVariable(self):
    print("populate variables")
    items = sorted(self.variable_to_instantiate.keys())
    items_labelled = []
    row = 0
    for i in items:
      label = self.variables[i].label
      # items_labelled.append("%s:%s"%(i,label))
      self.ui.listVariables.addItem("%s:%s"%(i,label))
      self.variable_index[row] = i
      row += 1

  def populateValues(self):
    print("populate values")
    if self.selected_variable_ID in self.variable_instantiated:
      values = self.variable_instantiated[self.selected_variable_ID]
      self.ui.listValues.show()
    else:
      values = ""
      self.ui.listValues.hide()
      return
    row = 0
    self.ui.listValues.clear()
    for i in values:
      s = str(i)
      self.ui.listValues.addItem(s)
      self.value_index[row] = i
      row += 1

  def on_listVariables_clicked(self, item):
    row = item.row()
    self.selected_variable_ID = self.variable_index[row]
    print("selected_variable", self.selected_variable_ID)
    self.populateValues()
    self.ui.lineEdit.show()
    self.ui.lineEdit.clear()
    self.ui.pushInstantiate.show()
    pass

  def on_listValues_clicked(self,item):
    row = item.row()
    value = self.value_index[row]
    self.ui.lineEdit.setText(str(value))
    return

  # def on_lineEdit_returnPressed(self):
  def on_pushInstantiate_pressed(self):
    s = self.ui.lineEdit.text()
    if s:
      print(s)
      self.defined_value = float(s)
      self.newly_instantiated[self.selected_variable_ID] = self.defined_value
      self.ui.listValues.clear()
      self.ui.listValues.addItem(str(self.defined_value))
      self.ui.listValues.show()
      self.ui.listVariables.setFocus()

  def on_pushAccept_pressed(self):
    print("accept")
    self.close()

  def on_pushCancel_pressed(self):
    print("cancel")
    self.newly_instantiated={}
    self.close()


  # def on_pushInstantiate_pressed(self):
  #   print("instantiate", self.selected_variable_ID, self.defined_value)
  #
  #   self.newly_instantiated[self.selected_variable_ID] = self.defined_value