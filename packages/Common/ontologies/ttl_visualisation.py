# OK idea, but does not work. Graphs are too big.

# 2023/03/02 Heinz A Preisig


import graphviz
from rdflib import Graph


# from plot_rdf import plot
# from rdflib.tools import rdf2dot


def extractLabel(s, prefixes):
  print(s)

  return s.split("/")[-1]


def plot(graph):
  """
  Create Digraph plot
  color names : https://graphviz.org/doc/info/colors.html
  """

  prefixes = {}
  for pre, ns in graph.namespaces():
    n = str(ns)  # ns.split(")")[0].split(")")[0]
    prefixes[pre] = n

  dot = graphviz.Digraph(graph_attr={"rankdir": "LR"})
  # Add nodes 1 and 2
  suffix = 0
  for s, p, o in graph.triples((None, None, None)):
    if "latexDefinition" not in p:  # causes problems
      ss = extractLabel(s, prefixes)
      sp = extractLabel(p, prefixes)
      so = extractLabel(o, prefixes)
      dot.node(ss)
      dot.node(so)
      dot.edge(ss, so, sp)
  return dot


ttl_files = [
        # "promo_equations.ttl",
        # "promo_language.ttl",
        "promo_variables.ttl",
        # "promo_indices.ttl",
        ]

# with scandir(".") as it:
#   for entry in it:
#     name = entry.name
#     if (".ttl" in name) and ("promo" in name):
#       ttl_files.append(name)

for f in ttl_files:
  g = Graph()
  g.load(f, format="ttl")
  p_name = f.split(".")[0]
  dot = plot(g)
  dot.render(p_name, view=True, cleanup=True )
