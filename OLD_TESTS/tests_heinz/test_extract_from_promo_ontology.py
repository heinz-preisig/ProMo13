"""
test extracting information from promo equation ontology
"""

import os

from rdflib import Graph, URIRef, Namespace, RDF, RDFS

from Common.common_resources import DIRECTORIES

BASE = "http://example.org/"
BASELG = "http://example.org/language/"
QUDT = "http://qudt.org/2.1/vocab/quantitykind#"

NAMESPACES = {"promo"  : BASE,
              "promolg": BASELG,
              "qudt"   : QUDT}


ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
f_promo_ttl = os.path.join(ttl_location, "var_equ_rdf.ttl")

promo = Namespace(BASE)
promolg = Namespace(BASELG)

class ProMoKnowledgeGraph():
  def __init__(self):
    self.graph = Graph()
    self.graph.load(f_promo_ttl, format="ttl")

  def getNumberOfVariables(self):
    count = 0
    for t in self.graph.triples((None,None, promo["variable"])): #promo["variable"])):
      print(t)
      s,p,o = t
      count += 1
    print("debugg: count:",count)
    return count

  def getAllVariableIRIs(self):
    varIRIs = []

    query = """
      SELECT ?a ?b ?c WHERE {
                              ?a rdf:type promo:variable .
                              ?a promo:label ?b .
                              ?a promo:is_defined_by_expression_list ?c.}
                    """
    res = self.graph.query(query, initBindings=NAMESPACES)

    for r in res:
      varIRIs.append(r)

    return varIRIs

  def getEquation(self, iri):

    res = "gugus"
    eq = []
    count = 0
    while res:
      query = """
    		SELECT ?item ?label
    		WHERE {
    				promo:%s rdf:_%s ?item .
    			}
    		""" %(iri, count)
      # print(query)
      count +=1

      try:
        res = self.graph.query(query,initBindings=NAMESPACES)
        for i in res:
          r = i
          print("result 1", r)
          eq.append(r[0].toPython())
      except:
        query = """
    		SELECT ?label
    		WHERE {
    				promo:%s rdf:_%s ?item .
    			}
    		""" %(iri, count)
        res = self.graph.query(query,initBindings=NAMESPACES)
        for i in res:
          print("result 2", i)
          eq.append((str(i[1])))
        # return
    #   item = str(res)[0]
    #   eq.append(item)
    return eq

if __name__ == '__main__':
    KG = ProMoKnowledgeGraph()

    # res = KG.getNumberOfVariables()
    # print("============ finished 1 : number of variables", res)

    # this works
    # res = KG.getAllVariableIRIs()
    # for r in res:
    #   print("all iri's :", r)

    # res = KG.getAllVariableIRIs()
    # for r in list(res):
    #   # print(r)
    #   iri = r[2]
    #   _e = iri.split("/")
    #   eq_ID = _e[-1]
    #   eq = KG.getEquation(eq_ID)
    #   print("equation %s:"%eq_ID, eq)
    # print("============ finished 2")

    e = "expression_list_85"
    res = KG.getEquation(e)
    print(res)
    print("the end")
    for i in res:
      print(i)
      k = URIRef(i)
      query = """
          		SELECT ?label
          		WHERE {
          				%s rdf:label ?label .
          			}
          		""" % (k)
      # print(query)
      try:
        res1 = KG.graph.query(query, initBindings=NAMESPACES)
        for r in res1:
          print("got",r)
      except:
        print("did not work")
        print(query)



