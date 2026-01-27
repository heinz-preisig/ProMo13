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

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from Common.resources_icons import roundButton
from OntologyBuilder.BehaviourLinker_v01.UIs.entity_changes import Ui_entity_changes
from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox


class EntityEditorFrontEnd(QtWidgets.QDialog):
    """
     make new and edit entity instances

    """
    message = pyqtSignal(dict)

    # setting up GUI --------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.ui = Ui_entity_changes()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)


        roundButton(self.ui.pushAddVariable, "new", tooltip="new variable")
        roundButton(self.ui.pushEditVariable, "edit", tooltip="edit variable")
        roundButton(self.ui.pushDeleteVariable, "delete", tooltip="delete variable")
        roundButton(self.ui.pushAccept, "accept", tooltip="accept")
        roundButton(self.ui.pushCancel, "cancel", tooltip="cancel")
        #
        roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
        roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
        roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)
        #
        self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)

        self.changed = False



# ======================= window controls ==========================


        # enable moving the window --https://www.youtube.com/watch?v=R4jfg9mP_zo&t=152s
    def on_pushMinimise_pressed(self):
        self.showMinimized()

    def on_pushMaximise_pressed(self):
        self.showMaximized()

    def on_pushNormal_pressed(self):
        self.showNormal()

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