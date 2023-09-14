from rdflib import Graph
from rdflib import Namespace
from rdflib import RDF
from rdflib import URIRef

from ProMo_RDF_Graph import PROMO_UNIT_PREFIX
from ProMo_RDF_Graph import UNITS

PROMO = "http://example.org#"
PROMOLG = "http://example.org/language#"
QUDT = "http://qudt.org/2.1/vocab/quantitykind#"

ENDPOINTS = [PROMO, PROMOLG, QUDT]

promo = Namespace(PROMO)
rdf = Namespace(RDF)
qudt = Namespace(QUDT)


def getPrefixAndIdentifier(uiref):
  rp = uiref.toPython()
  # print(rp)

  pre, ID = None, None
  if "#" in uiref:
    pre, ID = rp.split("#")
    pre = pre + "#"

  else:
    ID = rp.split("/")[-1]
    pre = rp.split(ID)[0]

  prefix = Namespace(pre)
  return prefix, ID


class ProMoOntology:
  def __init__(self, ontology):
    self.graph = Graph()
    self.graph.parse(ontology, format="trig")

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
    g = self.graph
    counter = 0
    for s, p, o in g.triples((None, RDF.type, promo["variable"])):
      print("variable ", o)
      counter += 1

    print("no of variables", counter)  # results 143

    query_var = """
        SELECT ?v ?l ?t ?n ?d ?u1 ?u2 ?u3 ?u4 ?u5 ?u6 ?u7 ?u8 ?p
            WHERE {
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
                    }
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

      units = []
      for quantity, qudt_term in UNITS:
        u = eval(PROMO_UNIT_PREFIX + "_%s" % quantity)[0]
        if u == "-":
          u = '0'
        units.append(int(u))

      indices = []
      v_iri = URIRef(iri)

      for s, p, o in g.triples((v_iri, URIRef(promo["has_index"]), None)):
        # indices.append(o)
        for si, pi, oi in g.triples((URIRef(promo["global_index_list"]), None, o)):
          _, no = pi.split("#_")
          # print("found index p:", pi, no)
          indices.append(int(no))

      for s, p, o in g.triples(((v_iri, URIRef(promo["is_defined_by_expression_list"]), None))):
        if o == RDF.nil:
          print("nil for iri %s: " % s, o)
          eq = None
        else:
          print("for iri %s: " % s, o)
          _r, eq_list = o.split("#")
          eq, e_type, e_network, e_doc = self.extractProMoExpression(eq_list)
          print("equation:", eq)
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
    expr = ""
    end = False
    i = 0
    while not end:

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
        prefix, o = getPrefixAndIdentifier(r[0])

      sub = URIRef(prefix[o])
      # print("sub is:", sub)
      # pred = URIRef(promo["label"]) #.replace("#", "/"))  # NOTE: predicate must have a / and not a # !!!! and sometimes it is the opposite buuuu!!!
      # print("pred is:", pred)
      found = False
      for s, p, o in g.triples((sub, None, None)):
        if "label" in p:
          # print("object", o)
          expr = expr + " " + str(o)
          found = True
      i += 1
      end = not (found)

    iri = promo[e]
    e_type = str(self.extractFromGenerator(g.objects(iri, promo["equation_class"])))
    e_network = str(self.extractFromGenerator(g.objects(iri, promo["network"])))
    e_doc = str(self.extractFromGenerator(g.objects(iri, promo["doc"])))
    print(e_type, e_network, e_doc)
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
      print("The End")

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
