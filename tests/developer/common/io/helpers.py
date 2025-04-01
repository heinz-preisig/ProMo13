import typing

from src.common.corelib import (
    Equation,
    EquationMap,
    Index,
    IndexMap,
    Variable,
    VariableMap,
)
from src.common.io import IOContext, IOContextMember


class FakeStorage:
    def __init__(self) -> None:
        self._context_member_options: dict[IOContextMember, list[str]] = {}
        self._index_data: dict[str, typing.Any] = {}
        self._variable_data: dict[str, typing.Any] = {}
        self._equation_data: dict[str, typing.Any] = {}

    def validate_repository_location(self, location: str) -> None:
        pass

    def set_context_member_options(
        self, context_member: IOContextMember, options: list[str]
    ) -> None:
        self._context_member_options[context_member] = options

    def new_get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        return self._context_member_options[context_member]

    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        match context_member:
            case IOContextMember.ONTOLOGY:
                return ["VALID_ONTOLOGY", "ontologyOK"]
            case IOContextMember.MODEL:
                return ["VALID_MODEL", "modelOK"]
            case IOContextMember.INSTANTIATION:
                return ["VALID_INSTANTIATION", "instantiationOK"]

    def set_index_data(self, data: typing.Any, ontology_name: str) -> None:
        self._index_data[ontology_name] = data

    def get_index_data(self, context: IOContext) -> typing.Any:
        return self._index_data[context.ontology_name]

    def set_variable_data(self, data: typing.Any, ontology_name: str) -> None:
        self._variable_data[ontology_name] = data

    def get_variable_data(self, context: IOContext) -> typing.Any:
        return self._variable_data[context.ontology_name]

    def set_equation_data(self, data: typing.Any, ontology_name: str) -> None:
        self._equation_data[ontology_name] = data

    def get_equation_data(self, context: IOContext) -> typing.Any:
        return self._equation_data[context.ontology_name]


IDENTIFIER_KEY = "identifier"


def build_index_map(map_data: typing.Any) -> IndexMap:
    indices = {}
    for idx_data in map_data:
        new_index = Index(**idx_data)

        identifier = idx_data[IDENTIFIER_KEY]
        indices[identifier] = new_index

    return indices


def build_variable_map(map_data: typing.Any, indices: IndexMap) -> VariableMap:
    INDICES_KEY = "indices"
    variables = {}
    for var_data in map_data:
        instanced_indices = [indices[idx] for idx in var_data[INDICES_KEY]]
        instanced_var_data = var_data | {INDICES_KEY: instanced_indices}
        new_var = Variable(**instanced_var_data)

        identifier = var_data[IDENTIFIER_KEY]
        variables[identifier] = new_var

    return variables


def build_equation_map(map_data: typing.Any, variables: VariableMap) -> EquationMap:
    VARIABLES_KEY = "variables"

    equations = {}
    for eq_data in map_data:
        instanced_variables = [variables[idx] for idx in eq_data[VARIABLES_KEY]]
        instanced_dict = {VARIABLES_KEY: instanced_variables}

        instanced_eq_data = eq_data | instanced_dict

        new_eq = Equation(**instanced_eq_data)

        identifier = eq_data[IDENTIFIER_KEY]
        equations[identifier] = new_eq

    return equations
