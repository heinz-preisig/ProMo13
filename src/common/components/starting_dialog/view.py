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
    show_event_triggered = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.ui = view_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self._mouse_position = self.pos()

        self._configure_appearance()
        self._configure_buttons()

    def _configure_appearance(self) -> None:
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setStyleSheet(DIALOG_STYLE_SHEET)

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

    def on_list_populated(self) -> None:
        self._configure_size()
        self.ui.selection_list.clearSelection()
        self.ui.selection_list.setCurrentIndex(QtCore.QModelIndex())
        self.ui.pushCentre.hide()

    def _configure_size(self) -> None:
        list_size = self._calculate_selection_list_size()

        button_bar_width = 3 * ICON_SIZE

        components_width = max(list_size.width(), button_bar_width)

        dialog_width = components_width + 30
        dialog_height = list_size.height() + ICON_SIZE + 60

        self.ui.selection_list.resize(components_width, list_size.height())
        self.resize(dialog_width, dialog_height)

    def _calculate_selection_list_size(self) -> QtCore.QSize:
        width = 20
        height = 20

        list_view = self.ui.selection_list
        list_model = list_view.model()

        for row in range(list_model.rowCount()):
            index = list_model.index(row, 0)
            item_size = list_view.sizeHintForIndex(index)
            height += item_size.height()
            width = max(width, item_size.width())

        return QtCore.QSize(width, height)

    def on_selection_changed(self) -> None:
        self.ui.pushCentre.setVisible(True)

    def on_double_click(self, index: QtCore.QModelIndex) -> None:
        if index.isValid():
            self.accept()

    def showEvent(self, arg__1: QtGui.QShowEvent) -> None:
        super().showEvent(arg__1)
        self.show_event_triggered.emit()

    # The Mouse move and mouse press are used to move the dialog
    # This will not work if the system uses Wayland!
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self._mouse_position = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QtCore.QPoint(event.globalPos() - self._mouse_position)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._mouse_position = event.globalPos()
