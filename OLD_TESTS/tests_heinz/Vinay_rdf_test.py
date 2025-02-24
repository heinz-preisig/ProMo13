from rdflib import Graph, Namespace, Literal, BNode, RDF, RDFS, DC, FOAF, XSD, URIRef, term

from plot_rdf import plot
"""
ex = Namespace('http://example.org/')
variable = URIRef(ex["variable"])
variable_name = URIRef(ex["name"])

g = Graph()
g.bind('ex', ex)


g.add((variable, RDF.type, RDF.Property))


# This is a task in Exercise 2

print(g.serialize(format='turtle'))
"""
# ex = Namespace("http://example.org")

g = Graph()

g.load("Vinay_rdf_test.ttl",format="ttl")

for prefix, space in g.namespaces():
  if prefix == "ex":
    ex = Namespace(space)
  # print(n)

for c in g.triples((None,None,None)):
  print(c)

# g.bind("ex",ex)

# Heinz = URIRef(ex,"heinz")

g.add((ex["Heinz"], ex["name"], Literal("heinz preisig"))) #term.URIRef('http:/example.org/person')))
g.add((ex["Heinz"], ex["address"], Literal("road ln")))
g.add((ex["Heinz"], ex["age"], Literal(72)))

print("gugus")
g.serialize("gugus.ttl", format="ttl")
g.serialize("gugus.json", format= "json-ld")


dot = plot(g)
dot.render_expression_to_list("gugus", view=True, )