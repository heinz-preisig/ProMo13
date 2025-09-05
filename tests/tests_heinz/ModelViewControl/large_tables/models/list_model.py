from typing import Any
from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt


class ListModel(QAbstractListModel):
    """A list model that wraps a TableModel to show only the first column."""
    
    def __init__(self, table_model):
        """Initialize with a reference to a TableModel.
        
        Args:
            table_model: The TableModel to wrap.
        """
        super().__init__()
        self._table_model = table_model
        # Connect to table model's signals to keep in sync
        self._table_model.rowsAboutToBeRemoved.connect(self._on_table_rows_removed)
        self._table_model.rowsInserted.connect(self._on_table_rows_inserted)
        self._table_model.dataChanged.connect(self._on_table_data_changed)
        self._table_model.modelAboutToBeReset.connect(self.beginResetModel)
        self._table_model.modelReset.connect(self.endResetModel)
        self._table_model.layoutAboutToBeChanged.connect(self.layoutAboutToBeChanged)
        self._table_model.layoutChanged.connect(self.layoutChanged)

    def _on_table_rows_removed(self, parent, first, last):
        self.beginRemoveRows(QModelIndex(), first, last)
        self.endRemoveRows()

    def _on_table_rows_inserted(self, parent, first, last):
        self.beginInsertRows(QModelIndex(), first, last)
        self.endInsertRows()

    def _on_table_data_changed(self, top_left, bottom_right, roles):
        # Forward the data changed signal with adjusted indices
        top_left = self.index(top_left.row())
        bottom_right = self.index(bottom_right.row())
        self.dataChanged.emit(top_left, bottom_right, roles)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows in the model."""
        return self._table_model.rowCount()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return the data for the given role and index."""
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return None
            
        # Get the name from the first column of the table model
        table_index = self._table_model.index(index.row(), 0)
        return self._table_model.data(table_index, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return the item flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set the role data for the item at index to value."""
        if role == Qt.EditRole and index.isValid():
            table_index = self._table_model.index(index.row(), 0)
            return self._table_model.setData(table_index, value, role)
        return False

    def add_item(self, text: str) -> None:
        """Add a new item to the list."""
        # Add a new row with the text in the first column and empty second column
        self._table_model.add_row(text, "")

    def remove_row(self, row: int) -> None:
        """Remove the row at the given index."""
        self._table_model.remove_row(row)
