

"""
variables' namespace is an issue

2023/05/03 Heinz A Preisig

"""


from rdflib import Graph, URIRef
from rdflib import Literal
from rdflib import RDF
from rdflib.namespace import RDFS
from rdflib import XSD
from rdflib import Namespace

ProMoOntology =  Namespace("http://www.semanticweb.org/promo#")
variable = URIRef(ProMoOntology["variable"])
variable_name = URIRef(ProMoOntology["name"])
variable_namespace = URIRef(ProMoOntology["namespace"])



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


    onto_graph.addN([(variable, RDF.Property, variable_name, variable_namespace)])

    # onto_graph.add((variable, RDF.Property, XSD.string))
    # onto_graph.add((XSD.string, RDF.value, Literal(label)))
    return onto_graph

  def write(self, onto_graph, f):
    print(onto_graph)



if __name__ == '__main__':
    V = VariableTripleStore()
    onto_graph = V.create("variable_namespace_test")
    print(onto_graph)
    onto_graph.serialize(destination="variable_namespace_test.ttl", format="trig")
    print("done")



