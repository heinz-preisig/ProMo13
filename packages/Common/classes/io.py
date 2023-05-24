"""Contains functions to perform Input/Output"""
# TODO Move this file to correct location.

import json
import networkx as nx
import os
from typing import List, Dict, Optional, Tuple

from packages.Common.classes import equation
from packages.Common.classes import entity
from packages.Common.classes import variable
from packages.Common.classes import ontology
from packages.Common import resource_initialisation


def load_equations_from_file(
    ontology_name: str,
    eq_ids: Optional[List[str]] = None
) -> Dict[str, equation.Equation]:
  """Loads data from file to create Equation objects.

  Args:
      ontology_name (str): Name of the ontology.
      eq_ids (Optional[List[str]], optional): Ids of the equations that
        will be loaded. If **None** all equations will be loaded.
        Defaults to **None**.

  Returns:
      Dict[str, equation.Equation]: Data of the equations. The keys are
        the  equation ids and the corresponding values are Equation
        objects.
  """
  path = resource_initialisation.FILES[
      "global_equation_id"
  ] % ontology_name

  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)

  # from pprint import pprint as pp
  # pp(data)

  if eq_ids is None:
    eq_ids = data.keys()

  languages = ["matlab"]
  for lang in languages:
    lang_path = resource_initialisation.DIRECTORIES[
        "ontology_location"
    ] % ontology_name + "/equations_" + lang + ".json"

    with open(lang_path, "r", encoding="utf-8",) as file:
      lang_data = json.load(file)

    for eq_id in eq_ids:
      if "representation" not in data[eq_id]:
        data[eq_id]["representation"] = {}
      if lang not in data[eq_id]["representation"]:
        data[eq_id]["representation"][lang] = {}
      data[eq_id]["representation"][lang]["rhs"] = lang_data[eq_id]["rhs"]
      data[eq_id]["representation"][lang]["lhs"] = lang_data[eq_id]["lhs"]

  equations = {}
  for eq_id in eq_ids:
    equations[eq_id] = equation.Equation(
        eq_id,
        resource_initialisation.FILES["latex_img"] % (ontology_name, eq_id),
        data[eq_id]["lhs"],
        data[eq_id]["rhs"],
        data[eq_id]["network"],
        data[eq_id]["representation"],
    )

  return equations


def load_entities_from_file(
    ontology_name: str,
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
  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)
  # from pprint import pprint as pp
  # pp(data)
  # TODO Change behaviour in case of no data.
  if not data:
    return {}

  if entity_names is None:
    entity_names = data.keys()

  # TODO Find a more elegant way of doing this
  all_equations = load_equations_from_file(ontology_name)

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


def load_variables_from_file(
    ontology_name: str,
    variable_ids: Optional[List[str]] = None,
) -> Tuple[Dict[str, variable.Variable], Dict[str, str]]:
  # """Loads data from file to create Variable objects.

  # Args:
  #     ontology_name (str): _description_
  #     variable_names (Optional[List[str]]): Ids of the variables that
  #     will be loaded. If **None** all variables are loaded. Defaults to
  #     **None**.

  # Returns:
  #     Dict[str, entity.Entity]: Data of the variables. The keys are
  #       the ids of the variables and the corresponding values are
  #       Variable objects.
  # """

  path = resource_initialisation.FILES["variables_file"] % ontology_name
  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)

  # TODO Change behaviour in case of no data.
  if not data:
    return {}

  # Loading the indices
  indices = {}
  # TODO: Remove when indices is a list of strings instead of int.
  for index, index_data in data["indices"].items():
    indices[index] = index_data
    if index_data["type"] == "block_index":
      indices[index]["indices"] = [str(i) for i in index_data["indices"]]

  # Loading the variables
  data = data["variables"]
  if variable_ids is None:
    variable_ids = data.keys()

  variables = {}
  for var_id in variable_ids:
    variables[var_id] = variable.Variable.from_dict(
        var_id,
        resource_initialisation.FILES["latex_img"] % (ontology_name, var_id),
        data[var_id],
    )

  return (variables, indices)


def load_topology_from_file(
    ontology_name: str,
    model_name: str,
    all_entities: Dict[str, entity.Entity]
) -> nx.Graph:
  index_sets = {
      "general": {},
      "specific": {},
  }
  path = resource_initialisation.FILES["model_flat_file"] % (
      ontology_name,
      model_name,
  )
  with open(path, "r", encoding="utf-8",) as file:
    data = json.load(file)

  topology_graph = nx.Graph()
  matrices = {
      "Dc_N_A": {
          "rows": [],
          "cols": [],
          "vals": [],
      },
      "Dc_NS_AS": {
          "rows": [],
          "cols": [],
          "vals": [],
      },
  }

  # For the species
  species_set = set()
  for domain_species in data["typed_token_lists"]["mass"].values():
    species_set.update(domain_species)
  species_list = list(species_set)
  species_list.sort()
  species_index = {spec: str(i)
                   for i, spec in enumerate(species_list, start=1)}

  # For the nodes
  nodes_index = {}
  node_species_index = {}
  offset = 1
  index_sets["general"]["N"] = []
  index_sets["general"]["N & S"] = []
  for i, old_node_index in enumerate(data["nodes"], start=1):
    node = str(i)
    node_data = data["nodes"][old_node_index]

    # Mapping all the simple nodes to have indexes in [1, N].
    nodes_index[old_node_index] = node

    # Mapping the species inside the nodes.
    node_species = [species_index[s] for s in node_data["tokens"]["mass"]]
    node_species_index[node] = {
        spec: (j + offset) for j, spec in enumerate(node_species)
    }
    node_species_index[node]["ini"] = offset
    offset += len(node_species)
    node_species_index[node]["fin"] = offset - 1

    # For the index_sets
    index_sets["general"]["N"].append(node)
    index_sets["general"]["N & S"].append(node_species)

    # TODO The domain is usually found using the ontology container
    # Find a way of obtaining this info here.
    networks = ["macroscopic"]
    intra_domains = {"macroscopic": ["solid", "liquid", "gas"]}

    entity_network = node_data["network"]
    for nw in networks:
      if entity_network in intra_domains[nw]:
        entity_domain = nw

    entity_type = node_data["type"]
    # TODO Check what happens with multiple tokens
    token = list(node_data["tokens"].keys())[0]
    entity_variant = node_data["variant"]
    ent_name = f"{entity_domain}.node.{entity_type}|{token}.{entity_variant}"

    # TODO Check if this is always the case
    is_reservoir = (entity_type == "constant|infinity")

    topology_graph.add_node(
        "N" + node,
        entity=all_entities[ent_name],
        inst_info=data["instantiation_info"]["nodes"][old_node_index],
        is_reservoir=is_reservoir,
    )

    idx_set = all_entities[ent_name].index_set
    # print(ent_name)
    if idx_set not in index_sets["specific"]:
      index_sets["specific"][idx_set] = []

    index_sets["specific"][idx_set].append(node)

  # For the arcs
  arc_species_index = {}
  offset = 1
  index_sets["general"]["A"] = []
  index_sets["general"]["A & S"] = []
  for i, old_arc_index in enumerate(data["arcs"], start=1):
    arc = str(i)
    arc_data = data["arcs"][old_arc_index]

    # Mapping the species inside the arcs.
    # TODO Homogenize the keys in nodes and arcs.
    arc_species = [species_index[s] for s in arc_data["typed_tokens"]]
    arc_species_index[arc] = {
        spec: (j + offset) for j, spec in enumerate(arc_species)
    }
    arc_species_index[arc]["ini"] = offset
    offset += len(node_species)
    arc_species_index[arc]["fin"] = offset - 1

    # For the index_sets
    index_sets["general"]["A"].append(arc)
    index_sets["general"]["A & S"].append(arc_species)

    # TODO The domain is usually found using the ontology container
    # Find a way of obtaining this info here.
    networks = ["macroscopic"]
    intra_domains = {"macroscopic": ["solid", "liquid", "gas"]}
    entity_network = arc_data["network"]
    for nw in networks:
      if entity_network in intra_domains[nw]:
        entity_domain = nw

    entity_type = arc_data["mechanism"] + "|" + arc_data["nature"]
    # TODO Check what happens with multiple tokens
    token = arc_data["token"]
    entity_variant = arc_data["variant"]
    ent_name = f"{entity_domain}.arc.{entity_type}|{token}.{entity_variant}"

    topology_graph.add_node(
        "A" + arc,
        entity=all_entities[ent_name],
        inst_info=data["instantiation_info"]["arcs"][old_arc_index],
        is_reservoir=False,
    )

    idx_set = all_entities[ent_name].index_set
    if idx_set not in index_sets["specific"]:
      index_sets["specific"][idx_set] = []

    index_sets["specific"][idx_set].append(arc)

    # Connections and matrix building
    node1 = nodes_index[str(arc_data["source"])]
    node2 = nodes_index[str(arc_data["sink"])]

    topology_graph.add_edge("A" + arc, "N" + node1)
    topology_graph.add_edge("A" + arc, "N" + node2)

    # TODO Generalize for all mechanisms and tokens
    if (
        arc_data["token"] == "mass" and
        arc_data["mechanism"] == "convection"
    ):
      matrices["Dc_N_A"]["rows"].extend([int(node1), int(node2)])
      matrices["Dc_N_A"]["cols"].extend([int(arc)]*2)
      matrices["Dc_N_A"]["vals"].extend([-1, 1])

      for spec in arc_species:
        matrices["Dc_NS_AS"]["rows"].extend([
            node_species_index[node1][spec],
            node_species_index[node2][spec],
        ])
        matrices["Dc_NS_AS"]["cols"].extend(
            [arc_species_index[arc][spec]]*2
        )
        matrices["Dc_NS_AS"]["vals"].extend([-1, 1])

  # TODO See how to link this with the equation composer
  matrices["V_60"] = matrices["Dc_N_A"]             # Fc_N_A
  matrices["V_61"] = matrices["Dc_NS_AS"]           # Fc_NS_AS
  matrices["V_66"] = matrices["Dc_N_A"]             # Dc_N_A
  matrices["V_67"] = matrices["Dc_NS_AS"]           # Dc_NS_AS

  del matrices["Dc_N_A"]
  del matrices["Dc_NS_AS"]

  # TODO Generalize for all indexes
  nr_nodes = len(data["nodes"])
  nr_arcs = len(data["arcs"])
  nr_specs = len(species_list)
  # TODO Probably change this
  index_sets["general"]["S"] = [str(x) for x in range(1, nr_specs + 1)]

  topology_graph.graph["index_sets_info"] = index_sets

  topology_entity = entity.Entity(
      "Topology",
      None,
      {},
      [],
      [],
      [],
      list(matrices.keys())
  )
  topology_graph.add_node(
      "T",
      entity=topology_entity,
      inst_info=matrices,
      is_reservoir=False,
  )

  for node in topology_graph:
    if node != "T":
      topology_graph.add_edge("T", node)

  # from pprint import pprint as pp
  # pp(topology_graph.graph["index_info"])

  return topology_graph


def get_available_ontologies():
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
    data = json.dump(all_entities, file, cls=EntityJSONEncoder)


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
