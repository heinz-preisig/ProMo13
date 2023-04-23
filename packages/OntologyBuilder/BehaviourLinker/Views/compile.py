import os
import subprocess


def generate_py_files(ui_folder, output_folder):
  # Get a list of UI files in the UI folder
  ui_files = [
      file
      for file in os.listdir(ui_folder)
      if file.endswith('.ui')
  ]

  # Generate the corresponding .py files for each UI file
  for file in ui_files:
    ui_file_path = os.path.join(ui_folder, file)
    py_file_name = os.path.splitext(file)[0] + '_ui.py'
    py_file_path = os.path.join(output_folder, py_file_name)

    # Execute pyuic command to generate the .py file
    subprocess.run(['pyuic5', ui_file_path, '-o', py_file_path], check=True)

    print(f'Generated: {py_file_path}')


script_dir = os.path.dirname(os.path.abspath(__file__))
ui_folder = os.path.join(script_dir, "UIs")
compiled_folder = os.path.join(script_dir, "Compiled_UIs")

generate_py_files(ui_folder, compiled_folder)
