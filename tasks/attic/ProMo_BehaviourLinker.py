#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
 APP for editing models THE ModelComposer
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2020. 10. 22"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# TODO: implement stdout and stderr output as command-line arguments

import os
import sys



root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets

# from OntologyBuilder.BehaviourEditor.ui_behaviour_linker_editor_impl import MainWindowImpl
from OntologyBuilder.BehaviourAssociation.ui_behaviour_linker_editor_impl import MainWindowImpl

# QtCore.pyqtRemoveInputHook()
a = QtWidgets.QApplication(sys.argv)

icon_name = "task_bi_partite_constrainer"
icon_file = icon_name+".svg"
icon = os.path.join(os.path.abspath("../packages/Common/icons"), icon_file)
a.setWindowIcon(QtGui.QIcon(icon))
w = MainWindowImpl(icon_name)
w.move(QtCore.QPoint(100, 100))
w.setWindowTitle("Constraining variable/equation bipartite graph")

w.show()
a.exec()
