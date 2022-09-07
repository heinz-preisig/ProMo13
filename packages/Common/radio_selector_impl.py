'''
Created on Sept 25, 2017

@summary:
@organization: Department of Chemical Engineering, NTNU, Norway
@contact:      heinz.preisig@chemeng.ntnu.no
@license:      GPLv3
@requires:     Python 2.7.1 or higher
@since:        2017-08-25
@version:      0.1
@change:
@copyright:    Preisig, Heinz A

changes
2019-05-08     regulated width  HA Preisig

'''

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.qt_resources import ModellerRadioButton
from Common.radio_selector import Ui_Form

TOKEN_STRING_SEPARATOR = " :: "


class RadioSelector(QtWidgets.QWidget):
  """
  sends a signal on selecting an item
  """

  newSelection = QtCore.pyqtSignal(str)

  def __init__(self, myparent=None):
    """
    Constructor
    """

    QtWidgets.QWidget.__init__(self, parent=myparent)
    self.ui = Ui_Form()
    self.ui.setupUi(self)
    self.groupboxes = {}
    self.radiobuttons = {}
    self.x = 10
    self.y = 10
    self.autoexclusive = False
    self.formLayoutWidget = None
    self.initialise = True

  def addListOfChoices(self, group_name, list_of_choices, checked, autoexclusive=True):
    """
    A list of radio buttons is added to a groupbox which is added below to the already existing ones.
    The title serves as a group identifier and is also conveyed by the signal that is sent when toggling
    a member in the list of radio buttons.
    :param autoexclusive:
    :param group_name: title and group identifier
    :param list_of_choices: list of triples with a token as a string,
                             a label string associated with the token and
                             a target method for the signal to be processed
    :param checked: if
                      - string then it is the label
                      - integer then it is the index, thus the ordinal number in the list of radio buttons
    :return: token, label_string
    """

    self.radiobuttons[group_name] = []
    self.groupboxes[group_name] = QtWidgets.QGroupBox(group_name, parent=self)
    self.formLayoutWidget = QtWidgets.QFormLayout(self.groupboxes[group_name])
    self.autoexclusive = autoexclusive

    # print("\nadd List %s"%(title))

    list_of_labels = []

    width = 0

    for item in list_of_choices:
      token, label_string, target = item
      label = "%s%s%s" % (token, TOKEN_STRING_SEPARATOR, label_string)
      # print("add item %s"%label)
      r = ModellerRadioButton(group_name, token, label_string, label, autoexclusive=autoexclusive)
      self.formLayoutWidget.setWidget(list_of_choices.index(item), QtWidgets.QFormLayout.LabelRole, r)
      r.radio_signal.connect(target)
      self.radiobuttons[group_name].append(r)
      list_of_labels.append(label_string)
      r_width = r.width()
      if r_width > width:
        width = r_width

    height = (len(list_of_choices) + 2) * 20
    self.groupboxes[group_name].setGeometry(self.x, self.y, width, height)

    self.y += height
    self.y += 0
    self.initialise = True
    token = None
    label_string = None

    count = 0
    if isinstance(checked, str):
      index = list_of_labels.index(checked)
      for token, label_string, target in list_of_choices:
        if label_string == label_string:
          index = count


    else:
      index = checked

    if index >= 0:
      self.check(group_name, index)

    return token, label_string

  def check(self, group_name, number):
    try:
      self.radiobuttons[group_name][number].setChecked(True)
    except:
      print("problems in setting check")
      # print(">>>>>>>>> error in setting check -- group %s,  number %s, length of group %s"%( group, number,
      # len(group)))

  def getGroups(self):
    return list(self.radiobuttons.keys())

  def getGroupLength(self, group_name):
    return len(self.radiobuttons[group_name])

  def uncheckGroup(self, group_name):
    for no in self.radiobuttons[group_name]:
      no.setChecked(False)

  def getCheckedInGroup(self, group_name):
    checked = []
    for r in self.radiobuttons[group_name]:
      symbol, string = str(r.text()).split(TOKEN_STRING_SEPARATOR)
      if r.isChecked():
        checked.append((symbol, string, True))
      else:
        checked.append((symbol, string, False))
    return checked

  def getListOfCheckedTokensInGroup(self, group_name):
    checked_tokens = []
    for r in self.radiobuttons[group_name]:
      token, label = str(r.text()).split(TOKEN_STRING_SEPARATOR)
      if r.isChecked():
        checked_tokens.append(token)
    return checked_tokens

  def getListOfCheckedLabelInGroup(self, group_name):
    checked_labels = []
    for r in self.radiobuttons[group_name]:
      token, label = str(r.text()).split(TOKEN_STRING_SEPARATOR)
      if r.isChecked():
        checked_labels.append(label)
    return checked_labels


# ======================= test ===========================================

def addToTokenList(token, token_string, ID, toggle):
  if toggle:
    print("got token :", token, token_string, ID, toggle)


if __name__ == '__main__':
  a = QtWidgets.QApplication([])
  selection = [('a', 'first', addToTokenList), ('b', 'second', addToTokenList)]
  w = RadioSelector()
  w.addListOfChoices("first title", selection, "first", autoexclusive=True)
  w.addListOfChoices("second title", selection, 1, autoexclusive=False)
  w.show()
  a.exec_()
  print("\n ", w.getCheckedInGroup("first title"))
  print("\n ", w.getCheckedInGroup("second title"))
