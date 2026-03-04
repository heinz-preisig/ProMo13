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


# Error logging utility
def log_error(method_name: str, error: Exception, context: str = ""):
    """Log error with method name and context for debugging"""
    error_msg = f"ERROR in {method_name}"
    if context:
        error_msg += f" ({context})"
    error_msg += f": {str(error)}"
    print(error_msg)  # Keep console output for debugging


# Global variable to track if changes have been made
changed = False


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
        roundButton(self.ui.pushEdit, "edit", tooltip="edit instance")
        roundButton(self.ui.pushDelete, "delete", tooltip="delete instance")
        roundButton(self.ui.pushSave, "save", tooltip="save data")
        roundButton(self.ui.pushExit, "off", tooltip="exit task")

        roundButton(self.ui.pushMinimise, "min_view", tooltip="minimise", mysize=35)
        roundButton(self.ui.pushMaximise, "max_view", tooltip="maximise", mysize=35)
        roundButton(self.ui.pushNormal, "normal_view", tooltip="normal", mysize=35)

        self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)
        self.interfaceComponents()

        # Connect button signals explicitly
        self.ui.pushDelete.clicked.connect(self.on_pushDelete_pressed)
        self.ui.pushEdit.clicked.connect(self.on_pushEdit_pressed)
        
        # Connect double-click signal for tree widget
        self.ui.tree_entities.doubleClicked.connect(self.on_tree_entities_double_clicked)

        # Add statusbar since the UI doesn't have one but this is a QMainWindow
        self.statusBar().showMessage("Ready")

    def send_message(self, message):
        # print("sending message", message)
        self.message.emit(message)

    def process_main_backend_message(self, message):
        # print("front  end got message", message)
        event = message.get("event")

        # update interface
        gui = message.get("interface", None)
        self.__gui_view(gui)

        # actions
        if event == "make_tree":
            data = message.get("data")
            self.__make_tree(data)
        elif event == "mark_changed":
            # Mark as changed - red LED and show save button
            self.markChanged()
        elif event == "save":
            # Handle save event - mark as saved (green LED, hide save button)
            self.markSaved()

    # ================== interface handling =========================
    def __gui_view(self, gui):
        pass
        buttons = self.gui_objects["buttons"]
        for button in buttons:
            buttons[button].setVisible(gui["buttons"][button])
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
        # Extract networks from node_entity_types data

        network_items = {}

        # Build tree structure
        for net in sorted(networks):
            # Building network
            # Create network item
            net_item = QtGui.QStandardItem(net)
            net_item.setData(('network', net), QtCore.Qt.UserRole + 1)
            net_item.setData(net, QtCore.Qt.UserRole + 2)
            net_item.setForeground(NETWORK_COLOR)
            tree_model.appendRow(net_item)
            network_items[net] = net_item
            # Added network item

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

        # Tree built successfully

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
                # Get the full path
                path = []
                current = item
                while current is not None:
                    path.insert(0, current.text())
                    current = current.parent()
                if len(path) == 3:
                    network, category, entity_type = path
                    event = "selected_entity_type"
                elif len(path) == 4:
                    network, category, entity_type, name = path
                    # For instances, just select them and show edit/delete buttons
                    event = "edit"
                else:
                    makeMessageBox("please select an entity type or an instance", buttons=["OK"])
                    event = "failed"

                message = {
                        "event": event,
                        "data" : {
                                "network"    : network,
                                "category"   : category,
                                "entity type": entity_type,
                                "name"       : name
                                }
                        }
                # Sending entity selection
                self.send_message(message)

    def on_tree_entities_double_clicked(self, index):
        """Handle double-click on tree entities - directly open entity editor for entity instances"""
        try:
            if not index.isValid():
                return

            # Get the item from the index
            item = self.ui.tree_entities.model().itemFromIndex(index)
            if item is None:
                return

            # Get full path to determine if it's an entity instance
            path = []
            current = item
            while current is not None:
                path.insert(0, current.text())
                current = current.parent()

            # Only allow opening entity editor for entity instances (path length = 4)
            if len(path) != 4:
                return  # Silently ignore double-clicks on non-instances

            network, category, entity_type, name = path

            # Send selected_instance message to backend to launch entity editor
            message = {
                    "event": "selected_instance",
                    "data" : {
                            "network"    : network,
                            "category"   : category,
                            "entity type": entity_type,
                            "name"       : name
                            }
                    }
            self.send_message(message)

        except Exception as e:
            log_error("on_tree_entities_double_clicked", e, "handling double-click on tree entity")

    # ===============================================================

    # ============== buttons =========================================
    def on_pushNew_pressed(self):
        self.send_message({"event": "new"})

    def on_pushEdit_pressed(self):
        """Handle Edit button - open selected entity instance in edit mode"""
        try:
            # Get currently selected item in tree
            index = self.ui.tree_entities.currentIndex()
            if not index.isValid():
                makeMessageBox("Please select an entity instance to edit", buttons=["OK"])
                return

            # Get the item from the index
            item = self.ui.tree_entities.model().itemFromIndex(index)
            if item is None:
                makeMessageBox("Please select an entity instance to edit", buttons=["OK"])
                return

            # Get full path to determine if it's an entity instance
            path = []
            current = item
            while current is not None:
                path.insert(0, current.text())
                current = current.parent()

            # Only allow editing of entity instances (path length = 4)
            if len(path) != 4:
                makeMessageBox("Please select an entity instance to edit (not entity type)", buttons=["OK"])
                return

            network, category, entity_type, name = path

            # Send edit message to backend
            message = {
                    "event": "selected_instance",
                    "data" : {
                            "network"    : network,
                            "category"   : category,
                            "entity type": entity_type,
                            "name"       : name
                            }
                    }
            self.send_message(message)

        except Exception as e:
            log_error("on_pushEdit_pressed", e, "editing entity")
            makeMessageBox(f"Error editing entity: {str(e)}", buttons=["OK"])

    def on_pushDelete_pressed(self):
        """Handle Delete button - delete currently selected entity instance"""
        try:
            # Get currently selected item in tree
            index = self.ui.tree_entities.currentIndex()
            if not index.isValid():
                makeMessageBox("Please select an entity instance to delete", buttons=["OK"])
                return

            # Get the item from the index
            item = self.ui.tree_entities.model().itemFromIndex(index)
            if item is None:
                makeMessageBox("Please select an entity instance to delete", buttons=["OK"])
                return

            # Get full path to determine if it's an entity instance
            path = []
            current = item
            while current is not None:
                path.insert(0, current.text())
                current = current.parent()

            # Only allow deletion of entity instances (path length = 4)
            if len(path) != 4:
                makeMessageBox("Please select an entity instance to delete (not entity type)", buttons=["OK"])
                return

            network, category, entity_type, name = path

            # Confirm deletion
            choice = makeMessageBox(
                    message=f"Delete entity instance '{name}'?\n\nThis action cannot be undone.",
                    buttons=["YES", "NO"]
                    )

            if choice != "YES":
                return

            # Send delete message to backend
            message = {
                    "event": "delete_instance",
                    "data" : {
                            "network"    : network,
                            "category"   : category,
                            "entity type": entity_type,
                            "name"       : name
                            }
                    }
            self.send_message(message)

        except Exception as e:
            log_error("on_pushDelete_pressed", e, "deleting entity")
            makeMessageBox(f"Error deleting entity: {str(e)}", buttons=["OK"])

    def on_pushSave_pressed(self):
        """Handle Save button - mark as saved and update LED"""
        try:
            # Mark as saved - green LED and hide save button
            self.markSaved()

            # Send save confirmation to backend
            self.send_message({"event": "save"})

        except Exception as e:
            log_error("on_pushSave_pressed", e, "saving changes")
            makeMessageBox(f"Error saving: {str(e)}", buttons=["OK"])

    def on_pushExit_pressed(self):
        self.closeMe()

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
                        "edit"  : self.ui.pushEdit,
                        "delete": self.ui.pushDelete,
                        "save"  : self.ui.pushSave,
                        "exit"  : self.ui.pushExit,
                        "tree"  : self.ui.tree_entities,
                        },
                "indicator": {
                        "LED": self.ui.LED,
                        },
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
        self.statusBar().showMessage("modified")

    def markSaved(self):
        global changed
        changed = False
        self.signalButton.changeIcon("LED_green")
        self.statusBar().showMessage("up to date")

    def closeMe(self):
        global changed
        if changed:
            dialog = makeMessageBox(
                    message="You have unsaved changes. Do you want to save before exiting?",
                    buttons=["YES", "NO", "cancel"]
                    )
            if dialog == "YES":
                self.on_pushSave_pressed()
                sys.exit()
            elif dialog == "NO":
                sys.exit()
            elif dialog == "cancel":
                return  # Don't exit
        else:
            sys.exit()
