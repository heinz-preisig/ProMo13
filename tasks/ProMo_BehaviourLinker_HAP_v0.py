import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets

root = os.path.abspath(os.path.join(".."))
sys.path.extend([root,
                 os.path.join(root, 'packages'),
                 os.path.join(root, 'tasks'),
                 os.path.join(root, 'src')
                 ])

from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.main import MainController
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.main import MainModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.main import MainView
from common.components.splash_screen import splash_screen


class App(QtWidgets.QApplication):
  # TODO: Add to a centralized file with constants
  # TODO: The entry point for the application should be in the root
  # RESOURCE_PATH = "../packages/OntologyBuilder/BehaviourLinker/resources/resources.qrc"

  def __init__(self, sys_argv: list[str]) -> None:
    super().__init__(sys_argv)

    self.main_model = MainModel()
    self.main_view = MainView(self.main_model)
    self.main_controller = MainController(self.main_model, self.main_view)


if __name__ == "__main__":
  app = App([])

  splash = splash_screen.ClickableSplashScreen(splash_screen.PromoModule.LINKER)
  splash.show()
  app.processEvents()

  loop = QtCore.QEventLoop()
  splash.clicked.connect(loop.quit)
  loop.exec()

  splash.close()
  app.main_view.show()
  # splash.finish(app.main_view)

  app.exec_()
