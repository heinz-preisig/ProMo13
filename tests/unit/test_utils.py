from pathlib import Path


def get_test_files_path() -> Path:
  """Return the test_files directory."""
  return Path(__file__).resolve().parent / 'test_files'
