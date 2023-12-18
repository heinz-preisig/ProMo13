#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI resourece for inputing a string to be not part of a constraing list
===============================================================================



"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2020. 12. 21"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.ui_string_dialog import Ui_Dialog
from Common.resources_icons import roundButton


class UI_String(QtWidgets.QDialog):
  '''
  user interface for defining a string
  designed to be either used with the signal mechanism or reading the result

  usage :
  ui_ask = UI_String("give new model name or type exit ", "model name or exit", limiting_list = acceptance_list)
      ui_ask.exec_()
      model_name = ui_ask.getText()
  '''

  # aborted = QtCore.pyqtSignal()
  accepted = QtCore.pyqtSignal(str)

  def __init__(self, prompt, placeholdertext="", fokus=True):
    """
    Serves the purpose of defining a string allowing for accepting or rejecting the result
    :param prompt: displayed in the window title
    :param placeholdertext: place holder shown in the line edit
    :param accept: method/function reference
    :param reject: method/function reference
    """
    # TODO: add validator
    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    # print(" <<<< show me")
    self.hide()

    roundButton(self.ui.pushAccept, "accept", tooltip="accept")
    roundButton(self.ui.pushReject, "reject", tooltip="reject")

    self.ui.pushAccept.hide()

    self.placeholdertext = placeholdertext
    self.setWindowTitle(prompt)
    self.real = None

    reg_ex = QtCore.QRegExp("^[-+]?[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?$")

    input_validator = QtGui.QRegExpValidator(reg_ex, self.ui.lineEdit)
    self.ui.lineEdit.setValidator(input_validator)

    self.ui.pushAccept.clicked.connect(self.__accept)
    self.ui.pushReject.clicked.connect(self.close)
    self.ui.lineEdit.textChanged.connect(self.__changedText)

    self.ui.pushReject.setFocus()
    self.ui.lineEdit.setPlaceholderText(placeholdertext)

    if fokus:
      self.ui.lineEdit.setFocus()

  def __changedText(self, Qtext):
    self.ui.pushAccept.show()
    try:
      self.real = float(Qtext)
    except:
      pass

  def __accept(self):
    self.accepted.emit(self.ui.lineEdit.text())
    self.text = self.ui.lineEdit.text()
    self.close()

  def getNumber(self):
    return self.real


# ============================ testing ======================


if __name__ == '__main__':
  from Common.resource_initialisation import DIRECTORIES
  import os

  JOIN = os.path.join

  DIRECTORIES["packages"] = JOIN(os.path.abspath(".."))
  DIRECTORIES["common"] = JOIN(DIRECTORIES["packages"], "Common")
  DIRECTORIES["icon_location"] = JOIN(DIRECTORIES["common"], "icons")

  a = QtWidgets.QApplication([])
  accept = [1.123]
  w = UI_String("give float")
  w.show()
  a.exec_()

  print("result: ", w.getNumber())
