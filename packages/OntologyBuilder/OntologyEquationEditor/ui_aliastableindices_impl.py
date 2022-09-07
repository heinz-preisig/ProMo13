"""
===============================================================================
 GUI resource -- handles the table for the indices
===============================================================================

Major change in that only a symbol is set for each base index set
matlab was chosen as being the root symbol container
The other aliases are generated via compilation.

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 04. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

MAX_HEIGHT = 800
MAX_WIDTH = 1000

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.resource_initialisation import FILES
from Common.resources_icons import roundButton
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyBuilder.OntologyEquationEditor.resources import CODE
from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES
from OntologyBuilder.OntologyEquationEditor.resources import renderIndexListFromGlobalIDToInternal
from OntologyBuilder.OntologyEquationEditor.ui_aliastable import Ui_AliasTable


class UI_AliasTableIndices(QtWidgets.QWidget):
  '''
  classdocs
  '''

  completed = QtCore.pyqtSignal(str)

  def __init__(self, indices):
    '''
    Constructor
    '''
    QtWidgets.QWidget.__init__(self)
    self.indices = indices
    self.languages = LANGUAGES['aliasing']
    self.ui = Ui_AliasTable()
    self.ui.setupUi(self)
    self.setup()
    self.setWindowTitle("indices aliases")
    self.ui.tableWidget.itemChanged.connect(self.rename)

    roundButton(self.ui.pushFinished, "back", tooltip="go back")
    roundButton(self.ui.pushInfo, "info", tooltip="information")

  def setup(self):

    a = self.ui.tableWidget
    a.clear()
    a.setRowCount(0)
    item = QtWidgets.QTableWidgetItem()
    item.setText("label")
    a.setHorizontalHeaderItem(0, item)
    col = 0
    a.setColumnCount(col + 1)
    item = QtWidgets.QTableWidgetItem()
    item.setText("label")
    a.setHorizontalHeaderItem(col, item)

    self.keep_symbol = {}
    for symbol in self.indices:
      if self.indices[symbol]["type"] == "index":
        row = a.rowCount()
        a.setRowCount(row + 1)
        self.keep_symbol[row] = symbol  # self.indices[symbol]["label"]  # not row+1 !
        item = QtWidgets.QTableWidgetItem()
        item.setText(str(symbol))
        a.setVerticalHeaderItem(row, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(self.indices[symbol]["aliases"][LANGUAGES["internal_code"]])
        a.setItem(row, col, item)
    self.__resize()

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
    ind_ID = self.keep_symbol[item.row()]
    label = str(item.text())
    # self.indices[ind_ID]["label"] = label
    for language in LANGUAGES["aliasing"]:
      if language == "global_ID":
        s = CODE[language]["index"] % ind_ID
      else:
        s = label
      self.indices[ind_ID]["aliases"][language] = s

    for ind_ID in self.indices:
      if self.indices[ind_ID]["type"] == "block_index":
        for language in LANGUAGES["aliasing"]:
          if language != "global_ID":
            [outer, inner] = self.indices[ind_ID]["indices"]
            rendered_outer = renderIndexListFromGlobalIDToInternal([outer], self.indices).strip()
            rendered_inner = renderIndexListFromGlobalIDToInternal([inner], self.indices).strip()
            alias = CODE[language]["block_index"] % (rendered_outer, rendered_inner)
            self.indices[ind_ID]["aliases"][language] = alias
    # self.indices.compile()
    self.__resize()

  def on_pushInfo_pressed(self):
    msg_popup = UI_FileDisplayWindow(FILES["info_index_alias_table"])
    msg_popup.exec_()

  def on_pushFinished_pressed(self):
    self.completed.emit("alias indices")
    self.hide()
