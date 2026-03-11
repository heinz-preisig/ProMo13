#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
 APP for editing models THE ModelComposer
===============================================================================


"""

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2026. 01. 23"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "12.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

root = os.path.abspath(os.path.join(".."))
sys.path.extend([root,
                 os.path.join(root, 'packages'),
                 os.path.join(root, 'tasks'),
                 os.path.join(root, 'src')
                 ])
# fmt: off
from OntologyBuilder.BehaviourLinker_v01.main_front_end import BehaviourLinkerFrontEnd
from OntologyBuilder.BehaviourLinker_v01.main_back_end import BehaviourLinerBackEnd


# fmt: on
def main():
    icon_f = "task_entity_generation.svg"
    icon = os.path.join(os.path.abspath("../packages/Common/icons"), icon_f)
    QtCore.pyqtRemoveInputHook()
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(icon))

    # Instantiate each once
    frontend = BehaviourLinkerFrontEnd()
    backend = BehaviourLinerBackEnd()

    # Link them together using Signals and Slots
    # F -> B: Button click triggers backend method
    backend.message.connect(frontend.process_main_backend_message)

    # F -> I: Backend signal updates interface label
    frontend.message.connect(backend.process_main_frontend_message)

    backend.load_ontology()

    frontend.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
