# 🌐 Multi-Domain Classification System

## ✅ System Status: FULLY FUNCTIONAL

The classification system now supports **different rules for different domain branches**:

- 🏗️ **Physical Branch**: Special rules (instantiate + input allowed)
- 🎮 **Control Branch**: Standard signal flow rules
- 💾 **Info Processing Branch**: Standard data flow rules  
- ⚗️ **Reaction Branch**: Standard reaction rules

## 🎯 Domain-Specific Rules

### **🏗️ Physical Branch**
```python
'physical': {
    'list_not_defined_variables': {
        'visible_buttons': ['input', 'instantiate', 'none'],
        # Cannot move directly to output
    },
    'list_instantiate': {
        'visible_buttons': ['instantiate', 'input', 'none'],
        # Can be in both instantiate + input (multiple selection)
    },
    'list_inputs': {
        'visible_buttons': ['none'],  # Only remove
    },
    'list_outputs': {
        'visible_buttons': ['none'],  # Only remove
    }
}
```

### **🎮 Control Branch**
```python
'control': {
    'list_not_defined_variables': {
        'visible_buttons': ['input', 'output', 'instantiate', 'none'],
        # Can classify as any single type
    },
    'list_inputs': {
        'visible_buttons': ['input', 'none'],
        # Standard input behavior
    },
    'list_outputs': {
        'visible_buttons': ['output', 'none'],
        # Standard output behavior
    },
    'list_instantiate': {
        'visible_buttons': ['instantiate', 'none'],
        # Standard instantiate behavior
    }
}
```

### **💾 Info Processing Branch**
```python
'info_processing': {
    'list_not_defined_variables': {
        'visible_buttons': ['input', 'output', 'instantiate', 'none'],
        # Can classify as any single type
    },
    'list_inputs': {
        'visible_buttons': ['input', 'none'],
        # Data inputs
    },
    'list_outputs': {
        'visible_buttons': ['output', 'none'],
        # Data outputs
    },
    'list_instantiate': {
        'visible_buttons': ['instantiate', 'none'],
        # Parameters and constants
    }
}
```

### **⚗️ Reaction Branch**
```python
'reaction': {
    'list_not_defined_variables': {
        'visible_buttons': ['input', 'output', 'instantiate', 'none'],
        # Can classify as any single type
    },
    'list_inputs': {
        'visible_buttons': ['input', 'none'],
        # Reactants and conditions
    },
    'list_outputs': {
        'visible_buttons': ['output', 'none'],
        # Products and results
    },
    'list_instantiate': {
        'visible_buttons': ['instantiate', 'none'],
        # Reaction parameters and rates
    }
}
```

## 🎮 How It Works

### **Automatic Domain Detection**
```python
def _get_entity_domain(self):
    """Get the domain branch for the current entity"""
    if hasattr(self, 'selected_entity_type') and self.selected_entity_type:
        return self.selected_entity_type.get('network', 'physical')
    return 'physical'  # Default to physical
```

### **Domain-Specific Rule Application**
```python
# The system automatically uses the correct rules based on entity domain
config = setup_dialog_with_rules(ui, list_name, var_info, current_classifications, domain)
success = validate_and_apply_classification(ui, list_name, var_id, entity, parent_widget, domain)
```

## 📋 User Experience by Domain

### **Physical Entity**
- **Pending**: `[Input, Instantiate, None]` (no direct output)
- **Instantiate**: `[Instantiate, Input, None]` (can select both)
- **Input**: `[None]` only (remove only)
- **Output**: `[None]` only (remove only)

### **Control/Info Processing/Reaction Entities**
- **Pending**: `[Input, Output, Instantiate, None]` (any single type)
- **Instantiate**: `[Instantiate, None]` (standard behavior)
- **Input**: `[Input, None]` (standard behavior)
- **Output**: `[Output, None]` (standard behavior)

## 🔧 Customization by Domain

### **Modify Physical Rules**
```python
'physical': {
    'list_not_defined_variables': {
        'visible_buttons': ['input', 'output', 'instantiate', 'none'],  # Add output
        'allowed_combinations': [
            ['input'], ['output'], ['instantiate'], ['none']
        ]
    }
}
```

### **Modify Control Rules**
```python
'control': {
    'list_instantiate': {
        'visible_buttons': ['instantiate', 'input', 'none'],  # Add input option
        'allowed_combinations': [
            ['instantiate'], ['input'], ['instantiate', 'input'], ['none']
        ]
    }
}
```

### **Add New Domain**
```python
'new_domain': {
    'list_inputs': {
        'visible_buttons': ['input', 'special', 'none'],
        'allowed_combinations': [['input'], ['special'], ['none']]
    }
    # ... other lists
}
```

## 🧪 Test Results

### **All Domains Working:**
- ✅ **Physical**: Special rules working (instantiate + input allowed)
- ✅ **Control**: Standard rules working
- ✅ **Info Processing**: Standard rules working
- ✅ **Reaction**: Standard rules working

### **Key Differences:**
- **Physical**: No direct output from pending, instantiate + input allowed
- **Others**: Standard single classification from pending

### **Automatic Switching:**
- System detects entity domain automatically
- Applies correct rules without user intervention
- Seamless user experience across domains

## 🚀 Benefits

### **1. Domain-Specific Behavior**
- Each domain has rules appropriate to its context
- Physical branch has special workflow requirements
- Other domains use standard classification patterns

### **2. Automatic Detection**
- No manual domain selection required
- Entity type determines rules automatically
- Transparent to the user

### **3. Easy Maintenance**
- Rules organized by domain
- Easy to modify specific domain behavior
- No impact on other domains when changing rules

### **4. Extensible**
- Easy to add new domains
- Consistent structure across domains
- Scalable architecture

## ✅ Status: READY FOR PRODUCTION

The multi-domain classification system is:
- ✅ **Fully implemented** and tested
- ✅ **Domain-specific rules** working correctly
- ✅ **Automatic domain detection** working
- ✅ **Easy to customize** and extend
- ✅ **Ready for all domain branches**

**The classification system now properly handles different rules for different domain branches!** 🎉
