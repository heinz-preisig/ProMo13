
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class KindForMind(object):
    pictures = "equation_%s.png"

    def THINK(self, PLEASE):
        table = QtWidgets.QTableWidget()
        table.setRowCount(8)
        table.setColumnCount(1)

        count = 0
        for i in [1,2,3,4,5,7,8,10]:
            f = self.pictures%i
            pic = QtGui.QPixmap(f)
            label = QtWidgets.QLabel(PLEASE)
            label.setPixmap(pic)
            table.insertRow(count)
            table.setCellWidget(count,1, label)
            count +=1
        print(count)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    PLEASE = QtWidgets.QWidget()
    ui = KindForMind()
    ui.THINK(PLEASE)
    PLEASE.show()
    sys.exit(app.exec_())