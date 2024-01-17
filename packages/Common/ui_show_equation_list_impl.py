"""
view variable and its defining equations

currently limited to 4 equations
"""
__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2023.01.03"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "11"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.pop_up_message_box import makeMessageBox
from Common.resources_icons import roundButton
from Common.ui_show_equation_list import Ui_ShowEquationList

LIMIT = 4
HEIGHT = 25
FACTOR = 0.5

class ImgWidget(QtWidgets.QWidget):

  def __init__(self, parent=None):
    super(ImgWidget, self).__init__(parent)

  def make(self,pixmap):
    self.pic = pixmap #QtGui.QPixmap(path)
    size = self.pic.size()
    scaled_size = FACTOR * size
    # print("size", size, "\n scaled", scaled_size)
    self.scaled_pic = self.pic.scaled(scaled_size, transformMode=1)
    self.scaled_size = self.scaled_pic.size()

  def paintEvent(self, event):
    painter = QtGui.QPainter(self)
    painter.drawPixmap(0, 0, self.scaled_pic)

class UI_ShowVariableEquation(QtWidgets.QDialog):

  def __init__(self, eq_list_ID, image_location, buttons=["back"]):
    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_ShowEquationList()
    self.ui.setupUi(self)

    BUTTONS = {"yes": (self.ui.pushYes, "accept"),
            "no": (self.ui.pushNo, "reject"),
            "back": (self.ui.pushBack, "go back"),
            }
    for b in BUTTONS.keys():
      (ui, tip) = BUTTONS[b]
      roundButton(ui, b , tip)

    for b in BUTTONS:
      if b not in buttons:
        (ui,tip) = BUTTONS[b]
        ui.hide()

    # this will hide the title bar
    self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

    self.eq_list_ID = eq_list_ID
    if len(eq_list_ID) == 0:
      makeMessageBox("variable has no equations", buttons=["OK"])
      self.close()

    Epixmap = {}
    no_eqs = len(eq_list_ID)

    count = 0
    maxsize = QtCore.QSize(0,0)
    for eqID in eq_list_ID:
      E_file = str(os.path.join(image_location, "%s.png" % eqID))
      Epixmap[eqID] = QtGui.QPixmap()
      Epixmap[eqID].load(E_file)
      size = FACTOR * Epixmap[eqID].size()
      if size.height() > maxsize.height() or size.width() > maxsize.width():
        maxsize = size
      count += 1

    self.ui.tableWidget.setColumnCount(2)
    self.ui.tableWidget.setRowCount(no_eqs)
    self.ui.tableWidget.setColumnWidth(0,maxsize.width())

    total_height = 0
    row = 0
    for eqID in eq_list_ID:
      image = ImgWidget(self.ui.tableWidget)
      image.make(Epixmap[eqID])
      size = image.scaled_size
      # print("setting", size)
      self.ui.tableWidget.setColumnWidth(1,maxsize.width())
      self.ui.tableWidget.setColumnWidth(0, 50)
      new_height = size.height()+6
      self.ui.tableWidget.setRowHeight(row,new_height)
      total_height +=new_height
      self.ui.tableWidget.setCellWidget(row,1,image)
      self.ui.tableWidget.setCellWidget(row,0,QtWidgets.QLabel(eqID))
      # self.ui.tableWidget.resizeRowsToContents()
      # self.ui.tableWidget.resizeColumnsToContents()
      row += 1

    width = min(maxsize.width()+75, self.size().width()-12)
    self.ui.tableWidget.resize(width,total_height+50)

    widget_size_width = width+50
    widget_size_hight = total_height+200

    self.resize(widget_size_width,widget_size_hight)
    self.exec_()

  def on_pushBack_pressed(self):
    self.answer = "bacl"
    self.close()

  def on_pushYes_pressed(self):
    self.answer = "yes"
    self.close()

  def on_pushNo_pressed(self):
    self.answer = "no"
    self.close()


if __name__ == '__main__':
  a = QtWidgets.QApplication(sys.argv)
  image_location = '/home/heinz/Dropbox/workspace/CAM-projects_ProMo/Ontology_Repository/Sandbox20/LaTeX'
  w = UI_ShowVariableEquation(["E_2", "E_13", "E_52", "E_33", "E_22"], image_location,["yes","back","no"])
  w.show()
  print(w.answer)
  sys.exit()
