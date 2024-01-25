import os
from typing import Optional, List

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from packages.Common import resource_initialisation

SIZE = 30


class SearchBarView(QtWidgets.QFrame):
  def __init__(self, parent=None, empty_msg: Optional[str] = None):
    super().__init__(parent)

    self.empty_msg = empty_msg or ""

    self.search_box = QtWidgets.QLineEdit()
    self.search_box.setFixedHeight(SIZE)

    self.completer = QtWidgets.QCompleter()

    self.icon_container = QtWidgets.QLabel()
    self.icon_container.setFixedSize(SIZE, SIZE)  # Set the size of the QLabel

    # TODO: Move this to the resource system
    icon_path = resource_initialisation.DIRECTORIES["icon_location"]
    icon_name = "search.png"

    icon = QtGui.QIcon(os.path.join(icon_path, icon_name))
    pixmap = icon.pixmap(self.icon_container.size())

    self.icon_container.setPixmap(pixmap)
    self.icon_container.setScaledContents(True)

    self.main_layout = QtWidgets.QHBoxLayout()
    self.main_layout.addWidget(self.icon_container)
    self.main_layout.addWidget(self.search_box)

    self.main_layout.setSpacing(0)
    self.main_layout.setContentsMargins(2, 2, 2, 2)

    # Allow the QFrame to expand vertically
    self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                       QtWidgets.QSizePolicy.Expanding)

    # Allow the layout to expand vertically
    self.main_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

    self.setLayout(self.main_layout)
    # Apply the style sheet to the widget
    self.setStyleSheet(
        """ QFrame{
        border-radius: 10px;
        border: 2px solid #B0B0B0;
    }"""
    )
    # Apply the style sheets to the components
    self.search_box.setStyleSheet(
        """QLineEdit {
          border: none;
          background-color: #F0F0F0;
      }"""
    )
    self.icon_container.setStyleSheet(
        """QLabel {
          border: none;
          border-radius: 4px;
          background-color: #F0F0F0;
      }"""
    )
