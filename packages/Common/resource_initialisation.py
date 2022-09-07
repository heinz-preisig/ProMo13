#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 sets absolute root for the modelling software environment
===============================================================================
Created on Jan16 July, 2016

"""
ONTOLOGY_VERSION = "3"
VARIABLE_EQUATIONS_VERSION = "8"

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2016. 07. 2016"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__version__ = "7.00"
__version__ = "8.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os as OS
from shutil import copyfile

from Common.pop_up_message_box import makeMessageBox

# from Common.ui_message_popup_impl import UI_MessagePopUp

# TODO: reloacte all shell commands into one location

FILE_NAMES = {
        "ontology_file"                       : "ontology.json",
        "model_file"                          : "model.json",
        "model_flat_file"                     : "model_flat.json",
        "indices_file"                        : "indices.json",
        # "rules_file"                      : "rules.json",
        "variables_file"                      : "variables_v8.json",
        "variables_file_v6"                   : "variables_v6.json",
        "variables_file_v7"                   : "variables_v7.json",
        "variables_file_v8"                   : "variables_v8.json",
        "variables_initial"                   : "variables_initial.json",
        "equations_file"                      : "equations.json",
        "typed_tokens_file"                   : "typed_tokens.json",
        "converting_tokens_file"              : "converting_tokens.json",
        # "automata_working"                    : "automata_working.json",
        "automata"                            : "automata.json",
        "graph_objects"                       : "graph_objects.json",
        "init_nodes"                          : "nodes.json",
        "init_arcs"                           : "arcs.json",
        "init_globals"                        : "globals.json",
        "calculation_sequence"                : "sequence.json",
        "constants_init_python"               : "constants.py",
        "networks_python"                     : "networks.py",
        "simulation_main_python"              : "main.py",
        "selections_variables"                : "selections.py",
        "global_variable_identifier"          : "global_variable_identifier.txt",
        "global_index_identifier"             : "global_index_identifier.txt",
        "global_equation_identifier"          : "global_equation_identifier.txt",
        "template_variable"                   : "template_variable",
        "latex_automaton"                     : "automata_tables.tex",
        "dot_graph_shell"                     : "show_dot_graphs.sh",
        "latex_shell_var_equ_doc_command"     : "make_documentation.sh",
        "latex_shell_automata_doc_command"    : "make_automata_table.sh",
        "latex_shell_var_equ_list_command"    : "latex_compile.sh",
        "variable_assignment_to_entity_object": "variable_assignment_to_entity_object.json"
        }

EXTENSION_GRAPH_DATA = ".json"
EXTENSION_AUTOMATA_DATA = ".json"
DEFAULT_EXTENSION_CURSOR = ".xpm"

DEFAULT_TEMP_MODEL_FILE = "temp"

# locations
JOIN = OS.path.join

DIRECTORIES = {}
DIRECTORIES["packages"] = JOIN(OS.path.abspath("../packages"))  # OS.getcwd()      #OS.path.abspath()
DIRECTORIES["repository_infrastructure"] = JOIN("..", DIRECTORIES["packages"], "Common", "RepositoryInfrastructure")
DIRECTORIES["ProMo_root"] = OS.path.abspath(JOIN("..", ".."))
DIRECTORIES["common"] = JOIN(DIRECTORIES["packages"], "Common")
DIRECTORIES["icon_location"] = JOIN(DIRECTORIES["common"], "icons")
DIRECTORIES["cursor_location"] = JOIN(DIRECTORIES["common"], "cursors")
# DIRECTORIES["ontology_repository"] = JOIN(DIRECTORIES["ProMo_root"], "Model_Repository")
DIRECTORIES["ontology_repository"] = JOIN(DIRECTORIES["ProMo_root"], "Ontology_Repository")
DIRECTORIES["documentation"] = JOIN(DIRECTORIES["ProMo_root"], "Documentation")
DIRECTORIES["protocol"] = JOIN(DIRECTORIES["common"], "protocol")
DIRECTORIES["new_ontology_starting_set"] = JOIN(DIRECTORIES["packages"], "Common", "RepositoryInfrastructure")
DIRECTORIES["equation_templates"] = JOIN(DIRECTORIES["packages"], "OntologyEquationEditor")

# those that are ontology dependent
DIRECTORIES["model_repository"] = "models"
DIRECTORIES["graphobject_resources"] = "resources"
DIRECTORIES["case_repository"] = "cases"
DIRECTORIES["ontology_graphs_location"] = "ontology_graphs"  #TODO: change to graphs--needs change of infrastructure handling
DIRECTORIES["graphs"] = "ontology_graphs" #TODO: change to graphs--needs change of infrastructure handling

DIRECTORIES["ontology_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s")  # %ontology_name
DIRECTORIES["model_library_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                             DIRECTORIES["model_repository"])  # %ontology_name
DIRECTORIES["resource_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                        DIRECTORIES["graphobject_resources"])  # %ontology_name

DIRECTORIES["model_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                     DIRECTORIES["model_repository"], "%s")  # %ontology_name, model_name

DIRECTORIES["cases_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                     DIRECTORIES["model_repository"], "%s",
                                     DIRECTORIES["case_repository"])  # %ontology_name, model_name

DIRECTORIES["specific_case"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                    DIRECTORIES["model_repository"], "%s",
                                    DIRECTORIES["case_repository"], "%s")  # %ontology_name, model_name, case_name
# DIRECTORIES["output_language"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
#                                       DIRECTORIES["model_repository"], "%s",
#                                       DIRECTORIES["case_repository"], "%s", "%s",

DIRECTORIES["latex"] = "LaTeX"
DIRECTORIES["latex_doc_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                         DIRECTORIES["latex"])  # %ontology_name

DIRECTORIES["latex_main_location"] = JOIN("%s", DIRECTORIES["latex"])
DIRECTORIES["latex_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s", DIRECTORIES["latex"])
DIRECTORIES["latex_resource_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s", DIRECTORIES["latex"],
                                              "resources")
DIRECTORIES["latex_resource_location_exec"] = JOIN("%s", DIRECTORIES["latex"],
                                                   "resources")

DIRECTORIES["automata_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                        DIRECTORIES["graphobject_resources"])  # %ontology_name

DIRECTORIES["output_language"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                      DIRECTORIES["model_repository"], "%s",
                                      DIRECTORIES["case_repository"], "%s",
                                      "%s")  # %ontology_name, model_name, case_name, language
DIRECTORIES["common_shell_scripts"] = JOIN(DIRECTORIES["common"], "shell_scripts")
DIRECTORIES["graph_locations"] = JOIN(DIRECTORIES["ontology_repository"], "%s", DIRECTORIES["graphs"])

FILES = {}
FILES["ontology_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s", FILE_NAMES["ontology_file"])  # %ontology_name
FILES["indices_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s", FILE_NAMES["indices_file"])  # %ontolgy_name
# FILES["rules_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s", FILE_NAMES["rules_file"])  # %ontology_name
FILES["global_variable_identifier"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                           FILE_NAMES["global_variable_identifier"])  # %ontology_name
FILES["global_index_identifier"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                        FILE_NAMES["global_index_identifier"])  # %ontology_name
FILES["global_equation_identifier"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                           FILE_NAMES["global_equation_identifier"])  # %ontology_name

FILES["variables_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                               FILE_NAMES["variables_file"])  # %ontology_name

FILES["variables_file_v6"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                  FILE_NAMES["variables_file_v6"])  # %ontology_name

FILES["variables_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                               FILE_NAMES["variables_file_v8"])  # %ontology_name

FILES["variables_file_v7"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                  FILE_NAMES["variables_file_v7"])  # %ontology_name

FILES["initial_variables_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                       FILE_NAMES["variables_initial"])  # %ontology_name

FILES["equations_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                               FILE_NAMES["equations_file"])  # %ontology_name
FILES["typed_token_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                 FILE_NAMES["typed_tokens_file"])  # %ontology_name

FILES["model_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                           DIRECTORIES["model_repository"], "%s",
                           FILE_NAMES["model_file"])  # %onto_name, model_name

FILES["model_flat_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                DIRECTORIES["model_repository"], "%s",
                                FILE_NAMES["model_flat_file"])  # %onto_name, model_name

FILES["model_case_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                DIRECTORIES["model_repository"], "%s",
                                "%s.json")  # %onto_name, model_name, case_name

FILES["pnglatex"] = JOIN(DIRECTORIES["common_shell_scripts"], "pnglatex.bash")
FILES["latex_png_header_file"] = JOIN(DIRECTORIES["ontology_location"],"png_header.tex")

FILES["lock_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s", "lock_file")

FILES["instantiation_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s", "instantiation.json")  # %ontology_name
FILES["converting_tokens_file"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                       FILE_NAMES["converting_tokens_file"])  # %ontology_name

# FILES["automata_working_file_spec"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
#                                            DIRECTORIES["graphobject_resources"],
#                                            FILE_NAMES["automata_working"])  # %ontology_name
FILES["automata_file_spec"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                   DIRECTORIES["graphobject_resources"],
                                   FILE_NAMES["automata"])  # %ontology_name

FILES["graph_resource_file_spec"] = JOIN(DIRECTORIES["ontology_repository"], "%s", DIRECTORIES["graphobject_resources"],
                                         FILE_NAMES["graph_objects"])  # %ontology_name

FILES["variable_assignment_to_entity_object"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                                     FILE_NAMES[
                                                         "variable_assignment_to_entity_object"])  # %ontology_name

FILES["template_variable"] = JOIN(DIRECTORIES["equation_templates"], FILE_NAMES["template_variable"])

FILES["latex_shell_var_equ_doc_command"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                                DIRECTORIES["latex"],
                                                FILE_NAMES["latex_shell_var_equ_doc_command"])
FILES["latex_shell_var_equ_doc_command_exec"] = JOIN(DIRECTORIES["latex_resource_location_exec"] % "%s",
                                                     FILE_NAMES["latex_shell_var_equ_doc_command"])
FILES["latex_shell_ontology_view_exec"] = JOIN(DIRECTORIES["resource_location"] % "%s",
                                               FILE_NAMES["dot_graph_shell"])
FILES["latex_shell_automata_doc_command"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                                 DIRECTORIES["latex"],
                                                 FILE_NAMES["latex_shell_automata_doc_command"])
FILES["latex_shell_var_equ_list_command"] = JOIN(DIRECTORIES["latex_resource_location"],
                                                FILE_NAMES["latex_shell_var_equ_list_command"])

FILES["OWL_variables"] = JOIN(DIRECTORIES["ontology_repository"], "%s", "python_owl.py")
FILES["OWL_template"] = "template_variables.owl"

FILES["latex_main"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                           DIRECTORIES["latex"], "main.tex")

FILES["latex_equation_list"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                           DIRECTORIES["latex"], "%s.tex")                       # ontology_name, variant_name

FILES["latex_documentation"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                    DIRECTORIES["latex"], "main.pdf")

FILES["latex_automaton_resource"] = JOIN(DIRECTORIES["ontology_repository"], "%s", DIRECTORIES["latex"],
                                         "resources", "automata_tables.tex")
FILES["latex_automaton"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                DIRECTORIES["latex"], FILE_NAMES["latex_automaton"])
FILES["latex_automaton_phase_file_name"] = JOIN(DIRECTORIES["ontology_repository"], "%s", DIRECTORIES["latex"],
                                                "automata" + "_" + "%s" + ".tex")  # %(ontology_name, phase)
FILES["latex_variables"] = JOIN("%s", DIRECTORIES["latex"], "variables_%s.tex")
FILES["latex_equations"] = JOIN("%s", DIRECTORIES["latex"], "equations_%s.tex")

FILES["latex_template_main"] = "template_main.latex"
FILES["latex_template_variables"] = "template_variables.latex"
FILES["latex_template_equations"] = "template_equations.latex"
FILES["latex_template_equation_list"] = "template_equation_list.latex"


### info files
FILES["info_ontology_foundation_editor"] = JOIN(DIRECTORIES["common"], "info_ontology_foundation_editor.html")
# FILES["info_ontology_foundation_second_stage_editor"] = JOIN(DIRECTORIES["common"],
#                                                              "info_ontology_foundation_second_stage_editor.html")
FILES["info_ontology_equation_editor"] = JOIN(DIRECTORIES["common"], "info_ontology_equation_editor.html")
FILES["info_ontology_variable_table"] = JOIN(DIRECTORIES["common"], "info_ontology_variable_table.html")
FILES["info_index_alias_table"] = JOIN(DIRECTORIES["common"], "info_index_alias_table.html")
FILES["info_variable_alias_table"] = JOIN(DIRECTORIES["common"], "info_variable_alias_table.html")

FILES["ontology_graphs_ps"] = JOIN("%s", DIRECTORIES["ontology_graphs_location"], 'graph__%s.ps')
FILES["ontology_graphs_gv"] = JOIN("%s", DIRECTORIES["ontology_graphs_location"], 'graph__%s.gv')
FILES["ontology_graphs_dot"] = JOIN("%s", DIRECTORIES["ontology_graphs_location"], 'graph__%s.dot')
FILES["network_matrices"] = JOIN(DIRECTORIES["ontology_repository"], "%s", "network_matrices.json")  # %ontology_name

FILES["graph_resource_documentation"] = JOIN(DIRECTORIES["common"], "actions.txt")

FILES["init_nodes"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                           DIRECTORIES["model_repository"], "%s",
                           DIRECTORIES["case_repository"], "%s",
                           FILE_NAMES["init_nodes"])  # %ontology_name, model_name, case_name
FILES["init_arcs"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                          DIRECTORIES["model_repository"], "%s",
                          DIRECTORIES["case_repository"], "%s",
                          FILE_NAMES["init_arcs"])  # %ontology_name, model_name, case_name
FILES["init_globals"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                             DIRECTORIES["model_repository"], "%s",
                             DIRECTORIES["case_repository"], "%s",
                             FILE_NAMES["init_globals"])  # %ontology_name, model_name, case_name

FILES["calculation_sequence"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                     DIRECTORIES["model_repository"], "%s",
                                     DIRECTORIES["case_repository"], "%s",
                                     FILE_NAMES["calculation_sequence"])  # %ontology_name, model_name, case_name

FILES["constants_initialized"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                      DIRECTORIES["model_repository"], "%s",
                                      DIRECTORIES["case_repository"], "%s", "%s",
                                      FILE_NAMES[
                                          "constants_init_python"])  # %ontology_name, model_name, case_name, language

FILES["networks_variables"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                   DIRECTORIES["model_repository"], "%s",
                                   DIRECTORIES["case_repository"], "%s", "%s",
                                   FILE_NAMES["networks_python"])  # %ontology_name, model_name, case_name, language

FILES["simulation_main_python"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                       DIRECTORIES["model_repository"], "%s",
                                       DIRECTORIES["case_repository"], "%s", "%s",
                                       FILE_NAMES[
                                           "simulation_main_python"])  # %ontology_name, model_name, case_name, language
FILES["selections_variables"] = JOIN(DIRECTORIES["ontology_repository"], "%s",
                                     DIRECTORIES["model_repository"], "%s",
                                     DIRECTORIES["case_repository"], "%s", "%s",
                                     FILE_NAMES[
                                         "selections_variables"])  # %ontology_name, model_name, case_name, language

FILES["coded_equations"] = JOIN("%s", "equations_%s.json")  # ontology_location, language
FILES["coded_variables"] = JOIN("%s", "variables_%s.json")  # ontology_location, language

FILES["icons"] = {
        "info": JOIN(DIRECTORIES["icon_location"], "info_icon.png")
        }


# compilation of rst to html  NOTE: not a good way of doing things -- generate HTML directly with normal editor
# import docutils.core

# docutils.core.publish_file(
#       source_path="/home/heinz/1_Gits/ProcessModeller/ProcessModeller_v7_04/packages/Common
#       /info_ontology_design_editor.rst",
#       destination_path="/home/heinz/1_Gits/ProcessModeller/ProcessModeller_v7_04/packages/Common
#       /info_ontology_design_editor.html",
#       writer_name="html")

# docutils.core.publish_file(
#       source_path="/home/heinz/1_Gits/ProcessModeller/ProcessModeller_v7_04/packages/Common
#       /info_ontology_design_editor.rst",
#       destination_path="/home/heinz/1_Gits/ProcessModeller/ProcessModeller_v7_04/packages/Common
#       /info_ontology_design_editor.tex",
#       writer_name="latex")


def checkAndFixResources(ontology_name, stage="ontology_stage_1"):
    REQUIRED_DIRECTORIES = [DIRECTORIES["ontology_repository"],
                            DIRECTORIES["ontology_location"] % ontology_name,
                            DIRECTORIES["model_library_location"] % ontology_name,
                            DIRECTORIES["resource_location"] % ontology_name,
                            DIRECTORIES["automata_location"] % ontology_name,
                            DIRECTORIES["latex_doc_location"] % ontology_name,
                            DIRECTORIES["latex_resource_location"] % ontology_name
                            ]

    # touples        #TODO: include all files
    # - first the required file
    # - second the source
    RESOURCE_FILES = {
            "ontology_stage_1": [(FILES["ontology_file"] % ontology_name,
                                  JOIN(DIRECTORIES["repository_infrastructure"], FILE_NAMES["ontology_file"])
                                  ),
                                 # (FILES["rules_file"]%ontology_name,
                                 #  JOIN(DIRECTORIES["repository_infrastructure"], FILE_NAMES["rules_file"])
                                 #  ),
                                 ],
            "ontology_stage_2": [(FILES["converting_tokens_file"] % ontology_name,
                                  JOIN(DIRECTORIES["repository_infrastructure"],
                                       FILE_NAMES["converting_tokens_file"])
                                  ),
                                 ],
            }

    MUST_HAVE_FILES = {
            "ontology_stage_1": [],
            "ontology_stage_2": [FILES["ontology_file"] % ontology_name,
                                 ],
            "ontology_stage_2": [FILES["ontology_file"] % ontology_name
                                 ],
            "model_composer"  : [FILES["typed_token_file"] % ontology_name,
                                 ],
            }

    if stage == "ontology_stage_1":

        for r in REQUIRED_DIRECTORIES:
            if not OS.path.exists(r):
                OS.mkdir(r)
                print("RESOURCES -- made new directory :", r)

    for f in MUST_HAVE_FILES[stage]:
        if not OS.path.exists(f):
            gugus = makeMessageBox("no such file : %s" % f) #, buttons=[])
            pass

    for r in range(len(RESOURCE_FILES[stage])):
        file, resource = RESOURCE_FILES[stage][r]
        if not OS.path.exists(file):
            copyfile(resource, file)
