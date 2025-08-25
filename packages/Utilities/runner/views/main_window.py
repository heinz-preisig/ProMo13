import os
import sys
import traceback
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPlainTextEdit


class ErrorConsole(QPlainTextEdit):
  """A simple error console widget that displays error messages."""

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setReadOnly(True)
    self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monospace';
                font-size: 10pt;
            }
        """)
    self.setMaximumBlockCount(1000)  # Limit number of lines

  def append_message(self, message, message_type='info'):
    """Append a message to the console with timestamp and color coding."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Set color based on message type
    if message_type == 'error':
      color = '#f48771'  # Light red
    elif message_type == 'warning':
      color = '#dcdcaa'  # Light yellow
    else:
      color = '#9cdcfe'  # Light blue

    # Format the message with HTML for colors
    formatted_message = (
            f'<span style="color:#6a9955">[{timestamp}]</span> '
            f'<span style="color:{color}">{message}</span>'
    )

    # Move cursor to end and insert HTML
    self.moveCursor(QTextCursor.End)
    self.textCursor().insertHtml(formatted_message + '<br>')
    self.ensureCursorVisible()


class MainWindow(QMainWindow):
  """Main application window with a stacked widget for list and table views."""

  LIST_MODE = 0
  TABLE_MODE = 1

  def __init__(self):
    """Initialize the main window and load the UI."""
    super().__init__()
    self.setWindowFlag(Qt.FramelessWindowHint)

    # Load the UI file
    ui_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ui', 'main_window.ui'
            )
    uic.loadUi(ui_file, self)

    # Initialize error console
    self._init_error_console()

    # Redirect stderr to our error console
    sys.stderr = self

  def _init_error_console(self):
    """Initialize and dock the error console."""
    # Create error console widget
    self.error_console = ErrorConsole()

    # Create dock widget
    dock = QDockWidget("Error Console", self)
    dock.setWidget(self.error_console)
    dock.setFeatures(QDockWidget.DockWidgetClosable |
                     QDockWidget.DockWidgetMovable |
                     QDockWidget.DockWidgetFloatable)

    # Add dock to the bottom of the main window
    self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    # Initially hide the dock to save space
    dock.hide()

    # Store reference to toggle later
    self.error_console_dock = dock

  def show_error_console(self, show=True):
    """Show or hide the error console."""
    self.error_console_dock.setVisible(show)

  def log_error(self, message):
    """Log an error message to the console."""
    self.error_console.append_message(str(message), 'error')

  def log_warning(self, message):
    """Log a warning message to the console."""
    self.error_console.append_message(str(message), 'warning')

  def log_info(self, message):
    """Log an info message to the console."""
    self.error_console.append_message(str(message), 'info')

  def write(self, text):
    """Override write to capture stderr output."""
    if text.strip():
      self.log_error(text.strip())

  def flush(self):
    """Override flush for stderr compatibility."""
    pass

  def exception_hook(self, exc_type, exc_value, exc_traceback):
    """Global exception handler to log uncaught exceptions."""
    # Don't log keyboard interrupts
    if issubclass(exc_type, KeyboardInterrupt):
      sys.__excepthook__(exc_type, exc_value, exc_traceback)
      return

    # Format the exception
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    self.log_error(f"Uncaught exception: {error_msg}")

    # Show the console when an error occurs
    self.show_error_console(True)

  #
