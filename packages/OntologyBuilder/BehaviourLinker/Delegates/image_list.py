from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# TODO: Icons should be stored in resources
import os
from Common import resource_initialisation

# TODO: Colors should come from the palette


class ImageItemDelegate(QtWidgets.QStyledItemDelegate):
  def sizeHint(self, option, index):
    if index.data():
      path = index.data(QtCore.Qt.UserRole)
      pixmap = QtGui.QPixmap(path)
      if not pixmap.isNull():
        pixmap_size = QtCore.QSize(pixmap.width(), pixmap.height())
        # Increase item size by 10 pixels in each direction
        return pixmap_size + QtCore.QSize(10, 10)
      else:
        return QtCore.QSize(50, 50)
    return super().sizeHint(option, index)

  def paint(self, painter, option, index):
    if not index.data(QtCore.Qt.UserRole):
      super().paint(painter, option, index)
      return

    if index.data():
      path = index.data(QtCore.Qt.UserRole)
      # print(path)
      pixmap = QtGui.QPixmap(path)
      if not pixmap.isNull():
        # Subtract 10 pixels in each direction to get original pixmap size
        size = option.rect.size() - QtCore.QSize(10, 10)
        scaled_pixmap = pixmap.scaled(
            size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        x = option.rect.x() + option.rect.width() / 2 - scaled_pixmap.width() / 2
        y = option.rect.y() + option.rect.height() / 2 - scaled_pixmap.height() / 2

        num_items = index.model().rowCount()
        # print(num_items + index.row())
        if (num_items + index.row()) % 2 == 0:
          background_color = QtGui.QColor(
              240, 240, 240)  # Light gray for even rows
        else:
          background_color = QtGui.QColor(
              220, 220, 220)  # Dark gray for odd rows

        painter.fillRect(option.rect, background_color)

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(int(x), int(y), scaled_pixmap)
        painter.restore()
      else:
        # Pixmap is null, so draw a red background with text
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(255, 200, 200)
                         )  # Light red color
        painter.drawRect(option.rect)
        # Leave some margin around the text
        text_rect = option.rect.adjusted(5, 5, -5, -5)
        # Black text color
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
        painter.drawText(text_rect, QtCore.Qt.AlignCenter,
                         (str(path).split("/")[-1]).split(".")[0])
        painter.restore()

      if option.state & QtWidgets.QStyle.State_Selected:
        painter.save()

        # Set the cover color and transparency
        # Light blue with alpha (100)
        cover_color = QtGui.QColor(105, 232, 213, 92)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(cover_color))

        # Draw a rectangle covering the item area
        painter.drawRect(option.rect)

        painter.restore()


class IconImageItemDelegate(ImageItemDelegate):
  def paint(self, painter, option, index):
    super().paint(painter, option, index)

    # Determine the status of the item (processed or pending)
    # Example: retrieve data from the model
    is_processed = index.data(QtCore.Qt.UserRole + 1)

    # Calculate the position to draw the custom icon
    # Example: adjust the size of the icons as needed
    icon_size = QtCore.QSize(16, 16)
    icon_margin = 2  # Example: adjust the margin around the icons as needed
    icon_x = option.rect.center().x() - icon_size.width() // 2
    icon_y = option.rect.top() + icon_margin
    icon_position = QtCore.QPoint(icon_x, icon_y)
    # icon_position = option.rect.topLeft() + QtCore.QPoint(icon_margin, icon_margin)

    icon_path = resource_initialisation.DIRECTORIES["icon_location"]

    # Draw the appropriate custom icon on top of the pixmap
    if is_processed:
      # Example: path to the processed icon file
      processed_icon = QtGui.QIcon(
          os.path.join(icon_path, "check_.png"))
      processed_pixmap = processed_icon.pixmap(icon_size)
      painter.drawPixmap(icon_position, processed_pixmap)
    else:
      # Example: path to the pending icon file
      pending_icon = QtGui.QIcon(os.path.join(icon_path, "pending_.png"))
      pending_pixmap = pending_icon.pixmap(icon_size)
      painter.drawPixmap(icon_position, pending_pixmap)
