# PyQt5 MVC + Delegate Example

A demonstration of Model-View-Controller architecture with Qt's model/view framework and custom delegates for rendering items.

## Project Structure

```
pyqt5_mvc/
├── __init__.py           # Package initialization
├── models/               # Data models
│   ├── __init__.py
│   ├── list_model.py     # List model implementation
│   └── table_model.py    # Table model implementation
├── views/                # UI views
│   ├── __init__.py
│   └── main_window.py    # Main window implementation
├── delegates/            # Custom delegates
│   ├── __init__.py
│   └── soft_highlight_delegate.py  # Custom item rendering
├── controllers/          # Controllers
│   ├── __init__.py
│   └── app_controller.py # Main application controller
├── tests/                # Unit tests
│   ├── __init__.py
│   ├── test_models.py    # Model tests
│   └── test_controller.py # Controller tests
└── ui/                   # UI files
    └── main_window.ui    # Qt Designer UI file

run_app.py                # Main entry point
README.md                 # This file
```

## Features

- **MVC Architecture**: Clear separation of concerns between data, UI, and logic
- **Custom Delegate**: Beautiful rendering of list and table items with selection highlighting
  - Rounded rectangle selection with gradient background
  - High contrast text for better readability
  - Smooth visual feedback on selection
- **Synchronized Views**: List and table views stay in sync with a single data source
  - Changes in one view immediately reflect in the other
  - Consistent selection state across views
- **Unit Tests**: Comprehensive test coverage for models and controllers
- **Modern UI**: Clean, responsive interface built with Qt Designer
  - Toggle between list and table views
  - Intuitive add/delete operations
  - Visual feedback for user actions

## Requirements

- Python 3.7+
- PyQt5

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install PyQt5
```

## Running the Application

To run the application:

```bash
python run_app.py
```

## Running Tests

To run the test suite:

```bash
python run_app.py --test
```

## Usage

1. **List View**:
   - Add items using the text input and "Add Item" button
   - Select and delete items with the "Delete Selected" button
   - Switch to table view using the "Switch to Table" button

2. **Table View**:
   - Add rows with name/value pairs
   - Select and delete rows
   - Switch back to list view using the "Switch to List" button

## License

This project is open source and available under the MIT License.
