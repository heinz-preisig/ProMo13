#
# https://stackoverflow.com/questions/5553342/adding-images-to-a-qtablewidget-in-pyqt
#

from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class ImageWidget(QtWidgets.QWidget):

    def __init__(self, imagePath, parent):
        super(ImageWidget, self).__init__(parent)
        self.picture = QtGui.QPixmap(imagePath)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.picture)


class TableWidget(QtWidgets.QTableWidget):

    def setImage(self, row, col, imagePath):
        image = ImageWidget(imagePath, self)
        self.setCellWidget(row, col, image)

    def buildTable(self, range):
        self.pictures = "equation_%s.png"
        count = 0
        for i in range:
            f = "equation_%s.png"%i
            self.setImage(count,1,f)
            count += 1

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    range = [1, 2, 3, 4, 5, 7, 8, 10]
    tableWidget = TableWidget(len(range), 2)
    tableWidget.buildTable(range)
    tableWidget.show()
    sys.exit(app.exec_())
