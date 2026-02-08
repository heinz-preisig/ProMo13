"""
Centralized UI settings for consistent appearance across the BehaviourLinker application.
"""

from PyQt5 import QtCore

class UISettings:
    """Centralized UI settings for consistent appearance"""
    
    # Icon sizes for different contexts
    ICON_SIZES = {
        'variable_selection': QtCore.QSize(250, 75),    # For variable selection lists (increased)
        'equation_selection': QtCore.QSize(320, 85),    # For equation selection lists (increased)
        'entity_variables': QtCore.QSize(250, 75),      # For entity variable lists (increased)
        'entity_equations': QtCore.QSize(320, 85),     # For entity equation lists (increased)
        'entity_lists': QtCore.QSize(250, 75),         # Default for entity lists (variables)
        'default': QtCore.QSize(48, 48)                # Default fallback size
    }
    
    # Row heights for different contexts
    ROW_HEIGHTS = {
        'variable_selection': 95,      # For variable selection lists (increased)
        'equation_selection': 105,     # For equation selection lists (increased)
        'entity_variables': 95,        # For entity variable lists (increased)
        'entity_equations': 105,       # For entity equation lists (increased)
        'entity_lists': 95,            # Default for entity lists (variables)
        'default': 56                  # Default fallback height
    }
    
    # Spacing settings
    SPACING = {
        'list_items': 5,               # Spacing between list items
        'default': 5                   # Default spacing
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
        
        # Apply settings
        list_widget.setIconSize(icon_size)
        list_widget.setUniformItemSizes(True)
        list_widget.setSpacing(spacing)
        
        # Set grid size for row height if available
        if hasattr(list_widget, 'setGridSize'):
            list_widget.setGridSize(QtCore.QSize(-1, row_height))
        
        # print(f"Configured list widget for context '{context}': icon_size={icon_size}, row_height={row_height}, spacing={spacing}")
    
    @classmethod
    def get_icon_size(cls, context='default'):
        """Get icon size for a specific context"""
        return cls.ICON_SIZES.get(context, cls.ICON_SIZES['default'])
    
    @classmethod
    def get_row_height(cls, context='default'):
        """Get row height for a specific context"""
        return cls.ROW_HEIGHTS.get(context, cls.ROW_HEIGHTS['default'])
