
__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2023.01.03"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "11"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui

from Common.resource_initialisation import FILES
from Common.ui_show_variable_equation import Ui_Dialog


class UI_ShowVariableEquation(QtWidgets.QDialog):
  def __init__(self, v_ID, eq_list_ID):
    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)


    self.v_ID = v_ID
    self.eq_list_ID = eq_list_ID

    fileLocation = '/home/heinz/Dropbox/workspace/CAM-projects_ProMo/Ontology_Repository/%s/LaTeX/%s.png' #FILES["latex_img"]
    V_file = fileLocation%("Sandbox20",v_ID)

    Vpixmap = QtGui.QPixmap()
    Vpixmap.load(V_file)
    sVpixmap = Vpixmap.scaledToHeight(20, mode=1) #pyqt bug
    self.ui.picture_variable.setPixmap(sVpixmap)

    # self.ui.label_variable1 = QtWidgets.QLabel(self)
    # self.ui.label_variable1.setGeometry(QtCore.QRect(150, 210, 541, 51))
    # self.ui.label_variable1.setObjectName("label_variable")
    # self.ui.label_variable1.setText("gugus")

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
    count = 0
    for eqID in eq_list_ID:
      E_file = fileLocation%("Sandbox20",eqID)
      Epixmap = QtGui.QPixmap()
      Epixmap.load(E_file)
      sEpixmap = Epixmap.scaledToHeight(20, mode=1)  # pyqt bug
      epic[count].setPixmap(sEpixmap)
      elabel[count].setText(eqID)
      count += 1

    for c in range(count,4):
      print(c)
      epic[c].hide()
      elabel[c].hide()







if __name__ == '__main__':
  a = QtWidgets.QApplication(sys.argv)
  w = UI_ShowVariableEquation("V_1",["E_2", "E_13"])
  w.show()
  a.exec_()
  sys.exit()