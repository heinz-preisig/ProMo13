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
__since__ = "2021. 02. 16"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets

from Common.ui_two_list_selector_dialog import Ui_Dialog
from Common.resources_icons import roundButton


class UI_TwoListSelector(QtWidgets.QDialog):
  '''
  selects from a list generating a new list, which can also re-arranged by moving elements up or down.
  '''

  newSelection = QtCore.pyqtSignal(list)
  finished = QtCore.pyqtSignal(list)

  def __init__(self):
    '''
    plain constructor
    '''

    super().__init__()
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    self.show()
    roundButton(self.ui.pushButtonExit, "exit", "exit" )


  def close(self):
    QtCore.QObject.close(self)
    del self

  def populateLists(self, selection, selected):
    self.ui.listWidgetLeft.clear()
    self.ui.listWidgetRight.clear()
    for i in selection:
      if i not in selected:
        self.ui.listWidgetLeft.addItem(i)
      else:
        self.ui.listWidgetRight.addItem(i)

  def getSelected(self):
    selected = []
    count = self.ui.listWidgetRight.count()
    for i in range(0, count):
      item = self.ui.listWidgetRight.item(i)
      s = str(item.text())
      selected.append(s)
    return selected

  def on_listWidgetRight_itemDoubleClicked(self):
    self.on_pushLeft_pressed()

  def on_listWidgetLeft_itemDoubleClicked(self):
    self.on_pushRight_pressed()

  def on_pushUp_pressed(self):
    r = self.ui.listWidgetRight.currentRow()
    print('up row', r)
    i = self.ui.listWidgetRight.takeItem(r)
    self.ui.listWidgetRight.insertItem(r - 1, i)
    self.ui.listWidgetRight.setCurrentItem(i)
    self.row = self.ui.listWidgetRight.currentRow()
    self.newSelection.emit(self.getSelected())

  def on_pushDown_pressed(self):
    r = self.ui.listWidgetRight.currentRow()
    print('down row', r)
    i = self.ui.listWidgetRight.takeItem(r)
    self.ui.listWidgetRight.insertItem(r + 1, i)
    self.ui.listWidgetRight.setCurrentItem(i)
    self.row = self.ui.listWidgetRight.currentRow()
    self.newSelection.emit(self.getSelected())

  def on_pushRight_pressed(self):
    # print( 'push left' )
    a = self.ui.listWidgetLeft.currentRow()
    item = self.ui.listWidgetLeft.takeItem(a)
    self.ui.listWidgetRight.addItem(item)
    self.update()
    self.newSelection.emit(self.getSelected())

  def on_pushLeft_pressed(self):
    # print( 'push right' )
    a = self.ui.listWidgetRight.currentRow()
    item = self.ui.listWidgetRight.takeItem(a)
    self.ui.listWidgetLeft.addItem(item)
    self.update()
    self.newSelection.emit(self.getSelected())

  def on_pushButtonExit_pressed(self):
    self.accept()
    return self.getSelected()
