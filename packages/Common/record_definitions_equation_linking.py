
"""
===============================================================================
 define data record structures
===============================================================================

This program is part of the ProcessModelling suite

This extends the record structures definitions because of loop in intialisation
The intention is to bring this further up into an ontology

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "15.11.2020"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "7.00"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from copy import deepcopy

from Common.common_resources import ENTITY_OBJECT_SEPARATOR
from Common.common_resources import TEMPLATE_ENTITY_OBJECT, getData
# from Common.record_definitions import VariantRecord



def functionMakeObjectStringID(network, entity, variant):
  entity_str_ID = TEMPLATE_ENTITY_OBJECT % (network, entity, variant)
  return entity_str_ID

def functionGetObjectsFromObjectStringID(entity_str_ID):
  network, component, entity, variant = entity_str_ID.split(ENTITY_OBJECT_SEPARATOR)
  return network, component, entity, variant

class EntityBehaviour(dict):
  def __init__(self): #, entities):
    super().__init__()
    # for e in entities:
    #   self[e] = None

  def addVariant(self, entity_str_ID, data): #network, entity, variant, data):
    # entity_str_ID = functionMakeObjectStringID(network, entity, variant)

    # self[entity_str_ID] = VariantRecord(tree=data["tree"],
    #                                     nodes=data["nodes"],
    #                                     IDs= data["IDs"],
    #                                     root_variable = data["root_variable"],
    #                                     blocked_list = data["blocked"],
    #                                     buddies_list = data["buddies"])
    self[entity_str_ID] = deepcopy(data)

  def removeVariant(self, obj):
    # entity_str_ID = functionMakeObjectStringID(network, entity, variant)
    elements = obj.split(".")
    if elements[-1] == "base":
      reminder = obj.replace(".base","")
      del_list = []
      for o in self:
        if reminder in o:
          del_list.append(o)
      for e in del_list:
        del self[e]
      self[obj] = None
    else:
      del self[obj]


  def getRootVariableID(self, entity_str_ID):
    if self[entity_str_ID]:
      root_variable = int(self[entity_str_ID]["root_variable"])
      return root_variable
    else:
      return None

  def getRootEquationID(self, entity_str_ID):
    if self[entity_str_ID]:
      root_variable = int(self[entity_str_ID]["root_equation"])
      return root_variable
    else:
      return None

  def getVariantList(self, network_def, entity_def):
    variant_set = set()
    for entity_str_ID in self:
      network, entity, variant = functionGetObjectsFromObjectStringID(entity_str_ID)
      if network == network_def:
        if entity == entity_def:
          variant_set.add(variant)
    return sorted(variant_set)




  def getAllVariants(self):
    variant_set = set()
    for entity_str_ID in self:
      network, entity, variant = functionGetObjectsFromObjectStringID(entity_str_ID)
      variant_set.add(variant)
    return sorted(variant_set)


  def getEquationIDList(self, entity_str_ID ):
    equation_ID_list = []
    for n in self[entity_str_ID]["nodes"]:
      _label, ID = self[entity_str_ID]["nodes"][n].split("_")
      if _label == "equation":
        equation_ID_list.append(int(ID))
    return equation_ID_list

  def getBlocked(self, entity_str_ID):
    blocked_ID = []
    for ID in self[entity_str_ID]["blocked"]:
      blocked_ID.append(int(ID))
    return blocked_ID

# NOTE: moved to record_definitions -- did not work as it generated a loop.
class VariantRecord(dict):  # .............................................................. hash is global index_ID
  """
  Generates a 'variant' record being used to store base entity representations in the form of list of equations
  """
  def __init__(self, tree={}, nodes=[], IDs=[], root_variable=None, root_equation=None, blocked_list=[], buddies_list=[], to_be_inisialised=[]):
    super()
    self["tree"] = tree
    self["nodes"] = nodes
    self["IDs"] = IDs
    self["root_variable"] = root_variable
    self["root_equation"] = root_equation
    self["blocked"] = blocked_list
    self["buddies"]= buddies_list
    self["to_be_initialised"] = to_be_inisialised


def readVariableAssignmentToEntity(f):
  # f = FILES["variable_assignment_to_entity_object"] % self.ontology_name
  # loaded_entity_behaviours = getData(f)
  data = getData(f)
  if data:
    loaded_entity_behaviours = data["behaviours"]
    node_arc_associations = data["associations"]
    entity_behaviours = {}

    if loaded_entity_behaviours:
      for entity_str_ID in loaded_entity_behaviours:  # careful there may not be all entities at least during
        # developments
        if loaded_entity_behaviours[entity_str_ID]:
          dummy = VariantRecord()
          data = loaded_entity_behaviours[entity_str_ID]
          for atr in dummy:
            if atr not in data:
              data[atr] = None
          tree = {}
          for treeStrID in data["tree"]:
            tree[int(treeStrID)] = data["tree"][treeStrID]
          data["tree"] = tree

          nodes = {}
          for nodeStrID in data["nodes"]:
            nodes[int(nodeStrID)] = data["nodes"][nodeStrID]
          data["nodes"] = nodes


          entity_behaviours[entity_str_ID] = VariantRecord(tree=data["tree"],
                                                                nodes=data["nodes"],
                                                                IDs=data["IDs"],
                                                                root_variable=data["root_variable"],
                                                                blocked_list=data["blocked"],
                                                                buddies_list=data["buddies"],
                                                                to_be_inisialised=data["to_be_initialised"])
    return node_arc_associations, entity_behaviours
  else:
    return None, None


  #
  # def getEquationIDList(self, ):
  #   equation_ID_list = []
  #   for n in self["nodes"]:
  #     _label, ID = self["nodes"][n].split("_")
  #     if _label == "equation":
  #       equation_ID_list.append(ID)
  #
  #   return equation_ID_list

class NodeArcAssociations(dict):
  def __init__(self, networks, node_objects, arc_objects):
    super()
    for nw in networks:
      self[nw] = {}
      self[nw]["nodes"] = {}
      self[nw]["arcs"] = {}
      for n in node_objects[nw]:
        self[nw]["nodes"][n] = None
      for a in arc_objects[nw]:
        self[nw]["arcs"][a] = None