"""
===============================================================================
 Resources for the equation editor
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 03. 221"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import time
from datetime import datetime
from pathlib import Path

import subprocess
from os.path import abspath
from os.path import dirname

from PyQt5 import QtCore
from PyQt5 import QtGui
from graphviz import Digraph
from jinja2 import Environment  # sudo apt-get install python-jinja2
from jinja2 import FileSystemLoader

from Common.classes import entity
from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.common_resources import invertDict
from Common.pop_up_message_box import makeMessageBox
from Common.record_definitions_equation_linking import VariantRecord
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.treeid import ObjectTree

# INDENT = "    "
# LF = "\n"
NEW = "_new_"
NEW_EQ = NEW  # ..................... for new equation
EMPTY_EQ = "_empty_"  # ..............for no equation
PORT = "port"  # .....................for variables that are to be defined
UNDEF_EQ_NO = "Exxx"  # ..............for no equation defined
CONSTANT = "constant"
NEW_VAR = NEW
TEMP_VARIABLE = "temporary"
LAYER_DELIMITER = "_"
VAR_REG_EXPR = QtCore.QRegExp("[a-zA-Z_]\w*")
BLOCK_INDEX_SEPARATOR = " & "

IRIPREFIX_DELIMITER = ":"
IRINAMESPACE_DELIMITER = "+"

# IRI_TEMPLATE = "%s:%s+%s" #%(prefix, namespace, label)
IRI_TEMPLATE = "%s:%s" #%(prefix, label)

def IRI_parse(iri):
  # prefix, _rest = iri.split(IRIPREFIX_DELIMITER)
  # namespace, label = _rest.split(IRINAMESPACE_DELIMITER)
  namespace, label = iri.split(IRIPREFIX_DELIMITER)
  # return prefix,namespace,label
  return namespace,namespace,label

# def IRI_make(prefix,namespace,label):
def IRI_make(prefix,label):
  # r = IRI_TEMPLATE%(prefix,namespace,label)
  r = IRI_TEMPLATE%(prefix,label)
  return r


TOOLTIPS = {}

TOOLTIPS["edit"] = {}
TOOLTIPS["edit"]["type"] = "click to shift variable type"
TOOLTIPS["edit"]["symbol"] = "click to modify symbol"
TOOLTIPS["edit"]["description"] = "modify description"
TOOLTIPS["edit"]["units"] = "time, length, amount, mass, temp, current, light\nmay only be modified for _new_ variable"
TOOLTIPS["edit"]["indices"] = "may only be modified for _new_ variable"
TOOLTIPS["edit"]["eqs"] = "add equation"
TOOLTIPS["edit"]["variable"] = "no action"
TOOLTIPS["edit"]["del"] = "delete"
TOOLTIPS["edit"]["network"] = "network where variable is defined"
TOOLTIPS["edit"]["token"] = "tokens for this variable"
TOOLTIPS["edit"]["ID"] = "assigned ID"
TOOLTIPS["edit"]["IRI"] = "assigned IRI"

TOOLTIPS["pick"] = {}
s = "click copy variable symbol into expression editor"
TOOLTIPS["pick"]["type"] = s
TOOLTIPS["pick"]["symbol"] = s
TOOLTIPS["pick"]["description"] = s
TOOLTIPS["pick"]["units"] = s
TOOLTIPS["pick"]["indices"] = s
TOOLTIPS["pick"]["eqs"] = s
TOOLTIPS["pick"]["variable"] = s
TOOLTIPS["pick"]["del"] = s
TOOLTIPS["pick"]["network"] = s
TOOLTIPS["pick"]["token"] = s
TOOLTIPS["pick"]["ID"] = "assigned ID"
TOOLTIPS["pick"]["IRI"] = "assigned IRI"

TOOLTIPS["show"] = {}
s = "sorting is enabled & click to see equation"
TOOLTIPS["show"]["type"] = s
TOOLTIPS["show"]["symbol"] = s
TOOLTIPS["show"]["description"] = s
TOOLTIPS["show"]["units"] = s
TOOLTIPS["show"]["indices"] = s
TOOLTIPS["show"]["eqs"] = s
TOOLTIPS["show"]["variable"] = s
TOOLTIPS["show"]["del"] = s
TOOLTIPS["show"]["network"] = s
TOOLTIPS["show"]["token"] = s
TOOLTIPS["show"]["ID"] = s
TOOLTIPS["show"]["IRI"] = "assigned IRI"

# ------------
TEMPLATES = {}

# used in compile space
TEMPLATES["temp_variable"] = "temp_%s"

# used in physvars
TEMPLATES["Equation_definition_delimiter"] = ":="
TEMPLATES["definition_delimiter"] = " :: "
TEMPLATES["index_diff_state"] = "d%s"
# TEMPLATES["block_index"] = "%s" + BLOCK_INDEX_SEPARATOR + "%s"
TEMPLATES["conversion_label"] = "%s_conversion"
TEMPLATES["conversion_alias"] = "C%s"
TEMPLATES["interface_variable"] = "_%s"
# TEMPLATES["sub_index"] = "%s_%s"

# differential space
TEMPLATES["differential_space"] = "d%s"

# table control

# columns are
# 0 type --> new variable
# 1 symbol
# 2 description / documentation
# 3 tokens
# 4 units
# 5 indices
# 6 equations
# 7 delete

ENABLED_COLUMNS = {}  # TODO: remove hard wiring
ENABLED_COLUMNS["initialise"] = {}
ENABLED_COLUMNS["initialise"]["constant"] = [0, 1, 2, 3, 4, 5, 6]
ENABLED_COLUMNS["initialise"]["state"] = [1, 2, 3, 4]
ENABLED_COLUMNS["initialise"]["frame"] = [1, 2, 3, 4]
ENABLED_COLUMNS["initialise"]["network"] = [1, 2, 5]
ENABLED_COLUMNS["initialise"]["others"] = []

ENABLED_COLUMNS["edit"] = {}
ENABLED_COLUMNS["edit"]["constant"] = [0, 1, 2, 3, 4, 5, 6, 7]
ENABLED_COLUMNS["edit"]["others"] = [0, 1, 2, 5, 6, 7]
ENABLED_COLUMNS["edit"]["state"] = [1, 2, 3, 4, 6, 7]
ENABLED_COLUMNS["edit"]["frame"] = [1, 2, 3, 7]
ENABLED_COLUMNS["edit"]["network"] = [1, 2, 4, 7]

ENABLED_COLUMNS["inter_connections"] = {}
ENABLED_COLUMNS["inter_connections"]["constant"] = [0, 1, 2, 3, 4, 5, 6, 7]
ENABLED_COLUMNS["inter_connections"]["transposition"] = [0, 1, 2, 5, 6, 7]
ENABLED_COLUMNS["inter_connections"]["others"] = [0, 1, 2, 3, 4, 5, 6, 7]
ENABLED_COLUMNS["inter_connections"]["state"] = [0, 1, 2, 3, 5, 6]

ENABLED_COLUMNS["intra_connections"] = {}
ENABLED_COLUMNS["intra_connections"]["constant"] = [0, 1, 2, 3, 4, 5, 6, 7]
ENABLED_COLUMNS["intra_connections"]["transposition"] = [0, 1, 2, 5, 6, 7]
ENABLED_COLUMNS["intra_connections"]["others"] = [0, 1, 2, 3, 4, 5, 6, 7]
ENABLED_COLUMNS["intra_connections"]["state"] = [0, 1, 2, 3, 4, 5, 6]

# code generation in abstract syntax


LIST_DELIMITERS = ["(", ")", "[", "]", "{", "}", "|", ",", "::", "&", "_"]
DELIMITERS_alias = {
        "(" : "left_round",
        ")" : "right_round",
        "[" : "left_square",
        "]" : "right_square",
        "{" : "left_wiggled",
        "}" : "right_wiggled",
        "|" : "or",
        "," : "comma",
        "::": "double_column",
        "&" : "ampersand",
        "_" : "underline"
        }

LIST_OPERATORS = ["+",  # ................ ordinary plus
                  "-",  # ................ ordinary minus
                  "^",  # ................ ordinary power
                  ":",  # ................ expand product
                  ".",  # ................ Hadamar product
                  "*",  # ................ reduce product
                  "ParDiff",  # .......... partial derivative
                  "TotalDiff",  # ........ total derivative
                  "Integral",  # ......... integral
                  "Product",  # ......... interval
                  "Instantiate",  # ...... instantiate
                  "max",  # .............. maximum
                  "min",  # .............. minimum
                  "in",  # ............... membership    TODO: behaves more like a delimiter...
                  "MakeIndex",  # ......... make a new index
                  ]

OPERATORS_alias = {
        "+"          : "plus",  # ................ ordinary plus
        "-"          : "minus",  # ................ ordinary minus
        "^"          : "power",  # ................ ordinary power
        ":"          : "expandProduct",  # ................ expand product
        "."          : "Hadamar",  # ................ Hadamar product
        "*"          : "reduceProduct",  # ................ reduce product
        "ParDiff"    : "ParDiff",  # .......... partial derivative
        "TotalDiff"  : "TotalDiff",  # ........ total derivative
        "Integral"   : "Integral",  # ......... integral
        "Product"    : "Product",  # ......... interval
        "Instantiate": "Instantiate",  # ...... instantiate
        "max"        : "max",  # .............. maximum
        "min"        : "min",  # .............. minimum
        "in"         : "in",  # ............... membership    TODO: behaves more like a delimiter...
        "MakeIndex"  : "MakeIndex",  # ......... make a new index
        }

# OPERATORS_rdf = {
#         "+"          : "plus",  # ................ ordinary plus
#         "-"          : "minus",  # ................ ordinary minus
#         "^"          : "power",  # ................ ordinary power
#         ":"          : "KR",  # ................ Khatri-Rao product
#         "."          : "expandProduct",  # ................ expand product
#         "|"          : "reduceProduct",  # ................ reduce product
#         "BlockReduce": "BlockReduce",  # ....... block reduce product
#         "ParDiff"    : "ParDiff",  # .......... partial derivative
#         "TotalDiff"  : "TotalDiff",  # ........ total derivative
#         "Integral"   : "Integral",  # ......... integral
#         "Product"    : "Product",  # ......... interval
#         "Instantiate": "Instantiate",  # ...... instantiate
#         "max"        : "max",  # .............. maximum
#         "min"        : "min",  # .............. minimum
#         "in"         : "in",  # ............... membership    TODO: behaves more like a delimiter...
#         "MakeIndex"  : "MakeIndex",  # ......... make a new index
#         }

UNITARY_NO_UNITS = ["exp", "log", "ln", "sqrt", "sin", "cos", "tan", "asin", "acos", "atan"]
UNITARY_RETAIN_UNITS = ["abs", "neg", "diffSpace", "left", "right"]
UNITARY_INVERSE_UNITS = ["inv"]
UNITARY_LOOSE_UNITS = ["sign"]
NAMED_FUNCTIONS = ["Root",]

LIST_FUNCTIONS_SINGLE_ARGUMENT = UNITARY_NO_UNITS + UNITARY_RETAIN_UNITS + UNITARY_INVERSE_UNITS + UNITARY_LOOSE_UNITS

LIST_FUNCTIONS = LIST_FUNCTIONS_SINGLE_ARGUMENT + NAMED_FUNCTIONS

CODE = {}

## Languages
LANGUAGES = {}
# LANGUAGES["output"] = ["matlab", "latex"]
LANGUAGES["global_ID"] = "global_ID"
LANGUAGES["global_ID_to_internal"] = "global_ID_to_internal"
LANGUAGES["internal_code"] = "internal_code"
LANGUAGES["internals"] = [LANGUAGES["internal_code"], "global_ID_to_internal"]  # "rename"]
LANGUAGES["code_generation"] = ["matlab"] #["global_ID", "python", "cpp", "matlab"]
LANGUAGES["documentation"] = ["latex"]
LANGUAGES["compile"] = LANGUAGES["code_generation"] + LANGUAGES["documentation"]
LANGUAGES["aliasing"] = LANGUAGES["compile"] + [LANGUAGES["internal_code"]]
LANGUAGES["aliasing_modify"] = LANGUAGES["compile"].copy()
# LANGUAGES["aliasing_modify"].remove(LANGUAGES["global_ID"])
LANGUAGES["rename"] = "rename"
LANGUAGES["matrix_form"] = ["matlab", "python", "cpp"]

###########    Core representation -- our language

# =====================================================================================================================
language = LANGUAGES["global_ID"]
CODE[language] = {}

ID_spacer = " "
ID_prefix = {
        "delimiter": "D_",
        "operator" : "O_",
        "function" : "F_",
        "variable" : "V_",
        "index"    : "I_",
        "diff_node": "diff_",
        "equation" : "E_"
        }

ID_delimiter = {i: ID_spacer + ID_prefix[i] +"%s" for i in ID_prefix}
        # "delimiter": ID_spacer + "D_%s",
        # "operator" : ID_spacer + "O_%s",
        # "function" : ID_spacer + "F_%s",
        # "variable" : ID_spacer + "V_%s",
        # "index"    : ID_spacer + "I_%s",
        # "diff_node": ID_spacer + "diff_%s"
        # }

delimiters = {d: ID_delimiter["delimiter"] % LIST_DELIMITERS.index(d) for d in LIST_DELIMITERS}
CODE[language]["delimiter"] = delimiters
CODE[language]["operator"] = {d: ID_delimiter["operator"] % LIST_OPERATORS.index(d) for d in LIST_OPERATORS}
CODE[language]["function"] = {d: ID_delimiter["function"] % LIST_FUNCTIONS.index(d) for d in LIST_FUNCTIONS}

CODE[language]["combi"] = {}
CODE[language]["combi"] = {
        "single_argument": CODE[language]["delimiter"]["("] + "%s" + \
                           CODE[language]["delimiter"][")"],
        "tuple"          : CODE[language]["delimiter"]["("] + "%s" + \
                           CODE[language]["delimiter"][","] + "%s" + \
                           CODE[language]["delimiter"][")"],
        "range"          : CODE[language]["delimiter"]["["] + "%s" + \
                           CODE[language]["delimiter"][","] + "%s" + \
                           CODE[language]["delimiter"]["]"]
        }

# ------------------------------------------------------------------------------------
CODE[language]["bracket"] = delimiters["("] + "%s" + delimiters[")"]
CODE[language][","] = CODE[language]["delimiter"][","]

### operators ------------------------------------------------------------------------
CODE[language]["+"] = "%s" + CODE[language]["operator"]["+"] + "%s"
CODE[language]["-"] = "%s" + CODE[language]["operator"]["-"] + "%s"
CODE[language]["^"] = "%s" + CODE[language]["operator"]["^"] + \
                      CODE[language]["delimiter"]["("] + \
                      "%s" + CODE[language]["delimiter"][")"]  # power
CODE[language][":"] = "%s" + CODE[language]["operator"][":"] + "%s"  # expand product
CODE[language]["."] = "%s" + CODE[language]["operator"]["."] + "%s"  # Hadamar product
CODE[language]["*"] = "%s " + CODE[language]["operator"]["*"] + "%s"   # reduce product
CODE[language]["ParDiff"] = CODE[language]["operator"]["ParDiff"] + \
                            CODE[language]["combi"]["tuple"]
CODE[language]["TotalDiff"] = CODE[language]["operator"]["TotalDiff"] + \
                              CODE[language]["combi"]["tuple"]
CODE[language]["Integral"] = CODE[language]["operator"]["Integral"] + \
                             CODE[language]["delimiter"]["("] + \
                             "{integrand!s}" + \
                             CODE[language]["delimiter"]["::"] + \
                             "{differential!s}" + \
                             CODE[language]["operator"]["in"] + \
                             CODE[language]["delimiter"]["["] + \
                             "{lower!s}" + \
                             CODE[language]["delimiter"][","] + \
                             "{upper!s}" + \
                             CODE[language]["delimiter"]["]"] + \
                             CODE[language]["delimiter"][")"]
# CODE[language]["Interval"] = CODE[language]["operator"]["Interval"] + \
#                              CODE[language]["delimiter"]["("] + \
#                              "%s" + \
#                              CODE[language]["operator"]["in"] + \
#                              CODE[language]["combi"]["range"] + \
#                              CODE[language]["delimiter"][")"]
CODE[language]["Product"] = CODE[language]["operator"]["Product"] + \
                            CODE[language]["delimiter"]["("] + "{argument!s}" + \
                            CODE[language]["delimiter"][","] + "{index!s}" + \
                            CODE[language]["delimiter"][")"]
CODE[language]["Instantiate"] = CODE[language]["operator"]["Instantiate"] + \
                                CODE[language]["combi"]["tuple"]

CODE[language]["max"] = CODE[language]["operator"]["max"] + CODE[language]["combi"]["tuple"]
CODE[language]["min"] = CODE[language]["operator"]["min"] + CODE[language]["combi"]["tuple"]

for f in LIST_FUNCTIONS_SINGLE_ARGUMENT:
  CODE[language][f] = CODE[language]["function"][f] + CODE[language]["combi"]["single_argument"]

CODE[language]["Root"] = CODE[language]["function"]["Root"] + CODE[language]["combi"]["single_argument"]

CODE[language]["()"] = "%s"  # used by temporary variables

CODE[language]["variable"] = ID_delimiter["variable"]  # ID of the variable
CODE[language]["index"] = ID_delimiter["index"]  # ID of the index
# CODE[language]["block_index"] = ID_delimiter["index"]  # ID of the blockindex
CODE[language]["index_diff_state"] = ID_delimiter["diff_node"]  # ID of the variable

CODE[language]["comment"] = ""

# =====================================================================================================================
language = LANGUAGES["global_ID_to_internal"]
source = LANGUAGES["global_ID"]
CODE[language] = {}
CODE[language].update(invertDict(CODE[source]["delimiter"]))
CODE[language].update(invertDict(CODE[source]["operator"]))
CODE[language].update(invertDict(CODE[source]["function"]))

# =====================================================================================================================
language = LANGUAGES["internal_code"]
CODE[language] = {}
CODE[language]["bracket"] = "(" + "%s" + ")"
CODE[language][","] = ","

CODE[language]["+"] = "%s + %s"
CODE[language]["-"] = "%s - %s"
CODE[language]["^"] = "%s^(%s)"  # power
CODE[language][":"] = "%s : %s"  # expand product
CODE[language]["."] = "%s . %s"  # Hadamar product
CODE[language]["*"] = "%s * %s"  # reduce product
CODE[language]["ParDiff"] = "ParDiff(%s,%s)"
CODE[language]["TotalDiff"] = "TotalDiff(%s,%s)"
CODE[language]["Integral"] = "Integral({integrand!s} :: {differential!s} in [{lower!s},{upper!s} ])"
# CODE[language]["Interval"] = "interval(%s in [%s , %s])"
CODE[language]["Product"] = "Product( {argument!s} \, {index!s} )"
CODE[language]["Instantiate"] = "Instantiate(%s, %s)"
CODE[language]["max"] = "max(%s, %s)"
CODE[language]["min"] = "min(%s, %s)"

for f in LIST_FUNCTIONS_SINGLE_ARGUMENT:  # UNITARY_NO_UNITS + UNITARY_RETAIN_UNITS:
  CODE[language][f] = f + "(%s)"  # identical syntax

CODE[language]["Root"] = "Root(%s)"

CODE[language]["()"] = "%s"  # "(%s)"   # TODO: remove bracketing of temp variable (L)
CODE[language]["index"] = "%s"
CODE[language]["index_diff_state"] = "d%s"

CODE[language]["comment"] = ""
CODE[language]["obj"] = "{}"

CODE[language]["variable"] = "%s"  # label of the variable


# ============================================================================================
language = "latex"
CODE[language] = {}
CODE[language]["bracket"] = r"\left(" + r"%s" + r"\right)"
CODE[language][","] = ","

CODE[language]["+"] = r"%s  + %s"
CODE[language]["-"] = r"%s  - %s"
CODE[language]["^"] = r"%s^{%s}"  # power
CODE[language][":"] = r"%s \, {\odot} \, %s"  # .........................expand product
CODE[language]["."] = r"%s \, . \, %s"  # ...............................Hadamar product
CODE[language]["*"] = r"%s \star %s"  # ..............reduce product
CODE[language]["BlockReduce"] = r"{0} \stackrel{{ {1} \, \in \, {2} }}{{\,\star\,}} {3}"
CODE[language]["ParDiff"] =r"\frac{\partial{%s}}{\partial{%s}}"
CODE[language]["TotalDiff"] =  r"\frac{d\,{%s}}{d\,{%s}}"
CODE[language]["Integral"] = r"\int_{{ {lower!s} }}^{{ {upper!s} }} \, {integrand!s} \enskip d\,{differential!s}"
# CODE[language]["Interval"] = r"%s \in \left[ {%s} , {%s} \right] "
CODE[language]["Product"] = r"\prod_{index!s}  {argument!s} "
CODE[language]["Instantiate"] = r"\text{Instantiate}(%s, %s)"
CODE[language]["max"] = r"\mathbf{max}\left( %s, %s \right)"
CODE[language]["min"] = r"\mathbf{min}\left( %s, %s \right)"
CODE[language]["index_diff_state"] = r"\dot{%s}"

for f in UNITARY_NO_UNITS:
  CODE[language][f] = f + r"(%s)"

CODE[language]["abs"] = r"|%s|"

CODE[language]["neg"] = r"\left( -%s \right)"
CODE[language]["inv"] = r"\left( %s \right)^{-1}"
CODE[language]["sign"] = r"\text{sign} \left( %s \right)"

# CODE[language]["blockProd"] = r"\displaystyle \prod_{{ {1} \in {2} }} {0}"
CODE[language]["Root"] = r"Root\left( %s\right)"
# CODE[language]["MixedStack"] = r"\text{MixedStack}\left( %s \right)"
# CODE[language]["Stack"] = r"\text{Stack}\left( %s \right)"

CODE[language]["diffSpace"] = r"\text{diffSpace}(%s)"
CODE[language]["left"] = r"\left({%s}\right)^{-\epsilon}"
CODE[language]["right"] = r"\left({%s}\right)^{+\epsilon}"
CODE[language]["equation"] = "%s = %s"
CODE[language]["()"] = "%s"  # r"\left(%s \right)"
#
CODE[language]["index"] = "{\cal{%s}}"
CODE[language]["block_index.delimiter"] = " "

CODE[language]["variable"] = "%s"  # label of the variable

CODE[language]["block_index"] = "{%s" + \
                                CODE[language]["block_index.delimiter"] + \
                                "%s}"


# ============================================================================================
# language = "RDF"
# CODE[language] = {}
# CODE[language]["bracket"] = DELIMITERS_alias["("] + r"%s" + DELIMITERS_alias["\right)"]
# CODE[language][","] = ","
#
# CODE[language]["+"] = r"%s" + OPERATORS_alias["+"] + r"%s"
# CODE[language]["-"] = r"%s" + OPERATORS_alias["-"] + r"%s"
# CODE[language]["^"] = r"%s" + OPERATORS_alias["^"] + r"%s"
# CODE[language][":"] = r"%s" + OPERATORS_alias[":"] + r"%s" # .........................Khatri-Rao product
# CODE[language]["."] = r"%s \, . \, %s"  # ...............................expand product
# CODE[language]["|"] = r"%s \stackrel{%s}{\,\star\,} %s"  # ..............reduce product
# CODE[language]["BlockReduce"] = r"{0} \stackrel{{ {1} \, \in \, {2} }}{{\,\star\,}} {3}"
# CODE[language]["ParDiff"] = r"\ParDiff{%s}{%s}"
# CODE[language]["TotalDiff"] = r"\TotDiff{%s}{%s}"
# CODE[language]["Integral"] = r"\int_{{ {lower!s} }}^{{ {upper!s} }} \, {integrand!s} \enskip d\,{differential!s}"
# # CODE[language]["Interval"] = r"%s \in \left[ {%s} , {%s} \right] "
# CODE[language]["Product"] = r"\prod_{index!s}  {argument!s} "
# CODE[language]["Instantiate"] = r"\text{Instantiate}(%s, %s)"
# CODE[language]["max"] = r"\mathbf{max}\left( %s, %s \right)"
# CODE[language]["min"] = r"\mathbf{min}\left( %s, %s \right)"
# CODE[language]["index_diff_state"] = r"\dot{%s}"
#
# for f in UNITARY_NO_UNITS:
#   CODE[language][f] = f + r"(%s)"
#
# CODE[language]["abs"] = r"|%s|"
#
# CODE[language]["neg"] = r"\left( -%s \right)"
# CODE[language]["inv"] = r"\left( %s \right)^{-1}"
# CODE[language]["sign"] = r"\text{sign} \left( %s \right)"
#
# CODE[language]["blockProd"] = r"\displaystyle \prod_{{ {1} \in {2} }} {0}"
# CODE[language]["Root"] = r"Root\left( %s\right)"
# CODE[language]["MixedStack"] = r"\text{MixedStack}\left( %s \right)"
# CODE[language]["Stack"] = r"\text{Stack}\left( %s \right)"
#
# CODE[language]["diffSpace"] = r"\text{diffSpace}(%s)"
# CODE[language]["left"] = r"\left({%s}\right)^{-\epsilon}"
# CODE[language]["right"] = r"\left({%s}\right)^{+\epsilon}"
# CODE[language]["equation"] = "%s = %s"
# CODE[language]["()"] = "%s"  # r"\left(%s \right)"
# #
# CODE[language]["index"] = "{\cal{%s}}"
# CODE[language]["block_index.delimiter"] = " "
#
# CODE[language]["variable"] = "%s"  # label of the variable
#
# CODE[language]["block_index"] = "{%s" + \
#                                 CODE[language]["block_index.delimiter"] + \
#                                 "%s}"

# generating the operator lists for the equation editor

OnePlace_TEMPLATE = LIST_FUNCTIONS
TwoPlace_TEMPLATE = ["+",
                     "-",
                     "^",
                     ".",
                     ":",
                     "*",
                     "ParDiff",
                     "TotalDiff",
                     "max",
                     "min",
                     "Instantiate",
                     ]
ThreePlace_TEMPLATE = ["blockProd"]
internal = LANGUAGES["internal_code"]
Special_TEMPLATE = {
        "Integral"   : CODE[internal]['Integral'].format(integrand='var',
                                                         differential='t',
                                                         lower='to',
                                                         upper='te'),
        }

# TODO: not nice needs fixing
OPERATOR_SNIPS = []
internal = LANGUAGES["internal_code"]
for i in OnePlace_TEMPLATE:
  OPERATOR_SNIPS.append(CODE[internal][i] % ('a'))
for i in TwoPlace_TEMPLATE:
  try:
    OPERATOR_SNIPS.append(CODE[internal][i] % ('a', 'b'))
  except:
    print("failed with :", i)

# for i in ThreePlace_TEMPLATE:
#   OPERATOR_SNIPS.append(CODE[internal]['|'] % ('a', 'b', 'c'))

for c in Special_TEMPLATE:
  OPERATOR_SNIPS.append(str(Special_TEMPLATE[c]))

# OPERATOR_SNIPS.append(CODE[internal]["Root"] % ('expression to be explicit in var'))


def makeInterfaceVariableName(symbol):
  return TEMPLATES["interface_variable"] % symbol


def revertInterfaceVariableName(symbol):
  return symbol[1:]


def setValidator(lineEdit):
  validator = QtGui.QRegExpValidator(VAR_REG_EXPR, lineEdit)
  lineEdit.setValidator(validator)
  return validator


def isVariableInExpression(expression, variable_ID):
  """
  is a defined variable in expression? -- logical
  expression : internally coded
  variable_ID : integer ID
  """

  items = expression.split(" ")
  for w in items:
    if len(w) > 0:
      if w[0] == "V":
        lbl, strID = w.split("_")
        v_ID = int(strID)  # w.replace("V_", "").strip())
        if v_ID == variable_ID:
          return True
  return False


def renderExpressionFromGlobalIDToInternal(expression, variables, indices):
  """
  render from global ID representation to internal text representation

  Issue here is that the variable may be of type PhysicalVariable in which case the label is an attribute
    or a dictionary as read from the variable file directly, in which case is is a hash tag
  :param expression:
  :param variables:
  :param indices:
  :return:
  """
  s = ""
  items = expression.split(" ")
  for w in items:
    if w:
      hash = " " + w
      if w[0] in ["D", "O", "F"]:
        # if "{" in w:
        #   print("found a {")
        r = CODE[LANGUAGES["global_ID_to_internal"]]
        try:
          a = CODE[LANGUAGES["global_ID_to_internal"]][hash]
        except:
          # print("debugging", hash)
          a = ""
      elif w[0] == "V":
        # v_ID = int(w.replace("V_", "").strip())
        try:
          a = variables[w].label  # RULE: label is used not alias TODO: fix alias edit table -- remove alias
        except:
          a = variables[w]["label"]
      elif w[0] == "I":
        i_ID = w #int(w.replace("I_", "").strip())
        a = indices[i_ID]["aliases"]["internal_code"]  # RULE: we use alias to reduce length of string
      else:
        a = "bla......%s........" % w
      s += " "
      s += a
  return s



def renderIndexListFromGlobalIDToInternal(indexList, indices):
  """
  render an index list to display representation
  :param indexList:
  :param indices:
  :return: string with indices
  """
  s = ""
  count = 0
  for i_ID in indexList:
    sI = indices[i_ID]["aliases"]["internal_code"]
    if count == 0:
      s += "%s " % sI
    else:
      s += ",  %s" % sI
    count += 1

  return s


class VarEqTree():
  """
  Generate a variable equation tree starting with a variable

  self. tree is an object tree with
  tree :
      tree.tree :: a recursive dictionary
                  primary hash :: enumerated object (variable | equation)
                  secondary hash :: ancestor & children
      tree.nodes :: a dictionary with
                  hash :: IDs identifiers of type enummeration (integers)
                  value :: variable_<variable ID> | equation_<equation_ID>
                  a recursive dictionary
      tree.IDs :: inverse of tree.nodes
                  hash :: variable_<variable ID> | equation_<equation_ID>
                  value :: IDs identifiers of type enumberation (integers)
  """

  def __init__(self, variables, var_ID, blocked, start_equation=None):
    self.TEMPLATE_VARIABLE = "variable_%s"
    self.TEMPLATE_EQUATION = "equation_%s"
    self.variables = variables
    self.var_ID = var_ID
    self.blocked = blocked
    self.start_equation = start_equation
    self.tree = ObjectTree(self.TEMPLATE_VARIABLE % var_ID)

    self.initObjects()

    self.makeObjecTree()

  def makeObjecTree(self):
    blocked_set = set(self.blocked)
    var_ID = self.var_ID
    self.starting_node_ID_label = self.TEMPLATE_VARIABLE % var_ID

    Tree = self.tree
    stack = []
    eq_IDs_set = set(self.get_equs(var_ID)) - blocked_set
    if self.start_equation != None:
      eq_IDs = [self.start_equation]
      for eq in eq_IDs_set:
        if eq not in eq_IDs:
          eq_IDs.append(eq)
    else:
      eq_IDs = sorted(eq_IDs_set)
      if len(eq_IDs) == 0:
        print("there is no equation for this variable")
        return
      self.start_equation = eq_IDs[0]

    for eq_ID in eq_IDs:
      # if eq_ID == 4:
      #   print("debugging -- found 4")
      stack.append((var_ID, eq_ID))
    first = True

    var_label = self.TEMPLATE_VARIABLE % var_ID
    self.addVariable(var_label, first)

    while stack:
      var_ID, eq_ID = stack[0]
      stack = stack[1:]  # shift stack

      equ_label = self.TEMPLATE_EQUATION % eq_ID
      var_label = self.TEMPLATE_VARIABLE % var_ID

      Tree.addChildtoNode(equ_label, var_label)
      self.addEquation(equ_label)
      self.addLink(equ_label, var_label)

      vars = self.get_equation_incidence_list(var_ID, eq_ID)
      for next_var_ID in vars:
        if next_var_ID == "95":
          print("debugging found 95")
        next_var_label = self.TEMPLATE_VARIABLE % next_var_ID
        if next_var_label not in Tree["IDs"]:
          Tree.addChildtoNode(next_var_label, equ_label)
          self.addVariable(next_var_label)
          next_eq_IDs = set(self.get_equs(next_var_ID)) - blocked_set
          for next_eq_ID in next_eq_IDs:
            if next_eq_ID:
              stack.append((next_var_ID, next_eq_ID))
        self.addLink(next_var_label, equ_label)
    print("debugging -- end of iteration")

  def initObjects(self):
    return None

  def addVariable(self, var_ID, first=False):
    None

  def addEquation(self, eq_ID, first=False):
    None

  def addLink(self, source_label, sink_label):
    return None

  def get_equs(self, var_ID):
    return sorted(self.variables[var_ID]["equations"].keys())

  def get_equation_incidence_list(self, var_ID, eq_ID):
    return self.variables[var_ID]["equations"][eq_ID]["incidence_list"]


class DotGraphVariableEquations(VarEqTree):

  # pdfposter -p2x4A3 vars_equs.pdf try2.pdf

  def __init__(self, variables, indices, var_ID, ontology_name, blocked, file_name="vars_equs", start_equation=None):
    self.ontology_name = ontology_name
    self.indices = indices
    self.variables = variables
    self.file_name = file_name
    self.file = None
    self.start_equation = start_equation

    self.latex_directory = os.path.join(DIRECTORIES["ontology_repository"], "%s",
                                        DIRECTORIES["latex"]) % ontology_name

    self.ontology_location = DIRECTORIES["ontology_location"] % ontology_name

    super().__init__(variables, var_ID, blocked=blocked, start_equation=start_equation)

  def view(self):
    self.simple_graph.view()  # generates pdf
    os.remove(self.file)

  def render(self):
    self.simple_graph.render(self.outputFile, cleanup=True)
    return self.outputFile

  def initObjects(self):

    self.var_labels, self.equ_labels = self.__make_var_and_equ_labels()

    o_template = os.path.join(DIRECTORIES["ontology_repository"], self.ontology_name,
                              DIRECTORIES["ontology_graphs_location"],
                              "%s")
    # the tree of networks
    f = o_template % self.file_name  # "vars_equs"
    self.outputFile = f
    print(f)
    graph_attr = {}
    graph_attr["nodesep"] = "1"
    graph_attr["ranksep"] = ".5"
    graph_attr["color"] = "black"
    graph_attr["splines"] = "true"  # ""polyline"
    edge_attr = {}
    edge_attr["tailport"] = "s"
    edge_attr["headport"] = "n"
    self.simple_graph = Digraph("T", filename=f)
    self.simple_graph.graph_attr = graph_attr
    self.simple_graph.edge_attr = edge_attr

    self.file = f
    print("debugging -- get started")

  def addLink(self, source_label, sink_label):
    if sink_label == self.starting_node_ID_label:
      colour = "red"
    else:
      colour = "black"
    self.simple_graph.edge(source_label, sink_label, color=colour)
    return None

  def __make_var_and_equ_labels(self):
    var_labels = {}
    equ_labels = {}
    port_variable = {}

    # v_name = FILES["coded_variables"] % (self.ontology_location, "latex")
    # var_labels_raw= getData(v_name)
    for var_id in self.variables:
      ID = self.TEMPLATE_VARIABLE % var_id
      var_labels[ID] = self.variables[var_id]["aliases"]["internal_code"]  # var_labels_raw[str(var_id)]["latex"] #
      for equ_ID in self.variables[var_id]["equations"]:
        ID = self.TEMPLATE_EQUATION % equ_ID
        equation = self.variables[var_id]["equations"][equ_ID]["rhs"]["global_ID"]
        rendered_expressions = renderExpressionFromGlobalIDToInternal(equation, self.variables,
                                                                      self.indices)
        equ_labels[ID] = rendered_expressions

    return var_labels, equ_labels

  def addVariable(self, var_ID_label, first=False):

    node_ID_label = str(var_ID_label)
    _dummy, ID_str = node_ID_label.split("_",1)
    V_ID_picture = ID_str
    # node_label = self.var_labels[var_ID_label]
    if first:
      colour = "red"
    else:
      colour = "cornsilk"
      if self.variables[ID_str]["port_variable"] and (self.variables[ID_str]["type"] == "state"):
        colour = "green"
    image = os.path.join(self.latex_directory, "%s.png" % ID_str)
    if not os.path.exists(image):
      print("missing picture file:", image)
      reply = makeMessageBox("equation picture file missing %s " % image, buttons=["OK"],
                             infotext="-- run equation composer and generate files")
    self.simple_graph.node(node_ID_label, "", image=image, style="filled", color=colour)

  def addEquation(self, eq_ID_label, first=False):
    node_ID_label = str(eq_ID_label)
    node_label = self.equ_labels[eq_ID_label]  # Note: can be used instead of picture
    _dummy, ID_str = node_ID_label.split("_",1)
    colour = "cyan"
    image = os.path.join(self.latex_directory, "%s.png" % ID_str)
    if not os.path.exists(image):
      print("missing picture file %s" % image)
      reply = makeMessageBox("equation picture file missing %s" % image, buttons=["OK"],
                             infotext="-- run equation composer and generate files")
    self.simple_graph.node(node_ID_label, '', image=image, shape="box", height="0.8cm", style="filled", color=colour)


def AnalyseBiPartiteGraph(variable_ID, ontology_container, ontology_name, blocked, file_name, start_equation=None):
  print("debugging --- variable ", variable_ID)
  var_equ_tree = DotGraphVariableEquations(ontology_container.variables,
                                           ontology_container.indices,
                                           variable_ID,
                                           ontology_name,
                                           blocked=blocked,
                                           file_name=file_name,
                                           start_equation=start_equation)

  print("debugging -- dotgraph done")
  buddies = getListOfBuddies(ontology_container, var_equ_tree, variable_ID)

  assignments = VariantRecord(tree=var_equ_tree.tree["tree"],
                              nodes=var_equ_tree.tree["nodes"],
                              IDs=var_equ_tree.tree["IDs"],
                              root_variable=var_equ_tree.var_ID,
                              root_equation=start_equation,
                              blocked_list=blocked,
                              buddies_list=list(buddies)
                              )

  return var_equ_tree, assignments


def getListOfBuddies(ontology_container, var_equ_tree, variable_ID):
  # finding the buddies -- currently the buddies are connected via the interfaces
  # the first variable defines the network and any variable that is in a interface is connected to a buddy
  # TODO: reconsider the definition and handling of the interfaces
  buddies = set()
  the_network = ontology_container.variables[variable_ID]["network"]
  for id in var_equ_tree.tree["IDs"]:
    o, str_ID = id.split("_",1)
    ID = str_ID
    if o == "variable":
      network = ontology_container.variables[ID]['network']
      if CONNECTION_NETWORK_SEPARATOR in network:
        buddies.add((ID, network))

  return buddies


def makeLatexDoc(file_name, assignments: entity.Entity, ontology_container, dot_graph_file=""):
  ontology_location = ontology_container.ontology_location
  ontology_name = ontology_container.ontology_name
  variables = ontology_container.variables

  latex_var_equ = []
  count = 0

  equation_dictionary = ontology_container.equation_variable_dictionary

  for ID in assignments["tree"]:
    component = assignments["nodes"][ID]
    if "E_" in component:
      _,eq_str_ID = component.split("_",1)
      var_str_ID = equation_dictionary[eq_str_ID][0]
      _,var_ID = var_str_ID.split("_",1)
      lhs = variables[var_str_ID]["aliases"]["latex"]
      rhs = equation_dictionary[eq_str_ID][1]["rhs"]["latex"]
      eq = "%s := %s" % (lhs, rhs)
      s = [count, str(var_ID), ID, eq, str(variables[var_str_ID]["tokens"])]
      latex_var_equ.append(s)
      count += 1

  for ID in assignments["tree"]:
    component = assignments["nodes"][ID]
    if "V_" in component:
      _,var_str_ID = component.split("_",1)
      _,var_ID = var_str_ID.split("_",1)
      eqs = variables[var_str_ID]["equations"]
      if not eqs:
        eq = "%s :: %s" % (variables[var_str_ID]["compiled_lhs"]["latex"],
                           "\\text{port variable}")
        s = [count, var_ID, "-", eq, str(variables[var_str_ID]["tokens"])]
        latex_var_equ.append(s)
        count += 1

  print("debugging -- got here")

  # get variable in LaTex form
  root_var = assignments["root_variable"]
  lhs = variables[root_var]["aliases"]["latex"] #compiled_variable_labels[root_var]

  latex_var_equ = reversed(latex_var_equ)
  THIS_DIR = dirname(abspath(__file__))
  j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
  template = FILES["latex_template_equation_list"]
  body = j2_env.get_template(template).render(variable=lhs, equations=latex_var_equ, dot=dot_graph_file)
  f_name = FILES["latex_equation_list"] % (ontology_name, file_name)
  f = open(f_name, 'w')
  f.write(body)
  f.close()

  shell_name = FILES["latex_shell_var_equ_list_command"] % ontology_name
  latex_location = DIRECTORIES["latex_location"] % ontology_name
  args = ['bash', shell_name, latex_location, file_name]
  print('ARGS: ', args)

  try:  # reports an error after completing the last one -- no idea
    make_it = subprocess.Popen(
            args,
            start_new_session=True,
            # check=True
            )
    out, error = make_it.communicate()
  except:
    print("equation generation failed")
    pass


def showPDF(file_name):
  args = ["evince", file_name]
  view_it = subprocess.Popen(args, start_new_session=True)
  out, error = view_it.communicate()


def generateLatexImages(ontology_name, ontology_container):

  # all_variables, _, all_equations = load_var_idx_eq_from_file(ontology_name)

  variables = ontology_container.variables
  equations = ontology_container.equation_dictionary
  incidence_dictionary = ontology_container.incidence_dictionary
  inv_incidence_dictionary = ontology_container.inv_incidence_dictionary

  latex_folder_path =  Path(DIRECTORIES["latex_doc_location"] % ontology_name  )


  latex_info = {}
  modified_vars = []
  for var_id in variables:
    var_png_file_path = latex_folder_path / (var_id + ".png")
    if os.path.exists(var_png_file_path): #.exists():
      png_mod_date = datetime.fromtimestamp(var_png_file_path.stat().st_mtime)
      modified = variables[var_id]["modified"]
      date_format = "%Y-%m-%d %H:%M:%S"
      var_mod_date = datetime.strptime(modified, date_format)
      # if "165" in var_id:
      #   print("got it",png_mod_date, var_mod_date,  png_mod_date > var_mod_date)
      if png_mod_date > var_mod_date:
        continue

    var_latex_alias = variables[var_id]["aliases"]["latex"]
    latex_info[var_id] = "$" + var_latex_alias + "$" #"$" + var.get_alias("latex") + "$"
    modified_vars.append(var_id)
    # self.writeMessage("modified variable", var_id)

  for eq_id in equations: #, eq in all_equations.items():
    eq_png_file_path = latex_folder_path / (eq_id + ".png")
    if eq_png_file_path.exists():
      png_mod_date = datetime.fromtimestamp(eq_png_file_path.stat().st_mtime)
      modified = equations[eq_id]["modified"] #eq.get_mod_date()
      date_format = "%Y-%m-%d %H:%M:%S"
      eq_mod_date = datetime.strptime(modified, date_format)
      if png_mod_date > eq_mod_date:
        continue
    (var_id,_) = incidence_dictionary[eq_id]
    lhs = variables[var_id]["aliases"]["latex"]
    rhs = equations[eq_id]["rhs"]["latex"] #eq.get_translation("latex")
    # pp(latex_translation)
    latex_info[eq_id] = "$" + lhs  + "=" + rhs + "$"

# pick up the equations that are modified due to changing variable
  for var_id in modified_vars:
    for eq_id in inv_incidence_dictionary[var_id]:
      (var_id, _) = incidence_dictionary[eq_id]
      lhs = variables[var_id]["aliases"]["latex"]
      rhs = equations[eq_id]["rhs"]["latex"] #eq.get_translation("latex")
      # pp(latex_translation)
      latex_info[eq_id] = "$" + lhs  + "=" + rhs + "$"



  original_work_dir = os.getcwd()
  os.chdir(latex_folder_path)
#
  for file_name, latex_alias in latex_info.items():
    # f_path = DIRECTORIES["latex_location"]%self.ontology_name
    # f_name = os.path.join(f_path, file_name)
    # print(f_name)
    f = open(file_name + ".tex", "w") # as f:
    f.write("\\documentclass[border=1pt]{standalone}\n")
    f.write("\\usepackage{amsmath}\n")
    f.write("\\begin{document}\n")
    f.write(latex_alias)
    f.write("\\end{document}\n")
    f.close()

    print("......................................................................................................................")
    time.sleep(1)

    # location = DIRECTORIES["latex_main_location"] % self.ontology_location
    # f_name = FILES["latex_shell_var_equ_doc_command_exec"] % self.ontology_location
    # documentation_file = FILES["latex_documentation"] % self.ontology_name
    # if not self.compile_only:
    #   saveBackupFile(documentation_file)
    # self.writeMessage("busy making var/eq images")
    p = QtCore.QProcess()
    p.startDetached("sh", ["resources/make_images.sh", file_name])

    # subprocess.run(["latex", "-interaction=nonstopmode", file_name + ".tex"],
    #                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # subprocess.run(["dvipng", "-D", "150", "-T", "tight", "-z", "9",
    #                 "-bg", "Transparent", "-o", file_name + ".png", file_name + ".dvi"],
    #                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("cwd", os.getcwd(), "--", file_name + ".tex")

    #os.remove(file_name + ".tex")
    # os.remove(file_name + ".aux")
    # os.remove(file_name + ".log")
    # os.remove(file_name + ".dvi")

  os.chdir(original_work_dir)

def dateString():
  now = datetime.now()  # datetime object containing current date and time
  now_string = now.strftime("%Y-%m-%d %H:%M:%S")
  return now_string

def sortingVariableAndEquationKeys(keys):
  keys_dic = {}
  for k in keys:
    # print(k)
    _, num = k.split("_")
    keys_dic[int(num)] = k

  sorted_keys = []
  print(sorted(keys_dic.keys()))
  for k in sorted(keys_dic.keys()):
    sorted_keys.append(keys_dic[k])
  return sorted_keys

if __name__ == '__main__':
  k = ['E_8', 'E_9', 'E_10', 'E_1', 'E_11', 'E_12', 'E_13', 'E_14', 'E_15', 'E_2', 'E_3', 'E_4', 'E_5', 'E_6', 'E_7']
  dk = sortingVariableAndEquationKeys(k)
  print("dk", dk)
