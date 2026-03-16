"""
Entity Editor Classification Module
Handles all classification-related operations including dialogs and rules
"""

from PyQt5.QtWidgets import QDialog, QPushButton, QLabel
from OntologyBuilder.BehaviourLinker_v01.UIs.class_selector import Ui_Dialog
from OntologyBuilder.BehaviourLinker_v01.classification_rules import (
    setup_dialog_with_rules, 
    validate_and_apply_classification
)


class EntityEditorClassification:
    """
    Manages all classification operations for the Entity Editor
    """
    
    def __init__(self, parent_dialog):
        """
        Initialize the classification manager
        
        Args:
            parent_dialog: The parent EntityEditorCore dialog
        """
        self.parent = parent_dialog
    
    def show_clean_classification_dialog(self, list_name, var_id, is_reservoir_mode=False):
        """
        Show clean classification dialog using rules module
        
        Args:
            list_name: Name of the list (e.g., 'list_inputs')
            var_id: Variable ID
            is_reservoir_mode: Whether in reservoir mode
        """
        # Get variable information and domain
        var_info = self._get_variable_info_for_classification(var_id)
        current_classifications = self._get_current_classification_for_variable(var_id)
        domain = self._get_entity_domain()
        
        # Create dialog
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Variable Classification")
        dialog.resize(250, 150)
        
        # Setup UI
        ui = Ui_Dialog()
        ui.setupUi(dialog)
        
        # Setup dialog using rules module with domain
        config = setup_dialog_with_rules(ui, list_name, var_info, current_classifications, domain)
        
        # Reservoir mode handling
        if is_reservoir_mode:
            instruction_label = QLabel("Reservoir mode: Multiple selections allowed")
            instruction_label.setStyleSheet("QLabel { color: blue; font-style: italic; }")
            ui.verticalLayout.insertWidget(1, instruction_label)
        
        # Add OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        ui.verticalLayout.addWidget(ok_button)
        
        # Show dialog and handle result
        if dialog.exec_() == QDialog.Accepted:
            success = validate_and_apply_classification(
                ui, list_name, var_id, self.parent.data.current_entity, self.parent, domain
            )
            
            if success:
                # Refresh UI
                self.parent.ui.populate_lists_from_entity(self.parent.data.current_entity)
    
    def _get_variable_info_for_classification(self, var_id):
        """
        Get variable information for classification
        
        Args:
            var_id: Variable ID
            
        Returns:
            dict: Variable information
        """
        return self.parent.data.get_variable_info(var_id)
    
    def _get_current_classification_for_variable(self, var_id):
        """
        Get current classification for variable
        
        Args:
            var_id: Variable ID
            
        Returns:
            list: Current classifications
        """
        return self.parent.data.get_current_classification_for_variable(var_id)
    
    def _get_entity_domain(self):
        """
        Get the domain branch for the current entity
        
        Returns:
            str: Domain branch (physical, control, info_processing, reaction)
        """
        return self.parent.data.get_entity_domain()
    
    def handle_classification_dialog(self, list_name, var_id, var_label, var_network, is_reservoir_mode=False):
        """
        Handle the classification dialog (legacy method for compatibility)
        
        Args:
            list_name: Name of the list
            var_id: Variable ID
            var_label: Variable label
            var_network: Variable network
            is_reservoir_mode: Whether in reservoir mode
        """
        # Use the new clean classification dialog
        self.show_clean_classification_dialog(list_name, var_id, is_reservoir_mode)
    
    def open_classification_dialog(self, list_name, var_id, var_label, var_network, is_reservoir_mode=False):
        """
        Open classification dialog (alternative method name)
        
        Args:
            list_name: Name of the list
            var_id: Variable ID
            var_label: Variable label
            var_network: Variable network
            is_reservoir_mode: Whether in reservoir mode
        """
        self.handle_classification_dialog(list_name, var_id, var_label, var_network, is_reservoir_mode)
    
    def open_equation_dialog(self, var_id, var_label, var_network, parent_widget=None):
        """
        Open equation dialog for a variable
        
        Args:
            var_id: Variable ID
            var_label: Variable label
            var_network: Variable network
            parent_widget: Parent widget for dialog
        """
        # Create equation dialog
        dialog = QDialog(parent_widget or self.parent)
        dialog.setWindowTitle(f"Equation for {var_label}")
        dialog.resize(400, 300)
        
        # Setup UI (simplified for now)
        from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QDialogButtonBox
        
        layout = QVBoxLayout()
        
        # Add text edit for equation
        equation_edit = QTextEdit()
        equation_edit.setPlaceholderText(f"Enter equation for {var_label}...")
        
        # Get current equation if exists
        if self.parent.data.current_entity:
            current_equations = getattr(self.parent.data.current_entity, 'equations', {})
            if var_id in current_equations:
                equation_edit.setText(current_equations[var_id])
        
        layout.addWidget(equation_edit)
        
        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            equation = equation_edit.toPlainText()
            self._save_equation(var_id, equation)
    
    def _save_equation(self, var_id, equation):
        """
        Save equation for a variable
        
        Args:
            var_id: Variable ID
            equation: Equation text
        """
        if self.parent.data.current_entity:
            if not hasattr(self.parent.data.current_entity, 'equations'):
                self.parent.data.current_entity.equations = {}
            
            if equation.strip():
                self.parent.data.current_entity.equations[var_id] = equation
            elif var_id in self.parent.data.current_entity.equations:
                del self.parent.data.current_entity.equations[var_id]
    
    def _open_simple_equation_dialog(self, var_id, var_label, var_network, parent_widget=None):
        """
        Open simple equation dialog
        
        Args:
            var_id: Variable ID
            var_label: Variable label
            var_network: Variable network
            parent_widget: Parent widget for dialog
        """
        # Simplified equation dialog
        self.open_equation_dialog(var_id, var_label, var_network, parent_widget)
    
    def get_classification_summary(self):
        """
        Get a summary of all classifications
        
        Returns:
            dict: Classification summary
        """
        summary = {
            'total_classified': 0,
            'by_type': {
                'input': 0,
                'output': 0,
                'instantiate': 0,
                'none': 0
            },
            'domain': self._get_entity_domain()
        }
        
        if self.parent.data.current_entity:
            classifications = getattr(self.parent.data.current_entity, 'local_variable_classifications', {})
            
            for var_id, var_class in classifications.items():
                class_list = var_class.get('classification', ['none'])
                summary['total_classified'] += 1
                
                for classification in class_list:
                    if classification in summary['by_type']:
                        summary['by_type'][classification] += 1
        
        return summary
    
    def validate_classifications(self):
        """
        Validate all classifications against current rules
        
        Returns:
            tuple: (is_valid, validation_results)
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'summary': self.get_classification_summary()
        }
        
        if not self.parent.data.current_entity:
            results['errors'].append("No current entity set")
            results['valid'] = False
            return results['valid'], results
        
        classifications = getattr(self.parent.data.current_entity, 'local_variable_classifications', {})
        domain = self._get_entity_domain()
        
        # Import rules for validation
        from OntologyBuilder.BehaviourLinker_v01.classification_rules import ClassificationRules
        rules = ClassificationRules()
        
        for var_id, var_class in classifications.items():
            class_list = var_class.get('classification', ['none'])
            
            # Validate each classification
            for list_name in ['list_inputs', 'list_outputs', 'list_instantiate', 'list_not_defined_variables']:
                is_valid, validated, error = rules.validate_selection(list_name, class_list, None, domain)
                
                if not is_valid:
                    results['errors'].append(f"Variable {var_id}: {error}")
                    results['valid'] = False
        
        return results['valid'], results
    
    def export_classifications(self):
        """
        Export classifications for saving
        
        Returns:
            dict: Exportable classification data
        """
        if not self.parent.data.current_entity:
            return {}
        
        return {
            'local_variable_classifications': getattr(self.parent.data.current_entity, 'local_variable_classifications', {}),
            'domain': self._get_entity_domain(),
            'summary': self.get_classification_summary()
        }
    
    def import_classifications(self, classification_data):
        """
        Import classifications from saved state
        
        Args:
            classification_data: Dictionary of classification data
        """
        if not classification_data or not self.parent.data.current_entity:
            return
        
        # Import classifications
        if 'local_variable_classifications' in classification_data:
            self.parent.data.current_entity.local_variable_classifications = classification_data['local_variable_classifications']
        
        # Refresh UI
        if hasattr(self.parent, 'ui') and self.parent.ui:
            self.parent.ui.populate_lists_from_entity(self.parent.data.current_entity)
