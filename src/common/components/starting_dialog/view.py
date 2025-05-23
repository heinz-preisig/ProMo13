from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from src.common.components.starting_dialog import view_ui

ICON_ACCEPT_PATH = "packages/Common/icons/accept_button_hap.png"
ICON_REJECT_PATH = "packages/Common/icons/reject_button_hap.png"
ICON_SIZE = 52
ICON_STYLE_SHEET = """
    background-color: white;
    border-style: outset;
    border-width: 2px;
    border-radius: 26px;
    border-color: white;
    font: bold 14px;
    padding: 6px;
"""
DIALOG_STYLE_SHEET = """
    background-color: white;
"""


class StartingDialogView(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.ui = view_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self._mouse_position = self.pos()

        self._configure_appearance()
        self._configure_buttons()

        self.ui.pushLeft.clicked.connect(self.reject)

    def _configure_appearance(self) -> None:
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setStyleSheet(DIALOG_STYLE_SHEET)

        list_min_width = 20
        list_base_height = 20

        list_width = list_min_width
        list_height = list_base_height

        button_bar_width = 3 * ICON_SIZE

        components_width = max(list_width, button_bar_width)

        dialog_width = components_width + 30
        dialog_height = list_height + ICON_SIZE + 60

        self.ui.listWidget.resize(components_width, list_height)
        self.resize(dialog_width, dialog_height)

    def _configure_buttons(self) -> None:
        self.ui.pushLeft.setText("")
        self.ui.pushLeft.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.ui.pushLeft.setIcon(QtGui.QIcon(ICON_REJECT_PATH))
        self.ui.pushLeft.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.ui.pushLeft.setStyleSheet(ICON_STYLE_SHEET)
        self.ui.pushLeft.setToolTip("reject")

        self.ui.pushCentre.setText("")
        self.ui.pushCentre.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.ui.pushCentre.setIcon(QtGui.QIcon(ICON_ACCEPT_PATH))
        self.ui.pushCentre.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        self.ui.pushCentre.setStyleSheet(ICON_STYLE_SHEET)
        self.ui.pushCentre.setToolTip("accept")

        self.ui.pushCentre.hide()
        self.ui.pushRight.hide()

    # The Mouse move and mouse press are used to move the dialog
    # This will not work if the system uses Wayland!
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()
        print("Pressed")
        print(self.oldPos)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        print("Moving")
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        print(self.oldPos)
