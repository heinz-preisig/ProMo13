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
__since__ = "16.09.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from owlready2 import onto_path
from owlready2 import sync_reasoner_pellet

from emmo_attach import get_ontology               # not clear why this gives an error





onto_path.append("./emmo/rdfxml")
emmo = get_ontology(name="emmo")
emmo.load()

onto = get_ontology("play.owl")
onto.imported_ontologies.append(emmo)


with onto:

  class VAR(emmo.physical_quantity):
    pass

  class is_function_of(VAR >> VAR):
    pass

  class has_unit_time(VAR >> int):
    pass

  class has_unit_length(VAR >> int):
    pass

  class has_unit_amount(VAR >> int):
    pass

  class has_unit_mass(VAR >> int):
    pass

  class has_unit_current(VAR >> int):
    pass

  class has_unit_light(VAR >> int):
    pass

  class has_no_units(VAR >> int):
    pass

a = VAR("a")
a.has_unit_time = [-2]

b = VAR("b")
c = VAR("c")

a.is_function_of = [onto.b, onto.c]

sync_reasoner_pellet([onto])

owlfile = "play.owl"

onto.save(owlfile)
print("end")