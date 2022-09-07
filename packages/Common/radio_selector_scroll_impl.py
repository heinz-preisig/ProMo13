import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.radio_selector_scroll import Ui_Form


class Selector(QtWidgets.QWidget):
  def __init__(self, parent):

    super(Selector, self).__init__(parent)

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
    a.show()
    a.setChecked(value)
    self.ID += 1
    return a

  def clean(self):
    print("debugging -- clean")
    for button in self.radio_buttons:
      button.deleteLater()


class Main(QtWidgets.QMainWindow):
  def __init__(self, parent=None):
    QtWidgets.QWidget.__init__(self, parent=parent)
    self.ui = Ui_Form()
    self.ui.setupUi(self)

    self.s = Selector(self.ui.scrollAreaWidgetContents)
    self.s.show()
    # self.radioButton = {}
    # for i in range(0,50):
    #   self.radioButton[i] = QtGui.QRadioButton(self.ui.scrollAreaWidgetContents)
    #   self.radioButton[i].setObjectName(str(i))
    #   self.radioButton[i].setText(str(i))
    #   self.radioButton[i].show()
    # self.ui.verticalLayout.addWidget(self.radioButton[i])
    # self.radio = QtGui.QRadioButton(self.ui.verticalLayoutWidget_2)
    #
    #   self.ui.formLayout.addRow(QtGui.QRadioButton("gugugs"))

    # super(Main, self).__init__(parent)
    # s = Selector()
    # self.ui.verticalLayout.addWidget(Selector(self))
    # self.ui.scrollAreaWidgetContents = Selector(self)
    # self.ui.scrollAreaWidgetContents.show()

    ###################
    # # main button
    # self.addButton = QtGui.QPushButton('button to add other widgets')
    # self.addButton.clicked.connect(self.clean) #(self.addWidget)
    #
    # # scroll area widget contents - layout
    # self.scrollLayout = QtGui.QFormLayout()
    #
    # # scroll area widget contents
    # self.scrollWidget = QtGui.QWidget()
    # self.scrollWidget.setLayout(self.scrollLayout)
    #
    # # scroll area
    # self.scrollArea = QtGui.QScrollArea()
    # self.scrollArea.setWidgetResizable(True)
    # self.scrollArea.setWidget(self.scrollWidget)
    #
    # # main layout
    # self.mainLayout = QtGui.QVBoxLayout()
    #
    # # add all main to the main vLayout
    # self.mainLayout.addWidget(self.addButton)
    # self.mainLayout.addWidget(self.scrollArea)
    #
    # # central widget
    # self.centralWidget = QtGui.QWidget()
    # self.centralWidget.setLayout(self.mainLayout)
    #
    #
    # self.radio_buttons =[]
    # self.ID = 0
    # for i in [1,2]:
    #   self.radio_buttons.append(self.addRadioButton(self.ID, i))

    # set central widget
    # self.setCentralWidget(self.centralWidget)
  #
  # def addWidget(self, ID):
  #   self.scrollLayout.addRow(RadioButton("gugugs"))
  #
  # def addRadioButton(self, ID, label, value=False):
  #   self.ID = ID
  #   a = RadioButton("%s :: %s"%(self.ID,label))
  #   self.scrollLayout.addRow(a)
  #   a.setChecked(value)
  #   self.ID += 1
  #   return a
  #
  # def clean(self):
  #   print("debugging -- clean")
  #   for button in self.radio_buttons:
  #     button.deleteLater()


class TestButton(QtWidgets.QPushButton):
  def __init__(self, parent=None):
    super(TestButton, self).__init__(parent)
    self.setText("I am in Test widget")
    # self.clicked.connect(self.clean)


class RadioButton(QtWidgets.QRadioButton):
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


app = QtWidgets.QApplication(sys.argv)
myWidget = Main()
myWidget.show()
app.exec_()
