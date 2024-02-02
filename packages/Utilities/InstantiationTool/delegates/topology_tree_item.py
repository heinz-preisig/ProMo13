import os
from pprint import pprint as pp

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

# TODO: Icons should be stored in resources
from packages.Common import resource_initialisation
from packages.shared_components import roles

CHECKBOX_SPACE = 20


class CustomTopologyItemDelegate(QtWidgets.QStyledItemDelegate):
  def paint(self, painter, option, index):
    # # Draw a rectangle around the space occupied by the text
    # border_color = QtGui.QColor(0, 0, 0)  # Set your desired border color
    # border_thickness = 2  # Set the thickness of the border as needed

    # painter.setPen(QtGui.QPen(border_color, border_thickness))
    # painter.setBrush(QtCore.Qt.NoBrush)
    # painter.drawRect(option.rect)

    super().paint(painter, option, index)
    if index.column() == 1:
      return

    item_name = index.data(roles.NAME_ROLE)

    icon_name = f"{index.data(roles.CLASS_ROLE)}.png"

    # Calculate the position to draw the custom icon
    icon_size = QtCore.QSize(24, 24)
    icon_margin = 5

    icon_x = option.rect.left() + CHECKBOX_SPACE + icon_margin
    icon_y = option.rect.center().y() - icon_size.height() // 2
    icon_position = QtCore.QPoint(icon_x, icon_y)

    icon_path = resource_initialisation.DIRECTORIES["icon_location"]

    icon = QtGui.QIcon(os.path.join(icon_path, icon_name))
    pixmap = icon.pixmap(icon_size)
    painter.drawPixmap(icon_position, pixmap)

    # Use the font metrics to measure text
    font = painter.font()
    font_metrics = QtGui.QFontMetrics(font)
    text_size = font_metrics.size(QtCore.Qt.TextSingleLine, item_name)

    # Calculate the position to draw the text
    text_x = icon_position.x() + icon_size.width() + icon_margin
    text_y = option.rect.center().y() + text_size.height() // 2
    text_position_rect = QtCore.QPoint(text_x, text_y - text_size.height())
    text_rect = QtCore.QRect(text_position_rect, text_size)

    # # Draw the text
    painter.drawText(text_rect, QtCore.Qt.AlignVCenter, item_name)
