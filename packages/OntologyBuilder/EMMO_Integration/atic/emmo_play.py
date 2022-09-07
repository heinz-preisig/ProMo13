#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "06.09.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from emmo import get_ontology
from owlready2 import sync_reasoner_pellet
emmo = get_ontology()
emmo.load()
# sync_reasoner_pellet([emmo])


onto = get_ontology("play.owl", )
onto.imported_ontologies.append(emmo)

# onto.base_iri = 'http://www.emmc.info/emmc-csa/demo#'
onto.base_iri = emmo.base_iri

print("classes : ", list(emmo.classes()))
print("individuals :", list(emmo.individuals()))
print("object_properties :", list(emmo.object_properties()))
print("properties :", emmo.search(iri="physical_quantity"))
print("base iri   :", emmo.base_iri)
print("base iri   :", onto.base_iri)

classe_labels = []

for i in emmo.classes():
  classe_labels.extend(i.label)
  print(i.label)

print("variable" in classe_labels)

with onto:

    class VAR(emmo.physical_quantity):
        pass
    class is_function_of(VAR >> VAR):
        pass

    # class Is_Part(emmo.is_part_of):
    #     pass

a = VAR("a")
b = VAR("b")
c = VAR("c")


a.is_function_of=[onto.a,onto.b]

onto.sync_attributes()


sync_reasoner_pellet([onto])

owlfile = "play.owl"

import os                                   # hmmm
if os.path.exists(owlfile):
    os.remove(owlfile)
onto.save(owlfile)

print(a)
print(a.is_function_of)
print("end")