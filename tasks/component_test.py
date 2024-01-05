
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import os

root = os.path.abspath(os.path.join(".."))
sys.path.append(root)

# fmt: off
from packages.shared_components.views.search_bar import SearchBarView
# fmt: on

# Create a simple application
app = QApplication([])

# Create a main window
window = QMainWindow()

# Create an instance of your custom widget
search_bar = SearchBarView()
search_bar.setFixedSize(200, 30)

# Set the custom widget as the central widget of the main window
window.setCentralWidget(search_bar)
# Or add some margins to the main window
window.setContentsMargins(10, 10, 10, 10)

# Show the main window
window.show()

# Start the application loop
app.exec_()
