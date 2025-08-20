from typing import List, Any
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt


class TableModel(QAbstractTableModel):
    """A table model that stores data in a 2D list structure."""
    
    HEADER = ["Name", "Value"]

    def __init__(self, rows: List[list[str]] | None = None):
        """Initialize the table model with optional initial data.
        
        Args:
            rows: Optional initial data as a list of [name, value] pairs.
        """
        super().__init__()
        self._rows: List[list[str]] = rows or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows in the model."""
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns in the model."""
        return len(self.HEADER)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return the data for the given role and index."""
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
            
        row = index.row()
        col = index.column()
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._rows[row][col] if col < len(self._rows[row]) else ""
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, 
                  role: int = Qt.DisplayRole) -> Any:
        """Return the header data for the given section and orientation."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADER[section] if 0 <= section < len(self.HEADER) else ""
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return the item flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set the role data for the item at index to value."""
        if role == Qt.EditRole and index.isValid():
            r, c = index.row(), index.column()
            if 0 <= r < len(self._rows) and 0 <= c < len(self._rows[r]):
                self._rows[r][c] = str(value)
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
                return True
        return False

    def add_row(self, name: str, value: str) -> None:
        """Add a new row with the given name and value."""
        insert_row = len(self._rows)
        self.beginInsertRows(QModelIndex(), insert_row, insert_row)
        self._rows.append([str(name), str(value)])
        self.endInsertRows()
        # Emit dataChanged for the new row to ensure views update
        top_left = self.index(insert_row, 0)
        bottom_right = self.index(insert_row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [])

    def remove_row(self, row: int) -> None:
        """Remove the row at the given index."""
        if 0 <= row < len(self._rows):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._rows.pop(row)
            self.endRemoveRows()
