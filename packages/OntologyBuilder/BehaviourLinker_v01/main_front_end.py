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
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItemModel

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

        # roundButton(self.ui.pushNew, "new", tooltip="new instance")
        # roundButton(self.ui.pushEdit, "edit", tooltip="edit instance")
        # roundButton(self.ui.pushDelete, "delete", tooltip="delete instance")
        roundButton(self.ui.pushSave, "save", tooltip="save data")
        roundButton(self.ui.pushExit, "off", tooltip="exit task")

        roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
        roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
        roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)

        self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)
        self.interfaceComponents()

        # Add statusbar since the UI doesn't have one but this is a QMainWindow
        self.statusBar().showMessage("Ready")

        self.changed = False

    def send_message(self, message):
        print("sending message", message)
        self.message.emit(message)

    def process_main_backend_message(self, message):
        print("front  end got message", message)
        event = message.get("event")

        # update interface
        gui = message.get("interface", None)
        self.__gui_view(gui)

        # actions
        if event == "make_tree":
            data = message.get("data")
            self.__make_tree(data)

    # ================== interface handling =========================
    def __gui_view(self, gui):
        pass
        buttons = self.gui_objects["buttons"]
        # lists = self.gui_objects["lists"]
        for button in buttons:
            # print("obj", button)
            buttons[button].setVisible(gui["buttons"][button])
        # for list in lists:
        #     if gui["lists"][list]:
        #        lists[list].reset()

        pass

    def __make_tree(self, data):
        """Build the entity tree with colors similar to HAP version."""
        # print(f"__make_tree called with data: {data}")
        if not data:
            print("No data received, returning")
            return

        # Extract node_entity_types and all_entities from the new data structure
        node_entity_types = data.get("node_entity_types", {})
        all_entities = data.get("all_entities", {})

        # Define colors (same as HAP version)
        NETWORK_COLOR = QtGui.QColor(255, 0, 0)  # Red for networks
        CATEGORY_COLOR = QtGui.QColor(0, 0, 255)  # Blue for node/arc
        TYPE_COLOR = QtGui.QColor(0, 128, 0)  # Green for entity types
        ENTITY_COLOR = QtGui.QColor(0, 0, 0)  # Black for instantiated entities

        # Clear existing tree - reset the model
        tree_model = QStandardItemModel()
        self.ui.tree_entities.setModel(tree_model)
        # print("Created new tree model")

        # Extract networks from node_entity_types data
        networks = set(node_entity_types.keys())
        # print(f"Extracted networks: {networks}")

        network_items = {}

        # Build tree structure
        for net in sorted(networks):
            # print(f"Building network: {net}")
            # Create network item
            net_item = QtGui.QStandardItem(net)
            net_item.setData(('network', net), QtCore.Qt.UserRole + 1)
            net_item.setData(net, QtCore.Qt.UserRole + 2)
            net_item.setForeground(NETWORK_COLOR)
            tree_model.appendRow(net_item)
            network_items[net] = net_item
            # print(f"Added network item: {net}")

            # Create categories (node, arc)
            for category in ['node', 'arc']:
                cat_item = QtGui.QStandardItem(category)
                cat_item.setData(('category', net, category), QtCore.Qt.UserRole + 1)
                cat_item.setData(f"{net}.{category}", QtCore.Qt.UserRole + 2)
                cat_item.setForeground(CATEGORY_COLOR)
                net_item.appendRow(cat_item)

                # Get entity types for this network from the data
                entity_types = node_entity_types.get(net, [])
                # print(f"Entity types for {net}.{category}: {entity_types}")

                # Create type items
                for entity_type in sorted(entity_types):
                    type_item = QtGui.QStandardItem(entity_type)
                    type_item.setData(('entity_type', net, category, entity_type), QtCore.Qt.UserRole + 1)
                    type_item.setData(entity_type, QtCore.Qt.UserRole + 2)
                    type_item.setForeground(TYPE_COLOR)
                    cat_item.appendRow(type_item)

                    # Add entities for this entity type
                    entities_for_type = []
                    for entity_id, entity_obj in all_entities.items():
                        # Check if entity matches this network, category, and type
                        if ">" not in entity_id:
                            parts = entity_id.split('.')
                            if len(parts) == 4:
                                entity_net, entity_cat, entity_type_name, entity_name = parts
                            else:
                                # makeMessageBox("id failed ?", buttons=["OK"])
                                print(">>>>>>>>>>>> unpacking of entity_id failed", parts)

                                pass

                            # print("\n ------------------", entity_name)
                            # print(net, "--", entity_net,"--",  net == entity_net)
                            # print(category, "--",entity_cat, "--", category ==  entity_cat)
                            # print(entity_type,"--", entity_type_name, entity_type == entity_type_name)

                            if (entity_net == net and
                                    entity_cat == category and
                                    entity_type_name == entity_type):
                                entities_for_type.append((entity_name, entity_obj))

                    # Sort entities by name
                    entities_for_type.sort(key=lambda x: x[0])

                    # Add entity items or placeholder
                    if entities_for_type:
                        for entity_name, entity_obj in entities_for_type:
                            entity_item = QtGui.QStandardItem(entity_name)
                            entity_item.setData(('entity', net, category, entity_type, entity_name),
                                                QtCore.Qt.UserRole + 1)
                            entity_item.setData(entity_name, QtCore.Qt.UserRole + 2)
                            entity_item.setData(entity_obj, QtCore.Qt.UserRole + 3)  # Store entity object
                            entity_item.setForeground(ENTITY_COLOR)
                            type_item.appendRow(entity_item)
                    # else:
                    #     # Add placeholder for entities (currently no entities loaded)
                    #     placeholder_item = QtGui.QStandardItem("(no entities)")
                    #     placeholder_item.setData(('placeholder', net, category, entity_type), QtCore.Qt.UserRole + 1)
                    #     placeholder_item.setForeground(ENTITY_COLOR)
                    #     type_item.appendRow(placeholder_item)

        # print(f"Tree built with {len(networks)} networks and colored structure")
        # print(f"Tree model has {tree_model.rowCount()} top-level items")

        # Make sure the tree view is properly configured
        self.ui.tree_entities.expandAll()
        self.ui.tree_entities.show()
        # print("Tree expanded and shown")

    def on_tree_entities_pressed(self):
        index = self.ui.tree_entities.currentIndex()
        if index.isValid():
            # Get the item from the index
            item = self.ui.tree_entities.model().itemFromIndex(index)
            network = None
            category = None
            entity_type = None
            name = None
            if item is not None:
                # Get the display text
                # text = item.text()
                # Get the item's data (type information)
                # item_data = item.data(QtCore.Qt.UserRole + 1)
                # Get the full path
                path = []
                current = item
                while current is not None:
                    path.insert(0, current.text())
                    current = current.parent()
                # full_path = ".".join(path)
                if len(path) == 3:
                    network, category, entity_type = path
                    event = "selected_entity_type"
                elif len(path) == 4:
                    network, category, entity_type, name = path
                    event = "selected_instance"
                else:
                    makeMessageBox("please select an entity type or an instance", buttons=["OK"])
                    event = "failed"

                # print(f"Clicked on: {text}")
                # print(f"Item type data: {item_data}")
                # print(f"Full path: {full_path}")
                # print(f"Row in parent: {index.row()}")
                message = {
                        "event": event,
                        "data" : {
                                "network"    : network,
                                "category"   : category,
                                "entity type": entity_type,
                                "name"       : name
                                }
                        }
                # print("network:", network, "   category:", category, "   entity type:", entity_type)
                # print(message)
                self.send_message(message)

    # ===============================================================

    # ============== buttons =========================================
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

    # ================ tree =========================================
    # def on_
    # ================ Window control ===============================

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
    def interfaceComponents(self):
        self.window_controls = {
                "maximise": self.ui.pushMaximise,
                "minimise": self.ui.pushMinimise,
                "normal"  : self.ui.pushNormal,
                }

        self.gui_objects = {
                "buttons"  : {
                        # "new"   : self.ui.pushNew,
                        # "edit"  : self.ui.pushEdit,
                        # "delete": self.ui.pushDelete,
                        "save": self.ui.pushSave,
                        "exit": self.ui.pushExit,
                        "tree": self.ui.tree_entities,
                        },
                "indicator": {
                        "LED": self.ui.LED,
                        },
                # "lists"    : {
                #         "list_equations"  : self.ui.list_equations,
                #         "list_integrators": self.ui.list_integrators,
                #         "list_input"      : self.ui.list_input,
                #         "list_output"     : self.ui.list_output,
                #         "list_instantiate": self.ui.list_instantiate,
                #         "list_pending"    : self.ui.list_pending,
                #         },
                "tree"     : self.ui.tree_entities,
                }

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
