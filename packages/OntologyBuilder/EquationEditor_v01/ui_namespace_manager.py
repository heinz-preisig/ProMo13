"""
Main UI of the namespace manger module

"""
__authors__ = 'Vinay Gautam: drvgautam@github.com'

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(807, 537)
        # MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter|Qt.AlignCenter)
        font = QFont()
        font.setBold(False)
        font.setWeight(50)
        item.setFont(font)
        self.treeWidgetMyModel = QTreeWidget(self.centralwidget)
        self.treeWidgetMyModel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidgetMyModel.setAutoFillBackground(False)
        self.treeWidgetMyModel.setStyleSheet(_fromUtf8("selection-color: rgb(0, 0, 127);"))
        self.treeWidgetMyModel.setFrameShape(QFrame.StyledPanel)
        self.treeWidgetMyModel.setAlternatingRowColors(True)
        self.treeWidgetMyModel.setAnimated(False)
        self.treeWidgetMyModel.setHeaderHidden(True)
        self.treeWidgetMyModel.setObjectName(_fromUtf8("treeWidgetMyModel"))
        self.gridLayout.addWidget(self.treeWidgetMyModel, 1, 0, 1, 1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)

        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.statusbar = QStatusBar(MainWindow)
        font = QFont()
        font.setPointSize(8)
        self.statusbar.setFont(font)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setIconSize(QSize(19, 19))
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.toolBarFunctions = QToolBar(MainWindow)
        self.toolBarFunctions.setEnabled(True)
        self.toolBarFunctions.setIconSize(QSize(46, 60))
        self.toolBarFunctions.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolBarFunctions.setObjectName(_fromUtf8("toolBarFunctions"))
        MainWindow.addToolBar(Qt.RightToolBarArea, self.toolBarFunctions)
        self.actionSelect_endpoint = QAction(MainWindow)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(_fromUtf8(":/images/endpoint.png")), QIcon.Normal, QIcon.Off)
        self.actionSelect_endpoint.setIcon(icon1)
        self.actionSelect_endpoint.setObjectName(_fromUtf8("actionSelect_endpoint"))
        self.actionLoad_model = QAction(MainWindow)
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(_fromUtf8(":/images/load_model.png")), QIcon.Normal, QIcon.Off)
        self.actionLoad_model.setIcon(icon2)
        self.actionLoad_model.setObjectName(_fromUtf8("actionLoad_model"))
        self.actionAbout = QAction(MainWindow)
        icon3 = QIcon()
        icon3.addPixmap(QPixmap(_fromUtf8(":/images/about.png")), QIcon.Normal, QIcon.Off)
        self.actionAbout.setIcon(icon3)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionEdit_namespaces = QAction(MainWindow)
        icon6 = QIcon()
        icon6.addPixmap(QPixmap(_fromUtf8(":/images/namespaces.png")), QIcon.Normal, QIcon.Off)
        self.actionEdit_namespaces.setIcon(icon6)
        self.actionEdit_namespaces.setObjectName(_fromUtf8("actionEdit_namespaces"))
        self.actionEdit_my_models = QAction(MainWindow)
        self.actionEdit_my_models.setObjectName(_fromUtf8("actionEdit_my_models"))
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionToolBarNamespaces = QAction(MainWindow)
        # self.actionToolBarNamespaces.setIcon(icon6)
        self.actionToolBarNamespaces.setObjectName(_fromUtf8("actionToolBarNamespaces"))
        self.actionExport_to_file = QAction(MainWindow)
        self.actionExport_to_file.setEnabled(False)
        icon11 = QIcon()
        icon11.addPixmap(QPixmap(_fromUtf8(":/images/export_graph.png")), QIcon.Normal, QIcon.Off)
        self.actionExport_to_file.setIcon(icon11)
        self.actionExport_to_file.setObjectName(_fromUtf8("actionExport_to_file"))
        self.actionExport_to_file_2 = QAction(MainWindow)
        self.actionExport_to_file_2.setEnabled(False)
        self.actionExport_to_file_2.setIcon(icon11)
        self.actionExport_to_file_2.setObjectName(_fromUtf8("actionExport_to_file_2"))
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExport_to_file)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionToolBarNamespaces)
        self.toolBar.addSeparator()
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "ProMo-semantics", None))
        self.actionSelect_endpoint.setToolTip(_translate("MainWindow", "Select endpoint", None))
        self.actionLoad_model.setText(_translate("MainWindow", "Load model...", None))
        self.actionLoad_model.setToolTip(_translate("MainWindow", "Load my model", None))
        self.actionAbout.setText(_translate("MainWindow", "About...", None))
        self.actionEdit_namespaces.setText(_translate("MainWindow", "Edit namespaces...", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionToolBarNamespaces.setText(_translate("MainWindow", "Namespaces", None))
        self.actionToolBarNamespaces.setToolTip(_translate("MainWindow", "Namespaces", None))
        