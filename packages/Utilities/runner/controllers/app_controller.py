import os
from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Common.resources_icons import getIcon
from Common.resources_icons import roundButton
from ..views import MainWindow

DEBUGGING = False

BASE = os.path.curdir
tasks_dir = os.path.realpath(BASE)

packages_dir = os.path.realpath(os.path.join(BASE, "../packages"))
image_path = os.path.join(packages_dir, 'Common',
                          'icons', 'task_ontology_foundation.svg')

help_dir = os.path.join(packages_dir, 'Common')

ACTIONS = {
        "pushFoundationEditor"        : {"CODE": "ProMo_OntologyFoundationDesigner.py",
                                         "INFO": "info_ontology_equation_editor",
                                         "ICON": getIcon("task_ontology_foundation")},
        "pushEquationEditor"          : {"CODE": "ProMo_OntologyEquationComposer.py",
                                         "INFO": "info_ontology_foundation_editor",
                                         "ICON": getIcon("task_ontology_equations")},
        "pushGraphComoponentDesigner" : {"CODE": "ProMo_ComposerGraphComponentDesigner.py",
                                         "INFO": "info_graphic_object_editor",
                                         "ICON": getIcon("task_graphic_objects")},
        "pushWriteRDFGraph"           : {"CODE": "ProMo_Write_RDF_Graph_Var_Expr.py",
                                         "INFO": "info_graphic_object_editor",
                                         "ICON": getIcon("task_write_RDF_graph")},
        "pushComposerAutomataDesigner": {"CODE": "ProMo_ComposerAutomataDesigner.py",
                                         "INFO": "info_automata_editor",
                                         "ICON": getIcon("task_automata")},
        "pushDotGraphs"               : {"CODE": "ProMo_OntologyDotGraphCreator.py",
                                         "INFO": "info_dot_graph",
                                         "ICON": getIcon("task_dot_graphs")},
        "pushEntityDesigner"          : {"CODE": "ProMo_BehaviourLinker_HAP_v0.py",
                                         "INFO": "info_behaviour_linker",
                                         "ICON": getIcon("task_entity_generation")},
        "pushTypedTokenDesigner"      : {"CODE": "ProMo_TypedTokenEditor.py",
                                         "INFO": "info_typed_token_editor",
                                         "ICON": getIcon("task_typed_token_editor")},
        "pushModelComposer"           : {"CODE": "ProMo_ModelComposer.py",
                                         "INFO": "info_modeller_editor",
                                         "ICON": getIcon("task_model_composer")},
        "pushModelInstantiate"             : {"CODE": "ProMo_ModelInstantiate.py",
                                         "INFO": "info_modeller_instantiator",
                                         "ICON": getIcon("task_instantiation")},
        }


class AppController:
  """Controller that manages the interaction between models and views."""

  def __init__(self, view: MainWindow):
    """Initialize the controller with models, view, and delegate.

    Args:
        view: The main window view
        delegate: The delegate for custom item rendering
    """
    self.view = view
    # self.delegate = delegate

    # Hook models & delegate to views
    self._setup_views()
    self.view.Exit.clicked.connect(self.view.close)
    self.view.Minimise.clicked.connect(self.view.showMinimized)

  def _setup_button(self, button_name):
    """Set up a single button with icon and size.
    
    Args:
        button_name (str): The name of the button to set up (without 'view.' prefix)
    """
    button = getattr(self.view, button_name, None)
    ACTIONS[button_name]["ICON"]
    if button is not None and button_name in ACTIONS:
      button.setIcon(ACTIONS[button_name]["ICON"])
      button.setIconSize(QtCore.QSize(64, 64))
      button.clicked.connect(partial(self.__run_task, button_name))

  def _find_all_buttons(self):
    """Find all QPushButton widgets in the view and return their names.
    
    Returns:
        list: List of button names (strings)
    """
    buttons = []
    # Find all QPushButton widgets in the view
    for widget in self.view.findChildren(QtWidgets.QPushButton):
      button_name = widget.objectName()
      if button_name:  # Only include widgets with a name
        if "push" in button_name:
          buttons.append(button_name)
    return buttons

  def _setup_views(self):
    """Set up all the views with their models and delegates."""
    # Set up window control buttons
    roundButton(self.view.Minimise, "min_view", tooltip="minimise", mysize=35)
    roundButton(self.view.Exit, "reject", tooltip="exit", mysize=35)

    # Find all buttons and filter out the ones we want to set up
    all_buttons = self._find_all_buttons()

    if DEBUGGING:
      print("All buttons found:", all_buttons)

    # Set up each button that has a corresponding action
    for button_name in all_buttons:
      self._setup_button(button_name)

  def __run_task(self, button_name):
    script_path = ACTIONS[button_name]["CODE"]
    try:
      print(f"Script path: {script_path}")

      if not os.path.isfile(script_path):
        raise FileNotFoundError(f"Script not found: {os.path.abspath(script_path)}")

      os.chdir(tasks_dir)
      print(f"Changed to directory: {os.getcwd()}")

      self.process = QtCore.QProcess(self.view)
      self.view.hide()

      # Connect error signals
      self.process.errorOccurred.connect(self._on_process_error)
      self.process.finished.connect(self._on_process_finished)

      print(f"Starting process: python {script_path}")
      self.process.start("python", [script_path])

      if not self.process.waitForStarted():
        raise RuntimeError("Failed to start the process")

      print(f"Process started successfully with PID: {self.process.processId()}")

    except Exception as e:
      error_msg = f"Error running task '{script_path}': {str(e)}"
      print(error_msg)
      QtWidgets.QMessageBox.critical(self.view, "Error", error_msg)

  def _on_process_error(self, error):
    error_msg = f"Process error: {error}"
    print(error_msg)
    if self.process:
      error_msg += f"\nError string: {self.process.errorString()}"
    QtWidgets.QMessageBox.critical(self.view, "Process Error", error_msg)

  def _on_process_finished(self, exit_code, exit_status):
    print(f"Process finished with exit code: {exit_code}, status: {exit_status}")
    if exit_code not in [0, 255]:
      error_msg = f"Process exited with code {exit_code}"
      if self.process:
        error_bytes = self.process.readAllStandardError().data()
        if error_bytes:
          error_msg += f"\nError output:\n{error_bytes.decode('utf-8', 'ignore')}"
      print(error_msg)
      QtWidgets.QMessageBox.warning(self.view, "Process Finished with Errors", error_msg)
    self.view.show()
