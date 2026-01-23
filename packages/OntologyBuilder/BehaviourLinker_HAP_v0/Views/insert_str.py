from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import insert_str_ui


class InsertStrView(QtWidgets.QDialog):

    def __init__(self, title, prompt, forbidden=[], parent=None):
        super().__init__(parent)

        # Set up the user interface
        self.ui = insert_str_ui.Ui_insert_str()
        self.ui.setupUi(self)

        self.setWindowTitle(title)
        self.ui.label_prompt.setText(prompt)
        self.ui.pbutton_accept.setEnabled(False)

        self.forbidden = forbidden

        # Regular expression pattern to match any string without whitespace
        pattern = r'^\S*$'
        regex = QtCore.QRegExp(pattern)

        self.ui.ledit_input.setValidator(QtGui.QRegExpValidator(regex))

        self.ui.ledit_input.textChanged.connect(self.on_text_changed)
        self.ui.pbutton_accept.clicked.connect(self.accept)
        self.ui.pbutton_cancel.clicked.connect(self.reject)

    def on_text_changed(self, text):
        if text.lower() in self.forbidden or text == "":
            self.ui.ledit_input.setStyleSheet("color: red;")
            self.ui.pbutton_accept.setEnabled(False)
        else:
            self.ui.ledit_input.setStyleSheet("color: black;")
            self.ui.pbutton_accept.setEnabled(True)
