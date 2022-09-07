#!/usr/bin/python3

import platform
import subprocess
import os
from functools import partial
import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

BASE = os.path.dirname(__file__)
tasks_dir = os.path.realpath(BASE)
#tasks_dir = BASE
packages_dir = os.path.realpath(os.path.join(BASE, "../packages"))
image_path = os.path.join(packages_dir, 'Common', 'icons', 'task_ontology_foundation.svg')
# pdf_reader = "evince"  # using platform specific options for windows, Linux and Mac
help_dir = os.path.join(packages_dir, 'Common')

CODE_PATHS = {
    "ProMo_OntologyFoundationDesigner.py": "ProMo_OntologyFoundationDesigner.py",
    "ProMo_OntologyEquationComposer.py": "ProMo_OntologyEquationComposer.py",
    "ProMo_ComposerGraphComponentDesigner.py": "ProMo_ComposerGraphComponentDesigner.py",
    "ProMo_BehaviourLinker.py": "ProMo_BehaviourLinker.py",
    "ProMo_ComposerAutomataDesigner.py": "ProMo_ComposerAutomataDesigner.py",
    "ProMo_TypedTokenEditor.py": "ProMo_TypedTokenEditor.py",
    "ProMo_ModelComposer.py": "ProMo_ModelComposer.py"
}
MAP_HELP_FILE = {
    "foundation": "info_ontology_foundation_editor",
    "equations": "info_ontology_equation_editor",
    "components": "info_graphic_object_editor",
    "linker": "info_behaviour_association_editor",
    "automaton": "info_automata_editor",
    "typedtoken": "info_typed_token_editor",
    "modeller": "info_modeller_editor",
}


class EmbTerminal(QtWidgets.QWidget):
    def __init__(self, parent=None, preferred_width=None):
        super(EmbTerminal, self).__init__(parent)
        self.process = QtCore.QProcess(self)
        wid = str(int(self.winId()))
        self.process.start('urxvt', ['-embed', wid])
        width = preferred_width or 840
        self.setMinimumSize(width, 240)

    def closeEvent(self, event):
        self.process.terminate()
        self.process.waitForFinished(1000)


class HomeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()

        self.filedialog = QtWidgets.QFileDialog()
        self.setDockOptions(self.GroupedDragging | self.AllowTabbedDocks | self.AllowNestedDocks)

        self.setWindowTitle("ProMo 1.0")  # window title
        self.resize(QtCore.QSize(1350, 980))

        self.central_widget = QtWidgets.QWidget(self)
        self.h_layout_central = QtWidgets.QHBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.left_frame = QtWidgets.QFrame(self.central_widget)
        self.left_frame.setObjectName("left_frame")
        self.left_frame.setStyleSheet("#left_frame{ background-color: #CCC; }")
        self.right_frame = QtWidgets.QFrame(self.central_widget)
        self.right_frame.setStyleSheet("background-color: #CCC;")

        self.l_vbox_layout = QtWidgets.QVBoxLayout(self.left_frame)
        self.r_vbox_layout = QtWidgets.QVBoxLayout(self.right_frame)

        self.r_bottom_dock = QtWidgets.QDockWidget("Python console", self.right_frame)
        self.r_bottom_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        self.r_top_frame = QtWidgets.QFrame(self.right_frame)
        self.r_top_layout = QtWidgets.QVBoxLayout(self.r_top_frame)
        self.r_top_frame.setStyleSheet(f"background-color: #CAFF9F;\n"
                                       f"padding: 5px 15px;")
        self.label_image = QtWidgets.QLabel(self.r_top_frame)
        self.label_image.setPixmap(QtGui.QPixmap(image_path))
        self.label_image.setScaledContents(False)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.r_top_frame.layout().addWidget(self.label_image)

        self.splitter_1 = QtWidgets.QSplitter(Qt.Horizontal)
        self.splitter_1.addWidget(self.left_frame)
        self.splitter_1.addWidget(self.right_frame)

        self.splitter_2 = QtWidgets.QSplitter(Qt.Vertical)
        self.splitter_2.addWidget(self.r_top_frame)

        self.l_top_frame = QtWidgets.QFrame(self.left_frame)
        self.l_top_v_layout = QtWidgets.QVBoxLayout(self.l_top_frame)
        self.l_bottom_frame = QtWidgets.QFrame(self.left_frame)
        self.l_bottom_v_layout = QtWidgets.QVBoxLayout(self.l_bottom_frame)

        self.splitter_3 = QtWidgets.QSplitter(Qt.Vertical)
        self.splitter_3.addWidget(self.l_top_frame)
        self.splitter_3.addWidget(self.l_bottom_frame)

        self.splitter_1.setSizes([35, 65])  # primary splitter
        self.splitter_3.setSizes([50, 50])  # left frame vertical splitter
        self.splitter_2.setSizes([70, 30])  # right frame vertical splitter

        self.h_layout_central.addWidget(self.splitter_1)
        self.r_vbox_layout.addWidget(self.splitter_2)
        self.l_vbox_layout.addWidget(self.splitter_3)

        self.right_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.left_frame.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        # fonts
        font_heading = QtGui.QFont("Umpush", 12, 50)

        # ----------------- adding widgets --------------------
        # ========= left top frame ============
        self.label_left_top_frame_heading = QtWidgets.QLabel(self.l_top_frame)
        self.label_left_top_frame_heading.setFont(font_heading)
        self.label_left_top_frame_heading.setText("Opened Tool")
        self.opened_window_list_widget = QtWidgets.QListWidget(self.l_top_frame)
        self.l_top_frame.layout().addWidget(self.label_left_top_frame_heading)
        self.l_top_frame.layout().addWidget(self.opened_window_list_widget)
        # ========= left bottom frame ============
        self.label_left_bottom_frame_heading = QtWidgets.QLabel(self.l_bottom_frame)
        self.label_left_bottom_frame_heading.setFont(font_heading)
        self.label_left_bottom_frame_heading.setText("Error Console")
        self.error_console = QtWidgets.QTextEdit(self.l_bottom_frame)
        self.l_bottom_frame.layout().addWidget(self.label_left_bottom_frame_heading)
        self.l_bottom_frame.layout().addWidget(self.error_console)

        # python terminal
        self.python_terminal = EmbTerminal(self.r_bottom_dock, self.width())
        self.r_bottom_dock.setWidget(self.python_terminal)
        self.r_bottom_dock.setContentsMargins(10, 35, 10, 10)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.r_bottom_dock)

        # create file menu actions
        file_menu = self.menuBar().addMenu("File")
        Open_action = QtWidgets.QAction("Open", self)
        Open_action.triggered.connect(self.open_dir)
        recent_files_action = QtWidgets.QAction("Recent Files", self)
        recent_files_action.triggered.connect(self.recent_files)
        Exit_action = QtWidgets.QAction("Exit", self)
        Exit_action.triggered.connect(self.Exit)
        file_menu.addActions((
            Open_action,
            recent_files_action,
            Exit_action
        ))

        # create view menu actions
        view_menu = self.menuBar().addMenu("View")
        toggle_opened_tools_action = QtWidgets.QAction("Opened Tools", self)
        toggle_opened_tools_action.triggered.connect(partial(self.toggle_frames, "opened_tools"))
        toggle_python_shell_action = QtWidgets.QAction("Python Shell", self)
        toggle_python_shell_action.triggered.connect(partial(self.toggle_frames, "python_shell"))
        toggle_error_console_action = QtWidgets.QAction("Error Console", self)
        toggle_error_console_action.triggered.connect(partial(self.toggle_frames, "error_console"))

        view_menu.addActions((toggle_opened_tools_action, toggle_python_shell_action, toggle_error_console_action))

        # create tool menu actions
        tools_menu = self.menuBar().addMenu("Tools")
        foundation_action = QtWidgets.QAction("foundation", self)
        foundation_action.triggered.connect(self.open_foundation)
        equations_action = QtWidgets.QAction("equations", self)
        equations_action.triggered.connect(self.open_equations)
        components_action = QtWidgets.QAction("components", self)
        components_action.triggered.connect(self.open_components)
        linker_action = QtWidgets.QAction("linker", self)
        linker_action.triggered.connect(self.open_linker)
        automaton_action = QtWidgets.QAction("automaton", self)
        automaton_action.triggered.connect(self.open_automaton)
        typedtoken_action = QtWidgets.QAction("typedtoken", self)
        typedtoken_action.triggered.connect(self.open_typedtoken)
        modeller_action = QtWidgets.QAction("modeller", self)
        modeller_action.triggered.connect(self.open_modeller)

        # add action to each menu tool menu
        tools_menu.addAction(foundation_action)
        tools_menu.addAction(equations_action)
        tools_menu.addAction(components_action)
        tools_menu.addAction(linker_action)
        tools_menu.addAction(automaton_action)
        tools_menu.addAction(typedtoken_action)
        tools_menu.addAction(modeller_action)

        # create help menu actions
        foundation_help = QtWidgets.QAction("foundation", self)
        foundation_help.triggered.connect(partial(self.ask_help, "foundation"))
        equations_help = QtWidgets.QAction("equations", self)
        equations_help.triggered.connect(partial(self.ask_help, "equations"))
        components_help = QtWidgets.QAction("components", self)
        components_help.triggered.connect(partial(self.ask_help, "components"))
        linker_help = QtWidgets.QAction("linker", self)
        linker_help.triggered.connect(partial(self.ask_help, "linker"))
        automaton_help = QtWidgets.QAction("automaton", self)
        automaton_help.triggered.connect(partial(self.ask_help, "automaton"))
        typedtoken_help = QtWidgets.QAction("typedtoken", self)
        typedtoken_help.triggered.connect(partial(self.ask_help, "typedtoken"))
        modeller_help = QtWidgets.QAction("modeller", self)
        modeller_help.triggered.connect(partial(self.ask_help, "modeller"))

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addActions((
            foundation_help,
            equations_help,
            components_help,
            linker_help,
            automaton_help,
            typedtoken_help,
            modeller_help
        ))

    def toggle_frames(self, toggle_label: str):
        if toggle_label == "opened_tools":
            self.l_top_frame.setHidden(not self.l_top_frame.isHidden())
        if toggle_label == "python_shell":
            self.r_bottom_dock.setHidden(not self.r_bottom_dock.isHidden())
            self.python_terminal.setMinimumSize(self.width(), 240)
        if toggle_label == "error_console":
            self.l_bottom_frame.setHidden(not self.l_bottom_frame.isHidden())

    def ask_help(self, program_name):
        """
        open help pdf file from packages/Common use platform specific pdf reader.
        """
        help_pdf_path = os.path.join(help_dir, f"{MAP_HELP_FILE[program_name]}.pdf")
        self.statusBar().showMessage(f"opening: {help_pdf_path}", 5 * 1000)
        if platform.system() == 'Windows':
            os.startfile(help_pdf_path)
        elif platform.system() == 'Darwin':
            subprocess.call(('open', help_pdf_path))
        else:
            subprocess.call(('xdg-open', help_pdf_path))

    def open_dir(self):
        dir_loc = self.filedialog.getExistingDirectory(self, "tasks directory", tasks_dir,
                                                       QtWidgets.QFileDialog.ShowDirsOnly)
        if dir_loc:
            self.statusBar().showMessage(f"selected dir: {dir_loc}", 5 * 1000)

    def recent_files(self):
        pass

    def Exit(self):
        self.close()  # invoke closeEvent implemented below

    def open_foundation(self):
        os.chdir(tasks_dir)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(
            partial(self.onStandardError, "ProMo_OntologyFoundationDesigner.py"))
        self.process.start("python", [CODE_PATHS["ProMo_OntologyFoundationDesigner.py"]])
        self.opened_window_list_widget.addItem(QtWidgets.QListWidgetItem("ProMo_OntologyFoundationDesigner.py"))

    def open_equations(self):
        os.chdir(tasks_dir)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(partial(self.onStandardError, "ProMo_OntologyEquationComposer.py"))
        self.process.start("python", [CODE_PATHS["ProMo_OntologyEquationComposer.py"]])
        self.opened_window_list_widget.addItem(QtWidgets.QListWidgetItem("ProMo_OntologyEquationComposer.py"))

    def open_components(self):
        os.chdir(tasks_dir)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(
            partial(self.onStandardError, "ProMo_ComposerGraphComponentDesigner.py"))
        self.process.start("python", [CODE_PATHS["ProMo_ComposerGraphComponentDesigner.py"]])
        self.opened_window_list_widget.addItem(QtWidgets.QListWidgetItem("ProMo_ComposerGraphComponentDesigner.py"))

    def open_linker(self):
        os.chdir(tasks_dir)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(partial(self.onStandardError, "ProMo_BehaviourLinker.py"))
        self.process.start("python", [CODE_PATHS["ProMo_BehaviourLinker.py"]])
        self.opened_window_list_widget.addItem(QtWidgets.QListWidgetItem("ProMo_BehaviourLinker.py"))

    def open_automaton(self):
        os.chdir(tasks_dir)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(partial(self.onStandardError, "ProMo_ComposerAutomataDesigner.py"))
        self.process.start("python", [CODE_PATHS["ProMo_ComposerAutomataDesigner.py"]])
        self.opened_window_list_widget.addItem(QtWidgets.QListWidgetItem("ProMo_ComposerAutomataDesigner.py"))

    def open_typedtoken(self):
        os.chdir(tasks_dir)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(partial(self.onStandardError, "ProMo_TypedTokenEditor.py"))
        self.process.start("python", [CODE_PATHS["ProMo_TypedTokenEditor.py"]])
        self.opened_window_list_widget.addItem(QtWidgets.QListWidgetItem("ProMo_TypedTokenEditor.py"))

    def open_modeller(self):
        os.chdir(tasks_dir)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(partial(self.onStandardError, "ProMo_ModelComposer.py"))
        self.process.start("python", [CODE_PATHS["ProMo_ModelComposer.py"]])
        self.opened_window_list_widget.addItem(QtWidgets.QListWidgetItem("ProMo_ModelComposer.py"))

    def onStandardError(self, program_name):
        returned_data = self.process.readAllStandardError().data().decode()
        self.error_console.append(f"\n\n{program_name}:\n{returned_data}")

        list_items = [self.opened_window_list_widget.item(index) for index in
                      range(self.opened_window_list_widget.count())]
        for item_index in range(len(list_items) - 1, -1, -1):
            item_text = list_items[item_index].text()
            if item_text == program_name:
                self.opened_window_list_widget.takeItem(item_index)

    def closeEvent(self, event: QtGui.QCloseEvent):
        try:
            self.python_terminal.close()
            self.process.terminate()
        except Exception:
            pass
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = HomeWindow()
    w.show()
    sys.exit(app.exec_())
