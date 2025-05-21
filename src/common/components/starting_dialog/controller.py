from PySide6 import QtCore, QtWidgets

from src.common.components.starting_dialog.model import StartingDialogModel
from src.common.components.starting_dialog.view import StartingDialogView


class StartingDialogController(QtCore.QObject):
    def __init__(self, model: StartingDialogModel, view: StartingDialogView) -> None:
        super().__init__()

        self._model = model
        self._view = view

    def test_launch_dialog(self) -> None:
        self._view.exec_()
