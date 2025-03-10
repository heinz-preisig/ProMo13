from enum import StrEnum
from pathlib import Path

from .context import IOContext


class Templates(StrEnum):
    ONTOLOGY_REPOSITORY_DIR = "{repository_location}/"
    ONTOLOGY_DIR = ONTOLOGY_REPOSITORY_DIR + "{ontology_name}/"
    MODEL_LIBRARY_DIR = ONTOLOGY_DIR + "models/"
    MODEL_DIR = MODEL_LIBRARY_DIR + "{model_name}/"
    INSTANTIATION_LIBRARY_DIR = MODEL_DIR + "instantiations/"

    ONTOLOGY_INDEX_FILE = ONTOLOGY_REPOSITORY_DIR + ".repository_index.json"
    MODEL_INDEX_FILE = MODEL_LIBRARY_DIR + ".repository_index.json"
    INSTANTIATION_INDEX_FILE = INSTANTIATION_LIBRARY_DIR + ".repository_index.json"


def resolve(ontology_context: IOContext, template: Templates) -> Path:
    path_parameters = {
        "repository_location": ontology_context.repository_location,
        "ontology_name": ontology_context.ontology_name,
        "model_name": ontology_context.model_name,
        "instantiation_name": ontology_context.instantiation_name,
    }

    return Path(template.format(**path_parameters))
