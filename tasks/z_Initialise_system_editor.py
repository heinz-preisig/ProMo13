#!/usr/bin/python3
# encoding: utf-8
"""

"""
# __docformat__ = "restructuredtext en"

import os
import sys

root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])

from PyQt5 import QtGui, QtWidgets

from ModelBuilder.z_Initialise_system_editor.Editor.editor_initialise_system_gui_impl import Ui_Initialise_system

# cwd = os.getcwd()
# sys.path.append(cwd)

if __name__ == '__main__':
  # mode = 'use'
  # mode = 'development ModelFactory'
  # if mode == 'development ModelFactory':
  #   ontology_name = 'Ball_02'
  #   ontology = OntologyContainer(ontology_name)
  #   ontology_location = ontology.onto_path
  #   mod_name = 'ball_fall'
  #   language = 'python'
  #   model_loc = '{}/models/{}'.format(ontology_location, mod_name)
  #   mf = ModelFactory(ontology, mod_name, language, model_loc)
  #   mf.produce_code()
  # else:
  a = QtWidgets.QApplication(sys.argv)
  a.setWindowIcon(QtGui.QIcon("./Common/icons/otter.png"))
  w = Ui_Initialise_system()
  w.setWindowTitle('Initialise system')
  w.show()
  r = a.exec_()
  sys.exit(r)
