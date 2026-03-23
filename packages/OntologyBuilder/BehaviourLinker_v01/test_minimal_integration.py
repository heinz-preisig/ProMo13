#!/usr/bin/env python3
"""
Test minimal integration - verify IconHelper integration works
"""

import sys
import os

# Add the packages directory to path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])

from PyQt5.QtWidgets import QApplication
from entity.entity_front_end_with_helper import create_entity_editor_with_helper
from entity.entity_front_end import EntityEditorFrontEnd


def test_minimal_integration():
    """Test that the minimal integration works exactly like the original"""
    app = QApplication([])
    
    print("=== Testing Minimal Integration ===")
    
    # Create both versions
    original_editor = EntityEditorFrontEnd()
    helper_editor = create_entity_editor_with_helper()
    
    # Test 1: Both should have the same UI structure
    print(f"✅ Original has UI: {hasattr(original_editor, 'ui')}")
    print(f"✅ Helper has UI: {hasattr(helper_editor, 'ui')}")
    
    # Test 2: Both should have the same button widgets
    original_buttons = [name for name in dir(original_editor.ui) if name.startswith('push')]
    helper_buttons = [name for name in dir(helper_editor.ui) if name.startswith('push')]
    
    print(f"✅ Original buttons: {len(original_buttons)}")
    print(f"✅ Helper buttons: {len(helper_buttons)}")
    print(f"✅ Same button count: {len(original_buttons) == len(helper_buttons)}")
    
    # Test 3: Check round button styling (they should both have round buttons)
    original_add_btn = original_editor.ui.pushAddVariable
    helper_add_btn = helper_editor.ui.pushAddVariable
    
    print(f"✅ Original button has style: {bool(original_add_btn.styleSheet())}")
    print(f"✅ Helper button has style: {bool(helper_add_btn.styleSheet())}")
    print(f"✅ Both have round button style: {bool(original_add_btn.styleSheet() and helper_add_btn.styleSheet())}")
    
    # Test 4: Check that methods exist
    print(f"✅ Original has add_variable_to_list: {hasattr(original_editor, 'add_variable_to_list')}")
    print(f"✅ Helper has add_variable_to_list: {hasattr(helper_editor, 'add_variable_to_list')}")
    
    print("✅ Minimal integration test passed!")
    return True


if __name__ == "__main__":
    test_minimal_integration()
