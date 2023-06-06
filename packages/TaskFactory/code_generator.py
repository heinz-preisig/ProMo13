
import os
import sys
import shutil

from pprint import pprint as pp

sys.path.insert(0, os.path.abspath(".."))

# fmt: off
from packages.TaskFactory import template_handler
from packages.Common.classes import vareqdigraph
from packages.Common.classes import equation
from packages.Common.classes import io
from packages.Common import resource_initialisation
# fmt: on

if len(sys.argv) != 2:
  print("ERROR: Wrong command-line arguments length")
  exit()

ontology_name = sys.argv[0]  # "DEMO"
model_name = sys.argv[1]  # "DEMO"

io.convert_model_file(ontology_name, model_name)
# model_name = "TEST_3Pores"

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

dir_path = resource_initialisation.DIRECTORIES["model_location"] % (
    ontology_name, model_name)
file_path = os.path.join(dir_path, "main.m")

with open(file_path, mode="w", encoding="utf-8") as message:
  message.write(content)

# To copy the @MultiDimVar
lib_path = os.path.join(
    resource_initialisation.DIRECTORIES["ProMo_root"], "ProMo/tests/Matlab/@MultiDimVar")
shutil.copytree(lib_path, dir_path + "/@MultiDimVar")

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
