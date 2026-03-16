"""
Clean Dialog Integration using Classification Rules Module
This shows how to simplify the dialog logic by using the separate rules module
"""

def show_clean_classification_dialog(self, list_name, var_id, is_reservoir_mode=False):
    """
    Clean classification dialog that uses the separate rules module
    
    This replaces the complex dialog logic with simple calls to the rules module
    """
    from PyQt5.QtWidgets import QDialog, QPushButton
    from OntologyBuilder.BehaviourLinker_v01.UIs.class_selector import Ui_Dialog
    from OntologyBuilder.BehaviourLinker_v01.classification_rules import (
        setup_dialog_with_rules, 
        validate_and_apply_classification
    )
    
    # Get variable information
    var_info = self._get_variable_info_for_classification(var_id)
    current_classifications = self._get_current_classification_for_variable(var_id)
    
    # Create dialog
    dialog = QDialog(self)
    dialog.setWindowTitle("Variable Classification")
    dialog.resize(250, 150)
    
    # Setup UI
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    
    # === CLEAN: Setup dialog using rules module ===
    config = setup_dialog_with_rules(ui, list_name, var_info, current_classifications)
    
    # Add reservoir mode handling if needed
    if is_reservoir_mode:
        from PyQt5.QtWidgets import QLabel
        instruction_label = QLabel("Reservoir mode: Multiple selections allowed")
        instruction_label.setStyleSheet("QLabel { color: blue; font-style: italic; }")
        ui.verticalLayout.insertWidget(1, instruction_label)
    
    # Add OK button
    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    ui.verticalLayout.addWidget(ok_button)
    
    # Show dialog and handle result
    if dialog.exec_() == QDialog.Accepted:
        # === CLEAN: Validate and apply using rules module ===
        success = validate_and_apply_classification(
            ui, list_name, var_id, self.current_entity, self
        )
        
        if success:
            # Refresh UI
            self.populate_lists_from_entity(self.current_entity)
        
        # No need for error handling - rules module handles it


# === INTEGRATION INSTRUCTIONS ===

"""
HOW TO INTEGRATE THIS CLEAN APPROACH:

1. Add import at the top of entity_front_end.py:
   from OntologyBuilder.BehaviourLinker_v01.classification_rules import (
       setup_dialog_with_rules, 
       validate_and_apply_classification
   )

2. Replace the existing dialog call with:
   self.show_clean_classification_dialog(list_name, var_id, is_reservoir_mode)

3. Add the clean dialog method to your EntityEditorFrontEnd class

4. Remove all the old validation logic - it's now in the rules module

BENEFITS:
✅ Rules are in a separate module - easy to edit
✅ Dialog logic is clean and simple
✅ UI visibility is controlled by rules
✅ Validation is centralized
✅ No impact on other code when rules change
"""
