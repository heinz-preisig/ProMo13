
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import RDF
from rdflib import URIRef
from rdflib import RDFS


PROMO = "http://example.org#"
PROMOLG = "http://example.org/language#"
QUDT = "http://qudt.org/2.1/vocab/quantitykind#"

ENDPOINTS = [PROMO,PROMOLG,QUDT]

print("RDF:",RDF)

promo = Namespace(PROMO)
rdf = Namespace(RDF)
qudt = Namespace(QUDT)



def getPrefixAndIdentifier(uiref):
	
	rp = uiref.toPython()
	#print(rp)

	pre,ID = None,None
	if "#" in uiref:
		pre,ID = rp.split("#")
		pre = pre +"#"

	else:
		ID = rp.split("/")[-1]
		pre = rp.split(ID)[0]

	prefix = Namespace(pre)
	return prefix, ID



g = Graph()
#g.load("equations_small_test.ttl",format="ttl")
g.load("var_equ_rdf.ttl",format="ttl")


promo = Namespace(PROMO)
rdf = Namespace(RDF)
qudt = Namespace(QUDT)

case1 = False
case2 = True
case3 = False

if case1:

	query1 = """
		  SELECT ?a ?b ?c WHERE {
								  ?a rdf:type promo:variable .
								  ?a promo:label ?b .
								  ?a promo:is_defined_by_expression_list ?c.}
						"""
	res = g.query(query1)

	for var_iri, label, equation_list in res:
		iri = var_iri.split('(')
		eq_list = equation_list.split("/")[-1]
		print(var_iri, str(label), eq_list)
		
elif case2:

	e = "expression_list_85"
	e = "expression_list_6"
	e = "expression_list_111"
	expr = ""
	end = False
	i = 0
	while not end:

		query2 = """
		  SELECT ?item
		  WHERE { promo:%s rdf:_%s ?item .
					}
				""" %(e,i)

		res = g.query(query2)

		for r in res:
			prefix,o = getPrefixAndIdentifier(r[0])
			# print(r)
			# print(prefix,o)

			# query2_1 = """
			# 	PREFIX promo: <http://example.org/>
			# 	PREFIX promolg: <http://example.org/language/>
			# 	PREFIX qudt: <http://qudt.org/2.1/vocab/quantitykind#>
			# 	SELECT ?label
			# 	WHERE{ promolg:%s rdfs:label ?label .}
			# 	"""%(o)

			# query2_2 = """
			# 				PREFIX promo: <http://example.org/>
			# 				PREFIX promolg: <http://example.org/language/>
			# 				PREFIX qudt: <http://qudt.org/2.1/vocab/quantitykind#>
			# 				SELECT ?label ?x
			# 				WHERE{ ?x a qudt:%s .
			# 								?x a promo:variable .
			# 							  ?x promo:label ?label .  }
			# 				""" % (o)

			# print(query2_1)

			# if o == "AmountOfSubstance":
			# 	print("got it zzz")
			# res = g.query(query2_2)
			# if not res:
			# 	res = g.query(query2_2)
			# for r in res:
			# 	print("label rrr:", r)
		### sparql is not suitable for extracting the label --> use rdf

		sub = prefix[o]
		# for s,o,p in g.triples((sub,None,None)):
		# 	print(s,o,p)
		print("sub is:",sub)
		pred = URIRef(promo["label"].replace("#","/"))  # NOTE: predicate must have a / and not a # !!!!
		print("pred is:", pred)
		found = False
		for s,p,o in g.triples((sub, None, None)):
			# print("object", o)
			if "label" in p:
				expr = expr + " " + str(o)
				found = True

		i +=1
		end = not(found)
		# for s,p,o in g.triples((sub,RDFS.label, None)):
		# 	print("object", o)
		# 	expr = expr + str(o)

	print("made:", expr)
		
elif case3:
	a = "http://qudt.org/2.1/vocab/quantitykind#AmountOfSubstance"
	print(a)
	if QUDT in a:
		print("got qudt")
		b = a.split(QUDT)[1]
		print(b)
		query3 = """
			PREFIX qudt: <http://qudt.org/2.1/vocab/quantitykind/> 
			PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
			PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 

			SELECT ?item
			WHERE { qudt:AmountOfSubstance rdfs:label ?item}
			"""
		print(query3)
		res = g.query(query3)
		

		for r in res:
			print("case 3: found:",r)
	
	pass
