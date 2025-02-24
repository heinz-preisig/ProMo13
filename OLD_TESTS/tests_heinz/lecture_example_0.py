from rdflib import Graph, Namespace, Literal, BNode, RDF, RDFS, DC, FOAF, XSD

EX = Namespace('http://example.org/')

g = Graph()
g.bind('ex', EX)

donaldTrumpSpouses = BNode()
g.add((donaldTrumpSpouses, RDF.type, RDF.Seq))
g.add((donaldTrumpSpouses, RDF._1, EX.IvanaTrump))
g.add((donaldTrumpSpouses, RDF._2, EX.MarlaMaples))
g.add((donaldTrumpSpouses, RDF._3, EX.MelaniaTrump))

#g.add((EX.Donald_Trump, SCHEMA.spouse, donaldTrumpSpouses))

print(g.serialize(format='turtle'))
