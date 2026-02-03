# PNG Display Fix for Equation Selector

## Problem
The equation selector was not displaying PNG images for equations, even though the PNG files exist in the correct location.

## Root Cause Analysis

### 1. **PNG Files Location Confirmed**
✅ PNG files exist at: `/home/heinz/1_Gits/CAM12/Ontology_Repository/processes_distributed_001/LaTeX/`
- Equation files: `E_1.png`, `E_2.png`, `E_3.png`, etc.
- Variable files: `V_1.png`, `V_2.png`, `V_3.png`, etc.
- All files have reasonable sizes (1-5KB)

### 2. **Path Resolution Working**
✅ The ontology container correctly resolves the LaTeX directory:
```
DIRECTORIES["latex_doc_location"] = JOIN(DIRECTORIES["ontology_repository"], "%s", DIRECTORIES["latex"])
# Results in: /home/heinz/1_Gits/CAM12/Ontology_Repository/processes_distributed_001/LaTeX
```

### 3. **PNG File Integration Working**
✅ The equation dictionary correctly includes PNG file paths via the circular dependency fix.

## Issues Identified and Fixed

### Issue 1: Icon Display Settings
**Problem**: Original icon size and display settings may not be optimal for equation images.

**Fix**: Adjusted the QListWidget settings:
```python
self.equation_list.setIconSize(QtCore.QSize(250, 60))  # Adjusted for equation images
self.equation_list.setSpacing(8)
self.equation_list.setUniformItemSizes(True)
self.equation_list.setViewMode(QtWidgets.QListWidget.ListMode)  # List mode for text + icon
```

### Issue 2: PNG Loading Robustness
**Problem**: Basic QIcon loading doesn't provide detailed error information.

**Fix**: Enhanced PNG loading with better error handling:
```python
# First try loading as QPixmap to get better error info
pixmap = QtGui.QPixmap(png_file)
if not pixmap.isNull():
    icon = QtGui.QIcon(pixmap)
    if not icon.isNull():
        item.setIcon(icon)
        print(f"✓ Loaded PNG icon for {eq_id}: {png_file} ({pixmap.width()}x{pixmap.height()})")
```

### Issue 3: Debug Information
**Problem**: No visibility into why PNG files weren't loading.

**Fix**: Added comprehensive debug logging:
- Variable equations found
- Equation dictionary size
- PNG file paths for each equation
- Loading success/failure with dimensions

## Testing

### Test Files Created:
1. **`debug_png_paths.py`** - Tests PNG file path resolution
2. **`test_png_loading.py`** - Tests actual PNG loading with PyQt5
3. **`simple_debug.py`** - Basic file system checks

### Expected Debug Output:
```
Debug: Variable equations: ['E_1', 'E_2', 'E_3']
Debug: Equation dictionary has 148 equations
Debug: Found E_1 in equation dictionary
Debug: E_1 -> PNG: /home/heinz/1_Gits/CAM12/Ontology_Repository/processes_distributed_001/LaTeX/E_1.png
✓ Loaded PNG icon for E_1: /path/to/E_1.png (250x60)
```

## Verification Steps

1. **Run the application** and check console output for PNG loading messages
2. **Select a variable** with equations in the entity editor
3. **Open equation selector** and verify PNG images appear
4. **Check debug output** for successful PNG loading

## Potential Remaining Issues

1. **Image Size**: Equation PNGs might be too large/small for the icon display
2. **Image Format**: PNGs might have transparency or format issues
3. **Qt Version**: Different Qt versions might handle PNG loading differently
4. **File Permissions**: PNG files might not be readable by the application

## Next Steps

1. **Test with actual application** to see debug output
2. **Verify PNG display** in the equation selector UI
3. **Adjust icon size** if needed based on actual PNG dimensions
4. **Consider alternative display** if QIcon approach still doesn't work

## Files Modified

- `behavior_association/equation_selector.py` - Enhanced PNG loading and display
- `Common/ontology_container.py` - Fixed circular dependency (previous fix)

## Test Command

```bash
cd /home/heinz/1_Gits/CAM12/ProMo12/packages/OntologyBuilder/BehaviourLinker_v01
python3 test_png_loading.py  # Test PNG loading (requires display)
```
