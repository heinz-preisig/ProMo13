from dataclasses import dataclass, field
import datetime
from enum import Enum
import json
from typing import Any, Dict, List, Tuple, Union

from src.common import corelib

_EPOCH = datetime.date(1970, 1, 1)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

VariableMap = Dict[str, "Variable"]
EquationMap = Dict[str, "Equation"]


class VariableTag(Enum):
  NOTAG = "none"
  CONSTANT = "constant"


@dataclass
class Variable:
  identifier: str
  iri: str = ""
  tag: VariableTag = VariableTag.NOTAG
  label: str = ""
  aliases: Dict[str, str] = field(default_factory=dict)
  compiled_lhs: Dict[str, str] = field(default_factory=dict)
  doc: str = ""
  index_structures: List[corelib.Index] = field(default_factory=list)
  equations: List["Equation"] = field(default_factory=list)
  network: str = "str"
  port_variable: bool = False
  tokens: List[str] = field(default_factory=list)
  units: List[int] = field(default_factory=list)
  created: datetime.date = _EPOCH
  modified: datetime.date = _EPOCH

  @classmethod
  def from_json(cls, identifier: str, data: Dict) -> "Variable":
    init_data = {}
    init_data["identifier"] = identifier
    init_data["iri"] = data["IRI"]
    init_data["label"] = data["label"]
    init_data["created"] = datetime.datetime.strptime(
        data["created"], _DATE_FORMAT)
    init_data["modified"] = datetime.datetime.strptime(
        data["modified"], _DATE_FORMAT)

    return cls(**init_data)


class EquationTag(Enum):
  NOTAG = "none"
  INTERFACE = "interface"
  INTEGRATOR = "integrator"


@dataclass
class Equation:
  identifier: str
  iri: str = ""
  tag: EquationTag = EquationTag.NOTAG
  variables: List[Variable] = field(default_factory=list)
  lhs: str = ""
  rhs: str = ""
  network: str = ""
  doc: str = ""
  created: datetime.date = _EPOCH
  modified: datetime.date = _EPOCH

  @property
  def dependent_variable(self):
    return self.variables[0]

  @property
  def independent_variables(self):
    return self.variables[1:]

  @classmethod
  def from_json(cls, identifier: str, data: Dict) -> "Equation":
    init_data = {}
    init_data["identifier"] = identifier

    if data["rhs"]["global_ID"].split()[0] == "O_8":
      init_data["tag"] = EquationTag.INTEGRATOR

    if data["type"] == "interface":
      init_data["tag"] = EquationTag.INTERFACE

    init_data["lhs"] = data["lhs"]["global_ID"]
    init_data["rhs"] = data["rhs"]["global_ID"]

    init_data["created"] = datetime.datetime.strptime(
        data["created"], _DATE_FORMAT)
    init_data["modified"] = datetime.datetime.strptime(
        data["modified"], _DATE_FORMAT)

    return cls(**init_data)


class VarEqJSONDecoder(json.JSONDecoder):
  def __init__(self):
    super().__init__(object_pairs_hook=self.custom_hook)
    self._data: Dict[str, Dict[str, Union[Variable, Equation]]] = {
        "variables": {},
        "equations": {},
    }
    self._map_var_eq = {}
    self._map_eq_var = {}

  def custom_hook(self, pairs: List[Tuple[str, Any]]) -> Dict[Any, Any]:
    for key, dict_data in pairs:
      # TODO: Change this as soon as the json files are refactored to
      # contain only one type of object. This is a workaround in the
      # meantime, to return a big dictas soon as we hit the top layer
      # of dicts in the json file.
      if key == "version":
        for var_id, var in self._data["variables"].items():
          var.equations = [
              self._data["equations"][eq_id]
              for eq_id in self._map_var_eq[var_id]
          ]

        for eq_id, eq in self._data["equations"].items():
          eq.variables = [
              self._data["variables"][var_id]
              for var_id in self._map_eq_var[eq_id]
          ]
        return self._data

      if key.startswith("V_"):
        new_variable = Variable.from_json(key, dict_data)
        self._data["variables"][new_variable.identifier] = new_variable
        self._map_var_eq[new_variable.identifier] = list(
            dict_data["equations"].keys())

      if key.startswith("E_"):
        new_equation = Equation.from_json(key, dict_data)
        self._data["equations"][new_equation.identifier] = new_equation

        # TODO: Use templates or regex instead of harcoded "V_"
        self._map_eq_var[new_equation.identifier] = [new_equation.lhs]
        self._map_eq_var[new_equation.identifier].extend([
            term
            for term in new_equation.lhs.split()
            if term.startswith("V_")
        ])

    return {key: dict_data for key, dict_data in pairs}
