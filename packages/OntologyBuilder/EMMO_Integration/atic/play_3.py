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

import inspect
import itertools
import os  # hmmm

from owlready2 import default_world  # ,get_ontology
from owlready2 import Nothing
from owlready2 import onto_path
from owlready2 import Ontology
from owlready2 import set_render_func
# from emmo import get_ontology
from owlready2 import sync_reasoner_pellet #, get_namespace


# import emmo
# from emmo import owldir


class NoSuchLabelError(LookupError):
  """Error raised when a label cannot be found."""
  pass


def render_func(entity):
  name = entity.label[0] if len(entity.label) == 1 else entity.name
  return "%s.%s"%(entity.namespace.name, name)


set_render_func(render_func)

# def render_using_label(entity):
#     return entity.label.first() or entity.name
# set_render_func(render_using_label)


# owl types
categories = (
      'annotation_properties',
      'data_properties',
      'object_properties',
      'classes',
      'individuals',
      # 'properties',
      )


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

  # def __getitem__(self, name):
  #   return self.__getattr__(name)

  def __getattr__(self, name):
    attr = super().__getattr__(name)
    if not attr:
      attr = self.get_by_label(name)
    return attr

  # def __dir__(self):
  #   """Include classes in dir() listing."""
  #   f = lambda s: s[s.rindex('.') + 1:] if '.' in s else s
  #   s = set(object.__dir__(self))
  #   for onto in [get_ontology(uri) for uri in self._namespaces.keys()]:
  #     s.update([f(repr(cls)) for cls in onto.classes()])
  #   return sorted(s)

  # def __objclass__(self):
  #   # Play nice with inspect...
  #   pass

  # def get_root_classes(self):
  #     """Returns a list or root classes."""
  #     return [cls for cls in self.classes()
  #             if not cls.ancestors().difference(set([cls, Thing]))]
  #
  def get_by_label(self, label):
    """Returns entity by label.

    If several entities have the same label, only the one which is
    found first is returned.  A KeyError is raised if `label`
    cannot be found.
    """
    # label = label.replace("-", "") FLB: problem with - in variable
    # Check for name in all categories in self
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
    # Check whether `label` matches a Python class name of any category
    # l = [cls for cls in itertools.chain.from_iterable(
    #       getattr(self, category)() for category in categories)
    #      if hasattr(cls, '__name__') and cls.__name__ == label]
    # if len(l) == 1:
    #   return l[0]
    # elif len(l) > 1:
    #   raise NoSuchLabelError('There is more than one Python class with '
    #                          'name %r'%label)
    # # Check imported ontologies
    # for onto in self.imported_ontologies:
    #   onto.__class__ = self.__class__  # magically change type of onto
    #   try:
    #     return onto.get_by_label(label)
    #   except NoSuchLabelError:
    #     pass

  #     # Fallback to check whether we have a class in the current or any
  #     # of the imported ontologies whos name matches `label`
  #     #for onto in [self] + self.imported_ontologies:
  #     #    l = [cls for cls in onto.classes() if cls.__name__ == label]
  #     #    if len(l) == 1:
  #     #        return l[0]
  #     #    elif len(l) > 1:
  #     #        raise NoSuchLabelError('There is more than one class with '
  #     #                               'name %r' % label)
  #     # Label cannot be found
  #     raise NoSuchLabelError('Ontology "%s" has no such label: %s' % (
  #         self.name, label))
  #
  # def get_by_label_all(self, label):
  #     """Like get_by_label(), but returns a list of all entities with
  #     matching labels.
  #     """
  #     return [entity for entity in
  #             itertools.chain.from_iterable(
  #                 getattr(self, c)() for c in categories)
  #             if hasattr(entity, 'label') and label in entity.label]
  #
  # def sync_reasoner(self):
  #     """Update current ontology by running the HermiT reasoner."""
  #     with self:
  #         owlready2.sync_reasoner()
  #
  def sync_attributes(self, sync_imported=False):
    """Call method is intended to be called after you have added new
    classes (typically via Python).

    If a class, object property or individual in the current
    ontology has no label, the name of the corresponding Python class
    will be assigned as label.

    If a class, object property or individual has no comment, it will
    be assigned the docstring of the corresponding Python class.

    If `sync_imported` is true, all imported ontologies are also
    updated.
    """
    for cls in itertools.chain(self.classes(), self.object_properties(),
                               self.individuals()):
      if not cls.label:
        try:
          cls.label.append(cls.__name__)
        except:
          cls.label.append(cls._name)
      if not cls.comment and cls.__doc__:
        cls.comment.append(inspect.cleandoc(cls.__doc__))
    if sync_imported:
      for onto in self.imported_ontologies:
        onto.sync_attributes()

  #     # FIXME - optionally, consider to also update the class names.
  #     # Possible options could be:
  #     #   - do not change names (defalt)
  #     #   - set name to ``prefix + "_" + uuid`` where `prefix` is any
  #     #     string (e.g. "EMMO") and `uuid` is an uuid.  This is the
  #     #     default for EMMO.
  #     #   - set names to the name of the corresponding Python class
  #     #   - set names equal to labels
  #
  # def get_relations(self):
  #     """Returns a generator for all relations."""
  #     return self.object_properties()
  #
  # def get_annotations(self, entity):
  #     """Returns a dict with annotations for `entity`.  Entity may be given
  #     either as a ThingClass object or as a label."""
  #     if isinstance(entity, str):
  #         entity = self.get_by_label(entity)
  #     d = {'comment': getattr(entity, 'comment', '')}
  #     for a in self.annotation_properties():
  #         d[a.label.first()] = [
  #             o.strip('"') for s, p, o in
  #             self.get_triples(entity.storid, a.storid, None)]
  #     return d
  #
  # def get_branch(self, root, leafs=(), include_leafs=True):
  #     """Returns a list with all direct and indirect subclasses of `root`.
  #     Any subclass found in the sequence `leafs` will be included in
  #     the returned list, but its subclasses will not.
  #
  #     If `include_leafs` is true, the leafs are included in the returned
  #     list, otherwise they are not.
  #
  #     The elements of `leafs` may be ThingClass objects or labels.
  #     """
  #     def _branch(root, leafs):
  #         if root not in leafs:
  #             branch = [root]
  #             for c in root.subclasses():
  #                 branch.extend(_branch(c, leafs))
  #         else:
  #             branch = [root] if include_leafs else []
  #         return branch
  #
  #     if isinstance(root, str):
  #         root = self.get_by_label(root)
  #     leafs = set(self.get_by_label(leaf) if isinstance(leaf, str)
  #                 else leaf for leaf in leafs)
  #     leafs.discard(root)
  #     return _branch(root, leafs)
  #
  # def is_individual(self, entity):
  #     """Returns true if entity is an individual."""
  #     if isinstance(entity, str):
  #         entity = self.get_by_label(entity)
  #     #return isinstance(type(entity), owlready2.ThingClass)
  #     return isinstance(entity, owlready2.Thing)
  #
  # def is_defined(self, entity):
  #     """Returns true if the entity is a defined class."""
  #     if isinstance(entity, str):
  #         entity = self.get_by_label(entity)
  #     return hasattr(entity, 'equivalent_to') and bool(entity.equivalent_to)
  #
  # def common_ancestors(self, cls1, cls2):
  #      """Return a list of common ancestors"""
  #      return set(cls1.ancestors()).intersection(cls2.ancestors())
  #
  # def number_of_generations(self, descendant, ancestor):
  #     """ Return shortest distance from ancestor to descendant"""
  #     if ancestor not in descendant.ancestors():
  #         raise ValueError('Descendant is not a descendant of ancestor')
  #     return self._number_of_generations(descendant, ancestor, 0)
  #
  # def _number_of_generations(self, descendant, ancestor, n):
  #     """ Recursive help function to number_of_generations(), return distance between a ancestor-descendant pair (
  #     n+1). """
  #     if descendant.name == ancestor.name:
  #         return n
  #     return min(self._number_of_generations(parent, ancestor, n + 1)
  #                for parent in descendant.get_parents()
  #                if ancestor in parent.ancestors())
  #
  # def closest_common_ancestors(self, cls1, cls2):
  #     """Returns a list  with closest_common_ancestor to cls1 and cls2"""
  #     distances = {}
  #     for ancestor in self.common_ancestors(cls1, cls2):
  #         distances[ancestor] = self.number_of_generations(cls1, ancestor) + self.number_of_generations(cls2,
  #         ancestor)
  #     return [ancestor for ancestor, distance in distances.items() if distance == min(distances.values())]
  def save_me(self, owl_file):
    if os.path.exists(owlfile):
      os.remove(owlfile)
    self.save(owlfile)


onto_path.append("./emmo/rdfxml")
emmo = get_ontology(name="emmo")
emmo.load()
# sync_reasoner_pellet([emmo])


onto = get_ontology("play.owl", )
onto.imported_ontologies.append(emmo)

onto.base_iri = 'http://www.emmc.info/emmc-csa/demo#'
# onto.base_iri = emmo.base_iri

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

# emmo_namespace = emmo.get_namespace("emmo-inferred.owl") # get_namespace("http://purl.obolibrary.org/obo/")
# emmo_namespace.has_part

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
  #
  #
  # class pascal(SI_unit):
  #   label = ['Pa']


  #
  # Properties
  # ==========
  # class position(emmo.physical_quantity):
  #   """Spatial position of an physical entity."""
  #   is_a = [has_unit.exactly(1, meter),
  #           has_type.exactly(3, real)]


  class area(emmo.physical_quantity):
    """Area of a surface."""
    is_a = [has_unit.exactly(1, square_meter),
            has_type.exactly(1, real)]
  #
  #
  # class pressure(emmo.physical_quantity):
  #   """The force applied perpendicular to the surface of an object per
  #   unit area."""
  #   is_a = [has_unit.exactly(1, pascal),
  #           has_type.exactly(1, real)]
  #
  #
  # class stiffness_tensor(pressure):
  #   r"""The stiffness tensor $c_{ijkl}$ is a property of a continuous
  #   elastic material that relates stresses to strains (Hooks's
  #   law) according to
  #
  #       $\sigma_{ij} = c_{ijkl} \epsilon_{kl}$
  #
  #   Due to symmetry and using the Voight notation, the stiffness
  #   tensor can be represented as a symmetric 6x6 matrix
  #
  #       / c_1111  c_1122  c_1133  c_1123  c_1131  c_1112 \
  #       | c_2211  c_2222  c_2233  c_2223  c_2231  c_2212 |
  #       | c_3311  c_3322  c_3333  c_3323  c_3331  c_3312 |
  #       | c_2311  c_2322  c_2333  c_2323  c_2331  c_2312 |
  #       | c_3111  c_3122  c_3133  c_3123  c_3131  c_3112 |
  #       \ c_1211  c_1222  c_1233  c_1223  c_1231  c_1212 /
  #
  #   """
  #   is_a = [has_unit.exactly(1, pascal),
  #           has_type.exactly(36, real)]
  #
  #
  # class atomic_number(emmo.physical_quantity):
  #   """Number of protons in the nucleus of an atom."""
  #   is_a = [has_type.exactly(1, integer)]
  #
  #
  # class lattice_vector(emmo.physical_quantity):
  #   """A vector that participitates defining the unit cell."""
  #   is_a = [has_unit.exactly(1, meter),
  #           has_type.exactly(3, real)]
  #
  #
  # class spacegroup(emmo.descriptive_property):
  #   """A spacegroup is the symmetry group off all symmetry operations
  #   that apply to a crystal structure.
  #
  #   It is identifies by its Hermann-Mauguin symbol or space group
  #   number (and setting) in the International tables of
  #   Crystallography."""
  #   is_a = [has_type.exactly(1, string)]
  #   pass
  #
  #
  # class plasticity(emmo.physical_quantity):
  #   """Describes Yield stress and material hardening."""
  #   is_a = [has_unit.exactly(1, pascal),
  #           has_type.min(2, real)]
  #
  #
  # class traction_separation(pressure):
  #   """The force required to separate two materials a certain distance per
  #   interface area.  Hence, traction_separation is a curve, that
  #   numerically can be represented as a series of (force,
  #   separation_distance) pairs."""
  #   is_a = [has_unit.exactly(1, pascal),
  #           has_type.min(4, real)]
  #
  #
  # class load_curve(pressure):
  #   """A measure for the displacement of a material as function of the
  #   appliced force."""
  #   is_a = [has_unit.exactly(1, pascal),
  #           has_type.min(4, real)]
  #
  #
  # #
  # # Subdimensional
  # # ==============
  # class interface(emmo.surface):
  #   """A 2D surface associated with a boundary.
  #
  #   Commonly referred to as "interface".
  #   """
  #   is_a = [emmo.has_property.exactly(1, area),
  #           emmo.has_property.exactly(1, traction_separation)]
  #
  #
  # #
  # # Material classes
  # # ================
  #
  # # Crystallography-related classes
  # # -------------------------------
  # class crystal_unit_cell(emmo.mesoscopic):
  #   """A volume defined by the 3 unit cell vectors.  It contains the atoms
  #   constituting the unit cell of a crystal."""
  #   is_a = [emmo.has_spatial_direct_part.some(emmo['e-bonded_atom']),
  #           emmo.has_space_slice.some(interface),
  #           emmo.has_property.exactly(3, lattice_vector),
  #           emmo.has_property.exactly(1, stiffness_tensor)]
  #
  #
  # class crystal(emmo.solid):
  #   """A periodic crystal structure."""
  #   is_a = [emmo.has_spatial_direct_part.only(crystal_unit_cell),
  #           emmo.has_property.exactly(1, spacegroup)]
  #
  #
  # # Add some properties to our atoms
  # emmo['e-bonded_atom'].is_a.append(emmo.has_property.exactly(1, atomic_number))
  # emmo['e-bonded_atom'].is_a.append(emmo.has_property.exactly(1, position))
  #
  #
  # # Continuum
  # # ---------
  # class boundary(emmo.state):
  #   """A boundary is a 4D region of spacetime shared by two material
  #   entities."""
  #   equivalient_to = [emmo.has_spatial_direct_part.exactly(2, emmo.state)]
  #   is_a = [emmo.has_space_slice.exactly(1, interface)]
  #
  #
  # class phase(emmo.continuum):
  #   """A phase is a continuum in which properties are homogeneous and can
  #   have different state of matter."""
  #   is_a = [emmo.has_property.exactly(1, stiffness_tensor),
  #           emmo.has_property.exactly(1, plasticity)]
  #
  #
  # class rve(emmo.continuum):
  #   """Representative volume element.  The minimum volume that is
  #   representative for the system in question."""
  #   is_a = [emmo.has_spatial_direct_part.only(phase | boundary)]
  #
  #
  # class welded_component(emmo.component):
  #   """A welded component consisting of two materials welded together
  #   using a third welding material.  Hence it has spatial direct
  #   parts 3 materials and two boundaries."""
  #   is_a = [
  #     emmo.has_spatial_direct_part.exactly(3, emmo.material),
  #     emmo.has_spatial_direct_part.exactly(2, boundary),
  #     emmo.has_property.exactly(1, load_curve)]

    #
    # Models
    # ======

  # ===========================
  # class has_unit(emmo.has_part):
  #   """Associates a unit to a property."""
  #   pass
  #
  #
  # class is_unit_for(emmo.is_part_of):
  #   """Associates a property to a unit."""
  #   inverse_property = has_unit
  #
  #
  # class has_type(emmo.has_convention):
  #   """Associates a type (string, number...) to a property."""
  #   pass

  #   class integer(emmo.number):
  #     pass
  #
  #
  # class real(emmo.number):
  #   pass
  #
  # class is_type_of(emmo.is_convention_for):
  #   """Associates a property to a type (string, number...)."""
  #   inverse_property = has_type
  #
  # class meter(emmo.measurement_unit):
  #   label = ['m']

  class VAR(emmo.physical_quantity):
    is_a = [has_unit.exactly(1, meter),
                has_type.exactly(3, real)]
    pass

  class is_function_of(VAR >> VAR):
    pass



a = VAR("a")
b = VAR("b")
c = VAR("c")

a.is_function_of = [onto.b, onto.c]

onto.sync_attributes()

sync_reasoner_pellet([onto])

owlfile = "play.owl"

onto.save_me(owlfile)

print(a)
print(a.is_function_of)
print("end")
