#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 editor for typed tokens -- list definition and conversion
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2019. 01. 04"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from collections import OrderedDict

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.common_resources import getData
from Common.common_resources import getOntologyName
from Common.common_resources import M_None
from Common.common_resources import putData
from Common.ontology_container import OntologyContainer
from Common.resource_initialisation import FILES
from Common.ui_two_list_selector_dialog_impl import UI_TwoListSelector
from OntologyBuilder.TypedTokenEditor.editor_typed_token import Ui_MainWindow
from Common.resources_icons import roundButton

SPACING = 20
INSTANCES_Generic = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                     "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                     "U", "V", "W", "X", "Y", "Z"]
INSTANCES = ["A", "W", "C", "R", "I"]  # "F", "G", "H", "I", "J",


# "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
# "U", "V", "W", "X", "Y", "Z"]


class Conversion(dict):
  def __init__(self, reactants, products):
    dict.__init__(self)
    self["reactants"] = reactants
    self["products"] = products


class TypedTokenData(OrderedDict):

  def __init__(self, file=None):
    OrderedDict.__init__(self)
    if file:
      self.read(file)
    else:
      pass

  def initialise(self, typed_tokens):
    for ttoken in typed_tokens:
      self[ttoken] = {}
      self[ttoken]["instances"] = []
      self[ttoken]["conversions"] = []

  def write(self, f):
    # print("write typed-tokens to %s" % f)
    putData(self, f, indent=2)

  def read(self, f):
    data = getData(f)
    status = False
    if data:
      for hash in data:
        self[hash] = data[hash]
      status = True
    return status


class TypedRadioButton(QtWidgets.QRadioButton):
  def __init__(self, ID, typed_token):
    QtWidgets.QRadioButton.__init__(self, ID)
    self.ID = ID
    self.typed_token = typed_token
    self.setFixedHeight(SPACING)
    self.setAutoExclusive(False)


class Ui_TokenEditor(QtWidgets.QMainWindow):
  def __init__(self):
    QtWidgets.QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)


    roundButton(self.ui.pushSave, "save", tooltip="save to file")
    roundButton(self.ui.pushAddTypedToken, "plus", tooltip="add typed token")
    roundButton(self.ui.pushSaveAndExit, "exit", tooltip="exit")

    # attach ontology
    ontology_name = getOntologyName(task="task_typed_tokens")
    ontology = OntologyContainer(ontology_name)  # DIRECTORIES["ontology_location"] % ontology_name)
    self.networks = ontology.list_leave_networks

    self.typed_token_file_spec = FILES["typed_token_file"] % ontology_name

    self.DATA = TypedTokenData()

    typed_tokens = []
    self.instances = {}
    for nw in self.networks:
      for token in ontology.token_typedtoken_on_networks[nw]:
        for typed_token in ontology.token_typedtoken_on_networks[nw][token]:
          typed_tokens.append(typed_token)
          # self.instances[typed_token] = INSTANCES

    self.DATA.initialise(typed_tokens)
    self.__interfaceLogics("start")
    self.new = False
    self.selected_typed_token_class = None
    gotten = self.load()
    if gotten:
      self.__interfaceLogics("loaded")
    else:
      self.__interfaceLogics("start")
      typed_tokens_class = self.__makeTokenWithTypedTokensCombo()
      self.new = True
      self.__interfaceLogics("new")

  def __interfaceLogics(self, state):

    if state == "start":
      self.ui.groupToken.hide()
      self.ui.groupConversion.hide()
      self.ui.pushSave.hide()
      self.ui.statusbar.showMessage("starting")

    elif state == "new":
      self.ui.groupToken.show()
      self.ui.pushAddTypedToken.hide()
      self.ui.pushSave.hide()
      self.ui.statusbar.showMessage("new definitions")

    elif state == "loaded":
      self.ui.groupToken.show()
      self.ui.pushAddTypedToken.show()
      self.ui.pushSave.show()
      self.ui.statusbar.showMessage("loaded file")

    elif state == "converting token defined":
      self.ui.groupConversion.show()
      self.ui.groupConverstonControl.show()
      self.ui.pushAddTypedToken.show()
      self.ui.pushSave.show()
      self.ui.statusbar.showMessage("")

    elif state == "not converting token define":
      self.ui.groupConversion.hide()
      self.ui.groupConverstonControl.hide()
      self.ui.pushAddTypedToken.show()

    elif state == "no conversion defined":
      self.ui.groupConverstonControl.hide()

    elif state == "conversion defined":
      self.ui.groupConverstonControl.show()

    elif state == "modified":
      self.ui.pushSave.show()

    elif state == "saved":
      self.ui.pushSave.hide()

  def __makeTokenWithTypedTokensCombo(self):

    self.ui.comboTokenWithTypedTokens.clear()
    # self.ui.comboTokenWithTypedTokens.addItem(M_None)
    ### typed_tokens_class
    typed_tokens_class = sorted(
            self.DATA.keys())  # self.typed_token_classs_without_conversion | self.typed_token_classs_with_conversion
    self.ui.comboTokenWithTypedTokens.addItems(list(typed_tokens_class))

    return list(typed_tokens_class)


  def __makeConversionCombos(self):

    conversions = self.DATA[self.typed_token_class]["conversions"]

    if len(conversions) == 0:
      self.__interfaceLogics("no conversion defined")
    else:
      self.ui.spinConversion.setMinimum(0)
      self.ui.spinConversion.setMaximum(len(conversions) - 1)
      self.ui.comboConversion.clear()
      for c in conversions:
        s = "%s --> %s" % (c["reactants"], c["products"])
        self.ui.comboConversion.addItem(s)
      self.__interfaceLogics("conversion defined")

  def __clearLayout(self, layout):
    """ removes the widgets from the layout """
    for i in reversed(range(layout.count())):
      widgetToRemove = layout.itemAt(i).widget()
      # remove it from the layout list
      layout.removeWidget(widgetToRemove)
      # remove it from the gui
      widgetToRemove.setParent(None)

  def __minNumberTypedTokens(self):
    conversions = self.DATA[self.typed_token_class]["conversions"]
    if len(conversions) == 0:
      return 1

    index = -1
    for no in range(len(INSTANCES)):
      s = INSTANCES[no]
      for c in conversions:
        for r in c["reactants"]:
          if r == s:
            if index < no:
              index = no
        for r in c["products"]:
          if r == s:
            if index < no:
              index = no

    return index + 1

  def load(self):
    state = False
    if self.DATA.read(self.typed_token_file_spec):
      # self.ui.message_box.clear()
      # self.ui.message_box.setText('Loading previous typed token file')
      state = True
      typed_tokens_class = self.__makeTokenWithTypedTokensCombo()
    return state

  def on_comboTokenWithTypedTokens_currentTextChanged(self, token):
    self.selected_typed_token_class = self.ui.comboTokenWithTypedTokens.currentText()  # str(token)
    if self.selected_typed_token_class == M_None: return

    self.typed_token_class = self.selected_typed_token_class
    self.__interfaceLogics("not converting token defined")
    if self.new:
      self.__interfaceLogics("not converting token defined")
      two_list_selector = UI_TwoListSelector()
      two_list_selector.populateLists(INSTANCES_Generic, [])
      two_list_selector.exec_()

      selection = two_list_selector.getSelected()
      if len(selection) > 0:
        self.new = False
        self.DATA[self.typed_token_class]["instances"] = selection
    else:
      pass

    self.__interfaceLogics("converting token defined")
    min_no = self.__minNumberTypedTokens()
    self.__makeConversionCombos()
    self.redraw_conversion_radios()

  def redraw_conversion_radios(self):
    no_of_typed_tokens = len(
            self.DATA[self.typed_token_class]["instances"])
    self.__interfaceLogics("modified")
    token = self.typed_token_class
    self.__clearLayout(self.ui.formReactants)
    self.__clearLayout(self.ui.formProducts)
    self.radioButtonsTokens = {
            "reactants": {},
            "products" : {}
            }
    for no in range(int(no_of_typed_tokens)):
      self.radioButtonsTokens[token] = {}
      t = self.DATA[self.typed_token_class]["instances"][no]
      label = "%s :: %s" % (token, t)
      r = TypedRadioButton(label, t)
      self.radioButtonsTokens["reactants"][no] = r
      self.ui.formReactants.setWidget(no, QtWidgets.QFormLayout.LabelRole, r)
      r = TypedRadioButton(label, t)
      self.radioButtonsTokens["products"][no] = r
      self.ui.formProducts.setWidget(no, QtWidgets.QFormLayout.LabelRole, r)

  @QtCore.pyqtSlot(int)
  def on_spinConversion_valueChanged(self, index):
    # print(" change index: ", index)
    self.ui.comboConversion.setCurrentIndex(index)

  def on_comboConversion_activated(self, index):
    set_products = self.ui.comboConversion.currentText()
    r, p = self.products = set_products.split('-->')
    index = self.ui.comboConversion.currentIndex()
    self.ui.spinConversion.setValue(index)


  def on_pushSave_pressed(self):
    # self.ui.message_box.clear()
    # self.ui.message_box.setText('Saving typed token file to:\n'
    #                             + str(self.typed_token_file_spec))
    self.DATA.write(self.typed_token_file_spec)
    self.__interfaceLogics("saved")
    pass

  def on_pushNewConversion_pressed(self):
    reactants = []
    products = []
    for r in self.radioButtonsTokens["reactants"]:
      a = self.radioButtonsTokens["reactants"][r]
      if a.isChecked():
        reactants.append(a.typed_token)
        a.setChecked(False)
      b = self.radioButtonsTokens["products"][r]
      if b.isChecked():
        products.append(b.typed_token)
        b.setChecked(False)
    if (not reactants) or (not products):
      # self.ui.message_box.setText("you need to define reactants and products to define a new conversion")
      return
    c = Conversion(reactants, products)
    self.DATA[self.typed_token_class]["conversions"].append(c)
    self.__makeConversionCombos()
    self.__interfaceLogics("modified")

  def on_pushDelete_pressed(self):
    c = self.DATA[self.typed_token_class]["conversions"].pop(self.ui.spinConversion.value())
    self.__makeConversionCombos()
    self.__interfaceLogics("modified")

  def on_pushAddTypedToken_pressed(self):
    selected = self.DATA[self.selected_typed_token_class]["instances"]
    selected_set = set(selected)
    possible_set = set(INSTANCES_Generic)
    enabled_set = possible_set - selected_set

    two_list_selector = UI_TwoListSelector()
    two_list_selector.populateLists(sorted(enabled_set), sorted(selected))
    two_list_selector.exec_()

    selection_add = set(two_list_selector.getSelected())
    new_selection = selected_set.union(selection_add)
    selection = sorted(new_selection)
    if len(selection) > 0:
      self.new = False
      self.DATA[self.selected_typed_token_class]["instances"] = selection
      self.redraw_conversion_radios()

  def on_pushSaveAndExit_pressed(self):
    self.close()

