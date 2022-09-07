# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_two_list_selector.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Ui_TwoListSelector(object):
  def setupUi(self, TwoListSelector):
    TwoListSelector.setObjectName("TwoListSelector")
    # TwoListSelector.resize(1058, 300)
    self.groupBox = QtWidgets.QGroupBox(TwoListSelector)
    self.groupBox.setGeometry(QtCore.QRect(20, 10, 1021, 281))
    self.groupBox.setObjectName("groupBox")
    self.layoutWidget = QtWidgets.QWidget(self.groupBox)
    self.layoutWidget.setGeometry(QtCore.QRect(910, 100, 87, 76))
    self.layoutWidget.setObjectName("layoutWidget")
    self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
    self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
    self.verticalLayout.setContentsMargins(0, 0, 0, 0)
    self.verticalLayout.setObjectName("verticalLayout")
    self.pushUp = QtWidgets.QPushButton(self.layoutWidget)
    self.pushUp.setObjectName("pushUp")
    self.verticalLayout.addWidget(self.pushUp)
    self.pushDown = QtWidgets.QPushButton(self.layoutWidget)
    self.pushDown.setObjectName("pushDown")
    self.verticalLayout.addWidget(self.pushDown)
    self.layoutWidget_2 = QtWidgets.QWidget(self.groupBox)
    self.layoutWidget_2.setGeometry(QtCore.QRect(430, 110, 87, 62))
    self.layoutWidget_2.setObjectName("layoutWidget_2")
    self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
    self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
    self.verticalLayout_2.setObjectName("verticalLayout_2")
    self.pushRight = QtWidgets.QPushButton(self.layoutWidget_2)
    self.pushRight.setObjectName("pushRight")
    self.verticalLayout_2.addWidget(self.pushRight)
    self.pushLeft = QtWidgets.QPushButton(self.layoutWidget_2)
    self.pushLeft.setObjectName("pushLeft")
    self.verticalLayout_2.addWidget(self.pushLeft)
    self.listAvailable = QtWidgets.QListWidget(self.groupBox)
    self.listAvailable.setGeometry(QtCore.QRect(41, 51, 371, 192))
    self.listAvailable.setObjectName("listAvailable")
    self.listSelected = QtWidgets.QListWidget(self.groupBox)
    self.listSelected.setGeometry(QtCore.QRect(521, 51, 381, 192))
    self.listSelected.setObjectName("listSelected")
    self.pushOK = QtWidgets.QPushButton(self.groupBox)
    self.pushOK.setGeometry(QtCore.QRect(410, 250, 97, 27))
    self.pushOK.setObjectName("pushOK")

    self.retranslateUi(TwoListSelector)
    QtCore.QMetaObject.connectSlotsByName(TwoListSelector)

  def retranslateUi(self, TwoListSelector):
    _translate = QtCore.QCoreApplication.translate
    TwoListSelector.setWindowTitle(_translate("TwoListSelector", "Form"))
    self.groupBox.setTitle(_translate("TwoListSelector", "Select"))
    self.pushUp.setText(_translate("TwoListSelector", "up"))
    self.pushDown.setText(_translate("TwoListSelector", "down"))
    self.pushRight.setText(_translate("TwoListSelector", ">>>"))
    self.pushLeft.setText(_translate("TwoListSelector", "<<<"))
    self.pushOK.setText(_translate("TwoListSelector", "OK"))
