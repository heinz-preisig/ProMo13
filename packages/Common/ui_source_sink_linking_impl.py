#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI resource -- select source and sink for interface
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2022. 01. 24"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"


from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.resources_icons import roundButton
from Common.ui_source_sink_linking import Ui_SourceSinkLinking
from Common.pop_up_message_box import makeMessageBox

from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES


class UI_SourceSinkLinking(QtWidgets.QDialog):
  '''
  selects from a list generating a new list, which can also re-arranged by moving elements up or down.
  '''

  newSelection = QtCore.pyqtSignal(list)
  selected = QtCore.pyqtSignal(list)
  delete_equ = QtCore.pyqtSignal(int, int)

  def __init__(self,
               left_nw : str,
               left_list: list,
               right_nw : str,
               right_list : list,
               equation_list: list, # list of triples (left_var_ID, right_var_ID, equ_ID)
               variables):
    '''
    plain constructor
    '''

    super().__init__()
    self.ui = Ui_SourceSinkLinking()
    self.ui.setupUi(self)
    self.show()
    roundButton(self.ui.pushAccept, "accept", "accept" )
    roundButton(self.ui.pushReset, "update", "reset lists" )
    roundButton(self.ui.pushExit, "exit", "exit" )
    roundButton(self.ui.pushDelete, "delete", "delete selected equation" )
    self.left_list = left_list
    self.right_list = right_list
    self.equation_list = equation_list
    self.variables = variables

    self.selectedSource = None
    self.selectedSink = None

    self.on_pushReset_pressed()
    self.ui.labelLeft.setText(left_nw)
    self.ui.labelRight.setText(right_nw)



  def on_pushReset_pressed(self):

    self.selectedSource = None
    self.selectedSink = None

    self.ui.listSource.clear()
    self.ui.listSink.clear()
    self.ui.listWidgetExisting.clear()

    self.left_index = []
    self. right_index = []
    self.delete_index = []

    for id in self.left_list:
      v = self.variables[id]
      v.language = LANGUAGES["internal_code"]
      text = str(v)
      self.ui.listSource.addItem(text)
      self.left_index.append(id)

    for id in self.right_list:
      v = self.variables[id]
      v.language = LANGUAGES["internal_code"]
      text = str(v)
      self.ui.listSink.addItem(text)
      self.right_index.append(id)

    for left_ID, right_ID, equ in self.equation_list:
      left_v = self.variables[int(left_ID)]
      left_v.language = LANGUAGES["internal_code"]
      right_v = self.variables[int(right_ID)]
      right_v.language = LANGUAGES["internal_code"]
      text = str(left_v)+ " := " + str(right_v)
      self.ui.listWidgetExisting.addItem(text)
      self.delete_index.append((equ,left_ID, right_ID))

    self.ui.pushAccept.hide()
    self.ui.pushDelete.hide()


  def on_listSource_itemClicked(self, item):
    row = self.ui.listSource.currentRow()
    text = item.text()
    selected_ID = self.left_index[row]
    self.selectedSource = selected_ID

    # print("debugging -- clicked left list", row, selected_ID, text)
    self.check()

  def on_listSink_itemClicked(self,item):
    row = self.ui.listSink.currentRow()
    text = item.text()
    selected_ID = self.right_index[row]
    self.selectedSink = selected_ID
    # print("debugging -- clicked right list", row, selected_ID, text)
    self.check()

  def check(self):
    if self.selectedSource and self.selectedSink:
      # print("debugging -- both are defined", self.selectedSource, self.selectedSink)
      source = self.variables[self.selectedSource]
      source.language = "internal_code"
      sink = self.variables[self.selectedSink]
      sink.language = "internal_code"
      source_units = self.variables[self.selectedSource].units
      sink_units = self.variables[self.selectedSink].units
      source_indexes = self.variables[self.selectedSource].index_structures
      sink_indexes = self.variables[self.selectedSink].index_structures
      # print("debugging -- source:", source, "units:", source_units, "indices:", source_indexes)
      # print("debugging -- sink  :", sink,  "units:", sink_units, "indices:", sink_indexes)

      for left_ID, right_ID, equ in self.equation_list:
        if (self.selectedSink == left_ID) and (self.selectedSource == right_ID) :
          msgbox = makeMessageBox("already defined", buttons=["OK"])
          self.ui.listSink.clearSelection()
          self.ui.listSource.clearSelection()
          return

      if (source_indexes == sink_indexes):
        if (source_units == sink_units):
          self.ui.pushAccept.show()
        else:
          msgbox = makeMessageBox("mismatch with units", buttons=["OK"])
      else:
        msgbox = makeMessageBox("mismatch with indices", buttons=["OK"])

  def on_listWidgetExisting_itemClicked(self, item):
    # pass
    row = self.ui.listWidgetExisting.currentRow()
    self.to_delete = row
    self.ui.pushDelete.show()

  def on_pushDelete_pressed(self):
    row = self.to_delete
    equ_to_delete, left_ID, right_ID = self.delete_index[row]
    self.delete_equ.emit(int(equ_to_delete), int(left_ID))
    print("debugging ")
    self.close()



  def on_pushExit_pressed(self):
    self.close()

  def on_pushAccept_pressed(self):
    self.selected.emit([self.selectedSource, self.selectedSink])
    self.close()







