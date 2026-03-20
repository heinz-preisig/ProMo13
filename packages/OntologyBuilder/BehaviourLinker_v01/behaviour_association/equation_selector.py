#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Equation Selector Dialog for CAM12/ProMo
===============================================================================

This module provides a dialog for selecting equations that define variables,
with support for multiple equations and initialization options.
"""

import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.ontology_container import OntologyContainer
from Common.pop_up_message_box import makeMessageBox
from OntologyBuilder.BehaviourLinker_v01.UIs.equation_selector import Ui_Dialog
from OntologyBuilder.BehaviourLinker_v01.ui_settings import UISettings


from OntologyBuilder.BehaviourLinker_v01.error_logger import log_error


class EquationSelectorDialog(QtWidgets.QDialog, Ui_Dialog):
    """
    Dialog for selecting equations that define a selected variable.
    Supports multiple equations and initialization options.
    """

    def __init__(self, variable_data, ontology_container, parent=None):
        super().__init__(parent)

        # Setup the UI from the compiled .ui file
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        self.variable_data = variable_data
        self.ontology_container = ontology_container
        self.selected_equation = None
        self.use_initialization = False

        # Setup additional UI elements and connections
        self.setup_additional_ui()
        self.load_equations()

    def setup_additional_ui(self):
        """Setup additional UI elements and connections not in the UI file"""
        # Set window title
        self.setWindowTitle("Select Equation for Variable Definition")
        self.setModal(True)

        # Fix typo in UI file - equiation_list should be equation_list
        self.equation_list = self.equiation_list  # Map the typo to correct name

        # Setup equation list with enhanced display
        UISettings.configure_list_widget(self.equation_list, 'equation_selection')
        self.equation_list.setViewMode(QtWidgets.QListWidget.ListMode)

        # Connect signals
        self.equation_list.itemSelectionChanged.connect(self.on_equation_selection_changed)
        self.equation_radio.toggled.connect(self.on_method_changed)
        self.instationate_radio.toggled.connect(self.on_method_changed)
        self.pushAccept.clicked.connect(self.accept_selection)
        self.pushCancel.clicked.connect(self.reject)

        # Setup window controls
        self.setup_window_controls()

        # Set initial state
        self.equation_radio.setChecked(True)
        self.on_method_changed()

        # Apply styles
        # self.apply_styles()

    def setup_window_controls(self):
        """Setup window control buttons"""
        # Load icons for window controls if available

        # Try to load standard window control icons
        from Common.resources_icons import roundButton

        roundButton(self.pushAccept, "accept", tooltip="accept")
        roundButton(self.pushCancel, "cancel", tooltip="cancel")

    def load_equations(self):
        """Load available equations for the selected variable from the ontology container"""
        try:
            self.equation_list.clear()

            # Display variable info
            var_label = self.variable_data.get('label', 'Unknown Variable')
            var_id = self.variable_data.get('id', 'Unknown ID')

            self.variable_symbol.setText(f"Variable: {var_label}")
            self.variable_ID.setText(f"ID: {var_id}")

            # Get equations from variable data first (to get the list of equation IDs)
            variable_equations = self.variable_data.get('equations', {})

            if not variable_equations:
                # No equations available
                item = QtWidgets.QListWidgetItem("No equations available for this variable")
                item.setData(QtCore.Qt.UserRole, None)
                self.equation_list.addItem(item)
                self.equation_radio.setEnabled(False)
                self.instationate_radio.setChecked(True)
                self.on_method_changed()
                return

            # Get full equation data from ontology container's equation dictionary
            equation_dictionary = getattr(self.ontology_container, 'equation_dictionary', {})

            # Add each equation to the list
            for eq_id in variable_equations:

                # Get equation data from ontology container (has PNG file info)
                eq_data = equation_dictionary.get(eq_id, {})

                # Fall back to variable data if not found in dictionary
                if not eq_data:
                    eq_data = variable_equations[eq_id]
                else:
                    print(f"Debug: Found {eq_id} in equation dictionary")

                eq_label = eq_data.get('label', f'Equation_{eq_id}')
                eq_expression = eq_data.get('expression', 'No expression')
                # Try to get latex expression from variable data if not in equation dictionary
                if 'expression' not in eq_data and 'rhs' in variable_equations[eq_id]:
                    rhs_data = variable_equations[eq_id]['rhs']
                    eq_expression = rhs_data.get('latex', 'No expression')

                png_file = eq_data.get('png_file')

                item = QtWidgets.QListWidgetItem()
                item.setData(QtCore.Qt.UserRole, eq_id)

                # Add LaTeX PNG image if available
                png_loaded = False

                # First, try to use preloaded icon from ontology container
                if hasattr(self.ontology_container,
                           'equation_icons') and eq_id in self.ontology_container.equation_icons:
                    preloaded_icon = self.ontology_container.equation_icons[eq_id]
                    if not preloaded_icon.isNull():
                        item.setIcon(preloaded_icon)
                        item.setText(eq_label)  # Show only label when PNG works
                        png_loaded = True
                    else:
                        log_error("load_equation_icons", Exception(f"Preloaded icon is null"),
                                  f"preloaded icon from ontology container is null for {eq_id}")
                else:
                    log_error("load_equation_icons", Exception(f"No preloaded icon"),
                              f"no preloaded icon found in ontology container for {eq_id}")

                # Fallback: try to load PNG if no preloaded icon available
                if not png_loaded and png_file and os.path.exists(png_file):
                    try:
                        app = QtWidgets.QApplication.instance()
                        if app is None:
                            log_error("load_equation_icons", Exception(f"No QApplication instance"),
                                      f"skipping PNG for {eq_id}")
                        else:
                            icon_direct = QtGui.QIcon(png_file)
                            if not icon_direct.isNull():
                                item.setIcon(icon_direct)
                                item.setText(eq_label)
                                png_loaded = True
                            else:
                                log_error("load_equation_icons", Exception(f"Direct PNG loading failed for {eq_id}"),
                                          f"PNG loading failed for {eq_id}")
                    except TypeError as e:
                        log_error("load_equation_icons", e,
                                  f"TypeError loading PNG icon for {eq_id} - Qt GUI initialization issue")
                    except Exception as e:
                        error_msg = str(e)
                        log_error("load_equation_icons", e,
                                  f"Unexpected error loading PNG icon for {eq_id}: {error_msg}")

                # Set text based on whether PNG was successfully loaded
                if not png_loaded:
                    item_text = f"{eq_label}\n{eq_expression}"
                    item.setText(item_text)
                # else:
                #     print(f"✓ Showing PNG icon for {eq_id}")

                self.equation_list.addItem(item)

        except Exception as e:
            makeMessageBox(f"Error loading equations: {str(e)}")

    def on_method_changed(self):
        """Handle definition method change"""
        use_equation = self.equation_radio.isChecked()

        # Show/hide equation group based on selection
        self.equation_group.setVisible(use_equation)

        # Update accept button state
        self.update_accept_button_state()

    def on_equation_selection_changed(self):
        """Handle equation selection change"""
        current_item = self.equation_list.currentItem()
        if current_item:
            eq_id = current_item.data(QtCore.Qt.UserRole)
            if eq_id:
                self.selected_equation = eq_id
            else:
                self.selected_equation = None

        self.update_accept_button_state()

    def update_accept_button_state(self):
        """Update the accept button enabled state"""
        if self.equation_radio.isChecked():
            # Need selected equation
            self.pushAccept.setEnabled(self.selected_equation is not None)
        else:
            # For initialization marking, always enabled
            self.pushAccept.setEnabled(True)

    def accept_selection(self):
        """Accept the current selection"""
        if self.equation_radio.isChecked():
            self.use_initialization = False
        else:
            self.use_initialization = True
            # No initialization value needed - just marking for initialization

        self.accept()

    def get_selection(self):
        """Get the selection result"""
        return {
                'equation_id'       : self.selected_equation,
                'use_initialization': self.use_initialization
                }


def preload_equation_icons(variable_data, ontology_container):
    """
    Preload equation PNG icons using exchange board for consistency.
    
    Args:
        variable_data: Dictionary containing variable information
        ontology_container: The ontology container
        
    Returns:
        Dictionary of preloaded icons {equation_id: QIcon}
    """
    try:
        # Use exchange board to load all equation icons
        exchange_board = OntologyContainer(ontology_container)
        preloaded_icons = exchange_board.load_equation_icons()

        # Filter icons to only include equations for this variable
        variable_equations = variable_data.get('equations', {})
        filtered_icons = {}

        for eq_id in variable_equations:
            if eq_id in preloaded_icons:
                filtered_icons[eq_id] = preloaded_icons[eq_id]

        return filtered_icons

    except Exception as e:
        log_error("preload_equation_icons", e, "preloading equation icons")
        return {}


def select_equation_for_variable(variable_data, ontology_container, parent=None):
    """
    Launch the equation selector dialog for a variable.
    
    Args:
        variable_data: Dictionary containing variable information
        ontology_container: The ontology container (with preloaded icons)
        
    Returns:
        Dictionary with selection results or None if cancelled
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    dialog = EquationSelectorDialog(variable_data, ontology_container, parent)

    # Make dialog modal to block other windows
    if parent:
        dialog.setWindowModality(QtCore.Qt.WindowModal)
    else:
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)

    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        return dialog.get_selection()

    return None
