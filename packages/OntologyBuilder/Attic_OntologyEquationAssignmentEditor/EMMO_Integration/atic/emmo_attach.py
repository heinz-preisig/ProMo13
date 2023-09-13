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
from owlready2 import Ontology
from owlready2 import set_render_func


def render_func(entity):
  name = entity.label[0] if len(entity.label) == 1 else entity.name
  return "%s.%s"%(entity.namespace.name, name)

  # def render_using_label(entity):
  #     return entity.label.first() or entity.name

  set_render_func(render_func)


def get_ontology(base_iri='emmo-inferred.owl', verbose=False, name=None):
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
  """A generic class extending owlready2.Ontology.
  """

  def __init__(self, default_world, base_iri, name=None):
    Ontology.__init__(self, default_world, base_iri, name=name)

  def __getattr__(self, name):
    attr = super().__getattr__(name)
    if not attr:
      attr = self._get_by_label(name)
    return attr

  def _get_by_label(self, label):
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
