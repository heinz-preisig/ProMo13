#
# https://stackoverflow.com/questions/5553342/adding-images-to-a-qtablewidget-in-pyqt
#

import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.ui_radio_selector_w_scroll import Ui_Form


class ImageWidget(QtWidgets.QWidget):

  def __init__(self, imagePath, parent):
    super(ImageWidget, self).__init__(parent)
    self.picture = QtGui.QPixmap(imagePath)
    # print("size picture :", self.picture.size())

  def paintEvent(self, event):
    painter = QtGui.QPainter(self)
    painter.drawPixmap(0, 0, self.picture)


class TableWidget(QtWidgets.QTableWidget):

  def setImage(self, row, col, imagePath):
    image = ImageWidget(imagePath, self)
    self.setCellWidget(row, col, image)


  def buildTable(self, item_range):
    template = "equation_%s.png"
    row_count = self.rowCount()
    l = len(item_range)+1
    for i in range(row_count, row_count+l):
      self.setRowCount(i)

    count = row_count
    for i in item_range:
      f = template % i
      # print(f)
      self.setImage(count, 1, f)
      count += 1


  def getSize(self):
    size = self.size()
    print("table widget size ", size)
    return size.width(),size.height()

  def setSize(self, w_,h_):
    self.adjustSize()
    w,h = self.getSize()
    self.resize(w+w_,h+h_)

class PictureTable(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_Form()
    self.tableWidget = TableWidget(0, 2)
    self.ui.setupUi(self)
    # self.tableWidget.resizeRowsToContents()

  def add(self,item_range):
    self.tableWidget.buildTable(item_range)
    self.ui.verticalLayout.addChildWidget(self.tableWidget)

  def getSize(self):
    size = self.tableWidget.size()
    print("table widget size ", size)
    return size.width(),size.height()

  def setSize(self, w_,h_):
    w,h = self.getSize()
    self.resize(w+w_,h+h_)

if __name__ == "__main__":
  app = QtWidgets.QApplication([])

  ui = PictureTable()
  item_range = [1, 2, 3, 4, 5, 7, 8, 10,]
  ui.add(item_range)
  ui.add(item_range)
  w,h =ui.tableWidget.getSize()
  ui.tableWidget.setMaximumHeight(h+50)
  ui.setMaximumHeight(h+50)
  ui.show()

  sys.exit(app.exec_())
