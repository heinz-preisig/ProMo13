#!/usr/bin/env python3
"""
Main entry point for the PyQt5 MVC + Delegate example.
"""

import sys
import os
import argparse
from functools import partial
import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QApplication

# Add the current directory to the Python path so we can import our package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'packages')))
from Utilities.runner.models import ListModel, TableModel
from Utilities.runner.views import MainWindow
from Utilities.runner.delegates import SoftHighlightDelegate
from Utilities.runner.controllers import AppController


def run_gui():
  """Initialize and run the GUI application."""
  app = QApplication(sys.argv)

  # Set application style for better look
  app.setStyle('Fusion')

  # Create and show the main window
  view = MainWindow()
  delegate = SoftHighlightDelegate()


  # Create controller to manage the application logic
  controller = AppController( view)

  # Set initial window size and show
  view.setWindowTitle("PyQt5 MVC + Delegate Example")
  # view.resize(700, 500)
  view.show()

  # Start the event loop
  sys.exit(app.exec_())


def run_tests():
  """Run the test suite."""
  import unittest
  from Utilities.runner.tests import test_models, test_controller

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
