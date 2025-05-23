from PySide6 import QtCore

from src.common import io


class StartingDialogModel:
    def __init__(self, manager: io.IOManager) -> None:
        self._manager = manager
        self.ontologies_model = QtCore.QStringListModel()

    def load_available_ontologies(self) -> None:
        available_ontologies = self._manager.get_context_member_valid_options(
            io.IOContextMember.ONTOLOGY
        )
        self.ontologies_model.setStringList(available_ontologies)
