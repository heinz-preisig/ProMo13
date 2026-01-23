from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class Interface(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Ready")
        self.button = QPushButton("Send")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
