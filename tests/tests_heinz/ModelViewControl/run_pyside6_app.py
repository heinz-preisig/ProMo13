#!/usr/bin/env python3
"""
Main entry point for the PySide6 MVC + Delegate example.
"""

import sys
import os
import argparse

from PySide6.QtWidgets import QApplication

# Add the current directory to the Python path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyside6_mvc.models import ListModel, TableModel
from pyside6_mvc.views import MainWindow
from pyside6_mvc.delegates import SoftHighlightDelegate
from pyside6_mvc.controllers import AppController


def run_gui():
    """Initialize and run the GUI application."""
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application style for better look
    app.setStyle('Fusion')
    
    # Create the table model with sample data
    table_model = TableModel([["Alpha", "Value 1"], ["Beta", "Value 2"], ["Gamma", "Value 3"]])
    
    # Create the list model that wraps the table model
    list_model = ListModel(table_model)
    
    # Create the main window
    view = MainWindow()
    
    # Create delegate for custom item rendering
    delegate = SoftHighlightDelegate()
    
    # Create controller to manage the application logic
    controller = AppController(list_model, table_model, view, delegate)
    
    # Set initial window size and show
    view.setWindowTitle("PySide6 MVC + Delegate Example")
    view.show()
    
    # Start the event loop
    sys.exit(app.exec())


def run_tests():
    """Run the test suite."""
    import unittest
    from pyside6_mvc.tests import test_models, test_controller
    
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(test_models))
    suite.addTests(loader.loadTestsFromModule(test_controller))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PySide6 MVC + Delegate Example")
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
