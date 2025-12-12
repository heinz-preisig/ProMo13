#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Code generation facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2025. 12. 11"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "0.12"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

from CodeGenerator.code_generator import CodeGenerator
from CodeGenerator.ui_code_generator import Ui_CodeGenerator
from Common.common_resources import askForModelFileGivenOntologyLocation
from Common.common_resources import getOntologyName
from Common.resource_initialisation import DIRECTORIES
from Common.resources_icons import roundButton


class EditorError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg


class UiCodeGenerator(QMainWindow):
  """
  Main window for the code generation:
  """

  def __init__(self, task_name):
    """
    The editor has the structure generates MatLab code from an ontology.
    """

    # set up dialog window with new title
    # note:needs mousePressEvent and mouseMoveEvent

    QMainWindow.__init__(self)
    self.setWindowTitle("Task Factory")
    self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
    self.ui = Ui_CodeGenerator()
    self.ui.setupUi(self)

    # check if ontology repository exists
    try:
      assert os.path.exists(DIRECTORIES["ontology_repository"])
    except:
      print("directory %s does not exist" % DIRECTORIES["ontology_repository"])

    # get ontology
    ontology_name = getOntologyName(task=task_name)
    if not ontology_name:
      exit(-1)

    # setup buttons
    roundButton(self.ui.pushInfo, "info", tooltip="information")
    roundButton(self.ui.pushExit, "off", tooltip="exit")
    self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)

    model_library_location = DIRECTORIES["model_library_location"] % ontology_name

    model_name, status = askForModelFileGivenOntologyLocation(model_library_location,
                                                                   alternative=False,
                                                                   left=("reject", "reject", "show"),
                                                                   # centre=("new", "new model", "show"),
                                                                   right=("accept", "accept", "hide")
                                                                   )
    if not model_name:
      exit(-1)

    self.code_generator = CodeGenerator(ontology_name, model_name)
    self.code_generator.generate_code()

  def on_pushExit_pressed(self):
    self.close()

  def mousePressEvent(self, event):
    self.oldPos = event.globalPos()

  def mouseMoveEvent(self, event):
    delta = QtCore.QPoint(event.globalPos() - self.oldPos)
    self.move(self.x() + delta.x(), self.y() + delta.y())
    self.oldPos = event.globalPos()
