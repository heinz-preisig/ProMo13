"""
test sparql
"""

import os

from rdflib import Graph, URIRef, Namespace, RDF

from Common.common_resources import DIRECTORIES


BASE = "http://example.org/"
BASELG = "http://example.org/language/"

ttl_location = os.path.join(DIRECTORIES["common"], "ontologies")
f_promo_ttl = os.path.join(ttl_location, "var_equ_rdf.ttl")

promo = Namespace(BASE)
promolg = Namespace(BASELG)

g = Graph()
g.load(f_promo_ttl, format="ttl")

# for t in g.triples((None,RDF.type, None)): #promo["variable"])):
#   print(t)

query = """
  PREFIX promo: <http://example.org/> 
  PREFIX promolg: <http://example.org/language/> 
  PREFIX qudt: <http://qudt.org/2.1/vocab/quantitykind#> 
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
  SELECT ?a  WHERE {
                          qudt:Temperature promo:doc ?a .}
                """

res = g.query(query)

for l in res:
  print("1 result:",l)

query = """
  PREFIX promo: <http://example.org/> 
  PREFIX promolg: <http://example.org/language/> 
  PREFIX qudt: <http://qudt.org/2.1/vocab/quantitykind#> 
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
  SELECT ?a ?b WHERE {
                          qudt:Temperature promo:doc ?a .
                          qudt:Temperature promo:label ?b .}
                """
res = g.query(query)
for l in res:
  print("2 result:",l)


namespaces = {"promo" : "http://example.org/",
              "promolg": "<http://example.org/language/",
              "qudt": "<http://qudt.org/2.1/vocab/quantitykind#" }
query = """
  SELECT ?a ?b ?c WHERE {
                          ?a rdf:type promo:variable .
                          ?a promo:label ?b .
                          ?a promo:is_defined_by_expression_list ?c.}
                """
res = g.query(query, initBindings=namespaces)

for l in res:
  print("3 result:",l)

query ="""
  PREFIX promo: <http://example.org/> 
  PREFIX promolg: <http://example.org/language/> 
  PREFIX qudt: <http://qudt.org/2.1/vocab/quantitykind#> 
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
  SELECT (COUNT(?member) AS ?count) ?member
    WHERE {
          promo:expression_list_78 rdf:first ?member  }
"""


res = g.query(query)
for l in res:
  print("4 result:",l)


query ="""
  PREFIX promo: <http://example.org/> 
  PREFIX promolg: <http://example.org/language/> 
  PREFIX qudt: <http://qudt.org/2.1/vocab/quantitykind#> 
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
  SELECT ?member
    WHERE {
          promo:expression_list_78 rdf:type ?member  }
"""


res = g.query(query)
for l in res:
  print("5 result:",l)