# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'save_file.ui'
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
    Dialog.resize(331, 71)
    Dialog.setModal(True)
    self.layoutWidget = QtWidgets.QWidget(Dialog)
    self.layoutWidget.setGeometry(QtCore.QRect(30, 20, 280, 29))
    self.layoutWidget.setObjectName("layoutWidget")
    self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
    self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.pushButtonDoNotSave = QtWidgets.QPushButton(self.layoutWidget)
    self.pushButtonDoNotSave.setObjectName("pushButtonDoNotSave")
    self.horizontalLayout.addWidget(self.pushButtonDoNotSave)
    self.pushButtonCancel = QtWidgets.QPushButton(self.layoutWidget)
    self.pushButtonCancel.setObjectName("pushButtonCancel")
    self.horizontalLayout.addWidget(self.pushButtonCancel)
    self.pushButtonSave = QtWidgets.QPushButton(self.layoutWidget)
    self.pushButtonSave.setObjectName("pushButtonSave")
    self.horizontalLayout.addWidget(self.pushButtonSave)

    self.retranslateUi(Dialog)
    QtCore.QMetaObject.connectSlotsByName(Dialog)

  def retranslateUi(self, Dialog):
    _translate = QtCore.QCoreApplication.translate
    Dialog.setWindowTitle(_translate("Dialog", "save file ?"))
    self.pushButtonDoNotSave.setText(_translate("Dialog", "do not save"))
    self.pushButtonCancel.setText(_translate("Dialog", "cancel"))
    self.pushButtonSave.setText(_translate("Dialog", "save"))
