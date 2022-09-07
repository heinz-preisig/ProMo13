import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class Main(QtWidgets.QMainWindow):
  def __init__(self, parent=None):
    super(Main, self).__init__(parent)

    # main button
    self.addButton = QtWidgets.QPushButton('button to add other widgets')
    self.addButton.clicked.connect(self.clean)  # (self.addWidget)

    # scroll area widget contents - layout
    self.scrollLayout = QtWidgets.QFormLayout()

    # scroll area widget contents
    self.scrollWidget = QtWidgets.QWidget()
    self.scrollWidget.setLayout(self.scrollLayout)

    # scroll area
    self.scrollArea = QtWidgets.QScrollArea()
    self.scrollArea.setWidgetResizable(True)
    self.scrollArea.setWidget(self.scrollWidget)

    # main layout
    self.mainLayout = QtWidgets.QVBoxLayout()

    # add all main to the main vLayout
    self.mainLayout.addWidget(self.addButton)
    self.mainLayout.addWidget(self.scrollArea)

    # central widget
    self.centralWidget = QtWidgets.QWidget()
    self.centralWidget.setLayout(self.mainLayout)

    # set central widget
    self.setCentralWidget(self.centralWidget)

    self.radio_buttons = []
    self.ID = 0
    for i in [1, 2]:
      self.radio_buttons.append(self.addRadioButton(self.ID, i))

  def addWidget(self, ID):
    self.scrollLayout.addRow(RadioButton("gugugs"))

  def addRadioButton(self, ID, label, value=False):
    self.ID = ID
    a = RadioButton("%s :: %s" % (self.ID, label))
    self.scrollLayout.addRow(a)
    a.setChecked(value)
    self.ID += 1
    return a

  def clean(self):
    print("debugging -- clean")
    for button in self.radio_buttons:
      button.deleteLater()


class TestButton(QtGui.QPushButton):
  def __init__(self, parent=None):
    super(TestButton, self).__init__(parent)
    self.setText("I am in Test widget")
    # self.clicked.connect(self.clean)


class RadioButton(QtGui.QRadioButton):
  radio_signal = QtCore.pyqtSignal(int, str, bool)

  def __init__(self, ID_label, parent=None):
    super(RadioButton, self).__init__(parent)
    self.setText(ID_label)
    [ID_str, self.label] = ID_label.split(" :: ")
    self.ID = int(ID_str)
    self.toggled.connect(self.beenToggled)

  def beenToggled(self, value):
    print("debugging", self.ID, self.label, value)
    self.radio_signal.emit(self.ID, self.label, value)


app = QtGui.QApplication(sys.argv)
myWidget = Main()
myWidget.show()
app.exec_()
