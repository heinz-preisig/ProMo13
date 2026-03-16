# 🎯 Physical Branch Classification Rules

## ✅ Updated Rules Summary

### **📝 Pending Variables (`list_not_defined_variables`)**
- **Visible buttons**: `[Input, Instantiate, None]`
- **Allowed actions**:
  - `Input` → Move to inputs list
  - `Instantiate` → Move to instantiate list  
  - `None` → Keep as pending
- **Blocked**: `Output` (cannot move directly to output)
- **Multiple selection**: No

### **⚙️ Instantiate Variables (`list_instantiate`)**
- **Visible buttons**: `[Instantiate, Input, None]`
- **Allowed actions**:
  - `Instantiate` only → Keep as instantiate only
  - `Instantiate + Input` → Add input classification (multiple)
  - `None` → Remove all classifications (become pending)
- **Blocked**: `Output` (cannot be in output list)
- **Multiple selection**: Yes (instantiate + input)

### **📥 Input Variables (`list_inputs`)**
- **Visible buttons**: `[None]` only
- **Allowed actions**:
  - `None` → Remove input classification (become pending)
- **Blocked**: `Input`, `Output`, `Instantiate` (cannot add, only remove)
- **Multiple selection**: No

### **📤 Output Variables (`list_outputs`)**
- **Visible buttons**: `[None]` only
- **Allowed actions**:
  - `None` → Remove output classification (become pending)
- **Blocked**: `Input`, `Output`, `Instantiate` (cannot add, only remove)
- **Multiple selection**: No

## 🎮 Physical Branch Workflow

### **Step 1: Start with Pending Variables**
```
📝 Pending Variables
├── Click Input → 📥 Input Variables
├── Click Instantiate → ⚙️ Instantiate Variables
└── Click None → 📝 Keep Pending
```

### **Step 2: Work with Instantiate Variables**
```
⚙️ Instantiate Variables
├── Click Instantiate only → ⚙️ Keep as Instantiate
├── Click Instantiate + Input → ⚙️📥 Instantiate + Input
└── Click None → 📝 Remove to Pending
```

### **Step 3: Remove Classifications**
```
📥 Input Variables → Click None → 📝 Pending
📤 Output Variables → Click None → 📝 Pending
```

## 🚫 Rule Enforcement

### **Blocked Operations:**
- ❌ **Pending → Output**: Cannot move directly to output
- ❌ **Input → Add Input**: Cannot add input, only remove
- ❌ **Output → Add Output**: Cannot add output, only remove
- ❌ **Instantiate → Output**: Cannot be in output list
- ❌ **Pending → Input + Instantiate**: Cannot select both at once

### **Allowed Operations:**
- ✅ **Pending → Input**: Move to input list
- ✅ **Pending → Instantiate**: Move to instantiate list
- ✅ **Instantiate + Input**: Variable can be in both lists
- ✅ **Input → None**: Remove input classification
- ✅ **Output → None**: Remove output classification
- ✅ **Instantiate → None**: Remove all classifications

## 🎯 User Experience

### **What Users See:**

**Pending List:**
```
[✓] Input  [✓] Instantiate  [✓] None
```

**Instantiate List:**
```
[✓] Instantiate  [✓] Input  [✓] None
(Can select both Instantiate and Input)
```

**Input List:**
```
[✓] None
(Only option is to remove input)
```

**Output List:**
```
[✓] None
(Only option is to remove output)
```

## 🔧 Customization

### **To Change Rules:**
Edit `classification_rules.py`:

```python
'list_not_defined_variables': {
    'visible_buttons': ['input', 'instantiate', 'output', 'none'],  # Add output
    'allowed_combinations': [
        ['input'], ['instantiate'], ['output'], ['none']  # Allow output
    ]
}
```

### **To Allow Multiple Selections:**
```python
'list_not_defined_variables': {
    'allowed_combinations': [
        ['input'], ['instantiate'], ['input', 'instantiate'], ['none']  # Allow both
    ]
}
```

## ✅ Status: READY FOR USE

The physical branch classification rules are now:
- ✅ **Fully implemented** and tested
- ✅ **Match your specifications** exactly
- ✅ **Ready for production use**
- ✅ **Easy to customize** if needed

**The classification system now works exactly as you specified for the physical branch!** 🎉
