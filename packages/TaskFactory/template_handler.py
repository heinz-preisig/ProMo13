import copy
import jinja2
from typing import Dict, List, Tuple, Set, Optional
from pprint import pprint as pp

from packages.Common.classes import variable, equation
from packages.Common.classes import vareqdigraph
from packages.Common import resource_initialisation as ri

class TemplateHandler:
  def __init__(
    self,
    language: str,
    all_variables: Dict[str, variable.Variable],
    all_indices: Dict,
    all_equations: Dict[str, equation.Equation],
    vareq: vareqdigraph.VarEqDiGraph,
  ):
    self.language = language
    self.all_variables = all_variables
    self.all_indices = all_indices
    self.all_equations = all_equations
    self.var_eq = vareq

    self.enviroment = jinja2.Environment(
      loader=jinja2.FileSystemLoader(ri.DIRECTORIES["templates"]),
      trim_blocks=True,
      lstrip_blocks= True,
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
    # Changing the alias of the index to the language specific ones
    general_info = data["index_sets_info"]["general"]
    general_info_copy = general_info.copy()

    for alias, index_data in general_info_copy.items():
      for index_data in self.all_indices.values():
        if index_data["aliases"]["internal_code"] == alias:
          lang_alias = index_data["aliases"][self.language]
          general_info[lang_alias] = general_info.pop(alias)
          break

    # pp(data["index_sets_info"])
    # THIS COMES FROM THE USER
    is_sparse = True
    # Information about the initialization of all variables
    data["instantiations"] = []
    for var_id, inst_info in self.var_eq.inst_variables.items():
      var_data = self.all_variables[var_id]
      index_structures = var_data.index_structures

      index_sets = ", ".join(
        [
          self.all_indices[i]["aliases"][self.language] 
          for i in index_structures
        ]
      )
      index_labels = ", ".join(
        [
          self.all_indices[i]["aliases"][self.language] + "_lbl"
          for i in index_structures
        ]
      )

      data["instantiations"].append({
        "var_id": var_id,
        "comment": [var_data.doc],
        "dimension": inst_info["dimension"],
        "vals": inst_info["vals"],
        "index_labels": index_labels,
        "index_sets": index_sets,
        "is_sparse": is_sparse,
      })

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

      var_data = self.all_variables[var_id]
      index_structures = var_data.index_structures

      ini = str(count)
      count += self.size_by_index(var_id, index_sets)
      fin = str(count - 1)

      integrator_info["interval"] = ini + ":" + fin


      data["integrators"].append(integrator_info)
      # pp(data["integrators"])

    # Information about the expressions
    data["expressions"] = []
    for expr in self.var_eq.expressions:
      expr_info = {}

      sys_counter = 1
      if len(expr) == 1:
        var_id, eq_id, top_ids, index_sets = expr[0]
        eq = self.all_equations[eq_id]

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
    var_data = self.all_variables[var_id]

    index_structures = var_data.index_structures

    index_label = self.all_indices[index_structures[0]]["aliases"]["internal_code"]

    index_sets_info = self.var_eq.top_graph.graph["index_sets_info"]

    index_union = set()
    for idx in index_sets:
      if index_label[0] == idx[0]:
        index_union.update(index_sets_info["specific"][idx])

    sum = 0
    # pp(index_sets_info)
    for i in index_union:
      element = index_sets_info["general"][index_label][int(i) - 1]
      if isinstance(element, list):
        sum += len(element)
      else:
        sum += 1

    return sum

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
    return self.all_variables[var_id].aliases[self.language]
  
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
      index_label = self.all_indices[idx]["aliases"]["internal_code"]
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
      expr_dependencies = [self.var_label(var_id) for var_id in eq_info["dependencies"]]
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

      expr_dependencies = [self.var_label(var_id) for var_id in list(all_dependencies)]
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
  def eq_label(self, eq_id:str, side:str) -> str:
    return self.all_equations[eq_id].representation[self.language][side]
  
  def main_index(self, var_id: str) -> str:
    var_data = self.all_variables[var_id]
    index_structures = var_data.index_structures

    return self.all_indices[index_structures[0]]["aliases"]["internal_code"][0]
