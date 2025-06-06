import enum

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class PromoModule(enum.StrEnum):
    LINKER = "../packages/Common/icons/task_entity_generation.svg"
    INSTANTIATION = "../packages/Common/icons/task_instantiation.svg"


SPLASH_SCREEN_SIZE = QtCore.QSize(300, 300)


class ClickableSplashScreen(QtWidgets.QSplashScreen):
    clicked = QtCore.pyqtSignal()

    def __init__(self, module: PromoModule) -> None:
        pixmap = QtGui.QPixmap(module).scaled(
            SPLASH_SCREEN_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        super().__init__(pixmap)

    def mousePressEvent(self, a0: QtGui.QMouseEvent | None) -> None:
        self.clicked.emit()
