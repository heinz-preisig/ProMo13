from PySide6 import QtCore, QtWidgets

from src.common.components.starting_dialog.model import StartingDialogModel
from src.common.components.starting_dialog.view import StartingDialogView


class StartingDialogController(QtCore.QObject):
    def __init__(self, model: StartingDialogModel, view: StartingDialogView) -> None:
        super().__init__()

        self._model = model
        self._view = view

        self._view.ui.selection_list.setModel(self._model._ontologies_model)

        # Connectons from the View
        self._view.show_event_triggered.connect(self.on_show_event_triggered)

    def on_show_event_triggered(self) -> None:
        self._model.load_available_ontologies()
