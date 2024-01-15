"""
module to fetch qudt information
we get
- the labels and elucidation of all quantity kinds
- the elucidation for each of them
- the units and their elucidations
"""
import os

from rdflib import Graph
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef

promo_location = os.path.abspath("..")
DATA_location = os.path.join(promo_location, "packages", "OntologyBuilder", "OntologyEquationEditor",
                             "../../Common/ontologies")

QUDT_base = "http://qudt.org/vocab/"
QUDT_QuantityKind = "http://qudt.org/vocab/quantitykind/"
QUDT_Unit = "http://qudt.org/vocab/unit/"
QUDT_Sou = "http://qudt.org/vocab/sou/SI"
QUDT_Constant = "http://qudt.org/2.1/vocab/constant"

promo_base = "promo", "http://example.org/"
QUDT_alias = {"description"         : "description",
              "symbol"              : "symbol",
              "informativeReference": "reference"
              }

QUDT_SI_UNITS = ["SEC", "M", "MOL", "KiloGM", "K", "A", "CD"]
ProMo_SI_Units = ["s", "m", "mol", "kg", "K", "A", "cd"]  # order is defined in variable_framework class Units

qudt_ontologies = ["constant","quantitykind", "unit"]

endpoints = dict([(i, "%s%s/" % (QUDT_base, i)) for i in qudt_ontologies])

local_endpoints = dict([(i, os.path.join(DATA_location, "qudt_%s.ttl" % i)) for i in qudt_ontologies])

dbpediaMatch = URIRef("http://qudt.org/schema/qudt/dbpediaMatch")
plainTextDescription = URIRef("http://qudt.org/schema/qudt/plainTextDescription")
latexText = URIRef("http://qudt.org/schema/qudt/latexDefinition")
# applicableUnit = URIRef("http://qudt.org/vocab/unit")#
applicableUnit = URIRef("http://qudt.org/schema/qudt/applicableUnit")

PREDICATES = [RDF.type,
              RDFS.label,
              dbpediaMatch,
              plainTextDescription,
              latexText,
              applicableUnit,
              ]
PROMO_predicates = ["type", "altlabel", "wiki", "text", "laTex", "qudt_units"]


def getTerms(prefix):
  """
  extract items with predicate

  """

  # get all terms
  terms = []
  g = Graph()
  endpoint = endpoints[prefix]
  g.parse(endpoint, format="ttl")
  g.serialize(local_endpoints[prefix], format="ttl")

  selected_subjects = []
  for sub in g.subjects(RDF.type, None):
    _sub = str(sub)
    s = _sub.replace(endpoint, "")
    if "//" not in s:
      terms.append(s)
      selected_subjects.append(sub)

  fname = os.path.join(DATA_location, "qudt_terms_%s.txt" % prefix)
  with open(fname, 'w') as f:
    for l in sorted(terms):
      f.write("\n%s" % l)

  # extract what we need and store in a corresponding ttl file for ProMo
  promo_qudt_graph = Graph()
  for sub in selected_subjects:
    for pred in PREDICATES:
      for s, p, o in g.triples((sub, pred, None)):
        print("sub, predicat", s, p)
        promo_qudt_graph.add((sub, p, o))

  fname = os.path.join(DATA_location, "promo_qudt_graph_%s.ttl" % prefix)
  promo_qudt_graph.serialize(fname, format="ttl")


def getUnits(units):
  """
  extract the units defined as a list of terms: units
  """
  gu = {}
  for u in units:
    fname = "%s%s.ttl" % (QUDT_Unit, u)
    gu[u] = Graph()
    gu[u].parse(fname, format="ttl")

  gg = Graph()
  for u in units:
    gg = gg + gu[u]

  fname = os.path.join(DATA_location, "promo_units.ttl")
  gg.serialize(fname, format="ttl")

  return " done getting units"


def loadListOfTerms(prefix):
  """
  load the list of terms from the respective files.
  """
  fname = os.path.join(DATA_location, "qudt_terms_%s.txt" % prefix)
  with open(fname, 'r') as f:
    t = f.read()
  terms = t.split("\n")[1:]
  return terms


prefix = "quantitykind"
fname = os.path.join(DATA_location, "promo_qudt_graph_%s.ttl" % prefix)

promo_loaded = os.path.exists(fname)
if promo_loaded:
  promo_qudt_graph = Graph()
  promo_qudt_graph.parse(fname, format="ttl")


def getQuantityKindItemInfo(term):
  """
  get all ProMo-relevant terms
  Note: since there can be several identical terms, a number is added to the hash generated from the predicate.
  Utilised in the front end.
  """
  if promo_loaded:
    sub = URIRef("%s%s" % (QUDT_QuantityKind, term))
    info = {}
    for i in range(len(PREDICATES)):
      pred = PREDICATES[i]
      count = 0
      for s, p, o in promo_qudt_graph.triples((sub, pred, None)):
        _hash = PROMO_predicates[i] + "_%s" % count
        info[_hash] = s, p, o
        count += 1

    return info

def receiver(package):
  if package == "updateUnitInformation":
    getTerms("unit")
    return "fetched unit information form qudt and saved ttl locally"
  elif package == "updateQuantityKindInformation":
    getTerms("quantitykind")
    return "fetched quantity kinds from qudt and saved ttl locally"
  elif package == "updateConstants":
    getTerms("constant")
  elif package == "getUnits":
    getUnits(QUDT_SI_UNITS)
    return "fetched units"