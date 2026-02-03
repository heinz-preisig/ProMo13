# Circular Dependency Fix for Equation Dictionary

## Problem
The original implementation had a circular dependency issue:

```python
def makeEquationDictionary(self):
    equation_dictionary = {}
    # Load PNG files first so we can add them to the dictionary
    equation_png_files = self.__load_equation_png_files()  # ❌ This calls self.equation_dictionary
    
    for var_ID in self.variables:
        for eq_ID in self.variables[var_ID]["equations"]:
            equation_dictionary[eq_ID] = self.variables[var_ID]["equations"][eq_ID]
            # ...
```

The `__load_equation_png_files()` method tried to iterate over `self.equation_dictionary`, but `self.equation_dictionary` hadn't been created yet, causing an `AttributeError`.

## Solution
Implemented a two-pass approach with a new helper method:

### 1. New Helper Method
```python
def __load_equation_png_files_for_ids(self, equation_ids):
    """Load PNG files for a specific set of equation IDs"""
    dict_equation_png = {}
    latex_folder_path = Path(DIRECTORIES["latex_doc_location"] % self.ontology_name)
    for eq_id in equation_ids:  # ✅ Takes equation IDs as parameter
        equ_png_file_path = latex_folder_path / (eq_id + ".png")
        if OS.path.exists(equ_png_file_path):
            dict_equation_png[eq_id] = equ_png_file_path
    return dict_equation_png
```

### 2. Fixed makeEquationDictionary Method
```python
def makeEquationDictionary(self):
    equation_dictionary = {}
    
    # First pass: create basic dictionary without PNG files
    for var_ID in self.variables:
        for eq_ID in self.variables[var_ID]["equations"]:
            equation_dictionary[eq_ID] = self.variables[var_ID]["equations"][eq_ID]
            equation_dictionary[eq_ID]["lhs"] = self.variables[var_ID]["compiled_lhs"]
    
    # Second pass: add PNG files to the completed dictionary
    equation_png_files = self.__load_equation_png_files_for_ids(equation_dictionary.keys())  # ✅ Uses completed dictionary keys
    for eq_id in equation_dictionary:
        equation_dictionary[eq_id]["png_file"] = equation_png_files.get(eq_id, None)
    
    return equation_dictionary
```

## Key Changes

1. **Two-Pass Approach**: 
   - Pass 1: Create basic equation dictionary
   - Pass 2: Add PNG file paths

2. **New Helper Method**: `__load_equation_png_files_for_ids()` takes equation IDs as parameter instead of accessing `self.equation_dictionary`

3. **Eliminated Circular Dependency**: No more dependency on `self.equation_dictionary` before it's created

## Benefits

- ✅ **Fixes Circular Dependency**: Method can now be called during initialization
- ✅ **Maintains Functionality**: Still adds PNG file paths to equation dictionary
- ✅ **Backward Compatible**: Existing `__load_equation_png_files()` method preserved
- ✅ **Clean Separation**: PNG loading logic is properly separated

## Testing

The fix resolves the original error:
```
AttributeError: 'OntologyContainer' object has no attribute 'equation_dictionary'. 
Did you mean: 'makeEquationDictionary'?
```

The method can now be called safely during `OntologyContainer.__init__()` via `self.indexEquations()`.

## Files Modified

- `Common/ontology_container.py`: Fixed `makeEquationDictionary()` method and added `__load_equation_png_files_for_ids()` helper method
