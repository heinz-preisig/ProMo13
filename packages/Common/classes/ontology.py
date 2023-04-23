class Ontology:
  def __init__(self, ontology_tree):
    self.tree = ontology_tree

  # TODO: FIX this function, remember that new entity elements are QModel indexes
  def get_ontology_tree_info(self, selector: int, data):
    ent_type, network, tokens, mechanism, *rest = data
    # print(data)
    if selector == 1:
      # top_networks = []
      # for network in self.tree:
      #     if len(self.tree[network]["parents"]) == 1 and self.tree[network]["parents"][0] == "root":
      #         top_networks.append(network)

      # TODO Fix this with a method to obtain the top networks

      # return top_networks
      return ["control", "macroscopic", "material", "reactions"]
    elif selector == 2:
      if ent_type == "arc":
        return list(self.tree[network]["structure"][ent_type].keys())

      if ent_type == "node":
        return list(self.tree[network]["structure"]["token"].keys())

      return None
    elif selector == 3:
      if ent_type == "arc":
        return list(self.tree[network]["structure"][ent_type][tokens].keys())

      if ent_type == "node":
        return list(self.tree[network]["structure"][ent_type].keys())

      return None
    elif selector == 4:
      if ent_type == "arc":
        return self.tree[network]["structure"][ent_type][tokens][mechanism]

      if ent_type == "node":
        return self.tree[network]["structure"][ent_type][mechanism]
      return None

    return None
