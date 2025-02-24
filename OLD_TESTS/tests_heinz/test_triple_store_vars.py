

"""
try to generate a scheme for storing the data in a triple store

2023/02/04 Heinz A Preisig

"""


from rdflib import Graph, URIRef
from rdflib import Literal
from rdflib import RDF
from rdflib.namespace import RDFS
from rdflib import XSD
from rdflib import Namespace

ProMoOntology =  Namespace("http://www.semanticweb.org/ProMoOntology#")
variable = URIRef(ProMoOntology["variable"])
variable_name = URIRef(ProMoOntology["name"])



RDFSTerms = {
        "is_a_subclass_of": RDFS.subClassOf,
        "link_to_class"   : RDFS.isDefinedBy,
        "value"           : RDF.value,
        "comment"         : RDFS.comment,
        "integer"         : XSD.integer,
        "string"          : XSD.string,
        }

class VariableTripleStore():
  def __int__(self):
    print("initialisation")

  def create(self, label): #, type, network, index_structures, units, expressions, aliases, port_variable, tokens ):
    onto_graph = Graph()
    onto_graph.bind("promo", ProMoOntology)


    onto_graph.add((variable, RDF.Property, variable_name))

    # onto_graph.add((variable, RDF.Property, XSD.string))
    # onto_graph.add((XSD.string, RDF.value, Literal(label)))
    return onto_graph

  def write(self, onto_graph, f):
    print(onto_graph)



if __name__ == '__main__':
    V = VariableTripleStore()
    onto_graph = V.create("gugus")
    print(onto_graph)
    onto_graph.serialize(destination="gugus.ttl")



