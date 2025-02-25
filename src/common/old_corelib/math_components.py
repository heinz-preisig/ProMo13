import datetime
import json
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

from attrs import Factory, define

from src.common.old_corelib import Index

_EPOCH = datetime.date(1970, 1, 1)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

VariableMap = dict[str, "Variable"]
EquationMap = dict[str, "Equation"]


class VariableTag(Enum):
    NOTAG = "none"
    CONSTANT = "constant"


@define(eq=False)
class Variable:
    identifier: str
    iri: str = ""
    tag: VariableTag = VariableTag.NOTAG
    label: str = ""
    aliases: dict[str, str] = Factory(dict)
    compiled_lhs: dict[str, str] = Factory(dict)
    doc: str = ""
    index_structures: list[Index] = Factory(list)
    network: str = "str"
    port_variable: bool = False
    tokens: list[str] = Factory(list)
    units: list[int] = Factory(list)
    created: datetime.date = _EPOCH
    modified: datetime.date = _EPOCH

    @classmethod
    def from_json(cls, identifier: str, data: dict) -> "Variable":
        init_data = {}
        init_data["identifier"] = identifier
        init_data["iri"] = data["IRI"]
        init_data["label"] = data["label"]
        init_data["created"] = datetime.datetime.strptime(data["created"], _DATE_FORMAT)
        init_data["modified"] = datetime.datetime.strptime(
            data["modified"], _DATE_FORMAT
        )

        return cls(**init_data)


class EquationTag(Enum):
    NOTAG = "none"
    INTERFACE = "interface"
    INTEGRATOR = "integrator"


@define(eq=False)
class Equation:
    identifier: str
    iri: str = ""
    tag: EquationTag = EquationTag.NOTAG
    variables: list[Variable] = Factory(list)
    lhs: str = ""
    rhs: str = ""
    network: str = ""
    doc: str = ""
    created: datetime.date = _EPOCH
    modified: datetime.date = _EPOCH

    @property
    def dependent_variable(self) -> Variable:
        return self.variables[0]

    @property
    def independent_variables(self) -> list[Variable]:
        return self.variables[1:]

    @classmethod
    def from_json(cls, identifier: str, data: dict) -> "Equation":
        init_data = {}
        init_data["identifier"] = identifier

        if data["rhs"]["global_ID"].split()[0] == "O_8":
            init_data["tag"] = EquationTag.INTEGRATOR

        if data["type"] == "interface":
            init_data["tag"] = EquationTag.INTERFACE

        init_data["lhs"] = data["lhs"]["global_ID"]
        init_data["rhs"] = data["rhs"]["global_ID"]

        init_data["created"] = datetime.datetime.strptime(data["created"], _DATE_FORMAT)
        init_data["modified"] = datetime.datetime.strptime(
            data["modified"], _DATE_FORMAT
        )

        return cls(**init_data)


class VarEqJSONDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_pairs_hook=self.custom_hook)
        self._data: dict[str, dict[str, Variable | Equation]] = {
            "variables": {},
            "equations": {},
        }
        self._map_var_eq = {}
        self._map_eq_var = {}

    def custom_hook(self, pairs: list[tuple[str, Any]]) -> dict[Any, Any]:
        for key, dict_data in pairs:
            # TODO: Change this as soon as the json files are refactored to
            # contain only one type of object. This is a workaround in the
            # meantime, to return a big dictas soon as we hit the top layer
            # of dicts in the json file.
            if key == "version":
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
                    dict_data["equations"].keys()
                )

            if key.startswith("E_"):
                new_equation = Equation.from_json(key, dict_data)
                self._data["equations"][new_equation.identifier] = new_equation

                # TODO: Use templates or regex instead of harcoded "V_"
                self._map_eq_var[new_equation.identifier] = [new_equation.lhs]
                self._map_eq_var[new_equation.identifier].extend(
                    [term for term in new_equation.lhs.split() if term.startswith("V_")]
                )

        return {key: dict_data for key, dict_data in pairs}
