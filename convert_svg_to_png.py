import os
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt

def convert_svg_to_png(svg_path, png_path, size=16):
    renderer = QSvgRenderer(svg_path)
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    
    image.save(png_path)

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output paths
    svg_files = [
        ("resources/images/arrow-right.svg", "resources/images/arrow-right.png"),
        ("resources/images/arrow-down.svg", "resources/images/arrow-down.png")
    ]
    
    for svg_rel, png_rel in svg_files:
        svg_path = os.path.join(script_dir, svg_rel)
        png_path = os.path.join(script_dir, png_rel)
        
        if os.path.exists(svg_path):
            convert_svg_to_png(svg_path, png_path)
            print(f"Converted {svg_path} to {png_path}")
        else:
            print(f"Warning: {svg_path} not found")
