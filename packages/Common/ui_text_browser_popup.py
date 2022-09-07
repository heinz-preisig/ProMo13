# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_text_browser_popup.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class Ui_TextBrowserPopUp(object):
  def setupUi(self, TextBrowserPopUp):
    TextBrowserPopUp.setObjectName("TextBrowserPopUp")
    TextBrowserPopUp.setWindowModality(QtCore.Qt.NonModal)
    TextBrowserPopUp.resize(875, 870)
    self.textBrowser = QtWidgets.QTextBrowser(TextBrowserPopUp)
    self.textBrowser.setGeometry(QtCore.QRect(20, 10, 841, 841))
    font = QtGui.QFont()
    font.setPointSize(14)
    font.setItalic(True)
    self.textBrowser.setFont(font)
    self.textBrowser.setAutoFormatting(QtWidgets.QTextEdit.AutoAll)
    self.textBrowser.setObjectName("textBrowser")

    self.retranslateUi(TextBrowserPopUp)
    QtCore.QMetaObject.connectSlotsByName(TextBrowserPopUp)

  def retranslateUi(self, TextBrowserPopUp):
    _translate = QtCore.QCoreApplication.translate
    TextBrowserPopUp.setWindowTitle(_translate("TextBrowserPopUp", "Dialog"))
