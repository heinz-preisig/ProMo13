from PyQt5 import QtCore


class SearchBarModel:

  autocomplete_list_changed = QtCore.pyqtSignal(list)
  search_list_changed = QtCore.pyqtSignal(list)

  def __init__(
      self,
      object_list,
      autocomplete_methods=None,
      search_methods=None,
  ):
    self.object_list = object_list
    autocomplete_methods = autocomplete_methods or []
    search_methods = search_methods or []

    self.autocomplete_model = QtCore.QStringListModel()
    self.search_strings_model = QtCore.QStringListModel()

    for item in self.object_list:
      for method in autocomplete_methods:
        self.autocomplete_strings.append(method(item))

      for method in search_methods:
        self.search_strings.append(method(item))

    self.autocomplete_list_changed.emit(self.autocomplete_strings)
    self.search_list_changed.emit(self.search_strings)
