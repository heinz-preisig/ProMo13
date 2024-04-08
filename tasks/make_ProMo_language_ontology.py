#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 ProMo Language ontology generator
===============================================================================
It reads the language elements
operator
delimiter
functions

and generates a ontology graph in the data directory
./data/promo_language.ttl", format="ttl

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2023, PREISIG, Heinz A"
__since__ = "2023. 02. 01"
__license__ = "GPL "
__version__ = "1.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from rdflib import Graph
from rdflib import RDF, RDFS
from rdflib import URIRef
from rdflib import Literal

from OntologyBuilder.OntologyEquationEditor.resources import DELIMITERS_alias
from OntologyBuilder.OntologyEquationEditor.resources import LIST_FUNCTIONS
from OntologyBuilder.OntologyEquationEditor.resources import OPERATORS_alias
from plot_rdf import plot

base = "http://example.org/language#"

g_promo_language = Graph()
g_promo_language.bind("promolg", "http://example.org/language#")

g = g_promo_language
promo_operator = URIRef(base + "operator")
predicate = RDF.type
predicate = RDFS.subClassOf
p_text = RDF.Property

for o in OPERATORS_alias:
  op = URIRef(base + OPERATORS_alias[o])
  g.add((op, predicate, promo_operator))
  g.add((op, RDFS.label, Literal(o)))

promo_delimiter = URIRef(base + "delimiter")
for d in DELIMITERS_alias:
  de = URIRef(base + DELIMITERS_alias[d])
  g.add((de, predicate, promo_delimiter))
  g.add((de, RDFS.label, Literal(d)))

promo_function = URIRef(base + "function")
for f in LIST_FUNCTIONS:
  fe = URIRef(base + f)
  g.add((fe, predicate, promo_function))
  g.add((fe, RDFS.label, Literal(f)))

g.serialize("promo_language.ttl", format="ttl")

dot = plot(g_promo_language)
dot.render("promo_language", view=True, cleanup=True)
