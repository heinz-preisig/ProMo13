from rdflib import Graph, Namespace, Literal, BNode, RDF, RDFS, DC, FOAF, XSD, URIRef, term, collection
# from rdflib.tools import rdf2dot
from plot_rdf import plot
from OntologyBuilder.OntologyEquationEditor.resources import OPERATORS_alias,LIST_FUNCTIONS, DELIMITERS_alias

g_variables = Graph()
g_variables.bind("promo","http://example.org/")
g_variables.load("variables.ttl",format="ttl")

for prefix, space in g_variables.namespaces():
  if prefix == "promo":
    promo = Namespace(space) # that's essential -- fetches the relevant IRI

g_equations = Graph()
g_equations.bind("promo","http://example.org/")
g_equations.load("equations.ttl",format="ttl")
g_promo_language = Graph()
g_promo_language.bind("promo","http://example.org/")
g_promo_language.load("promo_language.ttl", format="ttl")

# g = g_variables# + g_equations + g_promo_language

# g = g_promo_language
# for o in OPERATORS_alias:
#   op = OPERATORS_alias[o]
#   g.add((URIRef(promo[op]), RDF.type, URIRef(promo["operator"])))
#
# for d in DELIMITERS_alias:
#   de = DELIMITERS_alias[d]
#   # g.add((URIRef(promo[de]), URIRef(promo["delimiter"]), URIRef(promo["delimiter"])))
#   g.add((URIRef(promo[de]), RDF.type, URIRef(promo["delimiter"])))
#
# for f in LIST_FUNCTIONS:
#   g.add((URIRef(promo[f]), RDF.type, URIRef(promo["function"])))
#
# g.serialize("promo_language.ttl", format="ttl")

dot = plot(g_promo_language)
dot.render_expression_to_list("language", view=True, )
#
# dot = plot(g_variables)
# dot.render("variables", view=True,)
# dot = plot(g_equations)
# dot.render("equations", view=True,)

qudt = Namespace("http://qudt.org/schema/qudt/")

g = g_variables
for c in g.triples((None,None,None)):
  print(c)

# instantiate tokens:
g.add((promo["mass"], RDF.type, promo["token"] ))
g.add((promo["energy"], RDF.type, promo["token"] ))

# variables:
g.add((qudt["EnergyInternal"], RDF.type,promo["variable"]  ))
g.add((qudt["EnergyInternal"], promo["network"], Literal("physical")))
g.add((qudt["EnergyInternal"], promo["has_unit"], qudt["KiloGM"] ))

g.add((promo["t_1"], RDF._1, promo["mass"]))
g.add((promo["t_1"], RDF._2, promo["energy"]))
g.add((promo["EnergyInternal"], promo["has_tokens"], promo["t_1"]))

#  equations
g.add((promo["e_1"], RDF._1, promo["left_round"]))
g.add((promo["e_1"], RDF._2, promo["v_2"]))
g.add((promo["e_1"], RDF._3, promo["plus"]))
g.add((promo["e_1"], RDF._4, promo["v_3"]))
g.add((promo["e_1"], RDF._5, promo["right_round"]))

g.add((promo["e_1s"], RDF._1, promo["e_1"]))
g.add((promo["e_1s"], RDF._1, promo["e_2"]))
g.add((promo["e_1s"], RDF._1, promo["e_3"]))
g.add((promo["EnergyInternal"], RDF._1, promo["e_1s"]))

g.add((qudt["Entropy"], RDF.type, promo["variable"] ))
g.add((promo["Entropy"], promo["network"], Literal("physical")))

g.add((promo["t_2"], RDF._1, promo["energy"]))
g.add((promo["Entropy"], promo["tokens"], promo["t_2"]))


g.add((promo["e_2s"], RDF._1, promo["e_3"]))
g.add((promo["Entropy"], RDF.Seq, promo["e_2s"]))

#


dot = plot(g_variables)
dot.render_expression_to_list("variable_instances", view=True, )
dot = plot(g_equations)
dot.render_expression_to_list("equation_instances", view=True, )
g = g_variables + g_equations + g_promo_language
g.serialize("var_eq_instances.ttl", format="ttl")




##========================================

# # promo["tokens"] = collection.Collection(g, promo["tokens"])
# # promo["tokens"].append(promo["mass"])
# # promo["tokens"].append(promo["energy"])
#
# # g.add((promo["tokens"],RDF.first, promo["mass"]))
# # g.add((promo["tokens"],RDF.rest, promo["energy"]))
#
# # instantiate variables
# # g.add((promo["v1"], RDF.type, promo["variable"]))  # not needed ?
#
# # g.add((promo["v1"], promo["var_name"], Literal("U")))
# # g.add((promo["v1"], promo["var_name"], qudt["EnergyInternal"]))
#
# g.add((promo["v1"], RDF.type, qudt["EnergyInternal"]))
# # g.add((promo["v1"], promo["var_name"], qudt["EnergyInternal"]))
# g.add((promo["v1"], promo["network"], Literal("physical")))
# g.add((promo["v1"], promo["present_token"], Literal([False,False])))
#
# # g.add((promo["t_1"], RDF.type, promo["indicence_list"]))
# g.add((promo["t_1"], RDF._1, promo["mass"]))
# g.add((promo["t_1"], RDF._2, promo["energy"]))
# # g.add((promo["v1"], promo["incidence_list"], promo["t1"]))
# g.add((promo["v1"], RDF.Seq, promo["t_1"]))
#
# g.add((promo["e1"], promo["rhs"], Literal("expression string")))
# g.add((promo["e2"], promo["rhs"], Literal("expression string")))
# g.add((promo["e3"], promo["rhs"], Literal("expression string")))
# g.add((promo["e4"], promo["rhs"], Literal("expression string")))
#
# # g.add((promo["e1s"], RDF.type, promo["incidence_list"]))  # not needed ?
# g.add((promo["e1s"], RDF._1, promo["e1"]))
# g.add((promo["e1s"], RDF._1, promo["e2"]))
# g.add((promo["e1s"], RDF._1, promo["e3"]))
# # g.add((promo["e1s"], RDF.Seq, promo["v1"]))
# g.add((promo["v1"], RDF.Seq, promo["e1s"]))