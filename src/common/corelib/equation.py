import attrs

from .variable import Variable


@attrs.define
class Equation:
    identifier: str
    variables: list[Variable]
