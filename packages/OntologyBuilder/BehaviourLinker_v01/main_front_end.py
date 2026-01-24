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

import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from Common.resources_icons import roundButton
from OntologyBuilder.BehaviourLinker_v01.UIs.main import Ui_MainWindow
from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox


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




        # enable moving the window --https://www.youtube.com/watch?v=R4jfg9mP_zo&t=152s

    def mousePressEvent(self, event, QMouseEvent=None):
        self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event, QMouseEvent=None):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()

    def markChanged(self):
        global changed
        changed = True
        self.signalButton.changeIcon("LED_red")
        self.ui.statusbar.showMessage("modified")

    def on_pushExit_pressed(self):
        self.closeMe()

    def markSaved(self):
        global changed
        changed = False
        self.signalButton.changeIcon("LED_green")
        self.ui.statusbar.showMessage("up to date")

    def closeMe(self):

        if self.changed:
            dialog = makeMessageBox(message="save changes", buttons=["YES", "NO"])
            if dialog == "YES":
                self.on_pushOntologySave_pressed()
            elif dialog == "NO":
                pass
        else:
            pass
        sys.exit()
