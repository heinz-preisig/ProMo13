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
__since__ = "2023. 03. 02"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__version__ = "7.00"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os

from PyQt5.QtCore import QThread, QObject,pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication

from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import RDF
from rdflib import XSD


from Common.ontologies.plot_rdf import plot
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.common_resources import getOntologyName
from OntologyBuilder.OntologyEquationEditor.resources import DELIMITERS_alias
from OntologyBuilder.OntologyEquationEditor.resources import LIST_DELIMITERS
from OntologyBuilder.OntologyEquationEditor.resources import LIST_FUNCTIONS
from OntologyBuilder.OntologyEquationEditor.resources import LIST_OPERATORS
from OntologyBuilder.OntologyEquationEditor.resources import OPERATORS_alias

BASE = "http://example.org#"
BASELG = "http://example.org/language#"

# g.add((iri, namespaces["qudt"] + "A", namespaces["promo"] + "unit_current"))
# g.add((iri, namespaces["qudt"] + "A", Literal(_u.current)))
PROMO_UNIT_PREFIX = "unit"
UNITS = [("time", "SEC"),
         ("length", "M"),
         ("amount", "MOL"),
         ("mass",  "KiloGM"),
         ("temperature", "K"),
         ("current", "A"),
         ("light",  "CD"),
         ("nil", "UNITLESS"),
         ]

render_expression_to_list = True

class RDFProMo():
  def __init__(self, ontology_name):

    # get the named ontology
    self.ontology_location = DIRECTORIES["ontology_location"] % ontology_name
    self.ontology_name = ontology_name
    self.variables_expressions_ontology_file = FILES["variables_expressions_ontology_file"] % ontology_name
    pass
    self.graph = Graph()

  def create(self, variables, tokens, equation_dictionary, indices):

    self.variables = variables
    print ("number of variables", len(variables)) # gives 146

    self.tokens = tokens
    self.equation_dictionary = equation_dictionary
    self.indices = indices

    ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
    promo_language = Graph()

    f_promo_language = os.path.join(ttl_location, "promo_language.ttl")
    promo_language.load(f_promo_language, format="ttl")

    f_promo_variables = os.path.join(ttl_location, "promo_variables_eq_list.ttl")
    promo_variables = Graph()
    promo_variables.load(f_promo_variables, format="ttl")

    g = self.graph + promo_variables
    if render_expression_to_list:
      g = g + promo_language  #+ promo_equations
    self.graph = g

    namespaces = {}
    for prefix, ns in g.namespaces():
      namespaces[prefix] = ns
    self.namespaces = namespaces

    promo = Namespace(BASE)
    promolg = Namespace(BASELG)

    self.promo = promo
    self.promolg = promolg

    # tokens ============================================
    for t in tokens:
      # g.add((promo[t], RDFS.subClassOf, promo["token"]))
      g.add((promo[t], RDF.type, promo["token"]))


    # indices and block_indices =====================================



    for i in indices:
      index = indices[i]
      iri = self.getVarIndexIRI(index)

      if indices[i]["type"] == "index":
        g.add((iri, RDF.type, promo["index"]))
        for t in ["label", "network"]:
          triple = (iri, namespaces["promo"]+t, Literal(index[t]))
          g.add(triple)
          # print("index:", triple)

        predicate = eval("RDF._%s" % i)
        obj = promo["global_index_list"]
        triple = (obj, predicate, iri)
        g.add(triple)

    for i in indices:
      index = indices[i]
      iri = self.getVarIndexIRI(index)
      if indices[i]["type"] == "block_index":
        g.add((iri, RDF.type, promo["blockIndex"]))
        for t in ["label","network"]:
          triple = (iri, namespaces["promo"]+t, Literal(index[t]))
          g.add(triple)
          # print("blockindex:", triple)
        for j in indices[i]["indices"]:
          predicate = eval("RDF._%s" % j)
          objs = g.objects(promo["global_index_list"], predicate )
          for o in objs:
            triple = (iri, promo["has_index"], o)
            g.add(triple)

        predicate = eval("RDF._%s" % i)
        obj = promo["global_index_list"]
        triple = (obj, predicate, iri)
        g.add(triple)

    # f_promo_ttl = locationForTTL("level1.ttl")
    # g.serialize(f_promo_ttl, format="ttl")

    # variables ===================================================================
    # one needs the tokens, the indices before defining the variables
    for vID in variables:
      v = self.variables[vID]
      iri = self.getVarIndexIRI(v)

      # g.add((iri, RDFS.subClassOf, promo["variable"]))
      g.add((iri, RDF.type, promo["variable"]))
      for t in ["label", "type", "doc",  "port_variable", "network"]:
        g.add((iri, namespaces["promo"] + t, Literal(v[t])))

      #time=0, length=0, amount=0, mass=0, temperature=0, current=0, light=0, nil=0
      # print("unit", v["units"])
      _u = v["units"]
      for quantity, qudt_term in UNITS:
        promo_term = namespaces["promo"] + PROMO_UNIT_PREFIX + "_" + quantity
        promo_value = eval('v["units"].%s'%quantity)
        g.add((iri, namespaces["qudt"]+qudt_term, promo_term ))
        g.add((iri, promo_term, Literal(promo_value) ))


      for j in v["index_structures"]:
        predicate = eval("RDF._%s" % j)
        objs = g.objects(promo["global_index_list"], predicate)
        for o in objs:
          triple = (iri, promo["has_index"], o)
          g.add(triple)

    # f_promo_ttl = locationForTTL("level2.ttl")
    # g.serialize(f_promo_ttl, format="ttl")

    # equations ===================================================================
    # the equations come last. They need the indices and the variables.
    for eID in equation_dictionary:
      e = equation_dictionary[eID]
      expression_internal = e["rhs"]
      type = e["type"]
      doc = e["doc"]
      network = e["network"]

      # print("debugging - expression", expression_internal)
      if render_expression_to_list:
        triples = self.renderToRDF(eID, expression_internal, indices)
        s,p,o = triples[0]
        triple = s,RDF.type,RDF.List
        g.add(triple)
        # add other info:

        for t in triples:
          # print(">>>", t)
          try:
            g.add((t))
          except:
            print("does not work with triple",t)
      # print(s)
        triple = (s,promo["equation_class"], Literal(type))
        g.add(triple)
        triple = (s, promo["doc"], Literal(doc) )
        g.add(triple)
        triple = (s, promo["network"], Literal(network))
        g.add(triple)
      pass



    counter = 0
    no_equation = []
    for vID in variables:
      counter +=1
      v = self.variables[vID]
      iri = self.getVarIndexIRI(v)
      if v["equations"] != {}:
        for eqID in v["equations"]:
          if render_expression_to_list:
            obj = promo["expression_list_%s" % eqID]
            triple = (iri, promo["is_defined_by_expression_list"], obj)
            g.add(triple)

          else:
            obj = Literal("%s:"%eqID+equation_dictionary[eqID]["rhs"])
            triple = (iri, promo["is_defined_by_expression"], obj)
            g.add(triple)
      else:
        triple = (iri, promo["is_defined_by_expression_list"], RDF.nil)
        g.add(triple)
        no_equation.append(vID)



    print("number of variables :", counter)
    print("no equations:", no_equation, len(no_equation))

  def getVarIndexIRI(self, item):
    """
    item is either variable or index
    """
    prefix, term = item["IRI"].split(":")
    t = term.replace(" ","").replace("&","x")
    iri = self.namespaces[prefix] + t
    return iri



  def renderToRDF(self, equation_index, expression, indices):
    """
    render from global ID representation to RDF

    Issue here is that the variable may be of type PhysicalVariable in which case the label is an attribute
      or a dictionary as read from the variable file directly, in which case is is a hash tag
    :param equation_index: equation ID
    :param expression: in internal notation
    :return: rdf triples
    """

    promo = self.promo
    promolg = self.promolg
    items_ = expression.split(" ")[1:]
    items = []
    for i in items_:
      if i != "":
        items.append(i)


    rdf_items = []
    for i in range(len(items)):
      sub = promo["expression_list_%s" % equation_index]
      # if equation_index == 130:
      #   print("debugging")
      if i < 10:
        predicate = eval("RDF._0%s"%i)
      else:
        predicate = eval("RDF._%s"%i)
      w = items[i]
      if w:
        if w[0] == "D":
          _id = int(w.split("D_")[1])
          key = LIST_DELIMITERS[_id]
          a = DELIMITERS_alias[key]
          triple = sub, predicate, promolg[a]
          # print(triple)
        elif w[0] == "O":
          _io = int(w.split("O_")[1])
          key = LIST_OPERATORS[_io]
          a = OPERATORS_alias[key]
          triple = sub, predicate, promolg[a]
          # print(triple)
        elif w[0] == "F":
          _if = int(w.split("F_")[1])
          key = LIST_FUNCTIONS[_if]
          triple = sub, predicate, promolg[key]
          # print(triple)
        elif w[0] == "V":
          vID = int(w.split("V_")[1])
          v = self.variables[vID]
          obj = self.getVarIndexIRI(v)
          triple = sub, predicate, obj
          # if "promolg" in obj:
          #   print("gugus", obj)
          # print(triple)
        elif w[0] == "I":
          iID = int(w.split("I_")[1])
          # key = indices[iID]["IRI"].split(":")[1].replace(" ", "").replace("&", "x")
          key = self.getVarIndexIRI(indices[iID])
          if "<" in key:
            print("bug")
          triple = sub, predicate, key #promo[key]
          # print(triple)
        else:
          a = ">>>>> error with %s........" % w
          triple = "error"
          # print(triple)
        # print(triple)
        rdf_items.append((triple))
    return rdf_items

  def load(self, ontology_name):
    self.graph.load(self.variables_expressions_ontology_file, "ttl")

  def plotMe(self):
    ttl_location = os.path.join(DIRECTORIES["common"], "Common/ontologies")
    dot = plot(self.graph)
    f_promo_ttl = os.path.join(ttl_location, "var_equ_rdf")
    dot.render_expression_to_list(f_promo_ttl, view=True, cleanup=False)


# def locationForTTL(name):
#   ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
#   return os.path.join(ttl_location, name)

class Worker(QObject):
  from PyQt5 import QtCore
  finished = QtCore.pyqtBoundSignal(str)

  def run(self):
    from Common.ontology_container import OntologyContainer

    self.ontology_name = getOntologyName(task="task_RDF_variable_expression")

    ontology_container = OntologyContainer(self.ontology_name) #"ProMo_Sandbox9")
    tokens = ontology_container.tokens
    variables = ontology_container.variables
    indices = ontology_container.indices
    equation_dictionary = ontology_container.equation_dictionary

    # f_promo_ttl = locationForTTL("var_equ_rdf")
    f_promo_ttl = FILES["variablesExpression_ttl_file"]%self.ontology_name
    EQ_ontology = RDFProMo(self.ontology_name)
    EQ_ontology.create(variables, tokens, equation_dictionary, indices)
    EQ_ontology.graph.serialize(f_promo_ttl + ".ttl", format="ttl")
    EQ_ontology.graph.serialize(f_promo_ttl + ".n3", format="n3")
    EQ_ontology.graph.serialize(f_promo_ttl + ".ld", format="json-ld")

    self.finished.emit()

class MainWindow(QWidget):
  def __init__(self):
    super().__init__()
    # self.show()

    self.worker = Worker()

    # self.thread = QThread()
    # self.worker.moveToThread(self.thread)

    self.worker.run()
    self.worker.finished.connect(self.close)



if __name__ == '__main__':
  app = QApplication([])
  window = MainWindow()
  app.exec_()
