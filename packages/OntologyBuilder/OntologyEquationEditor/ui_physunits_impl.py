#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility  -- the units dialogue
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2010. 07. 22"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from OntologyBuilder.OntologyEquationEditor.ui_physunits import Ui_PysUnitsDialog


class UI_PhysUnitsDialog(QtWidgets.QDialog):
  '''
  dialog for a variable
  '''

  finished = QtCore.pyqtSignal()

  def __init__(self, title):
    '''
    constructs a dialog window based on QDialog
    @param title:     title string: indicates the tree's nature
    @param physVar: physical variable
    '''
    self.title = title
    self.physvar = None

    # set up dialog window with new title
    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_PysUnitsDialog()
    self.ui.setupUi(self)
    # self.__initSpinBoxes()
    self.physvar = None

  # def __initSpinBoxes(self):
  def setUp(self, physVar):
    self.setWindowTitle('edit %s for %s with symbol %s'
                        % (self.title, physVar.doc, physVar.label))
    self.physvar = physVar
    v = self.physvar.units  # getUnits()
    print(v.time)
    self.ui.spinBoxTime.setValue(v.time)  # int( v['time'].number.number ) )
    self.ui.spinBoxLength.setValue(v.length)  # v['length'].number.number )
    self.ui.spinBoxAmount.setValue(v.amount)  # v['amount'].number.number )
    self.ui.spinBoxMass.setValue(v.mass)  # v['mass'].number.number )
    self.ui.spinBoxTemperature.setValue(v.temperature)
    self.ui.spinBoxCurrent.setValue(v.current)  # v['current'].number.number )
    self.ui.spinBoxLight.setValue(v.light)  # v['light'].number.number )

  @QtCore.pyqtSlot(int)
  def on_spinBoxTime_valueChanged(self, number):
    # LOGGER.info('time: %s' % number)
    self.physvar.units.time = number  # setTime( int( number ) )

  @QtCore.pyqtSlot(int)
  def on_spinBoxLength_valueChanged(self, number):
    # LOGGER.info('length: %s' % number)
    self.physvar.units.length = number  # setLength( int( number ) )

  @QtCore.pyqtSlot(int)
  def on_spinBoxAmount_valueChanged(self, number):
    # LOGGER.info('amount: %s' % number)
    self.physvar.units.amount = number  # setAmount( int( number ) )

  @QtCore.pyqtSlot(int)
  def on_spinBoxMass_valueChanged(self, number):
    # LOGGER.info('mass: %s' % number)
    self.physvar.units.mass = number  # setMass( int( number ) )

  @QtCore.pyqtSlot(int)
  def on_spinBoxTemperature_valueChanged(self, number):
    # LOGGER.info('temperature: %s' % number)
    self.physvar.units.temperature = number  # setTemperature( int( number ) )

  @QtCore.pyqtSlot(int)
  def on_spinBoxCurrent_valueChanged(self, number):
    # LOGGER.info('current: %s' % number)
    self.physvar.units.current = number  # setCurrent( int( number ) )

  @QtCore.pyqtSlot(int)
  def on_spinBoxTime_valueLight(self, number):
    # LOGGER.info('time: %s' % number)
    self.physvar.light = number  # setLight( int( number ) )

  def on_pushOK_pressed(self):
    self.finished.emit()
    self.hide()
