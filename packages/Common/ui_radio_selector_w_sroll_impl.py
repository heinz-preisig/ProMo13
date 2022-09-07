"""
@summary:  allows for a given number of radio buttons
@organization: Department of Chemical Engineering, NTNU, Norway
@contact:      heinz.preisig@chemeng.ntnu.no
@license:      GPLv3
@requires:     Python 2.7.1 or higher
@since:        2016-12-17
@version:      0.1
@change:
@author:       Preisig, Heinz A
@copyright:    Preisig, Heinz A

"""

from collections import OrderedDict

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from Common.resources_icons import roundButton

from Common.ui_radio_selector_w_scroll import Ui_Form


class UI_RadioSelector(QtWidgets.QDialog):
  """
  selects an item from a list
  """

  newSelection = QtCore.pyqtSignal(list)

  def __init__(self, radios, checked, allowed=2, maxheight=200):
    '''
    Constructor
    '''
    # print("debugging -- radios", radios)
    self.radios = radios
    self.checked = checked
    self.allowed = allowed
    self.maxheight = maxheight

    QtWidgets.QDialog.__init__(self)
    self.ui = Ui_Form()
    self.ui.setupUi(self)
    self.radioButton = {}

    roundButton(self.ui.pushButton,"back", tooltip="close and submit the chosen set")

    self.setup(initialise=True)

  def setup(self, initialise=False):

    active_radios = self.radios #checked
    if not initialise:
      active_radios = self.checked
      if len(active_radios) < self.allowed:
        active_radios = self.radios
    # else:                                  # Note: cannot get it to fit at the beginning
    #   s = QtCore.QSize(0,0)
    #   self.resize(s)
    #   print("debugging -- resizing 0,0")

    max_width = 0
    height_offset = 40  # offset for bar etc
    width_offset = 100
    height = 0
    for i in active_radios:
      label = QtWidgets.QLabel(i)
      width = label.fontMetrics().boundingRect(label.text()).width()
      height = height + 2 * label.fontMetrics().boundingRect(label.text()).height()
      if width > max_width:
        max_width = width

    height = height + height_offset
    if height > self.maxheight:
      height = self.maxheight

    s = QtCore.QSize(max_width + width_offset, height)
    self.resize(s)
    # print("debugging -- resizing",max_width + width_offset, height)

    self.radioButton = OrderedDict()

    for b in active_radios:
      self.addRadio(b, b in self.checked)

  def addRadio(self, name, checked):
    self.radioButton[name] = QtWidgets.QRadioButton(self.ui.scrollAreaWidgetContents)
    self.radioButton[name].setAutoExclusive(False)
    self.radioButton[name].setObjectName(name)
    n = name.replace('&', '&&')  # brrrr
    self.radioButton[name].setText(n)
    self.radioButton[name].show()
    if checked:
      self.radioButton[name].toggle()
    self.radioButton[name].clicked.connect(self.gotClick)
    self.ui.verticalLayout.addWidget(self.radioButton[name])


  def gotClick(self):
    self.checked = []
    for b in list(self.radioButton.keys()):
      if self.radioButton[b].isChecked():
        self.checked.append(b)
      self.radioButton[b].deleteLater()
    self.newSelection.emit(self.checked)
    self.setup()

  def getMarked(self):
    return self.checked

  def on_pushButton_pressed(self):
    self.close()


if __name__ == '__main__':
  a = QtWidgets.QApplication([])
  selection = 'b'
  w = UI_RadioSelector(
          ['a', 'befg', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c'], [],
          maxheight=100)
  w.newSelection.connect(print)
  w.show()
  a.exec_()
  if selection is None:
    print('None')
  else:
    print(selection)
  w.show()
