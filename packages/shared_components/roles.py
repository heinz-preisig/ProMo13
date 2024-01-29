"""
Defines custom roles for the application's models.

This module defines the roles used in the models of the application.
Each role is represented as a constant with a unique value, which is
used to store and retrieve data in the models. The roles are defined
using the QtCore.Qt.UserRole enumerator to avoid conflicts with standard
roles.

Author: Alberto Rodriguez Fernandez
"""
from PyQt5.QtCore import Qt

ID_ROLE = Qt.UserRole                                     # type: ignore
NAME_ROLE = Qt.UserRole + 1                               # type: ignore
IMAGE_ROLE = Qt.UserRole + 2                              # type: ignore
SUBTYPE_ROLE = Qt.UserRole + 3                            # type: ignore
EXPANDED_ROLE = Qt.UserRole + 4                           # type: ignore
LAST_CHECK_STATE_ROLE = Qt.UserRole + 5                   # type: ignore
