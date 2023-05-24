# A temperary file added to test the EMMO import 
__authors__ = 'Vinay Gautam: drvgautam@github.com'

import os, sys

from emmo import get_ontology
# from ontopy import World


# # Load EMMO
# world = World(filename="inferred-emmo.owl")
# emmo = world.get_ontology(
#     "emmo-inferred"
# )
# emmo.load()

# # foaf = world.get_ontology('http://xmlns.com/foaf/0.1/')
# # foaf.load()

# print(emmo.get_imported_ontologies(recursive=True))




# thisdir = os.path.abspath(os.path.dirname(__file__))
# sys.path.insert(1, os.path.abspath(os.path.join(thisdir, '..', '..')))
# print(sys.path.insert(1, os.path.abspath(os.path.join(thisdir, '..', '..'))))


# print(dir(emmo))
emmo = get_ontology()
emmo.load()
# print(emmo._namespaces.keys)
#emmo.sync_reasoner()

# Create a new ontology with out extensions that imports EMMO
onto = get_ontology('onto.owl')
print(onto.base_iri)
onto.imported_ontologies.append(emmo)
onto.base_iri = 'http://www.emmc.info/emmc-csa/demo#'

for i in emmo.classes():
  print(i)