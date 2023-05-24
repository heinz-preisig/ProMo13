import os
from PyQt5.QtCore import QStringListModel

from packages.Common import resource_initialisation

class OntologySelectorModel(QStringListModel):
  def __init__(self):
    location = resource_initialisation.DIRECTORIES["ontology_repository"]
    directories = [
      f.path 
      for f in os.scandir(location)
      if f.is_dir() and not f.name.startswith('.')
    ]
    ontology_names = [
      os.path.splitext(os.path.basename(o))[0]
      for o in directories
    ]

    super().__init__(ontology_names)


