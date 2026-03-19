"""
testing the namespace interface
"""


import sys

import owlready2
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from rdflib import Graph, util
from rdflib.namespace import NamespaceManager
from shutil import copyfile
from subprocess import Popen
from os import remove, path

from ui_namespace_manager import Ui_MainWindow
from ui_namespace_editor_impl import Ui_Preferences
# from addMymodelUI import Ui_AddMyModel
from ui_namespace_editor import Ui_AddNamespace
# from addEndpointUI import Ui_AddEndpoint

from OntologyBuilder.OntologyEquationEditor.ui_namespace_test import Ui_Form
from OntologyBuilder.OntologyEquationEditor.ui_namespace_manager_impl import PreferencesDialog

from OntologyBuilder.OntologyEquationEditor.namespace_manager_utils import getListOfNamespaces, deleteNamespaceFromDatabase, addEntryToLog


from rdflib import Graph

# from owlready2 import *


class Main(QMainWindow):


  # Main window constructor
  def __init__(self):
    QMainWindow.__init__(self)
    self.ui = Ui_Form()
    self.ui.setupUi(self)

    self.ui.tableWidgetKnownNamespaces.clicked.connect(self.selectNameSpace)

    # URL_DB = getEndpointName()
    listOfNamespaces = getListOfNamespaces()
    self.cleanTable(listOfNamespaces)

    self.loadNamespacesToTable()
    self.gugus()

  def loadNamespacesToTable(self):
    # Clear table
    self.ui.tableWidgetKnownNamespaces.setRowCount(0)

    # Load known namespaces from DB
    namespaces = getListOfNamespaces()

    # Put the to table
    for namespace in namespaces:
      # Add an empty row to the table
      rowPosition = self.ui.tableWidgetKnownNamespaces.rowCount()
      self.ui.tableWidgetKnownNamespaces.insertRow(rowPosition)

      # Insert the namespace
      self.ui.tableWidgetKnownNamespaces.setItem(rowPosition, 0, QTableWidgetItem(str(namespace[0])))
      self.ui.tableWidgetKnownNamespaces.setItem(rowPosition, 1, QTableWidgetItem(str(namespace[1])))

      header = self.ui.tableWidgetKnownNamespaces.horizontalHeader()
      header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
      header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

  def selectNameSpace(self):
    pass

  def cleanTable(self, listOfNamespaces ):

    from requests import get, Timeout

    # row =    self.ui.tableWidgetKnownNamespaces.currentRow()
    # item = self.ui.tableWidgetKnownNamespaces.item(row,1)
    # prefix = str(self.ui.tableWidgetKnownNamespaces.item(row,0).text())
    #
    # Url = (item.text())
    # print("select name space", row, item.text())

    # Url = "https://github.com/emmo-repo/EMMO/blob/master/middle/materials.ttl"

    # onto = get_ontology(Url)
    #
    # try:
    #   onto.load()
    #
    #   classes = onto.classes()
    #   individuals = onto.individuals()

    for prefix, Url in listOfNamespaces:


      try:
        print("try to access %s"%Url)
        response = get(Url,timeout=3)
        res = response.status_code
      except:
        print("error -- cannot access")
        self.updateLibrary(prefix)
        res = 400
        # break
      # try:
      #   print("try again to access %s"%Url)
      #   response = get(Url,timeout=3)
      #   res = response.status_code
      # except Timeout:
      #   print("connection timed out")
      #   res = -1
      #     # break

      if res == 200:
        print('Web site exists')
        r = self.analyseGraph(prefix, Url)
        if r != 1:
          self.updateLibrary(prefix)
        # break
      else:
        print('Web site does not exist')
        self.updateLibrary(prefix)
        # break

    return



  def analyseGraph(self, prefix, Url):

    p1 = " http://www.w3.org/2000/01/rdf-schema#label"

    subj = set()
    pred = set()
    obje = set()

    try:
      onto = Graph()
      onto.load(Url, format="ttl")

      for s,p,o in onto.triples((None,None,None)):
        print(s,p,o)
        subj.add(s)
        pred.add(p)
        obje.add(o)

      with open("./data/%s-subj.txt"%prefix, 'w') as f:
        for l in sorted(subj):
          f.write("\n%s" % l)
      with open("./data/%s-pred.txt"%prefix, 'w') as f:
        for l in sorted(pred):
          f.write("\n%s" % l)
      with open("./data/%s-obj.txt"%prefix, 'w') as f:
        for l in sorted(obje):
          f.write("\n%s" % l)
      return 1

    except:
      print("cannot load:", Url)
      res = -2
      try:
        onto = owlready2.get_ontology(Url)
        res = 2
      except:
        print("cannot get owl file")
        res = -3
    return res


  def updateLibrary(self, prefix):
      deleteNamespaceFromDatabase(prefix)

      # Log
      addEntryToLog("Namespace " + prefix + " was deleted")

      self.loadNamespacesToTable()
    #   return

      # for c in classes:
      #   print(c)
      # for c in individuals:
      #   print(c)

      # setSettingToDB('endpoint_url', str(Url))


      # l = getListOfMyModelNamesFromDB()
      # print("here")

    # except:
    #   print("cannot load")
    #   return



  def on_bush_LoadNameSpaceTable_pressed(self):

    dialog = PreferencesDialog(3)
    #
    # dialog.exec_()
    #
    # del dialog


  def gugus(self):
    print("gugus")


if __name__ == '__main__':
  app = QApplication(sys.argv)

  window = Main()
  window.show()

  app.exec()