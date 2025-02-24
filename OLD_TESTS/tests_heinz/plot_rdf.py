"""
plot RDF graph

"""

import graphviz


EDGE_COLOUR = {
        "is_a_subclass_of": "blue",
        "link_to_class"   : "red",
        "value"           : "black",
        "comment"         : "green",
        "integer"         : "darkorange",
        "string"          : "cyan",
        }




PRIMITIVES = []

def extractLabel(s, prefixes):
  # print(s)

  return s.split("/")[-1]

def plot(graph):
  """
  Create Digraph plot
  color names : https://graphviz.org/doc/info/colors.html
  """

  prefixes = {}
  for pre,ns in graph.namespaces():
    n = str(ns) #ns.split(")")[0].split(")")[0]
    prefixes[pre] = n

  dot = graphviz.Digraph(graph_attr={"rankdir":"LR"})
  # Add nodes 1 and 2
  suffix = 0
  for s, p, o in graph.triples((None, None, None)):
    ss = extractLabel(s, prefixes)
    sp = extractLabel(p, prefixes)
    so = extractLabel(o,prefixes)
    dot.node(ss)
    dot.node(so)
    dot.edge(ss,so,sp)
  return dot


