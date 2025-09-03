import copy
from collections import Counter
from pprint import pprint as pp
from typing import Dict, List, Optional, Set, Tuple

import jinja2
import numpy as np

from Common import resource_initialisation as ri
from Common.classes import equation, equation_parser, index, variable
from src.common import old_topology


class TemplateHandler:
    def __init__(
        self,
        language: str,
        all_variables: dict[str, variable.Variable],
        all_indices: dict[str, index.Index],
        all_equations: dict[str, equation.Equation],
        all_topology_objects: dict[str, old_topology.TopologyObject],
        equation_seq: list[set[str]],
        map_eq_top: dict[str, set[old_topology.EntityContainer]],
        instantiation_data: dict[str, dict[tuple[str, ...], str]],
    ):
        self.language = language
        self.all_variables = all_variables
        self.all_indices = all_indices
        self.all_equations = all_equations
        self.all_topology_objects = all_topology_objects
        self.equation_seq = equation_seq
        self.map_eq_top = map_eq_top
        self.instantiation_data = instantiation_data

        self.enviroment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(ri.DIRECTORIES["templates"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self.load_language_filters()
        self.data = self.generate_language_data()

    def generate_content(self):
        template = self.load_language_template()
        return template.render(self.data)

    def generate_init_content(self):
        template = self.load_init_template()
        return template.render(self.data)

    def load_language_template(self):
        template_file = self.language + "_template"
        return self.enviroment.get_template(ri.FILE_NAMES[template_file])

    def load_init_template(self):
        template_file = self.language + "_input.jinja"
        return self.enviroment.get_template(template_file)

    def generate_index_info(self):
        index_sets = {
            "N": [],
            "A": [],
            "I": [],
            "S": [],
        }
        self.map_id_to_counter = {}
        species = set()

        index_set_counter = Counter(index_sets.keys())

        for top_id, top_obj in self.all_topology_objects.items():
            if not isinstance(top_obj, old_topology.EntityContainer):
                continue

            if isinstance(top_obj, old_topology.NodeSimple):
                self.map_id_to_counter[top_id] = index_set_counter["N"]
                index_set_counter["N"] += 1

            if isinstance(top_obj, old_topology.Arc):
                self.map_id_to_counter[top_id] = index_set_counter["A"]
                index_set_counter["A"] += 1

            if "mass" in top_obj.typed_tokens:
                species.update(top_obj.typed_tokens["mass"])

        index_set_counter["S"] += len(species)
        for key in index_sets:
            index_sets[key] = list(range(1, index_set_counter[key]))

        for i, species_name in enumerate(species, start=1):
            self.map_id_to_counter[species_name] = i

        # pp(index_sets)
        # pp(map_id_to_counter)

        self.update_instantiation_info()
        return index_sets

    def update_instantiation_info(self):
        updated_info = {}
        self.map_id_to_counter["1"] = 1
        for var_id, inst_data in self.instantiation_data.items():
            updated_info[var_id] = {}
            for tuple_key, value in inst_data.items():
                new_tuple = tuple(
                    [self.map_id_to_counter[identifier] for identifier in tuple_key]
                )
                updated_info[var_id][new_tuple] = value

        self.instantiation_data = updated_info

    def find_all_variables(self):
        model_variables = set()
        for top_obj in self.all_topology_objects.values():
            if isinstance(top_obj, old_topology.EntityContainer):
                model_variables.update(top_obj.entity_instance.get_variables())

        return model_variables

    def find_integrators(self):
        integrators = []
        for cycle in self.equation_seq:
            for eq_id in cycle:
                if self.all_equations[eq_id].is_integrator():
                    integrators.append(eq_id)

        return integrators

    def get_index_sets(self, eq_id: str):
        species_key = f"S_{eq_id}"
        index_sets = {}

        for top_obj in self.map_eq_top[eq_id]:
            key = f"{top_obj.identifier[0]}_{eq_id}"
            if key not in index_sets:
                index_sets[key] = set()

            index_sets[key].add(self.map_id_to_counter[top_obj.identifier])

            if "mass" in top_obj.typed_tokens:
                if species_key not in index_sets:
                    index_sets[species_key] = set()

                species_number_ids = [
                    self.map_id_to_counter[s] for s in top_obj.typed_tokens["mass"]
                ]
                index_sets[species_key].update(species_number_ids)

        return {
            key: sorted(list(index_values)) for key, index_values in index_sets.items()
        }

    def generate_language_data(self):
        data = {}

        # Information about the index sets
        data["index_sets_info"] = self.generate_index_info()

        data["index_order"] = ["N", "A", "I", "S"]
        # TODO: THIS COMES FROM THE USER
        is_sparse = False
        # This info will be refined in the load_model function after the gui for
        # the task manager is done.
        data["print_info"] = {}

        # Information about the initialization of all variables
        data["variables"] = []

        model_vars = self.find_all_variables()
        for var_id in model_vars:
            var_data = self.all_variables[var_id]
            index_structures = var_data.index_structures

            translated_index_structures = [
                self.all_indices[idx].get_translation(self.language)
                for idx in index_structures
            ]

            index_sets = ", ".join(translated_index_structures)

            index_labels = ", ".join(
                [idx + "_lbl" for idx in translated_index_structures]
            )
            var_size = [
                len(data["index_sets_info"][index_set_name])
                for index_set_name in translated_index_structures
            ]
            if not var_size:
                var_size = ["1"]

            data["variables"].append(
                {
                    "var_id": var_id,
                    "comment": [var_data.doc],
                    "instantiation_values": self.instantiation_data.get(var_id, {}),
                    "index_labels": index_labels,
                    "index_sets": index_sets,
                    "is_sparse": is_sparse,
                    "size": var_size,
                }
            )
        # pp(data["variables"])
        # Information about the integrators
        integrators = self.find_integrators()

        data["integrators"] = []
        count = 1
        for eq_id in integrators:
            integrator_info = self.all_equations[eq_id].parse_integrator()
            if integrator_info is None:
                print(f"Eq: {eq_id} is not an integrator.")
                continue

            integrator_info["index_sets"] = self.get_index_sets(eq_id)

            # integrator_info["top_ids"] = top_ids

            # var_data = self.all_variables[var_id]
            # index_structures = var_data.index_structures

            index_names = list(integrator_info["index_sets"])
            organized_index_names = sorted(
                index_names, key=lambda x: data["index_order"].index(x[0])
            )

            size_by_index = [
                len(integrator_info["index_sets"][index_name])
                for index_name in organized_index_names
            ]
            ini = str(count)
            count += np.prod(size_by_index)
            fin = str(count - 1)

            integrator_info["interval"] = ini + ":" + fin
            integrator_info["size_by_index"] = size_by_index

            data["integrators"].append(integrator_info)
        # pp(data["integrators"])

        # Information about the expressions
        data["expressions"] = []
        sys_counter = 1
        for equation_set in self.equation_seq:
            eq_id = list(equation_set)[0]
            eq = self.all_equations[eq_id]
            if len(equation_set) == 1 and not eq.is_root():
                var_id = eq.get_main_var_id()
                index_sets = self.get_index_sets(eq_id)
                if eq.is_integrator():
                    continue

                data["expressions"].append(
                    {
                        "type": "simple",
                        "id": eq_id,
                        "equations": [
                            {
                                "eq_id": eq_id,
                                "var_id": var_id,
                                "index_sets": index_sets,
                                "dependencies": eq.get_incidence_list(var_id),
                            }
                        ],
                    }
                )
            else:
                expr_info = {}
                expr_info["type"] = "system"
                expr_info["id"] = f"sys{sys_counter}"

                sys_counter += 1
                part_counter = 1

                equations = {}
                root_vars = {}
                for eq_id in equation_set:    # TODO: we need the index sets for each variable, not the equations and the initalisation must be done accordingly
                    eq = self.all_equations[eq_id]
                    var_id = eq.get_main_var_id()
                    equation_index_sets = self.get_index_sets(eq_id) #
                    root_variable_index_structures = self.all_variables[var_id].index_structures
                    # if eq.is_root():
                    #   root_vars[var_id] = eq.get_incidence_list(var_id)[0]
                    # else:

                    # HAP: fix ------------

                    check_ids = []
                    for id in root_variable_index_structures:
                      check_ids.append(self.all_indices[id].aliases["internal_code"] + "_" + eq_id)

                    size_by_index = []
                    for i in equation_index_sets:
                      if i in check_ids:
                        size_by_index.append(len(equation_index_sets[i]))
                    # size_by_index = [
                    #     len(indices_list) for indices_list in equation_index_sets.values()
                    # ]

                    # HAP: fix ------------

                    ini = str(part_counter)
                    part_counter += np.prod(size_by_index)
                    fin = str(part_counter - 1)

                    equations[var_id] = {
                        "eq_id": eq_id,
                        "var_id": var_id,
                        "index_sets": index_sets,
                        "interval": ini + ":" + fin,
                        "dependencies": eq.get_incidence_list(),
                        "is_root": eq.is_root(),
                    }
                # pp(equations)
                # pp(root_vars)
                # for root_var_id, replaced_var_id in root_vars.items():
                #   equations[replaced_var_id]["var_id"] = root_var_id

                # pp(equations)
                expr_info["equations"] = list(equations.values())
                data["expressions"].append(expr_info)

                # pp(data["expressions"])
                # for expr in self.var_eq.expressions:
                #   expr_info = {}

                #   sys_counter = 1
                #   if len(expr) == 1:
                #     var_id, eq_id, top_ids, index_sets = expr[0]
                #     # TODO: Extend this to add all the other index sets needed
                #     index_sets.add("S")

                #     eq = self.all_equations.get(eq_id)
                #     if eq.is_integrator():
                #       continue

                #     if eq.is_explicit_for_var(var_id):
                #       expr_info["type"] = "simple"
                #       expr_info["id"] = eq_id
                #       expr_info["equations"] = [{
                #           "eq_id": eq_id,
                #           "var_id": var_id,
                #           "top_ids": top_ids,
                #           "index_sets": index_sets,
                #           "dependencies": eq.get_incidence_list(var_id),
                #       }]
                #     else:
                #       expr_info["type"] = "root"
                #       expr_info["init_guess"] = ["Initial_Guess"]
                #       expr_info["id"] = "root" + eq_id
                #       expr_info["equations"] = [{
                #           "eq_id": eq_id,
                #           "var_id": var_id,
                #           "top_ids": top_ids,
                #           "index_sets": index_sets,
                #           "dependencies": eq.get_incidence_list(var_id) + [var_id],
                #       }]

                #   else:
                #     expr_info["type"] = "system"
                #     expr_info["id"] = f"system{sys_counter}"
                #     sys_counter += 1
                #     expr_info["equations"] = []
                #     expr_info["init_guess"] = ["initial_guess"]

                #     part_counter = 1
                #     for var_id, eq_id, top_ids, index_sets in expr:
                #       # TODO: Extend this to add all the other index sets needed
                #       index_sets.add("S")
                #       eq = self.all_equations[eq_id]
                #       ini = str(part_counter)
                #       part_counter += self.size_by_index(var_id, index_sets)
                #       fin = str(part_counter - 1)
                #       expr_info["equations"].append({
                #           "eq_id": eq_id,
                #           "var_id": var_id,
                #           "top_ids": top_ids,
                #           "interval": ini + ":" + fin,
                #           "index_sets": index_sets,
                #           "dependencies": eq.get_incidence_list(),
                #       })

                #   data["expressions"].append(expr_info)
        data["solvers"] = {
            "root": "fzero",
            "sys_of_equations": "fsolve",
        }

        return data

    def load_language_filters(self) -> None:
        # TODO Probably make it a static member
        filters = {
            "matlab": {
                "is_list": self.is_list,
                "label": self.var_label,
                "sets": self.specific_sets,
                "var_slice": self.var_slice,
                "dependencies": self.dependencies,
                "arguments": self.arguments,
                "eq_label": self.eq_label,
                "main_index": self.main_index,
            }
        }
        for filt_name, filt_function in filters[self.language].items():
            self.enviroment.filters[filt_name] = filt_function

    ############################### FILTERS ##############################
    ############################### MATLAB ###############################
    def is_list(self, variable):
        return isinstance(variable, list)

    def var_label(
        self,
        var_id: str,
    ) -> str:
        return self.all_variables.get(var_id).get_alias(self.language)

    def join_sets(self, main_set: str, index_sets: set[str]) -> list[str]:
        output = []
        for i in index_sets:
            if main_set[0] == i[0]:
                output.append(i)

        return output

    def specific_sets(
        self,
        var_id: str,
        index_sets: set[str],
    ) -> str:
        var_data = self.all_variables[var_id]
        index_structures = var_data.index_structures

        output = []

        for idx in index_structures:
            index_label = self.all_indices[idx].get_translation("internal_code")
            spec_idx_sets = self.join_sets(index_label, index_sets)
            if len(spec_idx_sets) == 1:
                output.append(spec_idx_sets[0])
            else:
                output.append("indexunion(" + ", ".join(spec_idx_sets) + ")")

        return ", ".join(output)

    def var_slice(
        self,
        var_id: str,
        index_sets: set[str],
    ) -> str:
        return (
            self.var_label(var_id) + "(" + self.specific_sets(var_id, index_sets) + ")"
        )

    def dependencies(self, expr_info: dict) -> str:
        if expr_info["type"] in ["simple"]:
            eq_info = expr_info["equations"][0]
            expr_dependencies = [
                self.var_label(var_id) for var_id in eq_info["dependencies"]
            ]
            # TODO: Extend to all main indices
            for main_idx in ["N", "A", "S"]:
                full_set = self.join_sets(main_idx, eq_info["index_sets"])
                # pp(full_set)
                if full_set:
                    if len(full_set) == 1:
                        expr_dependencies.append(full_set[0])
                    else:
                        expr_dependencies.append(
                            "indexunion(" + ", ".join(full_set) + ")"
                        )
        else:
            all_dependencies = set()
            # all_index_sets = set()
            for eq_info in expr_info["equations"]:
                # all_index_sets.update(eq_info["index_sets"])
                all_dependencies.update(eq_info["dependencies"])

            expr_dependencies = [
                self.var_label(var_id) for var_id in list(all_dependencies)
            ]
            # expr_dependencies.extend(list(all_index_sets))

        return ", ".join(expr_dependencies)

    def arguments(self, eq_info: dict) -> str:
        # pp(eq_info)
        eq_arg = [self.var_label(var_id) for var_id in eq_info["dependencies"]]

        # TODO: Extend to all main indices
        for main_idx in ["N", "A", "S"]:
            for idx in eq_info["index_sets"]:
                if main_idx == idx[0]:
                    eq_arg.append(main_idx)
                    break

        return ", ".join(eq_arg)

    # TODO: merge this with var_label
    def eq_label(self, eq_id: str, side: str) -> str:
        # TODO: The translation process will be done in the equation class
        # Change this when the translation function is out of io so it can be called
        # from the equation module without a circular dependency problem.
        if side == "lhs":
            global_id_rpr = self.all_equations[eq_id].lhs["global_ID"]
        else:
            global_id_rpr = self.all_equations[eq_id].rhs["global_ID"]

        parser = equation_parser.EquationParser(
            self.language, self.all_variables, self.all_indices
        )
        translated_eq = parser.parse(global_id_rpr)

        return translated_eq

    def main_index(self, var_id: str) -> str:
        var_data = self.all_variables[var_id]
        index_structures = var_data.index_structures

        return self.all_indices[index_structures[0]]["aliases"]["internal_code"][0]
