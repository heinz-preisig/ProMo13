from PyQt5 import QtCore
from PyQt5 import QtWidgets

from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import variable_editor_ui


class VariableEditorView(QtWidgets.QDialog):
    show_event_triggered = QtCore.pyqtSignal()

    def __init__(self, model, output_only, parent=None):
        super().__init__(parent)

        # Set up the user interface
        self.ui = variable_editor_ui.Ui_variable_editor()
        self.ui.setupUi(self)

        self._model = model

        if output_only:
            self.ui.cbox_input.setEnabled(False)
            self.ui.cbox_output.setChecked(True)
            self.ui.cbox_output.setEnabled(False)

    def on_input_checked(self):
        self.ui.cbox_output.setChecked(False)
        self.ui.cbox_instantiation.setChecked(False)
        self.ui.list_equations.setCurrentIndex(QtCore.QModelIndex())
        # self.ui.list_equations.clearSelection()

    def on_output_checked(self):
        self.ui.cbox_input.setChecked(False)

    def on_init_checked(self):
        self.ui.cbox_input.setChecked(False)
        # self.ui.list_equations.setCurrentIndex(QtCore.QModelIndex())
        # self.ui.list_equations.clearSelection()
        # print(self.ui.list_equations.currentIndex().isValid())

    def on_equation_selected(self):
        self.ui.cbox_input.setChecked(False)
        self.ui.cbox_instantiation.setChecked(False)

    def on_initial_data_fetched(self, is_input, is_output, is_init, selected_eq):
        self.ui.cbox_input.setChecked(is_input)
        self.ui.cbox_output.setChecked(is_output)
        self.ui.cbox_instantiation.setChecked(is_init)

        self.ui.list_equations.setCurrentIndex(selected_eq)
