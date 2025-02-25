from typing import List, Optional, Dict

IndexMap = Dict[str, "Index"]


class Index:
  def __init__(
      self,
      idx_id: str,
      type: str,
      label: str,
      network: List[str],
      aliases: Dict[str, str],
      IRI: str,
      indices: Optional[List[str]] = []
  ) -> None:
    self.idx_id = idx_id
    self.type = type
    self.label = label
    self.network = network
    self.aliases = aliases
    self.iri = IRI
    self.indices = indices

  def is_block_index(self) -> bool:
    if self.type == "block_index":
      return True

    return False

  def get_translation(self, language: str) -> Optional[str]:
    if language not in self.aliases:
      return None

    return self.aliases.get(language)

  def get_sub_indices(self) -> List[str]:
    return self.indices
