"""
useProMo_TaskFactory ontology_name model_name
"""
from CodeGenerator.ui_code_generator_impl import Ui_CodeGenerator

#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
 APP for editing base (foundation) ontology
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2025. 12. 11"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "0.12"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

root = os.path.abspath(os.path.join(".."))
sys.path.extend([
        root,
                 os.path.join(root, 'packages'),
                 os.path.join(root, 'tasks')])

from PyQt5 import QtGui, QtWidgets, QtCore

print(sys.path)

from CodeGenerator.ui_code_generator_impl import UiCodeGenerator


a = QtWidgets.QApplication(sys.argv)
icon_f = "task_ontology_foundation.svg"
icon = os.path.join(os.path.abspath("../packages/Common/icons"), icon_f)
a.setWindowIcon(QtGui.QIcon(icon))

w = UiCodeGenerator()
w.MAIN = a
w.move(QtCore.QPoint(100, 100))
w.show()
a.exec_()



# import sys
#
# file_path = "../src/code_generator/code_generator.py"
# args = sys.argv[1:]  # Exclude the script name from the arguments
#
# with open(file_path, "r") as file:
#   code = file.read()
#
# # Modify the code to use the command-line arguments
# modified_code = f"import sys\nsys.argv = {args}\n{code}"
#
# exec(modified_code)
