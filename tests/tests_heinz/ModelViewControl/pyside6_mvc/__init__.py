"""
PySide6 MVC + Delegate Example

A demonstration of Model-View-Controller architecture with Qt's model/view framework
and custom delegates for rendering items.
"""

__version__ = "0.1.0"

# Export the main components
from .models import ListModel, TableModel
from .views import MainWindow
from .delegates import SoftHighlightDelegate
from .controllers import AppController

__all__ = [
    'ListModel',
    'TableModel',
    'MainWindow',
    'SoftHighlightDelegate',
    'AppController'
]
