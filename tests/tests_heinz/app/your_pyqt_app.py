from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel("Hello from PyQt5 in Docker!")
label.show()
app.exec_()
