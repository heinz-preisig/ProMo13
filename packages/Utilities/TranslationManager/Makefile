# Makefile

# Specify the name of your application
APP_NAME = main.py

# Specify the path to the PyQt5 tools
PYUIC = pyuic5
PYRCC = pyrcc5

# Specify the paths of the directories
UI_DIR = views/UIs
PY_DIR = views/Compiled_UIs
QRC_DIR = resources

# Get the list of UI file names
UI_FILES = $(notdir $(wildcard $(UI_DIR)/*.ui))

# Generate the corresponding Python file names
PY_FILES = $(patsubst %.ui,$(PY_DIR)/%_ui.py,$(UI_FILES))

# Generate the dependencies for the UI files
UI_DEPENDENCIES = $(addprefix $(PY_DIR)/,$(UI_FILES:.ui=_ui.py))

all: build

build: $(UI_DEPENDENCIES) $(QRC_DIR)/resources_rc.py

run:
	python3 $(APP_NAME)

$(PY_DIR)/%_ui.py: $(UI_DIR)/%.ui
	$(PYUIC) $< -o $@

$(QRC_DIR)/resources_rc.py: $(QRC_DIR)/resources.qrc
	$(PYRCC) $< -o $@

clean:
	rm -f $(PY_DIR)/*.py

.PHONY: all compile clean
