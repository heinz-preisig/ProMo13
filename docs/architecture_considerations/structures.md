# Promo Architecture considerations



VC Directory Structure Best Practices



now we have two examples pyqt5_mvc and pyside6_mvc. What is the standard in the directory structure? Does one generate a new structure for each task or in a larger project with several subtasks, does one combine the individual sections controller, modell etc.?

Let me help you understand the standard directory structure for PyQt5/PySide6 MVC applications. Here's a concise breakdown:

## Standard MVC Structure

### For Small to Medium Projects

```
project_name/
├── controllers/      # All controller classes
├── models/          # All model classes
├── views/           # All view classes
├── resources/       # Icons, images, UI files
└── main.py          # Application entry point
```

### For Larger Projects

```
project_name/
├── feature1/         # Feature/module 1
│   ├── __init__.py
│   ├── controller.py
│   ├── model.py
│   └── view.py
├── feature2/         # Feature/module 2
│   ├── __init__.py
│   ├── controller.py
│   ├── model.py
│   └── view.py
├── common/           # Shared utilities, base classes
├── resources/        # Icons, images, UI files
└── main.py           # Application entry point
```

## Key Points

1. **Single Application**: Use the first structure for a single, cohesive application.
2. **Modular Applications**: Use the second structure for applications with distinct, independent features.
3. **Shared Components**: Place shared models, utilities, or base classes in a `common` or `core` package.
4. **UI Files**: Keep `.ui` files in a `resources/ui` directory or alongside their view classes.

## Best Practices

- Keep related MVC components close together
- Use `__init__.py` files to create proper Python packages
- Consider using relative imports within packages
- Keep the entry point (`main.py`) lean

Would you like me to help you set up a specific structure for your project?



Feedback submitted



how about if it is not one main, but each feature is run independently but in a logical sequence?

For a workflow where features run independently but in sequence, here's a recommended structure:

```
project_name/
├── features/                # Main features directory
│   ├── feature1/            # First feature
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   ├── model.py
│   │   ├── view.py
│   │   └── main.py          # Entry point for this feature
│   │
│   └── feature2/            # Second feature
│       ├── __init__.py
│       ├── controller.py
│       ├── model.py
│       ├── view.py
│       └── main.py          # Entry point for this feature
│
├── common/                  # Shared components
│   ├── __init__.py
│   ├── utilities.py
│   └── data_models.py
│
└── run_workflow.py          # Optional: Script to run features in sequence
```

Key aspects:

1. **Self-contained Features**:

   - Each feature has its own MVC structure
   - Each has its own `main.py` for independent execution
   - Features can be run individually or as part of a sequence

2. **Shared Resources**:

   - Common utilities and models in `common/`
   - Shared UI components can be in `common/ui/`

3. **Workflow Script**: `run_workflow.py` could look like:

   ```
   pythonfrom features.feature1.main import run as run_feature1
   from features.feature2.main import run as run_feature2
   
   def main():
       # Run features in sequence
       result1 = run_feature1()
       if result1.success:
           run_feature2(result1.data)
   
   if __name__ == "__main__":
       main()
   ```

4. **Feature Interface**: Each feature's `main.py` should expose a consistent interface, e.g.:

   ```
   pythonclass FeatureResult:
       def __init__(self, success, data=None):
           self.success = success
           self.data = data
   
   def run(input
   ```

```
undefined
```



Feedback submitted



and if the sequence is manually controlled, thus no workflow script?

For a manually controlled sequence with independent but related features, here's a clean structure:

```
project_name/
├── features/                # Main features directory
│   ├── feature1/            # First feature
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   ├── model.py
│   │   ├── view.py
│   │   └── launcher.py      # GUI/CLI launcher for this feature
│   │
│   └── feature2/            # Second feature
│       ├── __init__.py
│       ├── controller.py
│       ├── model.py
│       ├── view.py
│       └── launcher.py      # GUI/CLI launcher for this feature
│
├── common/                  # Shared components
│   ├── __init__.py
│   ├── data/               # Shared data storage
│   ├── utils/              # Shared utilities
│   └── widgets/            # Shared UI components
│
└── main_launcher.py        # Optional: Central launcher UI
```

Key aspects:

1. **Self-contained Features**:

   - Each feature has its own MVC structure
   - `launcher.py` provides a consistent way to start each feature
   - Features can be launched independently

2. **Data Sharing**:

   - Common data directory for shared state

   - Use a simple data manager in `common/` to handle data passing

   - Example data manager:

     ```
     python# common/data/manager.py
     _shared_data = {}
     
     def set_data(key, value):
         _shared_data[key] = value
     
     def get_data(key, default=None):
         return _shared_data.get(key, default)
     ```

3. **Feature Launcher**: Each `launcher.py` provides a simple interface:

   ```
   python# features/feature1/launcher.py
   from .controller import Controller
   from .view import MainWindow
   
   def launch():
       controller = Controller()
       view = MainWindow(controller)
       view.show()
       return view  # or controller, depending on needs
   ```

4. **Central Launcher (Optional)**: A simple UI to launch features:

   ```
   python# main_launcher.py
   import sys
   from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
   
   class Launcher(QMainWindow):
       def __init__(self):
           super().__init__()
           self.init_ui()
           
       def init_ui(self):
           self.setWindowTitle("Feature Launcher")
           layout = QVBoxLayout()
           
           # Add buttons for each feature
           btn1 = QPushButton("Launch Feature 1")
           btn1.clicked.connect(self.launch_feature1)
           layout.addWidget(btn1)
           
           # Add more buttons as needed
           
           container = QWidget()
           container.setLayout(layout)
           self.setCentralWidget(container)
       
       def launch_feature1(self):
           from features.feature1.launcher import launch
           self.feature1 = launch()
   ```

5. **Running Features**:

   - Run individually: `python -m features.feature1.launcher`
   - Or use the central launcher: `python main_launcher.py`

This structure gives you:

- Complete independence between features
- Easy manual control over feature execution
- Simple way to share data when needed
- Flexibility to add/remove features
- Option to run features individually or through a central launcher