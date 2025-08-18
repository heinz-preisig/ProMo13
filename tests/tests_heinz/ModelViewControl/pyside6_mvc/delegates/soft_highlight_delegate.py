from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QPainterPath
from PySide6.QtWidgets import QStyledItemDelegate, QStyle


class SoftHighlightDelegate(QStyledItemDelegate):
    """A delegate that paints alternating rows but respects selection.
    
    Selected rows get a rounded rectangle with a gentle gradient.
    """
    
    def paint(self, painter: QPainter, option, index) -> None:
        """Paint the item with custom highlighting for selected items."""
        # Save the painter state
        painter.save()
        
        # Get the text to display
        text = index.data(Qt.DisplayRole) or ""
        
        # Set up colors and style
        selected = option.state & QStyle.State_Selected
        
        # Always draw the background first
        if selected:
            # Create a more visible gradient for the selection background
            gradient = QLinearGradient(option.rect.topLeft(), option.rect.bottomLeft())
            gradient.setColorAt(0, QColor(42, 130, 218))  # Brighter blue
            gradient.setColorAt(1, QColor(0, 80, 180))    # Darker blue
            
            # Create a rounded rectangle path for the selection
            path = QPainterPath()
            radius = 4.0
            # Convert QRect to QRectF for addRoundedRect
            rect = QRectF(option.rect.adjusted(1, 1, -1, -1))  # Slightly smaller than cell
            path.addRoundedRect(rect, radius, radius)
            
            # Fill the background with the gradient
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawPath(path)
            
            # Set text color to white for better contrast
            text_color = Qt.white
        else:
            # For unselected items, use alternating row colors
            if index.row() % 2 == 0:
                painter.fillRect(option.rect, option.palette.base())
            else:
                painter.fillRect(option.rect, option.palette.alternateBase())
            
            # Use default text color
            text_color = option.palette.text().color()
        
        # Set up text drawing
        text_rect = option.rect.adjusted(8, 0, -8, 0)  # Add padding
        
        # Calculate text metrics and elide if needed
        metrics = painter.fontMetrics()
        elided_text = metrics.elidedText(text, Qt.ElideRight, text_rect.width())
        
        # Calculate vertical alignment
        text_rect = option.rect.adjusted(8, 0, -8, 0)
        text_rect.setTop(text_rect.top() + (text_rect.height() - metrics.height()) // 2)
        text_rect.setHeight(metrics.height())
        
        # Draw the text with the appropriate color
        painter.setPen(text_color)
        painter.drawText(text_rect, int(Qt.AlignLeft | Qt.AlignVCenter), elided_text)
        
        # Restore the painter state
        painter.restore()

    def sizeHint(self, option, index):
        """Return the size needed to display the item."""
        # Get the base size hint
        size = super().sizeHint(option, index)
        
        # Add some vertical padding
        size.setHeight(size.height() + 4)
        return size
