#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
GUI for automata editor

Automata control the user interface of the ModelComposer
===============================================================================
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2026. 01. 23"
__license__ = "GPL planned -- until further notice for internal Bio4Fuel & MarketPlace use only"
__version__ = "12"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5.QtCore import  pyqtSignal
from PyQt5 import QtWidgets

from Common.resources_icons import roundButton
from OntologyBuilder.BehaviourLinker_v01.UIs.main import Ui_MainWindow
# from OntologyBuilder.BehaviourLinker_v01.main_back_end import BackEnd


class BehaviourLinkerFrontEnd(QtWidgets.QMainWindow):
    """
     assigns variables and equtions to entities generating an entity instance

    """
    message = pyqtSignal(dict)

    # setting up GUI --------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.ui.tabsBrickTrees.setTabVisible(1,False)

        roundButton(self.ui.pushNew, "new", tooltip="new instance")
        roundButton(self.ui.pushEdit, "edit", tooltip="edit instance")
        roundButton(self.ui.pushDelete, "delete", tooltip="delete instance")
        roundButton(self.ui.pushSave, "save", tooltip="save data")
        roundButton(self.ui.pushExit, "off", tooltip="exit task")

        roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
        roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
        roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)

        self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)

        self.changed = False

        # self.ontology_name = getOntologyName(task="task_ontology_equations")
        # if not self.ontology_name:
        #     exit(-1)

        # self.interfaceComponents()
        # self.backend = BackEnd(self)

        # Initialize with a start message
        # self.send_message({"event": "start"})
        # self.backend.processEvent(message)

        self.treetop = {}

    def send_message(self, message):
        print("sending message", message)
        self.message.emit(message)

    def process_message(self, message):
        print("front  end got message", message)

    def interfaceComponents(self):
        self.window_controls = {
                "maximise": self.ui.pushMaximise,
                "minimise": self.ui.pushMinimise,
                "normal"  : self.ui.pushNormal,
                }

        self.gui_objects = {
                "new"             : self.ui.pushNew,
                "edit"            : self.ui.pushEdit,
                "delete"          : self.ui.pushDelete,
                "save"            : self.ui.pushSave,
                "exit"            : self.ui.pushExit,
                "tree"            : self.ui.tree_entities,
                "LED"             : self.ui.LED,
                "list_equations"  : self.ui.list_equations,
                "list_integrators": self.ui.list_integrators,
                "list_input"      : self.ui.list_input,
                "list_output"     : self.ui.list_output,
                "list_instantiate": self.ui.list_instantiate,
                "list_pending"    : self.ui.list_pending,
                }

    def on_pushNew_pressed(self):
        self.send_message({"event": "new"})