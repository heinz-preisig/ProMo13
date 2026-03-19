# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_documentation.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DocumentationDialog(object):
    def setupUi(self, DocumentationDialog):
        DocumentationDialog.setObjectName("DocumentationDialog")
        DocumentationDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        DocumentationDialog.resize(736, 68)
        DocumentationDialog.setModal(False)
        self.groupDocumentation = QtWidgets.QGroupBox(DocumentationDialog)
        self.groupDocumentation.setGeometry(QtCore.QRect(7, 5, 630, 50))
        self.groupDocumentation.setObjectName("groupDocumentation")
        self.lineDocumentation = QtWidgets.QLineEdit(self.groupDocumentation)
        self.lineDocumentation.setGeometry(QtCore.QRect(60, 20, 561, 27))
        self.lineDocumentation.setText("")
        self.lineDocumentation.setObjectName("lineDocumentation")
        self.pushCancle = QtWidgets.QPushButton(DocumentationDialog)
        self.pushCancle.setGeometry(QtCore.QRect(640, 30, 85, 27))
        self.pushCancle.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushCancle.setObjectName("pushCancle")

        self.retranslateUi(DocumentationDialog)
        QtCore.QMetaObject.connectSlotsByName(DocumentationDialog)

    def retranslateUi(self, DocumentationDialog):
        _translate = QtCore.QCoreApplication.translate
        self.groupDocumentation.setTitle(_translate("DocumentationDialog", "documentation"))
        self.lineDocumentation.setPlaceholderText(_translate("DocumentationDialog", "describe variable"))
        self.pushCancle.setText(_translate("DocumentationDialog", "cancel"))
