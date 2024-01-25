ROOT_DIR = .
INSTANTIATION_TOOL_PATH = $(ROOT_DIR)/packages/Utilities/InstantiationTool
DIALOGS_PATH = $(ROOT_DIR)/packages/dialogs

all: \
	build_dialogs \
	build_instantiation_tool

build_dialogs:
	@echo "==================="
	@echo "Building Dialogs..."
	@echo "==================="
	$(MAKE) -C $(DIALOGS_PATH)

build_instantiation_tool:
	@echo "============================="
	@echo "Building InstantiationTool..."
	@echo "============================="
	$(MAKE) -C $(INSTANTIATION_TOOL_PATH)

clean_all: \
	clean_dialogs \
	clean_instantiation_tool

clean_dialogs:
	@echo "==================="
	@echo "Cleaning Dialogs..."
	@echo "==================="
	$(MAKE) -C $(DIALOGS_PATH) clean

clean_instantiation_tool:
	@echo "============================="
	@echo "Cleaning InstantiationTool..."
	@echo "============================="
	$(MAKE) -C $(INSTANTIATION_TOOL_PATH) clean

