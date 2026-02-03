# Equation Selector Fixes for PNG Display and Multiple Equations

## Issues Identified

### Issue 1: PNG Files Not Displaying
**Problem**: PNG icons were not showing in the equation selector list.

**Root Cause**: 
- PNG files exist at correct locations
- Icon loading method needed improvement
- Icon size and display settings needed optimization

### Issue 2: Only One Equation Showing for Variable T
**Problem**: Variable T should show 2 equations but only 1 was displayed.

**Root Cause**:
- There are TWO variables with label "T":
  - **V_113** (Temperature, macroscopic network): Has **2 equations** (E_9, E_121)
  - **V_167** (T, reactions network): Has **1 equation** (E_60)
- The equation selector might be showing the wrong variable or not handling multiple equations properly

## Fixes Implemented

### Fix 1: Enhanced PNG Loading
```python
# Method 1: Load as QPixmap and scale
pixmap = QtGui.QPixmap(png_file)
if not pixmap.isNull():
    scaled_pixmap = pixmap.scaled(200, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
    icon = QtGui.QIcon(scaled_pixmap)
    item.setIcon(icon)

# Method 2: Direct QIcon loading as fallback
icon_direct = QtGui.QIcon(png_file)
if not icon_direct.isNull():
    item.setIcon(icon_direct)
```

### Fix 2: Optimized Display Settings
```python
self.equation_list.setIconSize(QtCore.QSize(200, 50))  # Optimized size
self.equation_list.setSpacing(5)
self.equation_list.setUniformItemSizes(True)
self.equation_list.setViewMode(QtWidgets.QListWidget.ListMode)
self.equation_list.setMinimumHeight(200)
```

### Fix 3: Comprehensive Debugging
Added detailed logging to track:
- Variable ID, label, and network
- Number of equations found
- Equation processing details
- PNG loading success/failure
- Item addition to list

### Fix 4: Improved Expression Handling
```python
# Try to get latex expression from variable data if not in equation dictionary
if 'expression' not in eq_data and 'rhs' in variable_equations[eq_id]:
    rhs_data = variable_equations[eq_id]['rhs']
    eq_expression = rhs_data.get('latex', 'No expression')
```

## Expected Debug Output

When you run the application and select variable T, you should see:

```
Debug: Variable ID: V_113
Debug: Variable label: T
Debug: Variable network: macroscopic
Debug: Variable equations: ['E_9', 'E_121']
Debug: Number of equations: 2
Debug: Equation dictionary has 148 equations
Debug: Processing equation E_9
Debug: Found E_9 in equation dictionary
Debug: E_9 -> Label: Equation_E_9, Expression: \frac{\partial{U}_{N}}{\partial{S}_{N}}, PNG: /path/to/E_9.png
✓ Loaded PNG icon for E_9: /path/to/E_9.png (1251x...)
Debug: Added item for E_9 to list
Debug: Processing equation E_121
Debug: Found E_121 in equation dictionary
Debug: E_121 -> Label: Equation_E_121, Expression: {H}_{N} . ({C_p}_{N})^{-1} + {T^{ref}}_{N}, PNG: /path/to/E_121.png
✓ Loaded PNG icon for E_121: /path/to/E_121.png (2068x...)
Debug: Added item for E_121 to list
Debug: Total items in equation list: 2
```

## What to Check

### 1. Variable Selection
- Verify which variable T is being selected (V_113 vs V_167)
- Check the debug output for variable ID and network
- V_113 should show 2 equations, V_167 should show 1

### 2. PNG Display
- Look for "✓ Loaded PNG icon" messages in debug output
- Check if PNG files appear as icons in the equation list
- Verify icon size and positioning

### 3. Multiple Equations
- Ensure both equations appear in the list
- Check that the list shows 2 items for V_113
- Verify both equations have proper labels and expressions

## Troubleshooting

### If PNGs Still Don't Show:
1. Check debug output for PNG loading messages
2. Verify PNG file paths are correct
3. Check if pixmap.isNull() returns true
4. Try different icon sizes

### If Only One Equation Shows:
1. Check which variable ID is being selected
2. Verify the variable has multiple equations in the JSON
3. Check if both equations are being processed
4. Verify both items are added to the list

## Files Modified

- `behavior_association/equation_selector.py` - Enhanced PNG loading, debugging, and display

## Test Cases

1. **Select V_113 (Temperature)**: Should show 2 equations with PNG icons
2. **Select V_167 (T interface)**: Should show 1 equation with PNG icon
3. **Select variable without equations**: Should show initialization option
4. **Check PNG loading**: All equations with PNG files should display icons

## Next Steps

Run the application and observe the debug output to identify:
- Which variable T is being selected
- Whether PNG files are loading successfully
- If multiple equations are being processed and displayed
