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

    def on_pushEdit_pressed(self):
        print("edit pressed")

    def on_pushDelete_pressed(self):
        print("delete pressed")

    def on_pushSave_pressed(self):
        print("save pressed")

    def on_pushExit_pressed(self):
        print("exit pressed")
        self.closeMe()

 # ===============================================================

    # def _update_tree_model(self) -> None:
    #     """Update the tree model with the current state of entities."""
    #     # print("\n=== _update_tree_model called ===")
    #     # print(f"Current entities: {list(self.all_entities.keys())}")
    #
    #     # Define colors
    #     NETWORK_COLOR = QtGui.QColor(255, 0, 0)  # Red for networks
    #     CATEGORY_COLOR = QtGui.QColor(0, 0, 255)  # Blue for node/arc
    #     TYPE_COLOR = QtGui.QColor(0, 128, 0)  # Green for entity types
    #     ENTITY_COLOR = QtGui.QColor(0, 0, 0)  # Black for instantiated entities
    #
    #     self.entity_tree_model = self.ui.tree_entities
    #
    #     network_items = {}
    #     category_items = {}
    #     type_items = {}
    #
    #     self.entity_tree_model.clear()
    #     networks = set()
    #
    #     # Add networks from both entities and generated types
    #     # for entity_id in self.all_entities:
    #     #   parts = entity_id.split('.')
    #     #   if len(parts) >= 2:
    #     #     networks.add(parts[0])
    #     # networks.update(self.all_entity_types.keys())
    #
    #     for net in sorted(self.inter_networks):
    #         net_item = QtGui.QStandardItem(net)
    #         net_item.setData(('network', net), QtCore.Qt.UserRole + 1)
    #         net_item.setData(net, QtCore.Qt.UserRole + 2)
    #         net_item.setForeground(NETWORK_COLOR)
    #         self.entity_tree_model.appendRow(net_item)
    #         network_items[net] = net_item
    #
    #         for category in ['node', 'arc']:
    #
    #             category_key = f"{net}.{category}"
    #             cat_item = QtGui.QStandardItem(category)
    #             cat_item.setData(('category', net, category), QtCore.Qt.UserRole + 1)
    #             cat_item.setData(category_key, QtCore.Qt.UserRole + 2)
    #             cat_item.setForeground(CATEGORY_COLOR)
    #             # network_items[net].appendRow(cat_item)
    #
    #             net_item.appendRow(cat_item)
    #
    #             # Get all generated types for this network and category
    #             generated_types = set()
    #             if (net in self.all_entity_types and
    #                     category in self.all_entity_types[net]):
    #                 generated_types = set(self.all_entity_types[net][category])
    #
    #             # Create a dictionary to store type items
    #             type_items = {}
    #
    #             # First, create items for all generated types
    #             for entity_type in sorted(generated_types):
    #                 type_item = QtGui.QStandardItem(entity_type)
    #                 type_item.setData(('entity_type', net, category, entity_type), QtCore.Qt.UserRole + 1)
    #                 type_item.setData(entity_type, QtCore.Qt.UserRole + 2)
    #                 type_item.setForeground(TYPE_COLOR)
    #                 cat_item.appendRow(type_item)
    #                 type_items[entity_type] = type_item
    #
    #             # Then add all entities under their types
    #             for entity_id, entity_obj in self.all_entities.items():
    #                 if not entity_id.startswith(f"{net}.{category}."):
    #                     continue
    #
    #                 try:
    #                     [network, category, entity_type, entity_name] = entity_id.split('.')
    #
    #                     # Note: here one can adsjust the entity show name
    #                     display_name = entity_name
    #
    #                     # Create the item
    #                     item = QtGui.QStandardItem(display_name)
    #                     item.setData(entity_id, QtCore.Qt.UserRole + 1)  # entity_id for quick access
    #                     item.setData(display_name, QtCore.Qt.UserRole + 2)  # display text
    #                     item.setData(entity_obj, QtCore.Qt.UserRole + 3)  # entity object
    #                     item.setForeground(ENTITY_COLOR)
    #
    #                     # Ensure the type item exists
    #                     if entity_type not in type_items:
    #                         type_item = QtGui.QStandardItem(entity_type)
    #                         type_item.setData(('entity_type', net, category, entity_type), QtCore.Qt.UserRole + 1)
    #                         type_item.setData(entity_type, QtCore.Qt.UserRole + 2)
    #
    #                         cat_item.appendRow(type_item)
    #                         type_items[entity_type] = type_item
    #
    #                     # Add the entity to its type
    #                     type_items[entity_type].appendRow(item)
    #
    #                 except Exception as e:
    #                     print(f"Error processing entity here {entity_id}: {e}")
    #
    #     self.tree_changed.emit()


# ======================= window controls ==========================


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
