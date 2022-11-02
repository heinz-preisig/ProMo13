"""This module contains the implementation of the GUI logic for the Instantiation dialog."""

import sys
# For debugging with pprint
from pprint import pprint as pp 

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex

# To run independently, quick fix
#sys.path.append("/home/alberto/Documents/Projects/ProMo11/ProMo/packages/")

from OntologyBuilder.OntologyEquationEditor import resources
from ModelBuilder.ModelComposer import ui_instantiation_dialog


class InstantiationDlg(QtWidgets.QDialog):
  """Implementation of the logic for the insantiation dialog.

  Attributes:
    ui (object): Contains the GUI widgets, obtained from QtDesigner.
    entity (dict): Stores the information about the entity linked to the nodes
      to be instantiated (only for a full instantiation). **None** if partial 
      instantiation is going to be done instead.
    variables (dict): Stores the information about all variables in the ontology.
    var_data (list[list[tuples]]): Contains one list for variables that need to
      be initialized and another for the rest. Each of these lists contain tuples
      of two items:

        * var_info (dict): Data of a single variable with the
          following fields:

          * id (int): The variable id.
          * same_in_all_nodes (bool): **True** if the variable has been instantiated 
            with the same value in all nodes or has not been instantiated in any.
            **False** otherwise.
          * value (float or None): The value of the variable if it has been
            instantiated with the same value in all nodes. **None** otherwise.

        * is_enabled (bool): **True** if the user is able to interact with the item.
          **False** otherwise.
        
    lists (list[QListWidget]): Contains the **QListWidgets** in the interface.
    tab_index_selected (int): Stores the index of the active tab.
  """

  def __init__(self, parent=None, var_data_all=[], entity=None, variables=None, single_node=True):
    """Initializes the InstantiationDlg with the required information.

    Args:
      parent (QWidget): Parent widget of the dialog. Defaults to **None**.
      var_data_all (list[dict]): Each element contains the data of a single variable
        with the following fields:

        * id (int): The variable id.
        * same_in_all_nodes (bool): **True** if the variable has been instantiated 
          with the same value in all nodes or has not been instantiated in any.
          **False** otherwise.
        * value (float or None): The value of the variable if it has been
          instantiated with the same value in all nodes. **None** otherwise.

        Defaults to **[]**.
      entity (dict): Stores the information about the entity linked to the nodes
        to be instantiated (only for a full instantiation). **None** if partial 
        instantiation is going to be done instead. Defaults to **None**.
      variables (dict): Stores the information about all variables in the ontology.
        Defaults to **None**.
      single_node (bool): **True** if the instantiation will be done for a single node.
        **False** otherwise. Defaults to **True**.
    """
    super().__init__(parent)
    self.ui = ui_instantiation_dialog.Ui_Dialog()
    self.ui.setupUi(self)

    if single_node:
      self.setWindowTitle("Instantiation (Single node)")
    else:
      self.setWindowTitle("Instantiation (Multiple nodes)")
      
    self.entity = entity
    self.variables = variables

        
    var_data_required = []
    var_data_others = []

    if self.entity is not None:
      # Separates variable depending if they are required to be instantiated or not.
      # only needed if a full instantiation is happening.
      var_required = self.entity["to_be_initialised"]
      for var_info in var_data_all:
        if var_info["id"] in var_required:
          var_data_required.append((var_info, True))
        else:
          var_data_others.append((var_info, True))
    else:
      for var_info in var_data_all:
        var_data_required.append((var_info, True))

      # self.ui.tab_others.setEnabled(False)
      self.ui.tab_variables.setTabEnabled(1, False)

    self.var_data = [var_data_required, var_data_others]
    self.lists = [self.ui.list_required, self.ui.list_others] 

    self.tab_index_selected = 0
    if self.entity is not None:
      self._update_enabled_vars()

    self._update_list()

    self.ui.pbutton_cancel.setFocus()

    # Connections
    self.ui.tab_variables.currentChanged.connect(self._tab_changed)
    # self.ui.list_required.currentRowChanged.connect(self._variable_selected)
    # self.ui.list_others.currentRowChanged.connect(self._variable_selected)
    self.ui.list_required.itemClicked.connect(
      lambda item: self._variable_selected(self.ui.list_required.row(item)))
    self.ui.list_others.itemClicked.connect(
      lambda item: self._variable_selected(self.ui.list_others.row(item)))
    self.ui.pbutton_instantiate.clicked.connect(self._instantiate) 
    self.ui.pbutton_accept.clicked.connect(super().accept)   
    self.ui.pbutton_cancel.clicked.connect(super().reject) 

  def _tab_changed(self, current_tab_index):
    """Controls the tab change.

    Args:
      tab_index (int): Index of the active tab.
    """
    self.tab_index_selected = current_tab_index
    # TODO if there is not extra functionality needed then this function can be a lambda.
    self._update_list()

  def _update_list(self):
    """Updates the current **QListWidget** with the current info."""
    # TODO Make this method always update both lists if is only used from the
    # instantiate and the __init__ methods.
    self.lists[self.tab_index_selected].clear()
        
    # The (*) symbol is used to represent a non instantiated variable.
    # The (~) symbol is used to represent variables that have been instantiated with
    # different values in different nodes.
    # Maybe we will use something else instead.
    # TODO Replace individual items instead of the whole list if it is better
    # performance wise for long lists. 
    for var_info, is_enabled in self.var_data[self.tab_index_selected]:
      if var_info["same_in_all_nodes"]:
        if var_info["value"] is None:
          value = "(*)"
        else:
          value = str(var_info["value"])
      else:
        value = "(~)"

      var_name = self.variables[var_info["id"]]["label"]
      list_item_name = var_name + ": " + value
      self._add_new_item_to_list(
        self.lists[self.tab_index_selected],
        list_item_name,
        is_enabled)        

    self._update_tab_title()
    self._set_instantiation_state(False)

  def _update_tab_title(self):
    """Update the first tab title when needed.

    The title will be in the form: "Required Variables (#)" where # is an integer
    representing how many variables are still required to be instantiated.  
    """
    non_initialized_counter = 0
    for var_info, is_enabled in self.var_data[0]:
      if var_info["same_in_all_nodes"] and var_info["value"] is None and is_enabled:
        non_initialized_counter += 1
        
    title = "Required Variables (" + str(non_initialized_counter)  + ")"
    self.ui.tab_variables.setTabText(0, title)

  def _set_instantiation_state(self, is_allowed):
    """Controls the use of GUI widgets related to the instantiation.

    Args:
      is_allowed (bool): **True** to allow interaction with the text box
        and the instantiate button. Also, the name of the selected variable 
        will be displayed in the variable name label. **False** to disable
        with the text box and the instantiate button. In this case the label
        will show a "?" sign.
    """
    self.ui.label_variable_name.setEnabled(is_allowed)
    self.ui.line_edit_value.setEnabled(is_allowed)
    self.ui.pbutton_instantiate.setEnabled(is_allowed)

    if not is_allowed:
      self.ui.label_variable_name.setText("?")
      self.ui.line_edit_value.clear()            

  def _variable_selected(self, item_pos):
    """Prepares the necessary widgets for the instantiation when a variable is selected.

    Also warns the user when a variable with different values in different nodes will
    be instantiated.

    Args:
      item_pos (int): Position in the **QListWidget** of the selected variable. It
        corresponds to the index in the proper var_data list.
    """
    var_info, is_enabled = self.var_data[self.tab_index_selected][item_pos]

    # Nothing happens while clicking on a disable item
    if not is_enabled:
      self._set_instantiation_state(False)
      return

    var_name = self.variables[var_info["id"]]["label"]
    
    if var_info["same_in_all_nodes"]:
      if var_info["value"] is None:
        self.ui.line_edit_value.clear()
      else:
        self.ui.line_edit_value.setText(var_info["value"])
        self.ui.line_edit_value.selectAll()
    else:      
      message = (
        "This variable does not have the same\n"
        "instantiation value in all nodes.\n"
        "Instantiation will overwrite the previous\n"
        "value for all nodes.\n"
        "Do you want to proceed?"
      )

      dlg_warning = QtWidgets.QMessageBox.warning(
        self, 
        "Instantiation warning",
        message, 
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No
      )

      if dlg_warning != QtWidgets.QMessageBox.Yes:
        self.ui.pbutton_cancel.setFocus()
        self.lists[self.tab_index_selected].currentItem().setSelected(False)
        self._set_instantiation_state(False)
        return

      self.ui.line_edit_value.clear()

    self.ui.label_variable_name.setText(var_name + ":=")
    self._set_instantiation_state(True)
    self.ui.line_edit_value.setFocus()

  def _instantiate(self):
    """Controls the instantiation process.

    Saves the new value for the selected variable. If the variable instantiated is
    not one of the required ones a new analisis is performed to check what variables
    are still needed and can still be instantiated.
    """
    pos = self.lists[self.tab_index_selected].currentRow()

    var_value = str(self.ui.line_edit_value.text())
    # TODO: Make a regex so several blank spaces are not allowed
    if var_value == "":
      var_value = None
    var_info, _ = self.var_data[self.tab_index_selected][pos]
    var_info["value"] = var_value
    var_info["same_in_all_nodes"] = True
    self.var_data[self.tab_index_selected][pos] = (var_info, True)

    if self.tab_index_selected == 1:
      self._update_enabled_vars()
    
    self._update_list()  

  def _add_new_item_to_list(self, list, item_name, is_enabled):
    """Adds a new item to a **QListWidget**.

    Uses flags to control some of the item properties.

    Args:
      list (QListWidget): Widget where the item will be inserted.
      item_name (string): Name of the item to be inserted. Already includes
        the variable name and its value. 
      is_enabled (bool):  **True** if the user is able to interact with the item.
        **False** otherwise.
    """
    # TODO Make the item_name here using var_name and var_value instead.
    # TODO Add different types of customization depending on the item (different
    # colors for the variables with values for example).
    item = QtWidgets.QListWidgetItem(item_name, list)
    flags = item.flags()
    if is_enabled:
      item.setFlags(flags | Qt.ItemIsEnabled)
    else:
      item.setFlags(flags & ~Qt.ItemIsEnabled)  

  def _update_enabled_vars(self):
    """Checks what variables are still needed.

    A new VarEq tree is generated. Variables that do not require instantiation but
    still get instantiated will not need equations anymore. These equations are added to
    the entity's original blocked equations and the tree is constructed from there.
    """
    blocked_equations = set(self.entity["blocked"])
    # Adding new blocked equations due to instantiation
    for var_info, _ in self.var_data[1]:
      if var_info["value"] is not None or not var_info["same_in_all_nodes"]:
        node_id = self.entity["IDs"]["variable_" + str(var_info["id"])]
        equations = []
        for tree_node in self.entity["tree"][node_id]["children"]:
          eq_id = self.entity["nodes"][tree_node][9:]
          blocked_equations.add(int(eq_id)) 

          

    # Generating new tree
    new_tree = resources.VarEqTree(
      self.variables, 
      self.entity["root_variable"],
      list(blocked_equations),
      self.entity["root_equation"]
    )
    
    # pp(self.variables)
    # pp(new_tree.tree)

    # Checking what variables are still needed
    enabled_vars = []
    for id in new_tree.tree["IDs"]:
      if "variable" in id:
        var_id = int(id[9:])
        enabled_vars.append(var_id)

    # Updating the data
    for list_id in [0,1]:
      for i, (var_info, is_enabled) in enumerate(self.var_data[list_id]):
        if var_info["id"] in enabled_vars and not is_enabled:
          self.var_data[list_id][i] = (var_info, True)
        if var_info["id"] not in enabled_vars and is_enabled:
          self.var_data[list_id][i] = (var_info, False)

class TestVariables:
  """Eases the generation of a variables tree for testing purposes."""
  def __init__(self):
    self.variables = {}

  def add(self, number, eqs=[]):
    self.variables[number] = {}
    self.variables[number]["label"] = "var_" + str(number)
    self.variables[number]["equations"] = {}
    for eq_number, incidence_list in eqs:
      self.variables[number]["equations"][eq_number] = {}
      self.variables[number]["equations"][eq_number]["incidence_list"] = incidence_list


if __name__ == "__main__":
  # Variables are created (only with necessary fields)
  variables = TestVariables()
  variables.add(0,[(1,['2','3','4'])])
  variables.add(2,[(5,['6']),(7,['8','9'])])
  variables.add(3,[(10,['6','8','11'])])
  variables.add(4,[(12,['6','11','13'])])
  variables.add(6,[(14,['15','16'])])
  for i in [8,9,11,13,15,16]:
    variables.add(i)

  # Entity is created from the VarEqTree (only with necessary fields)
  entity = resources.VarEqTree(variables.variables,0,[],1).tree
  entity["to_be_initialised"]=[8,9,11,13,15,16]
  entity["blocked"]=[]
  entity["root_variable"]=0
  entity["root_equation"]=1

  # Initial var_data is generated.
  var_data_all = []
  for i in [0,2,3,4,6,8,9,11,13,15,16]:
    var_info = {}
    var_info["id"] = i
    var_info["value"] = None
    var_info["same_in_all_nodes"] = True
    var_data_all.append(var_info)

  var_data_all[5]["same_in_all_nodes"] = False
  var_data_all[4]["same_in_all_nodes"] = False
  var_data_all[1]["same_in_all_nodes"] = False

  # entity = None

  app = QtWidgets.QApplication(sys.argv)
  dlg = InstantiationDlg(None, var_data_all, entity, variables.variables)
  return_value = dlg.exec_()
  if return_value == QtWidgets.QDialog.Accepted:
    pp(dlg.var_data)
  else:
    print("Cancelled")