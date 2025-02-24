import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton
#
# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setGeometry(300, 300, 300, 220)
#         self.setWindowTitle('Hello World')
#         self.show()
#
#     def closeEvent(self, event):
#         reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
#         QMessageBox.Yes | QMessageBox.No | QMessageBox.No, QMessageBox.No)
#         if reply == QMessageBox.Yes:
#             event.accept()
#         else:
#             event.ignore()
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     sys.exit(app.exec_())


def window():
  app = QApplication(sys.argv)
  w = QWidget()
  b = QPushButton(w)
  b.setText("Show message!")

  b.move(50, 50)
  b.clicked.connect(showdialog)
  w.setWindowTitle("PyQt Dialog demo")
  w.show()
  sys.exit(app.exec_())


def showdialog():
  msg = QMessageBox()
  msg.setIcon(QMessageBox.Information)

  msg.setText("This is a message box")
  msg.setInformativeText("This is additional information")
  msg.setWindowTitle("MessageBox demo")
  msg.setDetailedText("The details are as follows:")
  # msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
  msg.addButton("connect",QMessageBox.ActionRole)
  msg.addButton("gugus", QMessageBox.ActionRole)

  # if msg.buttonClicked:
  #   print("gugus")
  # else:
  #   print("not")

  retval = msg.exec_()
  print(retval)

def on_connectButton_pressed():
  print("connect button pressed")


def msgbtn(i):
  print
  "Button pressed is:", i.text()


if __name__ == '__main__':
  window()