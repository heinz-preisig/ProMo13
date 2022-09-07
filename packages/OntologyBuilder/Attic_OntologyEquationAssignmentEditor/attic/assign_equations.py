# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'assign_equations.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(813, 768)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(100, 0))
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.ForceTabbedDocks|QtWidgets.QMainWindow.VerticalTabs)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(30, 20, 256, 192))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.header().setVisible(False)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(40, 290, 731, 311))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_node = QtWidgets.QWidget()
        self.tab_node.setObjectName("tab_node")
        self.horizontalLayoutWidget_4 = QtWidgets.QWidget(self.tab_node)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(30, 70, 231, 191))
        self.horizontalLayoutWidget_4.setObjectName("horizontalLayoutWidget_4")
        self.horizontalLayoutNode = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayoutNode.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutNode.setObjectName("horizontalLayoutNode")
        self.tabWidget.addTab(self.tab_node, "")
        self.tab_arc = QtWidgets.QWidget()
        self.tab_arc.setObjectName("tab_arc")
        self.horizontalLayoutWidget_5 = QtWidgets.QWidget(self.tab_arc)
        self.horizontalLayoutWidget_5.setGeometry(QtCore.QRect(10, 60, 231, 191))
        self.horizontalLayoutWidget_5.setObjectName("horizontalLayoutWidget_5")
        self.horizontalLayoutToken = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_5)
        self.horizontalLayoutToken.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutToken.setObjectName("horizontalLayoutToken")
        self.horizontalLayoutWidget_6 = QtWidgets.QWidget(self.tab_arc)
        self.horizontalLayoutWidget_6.setGeometry(QtCore.QRect(250, 60, 231, 191))
        self.horizontalLayoutWidget_6.setObjectName("horizontalLayoutWidget_6")
        self.horizontalLayoutMechanism = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_6)
        self.horizontalLayoutMechanism.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutMechanism.setObjectName("horizontalLayoutMechanism")
        self.horizontalLayoutWidget_7 = QtWidgets.QWidget(self.tab_arc)
        self.horizontalLayoutWidget_7.setGeometry(QtCore.QRect(490, 60, 231, 191))
        self.horizontalLayoutWidget_7.setObjectName("horizontalLayoutWidget_7")
        self.horizontalLayoutNature = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_7)
        self.horizontalLayoutNature.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutNature.setObjectName("horizontalLayoutNature")
        self.tabWidget.addTab(self.tab_arc, "")
        self.comboEquationNumberStr = QtWidgets.QComboBox(self.centralwidget)
        self.comboEquationNumberStr.setGeometry(QtCore.QRect(60, 630, 111, 27))
        self.comboEquationNumberStr.setObjectName("comboEquationNumberStr")
        self.comboEquationExpression = QtWidgets.QComboBox(self.centralwidget)
        self.comboEquationExpression.setGeometry(QtCore.QRect(290, 630, 471, 27))
        self.comboEquationExpression.setObjectName("comboEquationExpression")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setOrientation(QtCore.Qt.Vertical)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Process Modeller"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_node), _translate("MainWindow", "node"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_arc), _translate("MainWindow", "arc"))
