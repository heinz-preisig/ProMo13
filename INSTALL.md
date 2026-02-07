# Installation Guide

## System Requirements

### Python Version
- Python >= 3.13, < 3.14

### System Dependencies (Linux/Ubuntu)
For PyQt5 to work properly, the following system packages are required:

```bash
sudo apt-get install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xkb1 libxkbcommon-x11-0 libfontconfig1
```

### Python Dependencies
Install the Python dependencies using pip:

```bash
pip install -r requirements.txt
```

Or if you're using PDM:

```bash
pdm install
```

### PyQt5 Installation
After installing the system dependencies, reinstall PyQt5 to ensure it's properly linked:

```bash
pip uninstall pyqt5
pip install pyqt5>=5.15.11
```

Or if using a virtual environment, force reinstall:

```bash
/home/heinz/1_Gits/CAM12/ProMo12/.venv/bin/pip install --force-reinstall PyQt5
```

## Troubleshooting

### PyQt5 Display Issues
If you encounter display issues with PyQt5, ensure all the system dependencies listed above are installed, then reinstall PyQt5.

### Common Issues
- **Missing XCB libraries**: Install the system dependencies listed above
- **Display connection issues**: Ensure X11 forwarding is enabled if running via SSH
- **Font rendering issues**: Install `libfontconfig1` package

## Development Setup

For development, you may also want to install the optional dependencies:

```bash
pdm install --with lint,pytest,docs
```

## Docker Support

The project also includes Docker support. See `docker_instructions.md` for details on running the application in a container.
