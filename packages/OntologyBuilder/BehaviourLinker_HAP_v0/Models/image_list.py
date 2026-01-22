from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel


class ImageListModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def load_data(self, data, pending=None):
        self.clear()
        
        print("\n=== DEBUG: ImageListModel.load_data ===")
        print(f"Received {len(data) if data is not None else 0} items to load")
        
        if not data:
            print("Warning: No data received to load")
            return
            
        for i, element in enumerate(data, 1):
            try:
                # Debug print for first 3 items and last item
                print(f"\nProcessing item {i}/{len(data)}")
                print(f"  Element type: {type(element).__name__}")
                print(f"  Element dir: {[attr for attr in dir(element) if not attr.startswith('__')]}")
                
                # Get ID
                if hasattr(element, 'get_id'):
                    item_id = element.get_id()
                    print(f"  Using get_id(): {item_id}")
                elif hasattr(element, 'id'):
                    item_id = str(element.id)
                    print(f"  Using element.id: {item_id}")
                else:
                    item_id = str(element)
                    print(f"  Using str(element): {item_id}")
                
                # Get image path
                img_path = ""
                if hasattr(element, 'get_img_path'):
                    img_path = element.get_img_path()
                    print(f"  Using get_img_path(): {img_path}")
                elif hasattr(element, 'img_path'):
                    img_path = element.img_path
                    print(f"  Using element.img_path: {img_path}")
                
                # Create and configure the item
                item = QStandardItem(item_id)
                item.setData(img_path, Qt.UserRole)
                
                # Add tooltip with more information
                tooltip = f"ID: {item_id}"
                if hasattr(element, 'name') and element.name:
                    tooltip += f"\nName: {element.name}"
                if hasattr(element, 'description') and element.description:
                    tooltip += f"\n{element.description}"
                item.setToolTip(tooltip)
                
                print(f"  Created item with ID: {item_id}, image: {img_path}")
                print(f"  Tooltip: {tooltip}")

                # Add to model
                if pending is None:
                    self.appendRow(item)
                else:
                    item.setData(element not in pending, Qt.UserRole + 1)
                    self.appendRow(item)
                    
            except Exception as e:
                print(f"\n!!! ERROR processing item {i}: {e}")
                print(f"Element: {element}")
                print(f"Element type: {type(element)}")
                import traceback
                traceback.print_exc()
        
        print(f"\nSuccessfully loaded {self.rowCount()}/{len(data) if data else 0} items")
        
        print(f"Total items loaded: {self.rowCount()}")
