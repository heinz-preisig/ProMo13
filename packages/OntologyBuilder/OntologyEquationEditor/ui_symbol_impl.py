"""
===============================================================================
 GUI resource -- handles symbol dialogue for physical variable
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2015. 03. 01"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# from OntologyEquations.resources import NEW_VAR

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from OntologyBuilder.OntologyEquationEditor.resources import setValidator
from OntologyBuilder.OntologyEquationEditor.ui_symbol import Ui_SymbolDialog

ALLREADY_DEFINED = 'already defined -- give new variable'


class UI_SymbolDialog(QtWidgets.QDialog):
  """
  dialog for a variable
  any new variable will also generate a new equation

  state controlled
  """

  finished = QtCore.pyqtSignal()

  def __init__(self):  # variables, phys_var): # equations, phys_var):
    """
    rename the physical variable.
    Some funny things going on. One has to get the phys_var and change the label in there. Local referencing of the
    label
    does not work. Also if one passes the reference of the label and replaces the contents does not work.....
    """
    self.phys_var = None
    self.forbidden_symbol = None

    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_SymbolDialog()
    self.ui.setupUi(self)
    self.setWindowTitle('edit variable symbol')
    self.MSG = self.ui.MSG.setPlainText
    self.MSG("provide variable symbol")
    self.validator = setValidator(self.ui.lineSymbol)
    self.state_OK = False
    self.hide()

  def setUp(self, phys_var, forbidden_symbol):
    self.phys_var = phys_var
    self.forbidden_symbol = forbidden_symbol
    self.ui.groupSymbol.show()
    self.ui.lineSymbol.setText(self.phys_var.label)
    self.ui.lineSymbol.selectAll()
    self.ui.pushCancle.show()

  def on_lineSymbol_textChanged(self, text):
    if str(text) in self.forbidden_symbol:  # symbol OK ?
      self.MSG("already defined")
      self.state_OK = False
      return
    if len(str(text)) == 0:
      self.MSG("provide new variable name")
      self.state_OK = False
      return

    self.MSG("OK")
    self.state_OK = True

  def on_lineSymbol_returnPressed(self):
    # print("debugging -- line 81 -- gotten here ")
    if self.state_OK:
      # self.phys_var.label = str(self.ui.lineSymbol.text())
      label = str(self.ui.lineSymbol.text())
      self.phys_var.changeLabel(label)
      self.finished.emit()
      self.close()
    else:
      self.MSG("Invalid, provide variable symbol or cancle")

  def on_pushCancle_pressed(self):
    self.close()
