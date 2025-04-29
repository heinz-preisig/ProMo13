import attrs

from . import index


@attrs.define
class Variable:
    identifier: str
    iri: str = ""
    label: str = ""
    doc: str = ""
    indices: list[index.Index] = attrs.Factory(list)
