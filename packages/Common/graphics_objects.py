#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 graph object resources
===============================================================================

The graph objects are used in the ModelComposer and defined based on a basic structure stored in
gaph_objects_ini.json
and edited in GraphComponentenEditor

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
from collections import OrderedDict
from copy import copy
from copy import deepcopy

from PyQt5 import QtGui

from Common.common_resources import ARC_COMPONENT_SEPARATOR
from Common.common_resources import M_None
from Common.common_resources import M_any
from Common.common_resources import getData
from Common.qt_resources import PEN_STYLES

NAMES = {
        "node"                 : "node_simple",
        "branch"               : "node_composite",
        "panel"                : "node_viewed",
        "connector"            : "connector",
        "intraface"            : "node_intraface",
        "interface"            : "node_interface",
        "reservoir"            : "constant",
        "parent"               : "ancestor",
        "sibling"              : "sibling",
        "connection"           : "arc_edge",
        "left panel"           : "pane_ancestors",
        "right panel"          : "pane_siblings",
        "root"                 : "root",
        "name"                 : "name",
        "network"              : "network",
        "named_network"        : "named_network",
        "property"             : "property",
        "tail"                 : "tail",
        "head"                 : "head",
        "arc info knot" : "info_knot",
        "elbow"                : "knot",
        "token"                : "token",
        "indicator token"      : "indicator_dot",  # indicators for tokens
        "indicator typed token": "indicator_text",  # indicators for typed_tokens
        }

LOCATION_PARAMETERS = {
        "arc_node_gap_factor": 0.8,
        "token_indicators"   : {
                "x" : -10,
                "y" : -15,
                "dx": 5,
                "dy": 0
                },
        "ancestor_spacing"   : 50,
        "sibling_spacing"    : 50,
        "ancestor_offset"    : 20,
        "sibling_offset"     : 20,
        "connector_offset"   : 50
        }

TOOLTIP_TEMPLATES = {
        "nodes"    : '<b> capacity: <br>%s - %s <b><br>%s <br>%s',
        "intraface": '<b> intraface: <br>%s - %s <b><br>%s <br> <b> %s - %s<b>',
        "arc"      : '<b>arc: <br> %s - %s <b><br>%s <br>%s <br>%s - %s ',
        "ancestor" : '<b> %s',  # name
        "sibling"  : '<b> %s',  # name
        }


class GraphObjectError(Exception):
  def __init__(self, phase, graphics_object, decoration, application, state):
    print("object error [phase] %s, [graphics_object] %s, [decoration] %s, [application] %s, [state] %s"
          % (phase, graphics_object, decoration, application, state))


# base objects
def String(s=M_None):
  return str(s)


def Boolean(m=True):
  return bool(m)


def List(l):
  return list(l)


def Value(w):
  return int(w)


def Colour(r=255, g=255, b=255, a=100):
  return int(r), int(g), int(b), int(a)


def ID(ID=None):  # must blow if it is not defined
  return ID


class BaseObject(dict):
  def __init__(self):
    super().__init__()
    self["position_x"] = Value(0)
    self["position_y"] = Value(0)
    self["layer"] = String("mainPanel")
    self["movable"] = Boolean(False)
    self["action"] = List([])


class EllipseData(BaseObject):
  def __init__(self):
    BaseObject.__init__(self)
    self["width"] = Value(10)
    self["height"] = Value(10)
    self["colour"] = Colour()


class PanelData(BaseObject):
  def __init__(self):
    BaseObject.__init__(self)
    self["width"] = Value(100)
    self["height"] = Value(100)
    self["colour"] = Colour()


class LineData(BaseObject):
  def __init__(self):
    BaseObject.__init__(self)
    self["style"] = String("no pen")
    self["width"] = Value(2)
    self["colour"] = Colour()


class TextData(BaseObject):
  def __init__(self):
    BaseObject.__init__(self)


class NetworkData(dict):
  def __init__(self):
    super().__init__()
    self["colour"] = Colour()


class TokenData(dict):
  def __init__(self):
    super().__init__()
    self["colour"] = Colour()


class IndicatorDot(EllipseData):
  def __init__(self):
    EllipseData.__init__(self)

    self["shape"] = "ellipse"
    self["position_x"] = Value(10)
    self["position_y"] = Value(10)
    self["layer"] = String("text")
    self["movable"] = Boolean(False)
    self["action"] = List([])
    self["width"] = Value(10)
    self["height"] = Value(10)
    self["colour"] = Colour(100, 0, 100, 255)


class IndicatorText(TextData):
  def __init__(self):
    TextData.__init__(self)

    self["shape"] = "text"


class NetworkDataObjects(dict):
  def __init__(self, networks, connection_networks):
    super().__init__()
    for nw in networks:
      self[nw] = deepcopy(NetworkData())
    for nw in connection_networks:
      self[nw] = deepcopy(NetworkData())

  def setData(self, network, value):
    # print("debugging -- network set ", value)
    self[network]["colour"] = value

  def getData(self, network):
    # print("debugging -- network get ", self[network]["colour"])
    return self[network]["colour"]

  def makeBrushes(self):
    BRUSHES = {}
    for nw in self:
      red, green, blue, ar = self[nw]["colour"]
      BRUSHES[nw] = QtGui.QBrush(QtGui.QColor(red, green, blue, ar))
    return BRUSHES


class NamedNetworkDataObjects(dict):
  def __init__(self, networks):
    super().__init__()
    self["network__named_network"] = {}
    for nw in networks:
      name = "A-%s" % nw
      self["network__named_network"][nw] = [name]
      self[name] = NetworkData()

  def updateWithData(self, data):
    for n_nw in data:
      if n_nw == "network__named_network":
        self["network__named_network"].update(data["network__named_network"])
      else:
        self[n_nw] = data[n_nw]

  def add(self, network, name):
    self["network__named_network"][network].append(name)
    self[name] = NetworkData()

  def remove(self, network, name):
    no_named_networks = len(self["network__named_network}"][network])
    if no_named_networks == 1:
      return False
    self["network__named_network"][network].remove(name)
    del self[name]
    return True

  def rename(self, network, old_name, new_name):
    self["network__named_network"][network].remove(old_name)
    self["network__named_network"][network].append(new_name)

    value = self[old_name]
    self[new_name] = value
    del self[old_name]
    pass

  def listOfNamedNetworksAll(self):
    l = []
    for nw in self["network__named_network"]:
      l.extend(self["network__named_network"][nw])
    l.append("network__named_network")
    return l

  def listOfNamedNetworksPerNetwork(self, network):
    return self["network__named_network"][network]

  def indexForNamedNetwork(self, network, name):
    list_named_networks = self["network__named_network"][network]
    index = list_named_networks.index(name)
    return index

  def setColour(self, named_network, colour):
    print("network set ", colour)
    self[named_network]["colour"] = colour

  def getColour(self, named_network):
    # print("debugging -- network get ", self[named_network]["colour"])
    return self[named_network]["colour"]

  def makeBrush(self, named_network):
    red, green, blue, ar = self[named_network]["colour"]
    brush = QtGui.QBrush(QtGui.QColor(red, green, blue, ar))
    return brush

  def makeBrushes(self):
    BRUSHES = {}
    for nw in self["network__named_network"]:
      for n_nw in self["network__named_network"][nw]:
        BRUSHES[n_nw] = self.makeBrush(n_nw)
    return BRUSHES


class TokenDataObjects(dict):
  def __init__(self, tokens):
    super().__init__()
    for token in tokens:
      self[token] = deepcopy(TokenData())

  def setData(self, token, value):
    print("token set ", value)
    self[token]["colour"] = value

  def getData(self, token):
    print("token get ", self[token]["colour"])
    return self[token]["colour"]

  def makeBrushes(self):
    BRUSHES = {}
    for nw in self:
      red, green, blue, ar = self[nw]["colour"]
      BRUSHES[nw] = QtGui.QBrush(QtGui.QColor(red, green, blue, ar))
    return BRUSHES


DATA_STRUCTURE = {
        NAMES["network"]: Colour(),
        "ellipse"       : EllipseData(),
        "panel"         : PanelData(),
        "line"          : LineData(),
        "text"          : TextData(),
        }

STRUCTURES_Graph_Item = {}

STRUCTURES_Graph_Item[NAMES["panel"]] = {
        NAMES["root"]       : "panel",
        NAMES["left panel"] : "panel",
        NAMES["right panel"]: "panel"
        }

STRUCTURES_Graph_Item[NAMES["connector"]] = {
        NAMES["root"]: "ellipse",
        NAMES["name"]: "text"
        }

STRUCTURES_Graph_Item[NAMES["node"]] = {
        NAMES["root"]         : "ellipse",
        NAMES["name"]         : "text",
        NAMES["network"]      : "ellipse",
        NAMES["named_network"]: "ellipse"
        }

STRUCTURES_Graph_Item[NAMES["branch"]] = {
        NAMES["root"]: "panel",
        NAMES["name"]: "text",
        }

STRUCTURES_Graph_Item[NAMES["intraface"]] = {
        NAMES["root"]: "panel",
        NAMES["name"]: "text",
        }

STRUCTURES_Graph_Item[NAMES["interface"]] = {
        NAMES["root"]: "ellipse",
        NAMES["name"]: "text",
        }

STRUCTURES_Graph_Item[NAMES["elbow"]] = {
        NAMES["root"]: "ellipse",
        }

STRUCTURES_Graph_Item[NAMES["arc info knot"]] = {
        NAMES["root"]: "ellipse",
        NAMES["name"]: "text",
        }

STRUCTURES_Graph_Item[NAMES["parent"]] = {
        NAMES["root"]: "ellipse",
        NAMES["name"]: "text",
        }

STRUCTURES_Graph_Item[NAMES["sibling"]] = {
        NAMES["root"]: "ellipse",
        NAMES["name"]: "text",
        }

STRUCTURES_Graph_Item[NAMES["connection"]] = {
        NAMES["root"]: "line",
        NAMES["head"]: "ellipse",
        NAMES["tail"]: "ellipse"
        }

# -------------------------------------------------------------------------
# RULE: The composer has three main layers: topology, tokens, typed_tokens
# TODO the M_None state can be deleted but this carry through a lot.
# RULE: first in the list is the default state

STATES = OrderedDict()
STATES["topology"] = {
        "nodes": ["enabled", "blocked", "selected"],
        "arcs" : ["enabled", "selected", "open"]
        }
STATES["token_topology"] = {
        "nodes": ["enabled", "selected", "blocked"],  # hash was typed_tokens
        "arcs" : ["enabled"]
        }
STATES["equation_topology"] = {
        "nodes": ["enabled", "selected"],
        "arcs" : ["enabled", "selected"]
        }
STATE_OBJECT_COLOURED = "enabled"
DEFAULT_PHASE = "topology"
# -------------------------------------------------------------------------

DEFAULT_STATES = OrderedDict()
for phase in STATES:
  DEFAULT_STATES[phase] = {}
  DEFAULT_STATES[phase]["nodes"] = STATES[phase]["nodes"][0]
  DEFAULT_STATES[phase]["arcs"] = STATES[phase]["arcs"][0]

PHASES = list(STATES.keys())

GRAPHICS_OBJECTS = sorted(STRUCTURES_Graph_Item.keys())

NODES = [NAMES["node"],
         NAMES["branch"],
         NAMES["intraface"],
         NAMES["interface"],
         # NAMES["boundary"],
         # NAMES["panel"],
         NAMES["connector"],
         NAMES["parent"],
         NAMES["sibling"]]
KNOTS = [NAMES["elbow"]]
ARCS = [NAMES["connection"]]

INTERFACE = [NAMES["interface"], NAMES["connection"]]
INTRAFACE = [NAMES["intraface"], ]

OBJECTS_nodes_with_states = [NAMES["node"],
                             NAMES["intraface"],
                             NAMES["interface"], ]
OBJECTS_arcs_with_states = [NAMES["connection"]]
OBJECTS_with_state = OBJECTS_nodes_with_states + OBJECTS_arcs_with_states

OBJECTS_without_state = [NAMES["branch"],
                         NAMES["elbow"],
                         NAMES["parent"],
                         NAMES["sibling"],
                         NAMES["connector"],
                         NAMES["panel"]]

DECORATIONS_with_state = ["root",
                          # "head",
                          # "tail"
                          ]
DECORATIONS_with_application = ["root"]

OBJECTS_with_application = [NAMES["node"],
                            NAMES["connection"],
                            NAMES["interface"],
                            NAMES["intraface"]
                            ]

OBJECTS_not_move = [NAMES["panel"],
                    NAMES["left panel"],
                    NAMES["right panel"]]

LAYERS = {
        "mainPanel"    : 0,
        "sidePanel"    : 5,
        "network"      : 10,
        "named_network": 15,
        "arc"          : 20,
        "knot"         : 30,
        "node"         : 40,
        "property"     : 50,
        "text"         : 60,
        }

OBJECTS_changing_position = [NAMES["node"],
                             NAMES["branch"],
                             NAMES["intraface"],
                             NAMES["interface"],
                             # NAMES["boundary"],
                             NAMES["elbow"]]

OBJECTS_colour_defined_separate = [NAMES["network"], NAMES["named_network"]]


class GraphObject():
  def __init__(self, **kwargs):
    self.__dict__ = kwargs


class GraphDataObjects(OrderedDict):
  """
  Factory for data objects for the graphical representation of the topology and its hierarchical representation
  Enables tailoring of the objects to different structures and applications
   - phase -- editor phase
   - graphics_object -- an identifier for each graphic object being used in the graphical representation
                        also referred to as root object as decorations are added
   - decoration -- decorations added to the root object
   - state -- object state

   Graphic objecs may have applications and states and activities associated with them
   Thus different combinations are generated according to membership to the different groups.
   Objects with or without...

   """

  def __init__(self, dict_application_node_types,
               application_arc_types):

    print("debugging")
    for phase in PHASES:
      self[phase] = {}
      for graphics_object in GRAPHICS_OBJECTS:
        self[phase][graphics_object] = {}
        decorations = STRUCTURES_Graph_Item[graphics_object]
        for decoration in decorations:
          shape = STRUCTURES_Graph_Item[graphics_object][decoration]
          self[phase][graphics_object][decoration] = {}
          # RULE : only root objects and a selected list of components carry states (nodes, arcs, head, tail)
          if (decoration in DECORATIONS_with_state) and (graphics_object in OBJECTS_with_state):
            # print("debugging -- object with state", graphics_object, decoration)
            pass
            if graphics_object != NAMES["connection"]:
              applications = dict_application_node_types[graphics_object]
              for application in applications:
                self[phase][graphics_object][decoration][application] = {}
                states = STATES[phase]["nodes"]
                for state in states:
                  self[phase][graphics_object][decoration][application][state] = deepcopy(DATA_STRUCTURE[shape])
            else:
              for application in application_arc_types:
                self[phase][graphics_object][decoration][application] = {}
                states = STATES[phase]["arcs"]

                for state in states:
                  self[phase][graphics_object][decoration][application][state] = deepcopy(DATA_STRUCTURE[shape])


          else:
            application = M_None
            state = M_None
            self[phase][graphics_object][decoration][application] = {}
            self[phase][graphics_object][decoration][application][state] = deepcopy(DATA_STRUCTURE[shape])

    print("debugging -- setting up graph objects")

  def setData(self, what, value, phase, root_object, decoration, application, state):
    if what != "action":
      if state != M_None:
        state = STATE_OBJECT_COLOURED  # RULE: only one state indicates the state
    print(
            "put data -- phase : %s ,root_object: %s, decoration: %s, application: %s , state: %s, what: %s, "
            "value : %s"
            % (phase, root_object, decoration, application, state, what, value))
    #
    # NOTE: there is a nasty exception showing when having no inter networks.
    self.__makeData(phase, root_object, decoration, application, state)
    self[phase][root_object][decoration][application][state][what] = value
    print(
            "did put data -- phase : %s ,root_object : %s, decoration : %s, application ; %s , state : %s, what : %s, "
            "value: %s"
            % (phase, root_object, decoration, application, state, what, value))
    if what == "action":
      print("debugging setting actions")

  def __makeData(self, phase, root_object, decoration, application, state):
    if phase not in self:
      self[phase] = {}
    if root_object not in self[phase]:
      self[phase][root_object] = {}
    if decoration not in self[phase][root_object]:
      self[phase][root_object][decoration] = {}
    if application not in self[phase][root_object][decoration]:
      self[phase][root_object][decoration][application] = {}
    if state not in self[phase][root_object][decoration][application]:
      self[phase][root_object][decoration][application][state] = {}

  def getData(self, phase, root_object, decoration, application, state):

    if decoration == NAMES["indicator token"]:
      data = IndicatorDot()
      return data

    elif decoration == NAMES["indicator typed token"]:
      data = IndicatorText()
      return data

    if phase == M_any:
      phase = DEFAULT_PHASE

    # if root_object not in OBJECTS_with_application:
    #   application = M_None
    # elif decoration not in DECORATIONS_with_application:
    #   application = M_None
    if root_object not in OBJECTS_with_state:
      state = M_None
    elif decoration not in DECORATIONS_with_state:
      state = M_None

    # if state not in self[phase][root_object][decoration][application]:
    #   state = M_None

    if root_object not in OBJECTS_with_application:
      application = M_None
    else:
      if decoration not in DECORATIONS_with_application:
        application = M_None

    # Note: safety valve:
    if application not in self[phase][root_object][decoration]:
      # self.__makeData(phase, root_object, decoration, application, state)
      print(" warning >>> should not come here")
    try:
      a = self[phase][root_object][decoration][application][state]
    except:
      # self.__makeData(phase, root_object, decoration, application, state)
      print("exception occurred")
    return self[phase][root_object][decoration][application][state]

  def makeBrushesAndPens(self):
    PENS = {}
    BRUSHES = {}
    for p in self:
      for r in self[p]:
        for d in self[p][r]:
          for a in self[p][r][d]:
            for s in self[p][r][d][a]:
              obj = self[p][r][d][a][s]
              if "colour" in obj:
                red, green, blue, ar = obj["colour"]
                if "style" in obj:
                  # print("                   pen ", r,d,a,s)
                  pen = QtGui.QPen(QtGui.QColor(red, green, blue, ar))
                  pen.setStyle(PEN_STYLES[obj["style"]])
                  pen.setWidth(obj["width"])
                  PENS[str([p, r, d, a, s])] = pen
                else:
                  # print("                 brush ", r,d,a,s)
                  BRUSHES[str([p, r, d, a, s])] = QtGui.QBrush(QtGui.QColor(red, green, blue, ar))

    return PENS, BRUSHES

  def getActiveObjects(self):
    active_objects = {}
    for p in PHASES:
      active_objects[p] = []
      for r in GRAPHICS_OBJECTS:
        decorations = STRUCTURES_Graph_Item[r]
        for d in decorations:
          for a in self[p][r][d]:
            # print("[p][r][d]", p,r,d, self[p][r][d])
            for s in self[p][r][d][a]:
              if self[p][r][d][a][s]["action"] != []:
                active_objects[p].append((r, d, a, s))
    return active_objects

  def getActiveObjectsRootDecorationToken(self):
    active_objects = {}
    for p in PHASES:
      obj = []
      for r in GRAPHICS_OBJECTS:
        decorations = STRUCTURES_Graph_Item[r]
        for d in decorations:
          for a in self[p][r][d]:
            token = a.split(ARC_COMPONENT_SEPARATOR)[0]
            for s in self[p][r][d][a]:
              if self[p][r][d][a][s]["action"] != []:
                obj.append((r, d, token))

      # print("object", obj)
      a = set(obj)
      active_objects[p] = sorted(a)
    return active_objects

  def getActiveObjectsRootDecoration(self):
    active_objects = {}
    for p in PHASES:
      obj = []
      for r in GRAPHICS_OBJECTS:
        decorations = STRUCTURES_Graph_Item[r]
        for d in decorations:
          for a in self[p][r][d]:
            for s in self[p][r][d][a]:
              if self[p][r][d][a][s]["action"] != []:
                obj.append((r, d))

      # print("object", obj)
      a = set(obj)
      active_objects[p] = sorted(a)
    return active_objects

  def getActiveObjectsRootDecorationState(self):
    if "ActiveObjectsRootDecorationState" not in self:
      active_objects = {}
      for p in PHASES:
        obj = []
        for r in GRAPHICS_OBJECTS:
          decorations = STRUCTURES_Graph_Item[r]
          for d in decorations:
            for a in self[p][r][d]:
              for s in self[p][r][d][a]:
                if self[p][r][d][a][s]["action"] != []:
                  obj.append((r, d, s))

        # print("object", obj)
        a = set(obj)
        active_objects[p] = sorted(a)
      self["ActiveObjectsRootDecorationState"] = active_objects

    return self["ActiveObjectsRootDecorationState"]

  def getActiveObjectRootDecorationState(self, phase, graphics_root_object,
                                         decoration, application, state):
    active_objects = self[phase]
    a = M_None
    s = M_None

    if graphics_root_object == NAMES["intraface"]:
      # print("debugging -- intraface")
      pass

    if graphics_root_object in active_objects:
      if decoration in active_objects[graphics_root_object]:
        if application in active_objects[graphics_root_object][decoration]:
          a = application
        else:
          a = M_None
        try:
          if state in active_objects[graphics_root_object][decoration][a]:
            s = state
          else:
            s = M_None
        except:
          print("get active object -- problem",
                "\n-phase               : ", phase,
                "\n-graphics_root_object: ", graphics_root_object,
                "\n-decoration          : ", decoration,
                "\n-application         : ", application,
                "\n-state               : ", state)
          # ,
          #       '\n1', phase, '\n2', graphics_root_object, '\n3',decoration, '\n4',application, '\n5',state)
      elif decoration in [NAMES["indicator token"], NAMES["indicator typed token"]]:  # RULE: this is the indicator
        a = M_None
        s = M_None

    return graphics_root_object, decoration, a, s


def getGraphData(networks,
                 list_interconnection_networks,
                 list_intraconnection_networks,
                 list_NetworkNodeObjects,
                 list_IntraNodeObjects,
                 list_InterNodeObjects,
                 list_arcObjects,
                 tokens,
                 graph_resource_file_spec):
  # get graph data
  dict_application_node_types = {NAMES["node"]     : list_NetworkNodeObjects,
                                 NAMES["intraface"]: list_IntraNodeObjects,
                                 NAMES["interface"]: list_InterNodeObjects}

  application_arc_types = list_arcObjects
  DATA = GraphDataObjects(dict_application_node_types,
                          application_arc_types)
  list_connections = copy(list_interconnection_networks)
  list_connections.extend(list_intraconnection_networks)

  NETWORK = NetworkDataObjects(networks, list_connections)
  TOKENS = TokenDataObjects(tokens)
  STATE_colours_set = set()
  for phase in STATES:
    for component in STATES[phase]:
      for state in STATES[phase][component]:
        STATE_colours_set.add(state)

  state_colours = {}
  for s in sorted(STATE_colours_set):
    state_colours[s] = Colour()  # colour data

  # TODO -- cleaning operation is missing
  if os.path.exists(graph_resource_file_spec):
    data_dict = getData(graph_resource_file_spec)
    mouse_data = data_dict["data"]

    for p in DATA:
      for r in DATA[p]:
        for d in DATA[p][r]:
          shape = STRUCTURES_Graph_Item[r][d]  # ["decoration"][d]
          for a in DATA[p][r][d]:
            for s in DATA[p][r][d][a]:
              try:
                obj = deepcopy(DATA_STRUCTURE[shape])
                obj.update(mouse_data[p][r][d][a][s])
                DATA[p][r][d][a][s] = obj  # mouse_data[p][r][d][a][s]
                # print(p, r, d, a, s, "-- OK")
              except:
                print(p, r, d, a, s, "-- x")
                pass

    # udate and clean out
    if "networks" in data_dict:
      NETWORK.update(data_dict["networks"])
    delete_me = set()
    for nw in NETWORK:
      if (nw in networks) or (nw in list_connections):  # list_interconnection_networks):
        pass
      else:
        delete_me.add(nw)
        print("delete network:", nw)
    for nw in delete_me:
      del NETWORK[nw]

    if "tokens" in data_dict:
      TOKENS.update(data_dict["tokens"])
    delete_me = set()
    for token in TOKENS:
      if token not in tokens:
        delete_me.add(token)
        print("delete token  :", token)
    for token in delete_me:
      del TOKENS[token]

    state_colours = {}
    for s in sorted(STATE_colours_set):
      state_colours[s] = Colour()  # colour data
      if "states" in data_dict:
        state_colours.update(data_dict["states"])

  return NETWORK, TOKENS, DATA, state_colours
