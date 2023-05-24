

"""
read FOAF ontology and have a look at it.
"""


from rdflib import Graph, URIRef
from rdflib import Literal
from rdflib import RDF
from rdflib.namespace import RDFS
from rdflib import XSD
from rdflib import Namespace

g = Graph()
g.load("/home/heinz/Dropbox/workspace/ontologies/FOAF.ttl",format="ttl")

for s,p,o in g.triples((None,None,None)):
  print(s,p,o)

if __name__ == '__main__':

  print(g)
