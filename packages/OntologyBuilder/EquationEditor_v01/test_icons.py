#!/usr/local/bin/python3

import sys
import os

# Add to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_icons():
    try:
        from Common.resources_icons import getIcon
        from Common.common_resources import ICONS
        
        # Test a few common icons
        test_icons = ["info", "compile", "save", "PDF", "exit", "edit", "back"]
        
        print("Testing icon availability:")
        for icon_name in test_icons:
            try:
                icon = getIcon(icon_name)
                if icon is None:
                    print(f"  {icon_name}: None (MISSING)")
                else:
                    print(f"  {icon_name}: Available")
            except Exception as e:
                print(f"  {icon_name}: ERROR - {e}")
        
        # Show ICONS dictionary content
        print(f"\nAvailable icons in ICONS:")
        for key, value in ICONS.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error testing icons: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_icons()
