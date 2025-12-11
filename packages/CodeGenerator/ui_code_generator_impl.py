#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
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

from Common.common_resources import askForModelFileGivenOntologyLocation
from Common.common_resources import getOntologyName
from Common.resource_initialisation import DIRECTORIES
from CodeGenerator.ui_code_generator import Ui_CodeGenerator
from CodeGenerator.code_generator import CodeGenerator

from Common.resources_icons import roundButton





class EditorError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg


class UiCodeGenerator(QMainWindow):
  """
  Main window for the ontology design:
  """

  def __init__(self):
    """
    The editor has  the structure of a wizard,  thus goes through several steps
    to define the ontology.
    - get the base ontology that provides the bootstrap procedure.
    - construct the index sets that are used in the definition of the different
      mathematical objects
    - start building the ontology by defining the state variables
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
    self.ontology_name = getOntologyName(task="task_ontology_equations")
    if not self.ontology_name:
      exit(-1)

    # setup buttons
    roundButton(self.ui.pushInfo, "info", tooltip="information")
    roundButton(self.ui.pushExit, "off", tooltip="exit")
    self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)


    self.model_library_location = DIRECTORIES["model_library_location"] % self.ontology_name

    self.model_name, status = askForModelFileGivenOntologyLocation(self.model_library_location,
                                                                   alternative=True,
                                                                   left=("reject", "reject", "show"),
                                                                   centre=("new", "new model", "show"),
                                                                   right=("accept", "accept", "hide")
                                                                   )

    self.code_generator = CodeGenerator(self.ontology_name, self.model_name)


    def on_pushExit_pressed(self):
      self.close()


