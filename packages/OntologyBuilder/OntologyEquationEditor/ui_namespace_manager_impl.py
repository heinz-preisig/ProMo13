"""
Implementation logic of the namespace manager utility
"""
__authors__ = 'Vinay Gautam: drvgautam@github.com'

import sys
import namespace_manager_utils
# from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QMessageBox, QFileDialog

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

class Main(QMainWindow):
    graph = Graph()
    myModelName = ''
    changesMadeToModel = False

    # Main window constructor
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        self.ui.actionEdit_namespaces.triggered.connect(self.showNamespacesPreferences)
        self.ui.actionToolBarNamespaces.triggered.connect(self.showNamespacesPreferences)


        self.ui.actionExit.triggered.connect(self.close)


        # Context Menu connections
        self.ui.treeWidgetMyModel.customContextMenuRequested.connect(lambda: namespace_manager_utils.openContextMenuInTree(self.ui.treeWidgetMyModel, self, self.getGraph()))

    
        # CONSTRUCT UI ELEMENTS
        itemEndpoint = QTableWidgetItem(namespace_manager_utils.getEndpointName())
        itemEndpoint.setTextAlignment(Qt.AlignHCenter)
    

       

    def getGraph(self):
        return self.graph

    def setGraph(self, newGraph):
        self.graph = newGraph

    def getMyModelName(self):
        return self.myModelName

    def setMyModelName(self, newName):
        self.myModelName = newName

    def getChangesMadeToModel(self):
        return self.changesMadeToModel

    def setChangesMadeToModel(self, bool_to_set):
        self.changesMadeToModel = bool_to_set



    def showEnrichInstanceWizard(self):
        # Check if user has loaded a my_model yet
        if self.getMyModelName() == '':
            # Show message box with error
            QMessageBox.critical(self, 'Error', "Please load a model first.", QMessageBox.Close)

            self.showMyModelsPreferences()

            return

        # If there are no instances in the graph, stop
        if len(namespace_manager_utils.getAllInstancesFromGraph(self.getGraph())) == 0:
            # Show message box with error)
            QMessageBox.critical(self, 'Error', "Model <span style='font-size:9pt; font-weight:550; color:#58ae82;'>" + self.getMyModelName() + "</span> does not have any instances.", QMessageBox.Close)
            return


    def showNamespacesPreferences(self):
        dialog = PreferencesDialog(3)

        dialog.exec_()

        del dialog

        # Reload Graph area
        # self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showMappingPreferences(self):
        dialog = PreferencesDialog(4)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showDialogPreferences(self):

        dialog = PreferencesDialog(0)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())

    def showDatabasePreferences(self):
        dialog = PreferencesDialog(6)

        dialog.exec_()

        del dialog

        # Reload Graph area
        self.loadMyModelToTree(self.getGraph(), self.getMyModelName())


class PreferencesDialog(QDialog):

    def __init__(self, tabIndex):
        QDialog.__init__(self)
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.ui.btnClearLog.clicked.connect(self.clearLogEntries)
        self.ui.btnAddNamespace.clicked.connect(self.showDialogAddNamespaces)
        self.ui.btnDeleteNamespace.clicked.connect(self.deleteNamespace)
        self.ui.btnRestoreDefaultNamespaces.clicked.connect(self.restoreDefaultNamespaces)
        self.ui.tableWidgetKnownNamespaces.itemDoubleClicked.connect(lambda: self.ui.tableWidgetKnownNamespaces.editItem(self.ui.tableWidgetKnownNamespaces.currentItem()))
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnExportDatabase.clicked.connect(self.exportDatabase)
        self.ui.btnImportDatabase.clicked.connect(self.importDatabase)
        self.ui.btnResetToDefaultDatabase.clicked.connect(self.restoreDatabaseToDefault)
        self.ui.tableWidgetKnownNamespaces.cellChanged.connect(self.editNamespaceInDB)

        # Show the requested tab
        self.tabIndex = tabIndex
        self.ui.tabWidgetPreferences.setCurrentIndex(self.tabIndex)

        # Context Menu connections
        self.ui.tableWidgetKnownNamespaces.customContextMenuRequested.connect(self.openContextMenuNamespacesTable)


        # Load tables
        self.loadAllTablesInPreferences()

    def loadAllTablesInPreferences(self):


        # Load log entries from DB to table
        self.loadLogEntriesToTable()

        # Load namespaces from DB to table
        self.loadNamespacesToTable()


        # Load database stats from DB to table
        self.loadDatabaseStatisticsToTable()

        # Make my model progressbar invisible
        self.ui.progressBarLoad.setVisible(False)


    def loadSameAsOptionSetting(self):

        self.ui.comboBoxSameAsOption.setCurrentIndex(self.ui.comboBoxSameAsOption.findText(namespace_manager_utils.getSettingFromDB('sameas_option')))

    def loadEquivalentPropertyOptionSetting(self):
        if namespace_manager_utils.getSettingFromDB('equivalent_property_option') == 1:
            self.ui.checkBoxPropertyEquivalentToOption.setChecked(True)
        else:
            self.ui.checkBoxPropertyEquivalentToOption.setChecked(False)

    def loadLabelOptionSetting(self):
        if namespace_manager_utils.getSettingFromDB('label_option') == 1:
            self.ui.checkBoxLabelOption.setChecked(True)
        else:
            self.ui.checkBoxLabelOption.setChecked(False)

    def loadCheckForUpdatesOptionSetting(self):
        if namespace_manager_utils.getSettingFromDB('auto_update') == 1:
            self.ui.checkBoxCheckForUpdatesAtStartupOption.setChecked(True)
        else:
            self.ui.checkBoxCheckForUpdatesAtStartupOption.setChecked(False)

   

    # LOG TAB FUNCTIONS
    def loadLogEntriesToTable(self):
        # Clear table
        self.ui.tableWidgetLogEntries.setRowCount(0)

        # Load log entries from DB
        entries = namespace_manager_utils.getListOfLogEntries()

        # Put the entry to table
        for entry in entries:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetLogEntries.rowCount()
            self.ui.tableWidgetLogEntries.insertRow(rowPosition)

            # Insert the endpoint
            self.ui.tableWidgetLogEntries.setItem(rowPosition, 0, QTableWidgetItem(entry[0]))
            self.ui.tableWidgetLogEntries.setItem(rowPosition, 1, QTableWidgetItem(entry[1]))

        # Highlight the first entry
        self.ui.tableWidgetLogEntries.selectRow(self.ui.tableWidgetLogEntries.rowCount() - 1)

         # Sort table
        self.ui.tableWidgetLogEntries.sortItems(0, QtCore.Qt.DescendingOrder) # latest entry will appear as first

    def clearLogEntries(self):
        # Clear table
        self.ui.tableWidgetLogEntries.setRowCount(0)

        # Delete entries from DB table
        namespace_manager_utils.clearLog()

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    # NAMESPACES TAB FUNCTIONS
    def showDialogAddNamespaces(self):
        dialog = AddNamespaceDialog()

        dialog.exec_()

        del dialog

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

        # Reload Graph area
        # window.loadMyModelToTree(window.getGraph(), window.getMyModelName())

    def loadNamespacesToTable(self):
        # Clear table
        self.ui.tableWidgetKnownNamespaces.setRowCount(0)

        # Load known namespaces from DB
        namespaces = namespace_manager_utils.getListOfNamespaces()

        # Put the to table
        for namespace in namespaces:
            # Add an empty row to the table
            rowPosition = self.ui.tableWidgetKnownNamespaces.rowCount()
            self.ui.tableWidgetKnownNamespaces.insertRow(rowPosition)

            # Insert the namespace
            self.ui.tableWidgetKnownNamespaces.setItem(rowPosition, 0, QTableWidgetItem(str(namespace[0])))
            self.ui.tableWidgetKnownNamespaces.setItem(rowPosition, 1, QTableWidgetItem(str(namespace[1])))

    def restoreDefaultNamespaces(self):

        # Delete all namespaces from db
        query = 'DELETE FROM namespaces'
        namespace_manager_utils.executeSQLSubmit(query)

        # Copy backup
        query = 'INSERT INTO namespaces SELECT * FROM namespaces_backup'

        namespace_manager_utils.executeSQLSubmit(query)

        # Log
        namespace_manager_utils.addEntryToLog("Default namespaces were restored")

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

        # window.loadMyModelToTree(window.getGraph(), window.getMyModelName())

    def deleteNamespace(self):
        # If no selection has been made
        if self.ui.tableWidgetKnownNamespaces.currentRow() == -1:
            # Show message box with error
            QMessageBox.critical(self, 'Error', "Please select a namespace from the list.", QMessageBox.Close)

            return

        # Take the namespace selected from table
        prefix = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0).text()

        namespace_manager_utils.deleteNamespaceFromDatabase(prefix)

        # Log
        namespace_manager_utils.addEntryToLog("Namespace " + prefix + " was deleted")

        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

        # Reset namespaces in my graph's namespace manager, so it can be populated again with the correct DB values
        window.graph.namespace_manager = NamespaceManager(Graph())


    # DATABASE TAB FUNCTIONS

    def loadDatabaseStatisticsToTable(self):

        self.ui.tableWidgetDatabaseStats.setItem(0, 0, QTableWidgetItem(str(len(namespace_manager_utils.getListOfNamespaces()))))
        self.ui.tableWidgetDatabaseStats.setItem(0, 1, QTableWidgetItem(str(len(namespace_manager_utils.getListOfLogEntries()))))

    def exportDatabase(self):
        fileNameAndPath = QFileDialog().getSaveFileName(self, "Export database to file", "", '*.sqlite')

        try:
            filePath = '/'.join(str(fileNameAndPath).split('/')[:-1])
        except UnicodeEncodeError:
            QMessageBox.critical(self, 'Error', "Export failed.\nPlease select a filename and path with latin characters.", QMessageBox.Close)
            return

        if fileNameAndPath != "":

            # Copy database to directory
            copyfile('database/myDB.sqlite', fileNameAndPath)

            QMessageBox.information(self, 'Success', "Current database was successfully saved in\n " + filePath + ".", QMessageBox.Close)

        #Log
        namespace_manager_utils.addEntryToLog("Current database was exported in " + filePath)
        # Reload all tables in preferences
        self.loadAllTablesInPreferences()

    def importDatabase(self):
        # Select database file to import
        fileNameAndPath = QFileDialog().getOpenFileName(self, "Select a database to import", "", '*.sqlite')

        if fileNameAndPath != "":

            try:
                test = str(fileNameAndPath)
            except UnicodeEncodeError:
                QMessageBox.critical(self, 'Error', "Import failed.\nPlease select a filename and path with latin characters.", QMessageBox.Close)
                return

            # Check if database is valid (with queries)
            if namespace_manager_utils.checkIfnamespaceManagerDatabase(str(fileNameAndPath)) == False:
                QMessageBox.critical(self, 'Error', "Not a database file.\nOperation cancelled.", QMessageBox.Close)
                return

            # Copy new database
            copyfile(fileNameAndPath, 'database/myDB.sqlite')
            QMessageBox.information(self, 'Success', "Selected database was successfully imported.", QMessageBox.Close)

            # Set selected endpoint DBpedia
            namespace_manager_utils.setSettingToDB('endpoint_url', 'https://dbpedia.org/sparql')

            #Log
            # Functions.addEntryToLog("Selected database was imported in tool")

            # Reload all tables in preferences
            self.loadAllTablesInPreferences()

    def restoreDatabaseToDefault(self):
        # Ask user first if they are sure
        reply = QMessageBox.question(self, 'Restore default database', "Are you sure you want to reset the database?\nAll changes will be lost.", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:

            # Set selected endpoint DBpedia
            namespace_manager_utils.setSettingToDB('endpoint_url', 'https://dbpedia.org/sparql')

            # Copy default database
            copyfile('database/myDB_default.sqlite', 'database/myDB.sqlite')

            QMessageBox.information(self, 'Success', "Default database was successfully restored.", QMessageBox.Close)

            # Reload all tables in preferences
            self.loadAllTablesInPreferences()

    def openContextMenuNamespacesTable(self):

        if self.ui.tableWidgetKnownNamespaces.rowCount() == 0:
            return

        selected_prefix = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0).text()
        selected_url = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 1).text()

        menu = QMenu()

        # Add general Namespace functions to menu

        # Add an Add namespace action
        menu.addAction("Add namespace...").triggered.connect(self.showDialogAddNamespaces)

        # Add a Delete namespace action
        menu.addAction("Delete namespace").triggered.connect(self.deleteNamespace)

        # Add a Restore default namespaces action
        menu.addAction("Restore default namespaces").triggered.connect(self.restoreDefaultNamespaces)

        # Add a separator
        menu.addSeparator()

        # If a namespace prefix is selected
        if self.ui.tableWidgetKnownNamespaces.currentColumn() == 0:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit prefix")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownNamespaces.editItem(self.ui.tableWidgetKnownNamespaces.currentItem()))
            edit_action.setFont(QFont("Segoe UI", -1, QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy prefix to clipboard").triggered.connect(lambda: namespace_manager_utils.copyTextToClipBoard(selected_prefix))

        # If a namespace url is selected
        elif self.ui.tableWidgetKnownNamespaces.currentColumn() == 1:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit URI")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownNamespaces.editItem(self.ui.tableWidgetKnownNamespaces.currentItem()))
            edit_action.setFont(QFont("Segoe UI", -1, QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy namespace to clipboard").triggered.connect(lambda: namespace_manager_utils.copyTextToClipBoard(selected_url))

            # Add an action and connect it with the appropriate function when triggered
            menu.addAction("View namespace in browser").triggered.connect(lambda: namespace_manager_utils.openLinkToBrowser(selected_url))

        position = QCursor.pos()

        menu.exec_(position)

    def openContextMenuEndpointsTable(self):

        if self.ui.tableWidgetKnownEndpoints.rowCount() == 0:
            return

        selected_name = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()
        selected_url = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1).text()

        menu = QMenu()

        # Add general Namespace functions to menu
        # Add an Add endpoint action
        menu.addAction("Add endpoint...").triggered.connect(self.showDialogAddEndpoint)

        # Add a Delete endpoint action
        delete_action = menu.addAction("Delete endpoint")
        delete_action.triggered.connect(self.deleteEndpoint)
        #currentEndpointName = Functions.getEndpointName()

        # Add a Select endpoint action with bold font
        select_action = menu.addAction("Select endpoint")
        select_action.triggered.connect(self.btnSelectEndpoint_clicked)

        # Add a separator
        menu.addSeparator()

        # If an endpoint name is selected
        if self.ui.tableWidgetKnownEndpoints.currentColumn() == 0:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit name")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownEndpoints.editItem(self.ui.tableWidgetKnownEndpoints.currentItem()))
            edit_action.setFont(QFont("Segoe UI", -1, QFont.Bold, False))

            # If the right-clicked name is the current name, editing should not be allowed
            if selected_name == namespace_manager_utils.getEndpointName() or selected_name == 'DBpedia':
                edit_action.setEnabled(False)

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy name to clipboard").triggered.connect(lambda: namespace_manager_utils.copyTextToClipBoard(selected_name))

        # If a endpoint url is selected
        elif self.ui.tableWidgetKnownEndpoints.currentColumn() == 1:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit URI")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetKnownEndpoints.editItem(self.ui.tableWidgetKnownEndpoints.currentItem()))
            edit_action.setFont(QFont("Segoe UI", -1, QFont.Bold, False))

            # If the right-clicked name is the current name, editing should not be allowed
            if selected_url == namespace_manager_utils.getEndpointURL() or selected_name == 'DBpedia':
                edit_action.setEnabled(False)
                delete_action.setEnabled(False)

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy URI to clipboard").triggered.connect(lambda: namespace_manager_utils.copyTextToClipBoard(selected_url))

            # Add an action and connect it with the appropriate function when triggered
            menu.addAction("View endpoint in browser").triggered.connect(lambda: namespace_manager_utils.openLinkToBrowser(selected_url))

        position = QCursor.pos()

        menu.exec_(position)

    def openContextMenuMyModelsTable(self):

        if self.ui.tableWidgetMyModels.rowCount() == 0:
            return

        selected_name = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0).text()
        selected_url = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 1).text()

        menu = QMenu()

        # Add general Namespace functions to menu
        # Add an Add model action
        menu.addAction("Add model...").triggered.connect(self.showDialogAddMyModel)

        # Add a Delete endpoint action
        menu.addAction("Delete model").triggered.connect(self.deleteMyModel)

        # Add a Select my model action with bold font
        select_action = menu.addAction("Load model")
        select_action.triggered.connect(self.loadMyModel)

        # Add a separator
        menu.addSeparator()

        # If a My model name is selected
        if self.ui.tableWidgetMyModels.currentColumn() == 0:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit name")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetMyModels.editItem(self.ui.tableWidgetMyModels.currentItem()))
            edit_action.setFont(QFont("Segoe UI", -1, QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy name to clipboard").triggered.connect(lambda: namespace_manager_utils.copyTextToClipBoard(selected_name))

        # If a My model url is selected
        elif self.ui.tableWidgetMyModels.currentColumn() == 1:

            # Add an action and connect it with the appropriate function when triggered
            edit_action = menu.addAction("Edit URI")
            edit_action.triggered.connect(lambda: self.ui.tableWidgetMyModels.editItem(self.ui.tableWidgetMyModels.currentItem()))
            edit_action.setFont(QFont("Segoe UI", -1, QFont.Bold, False))

            # Add a separator
            menu.addSeparator()

            # Add a Copy action
            menu.addAction("Copy URI to clipboard").triggered.connect(lambda: namespace_manager_utils.copyTextToClipBoard(selected_url))

            # Add an action to open model in browser and connect it with the appropriate function when triggered
            view_in_browser_action = menu.addAction("View model in browser")
            view_in_browser_action.triggered.connect(lambda: namespace_manager_utils.openLinkToBrowser(selected_url))

            if 'http' not in selected_url:
                view_in_browser_action.setEnabled(False)

        position = QCursor.pos()

        menu.exec_(position)

    def openContextMenuMappingsTable(self):

        if self.ui.tableWidgetKnownMappings.rowCount() == 0:
            return

        menu = QMenu()

        # Add delete mapping function to menu
        menu.addAction("Delete mapping").triggered.connect(self.deleteMapping)

        # Add delete all mappings function to menu
        menu.addAction("Delete all mappings").triggered.connect(self.deleteAllMappings)

        position = QCursor.pos()

        menu.exec_(position)

    def editNamespaceInDB(self):

        if self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0) is None or self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 1) is None:
            return

        current_prefix = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 0).text()
        current_url = self.ui.tableWidgetKnownNamespaces.item(self.ui.tableWidgetKnownNamespaces.currentRow(), 1).text()

        try:
            str(current_prefix)
            str(current_url)
        except UnicodeEncodeError:
            # Show error
            QMessageBox.critical(self, 'Error', "Please use only latin characters.", QMessageBox.Close)

            # Reload table
            self.loadNamespacesToTable()
            return

        # If a namespace prefix is changed
        if self.ui.tableWidgetKnownNamespaces.currentColumn() == 0:

            # If the whole text was deleted from prefix
            if len(current_prefix) == 0:

                # Show error message
                QMessageBox.critical(self, 'Error', "Prefix cannot be empty", QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            # If new prefix already exists in DB
            if current_prefix in namespace_manager_utils.getListOfNamespacePrefixesFromDB():
                # Show error message
                QMessageBox.critical(self, 'Error', "Prefix already exists in the list", QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            namespace_manager_utils.updatePrefixOfNamespaceInDatabase(current_prefix, current_url)

        # If a namespace url is changed
        elif self.ui.tableWidgetKnownNamespaces.currentColumn() == 1:

            # If the whole text was deleted from url
            if len(current_url) == 0:
                # Show error message
                QMessageBox.critical(self, 'Error', "URL cannot be empty", QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            # If new url already exists in DB
            if current_url in namespace_manager_utils.getListOfNamespaceUrlsFromDB():
                # Show error message
                QMessageBox.critical(self, 'Error', "URL already exists in the list", QMessageBox.Close)

                # Reload table
                self.loadNamespacesToTable()

                return

            namespace_manager_utils.updateUrlOfNamespaceInDatabase(current_prefix, current_url)

    def editEndpointInDB(self):

        if self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0) is None or self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1) is None:
            return

        current_name = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 0).text()
        current_url = self.ui.tableWidgetKnownEndpoints.item(self.ui.tableWidgetKnownEndpoints.currentRow(), 1).text()

        try:
            str(current_name)
            str(current_url)
        except UnicodeEncodeError:
            # Show error
            QMessageBox.critical(self, 'Error', "Please use only latin characters.", QMessageBox.Close)

            # Reload table
            self.loadEndpointsToTable()
            return

        # If the endpoint name is changed
        if self.ui.tableWidgetKnownEndpoints.currentColumn() == 0:

            # If the whole text was deleted from name
            if len(current_name) == 0:

                # Show error message
                QMessageBox.critical(self, 'Error', "Name cannot be empty", QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            # If new name already exists in DB
            if current_name in namespace_manager_utils.getListOfEndpointNamesFromDB():
                # Show error message
                QMessageBox.critical(self, 'Error', "Name already exists in the list", QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            namespace_manager_utils.updateNameOfEndpointInDatabase(current_name, current_url)

        # If the endpoint url is changed
        elif self.ui.tableWidgetKnownEndpoints.currentColumn() == 1:

            # If the whole text was deleted from url
            if len(current_url) == 0:
                # Show error message
                QMessageBox.critical(self, 'Error', "Endpoint URL cannot be empty", QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            # If new url already exists in DB
            if current_url in namespace_manager_utils.getListOfEndpointUrlsFromDB():
                # Show error message
                QMessageBox.critical(self, 'Error', "URL already exists in the list", QMessageBox.Close)

                # Reload table
                self.loadEndpointsToTable()

                return

            namespace_manager_utils.updateUrlOfEndpointInDatabase(current_name, current_url)

    def editMyModelInDB(self):

        if self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0) is None or self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 1) is None:
            return

        current_name = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 0).text()
        current_url = self.ui.tableWidgetMyModels.item(self.ui.tableWidgetMyModels.currentRow(), 1).text()

        try:
            str(current_name)
            str(current_url)
        except UnicodeEncodeError:
            # Show error
            QMessageBox.critical(self, 'Error', "Please use only latin characters.", QMessageBox.Close)

            # Reload table
            self.loadMyModelsToTable()
            return

        # If a model name is changed
        if self.ui.tableWidgetMyModels.currentColumn() == 0:

            # If the whole text was deleted from prefix
            if len(current_name) == 0:

                # Show error message
                QMessageBox.critical(self, 'Error', "Name cannot be empty", QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            # If new name already exists in DB
            if current_name in namespace_manager_utils.getListOfMyModelNamesFromDB():
                # Show error message
                QMessageBox.critical(self, 'Error', "Name already exists in the list", QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            namespace_manager_utils.updateNameOfMyModelInDatabase(current_name, current_url)

        # If my model url is changed
        elif self.ui.tableWidgetMyModels.currentColumn() == 1:

            # If the whole text was deleted from url
            if len(current_url) == 0:
                # Show error message
                QMessageBox.critical(self, 'Error', "URL cannot be empty", QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            # If new url already exists in DB
            if current_url in namespace_manager_utils.getListOfMyModelUrlsFromDB():
                # Show error message
                QMessageBox.critical(self, 'Error', "URL already exists in the list", QMessageBox.Close)

                # Reload table
                self.loadMyModelsToTable()

                return

            namespace_manager_utils.updateUrlOfMyModelInDatabase(current_name, current_url)



class AddNamespaceDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_AddNamespace()
        self.ui.setupUi(self)

        # MAKE CONNECTIONS
        self.ui.btnCancel.clicked.connect(self.close)
        self.ui.btnOK.clicked.connect(self.btnOK_clicked)

    def btnOK_clicked(self):
        prefix = self.ui.lineEditNamespacePrefix.text().lower()
        url = self.ui.lineEditNamespaceURL.text()

        # If the prefix field is empty
        if prefix == '':
            # Show message box with error
            QMessageBox.critical(self, 'Error', "Please type a prefix for the new namespace.", QMessageBox.Close)
            return

        # If the URL field is empty
        if url == "":
            # Show message box with error
            QMessageBox.critical(self, 'Error', "Please type a URL for the new namespace.", QMessageBox.Close)
            return

        # Check if latin characters
        try:
            str(prefix)
            str(url)
        except UnicodeEncodeError:
            # Show error
            QMessageBox.critical(self, 'Error', "Please use only latin characters.", QMessageBox.Close)
            return

        # If the given prefix exists in the DB.
        if prefix in namespace_manager_utils.getListOfNamespacePrefixesFromDB():
            # Show message box with error
            QMessageBox.critical(self, 'Error', "A namespace with the prefix <span style='font-size:9pt; font-weight:550; color:#000000;'>" + prefix +
                                       "</span> already exists in the list.", QMessageBox.Close)
            return

        # If given url exists in the DB
        if url in namespace_manager_utils.getListOfNamespaceUrlsFromDB():
            # Show message box with error
            QMessageBox.critical(self, 'Error', "A namespace with the url <span style='font-size:9pt; font-weight:550; color:#000000;'>" + url +
                                       "</span> already exists in the list.", QMessageBox.Close)
            return

        # Since everything is ok, we add the new namespace to the DB
        namespace_manager_utils.addNamespaceToDatabase(prefix, url)

        #Log
        namespace_manager_utils.addEntryToLog("New namespace " + prefix + " was inserted")

        # Close the dialog
        self.close()
 
    


# app = QApplication(sys.argv)
#
# window = Main()
# window.show()
#
# app.exec()


if __name__ == '__main__':
  app = QApplication(sys.argv)

  window = Main()
  window.show()

  app.exec()