"""
CoreLib Package

This package contains the foundational classes that form the base of
ProMo. It includes essential building blocks that define the core data
structures and interfaces used throughout the application.
"""

from .equation import Equation, EquationMap
from .index import Index, IndexMap
from .variable import Variable, VariableMap

__all__ = ["Index", "IndexMap", "Variable", "VariableMap", "Equation", "EquationMap"]
