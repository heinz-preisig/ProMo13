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
from rdflib import URIRef
from rdflib.graph import ConjunctiveGraph
from rdflib.plugins.stores.memory import Memory

from Common.common_resources import getOntologyName
from Common.ontologies.plot_rdf import plot
from Common.ontologies.RDF_configuration import PROMO
from Common.ontologies.RDF_configuration import PROMO_UNIT_PREFIX
from Common.ontologies.RDF_configuration import PROMOINDICES
from Common.ontologies.RDF_configuration import PROMOLG
from Common.ontologies.RDF_configuration import PROMOVARS
from Common.ontologies.RDF_configuration import UNITS, QUDT, QUDT_units, PROMONWS

from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from OntologyBuilder.OntologyEquationEditor.resources import DELIMITERS_alias
from OntologyBuilder.OntologyEquationEditor.resources import LIST_DELIMITERS
from OntologyBuilder.OntologyEquationEditor.resources import LIST_FUNCTIONS
from OntologyBuilder.OntologyEquationEditor.resources import LIST_OPERATORS
from OntologyBuilder.OntologyEquationEditor.resources import OPERATORS_alias

render_expression_to_list = True #False


def contextPrint(g, l):
  print("Contexts:")
  for c in g.contexts():
    print(l, f"-- {c.identifier} ")
  print("===================")


class RDFProMo():
  def __init__(self, ontology_name):

    # get the named ontology
    self.ontology_location = DIRECTORIES["ontology_location"] % ontology_name
    self.ontology_name = ontology_name
    self.variables_expressions_ontology_file = FILES["variables_expressions_ontology_file"] % ontology_name
    pass

    self.graph = None

  def stripConnectNetworkName(self, name):
    return name.replace(">>>", "_").replace(" ", "").replace("#", "/")

  def createMultiGraph3(self, variables, tokens, equation_dictionary, indices, networks, interconnections, file=None):

    g, graphs, namespaces, store = self.prepare_graph(interconnections, networks)
    self.graph = g
    self.namespaces = namespaces

    self.variables = variables
    # print("number of variables", len(variables))  # gives 146

    self.tokens = tokens
    self.equation_dictionary = equation_dictionary
    self.indices = indices

    promo = namespaces["promo"]

    # tokens ============================================
    for t in tokens:
      g.add((URIRef(promo[t]), RDF.type, URIRef(promo["token"])))

    # indices and block_indices =====================================

    for i in indices:
      index = indices[i]
      iri = self.getIndexIRI(index)
      _, no = i.split("_")

      if indices[i]["type"] == "index":
        g.add((iri, RDF.type, URIRef(promo["index"])))
        triple = (iri, URIRef(promo + "label"), Literal(index["aliases"]["internal_code"]))
        g.add(triple)
        triple = (iri, URIRef(promo + "network"), Literal(index["network"]))
        g.add(triple)

        # predicate = eval("RDF._%s" % no)
        #
        # obj = URIRef(promo["global_index_list"])
        #
        # triple = (obj, predicate, iri)
        # g.add(triple)

    promo_units = Graph(store=store, identifier="promo_units")

    # variables ===================================================================
    # one needs the tokens, the indices before defining the variables
    set_iri = set()
    list_iri = []
    for vID in variables:
      v = self.variables[vID]
      iri = self.getVarIndexIRI(v)
      set_iri.add(iri)
      list_iri.append(iri)

      nw = self.stripConnectNetworkName(v["network"])
      gnw = graphs[nw]
      gnw.add((iri, RDF.type, URIRef(promo["variable"])))
      for t in ["label", "type", "doc", "port_variable", "network"]:
        gnw.add((iri, URIRef(promo + t), Literal(v[t])))
      # contextPrint(g,"first")

      _u = v["units"]
      for quantity, qudt_term in UNITS:
        promo_term = URIRef(promo + PROMO_UNIT_PREFIX + "_" + quantity)
        promo_value = eval('v["units"].%s' % quantity)
        promo_units.add((promo_term, URIRef(promo["has_unit"]), URIRef(namespaces["qudt_units"] + qudt_term)))
        # gnw.add((iri, URIRef(namespaces["qudt"] + qudt_term), promo_term))
        gnw.add((iri, promo_term, Literal(promo_value)))

      # for j in v["index_structures"]:
      #   _, no = j.split("_")
      #   predicate = eval("RDF._%s" % no)
      #   objs = g.objects(promo["global_index_list"], predicate)
      #   for o in objs:
      #     triple = (iri, URIRef(promo["has_index"]), o)
      #     gnw.add(triple)

    # equations ===================================================================
    # the equations come last. They need the indices and the variables.
    for eID in equation_dictionary:
      e = equation_dictionary[eID]
      expression_internal = e["rhs"]
      type = e["type"]
      doc = e["doc"]
      network = e["network"]

      if render_expression_to_list:
        triples, quads = self.renderToRDF(eID, expression_internal, indices)
        s, p, o = triples[0]
        s, p, o, l = quads[0]
        triple = s, RDF.type, RDF.List
        quad = s, RDF.type, RDF.List, l
        g.add(triple)
        # g.add(quad)
        # add other info:
        for t in triples:
        # for t in quads:
          g.add((t))

        triple = (s, URIRef(promo["equation_class"]), Literal(type))
        g.add(triple)
        triple = (s, URIRef(promo["doc"]), Literal(doc))
        g.add(triple)
        triple = (s, URIRef(promo["network"]), Literal(network))
        g.add(triple)
      pass

    counter = 0
    no_equation = []
    for vID in variables:
      counter += 1
      v = self.variables[vID]
      nw = self.stripConnectNetworkName(v["network"])
      gnw = graphs[nw]

      iri = self.getVarIndexIRI(v)
      if v["equations"] != {}:
        for eqID in v["equations"]:
          if render_expression_to_list:

            obj = URIRef(promo["expression_list_%s" % eqID])
            triple = (iri, URIRef(promo["is_defined_by_expression_list"]), obj)
            gnw.add(triple)

          else:
            obj = Literal("%s:" % eqID + equation_dictionary[eqID]["rhs"]["global_ID"])
            triple = (iri, URIRef(promo["is_defined_by_expression"]), obj)
            gnw.add(triple)
            obj = Literal("%s:" % eqID + equation_dictionary[eqID]["rhs"]["latex"])
            triple = (iri, URIRef(promo["has_latex_representation"]), obj)
            gnw.add(triple)
      else:
        triple = (iri, URIRef(promo["is_defined_by_expression_list"]), RDF.nil)
        gnw.add(triple)
        no_equation.append(vID)

    print("number of variables :", counter)
    print("no equations:", no_equation, len(no_equation))
    print("no of iri", len(set_iri), len(list_iri))

    contextPrint(g, "finished")

    # print("debugging")

  def prepare_graph(self, interconnections, networks):
    store = Memory()
    g = ConjunctiveGraph(store=store)

    uris = {"promo": URIRef(PROMO),
            }

    promo_namespaces = {"promo": Namespace(PROMO),
                        }

    for nw in networks:
      uid = '%s%s' % (PROMO, nw)
      uris[nw] = URIRef(uid)
      promo_namespaces[nw] = Namespace(uid)

    for nw_ in interconnections:
      nw = self.stripConnectNetworkName(nw_)
      uid = '%s%s' % (PROMO, nw)
      uris[nw] = URIRef(uid)
      promo_namespaces[nw] = Namespace(uid)

    for nw in promo_namespaces:
      print("bind:", nw, " to ", promo_namespaces[nw])
      g.bind(nw, promo_namespaces[nw])
    graphs = {}

    for nw in promo_namespaces:
      graphs[nw] = Graph(store=store, identifier=uris[nw])

    # load support ontologies
    ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
    f_promo_language = os.path.join(ttl_location, "promo_language.ttl")
    id = URIRef(PROMOLG)
    promo_language = Graph(store=store, identifier=id)
    promo_language.parse(f_promo_language, format="trig")

    # f_promo_variables = os.path.join(ttl_location, "promo_variables_eq_list.ttl")
    # id = URIRef(PROMOVARS)
    # promo_variables = Graph(store=store, identifier=id)
    # promo_variables.parse(f_promo_variables, format="trig")

    # get all namespaces
    namespaces = {}
    namespaces["promovars"] = Namespace(PROMOVARS)
    namespaces["indices"] = Namespace(PROMOINDICES)

    for prefix, ns in g.namespaces():
      namespaces[prefix] = Namespace(ns)

    # add promo language
    namespaces["promolg"] = Namespace(PROMOLG)

    # @ qudt_units
    namespaces["qudt"] = Namespace(QUDT)
    namespaces["qudt_units"] = Namespace(QUDT_units) #"http://qudt.org/2.1/vocab/unit")

    return g, graphs, namespaces, store

  def getVarIndexIRI(self, item):
    """
    item is either variable or index
    """
    prefix, term = item["IRI"].split(":")
    nw_ = item["network"]
    nw = self.stripConnectNetworkName(nw_)

    t = term.replace(" ", "").replace("&", "x")
    iri = URIRef(self.namespaces[prefix] + t)
    return iri

  def getIndexIRI(self, item):
    """
    item is either variable or index
    """
    prefix, term = item["IRI"].split(":")
    t = item["aliases"]["internal_code"]

    # t = term.replace(" ", "").replace("&", "x")
    iri = URIRef(self.namespaces["indices"] + t)
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

    promo = self.namespaces["promo"]
    promolg = self.namespaces["promolg"]
    # promoindices = self.namespaces["indices"]

    items_ = expression["global_ID"].split(" ")[1:]
    items = []
    for i in items_:
      if i != "":
        items.append(i)

    rdf_items = []
    rdf_quads = []
    for i in range(len(items)):
      sub = promo["expression_list_%s" % equation_index]
      if i < 10:
        predicate = eval("RDF._0%s" % i)
      else:
        predicate = eval("RDF._%s" % i)

      w = items[i]
      if w:
        if w[0] == "D":
          _id = int(w.split("D_")[1])
          key = LIST_DELIMITERS[_id]
          a = DELIMITERS_alias[key]
          triple = sub, predicate, promolg[a]
          quad = sub, predicate, promolg[a], promolg
          # print(triple)
        elif w[0] == "O":
          _io = int(w.split("O_")[1])
          key = LIST_OPERATORS[_io]
          a = OPERATORS_alias[key]
          triple = sub, predicate, promolg[a]
          quad = sub, predicate, promolg[a], promolg
          # print(triple)
        elif w[0] == "F":
          _if = int(w.split("F_")[1])
          key = LIST_FUNCTIONS[_if]
          triple = sub, predicate, promolg[key]
          quad = sub, predicate, promolg[key], promolg
          # print(triple)
        elif w[0] == "V":
          vID = int(w.split("V_")[1])
          v = self.variables[w]  # vID]
          nw_ = self.variables[w]["network"]
          nw = self.stripConnectNetworkName(nw_)
          obj = self.getVarIndexIRI(v)
          triple = sub, predicate, obj
          quad = sub, predicate, obj, self.namespaces[nw]

        elif w[0] == "I":
          iID = int(w.split("I_")[1])
          # key = indices[iID]["IRI"].split(":")[1].replace(" ", "").replace("&", "x")
          key = self.getIndexIRI(indices[w])  # iID])
          if "<" in key:
            print("bug")

          triple = sub, predicate, key
          quad = sub, predicate, key, self.namespaces["indices"]
        else:
          a = ">>>>> error with %s........" % w
          triple = "error"

        rdf_items.append((triple))
        rdf_quads.append((quad))
    return rdf_items, rdf_quads

  def load(self, ontology_name):
    self.graph.parse(self.variables_expressions_ontology_file, "ttl")

  def plotMe(self):
    ttl_location = os.path.join(DIRECTORIES["common"], "Common/ontologies")
    dot = plot(self.graph)
    f_promo_ttl = os.path.join(ttl_location, "var_equ_rdf")
    dot.render(f_promo_ttl, view=True, cleanup=False)


if __name__ == '__main__':
  from PyQt5.QtCore import QObject
  from PyQt5.QtWidgets import QApplication
  from PyQt5.QtWidgets import QWidget


  class Worker(QObject):
    from PyQt5 import QtCore
    finished = QtCore.pyqtBoundSignal()

    # def makeGraph(self):
    #   from Common.ontology_container import OntologyContainer
    #
    #   self.ontology_name = getOntologyName(task="task_RDF_variable_expression")
    #
    #   ontology_container = OntologyContainer(self.ontology_name)
    #   tokens = ontology_container.tokens
    #   variables = ontology_container.variables
    #   indices = ontology_container.indices
    #   equation_dictionary = ontology_container.equation_dictionary
    #
    #   f_promo_ttl = FILES["variablesExpression_ttl_file"] % self.ontology_name
    #   EQ_ontology = RDFProMo(self.ontology_name)
    #   EQ_ontology.create(variables, tokens, equation_dictionary, indices)
    #   # EQ_ontology.graph.serialize(f_promo_ttl + ".ttl", format="ttl")
    #   # EQ_ontology.graph.serialize(f_promo_ttl + ".n3", format="n3")
    #   # EQ_ontology.graph.serialize(f_promo_ttl + ".ld", format="json-ld")
    #   EQ_ontology.graph.serialize(f_promo_ttl + ".ld", format="trig")
    #
    #   self.finished.emit()

    def makeMultiGraph(self):
      from Common.exchange_board import ProMoExchangeBoard

      self.ontology_name = getOntologyName(task="task_RDF_variable_expression")

      ontology_container = ProMoExchangeBoard(self.ontology_name)
      tokens = ontology_container.tokens
      variables = ontology_container.variables
      print("number of variables:", len(variables))
      indices = ontology_container.indices
      equation_dictionary = ontology_container.equation_dictionary
      networks = ontology_container.networks
      interconnections = ontology_container.interconnection_nws_list
      f_promo_ttl = FILES["variablesExpression_ttl_file"] % self.ontology_name
      EQ_ontology = RDFProMo(self.ontology_name)

      EQ_ontology.createMultiGraph3(variables, tokens, equation_dictionary, indices, networks, interconnections, file=f_promo_ttl)
      EQ_ontology.graph.serialize(f_promo_ttl + ".trig", format="trig")
      # EQ_ontology.graph.serialize(f_promo_ttl + ".n3", format="n3")
      # EQ_ontology.graph.serialize(f_promo_ttl + ".ld", format="json-ld")

      # EQ_ontology.plotMe()

      self.finished.emit()


  def plotMe(self):
    ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
    dot = plot(self.graph)
    f_promo_ttl = os.path.join(ttl_location, "var_equ_rdf")
    # dot.render_expression_to_list(f_promo_ttl, view=True, cleanup=False)
    dot.render(f_promo_ttl, view=True, cleanup=False)


  class MainWindow(QWidget):
    def __init__(self):
      super().__init__()
      # self.show()

      self.worker = Worker()

      # self.thread = QThread()
      # self.worker.moveToThread(self.thread)

      self.worker.makeMultiGraph()
      self.worker.finished.connect(self.close)


  app = QApplication([])
  window = MainWindow()
  app.exec_()
