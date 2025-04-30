import typing

from src.common import corelib
from src.common.io import IOContext, IOContextMember


class FakeStorage:
    def __init__(self) -> None:
        self._context_member_options: dict[IOContextMember, list[str]] = {
            IOContextMember.ONTOLOGY: [],
            IOContextMember.MODEL: [],
            IOContextMember.INSTANTIATION: [],
        }
        self._map_data: dict[str, dict[str, typing.Any]] = {}

    def validate_repository_location(self, location: str) -> None:
        pass

    def get_context_member_options(
        self, context_member: IOContextMember, context: IOContext
    ) -> list[str]:
        return self._context_member_options[context_member]

    def get_index_data(self, context: IOContext) -> typing.Any:
        ontology_name = context.ontology_name
        map_name = "index"

        return self._map_data[ontology_name][map_name]

    def get_variable_data(self, context: IOContext) -> typing.Any:
        ontology_name = context.ontology_name
        map_name = "variable"

        return self._map_data[ontology_name][map_name]

    def get_equation_data(self, context: IOContext) -> typing.Any:
        ontology_name = context.ontology_name
        map_name = "equation"

        return self._map_data[ontology_name][map_name]

    # Extra methods to change the state of the storage
    def set_context_member_options(
        self, context_member: IOContextMember, options: list[str]
    ) -> None:
        self._context_member_options[context_member] = options

    def set_map_data(self, ontology_name: str, full_map_data: typing.Any) -> None:
        self._map_data[ontology_name] = full_map_data


IDENTIFIER_KEY = "identifier"


def build_map(
    map_variant: corelib.CoreMapVariant, full_map_data: typing.Any
) -> corelib.CoreMap:
    match map_variant:
        case corelib.CoreMapVariant.INDEX:
            return build_index_map(full_map_data)
        case corelib.CoreMapVariant.VARIABLE:
            return build_variable_map(full_map_data)
        case corelib.CoreMapVariant.EQUATION:
            return build_equation_map(full_map_data)

    return {}


def build_index_map(full_map_data: typing.Any) -> corelib.IndexMap:
    index_map_data = full_map_data["index"]
    indices = {}
    for idx_data in index_map_data:
        new_index = corelib.Index(**idx_data)

        identifier = idx_data[IDENTIFIER_KEY]
        indices[identifier] = new_index

    return indices


def build_variable_map(full_map_data: typing.Any) -> corelib.VariableMap:
    indices = build_index_map(full_map_data)
    variable_map_data = full_map_data["variable"]

    INDICES_KEY = "indices"
    variables = {}
    for var_data in variable_map_data:
        instanced_indices = [indices[idx] for idx in var_data[INDICES_KEY]]
        instanced_var_data = var_data | {INDICES_KEY: instanced_indices}
        new_var = corelib.Variable(**instanced_var_data)

        identifier = var_data[IDENTIFIER_KEY]
        variables[identifier] = new_var

    return variables


def build_equation_map(full_map_data: typing.Any) -> corelib.EquationMap:
    variables = build_variable_map(full_map_data)
    equations_map_data = full_map_data["equation"]

    VARIABLES_KEY = "variables"
    equations = {}
    for eq_data in equations_map_data:
        instanced_variables = [variables[idx] for idx in eq_data[VARIABLES_KEY]]
        instanced_dict = {VARIABLES_KEY: instanced_variables}

        instanced_eq_data = eq_data | instanced_dict

        new_eq = corelib.Equation(**instanced_eq_data)

        identifier = eq_data[IDENTIFIER_KEY]
        equations[identifier] = new_eq

    return equations
