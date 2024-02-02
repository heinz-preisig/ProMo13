"""Contains functions to perform Input/Output"""
# TODO Move this file to correct location.

import json
import os
import subprocess
import copy
from typing import List, Dict, Optional, Tuple, Union
from pprint import pprint as pp
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from packages.Common.classes import equation
from packages.Common.classes import entity
from packages.Common.classes import variable
from packages.Common.classes import index
from packages.Common.classes import ontology
from packages.Common.classes import modeller_classes
from packages.Common import resource_initialisation

from packages.Common.classes import equation_parser


@dataclass
class TranslationInfo:
  variable_with_index: str
  variable_no_index: str
  index: str
  addition: str
  substraction: str
  negation: str
  expand_product: str
  hadamard: str
  reduce_product: str
  power: str
  parentheses: str
  exp: str
  log: str
  ln: str
  sqrt: str
  sin: str
  cos: str
  tan: str
  asin: str
  acos: str
  atan: str
  abs: str
  neg: str
  diffspace: str
  left: str
  right: str
  inv: str
  sign: str
  par_diff: str
  total_diff: str
  instantiate: str
  product: str
  integral: str
  root: str


def load_translation_info_from_file(
    language: str
) -> TranslationInfo:
  # TODO: Add to FILES in the resource initialization.
  packages_path = resource_initialisation.DIRECTORIES["packages"]
  remaining_path = (
      f"Utilities/TranslationManager/resources/language_configurations/"
      f"{language}/translation_template.json"
  )
  path = os.path.join(packages_path, remaining_path)

  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)

  info = TranslationInfo(**data)

  return info


def save_arc_options_to_file(ontology_name: str, arc_options: Dict[str, Dict[str, str]]):
  # TODO: Merge it with write entities to file
  path = resource_initialisation.FILES[
      "arc_options"
  ] % ontology_name
  with open(path, "w", encoding="utf-8",) as file:
    json.dump(arc_options, file, indent=4)


def translate_equations(ontology_name: str, language: str):
  # TODO: Maybe move this function to a different module (Utils)
  # TODO: Make a check if the equations need to be translated

  # TODO: Change this and pass it as arguments
  all_variables, all_indices, all_equations = load_var_idx_eq_from_file(
      ontology_name
  )

  parser = equation_parser.EquationParser(language, all_variables, all_indices)

  data_translated_equations = {}

  for eq_id, eq in all_equations.items():
    equation_global_id = eq.get_translation("global_ID")
    data_translated_equations[eq_id] = {
        "lhs": parser.parse(equation_global_id.get("lhs")),
        "rhs": parser.parse(equation_global_id.get("rhs"))
    }

  return data_translated_equations


def load_var_idx_eq_from_file(
    ontology_name: str,
) -> Tuple[
    Dict[str, variable.Variable],
    Dict[str, index.Index],
    Dict[str, equation.Equation],
]:
  path = resource_initialisation.FILES["variables_file"] % ontology_name

  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)

  # TODO Change behaviour in case of no data.
  if not data:
    return {}

  # Loading the indices
  indices = {}
  for idx_id, idx_info in data["indices"].items():
    # TODO: Go over the tokens in the indices
    del idx_info["tokens"]
    indices[idx_id] = index.Index(idx_id, **idx_info)

  # Loading the variables
  all_var_data = data["variables"]

  variables = {}
  equations = {}
  for var_id, var_info in all_var_data.items():
    eq_list = []
    for eq_id, eq_info in var_info["equations"].items():
      # TODO: Remove when this is no longer used.
      del eq_info["incidence_list"]

      eq_list.append(eq_id)

      equations[eq_id] = equation.Equation(
          eq_id,
          resource_initialisation.FILES["latex_img"] % (ontology_name, eq_id),
          **eq_info,
      )
    var_info["equations"] = eq_list

    variables[var_id] = variable.Variable(
        var_id,
        resource_initialisation.FILES["latex_img"] % (ontology_name, var_id),
        **var_info,
    )

  return (variables, indices, equations)


def load_entities_from_file(
    ontology_name: str,
    all_equations: Dict[str, equation.Equation],
    entity_names: Optional[List[str]] = None
) -> Dict[str, entity.Entity]:
  # """Loads data from file to create Entity objects.

  # Args:
  #     path (str): Path to the entity file.
  #     all_equations (Dict[str, equation.Equation]): All the equations
  #         in the Ontology. The keys are equation ids and the values are
  #         Equation objects.
  #     entity_names (list[str]): Names of the entities that will be
  #     loaded. If **None** all entities are loaded. Defaults to **None**.

  # Returns:
  #     list[Entity]: Contains instances of Entity with data loaded from
  #       the specified file.

  # Args:
  #     ontology_name (str): Name of the ontology.
  #     all_equations (Dict[str, equation.Equation]): Data of all
  #       equations. The keys are the equation ids and the corresponding
  #       values are Equation objects.
  #     entity_names (Optional[List[str]], optional): Names of the
  #       entities that will be loaded. If **None** all entities are
  #       loaded. Defaults to **None**.

  # Returns:
  #     Dict[str, entity.Entity]: Data of the entities. The keys are
  #       the names of the entities and the corresponding values are
  #       Entity objects.
  # """
  path = resource_initialisation.FILES[
      "variable_assignment_to_entity_object"
  ] % ontology_name

  # TODO: This file needs to be created empty when the ontology is
  # created. In here should be only an exception in case the file is not found.

  # # If the file doesnt exists it creates a new one
  # if not os.path.isfile(path):
  #   with open(path, "w", encoding="utf-8",) as file:
  #     json.dump({}, file, indent=4)
  #   return {}

  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)
  # from pprint import pprint as pp
  # pp(data)
  # TODO Change behaviour in case of no data.
  if not data:
    return {}

  if entity_names is None:
    entity_names = data.keys()

  entities = {}
  for ent_name in entity_names:
    if ent_name not in data:
      print(ent_name + " not found.")
      continue

    new_entity = entity.Entity(
        ent_name,
        all_equations,
        data[ent_name]["index_set"],
        data[ent_name]["integrators"],
        data[ent_name]["var_eq_forest"],
        data[ent_name]["init_vars"],
        data[ent_name]["input_vars"],
        data[ent_name]["output_vars"],
    )
    # TODO Check why it cant be stored as base#
    if "base_" in ent_name:
      ent_name = ent_name.replace("base_", "base#")

    entities[ent_name] = new_entity

  return entities


def load_ontology_from_file(ontology_name: str) -> ontology.Ontology:
  path = resource_initialisation.FILES["ontology_file"] % ontology_name
  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)

  return ontology.Ontology(data["ontology_tree"])


def load_topology_objects(
    ontology_name: str,
    model_name: str,
    all_entities: Dict[str, entity.Entity],
) -> Dict[str, modeller_classes.TopologyObject]:
  path_old = resource_initialisation.FILES["model_file"] % (
      ontology_name,
      model_name,
  )
  path_new = path_old[:-5] + "_new.json"
  custom_decoder = modeller_classes.custom_decoder_factory(all_entities)
  with open(path_new, "r", encoding="utf-8",) as file:
    topology_objects = json.load(
        file,
        cls=custom_decoder,
    )

  return topology_objects


def save_topology_objects(
    ontology_name: str,
    model_name: str,
    all_topology_objects: Dict[str, modeller_classes.TopologyObject],
    file_path: Optional[str] = None,
) -> None:
  if file_path is None:
    path_old = resource_initialisation.FILES["model_file"] % (
        ontology_name,
        model_name,
    )
    path_new = path_old[:-5] + "_new.json"
  else:
    path_new = file_path

  with open(path_new, "w", encoding="utf-8",) as file:
    json.dump(
        all_topology_objects,
        file,
        cls=modeller_classes.CustomJSONEncoder,
        indent=4
    )


def get_available_ontologies() -> List[str]:
  location = resource_initialisation.DIRECTORIES["ontology_repository"]
  directories = [
      f.path
      for f in os.scandir(location)
      if f.is_dir() and not f.name.startswith('.')
  ]
  ontology_names = [
      os.path.splitext(os.path.basename(o))[0]
      for o in directories
  ]

  return ontology_names


def get_available_models(ontology_name: str) -> List[str]:
  ontology_path = resource_initialisation.DIRECTORIES["ontology_location"] % ontology_name
  models_path = ontology_path + "/models/"

  directories = [
      f.path
      for f in os.scandir(models_path)
      if f.is_dir() and not f.name.startswith('.')
  ]
  model_names = [
      os.path.splitext(os.path.basename(o))[0]
      for o in directories
  ]

  return model_names


def convert_model_file(ontology_name, model_name):
  path_old = resource_initialisation.FILES["model_flat_file"] % (
      ontology_name,
      model_name,
  )
  path_new = path_old[:-5] + "_new.json"

  with open(path_old, "r", encoding="utf-8",) as file:
    data = json.load(file)

  new_data = copy.deepcopy(data)

  # TODO: Change the way the data is read instead of changing the data
  if "instantiation_info" not in data:  # 2023-07-10 HAP
    data["instantiation_info"] = {"nodes": {},
                                  "arcs": {}
                                  }

  for nodeID in data["nodes"]:
    instantiated = data["nodes"][nodeID]["instantiated_variables"]
    data["instantiation_info"]["nodes"][nodeID] = instantiated

  for arcID in data["arcs"]:
    data["instantiation_info"]["arcs"][arcID] = data["arcs"][arcID]["instantiated_variables"]

  if "instantiation_info" not in new_data:  # 2023-07-10 HAP
    new_data["instantiation_info"] = {"nodes": {},
                                      "arcs": {}
                                      }

  list_ids = ["V_15", "V_66", "V_100", "V_164", "V_169", "V_110"]
  node_id_list = []

  for node_id in data["nodes"]:
    if node_id == "1":
      continue

    node_id_list.append(node_id)

  nr = 0
  for node_id in data["instantiation_info"]["nodes"]:
    new_node_id = node_id
    if node_id != "1":
      new_node_id = node_id_list[nr]
      nr += 1
    new_data["instantiation_info"]["nodes"][new_node_id] = data["instantiation_info"]["nodes"][node_id]

    for var_id, value in data["instantiation_info"]["nodes"][node_id].items():
      if var_id in list_ids:
        new_data["instantiation_info"]["nodes"][new_node_id][var_id] = [value]

  # HACK: Manually converting instantiated values to list
  for arc_id in data["arcs"]:
    new_data["instantiation_info"]["arcs"][arc_id] = {
        var_id: [value]
        for var_id, value in data["instantiation_info"]["arcs"][arc_id].items()
    }

    # new_data["instantiation_info"]["arcs"][arc]["V_168"] = ["3e-12"]

  with open(path_new, "w", encoding="utf-8",) as file:
    json.dump(new_data, file, indent=4)


def generate_latex_images(ontology_name):

  all_variables, _, all_equations = load_var_idx_eq_from_file(ontology_name)

  latex_folder_path = Path(
      resource_initialisation.DIRECTORIES["latex_doc_location"] % ontology_name
  )

  latex_info = {}
  for var_id, var in all_variables.items():
    var_png_file_path = latex_folder_path / (var_id + ".png")
    if var_png_file_path.exists():
      png_mod_date = datetime.fromtimestamp(var_png_file_path.stat().st_mtime)
      var_mod_date = var.get_mod_date()
      if png_mod_date > var_mod_date:
        continue

    latex_info[var_id] = "$" + var.get_alias("latex") + "$"

  for eq_id, eq in all_equations.items():
    eq_png_file_path = latex_folder_path / (eq_id + ".png")
    if eq_png_file_path.exists():
      png_mod_date = datetime.fromtimestamp(eq_png_file_path.stat().st_mtime)
      eq_mod_date = eq.get_mod_date()
      if png_mod_date > eq_mod_date:
        continue
    latex_translation = eq.get_translation("latex")
    pp(latex_translation)
    latex_info[eq_id] = "$" + \
        latex_translation.get("lhs") + "=" + latex_translation.get("rhs") + "$"

  original_work_dir = os.getcwd()
  os.chdir(latex_folder_path)

  for file_name, latex_alias in latex_info.items():
    print(file_name)

    with open(file_name + ".tex", "w") as f:
      f.write("\\documentclass[border=1pt]{standalone}\n")
      f.write("\\usepackage{amsmath}\n")
      f.write("\\begin{document}\n")
      f.write(latex_alias)
      f.write("\\end{document}\n")

    subprocess.run(["latex", "-interaction=nonstopmode", file_name + ".tex"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["dvipng", "-D", "150", "-T", "tight", "-z", "9",
                    "-bg", "Transparent", "-o", file_name + ".png", file_name + ".dvi"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(file_name + ".tex")
    os.remove(file_name + ".aux")
    os.remove(file_name + ".log")
    os.remove(file_name + ".dvi")

  os.chdir(original_work_dir)


class EquationJSONEncoder(json.JSONEncoder):
  """Custom encoder for Equation objects."""

  def default(self, o):
    """Represents data from Equation objects as a dictionary.

    Args:
        obj (Equation): Equation object that will be encoded.

    Returns:
        dict: The dictionary representation of the Equation object. If
          the object is not an Equation instance then the default
          representation is returned.
    """
    if isinstance(o, equation.Equation):
      return o.convert_to_dict()
    return super().default(o)


def save_entities_to_file(ontology_name, all_entities):
  path = resource_initialisation.FILES[
      "variable_assignment_to_entity_object"
  ] % ontology_name
  with open(path, "w", encoding="utf-8",) as file:
    data = json.dump(all_entities, file, cls=EntityJSONEncoder, indent=4)


class EntityJSONEncoder(json.JSONEncoder):
  """Custom encoder for Entity objects."""

  def default(self, o):
    """Represents data from Equation objects as a dictionary.

    Args:
        o (Entity): Entity object that will be encoded.

    Returns:
        dict: The dictionary representation of the Entity object. If
          the object is not an Entity instance then the default
          representation is returned.
    """
    if isinstance(o, entity.Entity):
      return o.convert_to_dict()
    return super().default(o)


class VariableJSONEncoder(json.JSONEncoder):
  # """Custom encoder for Entity objects.

  # Only for backwards compatibility.
  # """
  def default(self, o):
    # """Represents data from Entity objects as a dictionary.

    # Args:
    #     o (Entity): Entity object that will be encoded.

    # Returns:
    #     dict: The dictionary representation of the Entity object. If
    #       the object is not an Entity instance then the default
    #       representation is returned.
    # """
    if isinstance(o, variable.Variable):
      return o.convert_to_dict()
    return super().default(o)
