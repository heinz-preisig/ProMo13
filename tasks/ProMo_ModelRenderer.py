#!/usr/bin/python3
# encoding: utf-8

"""
Author:  Arne Tobias Elve
What:    Start point for code rendering
Started: Date
Reason:
Status:  Production
Contact: arne.t.elve(at)ntnu.no
"""

import os
import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.ontology_container import OntologyContainer
from TaskBuilder.ModelRenderer.Editor.editor_model_renderer_gui_impl import Ui_ModelFactory
from TaskBuilder.ModelRenderer.main import ModelRenderer

root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])
# cwd = os.getcwd()
# sys.path.append(cwd)

if __name__ == '__main__':
  mode = 'use'
  # mode = 'development back-end'
  # mode = 'development front-end'
  if mode == 'development back-end':

    # Selectables:
    ontology_name = 'HEX_02'
    mod_name = 'cc_HEX_big'
    case_name = 'andreas'
    language = 'python'

    ontology = OntologyContainer(ontology_name)
    ontology_location = ontology.ontology_location
    # model_loc = '{}/models/{}'.format(ontology_location, mod_name)
    mr = ModelRenderer(ontology, mod_name, case_name)
    mr.setup_system(language)
    mr.generate_output()

  else:
    a = QtWidgets.QApplication(sys.argv)
    a.setWindowIcon(QtGui.QIcon("./Common/icons/modelfactory.png"))
    w = Ui_ModelFactory()
    w.setWindowTitle('Model Renderer')
    w.show()
    r = a.exec_()
    sys.exit(r)
