from PyQt5 import QtWidgets

from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import ImageItemDelegate
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.image_list import ImageListModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import entity_changes_ui


class EntityChangesView(QtWidgets.QDialog):

    def __init__(self, changes, parent=None):
        super().__init__(parent)

        # Set up the user interface
        self.ui = entity_changes_ui.Ui_entity_changes()
        self.ui.setupUi(self)

        view_widgets = [
                self.ui.list_add_vars,
                self.ui.list_add_eqs,
                self.ui.list_delete_vars,
                self.ui.list_delete_eqs,
                ]
        for model_list, view_widget in zip(changes, view_widgets):
            self.load_model_and_delegate(model_list, view_widget)

            if not model_list:
                view_widget.hide()
                self.ui.main_layout.removeWidget(view_widget)

        if not (changes[0] or changes[1]):
            self.ui.label_added.hide()
            self.ui.main_layout.removeWidget(self.ui.label_added)

        if not (changes[2] or changes[3]):
            self.ui.label_deleted.hide()
            self.ui.main_layout.removeWidget(self.ui.label_deleted)

        self.adjustSize()

        self.ui.pbutton_accept.clicked.connect(self.accept)
        self.ui.pbutton_cancel.clicked.connect(self.reject)

    def load_model_and_delegate(self, model_list, view_widget):
        model = ImageListModel()
        model.load_data(model_list)
        view_widget.setModel(model)
        delegate = ImageItemDelegate(view_widget)
        view_widget.setItemDelegate(delegate)
