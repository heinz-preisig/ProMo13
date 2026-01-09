import os
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication


root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages','src'),
                os.path.join(root, 'tasks')])

# fmt: off
# import packages.OntologyBuilder.BehaviourLinker_HAP_v0.resources.resources_rc
from Utilities.InstantiationTool.controllers.main import MainController
from Utilities.InstantiationTool.models.main import MainModel
from Utilities.InstantiationTool.views.main import MainView
from common.components.splash_screen import splash_screen

# fmt: on


class App(QApplication):
    # TODO: Add to a centralized file with constants
    # TODO: The entry point for the application should be in the root
    # RESOURCE_PATH = "../packages/OntologyBuilder/BehaviourLinker/resources/resources.qrc"

    def __init__(self, sys_argv: list[str]) -> None:
        super().__init__(sys_argv)


        resource_path = ":/styles/stylesheet.qss"
        style_file = QtCore.QFile(resource_path)
        if style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            stream = QtCore.QTextStream(style_file)
            stylesheet = stream.readAll()
            self.setStyleSheet(stylesheet)


        # Load the embedded font
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
        self.main_view = MainView()
        self.main_controller = MainController(self.main_model, self.main_view)


if __name__ == "__main__":
    app = App([])

    splash = splash_screen.ClickableSplashScreen(
        splash_screen.PromoModule.INSTANTIATION
    )
    splash.show()
    app.processEvents()

    loop = QtCore.QEventLoop()
    splash.clicked.connect(loop.quit)
    loop.exec()

    splash.close()
    app.main_view.show()

    app.exec_()
