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
__since__ = "10.09.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from emmo import get_ontology

from owlready2 import default_world  # ,get_ontology
from owlready2 import onto_path
from owlready2 import set_render_func
from owlready2 import sync_reasoner_pellet
from owlready2 import Ontology
from owlready2 import Nothing, ObjectProperty, Thing


import itertools
import inspect



class NoSuchLabelError(LookupError):
    """Error raised when a label cannot be found."""
    pass

def render_func(entity):
    name = entity.label[0] if len(entity.label) == 1 else entity.name
    return "%s.%s" % (entity.namespace.name, name)
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
    #'properties',
)

def get_ontology(base_iri='emmo-inferred.owl', verbose=False):
    """Returns a new Ontology from `base_iri`.

    If `verbose` is true, a lot of dianostics is written.
    """
    if (not base_iri.endswith('/')) and (not base_iri.endswith('#')):
        base_iri = '%s#' % base_iri
    if base_iri in default_world.ontologies:
        onto = default_world.ontologies[base_iri]
    else:
        onto = Ontology(default_world, base_iri)
    onto._verbose = verbose
    return onto

class Ontology(Ontology) : #, OntoGraph, OntoVocab):
    """A generic class extending owlready2.Ontology.
    """
    def __getitem__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name):
        attr = super().__getattr__(name)
        if not attr:
            attr = self.get_by_label(name)
        return attr

    def __dir__(self):
        """Include classes in dir() listing."""
        f = lambda s: s[s.rindex('.') + 1: ] if '.' in s else s
        s = set(object.__dir__(self))
        for onto in [get_ontology(uri) for uri in self._namespaces.keys()]:
            s.update([f(repr(cls)) for cls in onto.classes()])
        return sorted(s)

    def __objclass__(self):
        # Play nice with inspect...
        pass

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
        #label = label.replace("-", "") FLB: problem with - in variable
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
        l = [cls for cls in itertools.chain.from_iterable(
            getattr(self, category)() for category in categories)
             if hasattr(cls, '__name__') and cls.__name__ == label]
        if len(l) == 1:
            return l[0]
        elif len(l) > 1:
            raise NoSuchLabelError('There is more than one Python class with '
                                   'name %r' % label)
        # Check imported ontologies
        for onto in self.imported_ontologies:
            onto.__class__ = self.__class__  # magically change type of onto
            try:
                return onto.get_by_label(label)
            except NoSuchLabelError:
                pass
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
                cls.label.append(cls.__name__)
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
    #     """ Recursive help function to number_of_generations(), return distance between a ancestor-descendant pair (n+1). """
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
    #         distances[ancestor] = self.number_of_generations(cls1, ancestor) + self.number_of_generations(cls2, ancestor)
    #     return [ancestor for ancestor, distance in distances.items() if distance == min(distances.values())]



onto_path.append(("../emmo/rdfxml"))
emmo = get_ontology("emmo-properties.owl") #emmo-all-inferred.owl")
namespace = emmo.get_namespace(emmo.base_iri)
print("emmon", emmo)
emmo.load()


onto = get_ontology("play.owl", )
onto.imported_ontologies.append(emmo)

onto.base_iri = emmo.base_iri

print("base iri : ", default_world.ontologies)
print("classes : ", list(emmo.classes()))
print("individuals :", list(emmo.individuals()))
print("object_properties :", list(emmo.object_properties()))
print("properties :", emmo.search(iri="variable"))
print("base iri   :", emmo.base_iri)
print("base iri   :", onto.base_iri)

classe_labels = []
classes_dict = {}

print("\n ========= classes by label")
for i in emmo.classes():
  classe_labels.extend(i.label)
  print(i)

print("\n ======= dir")
for i in list(dir(emmo.property)):
    print(i)


print("variable" in classe_labels)
print(onto.physical_quantity)

print(emmo.get_python_module)

with onto:

    class VAR(emmo.physical):
        pass
    class Par(emmo.physical):
        pass
    class is_function_of(VAR >> Par):
        pass

    # class Is_Part(emmo.is_part_of):
    #     pass

a = VAR("a")
b = Par("b")
c = Par("c")


a.is_function_of=['b','c']


# onto.sync_attributes()

sync_reasoner_pellet([onto])

print("variable:", a)
print("variable:", a.is_function_of)
print("variable:", b)
print("variable:", c)
onto.save("play.owl")

print("end")