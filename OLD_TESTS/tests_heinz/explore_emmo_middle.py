# from owlready2 import *
import rdflib

ooo = "http://emmo.info/emmo"
oo =     "https://raw.githubusercontent.com/emmo-repo/EMMO/master/emmo.ttl"

# o = "https://github.com/emmo-repo/EMMO/blob/master/emmo.ttl"
# emmo = get_ontology(ooo)

print("gugus")

emmos ={"holistic",
        "isq",
        "manufacturing",
        "math",
        "metrology",
        "middle",
        "models",
        "ordinal",
        "perceptual",
        "perspective",
        "perspective",
        "physicalistic",
        "properties",
        "reductionistic",
        "semiotics",
        "siunits",
        "units-extension"
        }


t = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')

subj = set()
pred = set()
obj = set()

for emmo in emmos:
  f = open("classes_%s.txt"%emmo,'w')
  g = rdflib.Graph()
  try:
    g.load("http://emmo.info/emmo/1.0.0-beta/middle/%s"%emmo, format="ttl")

    for s,p,o in g.triples((None,t,None)):
      print(o)
      f.write(o+"\n")

    for s,p,o in g.triples((None,None,None)):
      subj.add(s)
      pred.add(p)
      obj.add(o)

  except:
    print("failed on emmo", emmo)
  f.close()
  print("emmo", emmo)

print("gugus")

with open("subj.txt", 'w') as f:
  for l in sorted(subj):
    f.write("\n%s"%l)
with open("pred.txt", 'w') as f:
  for l in sorted(pred):
    f.write("\n%s"%l)
with open("obj.txt", 'w') as f:
  for l in sorted(obj):
    f.write("\n%s"%l)