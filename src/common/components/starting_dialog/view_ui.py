# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'view.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLayout,
    QListView, QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.setWindowModality(Qt.NonModal)
        Dialog.resize(349, 257)
        self.selection_list = QListView(Dialog)
        self.selection_list.setObjectName(u"selection_list")
        self.selection_list.setGeometry(QRect(10, 90, 321, 111))
        self.layoutWidget = QWidget(Dialog)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 242, 71))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushLeft = QPushButton(self.layoutWidget)
        self.pushLeft.setObjectName(u"pushLeft")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushLeft.sizePolicy().hasHeightForWidth())
        self.pushLeft.setSizePolicy(sizePolicy)
        self.pushLeft.setFocusPolicy(Qt.ClickFocus)
        self.pushLeft.setIconSize(QSize(60, 60))
        self.pushLeft.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.pushLeft)

        self.pushCentre = QPushButton(self.layoutWidget)
        self.pushCentre.setObjectName(u"pushCentre")
        sizePolicy.setHeightForWidth(self.pushCentre.sizePolicy().hasHeightForWidth())
        self.pushCentre.setSizePolicy(sizePolicy)
        self.pushCentre.setFocusPolicy(Qt.ClickFocus)
        self.pushCentre.setIconSize(QSize(60, 60))
        self.pushCentre.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.pushCentre)

        self.pushRight = QPushButton(self.layoutWidget)
        self.pushRight.setObjectName(u"pushRight")
        sizePolicy.setHeightForWidth(self.pushRight.sizePolicy().hasHeightForWidth())
        self.pushRight.setSizePolicy(sizePolicy)
        self.pushRight.setFocusPolicy(Qt.ClickFocus)
        self.pushRight.setIconSize(QSize(60, 60))
        self.pushRight.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.pushRight)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
#if QT_CONFIG(tooltip)
        self.pushLeft.setToolTip(QCoreApplication.translate("Dialog", u"exit dialog", None))
#endif // QT_CONFIG(tooltip)
        self.pushLeft.setText("")
#if QT_CONFIG(tooltip)
        self.pushCentre.setToolTip(QCoreApplication.translate("Dialog", u"accept selection", None))
#endif // QT_CONFIG(tooltip)
        self.pushCentre.setText("")
#if QT_CONFIG(tooltip)
        self.pushRight.setToolTip(QCoreApplication.translate("Dialog", u"accept selection", None))
#endif // QT_CONFIG(tooltip)
        self.pushRight.setText("")
    # retranslateUi

