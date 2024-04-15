import copy
import jinja2
from typing import Dict, List, Tuple, Set, Optional
from pprint import pprint as pp
import numpy as np

from packages.Common.classes import equation_parser
from packages.Common.classes import variable
from packages.Common.classes import equation
from packages.Common.classes import index
from code_generator import equation_sequencer
from packages.Common import resource_initialisation as ri


class TemplateHandler:
  def __init__(
      self,
      language: str,
      all_variables: Dict[str, variable.Variable],
      all_indices: Dict[str, index.Index],
      all_equations: Dict[str, equation.Equation],
      vareq: equation_sequencer.VarEqDiGraph,
  ):
    self.language = language
    self.all_variables = all_variables
    self.all_indices = all_indices
    self.all_equations = all_equations
    self.var_eq = vareq

    self.enviroment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(ri.DIRECTORIES["templates"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    self.load_language_filters()
    self.template = self.load_language_template()
    self.data = self.generate_language_data()

  def generate_content(self):
    return self.template.render(self.data)

  def load_language_template(self) -> None:
    template_file = self.language + "_template"
    return self.enviroment.get_template(ri.FILE_NAMES[template_file])

  def generate_language_data(self):
    data = {}

    # Information about the index sets
    data["index_sets_info"] = copy.deepcopy(
        self.var_eq.top_graph.graph["index_sets_info"]
    )
    # pp(data["index_sets_info"])
    # Changing the alias of the index to the language specific ones
    general_idx_info = data["index_sets_info"]["general"]
    idx_list = list(general_idx_info.keys())
    for idx_id in idx_list:
      translated_idx = self.all_indices.get(
          idx_id).get_translation(self.language)
      general_idx_info[translated_idx] = general_idx_info.pop(idx_id)

    # TODO: Remove this when the indices are handled better
    data["index_sets_info"]["general"]["K"] = []
    pp(data["index_sets_info"])

    data["index_order"] = [
        self.all_indices[idx_id].get_translation(self.language)
        for idx_id in sorted(self.all_indices.keys())
    ]
    # pp(data["index_sets_info"])
    # TODO: THIS COMES FROM THE USER
    is_sparse = False
    # This info will be refined in the load_model function after the gui for
    # the task manager is done.
    names_info = self.var_eq.top_graph.graph["extra_info"]
    to_print = {
        "V_85": [
            {
                "extra_name": names_info["nodes"][3] + ":" + names_info["species"][1],
                "position": [3, 1]
            },
            {
                "extra_name": names_info["nodes"][4] + ":" + names_info["species"][1],
                "position": [4, 1]
            },
            {
                "extra_name": names_info["nodes"][5] + ":" + names_info["species"][1],
                "position": [5, 1]
            },
            {
                "extra_name": names_info["nodes"][3] + ":" + names_info["species"][2],
                "position": [3, 2]
            },
            {
                "extra_name": names_info["nodes"][4] + ":" + names_info["species"][2],
                "position": [4, 2]
            },
            {
                "extra_name": names_info["nodes"][5] + ":" + names_info["species"][2],
                "position": [5, 2]
            },
        ],
    }
    data["print_info"] = to_print

    # Information about the initialization of all variables
    data["variables"] = []
    # pp(self.var_eq.inst_variables)
    for var_id, inst_info in self.var_eq.inst_variables.items():
      var_data = self.all_variables[var_id]
      index_structures = var_data.index_structures

      index_sets = ", ".join(
          [
              self.all_indices.get(idx).get_translation(self.language)
              for idx in index_structures
          ]
      )

      index_labels = ", ".join(
          [
              self.all_indices.get(idx).get_translation(self.language) + "_lbl"
              for idx in index_structures
          ]
      )
      # pp(self.var_eq.top_graph.graph["index_sets_info"]["general"])
      var_size = [
          str(
              len(self.var_eq.top_graph.graph["index_sets_info"]["general"][idx]))
          for idx in self.all_variables[var_id].index_structures
      ]
      if not var_size:
        var_size = ["1", "1"]

      data["variables"].append({
          "var_id": var_id,
          "comment": [var_data.doc],
          "instantiation_values": inst_info,
          "index_labels": index_labels,
          "index_sets": index_sets,
          "is_sparse": is_sparse,
          "size": var_size,
      })
    # pp(data["variables"])
    # Information about the integrators
    data["integrators"] = []
    count = 1
    for var_id, eq_id, top_ids, index_sets in self.var_eq.integrators:
      integrator_info = self.all_equations[eq_id].parse_integrator()
      if integrator_info is None:
        print(f"Eq: {eq_id} is not an integrator.")
        continue

      integrator_info["index_sets"] = index_sets
      integrator_info["top_ids"] = top_ids

      # var_data = self.all_variables[var_id]
      # index_structures = var_data.index_structures

      ini = str(count)
      count += np.prod(self.size_by_index(var_id, index_sets))
      fin = str(count - 1)

      integrator_info["interval"] = ini + ":" + fin
      integrator_info["size_by_index"] = self.size_by_index(var_id, index_sets)

      data["integrators"].append(integrator_info)
      # pp(data["integrators"])
    # Information about the expressions
    data["expressions"] = []
    for expr in self.var_eq.expressions:
      expr_info = {}

      sys_counter = 1
      if len(expr) == 1:
        var_id, eq_id, top_ids, index_sets = expr[0]
        # TODO: Extend this to add all the other index sets needed
        index_sets.add("S")

        eq = self.all_equations.get(eq_id)
        if eq.is_integrator():
          continue

        if eq.is_explicit_for_var(var_id):
          expr_info["type"] = "simple"
          expr_info["id"] = eq_id
          expr_info["equations"] = [{
              "eq_id": eq_id,
              "var_id": var_id,
              "top_ids": top_ids,
              "index_sets": index_sets,
              "dependencies": eq.get_incidence_list(var_id),
          }]
        else:
          expr_info["type"] = "root"
          expr_info["init_guess"] = ["Initial_Guess"]
          expr_info["id"] = "root" + eq_id
          expr_info["equations"] = [{
              "eq_id": eq_id,
              "var_id": var_id,
              "top_ids": top_ids,
              "index_sets": index_sets,
              "dependencies": eq.get_incidence_list(var_id) + [var_id],
          }]

      else:
        expr_info["type"] = "system"
        expr_info["id"] = f"system{sys_counter}"
        sys_counter += 1
        expr_info["equations"] = []
        expr_info["init_guess"] = ["initial_guess"]

        part_counter = 1
        for var_id, eq_id, top_ids, index_sets in expr:
          # TODO: Extend this to add all the other index sets needed
          index_sets.add("S")
          eq = self.all_equations[eq_id]
          ini = str(part_counter)
          part_counter += self.size_by_index(var_id, index_sets)
          fin = str(part_counter - 1)
          expr_info["equations"].append({
              "eq_id": eq_id,
              "var_id": var_id,
              "top_ids": top_ids,
              "interval": ini + ":" + fin,
              "index_sets": index_sets,
              "dependencies": eq.get_incidence_list(),
          })

      data["expressions"].append(expr_info)
      data["solvers"] = {
          "root": "fzero",
          "sys_of_equations": "fsolve",
      }

    return data

  def size_by_index(self, var_id, index_sets):
    # TODO: Rewrite this, make a separation between index and index sets
    var_data = self.all_variables[var_id]

    index_structures = var_data.index_structures
    index_sets_info = self.var_eq.top_graph.graph["index_sets_info"]

    index_sizes = []

    # TODO: This needs to come from the entity itself
    index_sets.add("S")

    # TODO: Remove this when we only have one set of indices
    index_sets_total = copy.deepcopy(index_sets_info["specific"])
    index_sets_total.update({
        self.all_indices[key].get_translation(self.language): index_sets_info["general"][key]
        for key in index_sets_info["general"]
    })

    pp(index_sets_total)

    for idx_id in index_structures:
      index_label = self.all_indices[idx_id].get_translation("internal_code")
      index_union = set()
      for idx in index_sets:
        if index_label[0] == idx[0]:
          index_union.update(index_sets_total[idx])
      index_sizes.append(len(index_union))

    return index_sizes

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

  def join_sets(self, main_set: str, index_sets: Set[str]) -> List[str]:
    output = []
    for i in index_sets:
      if main_set[0] == i[0]:
        output.append(i)

    return output

  def specific_sets(
      self,
      var_id: str,
      index_sets: Set[str],
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
      index_sets: Set[str],
  ) -> str:
    return self.var_label(var_id) + "(" + self.specific_sets(var_id, index_sets) + ")"

  def dependencies(self, expr_info: Dict) -> str:
    if expr_info["type"] in ["simple", "root"]:
      eq_info = expr_info["equations"][0]
      expr_dependencies = [self.var_label(var_id)
                           for var_id in eq_info["dependencies"]]
      # TODO: Extend to all main indices
      for main_idx in ["N", "A", "S"]:
        full_set = self.join_sets(main_idx, eq_info["index_sets"])
        # pp(full_set)
        if full_set:
          if len(full_set) == 1:
            expr_dependencies.append(full_set[0])
          else:
            expr_dependencies.append("indexunion(" + ", ".join(full_set) + ")")
    else:
      all_dependencies = set()
      all_index_sets = set()
      for eq_info in expr_info["equations"]:
        all_index_sets.update(eq_info["index_sets"])
        all_dependencies.update(eq_info["dependencies"])

      expr_dependencies = [self.var_label(var_id)
                           for var_id in list(all_dependencies)]
      expr_dependencies.extend(list(all_index_sets))

    return ", ".join(expr_dependencies)

  def arguments(self, eq_info: Dict) -> str:
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
        self.language,
        self.all_variables,
        self.all_indices
    )
    translated_eq = parser.parse(global_id_rpr)

    return translated_eq

  def main_index(self, var_id: str) -> str:
    var_data = self.all_variables[var_id]
    index_structures = var_data.index_structures

    return self.all_indices[index_structures[0]]["aliases"]["internal_code"][0]
