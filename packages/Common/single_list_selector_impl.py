#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 graph object resources
===============================================================================

The graph objects are used in the ModelComposer and defined based on a basic structure stored in
gaph_objects_ini.json
and edited in GraphComponentenEditor
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2013. 01. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from copy import copy

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.resources_icons import roundButton
from Common.single_list_selector import Ui_Dialog


class SingleListSelector(QtWidgets.QDialog):
  '''
  selects an item from a list
  '''

  newSelection = QtCore.pyqtSignal(str)

  def __init__(self, thelist, selected=None, myparent=None, **kwargs):
               # left_icon="reject", left_tooltip="reject",
               # centre_icon="cancel", centre_tooltip="cancel",
               # right_icon="accept", right_tooltip="accept"):
    '''
    Constructor
    Behaviour
     -- double click assumes also right button pressed
     -- single click requires acceptance -- default right button
     -- left button is default reject
     -- returns selection and state (left | right | selected)

    Parameters
    ----------
    centre_icon
    centre_tooltip
    '''
    self.thelist = thelist
    self.selection = None
    QtWidgets.QDialog.__init__(self, parent=myparent)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    self.kwargs = kwargs

    self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Dialog|
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
            )



    icons = {}
    tooltips ={}
    buttons = {"left": self.ui.pushLeft,
               "centre": self.ui.pushCentre,
               "right": self.ui.pushRight,
              }
    for pos in ["left", "centre", "right"]:
      if pos in kwargs:
        icon, tooltip, mode = kwargs[pos]
        roundButton(buttons[pos], icon, tooltip)
        if mode == "hide":
          buttons[pos].hide()
        else:
          buttons[pos].show()
      else:
        buttons[pos].hide()


    self.ui.listWidget.addItems(thelist)

    self.selection = None
    self.state = None  # left | right | selected

    max_width = 0
    height = 20
    for i in thelist:
      label = QtWidgets.QLabel(i)
      width = label.fontMetrics().boundingRect(label.text()).width()
      height = height + label.fontMetrics().boundingRect(label.text()).height()
      if width > max_width:
        max_width = width
    self.__resizeMe(height, max_width + 20)


  def hide(self):
    QtWidgets.QWidget.hide(self)

  def getSelection(self):
    return self.selection, self.state

  def __resizeMe(self, height, width):
    tab_size = QtCore.QSize(width, height)
    self.ui.listWidget.resize(tab_size)
    size_b = self.ui.pushLeft.size()
    b_width = size_b.width()* 3 #there are two buttons plus margin
    b_height = size_b.height()
    if b_width < width:
      size_b.setWidth(width)
    elif width < b_width:
      width = b_width
      tab_size = QtCore.QSize(width, height)
      self.ui.listWidget.resize(tab_size)
    s = QtCore.QSize(width + 30, b_height + height + 60)
    self.resize(s)

  def on_listWidget_itemClicked(self, v):
    # print('item clicked')
    currentItem = self.ui.listWidget.currentItem()
    self.selection = str(currentItem.text())
    self.state = "selected"
    self.ui.pushRight.show()

  def on_listWidget_itemDoubleClicked(self, v):
    self.on_listWidget_itemClicked(v)
    self.state = "selected"
    self.on_pushRight_pressed()

  def on_pushRight_pressed(self):
    # self.newSelection.emit(str(self.selection))
    self.state = self.kwargs["right"][0]  #RULE: right must be accept
    # self.newSelection.emit(self.selection)
    self.hide()

  def on_pushCentre_pressed(self):
    self.state = self.kwargs["centre"][0]
    self.selection = None
    self.hide()

  def on_pushLeft_pressed(self):
    self.state = self.kwargs["left"][0]
    self.selection = None
    self.hide()

  def accept(self):  # overwrite dialogue method
    # print('accept', self.selection)
    self.hide()

  def reject(self):  # overwrite dialogue method
    print('reject', self.selection)
    self.hide()
    return


  def mousePressEvent(self, event): # Note: makes it movable
    self.oldPos = event.globalPos()

  def mouseMoveEvent(self, event): # Note: makes it movable
    delta = QtCore.QPoint(event.globalPos() - self.oldPos)
    self.move(self.x() + delta.x(), self.y() + delta.y())
    self.oldPos = event.globalPos()