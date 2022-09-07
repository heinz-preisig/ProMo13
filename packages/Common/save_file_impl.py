#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 save file module of the ModelComposer
===============================================================================

modal popup window asking for save | cancel | do not save (ignore)

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL"
__version__ = "5.01"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.save_file import Ui_Dialog


class SaveFileDialog(QtWidgets.QDialog):
  answer = QtCore.pyqtSignal(str)

  def __init__(self):
    QtWidgets.QWidget.__init__(self)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)

  def on_pushButtonSave_pressed(self):
    # print("save")
    self.answer.emit("save")
    self.close()

  def on_pushButtonCancel_pressed(self):
    # print("cancel")
    self.answer.emit("cancel")
    self.close()

  def on_pushButtonDoNotSave_pressed(self):
    # print("do not save")
    self.answer.emit("ignore")
    self.close()


if __name__ == '__main__':
  a = QtWidgets.QApplication(sys.argv)
  w = SaveFileDialog()
  w.show()
  value = a.exec_()
  print(">>>>>>>>>>>", value)
