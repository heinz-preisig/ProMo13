#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 ontology container as an RDF graph
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2023. 08. 23"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__version__ = "7.00"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from csv import writer

from Common.common_resources import getOntologyName
from Common.resource_initialisation import FILES

if __name__ == '__main__':
  from PyQt5.QtCore import QObject
  from PyQt5.QtWidgets import QApplication
  from PyQt5.QtWidgets import QWidget


  class Worker(QObject):
    from PyQt5 import QtCore
    finished = QtCore.pyqtBoundSignal()

    def writeCSVfile(self):

      from Common.exchange_board import OntologyContainer

      self.ontology_name = getOntologyName(task="task_ONTO_to_CSV")

      ontology_container = OntologyContainer(self.ontology_name)
      tokens = ontology_container.tokens
      variables = ontology_container.variables
      indices = ontology_container.indices
      equation_dictionary = ontology_container.equation_dictionary
      networks = ontology_container.networks
      interconnections = ontology_container.list_inter_branches_pairs

      extract = ["label",
                 "type",
                 "network",
                 "doc",
                 # "index_structures",
                 "units",
                 "IRI",
                 # "equation_list",
                 # "aliases",
                 # "token"
                 ]

      csv_data = {}
      for nw in networks:
        csv_data[nw] = []

      for v in variables:
        nw = variables[v]["network"]
        if nw not in interconnections:
          l = []
          for h in extract:
            l.extend([str(variables[v][h])])
          csv_data[nw].append(l)

      for nw in csv_data:
        if csv_data[nw]:
          csv_file = FILES["CSV_variable_file"] % (self.ontology_name,nw)
          with open(csv_file, "w", encoding="UTF8", newline="") as f:
            w = writer(f)
            w.writerow(extract)
            w.writerows(csv_data[nw])

      self.finished.emit()


  class MainWindow(QWidget):
    def __init__(self):
      super().__init__()
      self.worker = Worker()
      self.worker.writeCSVfile()
      self.worker.finished.connect(self.close)


  app = QApplication([])
  window = MainWindow()
  app.exec_()
