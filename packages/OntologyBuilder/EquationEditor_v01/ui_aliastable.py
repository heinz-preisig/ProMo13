# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_aliastable.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AliasTable(object):
    def setupUi(self, AliasTable):
        AliasTable.setObjectName("AliasTable")
        AliasTable.resize(711, 885)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AliasTable.sizePolicy().hasHeightForWidth())
        AliasTable.setSizePolicy(sizePolicy)
        self.tableWidget = QtWidgets.QTableWidget(AliasTable)
        self.tableWidget.setGeometry(QtCore.QRect(130, 10, 571, 861))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setSizeIncrement(QtCore.QSize(1, 1))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.layoutWidget = QtWidgets.QWidget(AliasTable)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 81, 111))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pushFinished = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushFinished.sizePolicy().hasHeightForWidth())
        self.pushFinished.setSizePolicy(sizePolicy)
        self.pushFinished.setMinimumSize(QtCore.QSize(40, 40))
        self.pushFinished.setMaximumSize(QtCore.QSize(40, 40))
        self.pushFinished.setText("")
        self.pushFinished.setObjectName("pushFinished")
        self.gridLayout_3.addWidget(self.pushFinished, 0, 0, 1, 1)
        self.pushInfo = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(40)
        sizePolicy.setVerticalStretch(40)
        sizePolicy.setHeightForWidth(self.pushInfo.sizePolicy().hasHeightForWidth())
        self.pushInfo.setSizePolicy(sizePolicy)
        self.pushInfo.setMinimumSize(QtCore.QSize(40, 40))
        self.pushInfo.setMaximumSize(QtCore.QSize(40, 40))
        self.pushInfo.setText("")
        self.pushInfo.setObjectName("pushInfo")
        self.gridLayout_3.addWidget(self.pushInfo, 1, 0, 1, 1)
        self.gridLayout_3.setRowStretch(0, 50)

        self.retranslateUi(AliasTable)
        QtCore.QMetaObject.connectSlotsByName(AliasTable)

    def retranslateUi(self, AliasTable):
        _translate = QtCore.QCoreApplication.translate
        AliasTable.setWindowTitle(_translate("AliasTable", "Form"))
