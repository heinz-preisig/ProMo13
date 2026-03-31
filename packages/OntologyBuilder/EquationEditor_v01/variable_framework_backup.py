"""
===============================================================================
 THE variable framework
===============================================================================

Translate  between global  representation  and local  representation.  Could be
extended  to do  the compilation  job as  well removing it  from  the  phys var
package.


Section Abstract Syntax
=======================

The  module  generates  variables  and  equations  building  on  the classes of
"physvars" the physical variables module.

The   variables   and    equations   are   stored   in   the   variable   space
(class physvars.VariableSpace).  Each  variable  may  be  given  by alternative
equations. Alternatives are coded into the variable name by adding a __V## thus
two underlines and an integer number.


 Equation / variable factory
 Generates two dictionaries and a list:
 EQUATIONS: a dictionary  of equations with  the key being the defined variable
            if the equation is implicit a new zero variable is to be defined.

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 04. 23"
__since__ = "2014. 10. 07"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "7.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# TODO: think about removing the compilation from the physvar package


import copy
import os
from collections import OrderedDict

from jinja2 import Environment
from jinja2 import FileSystemLoader

from Common.record_definitions import RecordIndex
from Common.record_definitions import makeCompletEquationRecord
from Common.record_definitions import makeCompleteVariableRecord
from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from OntologyBuilder.EquationEditor_v01.resources import CODE
from OntologyBuilder.EquationEditor_v01.resources import dateString
from OntologyBuilder.EquationEditor_v01.resources import ID_prefix
from OntologyBuilder.EquationEditor_v01.resources import ID_spacer
from OntologyBuilder.EquationEditor_v01.resources import IRI_make
from OntologyBuilder.EquationEditor_v01.resources import IRI_parse
from OntologyBuilder.EquationEditor_v01.resources import LANGUAGES
from OntologyBuilder.EquationEditor_v01.resources import renderExpressionFromGlobalIDToInternal
from OntologyBuilder.EquationEditor_v01.resources import renderIndexListFromGlobalIDToInternal
from OntologyBuilder.EquationEditor_v01.resources import TEMP_VARIABLE
from OntologyBuilder.EquationEditor_v01.resources import TEMPLATES
from OntologyBuilder.EquationEditor_v01.resources import UNITARY_INVERSE_UNITS
from OntologyBuilder.EquationEditor_v01.resources import UNITARY_LOOSE_UNITS
from OntologyBuilder.EquationEditor_v01.resources import UNITARY_NO_UNITS
from OntologyBuilder.EquationEditor_v01.resources import UNITARY_RETAIN_UNITS
from OntologyBuilder.EquationEditor_v01.tpg import *

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
internal = LANGUAGES["internal_code"]



def makeIncidenceDictionaries(variables):
  """
  variables may be defined by several equations

  :param variables: variable dictionary with integrated equation dictionary
  :param expression_network: network on which the expression is defined
  :return: incidence_dictionary
            - key: equation_ID (integer)
            - value: (lhs-variable_ID, rhs-incidence list (no string) )
           inverse incidence matrix as dictionary
            - key : variable ID (integer)
            - value: list of equations (integer)
  """
  incidence_dictionary = {}
  inv_incidence_dictionary_set = {v: set() for v in variables.keys()}
  for v in variables:
    # if v == 18:
    #   print("debugging")
    try:
      equations = variables[v].equations  # variables as class Variables
    except:
      equations = variables[v]["equations"]  # variables from variable dict, the variable file format
    for e in equations:
      # if e == 197:
      #   print("debugging 197")
      inc_list = makeIncidentList(equations[e]["rhs"]["global_ID"])
      incidence_dictionary[e] = (v, inc_list)
      equations[e]["incidence_list"] = inc_list

  for e in incidence_dictionary:
    var, inc_list = incidence_dictionary[e]
    for i in inc_list:
      # inv_incidence_dictionary_set[int(i)].add(e)
      inv_incidence_dictionary_set[i].add(e)

  inv_incidence_dictionary = {}
  for e in inv_incidence_dictionary_set:
    inv_incidence_dictionary[e] = sorted(inv_incidence_dictionary_set[e])

  return incidence_dictionary, inv_incidence_dictionary  # _set


def makeIncidentList(equation_ID_coded_string):
  """
  make incidence list for a ID-coded expression
  extracts all variables into a list
  :param equation_ID_coded_string:
  :return: sorted incidence list of variable IDs [integers
  """
  incidence_list = []
  splited = equation_ID_coded_string.split(ID_spacer)
  V_id = ID_prefix["variable"]  # ID_delimiter["variable"][1:3]
  for i in splited:
    if V_id in i:
      incidence_list.append(i)
  return sorted(set(incidence_list))

def prettyIndex(variable, space):
  s_index = set(variable.index_structures)
  pretty_index = renderIndexListFromGlobalIDToInternal(s_index, space.indices)
  return pretty_index

def stringBinaryOperation(language, operation, left, right,
                          index_ID=None, indices=None):
  """
  :param language: current output language
  :param operation: what binary operation
  :param left: left argument (object)
  :param right: right argument (object)
  :param index: index (object)
  :param index_compiled for reduced product (string)
  :param global_list: the global ordered list of indices
  :return: code string

  Operation: fills in the templates stored in 
  Special case is  the reduction product.  If  the output is  a matrix-oriented
  language,  then  one  needs  to  implement  the implicit  rules of the matrix
  multiplication. Let A and B be two two-dimensional objects with the indexsets
  a,b and c. Thus we write Aab |a| Bac, thus reduce the two objects over a then
  the result is Cbc. Thus in matrix notation using the prime for transposition:

  Aab |a| Bac -->   (Aab)' *  Bac     = Cbc    1,2 |1| 1,3 = 2,3
  Aab |a| Bac -->  ((Aab)' *  Bac)'   = Ccb    1,2 |1| 1,3 = 3,2     # BUG HERE
  Aab |b| Bbc -->    Aab   *  Bbc     = Cac    1,2 |2| 2,3 = 1,3
  Aac |a| Bab -->  ((Aac)' *  Bab)'   = Cbc    1,3 |1| 1,2 = 2,3
  Aac |c| Bbc -->    Aac   * (Bbc)'   = Cab    1,3 |3| 2,3 = 1,2
  Aa  |a| Bab -->   ((Aa)' *  Bab)'   = Cb     1   |1| 1,2 = 2
  Aab |a| Ba  -->   (Aab)' *  Ba      = Cb     1,2 |1| 1   = 2
  Ab  |b| Bab -->   (Ab    * (Bab)')' = Ca     2   |2| 1,2 = 1
  Aab |b| Bb  -->    Aab   *  Bb      = Ca     1,2 |2| 2   = 1

  Rules:
  - if left  index in position 1  --> transpose left
  - if right index in position 2  --> transpose right
  - if left only one index transpose left and result

  Note:
  - The index results must always be in the original order
  - The product   Aab |b| Bab --> is forbidden as it results in a Caa, which is
    not permitted.
  - Objects with one dimension only are interpreted as column vectors
  """
  if left.type == TEMP_VARIABLE:  # NOTE:TODO:RULE: this added additional bracket
    a = CODE[language]["()"] % left.__str__()
  else:
    a = "%s" % left.__str__()
  if right.type == TEMP_VARIABLE:
    b = CODE[language]["()"] % right.__str__()
  else:
    b = "%s" % right.__str__()
  if index_ID:
    index_compiled = compile_index(index_ID,indices,language)
    s = CODE[language][operation] % (a, index_compiled, b)
  else:
    try:
      s = CODE[language][operation] % (a, b)
    except:
      # print("debugging -- wrong template")
      if operation == "*":
        s_index_a = set(left.index_structures)
        s_index_b = set(right.index_structures)
        common_index_set = s_index_a & s_index_b
        index_ID = list(common_index_set)[0]
        index_compiled = compile_index(index_ID,indices,language)
        s = CODE[language][operation] % (a, index_compiled, b)

  return s


def compile_index(index, indices, language):
  index_compiled = indices[index]["aliases"][language]
  if language == LANGUAGES["global_ID"]:
    index_compiled = " %s" % index_compiled  # Note: nasty fix  aliases do not have the space in front of the "I_"
  return index_compiled


def simulateDeletion(variables, var_ID, indices):
  """
  used in equation editor, where the variables are defined differently than in the other editors TODO: consider change -- probably not feasible or worth the trouble
  simulate deletion in order to provide feedback to the user
  :param variables: variable (dictionary)
  :param var_ID: variable ID (integer)
  :return:
  """
  d_vars = set()
  d_equs = set()

  # - key: equation_ID(integer)
  # - value: (lhs - variable_ID, rhs - incidence list (integers) )

  # incidence_dictionary structure:
  # incidence_dictionary[equation_ID:int] = (variable_ID, incidencce_list[variable_ID: no string)
  # inv_incidence_dictionary_set[variable_ID: int]= [equation_ID:int]

  incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(variables)
  reduceVars(inv_incidence_dictionary, variables, incidence_dictionary, d_vars, d_equs, var_ID)
  d_vars_text = ""
  d_equs_text = ""
  for var_ID in d_vars:
    label = variables[var_ID].label
    d_vars_text += "\n %s" % label
  for eq_ID in d_equs:
    lhs, incidence_list = incidence_dictionary[eq_ID]
    equation = variables[lhs].equations[eq_ID]
    rhs = equation["rhs"]["global_ID"]
    expression_network = equation["network"]
    rhs_rendered = renderExpressionFromGlobalIDToInternal(rhs,
                                                          variables=variables,
                                                          indices=indices,
                                                          expression_network=expression_network)
    # print("debugging -- rhs", rhs, rhs_rendered)
    d_equs_text += "\n %s" % rhs_rendered

  return d_vars, d_equs, d_vars_text, d_equs_text


def simulateDeletionImproved(variables, var_ID, indices):
  """
  Improved dependency analysis for variable deletion simulation.
  Always analyzes full dependency graph but only marks non-state variables for deletion.
  State variables are protected as they form foundation of the model.
  
  :param variables: variable dictionary
  :param var_ID: variable ID to analyze
  :param indices: indices dictionary
  :return: (vars_to_delete, eqs_to_delete, vars_text, eqs_text, protected_state_vars)
  """
  print(f"=== IMPROVED DELETION ANALYSIS: {var_ID} ===")
  
  vars_to_delete = set()
  eqs_to_delete = set()
  protected_state_vars = set()
  visited_vars = set()
  visited_eqs = set()
  
  def dfs_analyze(current_var, depth=0):
    """Depth-first search through dependency graph"""
    if depth > 20 or current_var in visited_vars:  # Prevent infinite loops
      return
    visited_vars.add(current_var)
    
    var = variables[current_var]
    print(f"  Analyzing var {current_var} (type: {var.type}) at depth {depth}")
    
    # Always track dependencies, but only mark non-state for deletion
    if var.type != "state":
      vars_to_delete.add(current_var)
      print(f"    → Marked for deletion: {current_var}")
    else:
      protected_state_vars.add(current_var)
      print(f"    → Protected state variable: {current_var}")
    
    # Find all equations using this variable
    try:
      incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(variables)
    except:
      print("Error making incidence dictionaries")
      return
      
    if current_var not in inv_incidence_dictionary:
      print(f"    → No equations use variable {current_var}")
      return
      
    for eq_id in inv_incidence_dictionary[current_var]:
      if eq_id not in visited_eqs:
        visited_eqs.add(eq_id)
        eqs_to_delete.add(eq_id)
        print(f"    → Found equation {eq_id}")
        
        # Find all variables in this equation (both LHS and RHS)
        lhs, incidence_list = incidence_dictionary[eq_id]
        
        # Analyze LHS variable
        dfs_analyze(lhs, depth + 1)
        
        # Analyze RHS variables
        for other_var in incidence_list:
          dfs_analyze(other_var, depth + 1)
  
  # Start analysis
  dfs_analyze(var_ID)
  
  # Generate user-friendly text
  vars_text = ""
  eqs_text = ""
  
  for var_id in vars_to_delete:
    try:
      label = variables[var_id].label
    except:
      label = f"Var_{var_id}"
    vars_text += f"\n  • {label} (ID: {var_id})"
  
  for eq_id in eqs_to_delete:
    try:
      lhs, incidence_list = incidence_dictionary[eq_id]
      equation = variables[lhs].equations[eq_id]
      rhs = equation["rhs"]["global_ID"]
      rhs_rendered = renderExpressionFromGlobalIDToInternal(rhs, variables=variables, indices=indices, expression_network=None)
      eqs_text += f"\n  • {rhs_rendered}"
    except:
      eqs_text += f"\n  • Equation_{eq_id}"
  
  # Add protected state vars info
  if protected_state_vars:
    vars_text += f"\n\n🛡️ PROTECTED state variables (cannot be deleted):"
    for var_id in protected_state_vars:
      try:
        label = variables[var_id].label
      except:
        label = f"Var_{var_id}"
      vars_text += f"\n  • {label} (ID: {var_id})"
  
  print(f"=== ANALYSIS COMPLETE ===")
  print(f"Variables to delete: {len(vars_to_delete)}")
  print(f"Equations to delete: {len(eqs_to_delete)}")
  print(f"Protected state vars: {len(protected_state_vars)}")
  
  return vars_to_delete, eqs_to_delete, vars_text, eqs_text, protected_state_vars


def simulateDeletionOld(variables, var_ID, indices):
  """
  Original simulation method - kept for comparison/testing
  """
  d_vars = set()
  d_equs = set()

  # - key: equation_ID(integer)
  # - value: (lhs - variable_ID, rhs - incidence list (integers) )

  # incidence_dictionary structure:
  # incidence_dictionary[equation_ID:int] = (variable_ID, incidencce_list[variable_ID: no string])
  # inv_incidence_dictionary_set[variable_ID: int]= [equation_ID:int]

  incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(variables)
  reduceVars(inv_incidence_dictionary, variables, incidence_dictionary, d_vars, d_equs, var_ID)
  d_vars_text = ""
  d_equs_text = ""
  for var_ID in d_vars:
    label = variables[var_ID].label
    d_vars_text += "\n %s" % label
  for eq_ID in d_equs:
    lhs, incidence_list = incidence_dictionary[eq_ID]
    equation = variables[lhs].equations[eq_ID]
    rhs = equation["rhs"]["global_ID"]
    rhs_rendered = renderExpressionFromGlobalIDToInternal(rhs, variables=variables, indices=indices, expression_network=None)
    # print("debugging -- rhs", rhs, rhs_rendered)
    d_equs_text += "\n %s" % rhs_rendered

  return d_vars, d_equs, d_vars_text, d_equs_text


def reduceVars(inv_incidence_dictionary, variables, incidence_dictionary, d_vars, d_equs, var_ID):
  """
  used in equation editor, where variables are defined differently than in other editors TODO: consider change -- probably not feasible or worth trouble
  iterate to find all equations and variables to be deleted
  in most of the cases everything is deleted except state variables
    because equations are all dependent on each other.
  :param inv_incidence_dictionary: "inverse" incidence dictionary
  :param variables: variables (dictionary)
  :param incidence_dictionary: incidence dictionary (var, incidence list)
  :param d_vars: set of variables to be deleted - list of IDs (integers)
  :param d_equs: set of equations to be deleted - list of IDs (integers)
  :param var_ID: variable ID (integer)
  :return: None
  """
  var = variables[var_ID]
  if var.type != "state":  # RULE: Cannot delete state variables
    d_vars.add(var_ID)
  for eq_id in inv_incidence_dictionary[var_ID]:
    if eq_id not in d_equs:
      d_equs.add(eq_id)
      if var.type == "state":
        return  # Way out
      else:
        lhs, incidence_list = incidence_dictionary[eq_id]
        reduceVars(inv_incidence_dictionary, variables, incidence_dictionary, d_vars, d_equs, lhs)


################################################

def findDependentVariables(variables, var_ID, indices):
  """
  simulate deletion in order to provide feedback to the user
  :param variables: variable (dictionary)
  :param var_ID: variable ID (integer)
  :return:
  """
  found_vars = set()
  found_equs = set()

  # - key: equation_ID(integer)
  # - value: (lhs - variable_ID, rhs - incidence list (integers) )

  incidence_dictionary, inv_incidence_dictionary = makeIncidenceDictionaries(variables)
  iterateBipartiteGraph(inv_incidence_dictionary, variables, incidence_dictionary, found_vars, found_equs, var_ID)
  found_vars_text = ""
  found_equs_text = ""
  for var_ID in found_vars:
    try:
      label = variables[var_ID]["label"]
    except:
      label = variables[var_ID].label
    found_vars_text += "\n %s" % label
  for eq_ID in found_equs:
    lhs, incidence_list = incidence_dictionary[eq_ID]
    try:
      equation = variables[lhs]["equations"][eq_ID]
    except:
      equation = variables[lhs].equations[eq_ID]
    rhs = equation["rhs"]["global_ID"]
    expression_network = equation["network"]
    rhs_rendered = renderExpressionFromGlobalIDToInternal(rhs,
                                                          variables=variables,
                                                          indices=indices,
                                                          expression_network=expression_network)
    # print("debugging -- rhs", rhs, rhs_rendered)
    found_equs_text += "\n %s" % rhs_rendered

  return found_vars, found_equs, found_vars_text, found_equs_text


def iterateBipartiteGraph(inv_incidence_dictionary, variables, incidence_dictionary, d_vars, d_equs, var_ID):
  """
  used in anywhere else than in the equation editor, where the variables are defined differently than in the other editors
  TODO: consider change -- probably not feasible or worth the trouble
  iterate to find all equations and variables to be deleted
  in most of the cases everything is deleted except the state variables
    because the equations are all dependent on each other.
  :param inv_incidence_dictionary:  "inverse" incidence dictionary
  :param variables: variables (dictionary)
  :param incidence_dictionary: incidence dictionary (var, incidence list)
  :param d_vars: set of variables to be deleted - list of IDs (integers)
  :param d_equs: set of equations to be deleted - list of IDs (integers)
  :param var_ID: variable ID (integer)
  :return: None
  """
  # var = variables[var_ID]
  d_vars.add(var_ID)

  for eq_id in inv_incidence_dictionary[var_ID]:
    if eq_id not in d_equs:
      d_equs.add(eq_id)
      lhs, incidence_list = incidence_dictionary[eq_id]
      iterateBipartiteGraph(inv_incidence_dictionary, variables, incidence_dictionary, d_vars, d_equs, lhs)


#################################################

def makeCompiler(variables, indices, var_ID, equ_ID, language, verbose=0):
  """
  setup a compiler
  :param variables: variable dictionary
  :param indices:  incidence dictionary
  :param var_ID: variable ID (integer)
  :param equ_ID: equation ID (integer)
  :param language: language (string)
  :return: expression -- compiler
  """
  variable_definition_network = variables[var_ID].network
  expression_definition_network = variables[var_ID].equations[equ_ID]["network"]
  return makeCompilerForNetwork(variables,
                                indices,
                                variable_definition_network,
                                expression_definition_network,
                                language,
                                verbose)


def makeCompilerForNetwork(variables,
                           indices,
                           variable_definition_network,
                           expression_definition_network,
                           language,
                           verbose=0):
  compile_space = CompileSpace(variables,
                               indices,
                               variable_definition_network,
                               expression_definition_network,
                               language=language)
  return Expression(compile_space, verbose=verbose)


# =============================================================================
# error classes
# =============================================================================


class VarError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return ">>> %s" % self.msg


class TrackingError(VarError):
  def __init__(self, msg):
    self.msg = msg


class UnitError(VarError):
  """
  variable error with unit exception
  """

  def __init__(self, msg, pre, post):
    self.msg = msg + "\n -- pre: %s,\n -- post: %s" % (pre, post)


class IndexStructureError(VarError):
  """
  variable error with unit exception
  """

  def __init__(self, msg):
    self.msg = msg


class MatrixCompilationError(VarError):
  """
  variable error with unit exception
  """

  def __init__(self, msg):
    self.msg = msg


class EquationDeleteError(VarError):
  """
  variable error with unit exception
  """

  def __init__(self, msg):
    self.msg = msg


# =============================================================================
# Components of the variable/equation space
# =============================================================================

class Units():
  """
  Defines a container for the SI units
  TODO:could be generated from the ont ology
  """

  def __init__(self, time=0, length=0, amount=0, mass=0,
               temperature=0, current=0, light=0, nil=0, ALL=[]):
    """
    SI - unit container. There are two ways of using it:
      1. define all individual units separately using the keywords
      2. define a vector of all 8 units and pass it through the keyword ALL
    :param time: exponent for time
    :param length: exponent for length
    :param amount: exponent for amount
    :param mass: exponent for mass
    :param temperature: exponent for temperature
    :param current: exponent for current
    :param light: exponent for light
    :param nil:nil         TODO: can be eliminated - probably
    :param ALL: list of the eight exponents
    """
    if ALL == []:
      self.time = time
      self.length = length
      self.amount = amount
      self.mass = mass
      self.temperature = temperature
      self.current = current
      self.light = light
      self.nil = nil
    else:
      self.time = ALL[0]
      self.length = ALL[1]
      self.amount = ALL[2]
      self.mass = ALL[3]
      self.temperature = ALL[4]
      self.current = ALL[5]
      self.light = ALL[6]
      self.nil = ALL[7]

  def isZero(self):
    iszero = True
    d = [self.time, self.length, self.amount, self.mass, self.current,
         self.light]
    for i in d:
      if i != 0:
        iszero = False
    return iszero

  def __add__(self, other):
    """
    Checks if the two unit sets are the same. If not it raises an UnitError
    :param other: the other
    """
    if self.__dict__ == other.__dict__:
      return copy.copy(self)
    else:
      raise UnitError("add - incompatible units", self.prettyPrint(mode="string"), other.prettyPrint(mode="string"))

  def __mul__(self, other):
    u = [sum(unit) for unit in zip(Units.asList(self), Units.asList(other))]
    return Units(*u)

  def __eq__(self, other):
    return self.asList() == other.asList()

  def product(self, factor):
    u_list = self.asList()
    u = [i * factor for i in u_list]
    units = Units(ALL=u)
    # units.time = factor * int(self.time)
    # units.lenth = factor * int(self.length)
    # units.amount = factor * int(self.amount)
    # units.mass = factor * self.mass
    # units.temperature = factor * self.temperature
    # units.current = factor * self.current
    # units.light = factor * self.light
    # units.nil = copy.copy(self.nil)

    return units

  def asDictionary(self):
    return self.__dict__

  def prettyPrint(self, mode="latex"):
    pri = ''
    if self.mass != 0:
      if self.mass == 1:
        pri += r"kg \,"
      else:
        pri += r"kg^{%s} \," % self.mass
    if self.length != 0:
      if self.length == 1:
        pri += r"m "
      else:
        pri += r"m^{%s} \," % self.length
    if self.amount != 0:
      if self.amount == 1:
        pri += r"mol \,"
      else:
        pri += r"mol^{%s} \," % self.amount
    if self.temperature != 0:
      if self.temperature == 1:
        pri += r"K \,"
      else:
        pri += r"K^{%s} \," % self.temperature
    if self.current != 0:
      if self.current == 1:
        pri += r"A \,"
      else:
        pri += "A^{%s} " % self.current
    if self.light != 0:
      if self.light == 1:
        pri += r"cd \,"
      else:
        pri += r"cd^{%s} \," % self.light
    if self.time != 0:
      if self.time == 1:
        pri += r"s \,"
      else:
        pri += r"s^{%s} \," % self.time

    p_units = ""
    if mode == "string":
      for s in pri:
        if (s == "\\") or (s == ","):
          pass
        else:
          p_units += s
    else:
      p_units = pri
    return p_units

  def prettyPrintUIString(self):
    _s = self.prettyPrint()
    return _s.replace(r"\,", " ")

  def asList(self):
    r = [self.time, self.length, self.amount,
         self.mass, self.temperature, self.current, self.light, self.nil]
    return r

  def __str__(self):
    return str(self.asList())



class Variables(OrderedDict):
  """
  container for variables
  They are imported from a file by the ontology container.
  New variables are defined by the equation editor.
  RULE: variables can be used in the domain tree from the location they are defined downwards.
  RULE: variable labels/names/symbols are only unique from the location they are defined downwards
  Constraint: the container has data and properties
  Data are extracted using the function extractVariables using a filter for the attributes
  """

  def __init__(self, ontology_container):
    super()
    self.ontology_container = ontology_container
    self.networks = ontology_container.networks
    self.ontology_hierarchy = ontology_container.ontology_hierarchy
    self.intraconnection_networks = list(ontology_container.intraconnection_network_dictionary.keys())
    self.interconnection_networks = ontology_container.list_inter_branches_pairs  # list(ontology_container
    # .interconnection_network_dictionary.keys())
    self.heirs_network_dictionary = ontology_container.heirs_network_dictionary
    self.ProMoIRI = self.ontology_container.ProMoIRI
    # self.global_name_space = self.ontology_container.rules["name_space"]


  def resetProMoIRI(self):
    """
    reset what-defined ProMoIRI, which is a simple enumeration variable
    :return:
    """
    self.ProMoIRI = {
            "variable": 0,
            "equation": 0
            }
    return self.ProMoIRI

  def newProMoVariableIRI(self):
    self.ProMoIRI["variable"] += 1
    s = ID_prefix["variable"] + str(self.ProMoIRI["variable"])
    return s

  def newProMoEquationIRI(self):
    self.ProMoIRI["equation"] += 1
    s = ID_prefix["equation"] + str(self.ProMoIRI["equation"])
    return s

  # def addNewVariable(self, ID=globalVariableID(update=True), **kwargs, ):
  def addNewVariable(self, ID=None, **kwargs, ):
    """
    adds a new variable as a PhysicalVariable
    :param ID: being assigned as a global ID by default
    :param kwargs: on instantiation defined in VariableRecord
    :return: ID
    """
    if ID:
      self[ID] = PhysicalVariable(**kwargs)  # NOTE: no check on existence done -- must happen on defining
      self[ID].indices = self.ontology_container.indices  # variable does not know the indices dictionary on definition.
      self.ontology_container.addVariable(ID, **kwargs)
    else:
      raise VarError("no variable ID defined")
    return ID

  def importVariables(self, variables, indices):
    """
    In contrast to addNewVariable, this imports "existing" variables that were stored on a variable file.
    :param variables: From standard json file as read by the ontology container
    :param indices: From standard json file as read by the ontology container
    :return: None
    Note adding the all indices to all variables is not nice. Think about an alternative.
    """

    for ID in variables:
      variables[ID]["indices"] = indices  # todo: alternative?
      self[ID] = PhysicalVariable(**variables[ID])

    self.indexVariables()

  def indexVariables(self):
    """
    indexing
    dict index_definition_networks_for_variable ::
        key: network
        value: variable ID
    dict index_definition_network_for_variable_component_class ::
        key: network
        value: dict
              key: variable class
              value: variable ID
    dict index_networks_for_variable ::
        key: network
        value: dict
                key: variable class
                value: list of variable IDs
    dict index_accessible_variables_on_networks ::  RULE: defines namespaces
        key: network
        value: dict
                key: variable class
                value: list of variable IDs
    dict incidence_dictionary ::
            - key: equation_ID (integer)
            - value: (lhs-variable_ID, rhs-incidence list (integers) )
    dict inv_incidence_dictionary :: inverse incidence matrix as dictionary
            - key : variable ID (integer)
            - value: list of equations (integer)
    list equation_types

    :return:
    """
    self.index_definition_networks_for_variable = {}
    self.index_definition_network_for_variable_component_class = {}
    # self.index_equation_in_definition_network = {}
    self.index_networks_for_variable = {}
    self.index_accessible_variables_on_networks = {}  # defines accessible name space

    # for nw in self.networks + self.interconnection_networks + self.intraconnection_networks:
    all_networks = self.networks + self.ontology_container.list_inter_branches_pairs + self.intraconnection_networks
    
    # Check if any loaded variables are in the interface domain
    has_interface_variables = any(self[ID].network == "interface" for ID in self)
    
    # Add interface domain if it exists or if we have interface variables
    if (hasattr(self, 'interface_domain') and self.interface_domain) or has_interface_variables:
        if not hasattr(self, 'interface_domain') or not self.interface_domain:
            self.interface_domain = "interface"
        if self.interface_domain not in all_networks:
            all_networks.append(self.interface_domain)
    
    for nw in all_networks:
      self.index_definition_networks_for_variable[nw] = []

    for ID in self:
      self.index_definition_networks_for_variable[self[ID].network].append(ID)

    # make index for variables on the networks it was defined
    for nw in all_networks:
      self.index_networks_for_variable[nw] = {}

    for nw in all_networks:
      # Ensure variable types exist for this network
      if nw not in self.ontology_container.variable_types_on_networks:
        self.ontology_container.variable_types_on_networks[nw] = {}
        
      for variable_class in self.ontology_container.variable_types_on_networks[nw]:
        if variable_class not in self.index_networks_for_variable[nw]:
          self.index_networks_for_variable[nw][variable_class] = []
        for ID in self:
          if (self[ID].type == variable_class) and (self[ID].network == nw):
            for i_nw in self.ontology_container.heirs_network_dictionary[nw]:
              if variable_class not in self.index_networks_for_variable[i_nw]:
                self.index_networks_for_variable[i_nw][variable_class] = []
              self.index_networks_for_variable[i_nw][variable_class].append(ID)

    for nw in self.interconnection_networks:
      left_nw, right_nw = nw.split(CONNECTION_NETWORK_SEPARATOR)
      self.index_networks_for_variable[nw] = {}
      for variable_class in self.ontology_container.variable_types_on_interfaces[nw]:
        if variable_class not in self.index_networks_for_variable[nw]:
          self.index_networks_for_variable[nw][variable_class] = []
        for ID in self:
          if (self[ID].type == variable_class) and (self[ID].network == nw):
            self.index_networks_for_variable[nw][variable_class].append(ID)

    for nw in self.intraconnection_networks:
      self.index_networks_for_variable[nw] = {}
      for variable_class in self.ontology_container.variable_types_on_intrafaces[nw]:
        if variable_class not in self.index_networks_for_variable[nw]:
          self.index_networks_for_variable[nw][variable_class] = []
        for ID in self:
          if (self[ID].type == variable_class) and (self[ID].network == nw):
            self.index_networks_for_variable[nw][variable_class].append(ID)

    # make index for variables
    for nw in self.networks:
      ontology_behaviour = self.ontology_container.ontology_tree[nw]["behaviour"]
      self.index_definition_network_for_variable_component_class[nw] = {}
      for comp in ontology_behaviour:  # comp is in [arc, graph, node)
        for t in ontology_behaviour[comp]:  # t is variable type / class
          if t not in self.index_definition_network_for_variable_component_class[nw]:
            self.index_definition_network_for_variable_component_class[nw][t] = set()
          for ID in self:
            if (self[ID].network == nw) and (self[ID].type == t):
              self.index_definition_network_for_variable_component_class[nw][t].add(ID)

    for nw in self.interconnection_networks:
      self.index_definition_network_for_variable_component_class[nw] = {}
      for ID in self:
        if self[ID].network == nw:
          t = self[ID].type
          if t not in self.index_definition_network_for_variable_component_class[nw]:
            self.index_definition_network_for_variable_component_class[nw][t] = set()
          self.index_definition_network_for_variable_component_class[nw][t].add(ID)

    for nw in self.intraconnection_networks:
      self.index_definition_network_for_variable_component_class[nw] = {}
      for ID in self:
        if self[ID].network == nw:
          t = self[ID].type
          if t not in self.index_definition_network_for_variable_component_class[nw]:
            self.index_definition_network_for_variable_component_class[nw][t] = set()
          self.index_definition_network_for_variable_component_class[nw][t].add(ID)

    # Handle interface domain if it exists
    if hasattr(self, 'interface_domain') and self.interface_domain:
      self.index_definition_network_for_variable_component_class[self.interface_domain] = {}
      self.index_networks_for_variable[self.interface_domain] = {}  # Add this line
      for ID in self:
        if self[ID].network == self.interface_domain:
          t = self[ID].type
          if t not in self.index_definition_network_for_variable_component_class[self.interface_domain]:
            self.index_definition_network_for_variable_component_class[self.interface_domain][t] = set()
          self.index_definition_network_for_variable_component_class[self.interface_domain][t].add(ID)
          
          # Also add to index_networks_for_variable
          if t not in self.index_networks_for_variable[self.interface_domain]:
            self.index_networks_for_variable[self.interface_domain][t] = []
          self.index_networks_for_variable[self.interface_domain][t].append(ID)


    # incidence and inverse incidence lists
    self.incidence_dictionary, self.inv_incidence_dictionary = makeIncidenceDictionaries(self)

    equation_type_set = set()
    for equ_ID in self.incidence_dictionary:
      lhs, incidence_list = self.incidence_dictionary[equ_ID]
      equation_type_set.add(self[lhs].equations[equ_ID]["type"])
    self.equation_type_list = list(equation_type_set)

    # make for each variable the namespaces
    # Note is used for the definition of a variable in equation version with interface variables that decouple the domains
    self.nameSpacesForVariableLabel = {}
    # Note is used for the definition of a variable in equation with the version without interface -- makes the names global
    self.nameSpacesForVariableLabelGlobal = []
    for ID in self:
      label = self[ID].label
      if label not in self.nameSpacesForVariableLabel:
        self.nameSpacesForVariableLabel[label] = {}
        no = 0
        self.nameSpacesForVariableLabel[label][no] = []
      else:
        no = len(self.nameSpacesForVariableLabel[label].keys())
      definition_network = self[ID].network
      if CONNECTION_NETWORK_SEPARATOR in definition_network:  # Rule: No inheritance for interfaces
        if no not in self.nameSpacesForVariableLabel[label]:
          self.nameSpacesForVariableLabel[label][no] = []
        self.nameSpacesForVariableLabel[label][no].append(definition_network)
      elif definition_network == "interface":  # Special handling for interface domain
        if no not in self.nameSpacesForVariableLabel[label]:
          self.nameSpacesForVariableLabel[label][no] = []
        self.nameSpacesForVariableLabel[label][no].append(definition_network)
        # Interface domain has no heirs, so just add itself
        self.nameSpacesForVariableLabel[label][no + 1] = [definition_network]
      else:
        space = self.heirs_network_dictionary[definition_network]
        self.nameSpacesForVariableLabel[label][no + 1] = copy.copy(space)
      # if self.global_name_space:
      #   if label in self.nameSpacesForVariableLabelGlobal:
      #     raise VarError(" label already exists")
      #   else:
      #   self.nameSpacesForVariableLabelGlobal.append(label)

    acc = {}
    for nw in self.networks:
      acc[nw] = {}
      for variable_class in self.ontology_container.variable_types_on_networks[nw]:
        if variable_class not in acc[nw]:
          acc[nw][variable_class] = []
        for ID in self:
          if self[ID].type == variable_class:
            ID_nw = self[ID].network
            if ID_nw in self.ontology_hierarchy[nw]:  # it blows here
              acc[nw][variable_class].append(ID)

    # RULE: alternatives -- interconnections have variables version 8 and older or no interconnection variables direct access to the "other side"
    # inter_connections = False
    # if inter_connections :

    # if not self.global_name_space:
    for nw in self.interconnection_networks:
      acc[nw] = {}
      for variable_class in self.ontology_container.variable_types_on_interfaces[nw]:
        if variable_class not in acc[nw]:
          acc[nw][variable_class] = []
        for ID in self:
          if self[ID].type == variable_class:
            if self[ID].network == nw:
              acc[nw][variable_class].append(ID)
      [source, sink] = nw.split(CONNECTION_NETWORK_SEPARATOR)
      for variable_class in acc[source]:
        if variable_class not in acc[nw]:
          acc[nw][variable_class] = []
        acc[nw][variable_class].extend(acc[source][variable_class])

    for nw in self.ontology_container.interface_networks_accessible_to_networks_dictionary:
      for i_nw in self.ontology_container.interface_networks_accessible_to_networks_dictionary[nw]:
        for ID in self:
          # print("network -- ", self[ID].network)
          if self[ID].network == i_nw:
            for variable_class in self.ontology_container.variable_types_on_interfaces[i_nw]:
              # print("debugg variable class", variable_class)
              if variable_class not in acc[nw]:
                acc[nw][variable_class] = []
              acc[nw][variable_class].append(ID)

    for nw in acc:
      for variable_class in acc[nw]:
        acc[nw][variable_class] = list(set(acc[nw][variable_class]))
    self.index_accessible_variables_on_networks = acc

    return

  def indexInstantiated(self, network):
    all_variables_in_network = set()
    for ID in self:
      if self[ID].network == network:
        all_variables_in_network.add(ID)
    variables_being_instantiate = set()
    a = CODE["global_ID"]["operator"]["Instantiate"]
    for var_ID in self:
      for eq_ID in self[var_ID].equations:
        if self[var_ID].equations[eq_ID]["network"] == network:
          if a in self[var_ID].equations[eq_ID]["rhs"]:
            # print("debugging ", var_ID, eq_ID)
            variables_being_instantiate.add(var_ID)
    variables_not_instantiated = sorted(all_variables_in_network - variables_being_instantiate)
    return variables_not_instantiated

  def variableSpaces(self, what, network, enabled_variable_types):
    """
    THE single definition of variable space access rules
    Used by both UI picking and expression validation
    """
    v_counter = 0
    
    if what == "variable_picking":
      # Get accessible networks including interface domain
      # accessible_networks = list(self.ontology_container.heirs_network_dictionary[network])
      # inter_branches = self.ontology_container.interface_networks_accessible_to_networks_dictionary[network]

      # from the hierarchy
      if network in self.ontology_container.ontology_hierarchy:
        accessible_networks = self.ontology_container.ontology_hierarchy[network]
      else:
        # If network is not in hierarchy (e.g., 'interface'), use only the network itself
        accessible_networks = [network]
      
      inter_branches = self.ontology_container.list_inter_branches
      accessible_networks.extend(inter_branches)
      accessible_networks = list(set(accessible_networks))

      # print(f"DEBUG: Network {network} has heirs: {accessible_networks}")
      
      # Add interface domain if it exists and has variables
      # if hasattr(self, 'interface_domain') and self.interface_domain:
      #   accessible_networks.append(self.interface_domain)
      
      variable_space = {}
      v_space = {}
      v_space[network] = {}
      for nw in accessible_networks:
        for var_class in self.index_networks_for_variable[nw]:
          v_space[network][var_class] = []
      #
      # variables = self.ontology_container.variables
      # for var_id in self.ontology_container.variables:
      #   if variables[var_id]["network"]  in accessible_networks:
      #     variable_space.add(var_id)
      #     v_counter += 1
      
      # Build variable space for each accessible network
      for nw in accessible_networks:
        if nw in self.index_networks_for_variable:
          variable_space[nw] = {}
          for var_class in self.index_networks_for_variable[nw]:
            variable_space[nw][var_class] = set()

            # Filter by enabled_variable_types if provided
            for v in self.index_networks_for_variable[nw][var_class]:
              # if not enabled_variable_types or self[v].type in enabled_variable_types:
                variable_space[nw][var_class].add(v)
                if v not in v_space[network][var_class]:
                  v_space[network][var_class].append(v)
                v_counter += 1


      # Also include variables from heir networks that are accessible to current network
      # This handles cross-domain access (e.g., control accessing physical/macroscopic variables)
      # for heir_network in accessible_networks:
      #   if heir_network != network and heir_network in self.index_networks_for_variable:
      #     if heir_network not in variable_space:  # Don't overwrite existing
      #       variable_space[heir_network] = {}
      #       for var_class in self.index_networks_for_variable[heir_network]:
      #         variable_space[heir_network][var_class] = set()
      #
      #         # Filter by enabled_variable_types if provided
      #         for v in self.index_networks_for_variable[heir_network][var_class]:
      #           if not enabled_variable_types or self[v].type in enabled_variable_types:
      #             variable_space[heir_network][var_class].add(v)
      #             v_counter += 1
      variable_space = v_space

    elif what == "interface_picking":
      rule = "only local"
      networks = [network] # self.ontology_container.heirs_network_dictionary[network]
      variable_space = {}
      for nw in networks: #self.index_definition_network_for_variable_component_class:
        variable_space[nw] = {}
        for c in self.index_definition_network_for_variable_component_class[nw]:
          variable_space[nw][c] = set()
          for v in self.index_definition_network_for_variable_component_class[nw][c]:
            for i in enabled_variable_types:
              if self[v].type == i:
                variable_space[nw][c].add(v)
                v_counter += 1

    elif what == "variable_display":
      # NEW MODE: Show all variables accessible in the selected domain
      # This is simpler than variable_picking - no complex filtering
      
      # Get accessible networks from hierarchy
      if network in self.ontology_container.ontology_hierarchy:
        accessible_networks = self.ontology_container.ontology_hierarchy[network]
      else:
        # If network is not in hierarchy (e.g., 'interface'), use only the network itself
        accessible_networks = [network]
      
      # Add inter-branch networks for cross-domain access
      inter_branches = self.ontology_container.list_inter_branches
      accessible_networks.extend(inter_branches)
      accessible_networks = list(set(accessible_networks))
      
      variable_space = {}
      v_counter = 0
      
      # Build variable space for each accessible network
      for nw in accessible_networks:
        if nw in self.index_networks_for_variable:
          variable_space[nw] = {}
          for var_class in self.index_networks_for_variable[nw]:
            variable_space[nw][var_class] = set()
            
            # Include ALL variables (no filtering for display mode)
            for v in self.index_networks_for_variable[nw][var_class]:
              variable_space[nw][var_class].add(v)
              v_counter += 1
      
      # Add interface domain variables if they exist
      if hasattr(self, 'interface_domain') and self.interface_domain:
        if self.interface_domain in self.index_networks_for_variable:
          variable_space[self.interface_domain] = {}
          for var_class in self.index_networks_for_variable[self.interface_domain]:
            variable_space[self.interface_domain][var_class] = set()
            for v in self.index_networks_for_variable[self.interface_domain][var_class]:
              variable_space[self.interface_domain][var_class].add(v)
              v_counter += 1

    else:
      variable_space = self.index_networks_for_variable

    return variable_space, v_counter

  def getOrCreateInterfaceDomain(self):
    """
    Get or create interface domain for cross-domain variable access
    """
    if not hasattr(self, 'interface_domain'):
      self.interface_domain = "interface"
      
      # Ensure interface domain exists in ontology structure
      if self.interface_domain not in self.ontology_container.variable_types_on_networks:
        self.ontology_container.variable_types_on_networks[self.interface_domain] = {}
      
      # Ensure interface domain is in hierarchy
      if self.interface_domain not in self.ontology_container.heirs_network_dictionary:
        self.ontology_container.heirs_network_dictionary[self.interface_domain] = [self.interface_domain]
      
      # Add interface domain to variable types with common interface types
      # Interface variables can be of any type that source variables could be
      common_interface_types = ["state", "algebraic", "observation", "secondaryState", "effort"]
      self.ontology_container.variable_types_on_networks[self.interface_domain] = common_interface_types
    
    return self.interface_domain

  def createInterfaceVariable(self, source_domain, source_var_ID, target_network):
    """
    Create an interface variable in the interface domain
    Prevents duplication of interface variables
    """
    interface_domain = self.getOrCreateInterfaceDomain()
    source_var = self[source_var_ID]
    
    # Generate interface variable name: domain_varname
    interface_var_name = f"{source_domain}_{source_var.label}"
    
    # Check if interface variable already exists
    for var_ID in self:
      var = self[var_ID]
      if var.label == interface_var_name and var.network == interface_domain:
        # Interface variable already exists, return existing ID
        return var_ID
    
    # Create new interface variable
    interface_var_ID = self.newProMoVariableIRI()
    
    # Create interface equation using proper record structure
    interface_equ_ID = self.newProMoEquationIRI()
    
    # Create RHS dictionary in proper format with both global_ID and latex
    rhs_global_ID = source_var_ID
    source_latex = source_var.aliases.get("latex", source_var.label)
    decorated_latex = f"\\multimap{{{source_latex}}}"
    rhs_dic = {"global_ID": rhs_global_ID, "latex": decorated_latex}
    
    # Create incidence list for the interface equation
    incidence_list = makeIncidentList(rhs_global_ID)
    
    # Create proper equation record using makeCompletEquationRecord
    interface_equation_record = makeCompletEquationRecord(
        rhs=rhs_dic, 
        network=interface_domain, 
        doc=f"Interface equation linking {interface_var_name} to {source_domain}.{source_var.label}",
        incidence_list=incidence_list, 
        created=dateString()
    )
    
    # Create variable record using makeCompleteVariableRecord with equation included
    # Add LaTeX decoration for interface variables
    interface_aliases = source_var.aliases.copy()
    source_latex = source_var.aliases.get("latex", source_var.label)
    decorated_latex = f"\\multimap{{{source_latex}}}"
    interface_aliases["latex"] = decorated_latex

    from Common.common_resources import VARIABLE_TYPE_INTERFACE
    variable_record = makeCompleteVariableRecord(
        var_ID=interface_var_ID,
        label=interface_var_name,
        type=VARIABLE_TYPE_INTERFACE, #source_var.type,
        network=interface_domain,
        doc=f"Interface variable for {source_domain}.{source_var.label}",
        index_structures=source_var.index_structures,
        units=source_var.units,
        equations={interface_equ_ID: interface_equation_record},
        aliases=interface_aliases,
        port_variable=False,
        tokens=[],
        memory=getattr(source_var, 'memory', None)
    )
    
    # Add interface variable using the standard addNewVariable method
    self.addNewVariable(ID=interface_var_ID, **variable_record)
    
    # Add interface equation to ontology container for compiler access
    self.ontology_container.equation_dictionary[interface_equ_ID] = interface_equation_record
    
    # Initialize compiled_lhs for interface variables (needed for LaTeX generation)
    if "compiled_lhs" not in self.ontology_container.variables[interface_var_ID]:
        self.ontology_container.variables[interface_var_ID]["compiled_lhs"] = {}
    
    # Re-index variables to include new interface variable
    self.indexVariables()
    
    print(f"Created interface variable: {interface_var_name} = {source_var.label} (from {source_domain})")
    
    return interface_var_ID

  def changeVariableAlias(self, variable_ID, language, new_alias):
    old_alias =     self[variable_ID].aliases[language]
    if new_alias != old_alias:
      self[variable_ID].aliases[language] = new_alias
      # if language == "latex":
      #   self[variable_ID].compiled_lhs["latex"] = new_alias
      date = dateString()
      self.ontology_container.variables[variable_ID]["modified"] = dateString()  # NOTE: that was the problem
      self[variable_ID].modified = date
      print("changed variable", variable_ID, self[variable_ID].modified)

  def removeVariable(self, variable_ID):
    """
    removes the variable with variable_ID
    :param variable_ID:
    :return: None
    """
    # print("debugging -- remove variable ", variable_ID, self[variable_ID].label)
    del self[variable_ID]
    del self.ontology_container.variables[variable_ID]
    # self.changes["variables"].remove(variable_ID)
    self.indexVariables()

  def removeEquation(self, equation_ID):
    """
    In this case one does not know which variable it defines, so one must search first

    :param equation_ID:
    :return: None
    """
    for v in self:
      equations = self[v].equations
      if equation_ID in equations:
        del equations[equation_ID]
        # print("debugging -- remove equation ", equation_ID, "  in variable ", v, self[v].label)

    self.indexVariables()  # indexEquationsInNetworks()

  def addEquation(self, var_ID, equation_record):
    equ_ID = self.newProMoEquationIRI()  # globalEquationID(update=True)  # RULE: for global ID
    self[var_ID].equations[equ_ID] = equation_record
    self.indexVariables()
    self.ontology_container.indexEquations()
    print("debugging")

  def replaceEquation(self, var_ID, old_equ_ID, equation_record):
    variable_record = self[var_ID]
    old_equation_record = variable_record.equations[old_equ_ID]
    creation = old_equation_record["created"]
    equation_record["created"] = creation
    variable_record.equations[old_equ_ID] = equation_record
    # print("debugging -- replace equation")

  def existSymbol(self, network, label):
    """
    checks if a particular symbol (label) exists in the name space defined for the network
    :param network:
    :param label:
    :return: logical
    """
    if label not in self.nameSpacesForVariableLabel:
      return False

    for name_space in self.nameSpacesForVariableLabel[label]:
      if network in self.nameSpacesForVariableLabel[label][name_space]:
        return True
      else:
        for nw in self.nameSpacesForVariableLabel[label][name_space]:
          if CONNECTION_NETWORK_SEPARATOR in nw:
            _, rnw = nw.split(CONNECTION_NETWORK_SEPARATOR)
            if rnw == network:
              return True

    return False

  def existSymbolGlobal(self, label):
    log = label in self.nameSpacesForVariableLabelGlobal
    return log

  def getVariableList(self, network):
    """
    provides the list of variables as IDs in a given network
    :param network:
    :return:
    """
    acc = []
    for ID in self:
      def_nw = self[ID].network
      if def_nw in self.ontology_hierarchy[network]:
        acc.append(ID)
    return acc

  def getVariablesForTypeAndNetwork(self, vartype, network):
    """
    RULE: all variables that are available in this network are returned in the form of IDs
    :param vartype: variable type/class defined in the ontology
    :param nw: current network
    :return: IDs for the variables that are available in this network of type/class <vartype>
    """
    acc = []
    if CONNECTION_NETWORK_SEPARATOR in network:
      for ID in self:
        if self[ID].type == vartype:
          if network == self[ID].network:
            acc.append(ID)
      return acc
    # else
    for ID in self:
      if self[ID].type == vartype:
        def_nw = self[ID].network
        if def_nw in self.ontology_hierarchy[network]:  # it blows here
          acc.append(ID)
    return acc

  def extractVariables(self, filter):
    """
    The variable class holds also information about the structure of the data
    This method extracts the variable data as an ordred dictionary
    :return: ordered dictionary un-filtered variable data
    """

    data = {}
    for i in sorted(self):
      if ID_prefix["variable"] in i:
        data[i] = {}
        for a in dir(self[i]):
          if a in filter:
            value = eval("self[i].%s" % a)
            if a not in ["units", "port_variable"]:
              data[i][a] = value
            else:
              data[i][a] = eval(str(value))
          # if a in filter:
          #   for j in self[i].__dict__[a]:
          #     # data[i][a] = str(self[i].__dict__[a])
          #     data[i][a] = self[i].j

    return data


class CompileSpace:
  """
  Used for compilation
  - Transfers language across to the variables and access to the variables
  - Constructs an incidence list for the compiled expression
  - Constructs names for the temporary variables
  """
  counter = 0

  def __init__(self, variables, indices, variable_definition_network, expression_definition_network, language=internal):
    '''
    Access to variables and language definition
    alternative one : define var_equations defines the variable identifier and the equation identifier as a tuple
                      in this case the namespace
    alternative two : compile an expression
    @param variables: variable ordered dictionary (access by symbol)
    @param indices: all indices as a dictionary
    @var_equation: a
    @param language: target language string
    '''

    self.language = language  # sets the target language
    self.variables = variables
    self.indices = indices
    # self.eq_variable_incidence_list = []

    self.inverse_indices = {}
    self.base_indices = []
    self.block_indices = []

    for ind_ID in self.indices:
      label = self.indices[ind_ID]["label"]
      internal_code = self.indices[ind_ID]["aliases"]["internal_code"]
      self.inverse_indices[label] = ind_ID
      self.inverse_indices[internal_code] = ind_ID
      if self.indices[ind_ID]["type"] == "index":
        self.base_indices.append(ind_ID)
      elif self.indices[ind_ID]["type"] == "block_index":
        self.block_indices.append(ind_ID)
      else:
        raise VarError("fatal error -- not a propert index type %s" % ind_ID)

    # RULE: networks have access to the interfaces

    accessible_variable_space = []

    self.variable_definition_network = variable_definition_network
    self.expression_definition_network = expression_definition_network

  def getVariable(self, symbol, ):
    '''
    gets the variable "label" from the variable ordered dictionary and
    sets the appropriate language
    Uses unified variable space definition consistent with variableSpaces()
    @param symbol: variable's symbol
    @return: v : the variable object
    '''
    # print("get variable", symbol)

    # Use the same logic as variableSpaces for variable_picking
    variable_space, v_counter = self.variables.variableSpaces("variable_picking", self.expression_definition_network, None)
    
    # Manually add interface domain if it exists and has variables
    if hasattr(self.variables, 'interface_domain') and self.variables.interface_domain:
        if self.variables.interface_domain in self.variables.index_networks_for_variable:
            if self.variables.interface_domain not in variable_space:
                variable_space[self.variables.interface_domain] = {}
            for var_class in self.variables.index_networks_for_variable[self.variables.interface_domain]:
                if var_class not in variable_space[self.variables.interface_domain]:
                    variable_space[self.variables.interface_domain][var_class] = set()
                for var_ID in self.variables.index_networks_for_variable[self.variables.interface_domain][var_class]:
                    # Ensure we're working with a set
                    if not isinstance(variable_space[self.variables.interface_domain][var_class], set):
                        variable_space[self.variables.interface_domain][var_class] = set(variable_space[self.variables.interface_domain][var_class])
                    variable_space[self.variables.interface_domain][var_class].add(var_ID)
    
    v_list = set()
    
    # Search in all accessible networks from variable space
    for nw in variable_space:
      for var_class in variable_space[nw]:
        # Handle both sets and lists
        var_collection = variable_space[nw][var_class]
        if isinstance(var_collection, list):
          var_iterable = var_collection
        else:
          var_iterable = var_collection
          
        for var_ID in var_iterable:
          if symbol == self.variables[var_ID].label:
            v_list.add(var_ID)

    v_list = sorted(v_list)

    if len(v_list) == 0:
      # Check if this is an interface variable (format: domain_varname)
      if '_' in symbol:
        parts = symbol.split('_', 1)
        if len(parts) == 2:
          source_domain, source_label = parts
          
          # Try to find the original variable
          for var_ID in self.variables:
            var = self.variables[var_ID]
            if var.label == source_label and var.network == source_domain:
              # Return the variable ID for interface variables, not the variable object
              # This ensures the global_ID expression contains the proper variable ID
              interface_var_ID = var_ID
              v = self.variables[interface_var_ID]
              return v
      
      print("did not find %s in language %s" % (symbol, self.language))
      raise VarError(" no such variable %s defined" % symbol)
    elif len(v_list) == 1:
      v = self.variables[v_list[0]]
    elif len(v_list) > 1:
      # Prefer variables from current expression definition network
      for i in v_list:
        if self.variables[i].network == self.expression_definition_network:
          v = self.variables[i]
          break
      else:
        # If no current network match, prefer interface domain
        for i in v_list:
          if hasattr(self.variables, 'interface_domain') and \
             self.variables.interface_domain and \
             self.variables[i].network == self.variables.interface_domain:
            v = self.variables[i]
            break
        else:
          # Fallback to first match
          v = self.variables[v_list[0]]
    else:
      print("did not find %s in language %s" % (symbol, self.language))
      raise VarError(" no such variable %s defined" % symbol)

    try:
      v.language = self.language
    except:
      pass
    try:
      v.indices = self.indices
    except:
      pass
    return v

  def getIndex(self, symbol):
    for i in self.indices:
      if self.indices[i]["aliases"]["internal_code"] == symbol:
        return i
    return None


  def newTemp(self):
    '''
    defines the symbol for a new temporary variable
    @return: symbol for the temporary variable
    '''
    symbol = TEMPLATES["temp_variable"] % self.counter
    self.counter += 1
    return symbol


class PhysicalVariable():
  """
  Variables are  the base object in  the physical variable construct they have:
    - a symbol, an ID, which is unique within the global set of variables
    - a doc (string)
    - a list of uniquely named index structures
  """

  def __init__(self, **kwargs):
    # symbol= '', variable_type='',
    #            layer=None, doc='', index_structures=[], units=Units()):
    """

    @param symbol: an identifier for symbolic representation also serves as key
                   for  the variable dictionary thus this must be a unique name
                   in the set of variables.
    @param variable_type: variable type
    @param layer: ontology layer
    @param doc: a document string
    @param index_structures: list of index structures
    @param units: the units object
    @return:
    """
    # print(kwargs)
    self.__dict__ = kwargs

  def addEquation(self, equation_ID):
    self.equation_list.append(str(equation_ID))

  def removeEquation(self, equation_ID):
    print(self.port_variable)
    if self.port_variable:
      del self.equations[equation_ID]
    elif len(self.equations) == 1:
      # print("debugging - should not come here, this means one has to delete the variable")
      raise EquationDeleteError("cannot delete")
      pass
    else:
      del self.equations[equation_ID]

  def changeLabel(self, label):
    self.label = label
    prefix, namespace, old_label = IRI_parse(self.IRI)
    # self.IRI = IRI_make(prefix,namespace,label)
    self.IRI = IRI_make(prefix, label)

    for language in LANGUAGES["aliasing"]:
      if language != "global_ID":
        self.aliases[language] = label


  def shiftType(self, type):
    self.type = type
    # print("debugging -- shifting type")

  def setLanguage(self, language):
    self.language = language


  def __str__(self):

    if hasattr(self, 'language') and self.language in LANGUAGES["documentation"]:
      temp = "template_variable.%s" % self.language
      ind = []
      for ID in self.index_structures:
        ind.append(self.indices[ID]["aliases"][self.language])
      s = j2_env.get_template(temp).render(var=self.aliases[self.language], ind=ind)
    else:
      try:
        s = ID_spacer + self.aliases[self.language]
      except:
        # Fallback when language attribute is missing
        try:
          s = ID_spacer + self.label
        except:
          s = ID_spacer + "unknown_variable"

    return s


###############################################################################
#                                  OPERATORS                                  #
###############################################################################

class Operator(PhysicalVariable):
  def __init__(self, space, equation_type="generic"):
    PhysicalVariable.__init__(self)
    self.label = space.newTemp()
    self.space = space
    self.type = TEMP_VARIABLE
    self.equation_type = equation_type


class UnitOperator(Operator):
  def __init__(self, op, space):
    Operator.__init__(self, space)
    self.op = op

  def __str__(self):
    return self.asString()


class BinaryOperator(Operator):
  """
  Binary operator
  operator:
  + | - :: units must fit, index structures must fit

  @param op: string:: the operator
  @param a: variable:: left one
  @param b: variable:: right one
  """

  def __init__(self, op, a, b, space, reduceindex=None):
    Operator.__init__(self, space)
    self.op = op
    self.a = a
    self.b = b
    self.reduceindex = reduceindex
    self.space = space
    # self.indices = space.indices

    if reduceindex:
      self.index_ID = self.space.inverse_indices[self.reduceindex]
    else:
      self.index_ID = None


    try:
      _ = a.index_structures
    except:
      a.index_structures = []
      print("warning -- op1 has no index structure")
    try:
      _ = b.index_structures
    except:
      b.index_structures = []
      print("warning -- op2 has no index structure")
    self.s_index_a = set(a.index_structures)
    self.s_index_b = set(b.index_structures)
    self.pretty_a_indices = renderIndexListFromGlobalIDToInternal(self.s_index_a, space.indices)
    self.pretty_b_indices = renderIndexListFromGlobalIDToInternal(self.s_index_b, space.indices)


  def __str__(self):

    s = stringBinaryOperation(self.space.language, self.op, self.a, self.b, index_ID=self.index_ID, indices=self.space.indices)
    return s


class Add(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    Binary operator:
    + | - :: units must fit, index structures must fit

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    """

    BinaryOperator.__init__(self, op, a, b, space)

    self.units = a.units + b.units  # consistence check done in class

    if a.index_structures == b.index_structures:  # strictly the same
      self.index_structures = sorted(a.index_structures)

    else:
      print(" issue")
      print(self.space.indices.keys())
      pretty_a_indices = renderIndexListFromGlobalIDToInternal(a.index_structures, self.space.indices)
      pretty_b_indices = renderIndexListFromGlobalIDToInternal(b.index_structures, self.space.indices)
      raise IndexStructureError("add incompatible index structures %s"
                                % CODE[self.space.language][op] % (
                                        pretty_a_indices, pretty_b_indices))





class ReduceProduct(BinaryOperator):
  def __init__(self, op, a, b, space, reduceindex=None):
    """
    standard matrix product with the index defining which dimension is to be reduced.

    A_ij *i B_i = C_j: Normal reduce product of a matrix and a vector
    A_ij *i B_ik = C_jk: Normal reduce product of two matrices
    A_ijk *i B_il = C_jkl: Reduce product (not really just Einstein sum) for a 3D and a 2D
    A_ijk *i B_ik = C_jk: Page operation, so reducing only in one of the common indices not in both.
    """
    # print("this is the reduce product")



    BinaryOperator.__init__(self, op, a, b, space, reduceindex=reduceindex)

    self.units = a.units * b.units
    common_index_set = self.s_index_a & self.s_index_b
    l = len(common_index_set)

    index_ID = None
    if not reduceindex:

      # RULE: there must be only one and exaclty one common index
      # RULE: expansion is implied


      if l == 1:
        self.index_structures = sorted(self.s_index_a ^ self.s_index_b)
        index_ID = list(common_index_set)[0]

      else:
        if l > 1:
          msg = "ReduceProduct -- there are more than one common index -- not allowed"
        else:
          msg = "ReduceProduct -- there must be exactly one common index over which one reduces"

        msg += "\n first argument indices : %s" % self.pretty_a_indices
        msg += "\n second argument indices: %s" % self.pretty_b_indices
        print(msg)
        raise IndexStructureError(msg)

    else:
      if l == 1:
        self.index_structures = sorted(self.s_index_a ^ self.s_index_b)
        index_ID = list(common_index_set)[0]
      if l > 1:
        index_ID = self.space.inverse_indices[reduceindex]
        self.index_structures = sorted((self.s_index_a | self.s_index_b) - {index_ID})
      if l == 0:
        msg = " ReduceProduct -- there was no common index -- not allowed"
        print(msg)
        raise IndexStructureError(msg)


    self.reducedindex_ID =index_ID


def __str__(self):
    s = stringBinaryOperation(self.space.language, self.op,
                              self.a, self.b,
                              index_ID=self.reducedindex_ID,
                              indices=self.space.indices
                              )
    return s



class Hadamard(BinaryOperator):

  """
  A_ij . B_ij = C_ij: (No index so no reduce, so plain Hadamard)
  A_ij . B_i  = C_ij: (Same  just that B will be expanded to match A)
  A_ij . B_k = C_ijk: (Expand product, still no index so no reduce)
  A_ij * B_jk = C_ijk: (Similar to expand product but there is one
      common index, this is the operation used in the case when we
      move a vector like c_NS through the interface)
  """
  def __init__(self, op, a, b, space):

    # note: both, a & b, must have indices
    if a.index_structures == []:
      IndexStructureError("first operand must have an index structure %s"
                          % prettyIndex(a, space))
    if b.index_structures == []:
      IndexStructureError("second operand must have an index structure %s"
                          % prettyIndex(b, space))

    BinaryOperator.__init__(self, op, a, b, space)

    self.units = a.units * b.units

    self.index_structures = sorted(self.s_index_a | self.s_index_b)

  def __str__(self):
      s = stringBinaryOperation(self.space.language, self.op,
                                self.a, self.b,
                                indices=self.space.indices
                                )
      return s


class ExpandProduct(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    RULE: the two operants must not have any common index
    c_{X,Y,...} = a_X : b_{Y,...}
    """
    BinaryOperator.__init__(self, op, a, b, space)

    self.doc = 'EXPAND '
    try:
      self.units = a.units * b.units
    except:
      raise UnitError("add - incompatible units",
                      a.units.prettyPrint(mode="string"),
                      b.units.prettyPrint(mode="string"))


    common_index_set = self.s_index_a & self.s_index_b
    l = len(common_index_set)
    if l == 0:
      self.index_structures = sorted(self.s_index_a | self.s_index_b)

    else:
      msg = "ExpandProduct -- the two operands must not have any common index"
      msg += "\n first argument indices : %s" % self.pretty_a_indices
      msg += "\n second argument indices: %s" % self.pretty_b_indices
      raise IndexStructureError(msg)



  def __str__(self):
    language = self.space.language
    s = CODE[language][":"] % (self.a, self.b)
    return s



class Power(Operator):
  def __init__(self, op, a, b, space):
    """
    Binary operator:
    ^  :: the exponent,b

    Index structure of a propagates but not of b

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    @param prec: precedence
    """
    # TODO: what happens with the index sets -- currently the ones of a
    # BinaryOperator.__init__(self, op, a, b, space)
    Operator.__init__(self, space)
    # self.doc = TEMPLATES[op] % (a, b)

    # units of both basis and  exponent must be zero
    if (not a.units.isZero()) or (not b.units.isZero()):
      raise UnitError('units of basis and exponent must be zero',
                      a.units, b.units)
    else:
      self.units = a.units

    # RULE: exponent's indices are ignored and basis indices are copied
    self.index_structures = sorted(a.index_structures)

  def __str__(self):
    language = self.space.language
    if isinstance(self.b, PhysicalVariable):
      return stringBinaryOperation(language, '^', self.a, self.b)
    else:
      k = self.a.__str__()
      s = CODE[language]["^"] % (k, self.b)
      return s



class MaxMin(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    Binary operator
    operator:
    max | min :: units must fit, index structures must fit

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    """

    BinaryOperator.__init__(self, op, a, b, space)
    self.op = op
    self.units = a.units + b.units  # consistence check done in class

    # Rule: indices must be the same
    if a.index_structures == b.index_structures:  # strictly the same
      self.index_structures = sorted(a.index_structures)

    else:
      raise IndexStructureError("add incompatible index structures %s %s %s"
                                % ( self.pretty_a_indices, self.op, self.pretty_b_indices))

  def __str__(self):
    language = self.space.language
    s = CODE[language][self.op] % (self.a, self.b)
    return s


class Implicit(Operator):
  def __init__(self, arg, space):
    """
    implicit equations with the syntax:   Root( <variable> = 0 , <variable_solve_for>)
    <variable_solve_for> must correspond to lhs of the equation
    :param arg: variable
    :param var_to_solve: must correspond to lhs of the equation
    :param space: variable space
    """

    Operator.__init__(self, space)

    self.args = arg
    self.doc = "Root"

    # NOTE: do the checks only with the input language
    if self.space.language == "global_ID":
      # l, r = str(arg).split("_")
      print("debugging", self.space.language)
      # var_function_ID = int(r)
      self.var_to_solve = self.space.getVariable(self.space.variables.to_define_variable_name)  # var_to_solve
      # l, r = str(self.var_to_solve).split("_")
      var_to_solve_ID = str(self.var_to_solve).strip()  # int(r)

      if self.var_to_solve.label not in space.eq_variable_incidence_list:
        # TODO: this searches only one level down...
        self.msg = 'warning >>> variable %s not in incidence list' % self.var_to_solve

      found_vars, found_equs, found_vars_text, found_equs_text = findDependentVariables(self.space.variables,
                                                                                        var_to_solve_ID,
                                                                                        # var_function_ID,
                                                                                        self.space.indices)

      print("debugging -- collect equations for the root expression:", found_vars, found_equs, found_vars_text,
            found_equs_text)
      if var_to_solve_ID in found_vars:
        print("debugging -- that's great, found it")
      else:
        print("that's a problem -- variable not in the set")
        raise VarError("root error -- no dependency on the variable to be solved for")
      self.units = self.var_to_solve.units
      self.index_structures = sorted(self.var_to_solve.index_structures)

  def __str__(self):
    language = self.space.language
    return CODE[language]["Root"] % (self.args)


class Product(Operator):
  def __init__(self, argument, index, space):
    """
    product operator, where 'index' is the running index over which the sequence is reduced
    """
    Operator.__init__(self, space)

    for i in argument.units.asList():
      if i != 0:
        raise UnitError('Product expression must have no units', argument, '-')

    self.argument = argument
    self.units = argument.units
    self.index = self.space.getIndex(index)
    indices = copy.copy(argument.index_structures)
    indices.remove(self.index)
    self.index_structures = indices

  def __str__(self):
    language = self.space.language

    if language == "latex":
      index = self.space.indices[self.index]["aliases"][language]
      s = CODE[language]["Product"] % (index, self.argument)
    else:
      s = CODE[language]["Product"]%(self.argument, self.index)
    return s


class UnitaryFunction(Operator):

  def __init__(self, fct, arg, space):
    """
    Unitary functions such as sin cos etc.
    arguments may be an expression, but must have no units
    @param symbol: symbol representing
    @param fct: function name
    TODO: needs some work here such as variable name generated etc
    """

    from Common.record_definitions import RecordIndex

    Operator.__init__(self, space)

    self.args = arg
    self.fct = fct
    # print(">>>> got Ufunc")
    if fct in UNITARY_RETAIN_UNITS:  # RULE: unitary functions -- retain units
      self.units = copy.deepcopy(arg.units)
    elif fct in UNITARY_INVERSE_UNITS:  # RULE: unitary functions -- inverse units
      _units = Units.asList(arg.units)
      _u = [-1 * _units[i] for i in range(len(_units))]
      self.units = Units(ALL=_u)

    elif fct in UNITARY_NO_UNITS:  # RULE: unitary functions -- no units
      for i in arg.units.asList():  # TODO: check if this is right
        if i != 0:
          raise UnitError('%s expression must have no units'
                          % fct, arg, '-')
      self.units = arg.units

    elif fct in UNITARY_LOOSE_UNITS:  # RULe: unitary functions -- loose units
      self.units = Units()
    else:
      raise VarError('there is no unitary function : %s' % fct)

    if fct == "diffSpace":  # RULE: differential
      label = TEMPLATES["differential_space"] % arg.label
      indices = self.space.variables.ontology_container.indices
      inc_labels = []
      for inc_ID in indices:
        inc_labels.append(indices[inc_ID]["label"])
      if label not in inc_labels:
        index = RecordIndex()
        index["label"] = label
        definition_network = self.space.variable_definition_network
        index["network"] = self.space.variables.ontology_container.heirs_network_dictionary[definition_network]
        index_counter = len(indices) + 1
        indices[index_counter] = index
        for language in LANGUAGES["aliasing"]:
          indices[index_counter]["aliases"][language] = label

        language = LANGUAGES["global_ID"]
        s = CODE[language]["index"] % index_counter
        a = s  # .strip(" ")              # TODO: when we "compile" we have to add a space again. See reduceProduct.
        indices[index_counter]["aliases"][language] = a
        _index = index_counter
        self.index_structures = sorted(arg.index_structures)
        self.index_structures.append(_index)
      else:
        self.index_structures = sorted(arg.index_structures)
    else:
      self.index_structures = sorted(arg.index_structures)

  def __str__(self):
    language = self.space.language
    self.indices = self.space.indices
    try:
      CODE[language][self.fct] % (self.args)
    except:
      print("debugging -- argument:%s  language:%s" % (self.args, language))
    return CODE[language][self.fct] % (self.args)


class MakeIndex():

  def __init__(self, index_name, space):
    from Common.record_definitions import RecordIndex
    self.space = space

    indices = self.space.variables.ontology_container.indices
    inc_labels = []
    for inc_ID in indices:
      inc_labels.append(indices[inc_ID]["label"])
    if index_name not in inc_labels:
      index = RecordIndex()
      index["label"] = index_name
      definition_network = self.space.variable_definition_network
      index["network"] = self.space.variables.ontology_container.heirs_network_dictionary[definition_network]
      index_counter = len(indices) + 1
      indices[index_counter] = index
      for language in LANGUAGES["aliasing"]:
        indices[index_counter]["aliases"][language] = index_name

      language = LANGUAGES["global_ID"]
      s = CODE[language]["index"] % index_counter
      a = s  # .strip(" ")              # TODO: when we "compile" we have to add a space again. See reduceProduct.
      indices[index_counter]["aliases"][language] = a
      _index = index_counter
      self.index_structures = []
      self.units = Units()


class Instantiate(Operator):

  def __init__(self, var, value, space):
    """
    Symbolically instantiate a variable
    @param var: variable
    @param space: compile space
    The first variable defines the units, indexing and token, while the second variable defines it as a numbrical value.
    """
    # TODO: think about if indeed the second parameter <<value>> is needeed
    Operator.__init__(self, space, equation_type="instantiate")
    self.arg = var
    self.value = value
    self.index_structures = sorted(var.index_structures)
    self.units = var.units

  def __str__(self):
    self.language = self.space.language
    s = CODE[self.language]['Instantiate'] % (self.arg, self.value)
    return s


class Integral(Operator):
  def __init__(self, y, x, xl, xu, space):
    """
    implements an integral definition
    @param y: derivative
    @param x: integration variable
    @param xl: lower limit of integration variable
    @param xu: upper limit of integration variable
    """
    Operator.__init__(self, space)
    self.y = y
    self.x = x
    self.xl = xl
    self.xu = xu

    units = y.units * x.units  # consistence check done in class

    # RULE: index structures of integration variable and the limits must be the same
    xxl = x.index_structures == xl.index_structures
    xxu = x.index_structures == xu.index_structures
    if not (xxl and xxu):  # Strictly the same
      pretty_x_indices = renderIndexListFromGlobalIDToInternal(x.index_structures, self.indices)
      pretty_xl_indices = renderIndexListFromGlobalIDToInternal(xl.index_structures, self.indices)
      pretty_xu_indices = renderIndexListFromGlobalIDToInternal(xu.index_structures, self.indices)
      raise IndexStructureError(
              'interval -- incompatible index structures %s != %s != %s' %
              (pretty_x_indices, pretty_xl_indices, pretty_xu_indices))


    index_structures = sorted(y.index_structures)
    self.index_structures = index_structures
    xunits = Units.asList(x.units)
    yunits = Units.asList(y.units)
    units = [xunits[i] + yunits[i] for i in range(len(yunits))]

    self.units = Units(ALL=units)

  def __str__(self):
    language = self.space.language
    s = CODE[language]["Integral"].format(integrand=self.y,
                                          differential=self.x,
                                          lower=self.xl,
                                          upper=self.xu)
    return s


class TotDifferential(Operator):
  def __init__(self, x, y, space):
    """
    implements partial differential definition
    @param x: dx
    @param y: dy
    """

    Operator.__init__(self, space)
    self.x = x
    self.y = y

    xunits = Units.asList(x.units)
    yunits = Units.asList(y.units)
    units = [xu - yu for xu, yu in zip(xunits, yunits)]
    self.units = Units(ALL=units)


    s_index_a = set(x.index_structures)
    s_index_b = set(y.index_structures)

    self.index_structures = sorted(s_index_a | s_index_b)

  def __str__(self):
    return CODE[self.space.language]["TotalDiff"] % (self.x, self.y)


class ParDifferential(Operator):
  def __init__(self, x, y, space):
    """
    implements partial differential definition
    expands the index set
    @param x: dx
    @param y: dy
    """
    Operator.__init__(self, space)
    self.x = x
    self.y = y

    xunits = Units.asList(x.units)
    yunits = Units.asList(y.units)
    units = [xu - yu for xu, yu in zip(xunits, yunits)]
    self.units = Units(ALL=units)

    s_index_a = set(x.index_structures)
    s_index_b = set(y.index_structures)

    self.index_structures = sorted(s_index_a | s_index_b)

  def __str__(self):
    return CODE[self.space.language]["ParDiff"] % (self.x, self.y)

class ReduceSum(Operator):
  def __init__(self, x, reduceindex, space):
    """
    implements a tensor over one coordiante by summing up
    Parameters
    ----------
    x            :: tensor
    reduceindex  :: index over which one sums up
    space        :: space with necessary information
    """

    Operator.__init__(self, space)

    self.x = x
    self.reduce_index = reduceindex
    self.units = x.units

    s_index_structures = set(x.index_structures)
    index_ID = self.space.inverse_indices[reduceindex]
    self.index_structures = sorted(s_index_structures - {index_ID})
    self.reduce_index_ID = index_ID


  def __str__(self):
    language = self.space.language
    if language == "latex":
      index = self.reduce_index
    else:
      index = self.reduce_index_ID
    return CODE[language]["reduceSum"] % (self.x, index)



class Brackets(Operator):
  def __init__(self, a, space):
    Operator.__init__(self, space)
    self.a = a
    self.units = a.units
    self.index_structures = sorted(a.index_structures)

  def __str__(self):
    return CODE[self.space.language]["bracket"] % self.a


class Expression(VerboseParser):
  r"""
  separator spaces  : '\s+' ;
  token UFuncRetain : '\b(abs|neg|diffSpace|left|right)\b';
  token UFuncNone   : '\b(exp|log|ln|sqrt|sin|cos|tan|asin|acos|atan)\b';
  token UFuncInverse: '\b(inv)\b';
  token UFuncLoose  : '\b(sign)\b';
  token MaxMin      : '\b(max|min)\b';
  token IN          : '\b(in)\b';
  token Variable    : '[a-zA-Z_]\w*';
  token SUM         : '[+-]'; # plus minus
  token POWER       : '^';   # power
  token EXPAND      : ':';   # expand product
  token REDUCE      : '\*';
  token HADAMARD    : '.';    # Hadamard product

  START/e -> Expression/e
  ;
  Expression/e ->
    'Instantiate' '\(' Expression/i  ',' Expression/v  '\)'               $e=Instantiate(i, v, self.space)
      | Term/e( SUM/op Term/t                                             $e=Add(op,e,t,self.space)
      )*
  ;
  Term/t -> Factor/t (
     EXPAND/op Factor/f                                                   $t=ExpandProduct(op,t,f,self.space)
   | HADAMARD/op Factor/f                                                 $t=Hadamard(op,t,f,self.space)
   | REDUCE/op  Index/i Factor/f                                          $t=ReduceProduct(op,t,f,self.space, reduceindex=i)
   | REDUCE/op  Factor/f                                                  $t=ReduceProduct(op,t,f,self.space)
   | POWER/op Factor/f                                                    $fu=Power(op, t, f, self.space)
   )*
  ;
 Index/u -> Variable/m                                                    $u=m
 ;
 Identifier/a -> Variable/s                                               $a=self.space.getVariable(s)
 ;
  Factor/fu ->
       '\(' Expression/b '\)'                                             $fu=Brackets(b, self.space)
      | 'Integral' '\(' Expression/dx '::'
          Identifier/s IN '\['Identifier/ll ',' Identifier/ul '\]' '\)'   $fu=Integral(dx,s,ll,ul, self.space)
      | 'Product'  '\(' Expression/a ',' Index/u '\)'                     $fu=Product(a, u, self.space)
      | 'Root'  '\(' Expression/a '\)'                                    $fu=Implicit(a, self.space)
      | MaxMin/s   '\(' Expression/a ',' Expression/b '\)'                $fu=MaxMin(s, a, b, self.space)
      | 'TotalDiff'/f '\(' Expression/x ',' Expression/y '\)'             $fu=TotDifferential(x,y, self.space)
      | 'ParDiff'/f  '\(' Expression/x ',' Expression/y '\)'              $fu=ParDifferential(x,y, self.space)
      | 'reduceSum'/f '\(' Expression/x ',' Index/i '\)'                  $fu=ReduceSum(x,i,self.space)
      | UnitaryFunction/uf '\(' Expression/a '\)'                         $fu=UnitaryFunction(uf,a,  self.space)
      | Identifier/a                                                      $fu=a
  ;
  UnitaryFunction/fu ->
        UFuncRetain/fu
      | UFuncNone/fu
      | UFuncInverse/fu
      | UFuncLoose/fu
  ;
  """

  # RULE: power function is limited to identifier ^ (expression)
  # TODO: do we need BlockProduct ???  -- deleted
  # RULE: no numbers -- instantiate could therefore be simplified...!

  # verbose = 100

  def __init__(self, compile_space, verbose=0):  # variables, indices, variable_definition_network,
    # expression_definition_network, language=internal):
    '''
    Object to compile expression
    @param variables: an ordered dictionary of variable objects
    @param language: string defining the chosen target language
    '''
    self.space = compile_space  # CompileSpace(variables, indices, variable_definition_network,
    # expression_definition_network, language)
    # print("expression language:", self.space.language)
    VerboseParser.__init__(self)
    self.space.eq_variable_incidence_list = []
    self.verbose = verbose


def testDeletionApproaches(variables, var_ID, indices):
  """
  Test function to compare old vs improved deletion analysis
  """
  print("="*60)
  print(f"TESTING DELETION ANALYSIS FOR VARIABLE: {var_ID}")
  print("="*60)
  
  # Test old approach
  print("\n🔴 OLD APPROACH:")
  try:
    old_vars, old_eqs, old_vars_text, old_eqs_text = simulateDeletionOld(variables, var_ID, indices)
    print(f"  Variables to delete: {len(old_vars)}")
    print(f"  Equations to delete: {len(old_eqs)}")
    print(f"  Variables: {old_vars_text}")
    print(f"  Equations: {old_eqs_text}")
  except Exception as e:
    print(f"  ERROR in old approach: {e}")
  
  # Test improved approach  
  print("\n🟢 NEW APPROACH:")
  try:
    new_vars, new_eqs, new_vars_text, new_eqs_text, protected_vars = simulateDeletionImproved(variables, var_ID, indices)
    print(f"  Variables to delete: {len(new_vars)}")
    print(f"  Equations to delete: {len(new_eqs)}")
    print(f"  Protected state vars: {len(protected_vars)}")
    print(f"  Variables: {new_vars_text}")
    print(f"  Equations: {new_eqs_text}")
  except Exception as e:
    print(f"  ERROR in new approach: {e}")
  
  # Comparison
  print("\n📊 COMPARISON:")
  if 'old_vars' in locals() and 'new_vars' in locals():
    print(f"  Same variables found: {old_vars == new_vars}")
    print(f"  Same equations found: {old_eqs == new_eqs}")
    if len(old_vars) != len(new_vars):
      print(f"  ⚠️  Variable count differs: old={len(old_vars)}, new={len(new_vars)}")
    if len(old_eqs) != len(new_eqs):
      print(f"  ⚠️  Equation count differs: old={len(old_eqs)}, new={len(new_eqs)}")
  
  print("="*60)
  print("TEST COMPLETE\n")
  
  return True
