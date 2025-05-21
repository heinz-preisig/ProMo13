from src.common.io import IOManager


class StartingDialogModel:
    def __init__(self, manager: IOManager) -> None:
        self._manager = manager
