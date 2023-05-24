from rdflib import Graph, Namespace, Literal, BNode, RDF, RDFS, DC, FOAF, XSD, URIRef, term, collection
from plot_rdf import plot
import os

QUDT_base = "http://qudt.org/vocab/"
QUDT_QuantityKind = "http://qudt.org/vocab/quantitykind/"
QUDT_Unit = "http://qudt.org/vocab/unit/"
QUDT_Sou = "http://qudt.org/vocab/sou/SI"

promo_base = "promo","http://example.org/"
QUDT_alias = {"description": "description",
              "symbol": "symbol",
              "informativeReference": "reference"
              }

qudt_ontologies = ["quantitykind", "unit"]


endpoints = dict( [ (i, "%s%s/"%(QUDT_base,i)) for i in qudt_ontologies] )
local_endpoints = dict( [(i,"qudt_%s.ttl"%i) for i in qudt_ontologies] )

print("gugus")

def getTerms(prefix):
  terms = []
  g = Graph()
  endpoint = endpoints[prefix]
  g.load(endpoint, format="ttl")
  g.serialize(local_endpoints[prefix],format="ttl")

  for sub in g.subjects(RDF.type,None):
    _sub = str(sub)
    s = _sub.replace(endpoint, "")
    if "//" not in s:
      terms.append(s)

  with open("qudt_terms_%s.txt"%prefix, 'w') as f:
    for l in sorted(terms):
      f.write("\n%s" % l)




def getSelection(prefix, s_extract, p_extract=None):

  g = Graph()
  endpoint = local_endpoints[prefix]
  g.load(endpoint,format="ttl")

  ## selective extraction
  _hash_template = "%s:%s"
  selections = []
  subgraph = Graph()
  qudt_endpoint = endpoints[prefix]
  for t in g.triples((None, None, None)):
    s, p, o = t
    s_r, p_r, o_r = str(s).replace(qudt_endpoint, ""), str(p).replace(qudt_endpoint, ""), str(o).replace(qudt_endpoint, "")

    for e in s_extract:
      if e == s_r:
        if p_extract:
          # selections.append("selection %s\n"%e)
          for pt in p_extract:
            test = p_r.split("/")[-1]
            print("test", test)
            if pt in test:
              print("pt --- ", test, pt)
              _hash = _hash_template % (e, test)
              selections.append((_hash, s_r, p_r, o_r))
              subgraph.add(t)
        else:
          # selections.append((s, p, o))
          pass
  return selections, subgraph

if __name__ == '__main__':
  promo_triples = {}

  # get units information
  units = False
  if units:   # make units graph
    prefix = "unit"
    promo_triples[prefix] = []
    if not os.path.exists(local_endpoints[prefix]):
      getTerms(prefix)

    promo_triples[prefix], subgraph = getSelection(prefix, s_extract=["A","CD", "K","KiloGM", "M", "MOL", "SEC"], #,"UNITLESS" ])
                                 p_extract=["description","symbol","informativeReference"]
                                 )

    print("gugus")
    with open("qudt_%s.txt"%prefix,'w') as f:
      for l in promo_triples[prefix]:
        promo_hash, extracted_item, p , o = l
        try:
          f.write("\n%s,%s,%s,%s"%(str(promo_hash),str(extracted_item), str(p),str(o)))
        except:
          print("did not work for :",l)

    for s,o,p in subgraph.triples((None,None,None)):
      print()
      print(s,p,o)

    subgraph.serialize("qudt_%s_extract.ttl"%prefix,format="ttl")

  else:
    prefix = "quantitykind"
    promo_triples[prefix] = []
    if not os.path.exists(local_endpoints[prefix]):
      getTerms(prefix)

    promo_triples[prefix], subgraph = getSelection(prefix, s_extract=["Temperature"],
                                 p_extract=["description","symbol","informativeReference"]
                                 )

    print("gugus")
    with open("qudt_%s.txt"%prefix,'w') as f:
      for l in promo_triples[prefix]:
        promo_hash, extracted_item, p , o = l
        try:
          f.write("\n%s,%s,%s,%s"%(str(promo_hash),str(extracted_item), str(p),str(o)))
        except:
          print("did not work for :",l)

    for s,o,p in subgraph.triples((None,None,None)):
      print()
      print(s,p,o)


#
# def getSelection(prefix, endpoint, s_extract=[], p_extract=[]):
#
#   ## selective extraction
#   _hash_template = "%s:%s"
#   selections ={}
#   for e in s_extract:
#     for e_p in p_extract:
#       selections[e] = []
#   with open("%s_triples.txt"%prefix, 'w') as f:
#     for t in g.triples((None,None,None)):
#       s,p,o = t
#       s_r,p_r,o_r = s.replace(endpoint, ""), p.replace(endpoint, ""), o.replace(endpoint, "")
#       if s_extract == []:
#         f.write("\n%s -- %s -- %s"%(s_r,p_r,o_r))
#       else:
#         for e in s_extract:
#           if e == s_r:
#             if p_extract != []:
#               # selections[e].append("selection %s\n"%e)
#               for pt in p_extract:
#                 test = p_r.split("/")[-1]
#                 print("test", test)
#                 if pt in test:
#                   print("pt --- ", test, pt)
#                   _hash = _hash_template%(e,test)
#                   selections[e].append((_hash,s_r,p_r,o_r))
#             else:
#               selections[e].append((s,p,o))
#
#     for e in selections:
#       for t in selections[e]:
#         s = "\n%s"%str(t)
#         f.write(s)
#         # try:
#         #   s_r,p_r,o_r = t
#         #   f.write("\n%s: %s -- %s -- %s"%(e,s_r,p_r,o_r))
#         # except:
#         #   f.write(t)
