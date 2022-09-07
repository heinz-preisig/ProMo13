#!/usr/local/bin/python3
# encoding: utf-8

"""

@author : "PREISIG, Heinz A"
@copyright : "Copyright 2015, PREISIG, Heinz A"

NOTE:constructStructureComponentID
 the graph component is not a class but a simple string. Reason being that it
 is easier to handle for the automaton implementation.
 Could be handled differently by defining a class with a __str__ method and
 a converting method when "loading" automaton.

 Object ID :  <structure ID>.<decoration ID>&<application-type>:<state>

 delimiters:
     O_delimiter = '.'
     T_delimiter = '&'  within the application type we split with |
     S_delimiter = ':'

  application_type is now also a composite:
     node : <nodetype>|<token>|conversion
     arc  : <arc type>|<token>|<mechanism>


  each arc and each node have a network membership

Application filters
  graphical_object level 0 - topology
  graphical object level i - adding layer i

@changes :2017-03-24 : simple node got a network indicator
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2017, PREISIG, Heinz A"
__since__ = "2017. 03. 23"
__license__ = "GPL planned -- until further notice for internal Bio4Fuel & MarketPlace use only"
__version__ = "5.04 or later"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import json
import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from Common.resource_initialisation import DIRECTORIES
from Common.single_list_selector_impl import SingleListSelector
from Common.ui_string_dialog_impl import UI_String

# global
# terminology

DEFAULT = "default"

DIALOGUE = {
        "choose"   : "make a choice",
        "new model": "new model",
        "new case" : "new case"
        }

M_None = "-"  # used in place of None as the latter is not a string.
M_any = "*"

# ontology definitions --------------------------------------------------------

NODE_COMPONENT_SEPARATOR = "|"
ARC_COMPONENT_SEPARATOR = "|"
ENTITY_OBJECT_SEPARATOR = "."
EQUATION_COMPONENT_SEPARATOR = "|"
CONNECTION_NETWORK_SEPARATOR = " >>> "  # RULE: separator is the same for inter and intra networks
CONVERSION_SEPARATOR = " --> "
EXTENSION_DUPLICATES_REMOVED = "-D"

TEMPLATE_NODE_OBJECT = "%s" + NODE_COMPONENT_SEPARATOR + "%s"
TEMPLATE_NODE_OBJECT_WITH_TOKEN = "%s" + NODE_COMPONENT_SEPARATOR + "%s" + NODE_COMPONENT_SEPARATOR + "%s"
TEMPLATE_ENTITY_OBJECT = "%s" + ENTITY_OBJECT_SEPARATOR \
                         + "%s" + ENTITY_OBJECT_SEPARATOR \
                         + "%s" + ENTITY_OBJECT_SEPARATOR \
                          + "%s"                                     #network, node|arc, object, variant
TEMPLATE_INTRA_NODE_OBJECT_WITH_TOKEN = "%s" + NODE_COMPONENT_SEPARATOR + "%s"
TEMPLATE_INTRA_NODE_OBJECT = "%s"
TEMPLATE_INTER_NODE_OBJECT = "%s"
TEMPLATE_ARC_APPLICATION = "%s" + ARC_COMPONENT_SEPARATOR + "%s" + ARC_COMPONENT_SEPARATOR + "%s"  # %(token,
# mechanism, nature)
TEMPLATE_INTERCONNECTION_NETWORK = "%s" + CONNECTION_NETWORK_SEPARATOR + "%s"
TEMPLATE_INTRACONNECTION_NETWORK = "%s" + CONNECTION_NETWORK_SEPARATOR + "%s"
TEMPLATE_INTRACONNECTION_PAIRS = "%s" + CONNECTION_NETWORK_SEPARATOR + "%s"
TEMPLATE_EQUATION_ASSIGNMENT_KEY = "%s" + EQUATION_COMPONENT_SEPARATOR + "%s" + EQUATION_COMPONENT_SEPARATOR + "%s"

TEMPLATE_ENTITY_OBJECT_REMOVED_DUPLICATES = "%s"+ EXTENSION_DUPLICATES_REMOVED

VARIABLE_TYPE_INTERFACES = "get"


# % (node_type, nature, token)


def invertDict(dictionary):
  d = {}
  for i in dictionary:
    d[dictionary[i]] = i
  return d
  # return dict(zip(dictionary.values(), list(dictionary.keys())))


def indexList(List):
  # index -- hash:enumeration:int - value:label:string
  # inverse_index -- hash:label:string - value:enumeration:int

  index = {}
  inverse_index = {}

  for i in range(len(List)):
    index[i] = List[i]
    inverse_index[List[i]] = i

  return index, inverse_index


def getData(file_spec):
  # print("get data from ", file_spec)
  if os.path.exists(file_spec):
    f = open(file_spec, "r")
    data = json.loads(f.read())
    return data
  else:
    return None

def getEnumeratedData(file_spec):
  raw_data = getData(file_spec)
  if not raw_data:
    return None
  else:
    data = {}
    for str_ID in raw_data:
      data[int(str_ID)] = raw_data[str_ID]
    return data


def putDataOrdered(data, file_spec, indent="  "):
  dump = json.dumps(data, sort_keys=True, indent=indent)
  print("saved file : ", file_spec)
  with open(file_spec, "w") as f:
    f.write(dump)


def putData(data, file_spec, indent="  "):
  print("writing to file: ", file_spec)
  dump = json.dumps(data, indent=indent)
  with open(file_spec, "w+") as f:
    f.write(dump)


def __getSortedDirList(location):
  """
  appears in two places,
  - at the beginning to select the model to be edited
  - to define a snippsel

  :return: model name
  """
  # print("location: ", location)
  if not os.path.exists(location):
    # print("debugging no such directory")
    os.makedirs(location)
  things = os.listdir(location)
  dirs = []
  for thing in things:
    path, spec = os.path.split(thing)
    # print(path, spec)
    name, ext = os.path.splitext(spec)
    # print(name, ext)
    dirs.append(name)
  dirs.sort()

  return dirs

#
# def askForModelFileGivenOntologyLocation(model_library_location, new=False, exit="exit", left_icon=None,
#                                          right_icon=None):
#   model_names = __getSortedDirList(model_library_location)
#
#   model_name, status = selectFromList("choose model", model_names, left_icon=left_icon, right_icon=right_icon)
#   # print("debugging -- ask for model name", model_name, status)
#
#   if (not model_name) and (not status):
#     sys.exit()
#
#   if model_name:
#     return model_name, "existent"
#
#   # while (model_name in acceptance_list):
#   while not (model_name or (status == "exit")):
#     ui_ask = UI_String("give new model name or type exit ", "model name or exit", limiting_list=model_names)
#     ui_ask.exec_()
#     model_name = ui_ask.getText()
#     print("new model name defined", model_name)
#     if not model_name:  # == "exit":
#       return model_name, "exit"
#   return model_name, "new"


def askForModelFileGivenOntologyLocation(model_library_location,
                                      left_icon="new",
                                      left_tooltip= "new",
                                      right_icon="accept",
                                      right_tooltip="accept",
                                      alternative=True):

  model_names = __getSortedDirList(model_library_location)

  model_name = None
  status = None
  if model_names:

    model_name, status = selectFromList("choose model",
                                        model_names,
                                        left_icon=left_icon,
                                        left_tooltip= left_tooltip,
                                        right_icon=right_icon,
                                        right_tooltip=right_tooltip)

    # print("debugging -- ask for model name", model_name, status)

    if model_name:
      return model_name, "existent"

  if not alternative:
    return None, "exit"

  # while (model_name in acceptance_list):
  while not (model_name or (status == "exit")):
    ui_ask = UI_String("give new model name or type exit ", "model name or exit", limiting_list=model_names)
    ui_ask.exec_()
    model_name = ui_ask.getText()
    # print("new model name defined", model_name)
    if not model_name:  # == "exit":
      return model_name, "exit"
  return model_name, "new"


def askForCasefileGivenLocation(case_rep_loc,
                                      left_icon="new",
                                      left_tooltip= "new",
                                      right_icon="accept",
                                      right_tooltip="accept"):

  case_names = __getSortedDirList(case_rep_loc)

  if case_names:
    case_name, status = selectFromList("choose case",
                                        case_names,
                                        left_icon=left_icon,
                                        left_tooltip= left_tooltip,
                                        right_icon=right_icon,
                                        right_tooltip=right_tooltip)


    if (not case_name) and (not status):
      sys.exit()

    if case_name:
      return case_name, "existent"

  case_name = ""
  status = ""

  while not (case_name or (status == "exit")):
    ui_ask = UI_String("give new case name or type exit ", "case name or exit", limiting_list=case_names)
    ui_ask.exec_()
    case_name = ui_ask.getText()
    # print("debugging -- new model name defined", case_name)
    if not case_name:  # == "exit":
      return case_name, "exit"
  return case_name, "new"


def getOntologyName(new=False, task="ProMo_logo", behaviour="on_click", left_icon=None, right_icon=None):
  from Common.logo_impl import Logo
  """
  asks for a ontology name from a list of ontologies in the repository
  if it allows for a new one.
  hiden directories are ignored
  :param new: logical
  :param task: selects logo from logo repository -- default is ProMo_logo
  :param behaviour: on_cklick makes logo to behave as button (default) alterenative is auto_close after selection has 
  been made
  :return:  depends on new
            new == True :  it returns the chosen ontology, but also the list of existing ontologies
                           that can be used to constrain the definition of a new one.
            new ==False:   it returns the chosen ontology
  """

  logo = Logo(task)  # ("task_ontology_foundation")
  if behaviour == "on_click":
    logo.exec_()
  else:
    logo.show()

  location = DIRECTORIES["ontology_repository"]

  ontologies_d = [f.path for f in os.scandir(location) if f.is_dir()]
  ontologies = [os.path.splitext(os.path.basename(o))[0] for o in ontologies_d]
  for o in ontologies:
    if o[0] == ".":
      ontologies.remove(o)

  if behaviour != "on_click":
    logo.close()

  ontology, state = selectFromList("choose ontology", ontologies, left_icon=left_icon, right_icon=right_icon,
                                   left_tooltip=left_icon, right_tooltip=right_icon)
  if new:
    return ontology, ontologies
  elif ontology:
    return ontology
  else:
    sys.exit(0)


def makeTreeView(treeWidget, ontology_tree):
  root = "root"  # RULE: root of tree is called "root"

  treeWidget.clear()
  tree_items = {}
  networks = list(ontology_tree.keys())
  # root = self.root
  tree_items[root] = __addItemToTreeWidget(treeWidget, None, root)
  tree_items[root].name = ontology_tree[root]["name"]
  for nw in networks:
    if nw != root:
      parent = root
      child = ontology_tree[nw]["name"]
      nodes = []
      [nodes.append(n) for n in ontology_tree[nw]["parents"][::-1]]
      nodes.append(child)
      for child in nodes:
        if child in tree_items:
          parent = child
        else:
          parent_item = tree_items[parent]
          tree_items[child] = __addItemToTreeWidget(treeWidget, parent_item, child)
          tree_items[child].name = ontology_tree[child]["name"]
          parent = child

  treeWidget.expandAll()
  return tree_items


def __addItemToTreeWidget(treeWidget, parent, nodeID):
  name = str(nodeID)
  item = QtWidgets.QTreeWidgetItem(parent, None)
  item.nodeID = nodeID
  item.setText(0, name)
  item.setSelected(True)

  k = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable #\
    # | QtCore.Qt.ItemIsEditable
  item.setFlags(k)

  item.setSelected(False)

  treeWidget.addTopLevelItem(item)

  return item


def selectFromList(title, items, left_icon, right_icon, left_tooltip, right_tooltip):
  items.sort()
  if right_icon:
    if left_icon:
      selector = SingleListSelector(items, left_icon=left_icon, right_icon=right_icon,
                                    left_tooltip=left_tooltip, right_tooltip=right_tooltip)
    else:
      selector = SingleListSelector(items, left_icon=left_icon)
  elif left_icon:
    selector = SingleListSelector(items, left_icon=left_icon)
  else:
    selector = SingleListSelector(items)
  selector.setWindowTitle(title)
  selector.exec_()
  selector.show()
  selection, status = selector.getSelection()
  del selector
  return selection, status


def saveBackupFile(path):
  ver_temp = "(%s)"
  (abs_name, ext) = os.path.splitext(path)  # path : directory/<name>.<ext>
  #  TODO: the access check fails -- not clear why, when removed writing works OK
  if os.path.exists(path):
    _f, ver = getFilesAndVersions(abs_name, ext)
    old_path = path
    new_path = abs_name + ver_temp %str(ver + 1)  + ext
    next_path = abs_name + ver_temp %str(ver + 2) + ext
    os.rename(old_path, new_path)
    return old_path, new_path, next_path
  else:
    print("Error -- no such file : %s"%path, file=sys.stderr)
    return

def saveWithBackup(data, path):
  print("saving")
  old_path, new_path, next_path = saveBackupFile(path)
  putData(data,path)


def getFilesAndVersions(abs_name, ext):
  base_name = os.path.basename(abs_name)
  ver = 0  # initial last version
  _s = []
  directory = os.path.dirname(abs_name)  # listdir(os.getcwd())
  files = os.listdir(directory)

  for f in files:
    n, e = os.path.splitext(f)
    #        print 'name', n
    if e == ext:  # this is another type
      if n[0:len(base_name) + 1] == base_name + "(":  # only those that start with name
        #  extract version
        l = n.index("(")
        r = n.index(")")
        assert l * r >= 0  # both must be there
        v = int(n[l + 1:r])
        ver = max([ver, v])
        _s.append(n)
  return _s, ver


# NOTE: the global handling of the IDs has been abandoned for the time being -- was not practical now but may be
# necessary to reconsider in the future
# RULE: ProMoIRIs are handled local to the ontologies for the time being.
# def globalEquationID(update=False, reset=False):
#   """
#   defines a new global equation ID
#   :param reset: if true it will reset the counter to 0 and returns the 0 as the first ID
#   :return: ID
#   """
#   return globalID(FILES["global_equation_identifier"],update=update, reset=reset)
#
# def globalVariableID( update=False, reset=False):
#   """
#   defines a new global equation ID  essentially implements a global enumeration variable
#   :param reset: if true it will reset the counter to 0 and returns the 0 as the first ID
#   :return: ID
#   """
#   return globalID(FILES["global_variable_identifier"], update=update, reset=reset)
#
#
# def globalID(file, update=False, reset=False):
#   """
#   utility function for defining global ID for variables and equations.
#   NOTE: python runs this function when importing the function... that's very unfortunate as it changes the counter.
#         So there was a need for more control.
#   :param file:  file name -- allows for several enumeration types
#   :param update: adds control allowing to have the module to be loaded without changing the global counter
#   :param reset: reset the counter.
#   :return: the new ID
#   """
#
#   if (not os.path.exists(file)) or reset:
#     with open(file,'w') as f:
#       f.write('0')
#       return 0
#   with open(file) as f:
#     a = f.read()
#   ID = int(a) + 1
#
#   if update:
#     with open(file,'w') as f:
#       f.write(str(ID))
#
#       # print("debugging -- 383 -- new ID:",ID)
#   return ID


def walkDepthFirstFnc(tree, id):
  """
  walk a tree depth first iteratively
  :param tree: container with node and its children specified tree[#node]["children" ]
  :param id: #node
  :return: nodes
  """
  nodes = []
  stack = [id]
  while stack:
    cur_node = stack[0]
    stack = stack[1:]
    nodes.append(cur_node)
    for child in reversed(tree[cur_node]["children"]):
      stack.insert(0, child)
  return nodes


def walkBreathFirstFnc(tree, id):
  """
  walk a tree breath first iteratively
  :param tree: container with node and its children specified tree[#node]["children" ]
  :param id: #node
  :return: nodes
  """
  nodes = []
  stack = [id]
  while stack:
    cur_node = stack[0]
    stack = stack[1:]
    nodes.append(cur_node)
    for child in tree[cur_node]["children"]:
      stack.append(child)
  return nodes


class Stream(QtCore.QObject):
  newText = QtCore.pyqtSignal(str)

  def write(self, text):
    self.newText.emit(str(text))
    self.flush()

  def flush(self):
    pass


class Redirect(QtWidgets.QWidget):
  def __init__(self, textBrowser):
    QtWidgets.QWidget.__init__(self)
    self.textBrowser = textBrowser

  def home(self):
    self.std_outbox = self.textBrowser  # this is the QtGui.QTextEdit()
    self.std_outbox.moveCursor(QtGui.QTextCursor.Start)
    self.std_outbox.ensureCursorVisible()
    self.std_outbox.setLineWrapColumnOrWidth(500)
    self.std_outbox.setLineWrapMode(QtWidgets.QTextEdit.FixedPixelWidth)

  def update(self, text):
    cursor = self.std_outbox.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.insertText(text)
    self.std_outbox.setTextCursor(cursor)
    self.std_outbox.ensureCursorVisible()