"""
CLASSIFICATION RULES PATCH
Manual instructions for implementing the classification rules
"""

# === STEP 1: Add the validation method to EntityEditorFrontEnd class ===
# Add this method after the __init__ method (around line 135):

def _validate_classification_rules(self, var_id, classifications, current_list):
    """
    Validate and apply classification rules
    
    Rules:
    1. Variables cannot be in both inputs and outputs
    2. Variables in pending list cannot be in any other list  
    3. Variables in instantiated list can be in instantiated and outputs
    4. Choosing none resets the manual assignment
    """
    from PyQt5.QtWidgets import QMessageBox
    
    # Rule 4: Choosing none resets manual assignment
    if not classifications or "none" in classifications:
        return ["none"]  # Clear all classifications
    
    # Rule 2: If variable is in pending list, cannot be in any other list
    if current_list == 'list_not_defined_variables':
        # Pending variables cannot be classified elsewhere
        QMessageBox.warning(self, "Invalid Classification", 
                          "Variables in the pending list cannot be moved to other lists.")
        return None
    
    # Rule 1: Variables cannot be in both inputs and outputs
    if "input" in classifications and "output" in classifications:
        QMessageBox.warning(self, "Invalid Classification", 
                          "Variables cannot be in both inputs and outputs lists simultaneously.")
        return None
    
    # Rule 3: Variables in instantiated list can be in instantiated and outputs
    # This is allowed, so no validation needed
    
    return classifications


# === STEP 2: Modify the classification dialog logic ===
# Find this section around line 1238-1252:

# OLD CODE:
#                        # Collect all checked classifications (since buttons are now non-exclusive)
#                        classifications = []
#                        if ui.select_input.isChecked():
#                            classifications.append("input")
#                        if ui.select_output.isChecked():
#                            classifications.append("output")
#                        if ui.radioButton.isChecked():  # instantiate radio button
#                            classifications.append("instantiate")
#
#
#
#                        # Handle multiple classifications
#                        if not classifications:
#
#                            return

# REPLACE WITH:
#                        # Collect all checked classifications (since buttons are now non-exclusive)
#                        classifications = []
#                        if ui.select_input.isChecked():
#                            classifications.append("input")
#                        if ui.select_output.isChecked():
#                            classifications.append("output")
#                        if ui.radioButton.isChecked():  # instantiate radio button
#                            classifications.append("instantiate")
#
#                        # Apply classification rules
#                        validated_classifications = self._validate_classification_rules(var_id, classifications, list_name)
#                        
#                        if not validated_classifications:
#                            return
#
#                        # Handle multiple classifications
#                        if not validated_classifications:
#                            return


# === STEP 3: Update the classification application ===
# Find this section around line 1260:

# OLD CODE:
#                        # Use the new list-based classification system
#                        # This allows a variable to belong to multiple lists simultaneously
#                        if hasattr(self, 'current_entity') and self.current_entity:
#                            # Update the classification using the new system
#                            self.current_entity.change_classification(var_id, classifications)

# REPLACE WITH:
#                        # Use the new list-based classification system
#                        # This allows a variable to belong to multiple lists simultaneously
#                        if hasattr(self, 'current_entity') and self.current_entity:
#                            # Update the classification using the new system
#                            self.current_entity.change_classification(var_id, validated_classifications)


# === SUMMARY OF RULES IMPLEMENTED ===

"""
RULES IMPLEMENTED:

1. ✅ Variables cannot be in both inputs and outputs
   - Validation prevents simultaneous input/output classification
   - Shows warning message if attempted

2. ✅ Variables in pending list cannot be in any other list  
   - Prevents moving pending variables to other lists
   - Shows warning message if attempted

3. ✅ Variables in instantiated list can be in instantiated and outputs
   - This combination is allowed (no validation needed)
   - Variables can be in both instantiate and output lists

4. ✅ Choosing none resets the manual assignment
   - Selecting "none" clears all classifications
   - Returns ["none"] to reset the variable

The validation happens BEFORE the classification is applied, so invalid
classifications are rejected with appropriate warning messages.
"""
