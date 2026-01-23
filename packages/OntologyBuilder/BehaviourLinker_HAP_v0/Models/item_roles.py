"""
Standardized roles for item data in Qt model/view architecture.

This module defines a set of standardized roles for use with Qt's model/view architecture.
These roles extend Qt's default roles (like DisplayRole, UserRole) to provide
consistent data access across the application.

All custom roles are offset from Qt.UserRole to avoid conflicts.
Each role is documented with its purpose and expected data type.
"""

from enum import IntEnum
from PyQt5 import QtCore


class ItemDataRole(IntEnum):
    """
    Standardized roles for item data in Qt models.
    
    These roles are used with QAbstractItemModel.setData() and data() methods
    to store and retrieve item-specific data in a type-safe way.
    """
    # Base offset to avoid conflicts with Qt's default roles
    # (Qt.UserRole is 0x0100, we start after that)
    BASE = QtCore.Qt.UserRole + 0x100
    
    # Core item identification
    ITEM_TYPE = BASE + 1      # Type of item ('network', 'category', 'entity_type', 'entity')
    ITEM_ID = BASE + 2        # Unique identifier for the item
    ITEM_DATA = BASE + 3      # Primary data associated with the item
    
    # Entity-specific roles
    ENTITY_OBJECT = BASE + 10  # The actual entity object
    ENTITY_NAME = BASE + 11    # Display name of the entity
    
    # File/Path related
    FILE_PATH = BASE + 20     # File path (e.g., for images)
    
    # Status flags
    IS_PROCESSED = BASE + 30  # Boolean indicating if item is processed
    IS_EDITABLE = BASE + 31   # Boolean indicating if item is editable
    
    # Additional data slots (use with clear documentation)
    CUSTOM_1 = BASE + 100
    CUSTOM_2 = BASE + 101
    CUSTOM_3 = BASE + 102


# For backward compatibility and easier access
# These can be used as: roles.ENTITY_OBJECT, roles.ITEM_ID, etc.
roles = ItemDataRole
