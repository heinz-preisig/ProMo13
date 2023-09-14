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

import emmo_attach_all as O

from owlready2 import *

name = "play"
owlfile = name+".owl"

onto  = O.setup_ontology(name)

a = onto.VAR("a")
a.has_unit_time = [-2]
a.has_unit_mass = [1]

b = onto.VAR("b")
c = onto.VAR("c")

a.is_function_of = [onto.b]
c.is_function_of = [onto.a]

# sync_reasoner_pellet([onto])
# sync_reasoner([onto])


onto.save(owlfile)
print("end")