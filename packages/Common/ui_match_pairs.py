# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_match_pairs.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1124, 463)
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 1091, 371))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listWidgetLeft = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        self.listWidgetLeft.setObjectName("listWidgetLeft")
        self.horizontalLayout.addWidget(self.listWidgetLeft)
        self.listWidgetRight = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        self.listWidgetRight.setObjectName("listWidgetRight")
        self.horizontalLayout.addWidget(self.listWidgetRight)
        self.listWidgetPairs = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        self.listWidgetPairs.setObjectName("listWidgetPairs")
        self.horizontalLayout.addWidget(self.listWidgetPairs)
        self.horizontalLayout.setStretch(0, 5000)
        self.horizontalLayout.setStretch(1, 5000)
        self.horizontalLayout.setStretch(2, 5000)
        self.pushButtonExit = QtWidgets.QPushButton(Dialog)
        self.pushButtonExit.setGeometry(QtCore.QRect(40, 390, 89, 41))
        self.pushButtonExit.setObjectName("pushButtonExit")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButtonExit.setText(_translate("Dialog", "OK"))
