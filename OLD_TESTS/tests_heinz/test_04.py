


from ontopy import World
from owlready2 import *


from emmopy import get_emmo


# Load EMMO
world = World(filename="demo.sqlite3")
emmo = get_emmo(
    "https://raw.githubusercontent.com/emmo-repo/EMMO/master/emmo.ttl"
)
emmo.load()


name_spaces = set()
pref_labels = set()

base_iri = emmo.base_iri
tr = emmo.get_triples()
tr_a = emmo.get_unabbreviated_triples()

ns = emmo.get_namespace(base_iri)


for s,p,o in tr_a:
  print(s,p,o)

graph = default_world.as_rdflib_graph()


print("======================================== graph triples")
for s,o,p in graph.triples((None,None,None)):
  print(s,o,p)

print("\n====================================== classes ")
for c in emmo.classes():
  ns,pl = str(c).split(".")
  name_spaces.add(ns)
  pref_labels.add(pl)
  print(c, ns,pl)

emmo.sync_python_names()

print(name_spaces)
print("\n =================================================== labels")
for l in sorted(pref_labels):
  print(l)

with open("class_list.txt", 'w') as f:
  for l in sorted(pref_labels):
    f.write("\n%s"%l)