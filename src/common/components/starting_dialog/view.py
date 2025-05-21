from PySide6 import QtWidgets

from src.common.components.starting_dialog import view_ui


class StartingDialogView(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.ui = view_ui.Ui_Dialog()
        self.ui.setupUi(self)
