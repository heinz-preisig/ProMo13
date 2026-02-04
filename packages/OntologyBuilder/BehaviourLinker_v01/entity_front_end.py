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
from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor


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
        roundButton(self.ui.pushDeleteEntity, "delete", tooltip="delete entity")
        roundButton(self.ui.pushAccept, "accept", tooltip="accept")
        roundButton(self.ui.pushCancel, "cancel", tooltip="cancel")
        #
        #
        self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)
        
        # Add status label to the grid layout since verticalLayout_2 doesn't exist
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { color: gray; font-style: italic; margin: 5px; }")
        # Add to the bottom of the grid layout (row 7, spanning all columns)
        self.ui.gridLayout.addWidget(self.status_label, 7, 0, 1, 3)

        self.changed = False

    def set_ontology_container(self, ontology_container):
        """Set the ontology container for behavior association"""
        self.ontology_container = ontology_container

    def set_selected_entity_type(self, entity_type_data): #TODO: we may not need this one.
        """Set the selected entity type from the main tree"""
        self.selected_entity_type = entity_type_data
        print(f"EntityEditorFrontEnd received selected entity type: {self.selected_entity_type}")
        
        # Update the UI to show the selected entity type
        if self.selected_entity_type:
            network = self.selected_entity_type.get("network")
            category = self.selected_entity_type.get("category") 
            entity_type = self.selected_entity_type.get("entity type")
            name = self.selected_entity_type.get("name")  # This will be None for entity types, filled for instances
            
            if name:
                # An entity instance was selected - we're in edit mode
                selection_text = f"Editing: {network}.{category}.{entity_type}.{name}"
                self.status_label.setText(selection_text)
                self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; margin: 5px; }")
                # TODO: Load entity data and populate the form fields
            else:
                # An entity type was selected - we're in create mode
                selection_text = f"Creating: {network}.{category}.{entity_type}"
                self.status_label.setText(selection_text)
                self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; margin: 5px; }")

    def on_pushAddVariable_pressed(self):
        """Request behavior association editor launch from backend"""
        if not hasattr(self, 'ontology_container'):
            makeMessageBox("Ontology container not set")
            return
        
        # Send request to backend to launch association editor
        message = {
            "event": "launch_behavior_association_editor",
            "ontology_container": self.ontology_container
        }
        self.message.emit(message)

# ======================= window controls ==========================



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
        self.status_label.setText("modified")

    def markSaved(self):
        global changed
        changed = False
        self.signalButton.changeIcon("LED_green")
        self.status_label.setText("up to date")

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