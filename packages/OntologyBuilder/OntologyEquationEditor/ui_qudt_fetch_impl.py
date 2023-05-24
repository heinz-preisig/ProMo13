"""
===============================================================================
 GUI resource -- copies qudt to local and makes a reduced version with what
                 is used by ProMo
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2023. 02. 17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from OntologyBuilder.OntologyEquationEditor.qudt_fetcher_backend import *
# from Common.resource_initialisation import FILES
from Common.resources_icons import roundButton
# from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.OntologyEquationEditor.ui_qudt_fetch import Ui_QUDT_fetcher

MAX_HEIGHT = 800
MAX_WIDTH = 1000


class UI_QUDTFetch(QtWidgets.QWidget):
  '''
  Simple interface to fetch qudt information and store it locally
  '''

  completed = QtCore.pyqtSignal(str)

  def __init__(self):
    '''
    Constructor
    '''
    QtWidgets.QWidget.__init__(self)
    self.ui = Ui_QUDT_fetcher()
    self.ui.setupUi(self)
    self.setWindowTitle("QUDT interface")
    self.show()

    buttons = {
            self.ui.push_1: ["update", "update unit information"],
            self.ui.push_2: ["update", "update quantity kind information"],
            }

    for w in buttons:
      if buttons[w] != []:
        what,tooltip = buttons[w]
        # roundButton(w,what, tooltip)
        w.setToolTip(tooltip)
      else:
        w.hide()




  def on_push_1_pressed(self):
    print("debugging -- push_1 pressed")
    package = "updateQuantityKindInformation"
    error = False
    try:
      reply = receiver(package)
      print("reply:",reply)
    except:
      self.ui.push_1.setText("error quantity")
      error = True


    package = "updateUnitInformation"
    try:
      reply = receiver(package)
      print("reply:", reply)
      if not error:
        self.ui.push_1.hide()
    except:
      self.ui.push_1.setText("error units")

  def on_push_2_pressed(self):
    print("debugging -- push_2 pressed")
    package = "updateQuantityKindInformation"
    try:
      reply = receiver(package)
      print("reply:", reply)
      self.ui.push_2.hide()
    except:
      self.ui.push_2.setText("error units")
