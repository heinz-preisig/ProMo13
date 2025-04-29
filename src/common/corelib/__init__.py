"""
CoreLib Package

This package contains the foundational classes that form the base of
ProMo. It includes essential building blocks that define the core data
structures and interfaces used throughout the application.
"""

from .data_types import CoreMap, CoreMapVariant, EquationMap, IndexMap, VariableMap
from .equation import Equation
from .index import Index
from .variable import Variable

__all__ = [
    "CoreMap",
    "CoreMapVariant",
    "Index",
    "IndexMap",
    "Variable",
    "VariableMap",
    "Equation",
    "EquationMap",
]
