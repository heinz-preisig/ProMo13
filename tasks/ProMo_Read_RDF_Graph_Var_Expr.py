#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 reads ontology container as an RDF graph
 and reconstructs the original input for all equations.
 The equations are also available in internal and latex format
===============================================================================

2024-04-30  Heinz A Preisig

"""

from rdflib import Dataset
from rdflib import Namespace
from rdflib import RDF
from rdflib import URIRef

from Common.ontologies.RDF_configuration import PROMO
from Common.ontologies.RDF_configuration import PROMO_UNIT_PREFIX
from Common.ontologies.RDF_configuration import QUDT
from Common.ontologies.RDF_configuration import UNITS


promo = Namespace(PROMO)
rdf = Namespace(RDF)
qudt = Namespace(QUDT)


def getPrefixAndIdentifier(uiref):
  rp = uiref.toPython()

  if "#" in uiref:
    s = rp.split("#")
    if len(s) == 2:
      namespace = s[0]
      pre = s[0] + "#"
      ID = s[1]
    elif len(s) == 3:
      namespace = s[0]
      pre = s[0] + "#" + s[1]
      ID = s[2]
    else:
      print("error")

  else:
    ID = rp.split("/")[-1]
    pre = rp.split(ID)[0]
    namespace = pre

  prefix = Namespace(pre)
  return prefix, ID, namespace


class ProMoOntology:
  def __init__(self, ontology):
    self.graph = Dataset()
    self.graph.parse(ontology)

  def getVarIndexIRI(self, item):
    """
    item is either variable or index
    """
    prefix, term = item["IRI"].split(":")
    t = term.replace(" ", "").replace("&", "x")
    iri = promo + t
    return iri

  def getAllVariablesAndExpressions(self):
    """
    extract all variables from the ontology
    """

    get_graphs = False
    count_variables = True

    g = self.graph

    if count_variables:
      counter = 0
      for s, p, o, l in g.quads((None, RDF.type, promo["variable"], None)):
        # print("variable ", o, " context:", l)
        counter += 1

      print("no of variables", counter)  # results 143

    if get_graphs:
      query_graph = """ SELECT DISTINCT ?g 
                        WHERE {
                        GRAPH ?g { ?s ?p ?o }
                        }
                    """

      res_graph = g.query(query_graph)

      for r in res_graph:
        print(r)

    query_var = """
        SELECT ?v ?l ?t ?n ?d ?u1 ?u2 ?u3 ?u4 ?u5 ?u6 ?u7 ?u8 ?p
            WHERE { GRAPH ?g {
                    ?v rdf:type promo:variable .
                    ?v promo:label ?l .
                    ?v promo:type ?t .
                    ?v promo:network ?n .
                    ?v promo:doc ?d .
                    ?v promo:unit_time ?u1 .
                    ?v promo:unit_length ?u2 .
                    ?v promo:unit_amount ?u3 .
                    ?v promo:unit_mass ?u4 .
                    ?v promo:unit_temperature ?u5 .
                    ?v promo:unit_current ?u6 .
                    ?v promo:unit_light ?u7 .
                    ?v promo:unit_nil ?u8 .
                    ?v promo:port_variable ?p .
                    }}
              """
    res_var = g.query(query_var)

    variable_attribute_dict = {}

    for r in res_var:
      # print("length of r", len(r))
      equation_list = []
      iri, \
        label, \
        type, \
        network, \
        doc, \
        unit_time, \
        unit_length, \
        unit_amount, \
        unit_mass, \
        unit_temperature, \
        unit_current, \
        unit_light, \
        unit_nil, \
        port_variable = r

      _s = str(iri).split("/")
      v_nw, v_name = _s[-1].split("#")
      # print(v_nw,v_name)

      units = []
      for quantity, qudt_term in UNITS:
        u = eval(PROMO_UNIT_PREFIX + "_%s" % quantity)[0]
        if u == "-":
          u = '0'
        units.append(int(u))

      indices = []
      v_iri = URIRef(iri)

      for s, p, o, l in g.quads((v_iri, URIRef(promo["has_index"]), None, None)):
        # indices.append(o)
        for si, pi, oi, li in g.quads((URIRef(promo["global_index_list"]), None, o, None)):
          _, no = str(pi).split("#_")
          # print("found index p:", pi, no)
          indices.append(int(no))

      for s, p, o, l in g.quads(((v_iri, URIRef(promo["is_defined_by_expression_list"]), None, None))):
        if o == RDF.nil:
          q = str(s).split("#")
          # print("nil for iri %s: " % s, p, o, l)
          print("no equation for %s" % q[1])
          eq = None
        else:
          # print("for iri %s: " % s, o)
          _r, eq_list = str(o).split("#")
          eq, e_type, e_network, e_doc = self.extractProMoExpression(eq_list)
          print("equation domain %s: %s := %s" % (v_nw, v_name, eq))
          equation_attribute_dic = {"rhs"    : eq,
                                    "type"   : e_type,
                                    "network": e_network,
                                    "doc"    : e_doc,
                                    }
          equation_list.append(equation_attribute_dic)

      variable_attribute_dict[v_iri] = {"label"            : str(label),
                                        "type"             : str(type),
                                        "network"          : str(network),
                                        "doc"              : str(doc),
                                        "index_structures:": indices,
                                        "units"            : units,
                                        "equations"        : equation_list,
                                        }

    return variable_attribute_dict

  def extractProMoExpression(self, e):

    g = self.graph
    iri = promo[e]
    e_type = str(self.extractFromGenerator(g.objects(iri, promo["equation_class"])))
    e_network = str(self.extractFromGenerator(g.objects(iri, promo["network"])))
    e_doc = str(self.extractFromGenerator(g.objects(iri, promo["doc"])))


    expr = ""
    end = False
    i = 0
    while not end:
      # Note: Items are numbered 00,01,02,..... so we assume less than 100
      if i < 10:
        query = """
          SELECT ?item
          WHERE { promo:%s rdf:_0%s ?item .
              }
            """ % (e, i)
      else:
        query = """
          SELECT ?item
          WHERE { promo:%s rdf:_%s ?item .
              }
            """ % (e, i)

      res = g.query(query)

      for r in res:  # res comes as interator

        prefix, o, namespace = getPrefixAndIdentifier(r[0])

      sub = URIRef(prefix[o])
      found = False
      for s, p, o, l in g.quads((sub, None, None, None)):

        # print(">>> s: %s,  p:%s, o:%s, l:%s -- namespace:%s, -- source network:%s" % (s, p, o, l, namespace, domain_nw))

        if ("label" in p):
          expr = expr + " " + str(o)
          found = True

          # print("object", o, "graph", l)

      i += 1
      end = not (found)

    iri = promo[e]
    e_type = str(self.extractFromGenerator(g.objects(iri, promo["equation_class"])))
    e_network = str(self.extractFromGenerator(g.objects(iri, promo["network"])))
    e_doc = str(self.extractFromGenerator(g.objects(iri, promo["doc"])))
    # print(e_type, e_network, e_doc)
    return expr, e_type, e_network, e_doc

  def extractFromGenerator(self, generator):
    l = []
    for g in generator:
      l.append(g)
    if len(l) > 1:
      print("extraction error")
      return
    return l[0]


if __name__ == '__main__':
  from PyQt5.QtCore import QObject
  from PyQt5.QtWidgets import QWidget, QApplication


  class Worker(QObject):
    from PyQt5 import QtCore
    finished = QtCore.pyqtBoundSignal(str)

    def run(self):
      from Common.common_resources import getOntologyName
      from Common.resource_initialisation import FILES

      ontology_name = getOntologyName(task="task_RDF_render_expressions")

      f_promo_ttl = FILES["variablesExpression_ttl_file"] % ontology_name + ".trig"

      ProMoOnto = ProMoOntology(f_promo_ttl)  # "var_equ_rdf.ttl")
      variables = ProMoOnto.getAllVariablesAndExpressions()

      print("The End -- no of variables:", len(variables))

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


  app = QApplication([])
  window = MainWindow()
  app.exec_()
