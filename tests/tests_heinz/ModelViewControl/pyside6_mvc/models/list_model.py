from typing import Any, Optional
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal, Slot


class ListModel(QAbstractListModel):
    """A list model that displays the first column of a table model."""
    
    # Signal emitted when rows are added or removed
    rowsInserted = Signal(int, int)  # start, end
    rowsAboutToBeRemoved = Signal(int, int)  # start, end
    
    def __init__(self, table_model, parent=None):
        """Initialize the list model with a reference to a table model.
        
        Args:
            table_model: The table model to display
            parent: Parent QObject
        """
        super().__init__(parent)
        self._table_model = table_model
        
        # Connect to table model signals
        self._table_model.rowsInserted.connect(self._on_table_rows_inserted)
        self._table_model.rowsAboutToBeRemoved.connect(self._on_table_rows_about_to_be_removed)
        self._table_model.dataChanged.connect(self._on_table_data_changed)
        self._table_model.modelAboutToBeReset.connect(self.modelAboutToBeReset)
        self._table_model.modelReset.connect(self.modelReset)
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows in the model."""
        return self._table_model.rowCount()
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return the data stored under the given role for the item referred to by the index."""
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
            
        if role == Qt.DisplayRole or role == Qt.EditRole:
            # Get the first column's data from the table model
            return self._table_model.data(
                self._table_model.index(index.row(), 0), 
                role
            )
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set the role data for the item at index to value."""
        if not index.isValid() or role != Qt.EditRole:
            return False
            
        # Update the first column in the table model
        return self._table_model.setData(
            self._table_model.index(index.row(), 0),
            value,
            role
        )
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return the item flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags
            
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    def add_item(self, text: str) -> None:
        """Add a new item to the list.
        
        Args:
            text: Text for the new item
        """
        # Add a new row to the table model with the text in the first column
        self._table_model.add_row(text)
    
    def remove_row(self, row: int) -> bool:
        """Remove a row from the model.
        
        Args:
            row: Index of the row to remove
            
        Returns:
            bool: True if the row was removed, False otherwise
        """
        return self._table_model.remove_row(row)
    
    @Slot(int, int)
    def _on_table_rows_inserted(self, first: int, last: int) -> None:
        """Handle rows being inserted in the table model."""
        self.beginInsertRows(QModelIndex(), first, last)
        self.endInsertRows()
        self.rowsInserted.emit(first, last)
    
    @Slot(int, int)
    def _on_table_rows_about_to_be_removed(self, first: int, last: int) -> None:
        """Handle rows being removed from the table model."""
        self.beginRemoveRows(QModelIndex(), first, last)
        self.endRemoveRows()
        self.rowsAboutToBeRemoved.emit(first, last)
    
    @Slot(QModelIndex, QModelIndex, list)
    def _on_table_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list) -> None:
        """Handle data changes in the table model."""
        # Only care about changes to the first column
        if top_left.column() == 0:
            # Convert the table model index to a list model index
            list_index = self.index(top_left.row())
            self.dataChanged.emit(list_index, list_index, roles)
