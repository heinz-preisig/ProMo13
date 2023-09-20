#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 define data record structures
===============================================================================

This program is part of the ProcessModelling suite

This defines the record structures for all data records and the internal naming, thus the aliasing
The intention is to bring this further up into an ontology

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "03.04.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "7.00"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from collections import OrderedDict

from Common.common_resources import VARIABLE_TYPE_INTERFACES
from OntologyBuilder.OntologyEquationEditor.resources import CODE
from OntologyBuilder.OntologyEquationEditor.resources import IRI_make
from OntologyBuilder.OntologyEquationEditor.resources import LANGUAGES
from OntologyBuilder.OntologyEquationEditor.variable_framework import Units

TEMPLATES = {
        "incidence_matrix"          : "F_%s_%s",  # %(token, transfer_mechanism)
        "incidence_matrix_interface": "FI_%s_%s",  # %(token, transfer_mechanism)
        "projection_matrix"         : "P_%s_%s",  # %(<arc|node|conversion>, typed_token)
        "ratio_matrix"              : "R_%s",
        }


class OntologyContainerFile(dict):  # TODO: integrate typed token conversion into file
  def __init__(self, version):
    super()
    self["version"] = version  # ...................................................................... ontology version
    self["ontology_tree"] = OrderedDict()  # ........domain tree RULE: hand defined should correspond to subtree of EMMO
    self["interfaces"] = {}
    self["rules"] = {}  # rules are added in the editor_foundation_ontology_gui_impl as fixed rules


class VariableFile(dict):
  def __init__(self, variables, indices, version, ProMoIRI):
    self["version"] = version  # ..................................................................... ontology version
    self["variables"] = variables  # variable dictionary hash-key: global variable_ID contains also equation dictionary
    self["indices"] = indices  # .............................................. incidence dictionary hash-key: index_ID
    self["Ontology_global_IDs"] = ProMoIRI  # ................... RULE: variable and equation ID is global to ontology




class RecordVariable(dict):
  def __init__(self):
    """
    this is the basic record definition
    internally it is dynamically we use an additional dictionary for the compiled versions
    TODO: we need to decide if we store the ID version or the ProMo version (currently called internal)
    """
    super()  # .............................................. " the global var_ID is the hash tag -- enumeration type"
    self["label"] = ""
    self["type"] = ""  # ............................................................................... variable class
    self["network"] = ""  # ..................................................  specifies application/definition domain
    self["doc"] = ''
    self["index_structures"] = []  # ...........................................................    index_IDs: integers
    self["units"] = None,  # 8 integers exponents of time, length, amount, mass, temperature, current, light, nil
    self["equations"] = {}  # ............................................................ hash is equation_ID: integer
    self["aliases"] = {}  # ..................................  one for each language, with language being the hash key
    self["port_variable"] = False  # ................. port variables are at the bottom of the definition -- foundation
    self["tokens"] = []  # ...................................................................................... token
    self["IRI"] = "None"  # ......................................................... qudt or promo IRI for the variable
    self["created"] = None  # .....................................................................  creation data & time
    self["modified"] = None  # ...............................................................  modification data & time


# class RecordEquation(dict):
#   def __init__(self):  # ...... lhs variable is not included here, as the equation is stored in the lhs variable record
#     super()
#     " the equation_ID is the hash tag -- enumberation type"
#     self["rhs"] = ""  # ..................................................... global_ID coded string for the expression
#     self["doc"] = ""  # ............................................................................ documention string
#     self["network"] = ""  # ...........................may not be the same as the variable, but further out in the tree
#     self["incidence_list"] = []  # .................................................. list of variables in the equation
#     self["type"] = ""  # ............................................................................... equation class
#     self["create"] = None  # .....................................................................  creation data & time
#     self["modified"] = None  # ...............................................................  modification data & time


# class RecordEquation_6(dict):  # TODO: obsolete once Tobias is finished
#   def __init__(self):
#     super()
#     self["lhs"] = ''
#     self["rhs"] = ''
#     self["incidence_list"] = []
#     self["network"] = ''
#     self["equation_ID"] = ''


class EquationAssignment(dict):  # defines / controls entity definition
  def __init__(self, tree=None, buddies=None):
    super().__init__()
    self = {
            "tree"   : tree,  # ObjectTree dict
            "buddies": buddies,  # buddies
            }
    print("gotten here", self)


class RecordProMoIRI(dict):
  def __init__(self):
    self["variable"] = 0
    self["equation"] = 0


class RecordIndex(dict):  # ................................................................... hash is global index_ID
  def __init__(self):
    super()
    self["type"] = "index"  # .............................................................................. index class
    self["label"] = ""  # ........................................................................ label for readability
    self[
      "network"] = []  # TODO : the list of networks is available from the ontology >> heirs_network_dictionary -->
    # simplify
    self["aliases"] = {}  # ...................................................................... hash-key is language
    self["tokens"] = None
    self["IRI"] = "None"  # ......................................................... qudt or promo IRI for the variable


class RecordBlockIndex(dict):  # .............................................................. hash is global index_ID
  def __init__(self):
    super()
    self["type"] = "block_index"  # ....................................................................... index class
    self["label"] = ""  # ........................................................................ label for readability
    self["indices"] = []  # ................................................. the two indices making up the block index
    self["network"] = []  # TODO: list of networks it applies to ???
    self["aliases"] = {}  # ...................................................................... hash-key is language
    self["IRI"] = "None"  # ......................................................... qudt or promo IRI for the variable


# class RecordIncidenceMatrix(RecordVariable):  # obsolete for the time being
#   def __init__(self, network, token, transfer_mechanism, node_index, arc_index="arc"):
#     RecordVariable.__init__(self)
#     self["label"] = TEMPLATES["incidence_matrix"] % (token, transfer_mechanism)
#     self["type"] = "network"
#     self["network"] = network
#     self["doc"] = "incidence matrix"
#     self["tokens"] = token
#     self["transfer_mechanism"] = transfer_mechanism
#     self["index_structures"] = [node_index, arc_index]
#     self["immutable"] = True  # TODO: is this useful -- protect from stupidities ???


# class RecordProjectionMatrixConversion(RecordVariable):  # obsolete for the time being
#   def __init__(self, network, convertion, block_index_label):
#     RecordVariable.__init__(self)
#     self["label"] = TEMPLATES["projection_matrix"] % ("convertion", block_index_label)
#     self["network"] = network
#     self["doc"] = "projection matrix"
#     self["type"] = "network"
#     self["index_structures"] = [convertion, block_index_label]
#     self["immutable"] = True
#
#
# class RecordProjectionMatrix(RecordVariable):  # obsolete for the time being
#   def __init__(self, for_what, network, typed_token_label, typed_token_ID, block_index_ID):
#     RecordVariable.__init__(self)
#     self["label"] = TEMPLATES["projection_matrix"] % (for_what, typed_token_label)
#     self["network"] = network
#     self["doc"] = "projection matrix"
#     self["type"] = "network"
#     self["index_structures"] = [typed_token_ID, block_index_ID]
#     self["immutable"] = True
#
#
# class RecordConversionRatioMatrix(RecordVariable):  # obsolete for the time being
#   def __init__(self, network, typed_token_label, convertion_ID, typed_token_ID):
#     RecordVariable.__init__(self)
#     self["label"] = TEMPLATES["ratio_matrix"] % typed_token_label
#     self["network"] = network
#     self["doc"] = "convertion ratio matrix"
#     self["type"] = "network"
#     self["index_structures"] = [convertion_ID, typed_token_ID]
#     self["immutable"] = True


class Interface(dict):  # .........TODO: check if still in use ........................... interface record definition
  def __init__(self, interface_network_label, left_network, right_network, left_variable_classes):
    self["type"] = "event"  # ............................................ RULE: hard wired node type
    self["doc"] = ""
    self["index_structures"] = ["node"]  # ................................ RULE: hard wired index
    self["label"] = interface_network_label
    self["left_network"] = left_network
    self["right_network"] = right_network
    self["left_variable_classes"] = left_variable_classes
    self["internal_variable_classes"] = [VARIABLE_TYPE_INTERFACES]    # ..... RULE: hard wired interface variable class
    self["token"] = "information"  # ..................................... RULE: hard wired token
    self["mechanism"] = "link"  # ........................................ RULE: hard wired mechanism
    self["nature"] = "unidirectional"  # ................................. RULE: hard wired tranfer nature



def makeCompleteVariableRecord(var_ID,  # TODO: remove ?? and replace with variableRecord
                               label="",
                               type="",
                               network="",
                               doc="",
                               index_structures=[],
                               units=Units(),
                               equations={},
                               aliases={},
                               port_variable=False,
                               tokens=[],
                               IRI=None,
                               created=None,
                               compiled_lhs = {}
                               ):
  """
  NOTE: there is a problem here with the defaults -- do not use them, but define everthing explicitly.
  functional programming in Python has its problems. Here the defaults cause some problems -- why I do not know.
  But the consequence is that each of the items must be defined. So the only reason to implement it like this is to
  keep it centralised, in case things change down the road
  :param var_ID:
  :param label:
  :param type:
  :param network:
  :param doc:
  :param index_structures:
  :param units:
  :param equations:
  :param aliases:
  :return:
  """
  self = {}
  self["label"] = label  # ........................................................................ is hash in variables
  self["type"] = type
  self["network"] = network
  self["doc"] = doc
  self["index_structures"] = index_structures  # ................................................... as IDs == integers
  self["units"] = units  # ....................................................................
  self["equations"] = equations  # ..................................................... hash is equation ID, an integer
  self["aliases"] = aliases  # .....could be in code - not handy and not quite logical: there is also a compiled version
  self["port_variable"] = port_variable  # ............ port variables are at the bottom of the definition -- foundation
  self["tokens"] = tokens  # ..................................................................................... token
  # self["IRI"] = IRI_make("promo", network, label)  # NOTE: label is to be adjusted when changed
  self["IRI"] = IRI_make("promo", label)  # NOTE: label is to be adjusted when changed
  self["created"] = created
  self["modified"] = created
  self["compiled_lhs"] = {"global_ID": var_ID}

  for language in LANGUAGES["aliasing"]:
    self["aliases"][language] = label
  self["aliases"]["global_ID"] = var_ID #CODE["global_ID"]["variable"] % var_ID

  return self


def makeCompletEquationRecord(rhs="", type="generic", network="", doc="", incidence_list=[], created=None):
  self = {"rhs"           : {"global_ID": rhs},
          "type"          : type,
          "doc"           : doc,
          "network"       : network,
          "incidence_list": incidence_list,
          "created"       : created,
          "modified"      : created
          }
  return self
