import os

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QStyleOptionViewItem, QWidget

# TODO: Icons should be stored in resources
from packages.Common import resource_initialisation
from packages.Utilities.InstantiationTool.views.custom_tree_item_widget import CustomTopologyTreeItemWidget


NAME_ROLE = QtCore.Qt.UserRole
ICON_ROLE = QtCore.Qt.UserRole + 1
INSTANTIATION_ROLE = QtCore.Qt.UserRole + 2

CHECKBOX_SPACE = 20


class CustomTopologyItemDelegate(QtWidgets.QStyledItemDelegate):
  def sizeHint(self, option, index):
    if index.column() == 1:
      return QtCore.QSize(10, option.rect.height())

    return super().sizeHint(option, index)
  # def createEditor(
  #     self,
  #     parent: QWidget,
  #     option: QStyleOptionViewItem,
  #     index: QtCore.QModelIndex
  # ) -> QWidget:
  #   # return super().createEditor(parent, option, index)
  #   item_name = index.data(NAME_ROLE)
  #   icon_name = f"{index.data(ICON_ROLE)}.png"
  #   instantiation_value = index.data(INSTANTIATION_ROLE)

  #   return CustomTopologyTreeItemWidget(item_name, icon_name, instantiation_value, parent)

  # def editorEvent(self, event, model, option, index):
  #   self.check_box = QtWidgets.QCheckBox

  #   return super().editorEvent(event, model, option, index)

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

    item_name = index.data(NAME_ROLE)
    icon_name = f"{index.data(ICON_ROLE)}.png"
    instantiation_value = index.data(INSTANTIATION_ROLE)

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

    # Draw a QLineEdit-like frame
    # Set up the style options for the box
    # BOX_PAD = 2
    # box_height = option.rect.height() - 2 * BOX_PAD
    # box_width = 40
    # box_x = text_rect.right() + BOX_PAD
    # box_y = option.rect.top() + BOX_PAD
    # box_rect = QtCore.QRect(box_x, box_y, box_width, box_height)
    # painter.drawRect(box_rect)

    # text_rect = box_rect.adjusted(2, 2, -2, -2)  # Adjust for padding
    # painter.drawText(text_rect, QtCore.Qt.AlignCenter, instantiation_value)

    # # Draw a rectangle around the space occupied by the text
    # # border_color = QtGui.QColor(0, 0, 0)  # Set your desired border color
    # # border_thickness = 2  # Set the thickness of the border as needed

    # # painter.setPen(QtGui.QPen(border_color, border_thickness))
    # # painter.setBrush(QtCore.Qt.NoBrush)
    # # painter.drawRect(text_rect)

    # # # Draw a rectangle around the entire painting area
    # # painter.setPen(QtGui.QPen(border_color, border_thickness))
    # # painter.setBrush(QtCore.Qt.NoBrush)  # To make the rectangle border-only
    # # painter.drawRect(option.rect)  # Draw a rectangle around the entire area

    # # # Draw a rectangle around the icon
    # # icon_rect = QtCore.QRect(icon_position, icon_size)
    # # painter.setPen(QtGui.QPen(border_color, border_thickness))
    # # painter.setBrush(QtCore.Qt.NoBrush)
    # # painter.drawRect(icon_rect)

    # # # Calculate the position to draw the instantiation value text box
    # # instantiation_x = text_position.x() + 100  # Adjust the position as needed
    # # instantiation_y = text_position.y()
    # # instantiation_position = QtCore.QPoint(instantiation_x, instantiation_y)

    # # # Draw a text box for the instantiation value
    # # painter.drawText(instantiation_position, str(instantiation_value))

    # # # Calculate the position to draw the small square-shaped button
    # # button_size = QtCore.QSize(10, 10)
    # # button_x = option.rect.right() - button_size.width() - \
    # #     5  # Adjust the 5 as needed
    # # button_y = icon_position.y()
    # # button_position = QtCore.QRect(
    # #     button_x, button_y, button_size.width(), button_size.height())

    # # # Draw a small square-shaped button
    # # painter.fillRect(button_position, QtGui.QColor(
    # #     255, 0, 0))  # Adjust color as needed
