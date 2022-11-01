# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'instantiation_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(394, 409)
        self.verticalLayout_6 = QVBoxLayout(Dialog)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tab_variables = QTabWidget(Dialog)
        self.tab_variables.setObjectName(u"tab_variables")
        self.tab_required = QWidget()
        self.tab_required.setObjectName(u"tab_required")
        self.verticalLayout_4 = QVBoxLayout(self.tab_required)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.list_required = QListWidget(self.tab_required)
        self.list_required.setObjectName(u"list_required")

        self.verticalLayout_4.addWidget(self.list_required)

        self.tab_variables.addTab(self.tab_required, "")
        self.tab_others = QWidget()
        self.tab_others.setObjectName(u"tab_others")
        self.verticalLayout_5 = QVBoxLayout(self.tab_others)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.list_others = QListWidget(self.tab_others)
        self.list_others.setObjectName(u"list_others")

        self.verticalLayout_5.addWidget(self.list_others)

        self.tab_variables.addTab(self.tab_others, "")

        self.horizontalLayout.addWidget(self.tab_variables)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_variable_name = QLabel(Dialog)
        self.label_variable_name.setObjectName(u"label_variable_name")

        self.verticalLayout_2.addWidget(self.label_variable_name)

        self.line_edit_value = QLineEdit(Dialog)
        self.line_edit_value.setObjectName(u"line_edit_value")
        self.line_edit_value.setMinimumSize(QSize(100, 25))
        self.line_edit_value.setMaximumSize(QSize(100, 25))

        self.verticalLayout_2.addWidget(self.line_edit_value)

        self.pbutton_instantiate = QPushButton(Dialog)
        self.pbutton_instantiate.setObjectName(u"pbutton_instantiate")
        self.pbutton_instantiate.setMinimumSize(QSize(100, 30))
        self.pbutton_instantiate.setMaximumSize(QSize(100, 30))

        self.verticalLayout_2.addWidget(self.pbutton_instantiate)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pbutton_accept = QPushButton(Dialog)
        self.pbutton_accept.setObjectName(u"pbutton_accept")
        self.pbutton_accept.setMinimumSize(QSize(100, 30))
        self.pbutton_accept.setMaximumSize(QSize(100, 30))

        self.verticalLayout.addWidget(self.pbutton_accept)

        self.pbutton_cancel = QPushButton(Dialog)
        self.pbutton_cancel.setObjectName(u"pbutton_cancel")
        self.pbutton_cancel.setMinimumSize(QSize(100, 30))
        self.pbutton_cancel.setMaximumSize(QSize(100, 30))

        self.verticalLayout.addWidget(self.pbutton_cancel)


        self.verticalLayout_3.addLayout(self.verticalLayout)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout_6.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)

        self.tab_variables.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Instantiation", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Select a variable.", None))
        self.tab_variables.setTabText(self.tab_variables.indexOf(self.tab_required), QCoreApplication.translate("Dialog", u"Required variables (111)", None))
        self.tab_variables.setTabText(self.tab_variables.indexOf(self.tab_others), QCoreApplication.translate("Dialog", u"Others", None))
        self.label_variable_name.setText(QCoreApplication.translate("Dialog", u"var:", None))
        self.pbutton_instantiate.setText(QCoreApplication.translate("Dialog", u"Instantiate", None))
        self.pbutton_accept.setText(QCoreApplication.translate("Dialog", u"Accept", None))
        self.pbutton_cancel.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
    # retranslateUi

