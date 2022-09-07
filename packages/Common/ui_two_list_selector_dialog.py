# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_two_list_selector_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(551, 442)
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 528, 371))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listWidgetLeft = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        self.listWidgetLeft.setObjectName("listWidgetLeft")
        self.horizontalLayout.addWidget(self.listWidgetLeft)
        self.listWidgetRight = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        self.listWidgetRight.setObjectName("listWidgetRight")
        self.horizontalLayout.addWidget(self.listWidgetRight)
        self.pushButtonExit = QtWidgets.QPushButton(Dialog)
        self.pushButtonExit.setGeometry(QtCore.QRect(40, 390, 89, 41))
        self.pushButtonExit.setObjectName("pushButtonExit")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButtonExit.setText(_translate("Dialog", "OK"))
