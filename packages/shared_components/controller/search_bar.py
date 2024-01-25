from PyQt5.QtCore import QObject

from packages.shared_components.models.search_bar import SearchBarModel
from packages.shared_components.views.search_bar import SearchBarView


class SearchBarController(QObject):
  def __init__(
      self,
      model: SearchBarModel,
      view: SearchBarView,
  ):
    super().__init__()

    self._view = view
    self._model = model

    self._view.completer.setModel(self._model.autocomplete_model)

    self._model.autocomplete_list_changed.connect(
        self._view.on_autocomplete_list_changed
    )
