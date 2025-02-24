

from emmopy import get_emmo

emmo = get_emmo()

for c in emmo.classes():
  print(c)

graph = emmo.graph

for s,p,o in emmo.get_triples(None,None,None):
  print(s,o,p)

print("gugus")

for e in emmo.get_entities():
  print(e)
  a = emmo.get_annotations(e)
  print("\n",a)

print("gugus")


tr_a = emmo.get_unabbreviated_triples()
for s,p,o in tr_a:
  print(s,p,o)

print("gugus")
