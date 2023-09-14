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

# from owlready2 import default_world

# from OntologyBuilder.EMMO_Integration.emmo import get_ontology
from OntologyBuilder.OntologyEquationEditor.ontology import get_ontology
from owlready2 import default_world
from owlready2 import Nothing
from owlready2 import onto_path
from owlready2 import Ontology
from owlready2 import set_render_func, sync_reasoner,get_namespace

import os



# Load EMMO
emmo = get_ontology()
emmo.load()
#emmo.sync_reasoner()

# Create a new ontology with out extensions that imports EMMO
onto = get_ontology('onto.owl')
onto.imported_ontologies.append(emmo)
onto.base_iri = 'http://www.emmc.info/emmc-csa/promo#'

for i in emmo.classes():
  print(i)

class ProMoOwlOntology(Ontology):

  def __init__(self):
    name = None
    Ontology.__init__(self, default_world, onto.base_iri, name=name)

  def setupOnto(self):
# Add new classes and object/data properties needed by the use case
    with onto:
      class VAR(emmo.PhysicalQuantity):  # physical_quantity):
        pass

      class time(emmo.Second >> int):
        pass

      class length(emmo.Metre >> int):
        pass

      class amount(emmo.Mole >> int):
        pass

      class mass(emmo.Kilogram >> int):
        pass

      class temperature(emmo.Kelvin >> int):
        pass

      class current(emmo.Ampere >> int):
        pass

      class light(emmo.Candela >> int):
        pass

      class is_function_of(VAR >> VAR):
        pass

    return onto
