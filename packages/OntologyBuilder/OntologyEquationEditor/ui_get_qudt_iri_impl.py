"""
===============================================================================
 ProMo utility for defining variable's IRIs from either qudt or private ProMo
===============================================================================
On window close the getSelection returns None,None
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2023. 02. 17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import webbrowser

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from Common.pop_up_message_box import makeMessageBox
from Common.resources_icons import roundButton
from OntologyBuilder.OntologyEquationEditor.qudt_fetcher_backend import *
from OntologyBuilder.OntologyEquationEditor.ui_qudt_iri_fetcher_dialog import Ui_Dialog

MAX_HEIGHT = 800
MAX_WIDTH = 1000


class UI_QUDTFetch_IRI(QtWidgets.QDialog):
  '''
  classdoc
  '''

  selected = QtCore.pyqtSignal(str)

  def __init__(self, label, iri=None):
    '''
    Constructor
    '''

    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    self.original_terms = self.setup()
    self.makeTable(self.original_terms)
    self.setWindowTitle("QUDT interface")
    self.show()

    self.ui.tableWidget.itemClicked.connect(self.on_tableItem_clicked)
    self.ui.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
    regex = QtCore.QRegExp("[A-Z-a-z_\-]*")
    reg = QtGui.QRegExpValidator(regex)
    self.ui.lineEdit.setValidator(reg)
    self.ui.label.setText(label)
    self.label = label
    self.iri = iri

    buttons = {
            self.ui.push_1: ["accept", "accept choice and close", True],
            self.ui.push_2: ["info", "show explanation", True],
            self.ui.push_3: ["plus", "show in web browser", True],
            self.ui.push_4: ["IRI", "define a new ProMo IRI", False],
            }

    for w in buttons:
      if buttons[w] != []:
        what, tooltip, hide = buttons[w]
        roundButton(w, what, tooltip)
        if hide:
          w.hide()
      else:
        w.hide()

    self.new_iri = False
    self.back = False
    self.edit_mode = "define_iri"
    self.selection = None

  def setup(self):
    terms = loadListOfTerms("quantitykind")
    return terms

  def makeTable(self, terms):

    table = self.ui.tableWidget
    row = -2
    col = 1
    table.setColumnCount(col)

    item = QtWidgets.QTableWidgetItem()
    item.setText("term")
    table.setHorizontalHeaderLabels(["term"])
    table.setRowCount(len(terms))
    for t in terms:
      row += 1
      # print("gugus"),
      item = QtWidgets.QTableWidgetItem()
      item.setText(t)
      # tt = item.text()
      # print(t,tt,row,col)
      table.setItem(row, 1, item)
      # if row ==10:
      #   break

    self.__resize()
    self.terms = terms

  def __resize(self):
    """
    do not forget to set a minimal size of the window widget
    """
    tab = self.ui.tableWidget
    # fitting window
    tab.resizeColumnsToContents()
    tab.resizeRowsToContents()
    t = self.__tabSizeHint()
    tab.resize(t)
    x = t.width() + tab.x() + 12 + 20
    y = tab.y() + tab.height() + 12 + 20
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

  def on_tableItem_clicked(self, item):
    print("item clicked", item.row(), item.column())
    row = item.row()
    print("term :", self.terms[row])
    self.selection = self.terms[row]

    text = getQuantityKindItemInfo(self.selection)
    self.selections_text = text
    # enable wiki button if link exists
    if "wiki_0" in text.keys():
      self.ui.push_3.show()
      s, p, o = text["wiki_0"]
      self.wiki = o
      self.ui.push_3.show()
    else:
      self.ui.push_3.hide()
    self.ui.push_1.show()
    self.ui.push_2.show()

  def on_lineEdit_textChanged(self, text):
    """
    two modes of operation:
    reducing table:
      reduces the table as the text changes
      if the text does not exist, it will not change in the window.
    defining a new term
    """
    if self.edit_mode == "edit_iri":
      self.selection = text
      return
    print("check ", text)
    self.ui.push_2.hide()
    self.ui.push_3.hide()
    if not self.new_iri:
      reduce_terms = self.apply_filter(str(text).lower())
      if len(reduce_terms) > 0:
        self.makeTable(reduce_terms)
        self.back = False
      else:
        if not self.back:
          self.ui.lineEdit.backspace()
          self.back = True
        else:
          self.back = False
        # self.makeTable(self.original_terms)
    else:
      self.selection = text
      self.ui.push_1.show()

  def getSelection(self):
    if not self.selection:
      return None,None
    if self.new_iri:
      prefix = "promo"
    else:
      prefix = "qudt"
    iri = "%s:%s" % (prefix, self.selection.split(":")[-1])
    return iri, self.new_iri

  def on_push_1_pressed(self):  # accept
    term = self.selection
    print("accept:", term)
    self.close()
    return self.selection, self.new_iri

  def on_push_2_pressed(self):  # info button
    text = self.selections_text
    # enable info button
    s = ""
    for i in text:
      _s, p, o = text[i]
      s = s + "\n" + " %s:" % i + "%s \n" % o
    msg_box = makeMessageBox(buttons=["OK"], message=str(s))

  def on_push_3_pressed(self):  # open info in browser if it exists
    webbrowser.open(self.wiki)

  def on_push_4_pressed(self):  # make a new iri
    self.edit_mode = "edit_iri"
    self.ui.tableWidget.hide()
    self.ui.lineEdit.setText(self.iri)
    self.ui.push_1.show()
    self.ui.push_2.hide()
    self.ui.push_3.hide()
    self.new_iri = True
    self.selection = self.iri
    pass

  def apply_filter(self, filter):
    """
    case insensitive search
    """
    reduced_terms = []
    for t in self.original_terms:
      if filter.lower() in t.lower():
        reduced_terms.append(t)
    return reduced_terms


if __name__ == '__main__':  # run from test or task
  import os
  import sys

  root = os.path.abspath(os.path.join(".."))
  sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])

  QtCore.pyqtRemoveInputHook()
  a = QtWidgets.QApplication(sys.argv)

  icon_f = "task_model_composer.svg"
  icon = os.path.join(os.path.abspath("../packages/Common/icons"), icon_f)

  a.setWindowIcon(QtGui.QIcon(icon))

  # TODO: implement stdout and stderr output as command-line arguments

  w = UI_QUDTFetch_IRI()

  w.move(QtCore.QPoint(100, 100))

  w.show()
  a.exec()
