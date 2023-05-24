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

from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import RDF

from Common.ontologies.plot_rdf import plot
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from OntologyBuilder.OntologyEquationEditor.resources import DELIMITERS_alias
from OntologyBuilder.OntologyEquationEditor.resources import LIST_DELIMITERS
from OntologyBuilder.OntologyEquationEditor.resources import LIST_FUNCTIONS
from OntologyBuilder.OntologyEquationEditor.resources import LIST_OPERATORS
from OntologyBuilder.OntologyEquationEditor.resources import OPERATORS_alias

BASE = "http://example.org/"


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
    self.tokens = tokens
    self.equation_dictionary = equation_dictionary
    self.indices = indices

    ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
    promo_language = Graph()

    f_promo_language = os.path.join(ttl_location, "promo_language.ttl")
    promo_language.load(f_promo_language, format="ttl")

    f_promo_variables = os.path.join(ttl_location, "promo_variables_equations.ttl")
    promo_variables = Graph()
    promo_variables.load(f_promo_variables, format="ttl")

    f_promo_equations = os.path.join(ttl_location, "promo_equations.ttl")
    promo_equations = Graph()
    promo_equations.load(f_promo_equations, format="ttl")

    g = self.graph + promo_language + promo_variables + promo_equations
    self.graph = g

    namespaces = {}
    for prefix, ns in g.namespaces():
      namespaces[prefix] = ns
    self.namespaces = namespaces

    promo = Namespace(BASE)
    self.promo = promo

    # tokens ============================================
    for t in tokens:
      # g.add((promo[t], RDFS.subClassOf, promo["token"]))
      g.add((promo[t], RDF.type, promo["token"]))
    print("gugus")

    # indices and block_indices =====================================

    for i in indices:
      index = indices[i]
      iri = self.getVarIndexIRI(index)
      obj = promo["token_list"]
      if indices[i]["type"] == "block_index":
        for t in ["type", "label","indices", "network"]:
          triple = (iri, namespaces["promo"]+t, Literal(index[t]))
          g.add(triple)
          print("blockindex:", triple)

      if indices[i]["type"] == "index":
        for t in ["type", "label", "network"]:
          triple = (iri, namespaces["promo"]+t, Literal(index[t]))
          g.add(triple)
          print("index:", triple)

      predicate = eval("RDF._%s"%i)
      triple = iri, predicate, promo["global_index_list"]
      g.add((triple))

    # variables ===================================================================
    for vID in variables:
      v = self.variables[vID]
      iri = self.getVarIndexIRI(v)

      # g.add((iri, RDFS.subClassOf, promo["variable"]))
      g.add((iri, RDF.type, promo["variable"]))
      for t in ["label", "type", "doc",  "port_variable", "network"]:
        g.add((iri, namespaces["promo"] + t, Literal(v[t])))
      pass

    # equtions ===================================================================
    for eID in equation_dictionary:
      expression_internal = equation_dictionary[eID]["rhs"]
      print(equation_dictionary[eID]["rhs"])
      triples = self.renderToRDF(eID, expression_internal)
      for t in triples:
        try:
          g.add((t))
        except:
          print("does not work with triple",t)
      # print(s)
      pass

    # variables: append with equation lists
    for vID in variables:
      index_strutures_list = promo["index_structures_%s"%vID]
      eq_list = promo["expression_list_%s"%vID]
      v = self.variables[vID]
      iri = self.getVarIndexIRI(v)

      index_strutures = v["index_structures"]

      eqs = v["equations"]

      i_count = 0
      for iID in index_strutures:
        predicate = eval("RDF._%s"%i_count)
        # obj = promo["index_structures_list_%s"%iID]
        obj = promo[""]
        triple= index_strutures_list, predicate, obj
        print("debugging", triple)
        # print("gugus")
        g.add((triple))
        i_count += 1

      e_count = 0
      for eID in eqs:
        predicate = eval("RDF._%s"%e_count)
        obj = promo["expression_list_%s"%eID]
        triple= eq_list, predicate, obj
        print("debugging", triple)
        # print("gugus")
        g.add((triple))
        e_count += 1
      g.add((iri, promo["expression_list"], eq_list ))
      g.add((iri, promo["index_structures"], index_strutures_list))


  def getVarIndexIRI(self, item):
    """
    item is either variable or index
    """
    prefix, term = item["IRI"].split(":")
    t = term.replace(" ","").replace("&","x")
    iri = self.namespaces[prefix] + t
    return iri



  def renderToRDF(self, equation_index, expression):
    """
    render from global ID representation to RDF

    Issue here is that the variable may be of type PhysicalVariable in which case the label is an attribute
      or a dictionary as read from the variable file directly, in which case is is a hash tag
    :param expression:
    :param variables:
    :param indices:
    :return:
    """

    promo = self.promo
    items = expression.split(" ")[1:]
    rdf_items = []
    for i in range(len(items)):
      obj = promo["expression_list_%s" % equation_index]
      predicate = eval("RDF._%s"%i)
      w = items[i]
      if w:
        if w[0] == "D":
          _id = int(w.split("D_")[1])
          key = LIST_DELIMITERS[_id]
          a = DELIMITERS_alias[key]
          triple = obj, predicate, promo[a]
          # print(triple)
        elif w[0] == "O":
          _io = int(w.split("O_")[1])
          key = LIST_OPERATORS[_io]
          a = OPERATORS_alias[key]
          triple = obj, predicate, promo[a]
          # print(triple)
        elif w[0] == "F":
          _if = int(w.split("F_")[1])
          key = LIST_FUNCTIONS[_if]
          triple = obj, predicate, promo[key]
          # print(triple)
        elif w[0] == "V":
          vID = int(w.split("V_")[1])
          v = self.variables[vID]
          triple = obj, predicate, self.getVarIndexIRI(v)
          # print(triple)
        elif w[0] == "I":
          iID = int(w.split("I_")[1])
          key = indices[iID]["IRI"].split(":")[1]
          triple = obj, predicate, promo[key]
          print(triple)
        else:
          a = ">>>>> error with %s........" % w
          triple = "error"
          # print(triple)
        print(triple)
        rdf_items.append((triple))
    return rdf_items

  def load(self, ontology_name):
    self.graph.load(self.variables_expressions_ontology_file, "ttl")

  def plotMe(self):
    dot = plot(self.graph)
    f_promo_ttl = os.path.join(ttl_location, "var_equ_rdf")
    dot.render_expression_to_list(f_promo_ttl, view=True, cleanup=False)


if __name__ == '__main__':
  from Common.ontology_container import OntologyContainer

  ontology_container = OntologyContainer("ProMo_Sandbox9")
  tokens = ontology_container.tokens
  variables = ontology_container.variables
  indices = ontology_container.indices
  equation_dictionary = ontology_container.equation_dictionary

  ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
  f_promo_ttl = os.path.join(ttl_location, "var_equ_rdf")

  EQ_ontology = RDFProMo("gugus")
  EQ_ontology.create(variables, tokens, equation_dictionary, indices)
  EQ_ontology.graph.serialize(f_promo_ttl+".ttl", format="ttl")
  EQ_ontology.graph.serialize(f_promo_ttl+".n3", format="n3")
  # EQ_ontology.plotMe()
