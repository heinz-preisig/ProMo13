#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
objects for automata

Automata control the user interface of the ModelComposer
===============================================================================
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL planned -- until further notice for internal Bio4Fuel & MarketPlace use only"
__version__ = "5.04 or later"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
from collections import OrderedDict

from Common.common_resources import getData
from Common.common_resources import M_None
from Common.graphics_objects import PHASES

BUTTONS = ["left", "right"]

DEDICATED_KEY = {
        'reset': 'Key_Escape'
        }

# RULE: the first state must be reachable from the key automaton
# Note: this defines the states of the automata

GRAPH_EDITOR_STATES = OrderedDict()
GRAPH_EDITOR_STATES["topology"] = ["explore", "insert", "connect_arc", "re-connect_arc", "explode", "delete", ]
GRAPH_EDITOR_STATES["token_topology"] = ["inject"]
GRAPH_EDITOR_STATES["equation_topology"] = ["roam", "instantiate" ]


class MouseAutomatonEntry(dict):
  def __init__(self, state, output, cursor):
    super().__init__()
    for event in BUTTONS:
      self[event] = {}
      self[event]["state"] = state[event]
      self[event]["output"] = output[event]
    self["cursor"] = cursor


class KeyAutomatonEntry(dict):
  def __init__(self, state, output):
    super().__init__()
    self["state"] = state
    self["output"] = output


class MouseAutomaton(dict):
  """
  active object information :  graphics_object decorator application state
  """

  def __init__(self, active_objects, editor_states):
    """
    [editor_state][object_str][button]
    [editor_state][object_str]["cursor"]
    :param active_objects:
    :param editor_states:
    """

    super().__init__()

    for editor_state in editor_states:
      self[editor_state] = {}
      for object in active_objects:
        object_str = str(object)
        self[editor_state][object_str] = {}
        output = {}
        next_state = {}
        for button in BUTTONS:
          output[button] = M_None
          next_state[button] = M_None
        cursor = M_None
        self[editor_state][object_str] = MouseAutomatonEntry(next_state, output, cursor)

    self.printMe()

  def setOutput(self, object_str, state, button, output):
    self[object_str][state][button][0] = output

  def setNextState(self, object_str, state, button, next_state):
    self[object_str][state][button][1] = next_state

  def setCursor(self, object_str, state, button, cursor):
    self[object_str][state][button][2] = cursor

  def setAutomaton(self, old):
    for object in old:
      if object in self:
        self[object].update(old[object])

  def printMe(self):
    print("\nBlank automaton")
    for editor_state in self:
      for object in self[editor_state]:
        print("state :%s, object :%s, ---- item %s" % (editor_state, object, self[editor_state][object]))


class KeyAutomaton(dict):
  def __init__(self):
    super().__init__()
    for key in DEDICATED_KEY:
      next_state = M_None
      output = M_None
      self[key] = KeyAutomatonEntry(next_state, output)

  def setAutomaton(self, old):
    delete = []
    for key in self:
      if key not in old:
        delete.append(key)
    for key in delete:
      del self[key]
    self.update(old)

  def addEntry(self):
    self[M_None] = KeyAutomatonEntry(M_None, M_None)


def getAutomata(file_spec, active_objects_all_phases):
  mouse_automata = {}
  key_automata = {}
  for phase in PHASES:
    print("\nphase", phase)
    editor_states = GRAPH_EDITOR_STATES[phase]
    mouse_automata[phase] = MouseAutomaton(active_objects_all_phases[phase], editor_states)
    key_automata[phase] = KeyAutomaton()

  if os.path.exists(file_spec):
    for phase in PHASES:
      automata = getData(file_spec)
      if phase in automata["mouse"]:
        mouse_automata[phase].setAutomaton(automata["mouse"][phase])
      if phase in automata["key"]:
        key_automata[phase].setAutomaton(automata["key"][phase])

  return mouse_automata, key_automata
