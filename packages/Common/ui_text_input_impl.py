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
__since__ = "2023. 12. 15"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.ui_text_input import Ui_Dialog
from Common.resources_icons import roundButton


class UI_Combo_Integer(QtWidgets.QDialog):
  '''
  user interface for defining a string
  designed to be either used with the signal mechanism or reading the result

  usage :
  ui_ask = UI_String("give new model name or type exit ", "model name or exit", limiting_list = acceptance_list)
      ui_ask.exec_()
      model_name = ui_ask.getText()
  '''

  # aborted = QtCore.pyqtSignal()

  accepted = QtCore.pyqtSignal(int)

  def __init__(self, prompt, placeholdertext="", limiting_list=[], acceptance_list=[], fokus=True):
    """
    Serves the purpose of defining a string allowing for accepting or rejecting the result
    :param prompt: displayed in the window title
    :param placeholdertext: place holder shown in the line edi
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
    self.acceptance_list =  acceptance_list
    self.limiting_list = limiting_list
    self.setWindowTitle(prompt)
    self.text = None

    # reg_ex = QtCore.QRegExp("[-+]?[0-9]*")         #"[0-9]+.?[0-9]{,2}")
    # input_validator = QtGui.QRegExpValidator(reg_ex, self.ui.comboBox)
    # self.ui.comboBox.setValidator(input_validator)

    self.ui.pushAccept.clicked.connect(self.__accept)
    self.ui.pushReject.clicked.connect(self.close)
    self.ui.comboBox.currentTextChanged.connect(self.__changedText)
    self.ui.pushReject.setFocus()

    self.palette_red = QtGui.QPalette()
    self.palette_red.setColor(QtGui.QPalette.Text, QtCore.Qt.red)

    self.palette_black = QtGui.QPalette()
    self.palette_black.setColor(QtGui.QPalette.Text, QtCore.Qt.black)

    acceptance_list_txt = [str(n) for n in acceptance_list]
    self.ui.comboBox.addItems(acceptance_list_txt)

    if fokus:
      self.ui.comboBox.setFocus()

  def __changedText(self, Qtext):
    text = Qtext
    if text:
      number = int(text)
      print("got number %s"%number)
      self.ui.pushAccept.show()
      self.ui.pushAccept.setFocus()
      self.value = number

  def __accept(self):
    self.accepted.emit(self.value)
    self.close()

  def getValue(self):
    return self.value

# ============================ testing ======================


def changing(txt):
  print("changing:", txt)


if __name__ == '__main__':
  from Common.resource_initialisation import DIRECTORIES
  import os

  JOIN = os.path.join

  DIRECTORIES["packages"] = JOIN(os.path.abspath(".."))
  DIRECTORIES["common"] = JOIN(DIRECTORIES["packages"], "Common")
  DIRECTORIES["icon_location"] = JOIN(DIRECTORIES["common"], "icons")

  a = QtWidgets.QApplication([])
  accept = [1,2,3,10]
  w = UI_Combo_Integer("give float", str(accept), acceptance_list=accept)
  w.show()
  w.accepted.connect(changing)
  a.exec_()
