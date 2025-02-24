"""
from: https://github.com/RDFLib/rdflib/blob/main/examples/conjunctive_graphs.py

An RDFLib ConjunctiveGraph is an (unnamed) aggregation of all the Named Graphs
within a Store. The :meth:`~rdflib.graph.ConjunctiveGraph.get_context`
method can be used to get a particular named graph for use, such as to add
triples to, or the default graph can be used.

This example shows how to create Named Graphs and work with the
conjunction (union) of all the graphs.
"""

from rdflib import Literal, Namespace, URIRef
from rdflib.graph import ConjunctiveGraph, Graph, RDF
from rdflib.plugins.stores.memory import Memory

def contextPrint(g, l):
    print("Contexts:")
    for c in g.contexts():
        print(l, f"-- {c.identifier} ")
    print("===================")


if __name__ == "__main__":
    LOVE = Namespace("http://love.com#")
    LOVERS = Namespace("http://love.com/lovers/")

    mary = URIRef("http://love.com/lovers#mary")
    john = URIRef("http://love.com/lovers#john")

    cmary = URIRef("http://love.com/lovers/mary")
    cjohn = URIRef("http://love.com/lovers/john")

    store = Memory()

    graphs = {}
    g = ConjunctiveGraph(store=store)
    g.bind("love", LOVE)
    g.bind("lovers", LOVERS)

    g.add((URIRef("gugus"), RDF.type, Literal("hello")))
    contextPrint(g,"1")
    # Add a graph containing Mary's facts to the Conjunctive Graph
    graphs["mary"] = Graph(store=store, identifier=mary)
    gmary = graphs["mary"]
    contextPrint(g, "2")
    # Mary's graph only contains the URI of the person she loves, not his cute name
    gmary.add((mary, LOVE.hasName, Literal("Mary")))
    gmary.add((mary, LOVE.loves, john))
    contextPrint(g, "3")

    # Add a graph containing John's facts to the Conjunctive Graph
    graphs["john"] = Graph(store=store, identifier=john)
    # John's graph contains his cute name
    gjohn = graphs["john"]
    gjohn.add((john, LOVE.hasCuteName, Literal("Johnny Boy")))

    # Enumerate contexts
    print("Contexts:")
    for c in g.contexts():
        print(f"-- {c.identifier} ")
    print("===================")
    # Separate graphs
    print("John's Graph:")
    print(gjohn.serialize())
    print("===================")
    print("Mary's Graph:")
    print(gmary.serialize())
    print("===================")

    print("Full Graph")
    print(g.serialize())
    print("===================")


    print("Query the conjunction of all graphs:")
    xx = None
    for x in g[mary : LOVE.loves / LOVE.hasCuteName]:  # type: ignore[misc]
        xx = x
    print("Q: Who does Mary love?")
    print("A: Mary loves {}".format(xx))