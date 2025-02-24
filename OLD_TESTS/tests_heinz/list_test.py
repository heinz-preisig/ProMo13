
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import RDF
from rdflib import URIRef
from rdflib import RDFS


BASE = "http://example.org/"
Rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


d = Namespace(BASE)
rdf = Namespace(Rdf)

g = Graph()

myList = URIRef(d["myList"])
one = URIRef(d["one"])
two = URIRef(d["two"])
three = URIRef(d["three"])

g.add((myList, RDF.type , RDF.List))

count = 1
for o in [one,two,three]:
	p = eval("RDF._%s"%count)
	triple = myList, p , o
	g.add(triple)
	count += 1
#g.add((myList, RDF._1, one))
#g.add((myList, RDF._2, two))
#g.add((myList, RDF._3, three))

r = g.serialize("gugus.ttl","ttl")

query = """
		PREFIX d: <http://example.org/>
  SELECT (COUNT(?member) AS ?count) ?member
    WHERE {
          d:mylist/rdf:rest*/ rdf:first ?member  }
  """
  
query = """
PREFIX d: <http://example.org/>
		SELECT ?item
WHERE {
  d:myList d:contents/rdf:rest*/rdf:first ?item
}
"""

for i in range(1,10):
	query = """
		PREFIX d: <http://example.org/>
		SELECT ?item 
		WHERE {
				d:myList rdf:_%s ?item
			}

		"""%i

	res = g.query(query)
	print("result", list(res))

print("2========")


for s,p,o in g.triples((d["myList"], rdf["_1"] ,None)):
	print(s,p,o)
	
print("===============")

for i in range(1,10):
	pred = eval("rdf['_%s']"%i)
	#print(pred)
	for s,p,o in g.triples((d["myList"], pred, None)):
		print("object :", o)
	
	
#for s,p,o in g:
#	print(s,p,o)

NS = {'': d,
"rdf": RDF}

task1 = g.query("""
PREFIX d: <http://example.org/>
SELECT DISTINCT ?p WHERE{
    ?s ?p ?o .
}
""")

print(list(task1))
print("================")

