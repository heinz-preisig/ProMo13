"""
CoreLib Package

This package contains the foundational classes that form the base of
ProMo. It includes essential building blocks that define the core data
structures and interfaces used throughout the application.
"""
from typing import Dict

from .entity import Entity
from .equation import Equation
from .index import Index
from .variable import Variable

EntityMap = Dict[str, Entity]
EquationMap = Dict[str, Equation]
IndexMap = Dict[str, Index]
VariableMap = Dict[str, Variable]
