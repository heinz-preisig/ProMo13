# PNG File Integration for Equation Selection

## Overview
This document summarizes the implementation of PNG file integration for equation selection in the entity editor. The changes ensure that LaTeX-rendered equation images are properly displayed in the equation selection interface.

## Changes Made

### 1. Ontology Container Enhancement
**File**: `Common/ontology_container.py`

**Method Modified**: `makeEquationDictionary()`

```python
def makeEquationDictionary(self):
    equation_dictionary = {}
    # Load PNG files first so we can add them to the dictionary
    equation_png_files = self.__load_equation_png_files()
    
    for var_ID in self.variables:
        for eq_ID in self.variables[var_ID]["equations"]:
            equation_dictionary[eq_ID] = self.variables[var_ID]["equations"][eq_ID]
            equation_dictionary[eq_ID]["lhs"] = self.variables[var_ID]["compiled_lhs"]
            # Add PNG file path to equation dictionary
            equation_dictionary[eq_ID]["png_file"] = equation_png_files.get(eq_ID, None)
    return equation_dictionary
```

**Key Changes**:
- Now loads PNG file paths using existing `__load_equation_png_files()` method
- Adds `png_file` field to each equation entry in the dictionary
- Maintains backward compatibility by setting `None` when PNG file doesn't exist

### 2. Equation Selector Enhancement
**File**: `behavior_association/equation_selector.py`

**Method Modified**: `load_equations()`

```python
def load_equations(self):
    """Load available equations for the selected variable from the ontology container"""
    # Get equations from variable data first (to get the list of equation IDs)
    variable_equations = self.variable_data.get('equations', {})
    
    # Get full equation data from ontology container's equation dictionary
    equation_dictionary = getattr(self.ontology_container, 'equation_dictionary', {})
    
    # Add each equation to the list
    for eq_id in variable_equations:
        # Get equation data from ontology container (has PNG file info)
        eq_data = equation_dictionary.get(eq_id, {})
        
        # Fall back to variable data if not found in dictionary
        if not eq_data:
            eq_data = variable_equations[eq_id]
        
        eq_label = eq_data.get('label', f'Equation_{eq_id}')
        eq_expression = eq_data.get('expression', 'No expression')
        png_file = eq_data.get('png_file')  # Now available from equation dictionary
        
        # Create list item with PNG icon if available
        if png_file and os.path.exists(png_file):
            icon = QtGui.QIcon(png_file)
            item.setIcon(icon)
```

**Key Changes**:
- Now retrieves equation data from ontology container's `equation_dictionary`
- Accesses PNG file path from the enhanced equation dictionary
- Maintains fallback to variable data for robustness
- Properly handles PNG file display in the equation list

**Method Modified**: `show_equation_details()`

```python
def show_equation_details(self, eq_id):
    """Show details of the selected equation"""
    # Get equation data from ontology container's equation dictionary first
    equation_dictionary = getattr(self.ontology_container, 'equation_dictionary', {})
    eq_data = equation_dictionary.get(eq_id, {})
    
    # Fall back to variable data if not found in dictionary
    if not eq_data:
        equations = self.variable_data.get('equations', {})
        eq_data = equations.get(eq_id, {})
```

**Key Changes**:
- Also uses ontology container's equation dictionary for details display
- Maintains consistent data source across the interface

## Data Flow

1. **Ontology Loading**:
   - `OntologyContainer.__load_equation_png_files()` loads PNG file paths
   - `OntologyContainer.makeEquationDictionary()` adds PNG paths to equation data

2. **Equation Selection**:
   - Variable selection provides list of equation IDs
   - Equation selector retrieves full equation data from `equation_dictionary`
   - PNG files are displayed as icons in the equation list

3. **Fallback Mechanism**:
   - If equation data not found in dictionary, falls back to variable data
   - Ensures robustness even if ontology structure changes

## Benefits

1. **Centralized PNG Management**: All PNG file paths are managed in one place
2. **Consistent Data Source**: Equation selector uses the same data as other components
3. **Improved UI**: LaTeX equations are properly displayed as images
4. **Backward Compatibility**: Works even when PNG files don't exist
5. **Robust Error Handling**: Graceful fallbacks prevent crashes

## Testing

Two test scripts have been created:

1. **`test_equation_selection.py`**: Tests the equation selector dialog with mock data
2. **`test_png_integration.py`**: Tests the PNG file integration in the ontology container

## Usage

The equation selection interface now automatically:
- Displays LaTeX-rendered equations as PNG images when available
- Shows equation labels and expressions
- Provides fallback when PNG files are missing
- Maintains full functionality for initialization-only variables

## Future Enhancements

Potential improvements:
1. **PNG Generation**: Automatic PNG generation for equations without images
2. **Caching**: Cache PNG icons for better performance
3. **Error Reporting**: Better user feedback when PNG files are missing
4. **Dynamic Loading**: Load PNG files on-demand for large ontologies
