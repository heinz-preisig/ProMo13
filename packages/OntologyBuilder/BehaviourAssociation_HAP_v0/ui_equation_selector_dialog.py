# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_equation_selector_dialog.ui'
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
        Dialog.resize(714, 670)
        self.verticalLayout_4 = QVBoxLayout(Dialog)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(368, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.check_box_show_all_vars = QCheckBox(Dialog)
        self.check_box_show_all_vars.setObjectName(u"check_box_show_all_vars")

        self.horizontalLayout.addWidget(self.check_box_show_all_vars)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.list_variables = QListWidget(Dialog)
        self.list_variables.setObjectName(u"list_variables")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_variables.sizePolicy().hasHeightForWidth())
        self.list_variables.setSizePolicy(sizePolicy)
        self.list_variables.setMinimumSize(QSize(0, 64))
        self.list_variables.setMaximumSize(QSize(16777215, 64))
        self.list_variables.setFocusPolicy(Qt.NoFocus)
        self.list_variables.setLayoutDirection(Qt.LeftToRight)
        self.list_variables.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_variables.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.list_variables.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.list_variables.setProperty("showDropIndicator", True)
        self.list_variables.setDefaultDropAction(Qt.CopyAction)
        self.list_variables.setSelectionMode(QAbstractItemView.NoSelection)
        self.list_variables.setFlow(QListView.LeftToRight)
        self.list_variables.setViewMode(QListView.ListMode)

        self.verticalLayout_4.addWidget(self.list_variables)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tab_equations = QTabWidget(Dialog)
        self.tab_equations.setObjectName(u"tab_equations")
        self.tab_equations.setMinimumSize(QSize(600, 543))
        self.tab_equations.setFocusPolicy(Qt.TabFocus)
        self.tab_explicit = QWidget()
        self.tab_explicit.setObjectName(u"tab_explicit")
        self.verticalLayout = QVBoxLayout(self.tab_explicit)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.list_explicit = QListWidget(self.tab_explicit)
        self.list_explicit.setObjectName(u"list_explicit")
        self.list_explicit.setFocusPolicy(Qt.NoFocus)
        self.list_explicit.setFrameShadow(QFrame.Sunken)
        self.list_explicit.setDefaultDropAction(Qt.IgnoreAction)
        self.list_explicit.setSelectionMode(QAbstractItemView.NoSelection)

        self.verticalLayout.addWidget(self.list_explicit)

        self.tab_equations.addTab(self.tab_explicit, "")
        self.tab_implicit = QWidget()
        self.tab_implicit.setObjectName(u"tab_implicit")
        self.verticalLayout_2 = QVBoxLayout(self.tab_implicit)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.list_implicit = QListWidget(self.tab_implicit)
        self.list_implicit.setObjectName(u"list_implicit")
        self.list_implicit.setFocusPolicy(Qt.NoFocus)
        self.list_implicit.setDefaultDropAction(Qt.IgnoreAction)
        self.list_implicit.setSelectionMode(QAbstractItemView.NoSelection)

        self.verticalLayout_2.addWidget(self.list_implicit)

        self.tab_equations.addTab(self.tab_implicit, "")

        self.horizontalLayout_2.addWidget(self.tab_equations)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pbutton_save = QPushButton(Dialog)
        self.pbutton_save.setObjectName(u"pbutton_save")

        self.verticalLayout_3.addWidget(self.pbutton_save)

        self.pbutton_discard = QPushButton(Dialog)
        self.pbutton_discard.setObjectName(u"pbutton_discard")

        self.verticalLayout_3.addWidget(self.pbutton_discard)

        self.verticalSpacer_2 = QSpacerItem(20, 348, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.pbutton_accept = QPushButton(Dialog)
        self.pbutton_accept.setObjectName(u"pbutton_accept")

        self.verticalLayout_3.addWidget(self.pbutton_accept)

        self.pbutton_cancel = QPushButton(Dialog)
        self.pbutton_cancel.setObjectName(u"pbutton_cancel")

        self.verticalLayout_3.addWidget(self.pbutton_cancel)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Dialog)

        self.tab_equations.setCurrentIndex(1)
        self.pbutton_cancel.setDefault(True)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Equation selector", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Select a variable.", None))
        self.check_box_show_all_vars.setText(QCoreApplication.translate("Dialog", u"Show all variables.", None))
        self.tab_equations.setTabText(self.tab_equations.indexOf(self.tab_explicit), QCoreApplication.translate("Dialog", u"Explicit Equations (0)", None))
        self.tab_equations.setTabText(self.tab_equations.indexOf(self.tab_implicit), QCoreApplication.translate("Dialog", u"Implicit Equations (0)", None))
        self.pbutton_save.setText(QCoreApplication.translate("Dialog", u"Save", None))
        self.pbutton_discard.setText(QCoreApplication.translate("Dialog", u"Discard", None))
        self.pbutton_accept.setText(QCoreApplication.translate("Dialog", u"Accept", None))
        self.pbutton_cancel.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
    # retranslateUi

