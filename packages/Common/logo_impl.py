import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.logo import Ui_Dialog
from Common.resource_initialisation import DIRECTORIES


class Logo(QtWidgets.QDialog):
  """
  Opens a dialogue window with a logo.
  The whole window is one button.

  It can be used in two ways:
  first with the button being active and if activated logo window closes

    logo = Logo("task_ontology_foundation")
    logo.exec_()

  or
  second the logo window stays open until the applicaton closes it
    logo = Logo("task_ontology_foundation")
    logo.show()
    .
    .
    logo.close()

  """

  def __init__(self, icon_name):
    """
    :param icon_name: the name of the icon that shall be used.
    it is assumed that the icon is a svg file.
    """
    super().__init__(flags=QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    qr = self.frameGeometry()
    screen = QtWidgets.QDesktopWidget().availableGeometry().center()
    x = screen.x()
    y = screen.y()

    self.setGeometry(x-150, y-150, 300, 300)
    self.ui.pushButton.setGeometry(0, 0, 300, 300)

    if icon_name:
      icon = icon_name + ".svg"
      icon_location = DIRECTORIES["icon_location"]
      path = os.path.join(icon_location, icon)
      accept_icon = QtGui.QIcon(QtGui.QPixmap(path))
      self.ui.pushButton.setIcon(accept_icon)
      self.ui.pushButton.setIconSize(QtCore.QSize(300, 300))

    # oImage = QtGui.QImage(path) #"/home/heinz/1_Gits/ProcessModeller/ProcessModeller_v7_04/packages/Common/icons
    # /ProMo_logo.png")
    # # sImage = oImage.scaled(QtCore.QSize(300, 300))  # resize Image to widgets size
    # # palette = QtGui.QPalette()
    # # palette.setBrush(QtGui.QPalette.Button, QtGui.QBrush(sImage))
    # # # self.setPalette(palette)
    # # self.ui.pushButton.setPalette(palette)

  def on_pushButton_pressed(self):
    self.close()
