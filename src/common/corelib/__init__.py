"""
CoreLib Package

This package contains the foundational classes that form the base of
ProMo. It includes essential building blocks that define the core data
structures and interfaces used throughout the application.
"""
from typing import Dict

from .index import Index
from .index import IndexMap

from .math_components import Equation
from .math_components import EquationTag
from .math_components import EquationMap
from .math_components import Variable
from .math_components import VariableTag
from .math_components import VariableMap
from .math_components import VarEqJSONDecoder

from .entity import Entity
from .entity import EntityMathGraph
