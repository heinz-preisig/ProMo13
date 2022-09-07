#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
text window to display text files
===============================================================================

Main program controlling the graphical interface for the model construction.

Note: This implementation does not allow for several tokens with typed tokens.
Note: It only works with one set of typed tokens per network.

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtWidgets

from Common.ui_text_browser_popup import Ui_TextBrowserPopUp


class UI_FileDisplayWindow(QtWidgets.QDialog):

  def __init__(self, txt_file):
    QtWidgets.QMainWindow.__init__(self)
    self.ui = Ui_TextBrowserPopUp()
    self.ui.setupUi(self)

    self.ui.textBrowser.clear()

    with open(txt_file, 'r') as f:
      l = f.read()
      self.ui.textBrowser.append(l)
