"""
Define ImageListController

Classes:
    ImageListController: Manage interactions in the ImageList component.

"""
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QListView

from src.common.components.image_list.model import ImageListModel
from src.common.components.image_list.delegate import ImageItemDelegate


class ImageListController(QObject):
  """Manage interactions in the ImageList component.

  The view is a QListView.
  The model is a ImageListModel
  The delegate is a ImageItemDelegate

  Args:
      QObject (_type_): _description_
  """

  def __init__(self, view: QListView, model: ImageListModel):
    """Setup links between the parts of the ImageList component.

    Args:
        view (QListView): An instance of the view.
        model (ImageListModel): An instance of the model.
    """
    view.setModel(model)
    delegate = ImageItemDelegate(view)
    view.setItemDelegate(delegate)
