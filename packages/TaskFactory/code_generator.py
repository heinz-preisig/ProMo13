import os
import sys

from pprint import pprint as pp

sys.path.insert(0, os.path.abspath(".."))

from packages.Common.classes import io
from packages.Common.classes import equation
from packages.Common.classes import vareqdigraph
from packages.TaskFactory import template_handler

ontology_name = "test_ontology"
model_name = "SimpleMixer"

all_variables, all_indices = io.load_variables_from_file(ontology_name)
all_equations = io.load_equations_from_file(ontology_name)
all_entities = io.load_entities_from_file(ontology_name)
topology_graph = io.load_topology_from_file(
  ontology_name,
  model_name,
  all_entities,
)
var_eq = vareqdigraph.VarEqDiGraph(
  topology_graph,
  all_equations,
  all_indices,
  all_variables,
)
var_eq.find_solving_order()
# pp(var_eq.expressions)
# pp(var_eq.expressions)


# TODO Check what else is needed ex: solvers, initial guesses for solvers, etc
temp = template_handler.TemplateHandler(
  "matlab",
  all_variables,
  all_indices, 
  all_equations,
  var_eq,
)

content = temp.generate_content()

with open("test.m", mode="w", encoding="utf-8") as message:
  message.write(content)

# ######### To ask for initial conditions in an equation system ##########
# sub: nx.DiGraph = dir_graph.subgraph(all_cycles[0]).copy()
# print_graph(sub,"subgraph.png")
# for node in sub:
#   remove_edges = []
#   for edge in nx.edges(sub, node):
#     if node == edge[0]:
#       remove_edges.append(edge)

#   sub.remove_edges_from(remove_edges)
#   # print_graph(sub, str(node) + ".png")
#   cycles = len(list(nx.simple_cycles(sub)))
  
  
#   print("Node: " + str(node) + " --- Cycles: " + str(cycles))

#   sub.add_edges_from(remove_edges)
#   # print_graph(sub, "re_added-" + str(node) + ".png")
# ########################################################################

