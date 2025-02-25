"""
CoreLib Package

This package contains the foundational classes that form the base of
ProMo. It includes essential building blocks that define the core data
structures and interfaces used throughout the application.
"""

from typing import Dict

from .index import Index, IndexMap
from .math_components import (
    Equation,
    EquationMap,
    EquationTag,
    VarEqJSONDecoder,
    Variable,
    VariableMap,
    VariableTag,
)
from .ontology_context import OntologyContext
from .entity import Entity, EntityMap, EntityMathGraph