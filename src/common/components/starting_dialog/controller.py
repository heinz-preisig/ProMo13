from PySide6 import QtCore

from src.common.components.starting_dialog.view import StartingDialogView


class StartingDialogController(QtCore.QObject):
    def __init__(self, view: StartingDialogView, options_list: list[str]) -> None:
        super().__init__()

        self._view = view
        self._model = QtCore.QStringListModel(options_list)
        self._view.ui.selection_list.setModel(self._model)

        # Connectons from the View
        # self._view.show_event_triggered.connect(self.on_show_event_triggered)

        self._view.ui.selection_list.selectionModel().currentChanged.connect(
            self._view.on_selection_changed
        )
        self._view.ui.selection_list.doubleClicked.connect(self.on_double_click)
        self._view.ui.pushLeft.clicked.connect(self._view.reject)
        self._view.ui.pushCentre.clicked.connect(self._view.accept)

    def on_double_click(self, index: QtCore.QModelIndex) -> None:
        if index.isValid():
            self._view.accept()
