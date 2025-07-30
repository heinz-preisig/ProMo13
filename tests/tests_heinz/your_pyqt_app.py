#!/usr/bin/env python3
"""
Simple PyQt5 test application to verify if the environment is set up correctly.
"""
import sys
from PyQt5 import QtWidgets, QtCore

def main():
    print("Starting PyQt5 test application...")
    print(f"Python version: {sys.version}")
    print(f"Qt version: {QtCore.QT_VERSION_STR}")
    print(f"PyQt version: {QtCore.PYQT_VERSION_STR}")
    
    app = QtWidgets.QApplication(sys.argv)
    print("QApplication created successfully")
    
    window = QtWidgets.QWidget()
    window.setWindowTitle("PyQt5 Test")
    window.resize(300, 200)
    
    layout = QtWidgets.QVBoxLayout()
    label = QtWidgets.QLabel("If you can see this, PyQt5 is working correctly!")
    layout.addWidget(label)
    
    button = QtWidgets.QPushButton("Close")
    button.clicked.connect(window.close)
    layout.addWidget(button)
    
    window.setLayout(layout)
    window.show()
    
    print("Window displayed. If you can see it, X11 forwarding is working.")
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
