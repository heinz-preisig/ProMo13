import copy
import json
import stat
from pathlib import Path
from typing import Protocol

import attrs

from .ontology_context import OntologyContext
from .ontology_context_manager import OntologyContextManager


class IOManager(Protocol):
    def get_ontology_context(self) -> OntologyContext: ...
    def update_ontology_context(self, context: OntologyContext) -> None: ...


@attrs.define
class DefaultIOManager:
    _ontology_context_manager: OntologyContextManager = attrs.field(
        init=False, factory=OntologyContextManager
    )

    def get_ontology_context(self) -> OntologyContext:
        return self._ontology_context_manager.get_ontology_context()

    def update_ontology_context(self, context: OntologyContext) -> None:
        self._ontology_context_manager.update_ontology_context(context)
