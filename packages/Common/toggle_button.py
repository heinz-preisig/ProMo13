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
__since__ = "2018. 09. 15"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets


class ToggleButton(QtWidgets.QPushButton):
  """
  A toggle button
  On change the button shows the current state, which is also emited.
  """

  changed = QtCore.pyqtSignal(str)

  def __init__(self, labelA, labelB):

    QtWidgets.QPushButton.__init__(self)
    self.clicked.connect(self.toggleMe)
    self.labelA = labelA
    self.labelB = labelB
    self.setText(labelA)
    self.state = labelA
    self.changed.emit(self.state)

  def toggleMe(self):
    if self.state == self.labelA:
      self.state = self.labelB
      self.setText(self.labelB)
    else:
      self.state = self.labelA
      self.setText(self.labelA)

    self.changed.emit(self.state)


# ============= test ===============

def printme(value):
  print("toggled", value)


if __name__ == '__main__':
  app = QtWidgets.QApplication(sys.argv)
  button = ToggleButton('A', 'B')
  button.show()
  button.changed.connect(printme)
  sys.exit(app.exec_())
