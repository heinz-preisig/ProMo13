# pylint: skip-file
import sys
import os
import json
from pprint import pprint as pp

from PyQt5 import QtWidgets

sys.path.insert(0, os.path.abspath("../.."))

from packages.Common.classes import io
from packages.Common.classes import variable
from packages.Common.classes import equation
from packages.Common.classes import entity

from packages.ModelBuilder.ModelComposer import instantiation_dialog_impl

ontology_name = "ProMo_sandbox7"

# class TestVariables:
#   """Eases the generation of a variables tree for testing purposes."""
#   def __init__(self):
#     self.variables = {}

#   def add(self, number, eqs=[]):
#     self.variables[number] = {}
#     self.variables[number]["label"] = "var_" + str(number)
#     self.variables[number]["equations"] = {}
#     for eq_number, incidence_list in eqs:
#       self.variables[number]["equations"][eq_number] = {}
#       self.variables[number]["equations"][eq_number]["incidence_list"] = incidence_list

# # Variables are created (only with necessary fields)
# variables = TestVariables()
# variables.add(0,[(1,["2","3","4"])])
# variables.add(2,[(5,["6"]),(7,["8","9"])])
# variables.add(3,[(10,["6","8","11"])])
# variables.add(4,[(12,["6","11","13"])])
# variables.add(6,[(14,["15","16"])])
# for i in [8,9,11,13,15,16]:
#   variables.add(i)

# # Entity is created from the VarEqTree (only with necessary fields)
# entity = resources.VarEqTree(variables.variables,0,[],1).tree
# entity["to_be_initialised"]=[8,9,11,13,15,16]
# entity["blocked"]=[]
# entity["root_variable"]=0
# entity["root_equation"]=1

all_variables = {}
for i in [0,2,3,4,6,8,9,11,13,15,16]:
  var_id = "V_" + str(i)
  all_variables[var_id] = variable.Variable(var_id, var_id)

equations = [
  ("1",["0", "2", "3", "4"]),
  ("5",["2", "6"]),
  ("7",["2", "8", "9"]),
  ("10",["3", "6", "8", "11"]),
  ("12",["4", "6", "11", "13"]),
  ("14",["6", "15","16"]),
]

all_equations = {}
for id, var_list in equations:
  eq_id = "E_" + id
  good_id_list = ["V_" + item for item in var_list]
  all_equations[eq_id] = equation.Equation(
    eq_id,
    good_id_list[0],
    " ".join(good_id_list[1:]),
    "test",
  )

test_entity = entity.Entity.from_root(
  "test_entity",
  "V_0",
  "E_1",
  all_equations,
)

var_eq_info = {}
var_eq_info["V_2"] = ["E_5", "E_7"]
var_eq_info["V_3"] = ["E_10"]
var_eq_info["V_4"] = ["E_12"]
var_eq_info["V_6"] = ["E_14"]

test_entity.generate_var_eq_tree(var_eq_info)
test_entity.update_var_eq_tree()

# Initial var_data is generated.
var_data_all = []
for i in [0,2,3,4,6,8,9,11,13,15,16]:
  var_info = {}
  var_info["id"] = "V_" + str(i)
  var_info["value"] = None
  var_info["same_in_all_nodes"] = True
  var_data_all.append(var_info)

var_data_all[5]["same_in_all_nodes"] = False
var_data_all[4]["same_in_all_nodes"] = False
var_data_all[1]["same_in_all_nodes"] = False

app = QtWidgets.QApplication(sys.argv)
dlg = instantiation_dialog_impl.InstantiationDlg(
  var_data_all,
  test_entity,
  all_variables,
  True,
  None,
)

return_value = dlg.exec_()
if return_value == QtWidgets.QDialog.Accepted:
  pp(dlg.var_data)
else:
  print("Cancelled")