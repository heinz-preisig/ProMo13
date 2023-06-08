
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
import os

root = os.path.abspath(os.path.join(".."))
sys.path.append(root)

# fmt: off
from packages.OntologyBuilder.BehaviourLinker.Views.main import MainView
from packages.OntologyBuilder.BehaviourLinker.Models.main import MainModel
from packages.OntologyBuilder.BehaviourLinker.Controllers.main import MainController

import packages.OntologyBuilder.BehaviourLinker.resources.resources_rc
# fmt: on


class App(QApplication):
  # TODO: Add to a centralized file with constants
  # TODO: The entry point for the application should be in the root
  # RESOURCE_PATH = "../packages/OntologyBuilder/BehaviourLinker/resources/resources.qrc"

  def __init__(self, sys_argv):
    super(App, self).__init__(sys_argv)

    # TODO: Switch to file reading after the entry point is fixed.
    # Load the embedded stylesheet from the resource
    resource_path = ":/styles/stylesheet.qss"
    resource_data = QtCore.QResource(resource_path).data()
    stylesheet = resource_data.decode()

    # Apply the stylesheet to the application
    self.setStyleSheet(stylesheet)

    # Load the embedded font from the resource
    resource_path = ":/fonts/Lato-Regular.ttf"
    font_id = QtGui.QFontDatabase.addApplicationFont(resource_path)

    # Retrieve the font family name from the font ID
    font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
    if font_families:
      font_family = font_families[0]
    else:
      # Font registration failed, use fallback font
      font_family = "Arial"

    # Create the font object
    font = QtGui.QFont(font_family, 12)

    # Set the font for the application
    self.setFont(font)

    self.main_model = MainModel()
    self.main_view = MainView(self.main_model)
    self.main_controller = MainController(self.main_model, self.main_view)

    self.main_view.show()


if __name__ == '__main__':
  app = App([])
  app.exec_()
