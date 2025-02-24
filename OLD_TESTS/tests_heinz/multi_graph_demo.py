from rdflib import Dataset, ConjunctiveGraph
from rdflib.namespace import RDF

g = ConjunctiveGraph()
g.parse("multi_graph.trig")

for s, p, o, g in g.quads((None, RDF.type, None, None)):
    print(s, g)

g.serialize("mulit_graph.qds",format="nquads")