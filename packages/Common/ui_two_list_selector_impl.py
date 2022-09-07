#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI resource -- selects from a list into a list
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 08. 2010"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets

from Common.ui_two_list_selector import Ui_TwoListSelector


class UI_TwoListSelector(QtCore.QObject):
  '''
  selects from a list generating a new list, which can also re-arranged by moving elements up or down.
  '''

  newSelection = QtCore.pyqtSignal(list)
  finished = QtCore.pyqtSignal(list)

  def __init__(self):
    '''
    plain constructor
    '''

    QtWidgets.QWidget.__init__(self)
    self.ui = Ui_TwoListSelector()
    self.ui.setupUi(self)
    self.show()
    self.exec_()

  def close(self):
    QtCore.QObject.close(self)
    del self

  def populateLists(self, selection, selected):
    self.ui.listAvailable.clear()
    self.ui.listSelected.clear()
    for i in selection:
      if i not in selected:
        self.ui.listAvailable.addItem(i)
      else:
        self.ui.listSelected.addItem(i)

  def getSelected(self):
    selected = []
    count = self.ui.listSelected.count()
    for i in range(0, count):
      item = self.ui.listSelected.item(i)
      s = str(item.text())
      selected.append(s)
    return selected

  def on_listSelected_itemDoubleClicked(self):
    self.on_pushLeft_pressed()

  def on_listAvailable_itemDoubleClicked(self):
    self.on_pushRight_pressed()

  def on_pushUp_pressed(self):
    r = self.ui.listSelected.currentRow()
    print('up row', r)
    i = self.ui.listSelected.takeItem(r)
    self.ui.listSelected.insertItem(r - 1, i)
    self.ui.listSelected.setCurrentItem(i)
    self.row = self.ui.listSelected.currentRow()
    self.newSelection.emit(self.getSelected())

  def on_pushDown_pressed(self):
    r = self.ui.listSelected.currentRow()
    print('down row', r)
    i = self.ui.listSelected.takeItem(r)
    self.ui.listSelected.insertItem(r + 1, i)
    self.ui.listSelected.setCurrentItem(i)
    self.row = self.ui.listSelected.currentRow()
    self.newSelection.emit(self.getSelected())

  def on_pushRight_pressed(self):
    # print( 'push left' )
    a = self.ui.listAvailable.currentRow()
    item = self.ui.listAvailable.takeItem(a)
    self.ui.listSelected.addItem(item)
    self.update()
    self.newSelection.emit(self.getSelected())

  def on_pushLeft_pressed(self):
    # print( 'push right' )
    a = self.ui.listSelected.currentRow()
    item = self.ui.listSelected.takeItem(a)
    self.ui.listAvailable.addItem(item)
    self.update()
    self.newSelection.emit(self.getSelected())

  def on_pushOK_pressed(self):
    self.finished.emit(self.getSelected())
    self.hide()
