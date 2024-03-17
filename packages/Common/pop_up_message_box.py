#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "11.11.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox

BUTTONS = {
        "OK"             : QtWidgets.QMessageBox.Ok,
        "NO"             : QtWidgets.QMessageBox.No,
        "YES"            : QtWidgets.QMessageBox.Yes,
        "open"           : QtWidgets.QMessageBox.Open,
        "save"           : QtWidgets.QMessageBox.Save,
        "cancel"         : QtWidgets.QMessageBox.Cancel,
        "close"          : QtWidgets.QMessageBox.Close,
        "discard"        : QtWidgets.QMessageBox.Discard,
        "apply"          : QtWidgets.QMessageBox.Apply,
        "reset"          : QtWidgets.QMessageBox.Reset,
        "restore_default": QtWidgets.QMessageBox.RestoreDefaults,
        "help"           : QtWidgets.QMessageBox.Help,
        "save_all"       : QtWidgets.QMessageBox.SaveAll,
        "yes"            : QtWidgets.QMessageBox.Yes,
        "yes_to_all"     : QtWidgets.QMessageBox.YesToAll,
        "no"             : QtWidgets.QMessageBox.No,
        "no_to_all"      : QtWidgets.QMessageBox.NoToAll,
        "abort"          : QtWidgets.QMessageBox.Abort,
        "retry"          : QtWidgets.QMessageBox.Retry,
        "ignore"         : QtWidgets.QMessageBox.Ignore,
        # "no button"      : QtWidgets.QMessageBox.NoButton,
        }

ACTIONROLES= {
        "invalid" : QMessageBox.InvalidRole,     # -1	The button is invalid.
        "accept"  : QMessageBox.AcceptRole,      # 0	Clicking the button causes the dialog to be accepted (e.g. OK).
        "reject"  : QMessageBox.RejectRole,      # 1	Clicking the button causes the dialog to be rejected (e.g. Cancel).
        "destruct": QMessageBox.DestructiveRole, # 2	Clicking the button causes a destructive change
                                                 # (e.g. for Discarding Changes) and closes the dialog.
        "action"  : QMessageBox.ActionRole,      # 3	Clicking the button causes changes to the elements within the dialog.
        "help"    : QMessageBox.HelpRole,        # 4	The button can be clicked to request help.
        "yes"     : QMessageBox.YesRole,         # 5	The button is a "Yes"-like button.
        "no"      : QMessageBox.NoRole,          # 6	The button is a "No"-like button.
        "apply"   : QMessageBox.ApplyRole,       # 8	The button applies current changes.
        "reset"   : QMessageBox.ResetRole,       # 7	The button resets the dialog's fields to default values.
        }

MYBUTTONS = {}

def makeMessageBox(message, buttons=None, custom_buttons=None, default=None, infotext=""):
  """
  Buttons[0] is set as default
  """
  if buttons is None:
    buttons = ["cancel", "OK"]
  elif buttons == "not button":
    buttons = []
  if custom_buttons is None:
    custom_buttons = []

  msg_box = QtWidgets.QMessageBox()
  msg_box.setText(message)
  msg_box.setInformativeText(infotext)
  msg_box.setWindowTitle("dialog")
  msg_box.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.Popup)




  # save = QtWidgets.QMessageBox.Save
  # discard = QtWidgets.QMessageBox.Discard
  # cancel = QtWidgets.QMessageBox.Cancel
  if buttons:
    mybuttons = BUTTONS[buttons[0]]
    for buts in buttons:
      if buts in BUTTONS:
        mybuttons = mybuttons | BUTTONS[buts]
    if mybuttons:
      msg_box.setStandardButtons(mybuttons)  # discard | save | cancel);
      # msg_box.setDefaultButton(BUTTONS[buttons[0]])

  for buts, action in custom_buttons:
    MYBUTTONS[buts] = msg_box.addButton(buts, ACTIONROLES["action"])

  if default in buttons:
    msg_box.setDefaultButton(BUTTONS[default])
  if default in MYBUTTONS:
    msg_box.setDefaultButton(MYBUTTONS[default])

  msg_box.show()
  r = msg_box.exec_()


  for i in BUTTONS:
    if r == BUTTONS[i]:
      return i

  selection, action = custom_buttons[r]
  return selection


if __name__ == '__main__':
  a = QtWidgets.QApplication(sys.argv)
  s = makeMessageBox("hello this is a very long message  even longer than one expcts \n hello",
                     buttons="not button", #["OK"],
                     custom_buttons=[("node","accept"),("arc", "accept")],
                     default="arc",
                     infotext="info text")
  print(s)
  sys.exit()
