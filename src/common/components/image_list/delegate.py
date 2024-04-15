"""
Define a delegate for the ImageList component.

Classes:
    Provide custom rendering for the ImageList component.
"""
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

# TODO: Icons should be stored in resources
# TODO: Colors should come from the palette
# import os
# from packages.Common import resource_initialisation

from src.common import roles


class ImageItemDelegate(QtWidgets.QStyledItemDelegate):
  """
  Provide custom rendering for the ImageList component.

  Methods:
      :meth:`sizeHint`: Compute the size of the item.
      :meth:`paint`: Draw the item.
  """
  _NULL_PIXMAP_COLOR = QtGui.QColor(255, 200, 200)  # Light red
  _COVER_COLOR = QtGui.QColor(105, 232, 213, 92)  # Light blue
  _EVEN_ROW_COLOR = QtGui.QColor(240, 240, 240)  # Light gray
  _ODD_ROW_COLOR = QtGui.QColor(220, 220, 220)  # Dark gray

  def sizeHint(  # PyQt name pylint: disable=invalid-name
      self,
      option: QtWidgets.QStyleOptionViewItem,
      index: QtCore.QModelIndex
  ) -> QtCore.QSize:
    """Compute the size of the item.

    The size is always the size of the pixmap + a padding if the pixmap
    is valid. If not the size is 50px by 50px.

    option (QtWidgets.QStyleOptionViewItem): Parameters to draw the
    widget.
    index (QtCore.QModelIndex): Index of the item.
    """
    del option  # unused
    path = str(index.data(roles.IMAGE_PATH_ROLE))
    pixmap = QtGui.QPixmap(path)
    if pixmap.isNull():
      return QtCore.QSize(50, 50)

    pixmap_size = QtCore.QSize(pixmap.width(), pixmap.height())

    return pixmap_size + QtCore.QSize(10, 10)

  def paint(
      self,
      painter: QtGui.QPainter,
      option: QtWidgets.QStyleOptionViewItem,
      index: QtCore.QModelIndex,
  ) -> None:
    """Draw the item.

    If the pixmap is valid draw the pixmap, if not it will draw the id
    of the item. A cover is draw on top of the item if it is selected.

    Args:
        painter (QtGui.QPainter): High level interface to draw the
         widget.
        option (QtWidgets.QStyleOptionViewItem): Parameters to draw the
         widget.
        index (QtCore.QModelIndex): Index of the item.
    """

    path = str(index.data(roles.IMAGE_PATH_ROLE))
    pixmap = QtGui.QPixmap(path)

    if pixmap.isNull():
      self._paint_null_pixmap(painter, option, index)
    else:
      self._paint_valid_pixmap(painter, option, index, pixmap)

    if option.state & QtWidgets.QStyle.State_Selected:  # type: ignore
      self._paint_selection_cover(painter, option)

  def _paint_valid_pixmap(
      self,
      painter: QtGui.QPainter,
      option: QtWidgets.QStyleOptionViewItem,
      index: QtCore.QModelIndex,
      pixmap: QtGui.QPixmap,
  ) -> None:

    painter.save()
    self._setup_painter(painter)

    size = option.rect.size() - QtCore.QSize(10, 10)
    scaled_pixmap = pixmap.scaled(
        size,
        Qt.KeepAspectRatio,  # type: ignore
        Qt.SmoothTransformation,  # type: ignore
    )

    x = option.rect.x() + option.rect.width() / 2 - scaled_pixmap.width() / 2
    y = option.rect.y() + option.rect.height() / 2 - scaled_pixmap.height() / 2

    num_items = index.model().rowCount()
    if (num_items + index.row()) % 2 == 0:
      background_color = ImageItemDelegate._EVEN_ROW_COLOR
    else:
      background_color = ImageItemDelegate._ODD_ROW_COLOR
    painter.fillRect(option.rect, background_color)

    # painter.drawPixmap(x, y, scaled_pixmap)
    painter.drawPixmap(x, y, pixmap)

    painter.restore()

  def _paint_null_pixmap(
      self,
      painter: QtGui.QPainter,
      option: QtWidgets.QStyleOptionViewItem,
      index: QtCore.QModelIndex,
  ) -> None:
    """Draw when the pixmap is null

    The item will be rendered the item ID with red background
    """

    item_id = index.data(roles.ID_ROLE)

    painter.save()

    self._setup_painter(painter, ImageItemDelegate._NULL_PIXMAP_COLOR)

    painter.drawRect(option.rect)
    text_rect = option.rect.adjusted(5, 5, -5, -5)
    painter.drawText(text_rect, QtCore.Qt.AlignCenter, item_id)  # type: ignore

    painter.restore()

  def _paint_selection_cover(self, painter, option):

    painter.save()

    self._setup_painter(painter, ImageItemDelegate._COVER_COLOR)

    painter.drawRect(option.rect)

    painter.restore()

  def _setup_painter(
      self,
      painter: QtGui.QPainter,
      brush_color: QtGui.QColor = QtGui.QColor("white"),
      pen_color: QtGui.QColor = QtGui.QColor("black"),
  ) -> None:
    """Setup a basic painter"""
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setPen(pen_color)
    painter.setBrush(brush_color)


# class IconImageItemDelegate(ImageItemDelegate):
#   def paint(self, painter, option, index):
#     super().paint(painter, option, index)

#     # Determine the status of the item (processed or pending)
#     # Example: retrieve data from the model
#     is_processed = index.data(QtCore.Qt.UserRole + 1)

#     # Calculate the position to draw the custom icon
#     # Example: adjust the size of the icons as needed
#     icon_size = QtCore.QSize(16, 16)
#     icon_margin = 2  # Example: adjust the margin around the icons as needed
#     icon_x = option.rect.center().x() - icon_size.width() // 2
#     icon_y = option.rect.top() + icon_margin
#     icon_position = QtCore.QPoint(icon_x, icon_y)
#     # icon_position = option.rect.topLeft() + QtCore.QPoint(icon_margin, icon_margin)

#     icon_path = resource_initialisation.DIRECTORIES["icon_location"]

#     # Draw the appropriate custom icon on top of the pixmap
#     if is_processed:
#       # Example: path to the processed icon file
#       processed_icon = QtGui.QIcon(
#           os.path.join(icon_path, "check_.png"))
#       processed_pixmap = processed_icon.pixmap(icon_size)
#       painter.drawPixmap(icon_position, processed_pixmap)
#     else:
#       # Example: path to the pending icon file
#       pending_icon = QtGui.QIcon(os.path.join(icon_path, "pending_.png"))
#       pending_pixmap = pending_icon.pixmap(icon_size)
#       painter.drawPixmap(icon_position, pending_pixmap)
