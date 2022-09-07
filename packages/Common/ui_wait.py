# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_wait.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_waiter(object):
    def setupUi(self, waiter):
        waiter.setObjectName("waiter")
        waiter.resize(400, 300)
        self.label = QtWidgets.QLabel(waiter)
        self.label.setGeometry(QtCore.QRect(100, 60, 67, 17))
        self.label.setObjectName("label")

        self.retranslateUi(waiter)
        QtCore.QMetaObject.connectSlotsByName(waiter)

    def retranslateUi(self, waiter):
        _translate = QtCore.QCoreApplication.translate
        waiter.setWindowTitle(_translate("waiter", "Form"))
        self.label.setText(_translate("waiter", "wait"))
