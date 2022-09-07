# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'radio_selector_scroll.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Ui_Form(object):
  def setupUi(self, Form):
    Form.setObjectName("Form")
    Form.resize(948, 885)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
    Form.setSizePolicy(sizePolicy)
    self.pushButton = QtWidgets.QPushButton(Form)
    self.pushButton.setGeometry(QtCore.QRect(310, 70, 97, 27))
    self.pushButton.setObjectName("pushButton")
    self.verticalLayoutWidget = QtWidgets.QWidget(Form)
    self.verticalLayoutWidget.setGeometry(QtCore.QRect(320, 220, 401, 491))
    self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
    self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
    self.verticalLayout.setContentsMargins(0, 0, 0, 0)
    self.verticalLayout.setObjectName("verticalLayout")
    self.scrollArea = QtWidgets.QScrollArea(self.verticalLayoutWidget)
    self.scrollArea.setWidgetResizable(True)
    self.scrollArea.setObjectName("scrollArea")
    self.scrollAreaWidgetContents = QtWidgets.QWidget()
    self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 397, 487))
    self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
    self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    self.verticalLayout.addWidget(self.scrollArea)

    self.retranslateUi(Form)
    QtCore.QMetaObject.connectSlotsByName(Form)

  def retranslateUi(self, Form):
    _translate = QtCore.QCoreApplication.translate
    Form.setWindowTitle(_translate("Form", "Form"))
    self.pushButton.setText(_translate("Form", "PushButton"))
