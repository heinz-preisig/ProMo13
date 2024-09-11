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
from Common.ui_show_variable_equation import Ui_Dialog

LIMIT = 4
HEIGHT = 25
FACTOR = 0.5


class UI_ShowVariableEquation(QtWidgets.QDialog):
  def __init__(self, eq_list_ID, image_location):
    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)

    roundButton(self.ui.pushButtonExit, "exit", "exit")
    # this will hide the title bar
    self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

    self.eq_list_ID = eq_list_ID
    if len(eq_list_ID) == 0:
      makeMessageBox("variable has no equations", buttons=["OK"])
      self.close()

    else:
      elabel = [self.ui.label_equation_0,
                self.ui.label_equation_1,
                self.ui.label_equation_2,
                self.ui.label_equation_3,
                ]
      epic = [self.ui.picture_equation_0,
              self.ui.picture_equation_1,
              self.ui.picture_equation_2,
              self.ui.picture_equation_3,
              ]

      if len(eq_list_ID) > LIMIT:
        makeMessageBox(message="warning -- there are more than 4 equations", buttons=["OK"])
      count = 0
      for eqID in eq_list_ID:
        E_file = str(os.path.join(image_location, "%s.png" % eqID))
        Epixmap = QtGui.QPixmap()
        Epixmap.load(E_file)
        # print("size %s"%eqID,Epixmap.size() )
        size = FACTOR * Epixmap.size()
        sEpixmap = Epixmap.scaled(size, transformMode=0)
        epic[count].setPixmap(sEpixmap)
        elabel[count].setText(eqID)
        count += 1
        if count == LIMIT:
          break

      for c in range(count, 4):
        # print(c)
        epic[c].hide()
        elabel[c].hide()

      self.exec_()

  def on_pushButtonExit_pressed(self):
    self.close()


if __name__ == '__main__':
  a = QtWidgets.QApplication(sys.argv)
  image_location = '/home/heinz/Dropbox/workspace/CAM-projects_ProMo/Ontology_Repository/processes_HAP_structure_testing/LaTeX'
  w = UI_ShowVariableEquation(["E_121", "E_13", "E_52", "E_33"], image_location)
  w.show()
  # a.exec_()
  sys.exit()
