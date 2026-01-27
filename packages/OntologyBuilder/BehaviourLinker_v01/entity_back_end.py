import json
import os
import sys

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from Common.classes.entity import Entity
# from BricksAndTreeSemantics import ONTOLOGY_REPOSITORY
# from BricksAndTreeSemantics import PRIMITIVES
# from OntologyBuilder.BehaviourLinker_v01.BricksAndTreeSemantics import RULES
# from DataModelNoBrickNumbers import DataModel
# from OntologyBuilder.BehaviourLinker_v01.main_automaton import UI_state
# from Utilities import TreePlot
# from Utilities import camelCase
# from Utilities import debugging
from Common.common_resources import getOntologyName
from Common.ontology_container import OntologyContainer
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES



TIMING = False
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

root = os.path.abspath(os.path.join("."))
sys.path.extend([root, os.path.join(root, "resources")])




class EntityEditorBackEnd(QObject):
    message = pyqtSignal(dict)

    def __init__(self, ontology_container):
        super().__init__()
        self.ontology_container = ontology_container

    def process_message(self, message):
        pass