# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_symbol.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SymbolDialog(object):
    def setupUi(self, SymbolDialog):
        SymbolDialog.setObjectName("SymbolDialog")
        SymbolDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        SymbolDialog.resize(376, 99)
        SymbolDialog.setModal(False)
        self.groupSymbol = QtWidgets.QGroupBox(SymbolDialog)
        self.groupSymbol.setGeometry(QtCore.QRect(9, 9, 630, 51))
        self.groupSymbol.setObjectName("groupSymbol")
        self.lineSymbol = QtWidgets.QLineEdit(self.groupSymbol)
        self.lineSymbol.setGeometry(QtCore.QRect(60, 10, 191, 27))
        self.lineSymbol.setText("")
        self.lineSymbol.setObjectName("lineSymbol")
        self.pushCancle = QtWidgets.QPushButton(self.groupSymbol)
        self.pushCancle.setGeometry(QtCore.QRect(270, 10, 85, 27))
        self.pushCancle.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushCancle.setObjectName("pushCancle")
        self.MSG = QtWidgets.QPlainTextEdit(SymbolDialog)
        self.MSG.setGeometry(QtCore.QRect(10, 60, 351, 31))
        self.MSG.setObjectName("MSG")

        self.retranslateUi(SymbolDialog)
        QtCore.QMetaObject.connectSlotsByName(SymbolDialog)
        SymbolDialog.setTabOrder(self.lineSymbol, self.pushCancle)

    def retranslateUi(self, SymbolDialog):
        _translate = QtCore.QCoreApplication.translate
        self.groupSymbol.setTitle(_translate("SymbolDialog", "symbol"))
        self.lineSymbol.setPlaceholderText(_translate("SymbolDialog", "symbol"))
        self.pushCancle.setText(_translate("SymbolDialog", "cancel"))
