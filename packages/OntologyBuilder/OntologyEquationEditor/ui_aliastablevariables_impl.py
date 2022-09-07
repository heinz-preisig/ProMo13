"""
===============================================================================
 GUI resource -- handles the table for the variables
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2016. 08. 15"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.resource_initialisation import FILES
from Common.resources_icons import roundButton
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES
from OntologyBuilder.OntologyEquationEditor.ui_aliastable import Ui_AliasTable

MAX_HEIGHT = 800
MAX_WIDTH = 1000


class UI_AliasTableVariables(QtWidgets.QWidget):
  '''
  classdocs
  '''

  completed = QtCore.pyqtSignal(str)

  def __init__(self, variables, current_network):
    '''
    Constructor
    '''
    QtWidgets.QWidget.__init__(self)
    self.variables = variables  # all
    self.current_network = current_network
    self.variables_ID_list = self.variables.index_definition_networks_for_variable[self.current_network]
    self.languages = LANGUAGES['aliasing_modify']
    self.ui = Ui_AliasTable()
    self.ui.setupUi(self)
    self.setup()
    self.setWindowTitle("variable aliases")
    self.ui.tableWidget.itemChanged.connect(self.rename)
    self.show()

    roundButton(self.ui.pushFinished, "back", tooltip="go back")
    roundButton(self.ui.pushInfo, "info", tooltip="information")

  def setup(self):

    aliases = {}
    self.keep_IDs = {}
    # for i in range(len(self.variables_ID_list)):
    #   ID = self.variables_ID_list[i]
    for ID in self.variables_ID_list:
      aliases[ID] = self.variables[ID].aliases
    a = self.ui.tableWidget
    a.clear()
    a.setRowCount(0)
    item = QtWidgets.QTableWidgetItem()
    item.setText("label")
    a.setHorizontalHeaderItem(0, item)
    col = 0
    for l in self.languages:  # label columns with languages
      a.setColumnCount(col + 1)
      item = QtWidgets.QTableWidgetItem()
      item.setText(l)
      a.setHorizontalHeaderItem(col, item)
      col += 1
    for ID in aliases:  # fill in all variables' aliases
      row = a.rowCount()
      self.keep_IDs[row] = ID
      a.setRowCount(row + 1)
      item = QtWidgets.QTableWidgetItem()
      item.setText(self.variables[ID].label)  # str(ID))
      a.setVerticalHeaderItem(row, item)
      col = 0
      for l in self.languages:
        try:
          s = aliases[ID][l]
        except:
          s = self.variables[ID].label
        item = QtWidgets.QTableWidgetItem()
        item.setText(s)
        a.setItem(row, col, item)
        col += 1
    self.__resize()
    self.aliases = aliases

  def __resize(self):
    tab = self.ui.tableWidget
    # fitting window
    tab.resizeColumnsToContents()
    tab.resizeRowsToContents()
    t = self.__tabSizeHint()
    tab.resize(t)
    x = t.width() + tab.x() + 12
    y = tab.y() + tab.height() + 12
    s = QtCore.QSize(x, y)
    self.resize(s)

  def __tabSizeHint(self):
    tab = self.ui.tableWidget
    width = 0
    for i in range(tab.columnCount()):
      width += tab.columnWidth(i)

    width += tab.verticalHeader().sizeHint().width()
    width += tab.verticalScrollBar().sizeHint().width()
    width += tab.frameWidth() * 2
    if width > MAX_WIDTH:
      width += tab.verticalScrollBar().sizeHint().width()
    width -= 0  # NOTE: manual fix

    height = 0
    for i in range(tab.rowCount()):
      height += tab.rowHeight(i)
    height += tab.horizontalHeader().sizeHint().height()
    height += tab.frameWidth() * 2
    if height > MAX_HEIGHT:
      height += tab.horizontalScrollBar().sizeHint().height()

    return QtCore.QSize(width, min(height, MAX_HEIGHT))

  def rename(self, item):
    language = self.languages[int(item.column())]
    row = int(item.row())
    ID = self.keep_IDs[row]
    # self.variables[ID].aliases[language] = str(item.text())
    self.variables.changeVariableAlias(ID, language, str(item.text()))
    self.__resize()

  def on_pushInfo_pressed(self):
    msg_popup = UI_FileDisplayWindow(FILES["info_variable_alias_table"])
    msg_popup.exec_()

  def on_pushFinished_pressed(self):
    self.completed.emit("alias variables")
    self.close()
