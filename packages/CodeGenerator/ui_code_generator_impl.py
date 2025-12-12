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
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QSplitter,QSizePolicy
from PyQt5.QtGui import QFont, QTextCursor,QTextCharFormat,QColor

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


    self.ui.centralwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    splitter = self.ui.splitter
    splitter.setOrientation(QtCore.Qt.Vertical)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 1)


    # setup widgets for stout and sterr
    self.stdout_widget = self.ui.textStdout
    self.stderr_widget = self.ui.textStderr
    
    # Set size policies for text widgets
    self.stdout_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.stderr_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # Set minimum sizes to prevent widgets from becoming too small
    self.stdout_widget.setMinimumSize(100, 100)
    self.stderr_widget.setMinimumSize(100, 100)



    # Set monospace font for better readability
    fixed_font = QFont("Monospace")
    fixed_font.setStyleHint(QFont.TypeWriter)
    self.stdout_widget.setFont(fixed_font)
    self.stderr_widget.setFont(fixed_font)

    # Set different background colors for better distinction
    self.stderr_widget.setStyleSheet("background-color: #fff0f0;")  # Light red background for errors

    # Redirect stdout and stderr
    self.original_stdout = sys.stdout
    self.original_stderr = sys.stderr
    sys.stdout = self.StdoutWrapper(self, "stdout")
    sys.stderr = self.StdoutWrapper(self, "stderr")


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


  class StdoutWrapper:
    def __init__(self, parent, stream_type):
      self.parent = parent
      self.stream_type = stream_type
      self.buffer = ""

    def write(self, text):
      self.buffer += text
      if '\n' in text:
        self.flush()

    def flush(self):
      if not self.buffer.strip():
        self.buffer = ""
        return

      if self.stream_type == "stdout":
        widget = self.parent.stdout_widget
        color = "black"
      else:
        widget = self.parent.stderr_widget
        color = "red"

      cursor = widget.textCursor()
      cursor.movePosition(QTextCursor.End)

      # Create format with the appropriate color
      format = QTextCharFormat()
      format.setForeground(QColor(color))
      cursor.setCharFormat(format)

      # Insert the text
      cursor.insertText(self.buffer)

      # Auto-scroll
      widget.ensureCursorVisible()

      self.buffer = ""


  def closeEvent(self, event):
    # Restore original stdout/stderr
    sys.stdout = self.original_stdout
    sys.stderr = self.original_stderr
    event.accept()