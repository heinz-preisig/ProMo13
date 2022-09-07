# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logo.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Ui_Dialog(object):
  def setupUi(self, Dialog):
    Dialog.setObjectName("Dialog")
    Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
    Dialog.resize(400, 300)
    self.pushButton = QtWidgets.QPushButton(Dialog)
    self.pushButton.setGeometry(QtCore.QRect(150, 86, 251, 211))
    self.pushButton.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
    self.pushButton.setText("")
    self.pushButton.setObjectName("pushButton")

    self.retranslateUi(Dialog)
    QtCore.QMetaObject.connectSlotsByName(Dialog)

  def retranslateUi(self, Dialog):
    _translate = QtCore.QCoreApplication.translate
    Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
    self.pushButton.setToolTip(_translate("Dialog", "push to continue"))
