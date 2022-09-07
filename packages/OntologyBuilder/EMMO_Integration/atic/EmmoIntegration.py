#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
EMMO integration to base editor
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2019. 01. 16"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

from graphviz import Digraph

from Common.common_resources import walkDepthFirstFnc

thisdir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(1, os.path.abspath(os.path.join('../../../ModelRepository/ontology-master/python/')))
# print(sys.path)

from emmo import  get_ontology

from Common.treeid import ObjectTree


def makeTaggedTree(onto, id):
  # BFS(v)
  #   let neighbours be the set of all  neighbours of  vertex  v
  #   for neighbor in neighbors:
  #     if neighbor is not visited:
  #       visit neighbour
  #   for neighbor in neighbors:
  #     recurisvely call BFS(neighbor)

  Tree = ObjectTree("state")
  stack = ["state"]
  while stack:
    cur_node = stack[0]
    stack = stack[1:]
    children = getChildren(onto, cur_node)
    stack.extend(children)

    for child in children:
      Tree.addChildtoNode(child, cur_node)

  return Tree


def getChildren(object, name):
  k = object.__getattr__(name)
  m = k.subclasses()
  if m:
    children = []
    for s in m:
      children.append(str(s).split('.')[-1])
    return children
  else:
    return []


def makeDotGraph(tree):
  file_name = os.path.join(thisdir, "emmo_old")
  graph_attr = {}
  graph_attr["nodesep"] = "1"
  graph_attr["ranksep"] = "0.3"
  # graph_attr.edge_attr["color"] = "blue"
  graph_attr["splines"] = "false"  # ""polyline"
  edge_attr = {}
  graph = Digraph('EMMO tree', filename=file_name)
  graph.node("emmo_old", "emmo_old")
  parent = "emmo_old"
  for node in walkDepthFirstFnc(tree, "state"):
    if node != "state":
      parent = tree[node]["ancestors"][0]
    graph.node(node)
    graph.edge(parent, node)

  graph.view()


class Node():
  def __init__(self, name):
    self.name = name
    self.children = []
    self.ancestors = []

  def addChildren(self, children):
    self.children = children


if __name__ == '__main__':
  onto = get_ontology('emmo.owl')
  onto.load()
  # onto.sync_reasoner()

  state = onto.state
  subclasslist = list(onto.state.subclasses())
  print(subclasslist)

  Tree = makeTaggedTree(onto, "state")
  print(Tree.makeTaggedTree())

  makeDotGraph(Tree.makeTaggedTree())
