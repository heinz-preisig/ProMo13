import sys
from PyQt6.QtWidgets import QApplication
from backend_mod import Backend
from interface_mod import Interface


def main():
    app = QApplication(sys.argv)

    # Instantiate each once
    backend = Backend()
    interface = Interface()

    # Link them together using Signals and Slots
    # I -> B: Button click triggers backend method
    interface.button.clicked.connect(lambda: backend.handle_request("App Data"))

    # B -> I: Backend signal updates interface label
    backend.data_signal.connect(interface.label.setText)

    interface.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
