#!/usr/bin/python3
# encoding: utf-8
# !/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 APP for editing graph components used in ModelComposer
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2009. 04. 17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])

from ModelBuilder.GraphComponentEditor.editor_graphcomponents_gui_impl import EditorGraphComponentsDialogImpl

cwd = os.getcwd()
sys.path.append(cwd)

a = QtWidgets.QApplication(sys.argv)
icon_f = "task_graphic_objects.svg"
icon = os.path.join(os.path.abspath("../packages/Common/icons"), icon_f)
a.setWindowIcon(QtGui.QIcon(icon))

w = EditorGraphComponentsDialogImpl()
w.MAIN = a
w.move(QtCore.QPoint(100, 100))
w.show()
a.exec_()
