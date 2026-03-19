"""
Namespace editor UI, generated using Qt Designer

"""
__authors__ = 'Vinay Gautam: drvgautam@github.com'


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



try:
    _fromUtf8 = QStringListModel.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_AddNamespace(object):
    def setupUi(self, AddNamespace):
        AddNamespace.setObjectName(_fromUtf8("AddNamespace"))
        AddNamespace.resize(417, 139)
        self.gridLayout = QGridLayout(AddNamespace)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblNamespacePrefix = QLabel(AddNamespace)
        font = QFont()
        font.setPointSize(10)
        self.lblNamespacePrefix.setFont(font)
        self.lblNamespacePrefix.setObjectName(_fromUtf8("lblNamespacePrefix"))
        self.horizontalLayout.addWidget(self.lblNamespacePrefix)
        self.lineEditNamespacePrefix = QLineEdit(AddNamespace)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditNamespacePrefix.sizePolicy().hasHeightForWidth())
        self.lineEditNamespacePrefix.setSizePolicy(sizePolicy)
        self.lineEditNamespacePrefix.setMinimumSize(QSize(300, 0))
        font = QFont()
        font.setPointSize(10)
        self.lineEditNamespacePrefix.setFont(font)
        self.lineEditNamespacePrefix.setObjectName(_fromUtf8("lineEditNamespacePrefix"))
        self.horizontalLayout.addWidget(self.lineEditNamespacePrefix)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblNamespaceURL = QLabel(AddNamespace)
        self.lblNamespaceURL.setMinimumSize(QSize(37, 0))
        font = QFont()
        font.setPointSize(10)
        self.lblNamespaceURL.setFont(font)
        self.lblNamespaceURL.setObjectName(_fromUtf8("lblNamespaceURL"))
        self.horizontalLayout_2.addWidget(self.lblNamespaceURL)
        self.lineEditNamespaceURL = QLineEdit(AddNamespace)
        self.lineEditNamespaceURL.setMinimumSize(QSize(300, 0))
        font = QFont()
        font.setPointSize(10)
        self.lineEditNamespaceURL.setFont(font)
        self.lineEditNamespaceURL.setFocusPolicy(Qt.StrongFocus)
        self.lineEditNamespaceURL.setObjectName(_fromUtf8("lineEditNamespaceURL"))
        self.horizontalLayout_2.addWidget(self.lineEditNamespaceURL)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 3)
        self.btnCancel = QPushButton(AddNamespace)
        self.btnCancel.setMinimumSize(QSize(75, 0))
        self.btnCancel.setMaximumSize(QSize(75, 16777215))
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 2, 2, 1, 1)
        self.btnOK = QPushButton(AddNamespace)
        self.btnOK.setEnabled(True)
        self.btnOK.setMinimumSize(QSize(75, 0))
        self.btnOK.setMaximumSize(QSize(75, 16777215))
        self.btnOK.setDefault(True)
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.gridLayout.addWidget(self.btnOK, 2, 1, 1, 1)

        self.retranslateUi(AddNamespace)
        QMetaObject.connectSlotsByName(AddNamespace)

    def retranslateUi(self, AddNamespace):
        AddNamespace.setWindowTitle(_translate("AddNamespace", "Add a new namespace", None))
        self.lblNamespacePrefix.setToolTip(_translate("AddNamespace", "Type a prefix for the new namespace", None))
        self.lblNamespacePrefix.setText(_translate("AddNamespace", "Prefix:", None))
        self.lineEditNamespacePrefix.setToolTip(_translate("AddNamespace", "Type a prefix for the new namespace", None))
        self.lblNamespaceURL.setToolTip(_translate("AddNamespace", "Type a URL for the new namespace", None))
        self.lblNamespaceURL.setText(_translate("AddNamespace", "URI:", None))
        self.lineEditNamespaceURL.setToolTip(_translate("AddNamespace", "Type a URL for the new namespace", None))
        self.lineEditNamespaceURL.setText(_translate("AddNamespace", "http://", None))
        self.btnCancel.setText(_translate("AddNamespace", "Cancel", None))
        self.btnOK.setText(_translate("AddNamespace", "OK", None))

