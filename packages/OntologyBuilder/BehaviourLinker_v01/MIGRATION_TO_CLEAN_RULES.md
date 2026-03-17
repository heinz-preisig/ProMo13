# Migration to Clean Classification Rules

## 🎯 Current Problem
- Classification logic is mixed with dialog code
- Rules are hard to modify without affecting other code
- UI visibility logic is scattered throughout the dialog

## 🚀 Clean Solution
- Separate rules module (`classification_rules.py`)
- Clean dialog logic
- Easy rule editing without side effects

## 📋 Migration Steps

### Step 1: Add Import
Add this to the top of `entity_front_end.py`:
```python
from OntologyBuilder.BehaviourLinker_v01.classification_rules import (
    setup_dialog_with_rules, 
    validate_and_apply_classification
)
```

### Step 2: Add Clean Dialog Method
Add this method to the `EntityEditorFrontEnd` class:
```python
def show_clean_classification_dialog(self, list_name, var_id, is_reservoir_mode=False):
    """Clean classification dialog using rules module"""
    from PyQt5.QtWidgets import QDialog, QPushButton
    from OntologyBuilder.BehaviourLinker_v01.UIs.class_selector import Ui_Dialog
    
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
    
    # Setup dialog using rules module
    config = setup_dialog_with_rules(ui, list_name, var_info, current_classifications)
    
    # Reservoir mode handling
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
        success = validate_and_apply_classification(
            ui, list_name, var_id, self.current_entity, self
        )
        
        if success:
            self.populate_lists_from_entity(self.current_entity)
```

### Step 3: Replace Dialog Call
Find this section around line 1187:
```python
# OLD CODE:
if list_name in ['list_inputs', 'list_outputs', 'list_instantiate', 'list_not_defined_variables']:
    # Show classification dialog for these lists
    # [150+ lines of complex dialog logic...]
```

Replace with:
```python
# NEW CODE:
if list_name in ['list_inputs', 'list_outputs', 'list_instantiate', 'list_not_defined_variables']:
    self.show_clean_classification_dialog(list_name, var_id, is_reservoir_mode)
```

### Step 4: Remove Old Validation Method
You can now remove the `_validate_classification_rules` method since it's in the rules module.

## 🎯 Benefits After Migration

### ✅ Easy Rule Editing
Edit `classification_rules.py` without touching other code:
```python
'list_outputs': {
    'visible_buttons': ['output', 'instantiate', 'none'],  # Change visibility
    'allowed_combinations': [
        ['output'],
        ['instantiate'],
        ['output', 'instantiate'],  # Change allowed combos
        ['none']
    ],
    'description': 'Output and instantiate variables allowed'
}
```

### ✅ Clean Dialog Logic
The dialog code becomes simple and focused:
```python
# Setup UI with rules
config = setup_dialog_with_rules(ui, list_name, var_info, current_classifications)

# Validate and apply with rules  
success = validate_and_apply_classification(ui, list_name, var_id, entity, parent)
```

### ✅ No Side Effects
- Changing rules doesn't affect dialog code
- Changing dialog doesn't affect rules
- Each can be tested independently

## 🎮 How It Works

### Rule-Based Visibility
```python
# Only relevant buttons are shown
list_inputs → ['input', 'none']
list_outputs → ['output', 'instantiate', 'none']  
list_not_defined_variables → ['none']  # Only none option
```

### Rule-Based Validation
```python
# Automatic validation based on rules
input + output → ❌ Blocked (with message)
instantiate + output → ✅ Allowed
pending + anything → ❌ Blocked (with message)
```

### Easy Customization
```python
# Want to allow input + output? Just change the rules:
'list_inputs': {
    'allowed_combinations': [
        ['input'],
        ['output'],        # Add this
        ['input', 'output'], # Add this
        ['none']
    ]
}
```

## 🔄 Testing the Migration

1. **Backup current code**: `git stash` or copy file
2. **Apply migration steps**
3. **Test each list type**:
   - Inputs list: Should only show Input/None
   - Outputs list: Should show Output/Instantiate/None
   - Instantiate list: Should show Instantiate/Output/None  
   - Pending list: Should only show None
4. **Test validation rules**:
   - Try invalid combinations (should show warnings)
   - Try valid combinations (should work)
5. **Test reservoir mode** (if you use it)

## 🎯 Result

After migration:
- ✅ **Rules are separate** - easy to edit
- ✅ **Dialog is clean** - simple logic
- ✅ **No side effects** - safe modifications
- ✅ **Maintainable** - clear separation of concerns
