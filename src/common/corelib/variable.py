import attrs

from . import index

type VariableMap = dict[str, Variable]


@attrs.define
class Variable:
    identifier: str
    label: str = ""
    doc: str = ""
    indices: list[index.Index] = attrs.Factory(list)
