"""
from https://gis.stackexchange.com/questions/428399/adding-dynamic-filter-to-tablewidget-with-pyqgis
"""
from PyQt5.QtWidgets import *
class MyWindow(QDialog):

  def __init__(self, parent):
    super().__init__(parent)

    layout = QVBoxLayout()
    self.edit = QLineEdit()
    self.edit.textChanged.connect(self.filter)
    layout.addWidget(self.edit)

    data = [
            ('France', 'Paris'),
            ('United Kingdom', 'London'),
            ('Italy', 'Rome'),
            ('Germany', 'Berlin')
            ]

    self.tableWidget = QTableWidget(self)
    self.tableWidget.setRowCount(4)

    self.tableWidget.setColumnCount(2)
    self.tableWidget.setHorizontalHeaderLabels(['Country', 'Capital'])

    for row in range(4):
      for column in range(2):
        item = QTableWidgetItem(data[row][column])
        self.tableWidget.setItem(row, column, item)

    self.tableWidget.horizontalHeader().setStretchLastSection(True)
    self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

    layout.addWidget(self.tableWidget)
    self.setLayout(layout)

  def filter(self, filter_text):
    for i in range(self.tableWidget.rowCount()):
      for j in range(self.tableWidget.columnCount()):
        item = self.tableWidget.item(i, j)
        match = filter_text.lower() not in item.text().lower()
        self.tableWidget.setRowHidden(i, match)
        if not match:
          break


dlg = MyWindow(mainWindow())
dlg.show()