from PyQt5.QtWidgets import QApplication, QListView
from src.common.components import image_list
from pathlib import Path


def main():
  # Create an instance of QApplication
  app = QApplication([])

  # Initialize the model, view and controller
  model = image_list.ImageListModel()
  view = QListView()
  view.setMinimumSize(500, 500)

  controller = image_list.ImageListController(view, model)

  # Add some test data to the model
  item_ids = ["V_1", "V_2", "V_3"]
  item_paths = [
      Path("../Ontology_Repository/processes_000/LaTeX/V_1.png").resolve(),
      Path("../Ontology_Repository/processes_000/LaTeX/V_2.png").resolve(),
      Path("../Ontology_Repository/processes_000/LaTeX/V_3.png").resolve(),
  ]

  model.load_data(item_ids[1:], item_paths[1:])

  # Show the view
  view.show()

  # Start the application event loop
  app.exec_()


if __name__ == "__main__":
  main()
