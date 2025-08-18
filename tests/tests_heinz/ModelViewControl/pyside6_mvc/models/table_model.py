from typing import Any, List, Optional
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal, Slot


class TableModel(QAbstractTableModel):
    """A table model that stores data in a 2D list structure."""
    
    # Signal emitted when rows are added or removed
    rowsInserted = Signal(int, int)  # start, end
    rowsAboutToBeRemoved = Signal(int, int)  # start, end
    dataChanged = Signal(QModelIndex, QModelIndex, list)  # topLeft, bottomRight, roles
    
    def __init__(self, data: List[List[Any]] = None, parent=None):
        """Initialize the table model with optional data.
        
        Args:
            data: Initial 2D data (list of lists)
            parent: Parent QObject
        """
        super().__init__(parent)
        self._data = data if data is not None else [[]]
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows in the model."""
        return len(self._data) if self._data else 0
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns in the model."""
        return len(self._data[0]) if self._data and self._data[0] else 0
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return the data stored under the given role for the item referred to by the index."""
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole or role == Qt.EditRole:
            row = index.row()
            col = index.column()
            if 0 <= row < len(self._data) and 0 <= col < len(self._data[row]):
                return self._data[row][col]
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set the role data for the item at index to value."""
        if not index.isValid() or role != Qt.EditRole:
            return False
            
        row = index.row()
        col = index.column()
        
        if 0 <= row < len(self._data) and 0 <= col < len(self._data[row]):
            self._data[row][col] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        """Return the data for the given role and section in the header with the specified orientation."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return f"Column {section + 1}"
            return f"Row {section + 1}"
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return the item flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
            
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    def add_row(self, *items: Any) -> None:
        """Add a new row to the model.
        
        Args:
            *items: Items to add to the new row. If fewer items than columns,
                   the remaining items will be empty strings.
        """
        num_columns = max(self.columnCount(), len(items))
        row_data = list(items) + [''] * (num_columns - len(items))
        
        # If this is the first row, ensure we have the right number of columns
        if not self._data:
            self._data = [['' for _ in range(num_columns)]]
        
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(row_data)
        self.endInsertRows()
        
        # Emit signal that rows were added
        self.rowsInserted.emit(len(self._data) - 1, len(self._data) - 1)
    
    def remove_row(self, row: int) -> bool:
        """Remove a row from the model.
        
        Args:
            row: Index of the row to remove
            
        Returns:
            bool: True if the row was removed, False otherwise
        """
        if 0 <= row < len(self._data):
            self.beginRemoveRows(QModelIndex(), row, row)
            self.rowsAboutToBeRemoved.emit(row, row)
            self._data.pop(row)
            self.endRemoveRows()
            return True
        return False
    
    def get_data(self) -> List[List[Any]]:
        """Return a copy of the model's data."""
        return [row[:] for row in self._data]
