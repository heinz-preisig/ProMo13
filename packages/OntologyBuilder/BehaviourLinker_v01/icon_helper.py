#!/usr/bin/env python3
"""
Simple Icon Helper - Extracted from entity_front_end.py
Minimal refactoring to centralize icon logic without changing behavior
"""

from Common.resources_icons import getIcon, roundButton


class IconHelper:
    """Simple helper for icon-related operations"""
    
    @staticmethod
    def get_variable_icon(var_id, ontology_container=None):
        """Get icon for a variable from ontology container or fallback"""
        if ontology_container and hasattr(ontology_container, 'variable_entity_dict'):
            variables = ontology_container.variable_entity_dict
            if var_id in variables and hasattr(variables[var_id], 'get_png_icon'):
                icon_path = variables[var_id].get_png_icon()
                if icon_path:
                    from PyQt5 import QtGui
                    return QtGui.QIcon(icon_path)
        
        # Fallback to default icons
        return getIcon("dependent_variable")
    
    @staticmethod
    def get_equation_icon():
        """Get icon for equations"""
        return getIcon("equation")
    
    @staticmethod
    def get_button_icon(icon_name):
        """Get icon for buttons"""
        return getIcon(icon_name)
    
    @staticmethod
    def setup_round_button(button, icon_name, tooltip=None, mysize=None):
        """Setup round button with icon - exactly like the original"""
        if mysize:
            roundButton(button, icon_name, tooltip=tooltip, mysize=mysize)
        else:
            roundButton(button, icon_name, tooltip=tooltip)
