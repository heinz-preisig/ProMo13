"""
Centralized UI settings for consistent appearance across the BehaviourLinker application.
"""

from PyQt5 import QtCore


class UISettings:
    """Centralized UI settings for consistent appearance"""

    # Icon sizes for different contexts
    ICON_SIZES = {
            'variable_selection': QtCore.QSize(240, 56),  # For variable selection lists (20% smaller: 300*0.8=240, 70*0.8=56)
            'equation_selection': QtCore.QSize(320, 85),  # For equation selection lists (increased)
            'entity_variables'  : QtCore.QSize(300, 70),  # For entity variable lists (more compact)
            'entity_equations'  : QtCore.QSize(320, 85),  # For entity equation lists (increased)
            'entity_lists'      : QtCore.QSize(300, 70),  # Default for entity lists (variables) - more compact
            'default'           : QtCore.QSize(48, 48)  # Default fallback size
            }

    # Row heights for different contexts
    ROW_HEIGHTS = {
            'variable_selection': 100,  # For variable selection lists (20% smaller: 90*0.8=72)
            'equation_selection': 105,  # For equation selection lists (increased)
            'entity_variables'  : 90,  # For entity variable lists (more compact height)
            'entity_equations'  : 105,  # For entity equation lists (increased)
            'entity_lists'      : 90,  # Default for entity lists (variables) - more compact height
            'default'           : 56  # Default fallback height
            }

    # Spacing settings
    SPACING = {
            'list_items': 5,  # Spacing between list items
            'default'   : 5  # Default spacing
            }

    # Font sizes for different contexts
    FONT_SIZES = {
            'variable_selection': 10,  # For variable selection lists (smaller font)
            'equation_selection': 11,  # For equation selection lists
            'entity_variables'  : 10,  # For entity variable lists (smaller font)
            'entity_equations'  : 11,  # For entity equation lists
            'entity_lists'      : 10,  # Default for entity lists (variables) - smaller font
            'default'           : 11  # Default fallback font size
            }

    @classmethod
    def configure_list_widget(cls, list_widget, context='default'):
        """
        Configure a list widget with consistent settings based on context.
        
        Args:
            list_widget: The QListWidget to configure
            context: The context ('variable_selection', 'equation_selection', 'entity_lists', 'default')
        """
        # Get settings for the context, fallback to default
        icon_size = cls.ICON_SIZES.get(context, cls.ICON_SIZES['default'])
        row_height = cls.ROW_HEIGHTS.get(context, cls.ROW_HEIGHTS['default'])
        spacing = cls.SPACING.get('list_items', cls.SPACING['default'])
        font_size = cls.FONT_SIZES.get(context, cls.FONT_SIZES['default'])

        # Apply settings
        list_widget.setIconSize(icon_size)
        list_widget.setUniformItemSizes(True)
        list_widget.setSpacing(spacing)

        # Set font size
        from PyQt5 import QtGui
        font = QtGui.QFont()
        font.setPointSize(font_size)
        list_widget.setFont(font)

        # Set grid size for row height if available
        if hasattr(list_widget, 'setGridSize'):
            list_widget.setGridSize(QtCore.QSize(-1, row_height))

        # print(f"Configured list widget for context '{context}': icon_size={icon_size}, row_height={row_height}, font_size={font_size}, spacing={spacing}")

    @classmethod
    def get_icon_size(cls, context='default'):
        """Get icon size for a specific context"""
        return cls.ICON_SIZES.get(context, cls.ICON_SIZES['default'])

    @classmethod
    def get_row_height(cls, context='default'):
        """Get row height for a specific context"""
        return cls.ROW_HEIGHTS.get(context, cls.ROW_HEIGHTS['default'])
