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

from owlready2 import default_world
from owlready2 import Nothing
from owlready2 import onto_path
from owlready2 import Ontology
from owlready2 import set_render_func, sync_reasoner,get_namespace


def render_func(entity):
  name = entity.label[0] if len(entity.label) == 1 else entity.name
  return "%s.%s"%(entity.namespace.name, name)

  # def render_using_label(entity):
  #     return entity.label.first() or entity.name

  set_render_func(render_func)


# def get_ontology(base_iri='emmo-inferred.owl', verbose=False, name=None):


# def get_ontology(base_iri='http://emmo.info/emmo', verbose=False, name=None):
# base_iri="http://www.semanticweb.org/heinz/ontologies/2020/1/EMMO_HAP/EMMO_HAP"
# base_iri="file:///home/heinz/ontologies/EMMO_HAP/"
base_iri="/home/heinz/ontologies/EMMO_Jesper_local"
def get_ontology(base_iri=base_iri, verbose=False, name=None):
  """Returns a new Ontology from `base_iri`.

  If `verbose` is true, a lot of dianostics is written.
  """

  if (not base_iri.endswith('/')) and (not base_iri.endswith('#')):
    base_iri = '%s#'%base_iri
  if base_iri in default_world.ontologies:
    onto = default_world.ontologies[base_iri]
  else:
    onto = MyOntology(default_world, base_iri, name=name)
  onto._verbose = verbose
  return onto


class MyOntology(Ontology):  # , OntoGraph, OntoVocab):
  """
  A generic class extending owlready2.Ontology to enable getting an entity by its label
  """

  def __init__(self, default_world, base_iri, name=None):
    Ontology.__init__(self, default_world, base_iri, name=name)

  def __getattr__(self, name):
    attr = super().__getattr__(name)
    if not attr:
      attr = self._get_by_label(name)
    return attr

  def _get_by_label(self, label):
    """
    Returns entity by label.

    If several entities have the same label, only the one which is
    found first is returned.  A KeyError is raised if `label`
    cannot be found.
    """

    # owlready2 access the content of an ontology
    # https://owlready2.readthedocs.io/en/latest/onto.html#accessing-the-content-of-an-ontology
    categories = (
          'annotation_properties',
          'data_properties',
          'object_properties',
          'classes',
          'individuals',
          'properties',
          )
    for category in categories:
      method = getattr(self, category)
      # print("debugging -- methods", list(method()))
      for entity in method():
        if label in entity.label:
          return entity
    # Check for special names
    d = {
          'Nothing': Nothing,
          }
    if label in d:
      return d[label]

  def get_by_label(self, label):
    return self._get_by_label(label)


def setup_ontology(onto_name):
  # onto_path.append(".")   #("./emmo/rdfxml")
  emmo = get_ontology(name="emmo-physical-properties")#.domains.symbolic")
  emmo.load()

  # link = "file:///home/heinz/1_Gits/ProcessModeller/EMMO_local/domains/emmo-physical-properties.owl"
  # p_emmo = get_namespace(link)
  # sync_reasoner([emmo])

  classe_labels = []
  for i in emmo.classes():
    classe_labels.extend(i.label)
    if "physical quantity" in str(i.label):
      print(i.iri)  #"file:///home/heinz/1_gits/ProcessModeller/EMMO_local/domains/emmo-physical-properties.owl#"
      phys_quantity_iri = emmo.__class__(default_world=emmo.world, base_iri=base_iri, name="physical quantity")

  onto = get_ontology(onto_name + ".owl")
  onto.imported_ontologies.append(emmo)

  with onto:
    # emmo_class =  onto.get_by_label("physical quantity")
    # print(dir(emmo))
    class VAR(emmo.physical_quantity): #physical_quantity):
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

  return onto
