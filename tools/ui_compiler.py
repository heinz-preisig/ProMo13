import json
import pathlib
import subprocess

COMPILATION_MAP_FILE = "tools/ui_map.json"
# COMPILER = "pyside6-uic"
COMPILER = "pyuic5"


def load_compilation_info() -> list[dict[str, str]]:
    with open(COMPILATION_MAP_FILE) as f:
        compilation_info = json.load(f)

    return compilation_info


def is_compilation_needed(
    ui_file_path: pathlib.Path, py_file_path: pathlib.Path
) -> bool:
    if not py_file_path.exists():
        return True

    return ui_file_path.stat().st_mtime > py_file_path.stat().st_mtime


def get_file_paths(
    compilation_item: dict[str, str],
) -> tuple[pathlib.Path, pathlib.Path]:
    ui_file_path = (
        pathlib.Path(compilation_item["ui_dir"]) / f"{compilation_item['name']}.ui"
    )
    py_file_path = (
        pathlib.Path(compilation_item["ui_gen_dir"])
        / f"{compilation_item['name']}_ui.py"
    )

    return ui_file_path, py_file_path


def compile_ui_files() -> None:
    compilation_info = load_compilation_info()

    for compilation_item in compilation_info:
        ui_file_path, py_file_path = get_file_paths(compilation_item)
        if is_compilation_needed(ui_file_path, py_file_path):
            subprocess.run([COMPILER, ui_file_path, "-o", py_file_path], check=True)
            print(f"Generated: {py_file_path}")
        else:
            print(f"Skipped: {py_file_path}")


compile_ui_files()
