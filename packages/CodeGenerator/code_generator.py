import os
import shutil
import sys
from pprint import pprint as pp

sys.path.insert(0, os.path.abspath(".."))


root = os.path.abspath(os.path.join(".."))
sys.path.extend([root, os.path.join(root, 'packages','src'),
                os.path.join(root, 'tasks')])

# fmt: off
from Common import resource_initialisation
from Common.classes import io
from code_generator import equation_sequencer, template_handler
from  common.old_io import IOHandler

# fmt: on
#
# if len(sys.argv) != 2:
#     print("ERROR: Wrong command-line arguments length")
#     exit()

# ontology_name = sys.argv[0]  # "DEMO"
# model_name = sys.argv[1]  # "DEMO"
class CodeGenerator:
    def __init__(self, ontology_name, model_name):
        self.ontology_name = ontology_name
        self.model_name = model_name

    def generate_code(self):

# Loading information from the files
        all_variables, all_indices, all_equations = io.load_var_idx_eq_from_file(self.ontology_name)

        all_entities = io.load_entities_from_file(self.ontology_name, all_equations)

        all_topology_objects = io.load_topology_objects(self.ontology_name, self.model_name, all_entities)


        equation_seq, map_eq_top = equation_sequencer.sequence_equations(
            all_topology_objects,
        )

        io_handler = IOHandler()
        params = {"ontology_name": self.ontology_name, "model_name": self.model_name}
        io_handler.add_path_parameters(params)

        instantiation_data = io_handler.get_instantiation_data()

        # TODO Check what else is needed ex: solvers, initial guesses for solvers, etc
        temp = template_handler.TemplateHandler(
            "matlab",
            all_variables,
            all_indices,
            all_equations,
            all_topology_objects,
            equation_seq,
            map_eq_top,
            instantiation_data,
        )

        content = temp.generate_content()

        dir_path = resource_initialisation.DIRECTORIES["model_location"] % (
            self.ontology_name,
            self.model_name,
        )
        file_path = os.path.join(dir_path, "main.m")

        with open(file_path, mode="w", encoding="utf-8") as message:
            message.write(content)

        init_file_path = os.path.join(dir_path, "init.m")
        init_content = temp.generate_init_content()

        with open(init_file_path, mode="w", encoding="utf-8") as message:
            message.write(init_content)

        # To copy the @MultiDimVar
        lib_path = os.path.join(
            resource_initialisation.DIRECTORIES["ProMo_root"],
            "ProMo/static_assets/@MultiDimVar",
        )
        dest_path = dir_path + "/@MultiDimVar"

        # Check if the destination directory exists
        if os.path.exists(dest_path):
            # If it exists, remove it
            shutil.rmtree(dest_path)

        # Now you can copy the directory
        shutil.copytree(lib_path, dest_path)

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
