# Ontology Rules System Documentation

## Overview
The ontology rule system controls behavior and properties of variable classes, node classes, and networks within the ontology editor. It's a runtime configuration system that determines how different components behave.

## Architecture

### 1. Rules Class (`Rules`)
**Purpose**: Template/initializer for new ontologies
- Located in: `OntologyFoundationEditor/rulesClass.py`
- Provides default empty structures
- **Only used during ontology initialization**, not at runtime

```python
class Rules(dict):
    def __init__(self):
        self["variable_classes"] = {
            "variable_classes_having_port_variables": [],
            "are_persistent_variables": [],
            "are_constants": [],
            "is_visible_in_interface": [],  # ← Our new rule
        }
        self["node_classes"] = {
            "nodes_allowing_token_injection": [],
            "nodes_allowing_token_conversion": [],
        }
        self["networks"] = {
            "network_enable_adding_indices": {},
            "normed_network": {},
        }
```

### 2. Runtime Storage (`ontology["rules"]`)
**Purpose**: Actual rule storage used by the system
- Flat dictionary structure stored in ontology file
- Accessed via `ontology_container.rules`
- Used by all components at runtime

```python
ontology["rules"] = {
    "is_visible_in_interface": ["control", "state"],
    "variable_classes_having_port_variables": ["dynamic"],
    "are_constants": ["parameter"],
    # ... other rules
}
```

## Rule Categories

### Variable Class Rules
Control behavior of variable types:
- `is_visible_in_interface`: Creates interface variables automatically
- `variable_classes_having_port_variables`: Allows port variable creation
- `are_persistent_variables`: Variables that persist between time steps
- `are_constants`: Variables that are numerically instantiated

### Node Class Rules
Control behavior of node types:
- `nodes_allowing_token_injection`: Nodes that can inject tokens
- `nodes_allowing_token_conversion`: Nodes that can convert tokens

### Network Rules
Control network properties:
- `network_enable_adding_indices`: Whether indices can be added to specific networks
- `normed_network`: Whether network is normed

## Rule Management Flow

### 1. Initialization (Foundation Editor)
```python
def __addFixedRules(self):
    RULES = Rules()  # Template
    rules = self.ontology["rules"]  # Runtime storage
    
    # Copy template to runtime if not exists
    for c in RULES:
        for r in RULES[c]:
            if r not in rules:
                rules[r] = RULES[c][r]
```

### 2. UI Interaction (Radio Buttons)
```python
def on_radioButtonIsInInterface_toggled(self, position):
    self.__setRuleValue(position, "is_visible_in_interface")

def __setRuleValue(self, position, rule):
    if position:
        # Prevent duplicates
        if self.current_behaviour_variable not in self.ontology["rules"][rule]:
            self.ontology["rules"][rule].append(self.current_behaviour_variable)
    else:
        try:
            self.ontology["rules"][rule].remove(self.current_behaviour_variable)
        except:
            pass
```

### 3. Runtime Usage (Equation Editor)
```python
# Check if variable type has rule
if (self.selected_variable_type in self.ontology_container.rules.get("is_visible_in_interface", [])):
    # Apply rule behavior
    self.__createInterfaceVariableAndEquation(var_ID, symbol, documentation)
```

## Key Points

1. **Template vs Runtime**: `Rules` class is only for initialization, `ontology["rules"]` is runtime
2. **List-based Storage**: All rules stored as lists (not sets) for serialization compatibility
3. **Duplicate Prevention**: Added checking to prevent multiple entries in rule lists
4. **UI Synchronization**: Radio buttons automatically update based on current rule values
5. **Persistence**: Rules are saved/loaded with ontology file

## Adding New Rules

### Step 1: Define in Rules Class
Add to `rulesClass.py`:
```python
self["variable_classes"] = {
    # ... existing rules
    "your_new_rule": [],
}
```

### Step 2: Add UI Radio Button
Add to `editor_foundation_ontology_gui.ui` and connect in `rulesClass.py`:
```python
self["your_new_rule"] = ui.radioButtonYourNewRule
```

### Step 3: Add Toggle Handler
Add to `editor_foundation_ontology_gui_impl.py`:
```python
def on_radioButtonYourNewRule_toggled(self, position):
    self.__setRuleValue(position, "your_new_rule")
```

### Step 4: Use in Runtime Code
Check rule in your component:
```python
if (your_variable_type in self.ontology_container.rules.get("your_new_rule", [])):
    # Apply your rule behavior
    pass
```

## Our New Rule: `is_visible_in_interface`

The `is_visible_in_interface` rule follows this exact pattern:

1. **Definition**: Added to `Rules` class template
2. **UI Component**: Radio button `radioButtonIsInInterface`
3. **Handler**: `on_radioButtonIsInInterface_toggled()` method
4. **Runtime Usage**: Equation Editor checks rule to create interface variables
5. **Behavior**: Automatically creates `<domain>_<variable>` interface variable and equation

### Implementation Details
- **Interface Variable Name**: `<domain_name>_<variable_name>`
- **Interface Equation**: `<domain_name>_<variable_name> = <variable_name>`
- **Storage**: Both variable and equation stored in interface domain
- **Trigger**: When creating new variable/equation for variable type in rule list

## File Locations

- **Rules Definition**: `OntologyFoundationEditor/rulesClass.py`
- **UI Definition**: `OntologyFoundationEditor/editor_foundation_ontology_gui.ui`
- **UI Implementation**: `OntologyFoundationEditor/editor_foundation_ontology_gui_impl.py`
- **Runtime Usage**: `EquationEditor_v01/ui_equations_impl.py`

## Debugging Tips

1. **Check Rule Values**: 
   ```python
   print(self.ontology_container.rules["is_visible_in_interface"])
   ```

2. **Verify UI Sync**: Radio buttons should reflect current rule state when selecting variable classes

3. **Check Runtime Behavior**: Ensure rule checking code uses correct rule name and access pattern

4. **Duplicate Issues**: The `__setRuleValue` method now prevents duplicates automatically

This system provides a flexible, extensible way to control ontology behavior while maintaining backward compatibility and proper persistence.
