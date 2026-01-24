from PyQt6.QtCore import QObject, pyqtSignal

class Backend(QObject):
    data_signal = pyqtSignal(str)

    def handle_request(self, msg):
        print(f"Backend processing: {msg}")
        self.data_signal.emit(f"Result for: {msg}")
