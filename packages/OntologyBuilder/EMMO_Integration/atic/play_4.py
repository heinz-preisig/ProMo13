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
__since__ = "12.09.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

""" 
main changes : obsolete code eliminted specifically the Ontology class reduced to MyOntology class with implementing only
the make reference to an object through its name.

"""

from owlready2 import Nothing
from owlready2 import Ontology
from owlready2 import default_world
from owlready2 import onto_path
from owlready2 import set_render_func
from owlready2 import sync_reasoner_pellet


def render_func(entity):
  name = entity.label[0] if len(entity.label) == 1 else entity.name
  return "%s.%s" % (entity.namespace.name, name)


# def render_using_label(entity):
#     return entity.label.first() or entity.name

set_render_func(render_func)


def get_ontology(base_iri='emmo-inferred.owl', verbose=False, name=None):
  """Returns a new Ontology from `base_iri`.

  If `verbose` is true, a lot of dianostics is written.
  """

  if (not base_iri.endswith('/')) and (not base_iri.endswith('#')):
    base_iri = '%s#' % base_iri
  if base_iri in default_world.ontologies:
    onto = default_world.ontologies[base_iri]
  else:
    onto = MyOntology(default_world, base_iri, name=name)
  onto._verbose = verbose
  return onto


class MyOntology(Ontology):  # , OntoGraph, OntoVocab):
  """A generic class extending owlready2.Ontology.
  """

  def __init__(self, default_world, base_iri, name=None):
    Ontology.__init__(self, default_world, base_iri, name=name)

  def __getattr__(self, name):
    attr = super().__getattr__(name)
    if not attr:
      attr = self.get_by_label(name)
    return attr

  def get_by_label(self, label):
    """Returns entity by label.

    If several entities have the same label, only the one which is
    found first is returned.  A KeyError is raised if `label`
    cannot be found.
    """
    # label = label.replace("-", "") FLB: problem with - in variable
    # Check for name in all categories in self

    # owl types
    categories = (
      'annotation_properties',
      'data_properties',
      'object_properties',
      'classes',
      'individuals',
      # 'properties',
      )
    for category in categories:
      method = getattr(self, category)
      for entity in method():
        if label in entity.label:
          return entity
    # Check for special names
    d = {
      'Nothing': Nothing,
      }
    if label in d:
      return d[label]


onto_path.append("./emmo/rdfxml")
emmo = get_ontology(name="emmo")
emmo.load()

onto = get_ontology("play.owl")
onto.imported_ontologies.append(emmo)


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
  #
  # Relations
  # =========
  class has_unit(emmo.has_part):
    """Associates a unit to a property."""
    pass


  class is_unit_for(emmo.is_part_of):
    """Associates a property to a unit."""
    inverse_property = has_unit


  class has_type(emmo.has_convention):
    """Associates a type (string, number...) to a property."""
    pass


  class is_type_of(emmo.is_convention_for):
    """Associates a property to a type (string, number...)."""
    inverse_property = has_type


  #
  # Types
  # =====
  class integer(emmo.number):
    pass


  class real(emmo.number):
    pass


  class string(emmo.number):  # ['well-formed']): #FIXME Ontology "emmo-all-inferred" has no such label: well-formed
    pass


  #
  # Units
  # =====
  class SI_unit(emmo.measurement_unit):
    """Base class for all SI units."""
    pass


  class meter(SI_unit):
    label = ['m']


  class square_meter(SI_unit):
    label = ['m²']


  class area(emmo.physical_quantity):
    """Area of a surface."""
    is_a = [has_unit.exactly(1, square_meter),
            has_type.exactly(1, real)]


  class VAR(emmo.physical_quantity):
    is_a = [has_unit.exactly(1, meter),
            has_type.exactly(3, real)]
    pass


  class is_function_of(VAR >> VAR):
    pass

a = VAR("a")
b = VAR("b")
c = VAR("c")

a.is_function_of = [onto.a, onto.b]

# onto.sync_attributes()

sync_reasoner_pellet([onto])

owlfile = "play.owl"

onto.save(owlfile)

print(a)
print(a.is_function_of)
print("end")
