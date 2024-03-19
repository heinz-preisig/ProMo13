from PyQt5.QtWidgets import *
import PyQt5.QtCore as QtCore
import sys

from Common.radio_selector_dialog import Ui_Dialog

from Common.resources_icons import roundButton
class RadioSelectorDialog(QDialog):
    def __init__(self, buttons, parent=None):

      QWidget.__init__(self, parent=parent)

      self.ui = Ui_Dialog()
      self.ui.setupUi(self)
      QWidget.__init__(self)

      self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)

      layout = QGridLayout()
      self.setLayout(layout)
      self.selection=None


      # spacerItem = QSpacerItem(100, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
      #
      # pushButtonExit = QPushButton()
      # pushButtonExit.pressed.connect(self.goExit)
      # pushButtonAccept = QPushButton()
      # pushButtonAccept.pressed.connect(self.goAccept)
      # layout.addWidget(pushButtonExit, 0,0)
      # # layout.addItem(spacerItem,0,1)
      # layout.addWidget(pushButtonAccept, 0,2)
      # # layout.addItem(spacerItem,1,0)



      # roundButton(pushButtonExit, "exit", "exit" )
      # roundButton(pushButtonAccept,"accept","accept")

      # self.ui.prompt.setText(prompt)

      count = 2
      for b in buttons:

        radiobutton = QRadioButton(b)
        radiobutton.setChecked(False)
        radiobutton.selection = b
        radiobutton.toggled.connect(self.onClicked)
        layout.addWidget(radiobutton, count, 0)
        count +=1

      self.show()
      self.exec_()
      self.raise_()

    def onClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            print("Country is %s" % (radioButton.selection))
            self.selection = radioButton.selection
        self.close()

    # def goAccept(self):
    #   self.close()
    #
    # def goExit(self):
    #   print("exit", self.selection)
    #   self.selection = None
    #   self.close()

    def mouseMoveEvent(self, event):
      delta = QtCore.QPoint(event.globalPos() - self.oldPos)
      self.move(self.x() + delta.x(), self.y() + delta.y())
      self.oldPos = event.globalPos()

    def mousePressEvent(self, event):
      self.oldPos = event.globalPos()


if __name__ == '__main__':
  app = QApplication(sys.argv)
  buttons = ["hello","gugus"]
  screen = RadioSelectorDialog(buttons)
  # screen.show()
  # app.exec_()
  print("response",screen.selection)