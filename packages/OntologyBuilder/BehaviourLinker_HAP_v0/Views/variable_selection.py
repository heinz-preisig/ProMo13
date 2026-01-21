from PyQt5 import QtWidgets

from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import ImageItemDelegate
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.image_list import ImageListModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import variable_selection_ui


class VariableSelectionView(QtWidgets.QDialog):

    def __init__(self, variables, parent=None):
        super().__init__(parent)

        # Set up the user interface
        self.ui = variable_selection_ui.Ui_variable_selection()
        self.ui.setupUi(self)

        model = ImageListModel()
        model.load_data(variables)
        self.ui.list_variables.setModel(model)
        delegate = ImageItemDelegate(self.ui.list_variables)
        self.ui.list_variables.setItemDelegate(delegate)

        index = model.index(0, 0)
        if index.isValid():
            self.ui.list_variables.setCurrentIndex(index)
        else:
            self.ui.pbutton_accept.setEnabled(False)

        self.ui.list_variables.doubleClicked.connect(self.accept)
        self.ui.pbutton_accept.clicked.connect(self.accept)
        self.ui.pbutton_cancel.clicked.connect(self.reject)
