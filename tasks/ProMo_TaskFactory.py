import sys

file_path = "../packages/TaskFactory/code_generator.py"
args = sys.argv[1:]  # Exclude the script name from the arguments

with open(file_path, "r") as file:
  code = file.read()

# Modify the code to use the command-line arguments
modified_code = f"import sys\nsys.argv = {args}\n{code}"

exec(modified_code)
