import attrs

from .variable import Variable

type EquationMap = dict[str, Equation]


@attrs.define
class Equation:
    identifier: str
    variables: list[Variable]
