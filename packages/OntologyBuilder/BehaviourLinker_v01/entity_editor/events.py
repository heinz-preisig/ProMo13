"""
Entity Editor Events Module
Handles all user interactions and event handling for the Entity Editor
"""

from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt, QTimer


class EntityEditorEvents:
    """
    Manages all event handling for the Entity Editor
    """
    
    def __init__(self, parent_dialog):
        """
        Initialize the events manager
        
        Args:
            parent_dialog: The parent EntityEditorCore dialog
        """
        self.parent = parent_dialog
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.pending_click_data = None
        self._setup_event_connections()
    
    def _setup_event_connections(self):
        """Setup all event connections"""
        self._setup_list_handlers()
        self._setup_button_handlers()
        self._setup_context_menus()
        self._setup_click_timer()
    
    def _setup_list_handlers(self):
        """Setup list widget event handlers"""
        # Single click handlers
        self.parent.ui.list_inputs.itemClicked.connect(self.on_list_item_clicked)
        self.parent.ui.list_outputs.itemClicked.connect(self.on_list_item_clicked)
        self.parent.ui.list_instantiate.itemClicked.connect(self.on_list_item_clicked)
        self.parent.ui.list_not_defined_variables.itemClicked.connect(self.on_list_item_clicked)
        self.parent.ui.list_equations.itemClicked.connect(self.on_list_item_clicked)
        
        # Selection change handlers
        self.parent.ui.list_inputs.itemSelectionChanged.connect(self.on_list_selection_changed)
        self.parent.ui.list_outputs.itemSelectionChanged.connect(self.on_list_selection_changed)
        self.parent.ui.list_instantiate.itemSelectionChanged.connect(self.on_list_selection_changed)
        self.parent.ui.list_not_defined_variables.itemSelectionChanged.connect(self.on_list_selection_changed)
        self.parent.ui.list_equations.itemSelectionChanged.connect(self.on_list_selection_changed)
        
        # Double click handlers
        self.parent.ui.list_not_defined_variables.itemDoubleClicked.connect(self.on_list_pending_variables_double_clicked)
    
    def _setup_button_handlers(self):
        """Setup button event handlers"""
        # Main action buttons
        self.parent.ui.pushAccept.clicked.connect(self.on_pushAccept_pressed)
        self.parent.ui.pushCancle.clicked.connect(self.on_pushCancle_pressed)
        
        # Variable manipulation buttons
        self.parent.ui.pushAddVariable.clicked.connect(self.on_pushAddVariable_pressed)
        self.parent.ui.pushAddStateVariable.clicked.connect(self.on_pushAddStateVariable_pressed)
        self.parent.ui.pushAddTransport.clicked.connect(self.on_pushAddTransport_pressed)
        self.parent.ui.pushAddIntensitity.clicked.connect(self.on_pushAddIntensitity_pressed)
        self.parent.ui.pushDeleteVariable.clicked.connect(self.on_pushDeleteVariable_pressed)
    
    def _setup_context_menus(self):
        """Setup context menu handlers"""
        self.parent.ui.list_inputs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parent.ui.list_inputs.customContextMenuRequested.connect(self.on_context_menu_requested)
        
        self.parent.ui.list_outputs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parent.ui.list_outputs.customContextMenuRequested.connect(self.on_context_menu_requested)
        
        self.parent.ui.list_instantiate.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parent.ui.list_instantiate.customContextMenuRequested.connect(self.on_context_menu_requested)
        
        self.parent.ui.list_not_defined_variables.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parent.ui.list_not_defined_variables.customContextMenuRequested.connect(self.on_context_menu_requested)
        
        self.parent.ui.list_equations.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parent.ui.list_equations.customContextMenuRequested.connect(self.on_context_menu_requested)
    
    def _setup_click_timer(self):
        """Setup click timer for double-click detection"""
        self.click_timer.timeout.connect(self.on_single_click_timeout)
    
    def on_list_item_clicked(self, item):
        """Handle list item click events"""
        # Start single click timer
        click_data = {
            'item': item,
            'list_widget': item.listWidget(),
            'var_id': item.data(0, 32),
            'var_label': item.text(0),
            'timestamp': QTimer.currentTime()
        }
        
        self.pending_click_data = click_data
        self.click_timer.start(300)  # Wait for potential double-click
    
    def on_list_selection_changed(self):
        """Handle list selection change events"""
        # Update button states based on selection
        self._update_button_states()
        
        # Update accept button visibility
        self._update_accept_button_visibility()
    
    def on_list_pending_variables_double_clicked(self, item):
        """Handle double-click on pending variables list"""
        # Stop the single-click timer
        self.click_timer.stop()
        self.pending_click_data = None
        
        # Go directly to equation selection
        var_id = item.data(0, 32)
        var_label = item.text(0)
        
        self.parent.classification.open_equation_dialog(var_id, var_label, "")
    
    def on_list_pending_variables_single_clicked(self, item):
        """Handle single-click on pending variables"""
        var_id = item.data(0, 32)
        var_label = item.text(0)
        list_name = "list_not_defined_variables"
        
        # Show classification dialog
        self.parent.classification.show_clean_classification_dialog(list_name, var_id, False)
    
    def on_single_click_timeout(self):
        """Handle single-click timeout"""
        if self.pending_click_data:
            click_data = self.pending_click_data
            self.pending_click_data = None
            
            # Handle the single click
            self.handle_single_click(click_data)
    
    def handle_single_click(self, click_data):
        """
        Handle single click on list item
        
        Args:
            click_data: Dictionary containing click information
        """
        item = click_data.get('item')
        list_widget = click_data.get('list_widget')
        var_id = click_data.get('var_id')
        var_label = click_data.get('var_label')
        
        if not var_id or not list_widget:
            return
        
        # Determine list name
        list_name = self._get_list_name_from_widget(list_widget)
        
        # Check if we're in reservoir editing mode
        is_reservoir_mode = self._is_reservoir_mode()
        
        # Handle different behavior based on which list was clicked
        if var_id:
            if list_name in ['list_inputs', 'list_outputs', 'list_instantiate', 'list_not_defined_variables']:
                # Clean classification dialog with rules module
                self.parent.classification.show_clean_classification_dialog(list_name, var_id, is_reservoir_mode)
    
    def on_context_menu_requested(self, position):
        """Handle context menu requests"""
        list_widget = self.parent.sender()
        
        if not list_widget:
            return
        
        # Get item at position
        item = list_widget.itemAt(position)
        if not item:
            return
        
        var_id = item.data(0, 32)
        var_label = item.text(0)
        list_name = self._get_list_name_from_widget(list_widget)
        
        # Create context menu
        menu = QMenu(self.parent)
        
        # Add common actions
        if list_name != 'list_not_defined_variables':
            # Remove from current list action
            remove_action = QAction(f"Remove from {list_name.replace('list_', '').title()}", self.parent)
            remove_action.triggered.connect(lambda: self._remove_from_list(var_id, list_name))
            menu.addAction(remove_action)
        
        # Classification actions
        classify_menu = menu.addMenu("Classify As")
        
        # Add classification options based on domain
        domain = self.parent.data.get_entity_domain()
        if domain == 'physical':
            if list_name == 'list_not_defined_variables':
                classify_menu.addAction("Input", lambda: self._classify_as(var_id, 'input'))
                classify_menu.addAction("Instantiate", lambda: self._classify_as(var_id, 'instantiate'))
        else:
            # Other domains have different options
            classify_menu.addAction("Input", lambda: self._classify_as(var_id, 'input'))
            classify_menu.addAction("Output", lambda: self._classify_as(var_id, 'output'))
            classify_menu.addAction("Instantiate", lambda: self._classify_as(var_id, 'instantiate'))
        
        classify_menu.addAction("None", lambda: self._classify_as(var_id, 'none'))
        
        # Equation action (for pending variables)
        if list_name == 'list_not_defined_variables':
            equation_action = QAction("Set Equation...", self.parent)
            equation_action.triggered.connect(lambda: self.parent.classification.open_equation_dialog(var_id, var_label, ""))
            menu.addAction(equation_action)
        
        # Show menu
        menu.exec_(list_widget.mapToGlobal(position))
    
    def on_left_click_context_menu(self, position):
        """Handle left-click context menu"""
        self.on_context_menu_requested(position)
    
    def on_left_click_context_menu_for_widget(self, widget, position):
        """Handle context menu for specific widget"""
        # Similar to on_context_menu_requested but for specific widget
        item = widget.itemAt(position)
        if not item:
            return
        
        var_id = item.data(0, 32)
        var_label = item.text(0)
        list_name = self._get_list_name_from_widget(widget)
        
        # Create and show context menu
        self._create_context_menu(var_id, var_label, list_name, widget, position)
    
    def on_pushAccept_pressed(self):
        """Handle Accept button press"""
        # Validate entity data
        is_valid, errors = self.parent.data.validate_entity_data()
        
        if not is_valid:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self.parent, "Validation Error", "\\n".join(errors))
            return
        
        # Accept the dialog
        self.parent.accept()
    
    def on_pushCancle_pressed(self):
        """Handle Cancel button press"""
        # Cancel the dialog
        self.parent.reject()
    
    def on_pushAddVariable_pressed(self):
        """Handle Add Variable button press"""
        self._launch_new_variable_selector()
    
    def on_pushAddStateVariable_pressed(self):
        """Handle Add State Variable button press"""
        self._launch_state_variable_selector()
    
    def on_pushAddTransport_pressed(self):
        """Handle Add Transport button press"""
        # Handle transport addition
        pass
    
    def on_pushAddIntensitity_pressed(self):
        """Handle Add Intensity button press"""
        # Handle intensity addition
        pass
    
    def on_pushDeleteVariable_pressed(self):
        """Handle Delete Variable button press"""
        # Get selected variable
        var_id = self.parent.ui.get_selected_variable_id(self.parent.ui.list_inputs)
        if not var_id:
            var_id = self.parent.ui.get_selected_variable_id(self.parent.ui.list_outputs)
        if not var_id:
            var_id = self.parent.ui.get_selected_variable_id(self.parent.ui.list_instantiate)
        if not var_id:
            var_id = self.parent.ui.get_selected_variable_id(self.parent.ui.list_not_defined_variables)
        
        if var_id:
            self._delete_variable_from_context(var_id)
    
    def on_radio_selected(self):
        """Handle radio button selection"""
        # This is handled by the classification dialog
        pass
    
    def _get_list_name_from_widget(self, widget):
        """Get list name from widget"""
        if widget == self.parent.ui.list_inputs:
            return 'list_inputs'
        elif widget == self.parent.ui.list_outputs:
            return 'list_outputs'
        elif widget == self.parent.ui.list_instantiate:
            return 'list_instantiate'
        elif widget == self.parent.ui.list_not_defined_variables:
            return 'list_not_defined_variables'
        elif widget == self.parent.ui.list_equations:
            return 'list_equations'
        return 'unknown'
    
    def _is_reservoir_mode(self):
        """Check if we're in reservoir editing mode"""
        if hasattr(self.parent.data, 'current_entity_data') and self.parent.data.current_entity_data:
            return "constant|infinity" in self.parent.data.current_entity_data.get("entity_type", "")
        return False
    
    def _update_button_states(self):
        """Update button states based on current selection"""
        # Check if any list has a selection
        has_selection = any(
            list_widget.currentItem() is not None 
            for list_widget in [
                self.parent.ui.list_inputs,
                self.parent.ui.list_outputs,
                self.parent.ui.list_instantiate,
                self.parent.ui.list_not_defined_variables,
                self.parent.ui.list_equations
            ]
        )
        
        # Enable/disable variable manipulation buttons
        self.parent.ui.set_variable_buttons_enabled(has_selection)
    
    def _update_accept_button_visibility(self):
        """Update accept button visibility based on entity state"""
        # Enable accept button if entity has changes
        if hasattr(self.parent, 'changed') and self.parent.changed:
            self.parent.ui.set_accept_button_enabled(True)
        else:
            self.parent.ui.set_accept_button_enabled(False)
    
    def _remove_from_list(self, var_id, list_name):
        """Remove variable from specific list"""
        if self.parent.data.current_entity:
            # Set classification to 'none' to remove from all lists
            self.parent.data.current_entity.change_classification(var_id, ['none'])
            
            # Refresh UI
            self.parent.ui.populate_lists_from_entity(self.parent.data.current_entity)
    
    def _classify_as(self, var_id, classification):
        """Classify variable as specific type"""
        if self.parent.data.current_entity:
            self.parent.data.current_entity.change_classification(var_id, [classification])
            
            # Refresh UI
            self.parent.ui.populate_lists_from_entity(self.parent.data.current_entity)
    
    def _create_context_menu(self, var_id, var_label, list_name, widget, position):
        """Create context menu for variable"""
        menu = QMenu(self.parent)
        
        # Add actions based on context
        if list_name != 'list_not_defined_variables':
            remove_action = QAction(f"Remove from {list_name.replace('list_', '').title()}", self.parent)
            remove_action.triggered.connect(lambda: self._remove_from_list(var_id, list_name))
            menu.addAction(remove_action)
        
        # Classification menu
        classify_menu = menu.addMenu("Classify As")
        domain = self.parent.data.get_entity_domain()
        
        # Add domain-specific options
        if domain == 'physical':
            if list_name == 'list_not_defined_variables':
                classify_menu.addAction("Input", lambda: self._classify_as(var_id, 'input'))
                classify_menu.addAction("Instantiate", lambda: self._classify_as(var_id, 'instantiate'))
        else:
            classify_menu.addAction("Input", lambda: self._classify_as(var_id, 'input'))
            classify_menu.addAction("Output", lambda: self._classify_as(var_id, 'output'))
            classify_menu.addAction("Instantiate", lambda: self._classify_as(var_id, 'instantiate'))
        
        classify_menu.addAction("None", lambda: self._classify_as(var_id, 'none'))
        
        # Show menu
        menu.exec_(widget.mapToGlobal(position))
    
    def _launch_new_variable_selector(self):
        """Launch new variable selector dialog"""
        # This would open a dialog to select/create new variables
        pass
    
    def _launch_state_variable_selector(self):
        """Launch state variable selector dialog"""
        # This would open a dialog to select state variables
        pass
    
    def _delete_variable_from_context(self, var_id):
        """Delete variable from current context"""
        if self.parent.ui.confirm_action("Delete Variable", f"Are you sure you want to delete variable {var_id}?"):
            if self.parent.data.current_entity:
                # Remove variable from entity
                self.parent.data.current_entity.remove_variable(var_id)
                
                # Refresh UI
                self.parent.ui.populate_lists_from_entity(self.parent.data.current_entity)
