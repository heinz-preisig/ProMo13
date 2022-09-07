#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Generate dot graph for the base ontology
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 07. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])

from graphviz import Digraph
from PyPDF2 import PdfFileMerger
from PyQt5 import QtWidgets

from Common.common_resources import getData
from Common.common_resources import getOntologyName
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES


def walkTreeOnly(ontology, node, graph):
  children = ontology[node]["children"]
  if children:
    connector = node
    b_connector = connector + "c"
    graph.node(b_connector, "", shape="none", height="0", width="0")
    graph.edge(connector, b_connector, dir="none")
    for child in children:
      node_type = ontology[child]["type"]
      print(node_type)
      if node_type == "inter":
        color = "limegreen"
      elif node_type == "intra":
        color = "lightblue"
      else:
        color = "olive"
      graph.node(child, style="filled", color=color)
      graph.edge(b_connector, child)
      walkTreeOnly(ontology, child, graph)
  else:
    return


def makeTree(ontology, node, tree):
  children = ontology[node]["children"]
  if children:
    connector = node
    for child in children:
      # print(child)
      tree.append(child)
      makeTree(ontology, child, tree)
  else:
    return


def singleNodeOnly(ontology, network, graph, behaviour_nodes, structure_nodes):
  parent = network

  layer_1 = network + "behaviour"
  graph.node(layer_1, "behaviour", shape="diamond")
  graph.edge(parent, layer_1)
  node_style = "filled"
  for layer_2 in ontology[network]["behaviour"]:
    s_1_2 = layer_1 + layer_2
    graph.node(s_1_2, layer_2)
    graph.edge(layer_1, s_1_2)
    for layer_3 in ontology[network]["behaviour"][layer_2]:
      s_1_2_3 = s_1_2 + layer_3
      graph.node(s_1_2_3, layer_3)
      graph.edge(s_1_2, s_1_2_3)
      # for layer_4 in ontology[network]["behaviour"][layer_2][layer_3]:
      #   s_1_2_3_4 = s_1_2_3+layer_4
      node_style = "filled"
      s_test = "behaviour" + layer_2 + layer_3  # +layer_4    # without node
      if s_test not in behaviour_nodes:
        behaviour_nodes.append(s_test)
        node_color = "green"
        peripheries = "2"
      else:
        node_color = "greenyellow"
        peripheries = "1"

        # graph.node(s_1_2_3_4, layer_4, style=node_style, color= node_color, peripheries=peripheries)
        # graph.edge(s_1_2_3, s_1_2_3_4)

      graph.node(s_1_2_3, layer_3, style=node_style, color=node_color, peripheries=peripheries)
      # graph.edge(s_1_2, s_1_2_3)

  layer_1 = network + "structure"
  graph.node(layer_1, "structure", shape="diamond")
  graph.edge(parent, layer_1)
  for layer_2 in ontology[network]["structure"]:
    s_1_2 = layer_1 + layer_2
    graph.node(s_1_2, layer_2)
    graph.edge(layer_1, s_1_2)
    for layer_3 in ontology[network]["structure"][layer_2]:
      # if layer_3 :
      s_test = "structure" + layer_2 + layer_3
      if s_test not in structure_nodes:
        color = "pink3"
        peripheries = "2"
        structure_nodes.append(s_test)
      else:
        color = "pink"
        peripheries = "1"

      s_1_2_3 = s_1_2 + layer_3
      graph.node(s_1_2_3, layer_3, style=node_style, color=color, peripheries=peripheries)
      graph.edge(s_1_2, s_1_2_3)

      for layer_4 in ontology[network]["structure"][layer_2][layer_3]:
        s_1_2_3_4 = s_1_2_3 + layer_4
        node_style = "filled"
        # if layer_3 != "nature": #ontology[network]["structure"][layer_2][layer_3].__class__ == list:

        s_test = "structure" + layer_2 + layer_3 + layer_4  # without node
        if s_test not in structure_nodes:
          color = "pink3"
          peripheries = "2"
          structure_nodes.append(s_test)
        else:
          color = "pink"
          peripheries = "1"

        graph.node(s_1_2_3_4, layer_4, style=node_style, color=color, peripheries=peripheries)
        graph.edge(s_1_2_3, s_1_2_3_4)

        if type(ontology[network]["structure"][layer_2][layer_3]) is dict:
          s_1_2_3_4 = s_1_2_3 + layer_4
          graph.node(s_1_2_3_4, layer_4)
          # graph.edge(s_1_2_3, s_1_2_3_4)
          node_style = "filled"
          for layer_5 in ontology[network]["structure"][layer_2][layer_3][layer_4]:
            s_1_2_3_4_5 = s_1_2_3_4 + layer_5
            s_test = "structure" + layer_2 + layer_3 + layer_4 + layer_5  # without node
            if s_test not in structure_nodes:
              structure_nodes.append(s_test)
              peripheries = "2"
              color = "mediumturquoise"
            else:
              color = "lightblue"
              peripheries = "1"
            graph.node(s_1_2_3_4_5, layer_5, style=node_style, color=color, peripheries=peripheries)
            graph.edge(s_1_2_3_4, s_1_2_3_4_5)


def walkTree(ontology, node, graph, behaviour_nodes, structure_nodes):
  children = ontology[node]["children"]
  parent = node
  # for i in ["structure", "behaviour"]:
  i = "behaviour"
  s = node + i
  graph.node(s, i, shape="diamond")
  graph.edge(parent, s)
  for j in ontology[node][i]:
    s_j = s + j
    graph.node(s_j, j)
    graph.edge(s, s_j)
    if i == "behaviour":
      for k in ontology[node][i][j]:
        if k != []:
          s_j_k = s_j + k
          graph.node(s_j_k, k)
          graph.edge(s_j, s_j_k)
          for l in ontology[node][i][j][k]:
            s_j_k_l = s_j_k + l
            # graph.node(s_j_k_l, l)
            # graph.edge(s_j_k, s_j_k_l)
            b_l = "behaviour" + l
            if b_l not in behaviour_nodes:
              behaviour_nodes.append(b_l)
              graph.node(b_l, l, style="filled", color="green")
              graph.edge(s_j_k, b_l)
        else:
          graph.node(s_j, j, shape="filled")
      # else:
  i = "structure"
  s = node + i
  graph.node(s, i, shape="diamond")
  graph.edge(parent, s)
  for j in ontology[node][i]:
    s_j = s + j
    graph.node(s_j, j)
    graph.edge(s, s_j)
    for k in ontology[node][i][j]:
      if k:
        s_j_k = s_j + k
        graph.node(s_j_k, k)
        graph.edge(s_j, s_j_k)
        for l in ontology[node][i][j][k]:
          s_l = "structure" + l
          if ontology[node][i][j][k].__class__ == list:
            if s_l not in structure_nodes:
              structure_nodes.append(s_l)
              graph.node(s_l, l, style="filled", color="pink")
              graph.edge(s_j_k, s_l)
              # print(l)
          else:
            s_j_k_l = s_j_k + l
            graph.node(s_j_k_l, l)
            graph.edge(s_j_k, s_j_k_l)
            for m in ontology[node][i][j][k][l]:
              s_j_k_l_m = s_j_k + l + m
              if ontology[node][i][j][k][l]:
                for n in ontology[node][i][j][k][l]:
                  s_n = "structure" + n
                  if s_n not in structure_nodes:
                    structure_nodes.append(s_n)
                    s_j_k_l_m_n = s_j_k_l_m + n
                    graph.node(s_n, n, style="filled", color="lightblue")
                    graph.edge(s_j_k_l, s_n)
                    # print(node,i,j,k,l,n)
                  pass
          pass
  if children:
    s_c = node + "children"
    graph.node(s_c, "children", shape="rectangle")
    graph.edge(parent, s_c)
    s_k = [s_c]
    no = 6
    for k in range(1, no):
      s_k.append(s_c + str(k))
      graph.node(s_k[k], "v", style="filled", shape="invtriangle")
      graph.edge(s_k[k - 1], s_k[k])
    hook = s_k[no - 1]
    for child in children:
      # print(child)
      graph.node(child, shape="box")
      graph.edge(hook, child)
      walkTree(ontology, child, graph, behaviour_nodes, structure_nodes)
  else:
    return


def walkTreeToLists(ontology, node, lists):
  parent = node
  children = ontology[node]["children"]
  obj = ontology[node]["behaviour"]
  parents = ontology[node]["parents"]
  objectlist = []
  seekList(obj, objectlist, parents, lists)
  if children:
    for child in children:
      walkTreeToLists(ontology, child, lists)


def seekList(obj, objectlist, parents, lists, first=True):
  if first:
    objectlist = []
  if obj.__class__ == dict:
    if dict != {}:
      for o in obj:
        objectlist.append(o)
        seekList(obj[o], objectlist, parents, lists, first=False)
    else:
      list.append((parents, obj, objectlist))
  else:
    lists.append((parents, obj, objectlist))


# #testing
#
if __name__ == '__main__':

  a = QtWidgets.QApplication([])

  ontology_name = getOntologyName()

  dot_path = os.path.join(DIRECTORIES["ontology_repository"], ontology_name, DIRECTORIES["ontology_graphs_location"],
                          "%s")
  o_template = dot_path  # + ".gv"
  o = FILES["ontology_file"] % ontology_name

  ontology = getData(o)["ontology_tree"]

  #
  # the tree of networks
  f = o_template % "tree"
  print(f)
  graph_attr = {}
  graph_attr["nodesep"] = "1"
  graph_attr["ranksep"] = "0.3"
  # graph_attr.edge_attr["color"] = "blue"
  graph_attr["splines"] = "false"  # ""polyline"
  edge_attr = {}
  # edge_attr["tailport"] = "s"
  # edge_attr["headport"] = "n"
  simple_graph = Digraph("T", filename=f)
  simple_graph.graph_attr = graph_attr
  simple_graph.edge_attr = edge_attr
  ontology_hierarchy = walkTreeOnly(ontology, "root", simple_graph)

  print(ontology_hierarchy)
  simple_graph.view()  # generates pdf
  os.remove(f)

  #
  # one node at the time starting with the root node in the network tree
  behaviour_nodes = []
  structure_nodes = []
  graph_attr["rankdir"] = "LR"
  edge_attr["tailport"] = "e"
  edge_attr["headport"] = "w"  # msg_box"
  graph_attr["nodesep"] = "0.4"
  graph_attr["ranksep"] = "0.8"

  node = "root"
  n = str(node)
  f = o_template % n
  print(f)
  node_graph = Digraph(n, filename=f, graph_attr=graph_attr)
  node_graph.graph_attr = graph_attr
  node_graph.edge_attr = edge_attr
  ontology_hierarchy = singleNodeOnly(ontology, n, node_graph, behaviour_nodes, structure_nodes)

  node_graph.view()

  tree = ["root"]
  makeTree(ontology, "root", tree)
  for node in tree:
    if node != "root":
      n = str(node)
      f = o_template % n
      print(f)
      node_graph = Digraph(n, filename=f, graph_attr=graph_attr)
      ontology_hierarchy = singleNodeOnly(ontology, n, node_graph, behaviour_nodes, structure_nodes)

      node_graph.view()

  pdf_template = dot_path + ".pdf"

  merger = PdfFileMerger()
  pdf = pdf_template % "tree"
  merger.append(open(pdf, 'rb'))
  pdf = pdf_template % str("root")
  merger.append(open(pdf, 'rb'))
  for node in tree:
    if node != "root":
      pdf = pdf_template % str(node)
      merger.append(open(pdf, 'rb'))
    os.remove(o_template % str(node))

  o = dot_path % "all_nodes" + ".pdf"
  merger.write(o)

  print("file written to :", o)
