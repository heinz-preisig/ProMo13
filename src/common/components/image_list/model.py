"""
Define ImageListModel

Classes:
    ImageListModel: Handle a list of images.

"""

from pathlib import Path
from typing import List, Optional

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from src.common import roles


class ImageListModel(QStandardItemModel):
  """
  Handle a list of images

  Custom model to handle a list of images instead of a list of strings.

  Methods:
      :meth:`load_data`: Load data into the model.
  """

  def load_data(
      self,
      item_ids: List[str],
      item_paths: List[Path],
      icon_mode: bool = False,
      pending_item_ids: Optional[List[str]] = None,
      name_mode: bool = False,
      item_names: Optional[List[str]] = None,
  ):
    """Load data into the model.

    Args:
        item_ids (List[str]): Item IDs to load.
        item_paths (List[Path]): Paths corresponding to the item IDs.
        icon_mode (bool, optional): If True, the method will set the
         pending status of each item. Defaults to False.
        pending_item_ids (Optional[List[str]], optional): Item IDs
         that are pending. This must be provided if `icon_mode` is
         True. Defaults to None.
        name_mode (bool, optional): If True, the method will set the
         name role of each item. Defaults to False.
        item_names (Optional[List[str]], optional): Item names. This
         must be provided if `name_mode` is True. Defaults to None.

    Raises:
        ValueError: If `icon_mode` is True but `pending_item_ids`
         is None.
        ValueError: If `name_mode` is True but `item_names` is None.
    """
    if icon_mode and pending_item_ids is None:
      raise ValueError(
          "pending_item_ids must not be None when icon_mode is True"
      )

    if name_mode and item_names is None:
      raise ValueError(
          "item_names must not be None when name mode is True"
      )

    pending_item_ids = pending_item_ids or []
    item_names = item_names or ["" for _ in item_ids]

    self.clear()

    for item_id, item_path, item_name in zip(item_ids, item_paths, item_names):
      item = QStandardItem()
      item.setData(item_id, roles.ID_ROLE)
      item.setData(item_path, roles.IMAGE_PATH_ROLE)

      if name_mode:
        item.setData(item_name, roles.NAME_ROLE)

      if icon_mode:
        item.setData(
            item_id in pending_item_ids,
            roles.PENDING_ROLE,
        )

      self.appendRow(item)
