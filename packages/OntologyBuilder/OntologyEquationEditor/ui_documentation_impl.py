#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI resource
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

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from OntologyBuilder.OntologyEquationEditor.ui_documentation import Ui_DocumentationDialog


class UI_DocumentationDialog(QtWidgets.QDialog):
  """
      define documentation of a physical variable
  """

  finished = QtCore.pyqtSignal()

  def __init__(self, phys_var):
    """
    constructs a dialog window based on QDialog
    @param title:     title string: indicates the tree's nature
    @param current_variable_type: physical variable
    """
    self.phys_var = phys_var
    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_DocumentationDialog()
    self.ui.setupUi(self)
    self.setWindowTitle('edit documentation')
    self.ui.lineDocumentation.setText(phys_var.doc)
    self.ui.lineDocumentation.selectAll()
    self.ui.pushCancle.show()

  def on_lineDocumentation_editingFinished(self):
    doc = str(self.ui.lineDocumentation.text())
    self.phys_var.doc = doc
    self.finished.emit()
    self.hide()

  def on_pushCancle_pressed(self):
    self.hide()
