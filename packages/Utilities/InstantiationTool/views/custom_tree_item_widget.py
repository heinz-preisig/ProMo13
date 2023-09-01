import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

# TODO: Icons should be stored in resources
from packages.Common import resource_initialisation

CHECKBOX_MARGIN = 5
ICON_MARGIN = 5
BUTTON_MARGIN = 5


class CustomTopologyTreeItemWidget(QtWidgets.QWidget):
  def __init__(
      self,
      name: str,
      icon_name: str,
      inst_value: str,
      parent=None
  ):
    super().__init__(parent)
    self.check_box = QtWidgets.QCheckBox("", parent)
    self.copy_button = QtWidgets.QPushButton("", parent)

    icon_path = resource_initialisation.DIRECTORIES["icon_location"]
    icon = QtGui.QIcon(os.path.join(icon_path, "copy.png"))
    self.copy_button.setIcon(icon)
    self.icon_name = icon_name
    self.main_text = name

  def paintEvent(self, event):
    painter = QtGui.QPainter(self)
    option = QtWidgets.QStyleOptionViewItem()
    option.initFrom(self)

    # Calculate positions for the checkbox
    check_box_rect = self.check_box.geometry()
    checkbox_x = CHECKBOX_MARGIN  # Adjust as needed
    checkbox_y = (self.height() - check_box_rect.height()) // 2

    check_box_rect.moveTopLeft(QtCore.QPoint(checkbox_x, checkbox_y))
    self.check_box.setGeometry(check_box_rect)

    # Calculate the position to draw the custom icon
    icon_size = QtCore.QSize(24, 24)
    icon_x = check_box_rect.right() + ICON_MARGIN
    icon_y = option.rect.center().y() - icon_size.height() // 2
    icon_position = QtCore.QPoint(icon_x, icon_y)

    icon_path = resource_initialisation.DIRECTORIES["icon_location"]

    icon = QtGui.QIcon(os.path.join(icon_path, self.icon_name))
    pixmap = icon.pixmap(icon_size)
    painter.drawPixmap(icon_position, pixmap)

    # Calculate the position to draw the text
    # Get the font metrics to measure text height
    font = painter.font()
    font_metrics = QtGui.QFontMetrics(font)
    text_size = font_metrics.size(QtCore.Qt.TextSingleLine, self.main_text)

    text_x = icon_position.x() + icon_size.width() + ICON_MARGIN
    text_y = option.rect.center().y() + text_size.height() // 2

    text_position_rect = QtCore.QPoint(text_x, text_y - text_size.height())
    text_rect = QtCore.QRect(text_position_rect, text_size)

    # Draw the text
    painter.drawText(text_rect, QtCore.Qt.AlignVCenter, self.main_text)

    # Calculate position for the button
    button_rect = self.copy_button.geometry()

    button_x = text_rect.right() + BUTTON_MARGIN
    button_y = (self.height() - button_rect.height()) // 2

    button_rect.moveTopLeft(QtCore.QPoint(button_x, button_y))
    self.copy_button.setGeometry(button_rect)
