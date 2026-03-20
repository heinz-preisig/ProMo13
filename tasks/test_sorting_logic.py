#!/usr/bin/python3
# encoding: utf-8

"""
===============================================================================
Test equation sorting logic
===============================================================================
"""

# Test data - equations with proper numerical sequence
equations = {
    'E_1': {'lhs': 'V_1', 'rhs': 'V_2 + V_3'},
    'E_2': {'lhs': 'V_4', 'rhs': 'V_5 * 2'},
    'E_3': {'lhs': 'V_6', 'rhs': 'V_7 + V_8'},
    'E_7': {'lhs': 'V_1', 'rhs': 'V_2 + V_3'},
    'E_5': {'lhs': 'V_4', 'rhs': 'V_5 * 2'},
    'E_10': {'lhs': 'V_1', 'rhs': 'V_2 + V_3'}
}

print("Testing equation ID extraction and sorting...")

# Test the sorting logic
equation_ids = []
for eq_id in equations.keys():
    if eq_id.startswith('E_'):
        try:
            num = int(eq_id[2:])
            equation_ids.append((num, eq_id))
            print(f'E_{eq_id} -> {num}')
        except ValueError:
            equation_ids.append((float('inf'), eq_id))
            print(f'E_{eq_id} -> ERROR')

# Sort numerically
equation_ids.sort()

print(f'\nSorted order: {[eq_id for num, eq_id in equation_ids]}')
print(f'Expected order: E_1, E_2, E_3, E_5, E_7, E_10')

# Check if sorting is correct
expected_order = ['E_1', 'E_2', 'E_3', 'E_5', 'E_7', 'E_10']
actual_order = [eq_id for num, eq_id in equation_ids]

if actual_order == expected_order:
    print('✅ Sorting is CORRECT')
else:
    print('❌ Sorting is INCORRECT')
    print(f'Expected: {expected_order}')
    print(f'Actual:   {actual_order}')
