import enum

from src.common.corelib import equation, index, variable

type IndexMap = dict[str, index.Index]
type VariableMap = dict[str, variable.Variable]
type EquationMap = dict[str, equation.Equation]
type CoreMap = IndexMap | VariableMap | EquationMap


class CoreMapVariant(enum.StrEnum):
    INDEX = "index"
    VARIABLE = "variable"
    EQUATION = "equation"
