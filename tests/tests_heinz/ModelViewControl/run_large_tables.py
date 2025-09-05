#!/usr/bin/env python3
"""
Main entry point for the PyQt5 MVC + Delegate example.
https://www.pythonguis.com/tutorials/qtableview-modelviews-numpy-pandas/
"""

import argparse
import os
import sys

from PyQt5.QtWidgets import QApplication

# Add the current directory to the Python path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from large_tables.models import ListModel, TableModel
from large_tables.views import MainWindow
from large_tables.delegates import SoftHighlightDelegate
from large_tables.controllers import AppController


def run_gui():
  """Initialize and run the GUI application."""
  app = QApplication(sys.argv)

  # Set application style for better look
  app.setStyle('Fusion')

  # Create the table model with sample data
  table_model = TableModel([["Alpha", ""], ["Beta", ""], ["Gamma", ""]])

  # Create the list model that wraps the table model
  list_model = ListModel(table_model)

  # Create and show the main window
  view = MainWindow()

  # Create delegate for custom item rendering
  delegate = SoftHighlightDelegate()

  # Create controller to manage the application logic
  controller = AppController(list_model, table_model, view, delegate)

  # Set initial window size and show
  view.setWindowTitle("PyQt5 MVC + Delegate Example")
  view.resize(700, 500)
  view.show()

  # Start the event loop
  sys.exit(app.exec_())


def run_tests():
  """Run the test suite."""
  import unittest
  from pyqt5_mvc.tests import test_models, test_controller

  # Create a test suite
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(test_models.TestModels))
  suite.addTest(unittest.makeSuite(test_controller.TestController))

  # Run the tests
  runner = unittest.TextTestRunner(verbosity=2)
  return runner.run(suite)


if __name__ == "__main__":
  # Parse command line arguments
  parser = argparse.ArgumentParser(description="PyQt5 MVC + Delegate Example")
  parser.add_argument(
          "--test", action="store_true", help="Run tests instead of the GUI"
          )
  parser.add_argument(
          "--verbose", action="store_true", help="Enable verbose output"
          )
  args = parser.parse_args()

  # Suppress Qt debug messages unless verbose mode is enabled
  if not args.verbose:
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false"

  if args.test:
    # Run tests
    result = run_tests()
    sys.exit(not result.wasSuccessful())
  else:
    # Run the GUI
    run_gui()
