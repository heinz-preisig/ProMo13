import ontospy

model = ontospy.Ontospy("http://qudt.org/schema/qudt/",verbose=True)

for c in model.all_classes:
  print(c)

for p in model.all_properties:
  print(p)

print("gugus")